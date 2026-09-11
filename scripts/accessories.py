"""Fit the supplied hair / cap / glasses assets onto the rig head.

The packs are authored at arbitrary scale, position and yaw, so every item is
re-anchored from its own geometry rather than from hard-coded transforms:
  * hair  - measured by its skull cap (top slice), crown pinned to the head top
  * cap   - measured by its band, dropped over the skull
  * glasses - measured by its width, seated on the front face at eye level
"""
import os
import numpy as np
import trimesh
from PIL import Image
import rig as R
from geom import pbr, GLOSS, CLOTH

ITEMS = os.path.join(R.ROOT, "assets/items")
HX, HY, HZ = R.HEAD["center"]
HEAD_BACK = HZ + R.HEAD["size"][2] / 2


def load_item(key):
    m = trimesh.load(f"{ITEMS}/{key}.glb", force="mesh", process=False)
    return m.copy()


def _yaw(mesh, deg):
    if deg:
        mesh.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(deg), [0, 1, 0], mesh.bounds.mean(axis=0)))
    return mesh


def _cap_profile(mesh, upper=0.55, thresh=0.80, bins=56):
    """Locate the skull-gripping band of a wig: its height, width and centre.

    Scanning only the upper part of the mesh keeps long lengths and ponytails
    from being mistaken for the part that actually sits on the head.
    """
    v = mesh.vertices
    lo, hi = v[:, 1].min(), v[:, 1].max()
    h = max(hi - lo, 1e-9)
    edges = np.linspace(hi - h * upper, hi, bins + 1)
    widths, cx, cz = np.zeros(bins), np.zeros(bins), np.zeros(bins)
    for i in range(bins):
        sel = (v[:, 1] >= edges[i]) & (v[:, 1] <= edges[i + 1])
        if sel.sum() < 4:
            continue
        s = v[sel]
        widths[i] = s[:, 0].max() - s[:, 0].min()
        cx[i] = (s[:, 0].max() + s[:, 0].min()) / 2
        cz[i] = (s[:, 2].max() + s[:, 2].min()) / 2
    wmax = widths.max()
    if wmax <= 1e-6:
        b = mesh.bounds
        return (b[0][1] + b[1][1]) / 2, b[1][0] - b[0][0], *((b[0] + b[1]) / 2)[[0, 2]]
    ok = np.where(widths >= thresh * wmax)[0]
    i = int(ok.max())                       # highest band that still grips the skull
    return (edges[i] + edges[i + 1]) / 2, wmax, cx[i], cz[i]


def _slice_extent(mesh, frac=0.30, top=True):
    """Width/depth of the top (or bottom) slice — the part that grips the head."""
    v = mesh.vertices
    lo, hi = v[:, 1].min(), v[:, 1].max()
    h = hi - lo
    sel = v[:, 1] >= hi - h * frac if top else v[:, 1] <= lo + h * frac
    s = v[sel] if sel.sum() > 8 else v
    return (s[:, 0].max() - s[:, 0].min(), s[:, 2].max() - s[:, 2].min(),
            (s[:, 0].max() + s[:, 0].min()) / 2, (s[:, 2].max() + s[:, 2].min()) / 2)


def recolor(mesh, color, keep_detail=True, finish=CLOTH):
    """Re-tint a textured asset to a chosen colour, keeping its shading detail.

    The source texture's luminance is normalised and used to modulate the new
    colour, so strand/weave detail survives but the hue is fully under control.
    """
    if color is None:
        return mesh
    tex = None
    try:
        tex = mesh.visual.material.baseColorTexture
    except Exception:
        pass
    if tex is None or not keep_detail:
        mesh.visual = trimesh.visual.TextureVisuals(material=pbr(color, finish))
        return mesh

    img = tex.convert("RGB")
    if max(img.size) > 512:
        img.thumbnail((512, 512), Image.LANCZOS)
    lum = np.asarray(img.convert("L"), dtype=np.float32) / 255.0
    p5, p95 = np.percentile(lum, 5), np.percentile(lum, 95)
    lum = np.clip((lum - p5) / max(p95 - p5, 1e-3), 0, 1)
    lum = 0.42 + 0.58 * lum                     # keep shadows readable, never crushed
    from geom import hexs
    rgb = np.array(hexs(color), dtype=np.float32)   # texture pixels stay in sRGB
    out = np.clip(lum[..., None] * rgb[None, None, :], 0, 1)
    new = Image.fromarray((out * 255).astype(np.uint8))
    mat = pbr((1, 1, 1), finish)
    mat.baseColorTexture = new
    mesh.visual = trimesh.visual.TextureVisuals(uv=mesh.visual.uv, material=mat)
    return mesh


def fit_hair(key, color=None, yaw=0.0, scale=1.0, dy=0.0, dz=0.0, grip=1.34,
             max_w=1.80, max_up=0.48, back=0.14, drop=0.95):
    """Seat hair on the skull.

    Width is matched to the head plus a hair-thickness allowance. Short wrap-around
    styles are centred on the skull; long styles are pinned by the crown so the
    length falls past the shoulders instead of lifting the cap off the head.
    """
    m = load_item(key)
    _yaw(m, yaw)
    _, cw, _, _ = _cap_profile(m)
    k = (R.HEAD_W * grip / max(cw, 1e-6)) * scale
    span = m.bounds[1] - m.bounds[0]
    k = min(k, R.HEAD_W * max_w / max(span[0], 1e-6))   # never balloon past the skull
    m.apply_scale(k)

    cy, _, ccx, _ = _cap_profile(m)
    b = m.bounds
    y = (R.HEAD_TOP - 0.23) + dy - cy
    if b[1][1] + y > R.HEAD_TOP + max_up:               # never tower over the skull
        y = R.HEAD_TOP + max_up - b[1][1]
    # Anchor the front edge to the face so hair falls backwards, never through it.
    m.apply_translation([HX - ccx, y, (R.HEAD_FRONT - 0.05) + dz - b[0][2]])
    _clamp_back(m, back)
    _clamp_length(m, drop)
    return recolor(m, color, finish=GLOSS)


def _clamp_back(mesh, margin):
    """Squash the wig's depth so it hugs the skull instead of jutting out behind.

    The head is only ~1.0 deep, so a wig reaching half a head-depth past it reads
    as a lump stuck to the back. The front stays pinned; the excess is compressed.
    """
    limit = HEAD_BACK + margin
    zmax = mesh.bounds[1][2]
    if zmax <= limit:
        return mesh
    anchor = R.HEAD_FRONT - 0.06
    v = mesh.vertices
    sel = v[:, 2] > anchor
    v[sel, 2] = anchor + (v[sel, 2] - anchor) * ((limit - anchor) / (zmax - anchor))
    mesh.vertices = v
    return mesh


def _clamp_length(mesh, drop):
    """Cap how far hair falls below the jaw, so nothing drags to the knees."""
    floor = R.HEAD_BOTTOM - drop
    ymin = mesh.bounds[0][1]
    if ymin >= floor:
        return mesh
    top = mesh.bounds[1][1]
    v = mesh.vertices
    sel = v[:, 1] < top
    v[sel, 1] = top - (top - v[sel, 1]) * ((top - floor) / (top - ymin))
    mesh.vertices = v
    return mesh


def fit_cap(key, color=None, yaw=0.0, scale=1.0, dy=0.0, dz=0.0, grip=1.16, overlap=0.26):
    """Drop a cap over the skull.

    The crown band sets the width; the cap's lowest point is parked `overlap`
    below the top of the head so it grips instead of hovering.
    """
    m = load_item(key)
    _yaw(m, yaw)
    bw, _, _, _ = _slice_extent(m, 0.50, top=True)
    m.apply_scale((R.HEAD_W * grip / max(bw, 1e-6)) * scale)
    _, _, bcx, bcz = _slice_extent(m, 0.50, top=True)
    b = m.bounds
    m.apply_translation([HX - bcx, (R.HEAD_TOP - overlap) + dy - b[0][1], HZ + dz - bcz])
    return recolor(m, color, finish=CLOTH)


def fit_glasses(keys=("glasses__Object_0", "glasses__Object_1"), frame="#16181D",
                lens="#59738C", yaw=0.0, scale=1.0, dy=0.0, dz=0.0, width=0.99):
    """Seat glasses flat on the blank face at eye level."""
    parts = [load_item(k) for k in keys]
    group = trimesh.util.concatenate([p.copy() for p in parts])
    _yaw(group, yaw)
    gb = group.bounds
    span = gb[1] - gb[0]
    # The widest horizontal axis is the lens-to-lens direction.
    if span[2] > span[0]:
        for p in parts:
            _yaw(p, 90)
        group = trimesh.util.concatenate([p.copy() for p in parts])
        gb = group.bounds
        span = gb[1] - gb[0]
    k = (R.HEAD_W * width / max(span[0], 1e-6)) * scale
    ctr = (gb[0] + gb[1]) / 2
    out = []
    for i, p in enumerate(parts):
        _yaw(p, yaw) if False else None
        p.apply_translation(-ctr)
        p.apply_scale(k)
        p.apply_translation([HX, R.EYE_Y + dy, R.HEAD_FRONT + 0.10 + dz])
        col, fin, a = (frame, GLOSS, 1.0) if i == 0 else (lens, GLOSS, 0.55)
        p.visual = trimesh.visual.TextureVisuals(material=pbr(col, fin, alpha=a))
        out.append(p)
    return out
