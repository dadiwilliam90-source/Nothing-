"""Rounded-box primitives + PBR materials, matched to the base rig's look."""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

# Finishes tuned so flat colours still read as real fabric / leather / metal.
CLOTH = dict(metallic=0.0, rough=0.78)
DENIM = dict(metallic=0.0, rough=0.88)
LEATHER = dict(metallic=0.0, rough=0.42)
METAL = dict(metallic=0.95, rough=0.28)
GLOSS = dict(metallic=0.0, rough=0.22)
RUBBER = dict(metallic=0.0, rough=0.95)


def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexs(h):
    """Hex (or 0-1 tuple) -> sRGB 0-1. Use for texture pixel maths."""
    if not isinstance(h, str):
        return tuple(float(v) for v in h)
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hexc(h):
    """Hex sRGB -> linear RGB. glTF baseColorFactor is linear, so this must convert."""
    return tuple(_srgb_to_linear(v) for v in hexs(h))


def shade(color, factor=0.84):
    """Darken (or lighten, factor > 1) a colour in sRGB for ribbing and hems."""
    return tuple(min(1.0, v * factor) for v in hexs(color))


def pbr(color, finish=CLOTH, alpha=1.0, name="mat"):
    r, g, b = hexc(color)
    return PBRMaterial(
        name=name,
        baseColorFactor=[r, g, b, alpha],
        metallicFactor=finish["metallic"],
        roughnessFactor=finish["rough"],
        alphaMode="BLEND" if alpha < 1.0 else "OPAQUE",
        doubleSided=False,
    )


def _paint(mesh, color, finish, alpha, name):
    mesh.visual = trimesh.visual.TextureVisuals(material=pbr(color, finish, alpha, name))
    return mesh


def rbox(center, size, color, radius=0.055, finish=CLOTH, alpha=1.0, subdiv=2, name="part"):
    """Rounded box — convex hull of spheres at the inset corners.

    Matches the soft bevel of the supplied rig so garments never look like raw cubes.
    """
    size = np.asarray(size, dtype=float)
    r = float(min(radius, size.min() / 2.05))
    if r <= 1e-4:
        m = trimesh.creation.box(extents=size)
    else:
        inner = size - 2 * r
        pts = []
        ico = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
        for sx in (-1, 1):
            for sy in (-1, 1):
                for sz in (-1, 1):
                    off = np.array([sx, sy, sz]) * inner / 2
                    pts.append(ico.vertices + off)
        m = trimesh.Trimesh(vertices=np.vstack(pts)).convex_hull
    m.apply_translation(np.asarray(center, dtype=float))
    return _paint(m, color, finish, alpha, name)


def cyl(center, radius, height, color, axis="y", finish=CLOTH, alpha=1.0, sections=40, name="part"):
    m = trimesh.creation.cylinder(radius=radius, height=height, sections=sections)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "z":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation(np.asarray(center, dtype=float))
    return _paint(m, color, finish, alpha, name)


def sphere(center, radius, color, finish=CLOTH, alpha=1.0, subdiv=3, name="part"):
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=radius)
    m.apply_translation(np.asarray(center, dtype=float))
    return _paint(m, color, finish, alpha, name)


def ellipsoid(center, size, color, finish=CLOTH, alpha=1.0, subdiv=3, name="part"):
    """Axis-aligned ellipsoid sized by its full extents."""
    m = trimesh.creation.icosphere(subdivisions=subdiv, radius=0.5)
    m.apply_scale(np.asarray(size, dtype=float))
    m.apply_translation(np.asarray(center, dtype=float))
    return _paint(m, color, finish, alpha, name)


def rotate(mesh, angle_deg, axis, pivot):
    T = trimesh.transformations.rotation_matrix(
        np.radians(angle_deg), axis, np.asarray(pivot, dtype=float))
    mesh.apply_transform(T)
    return mesh


def taper(mesh, factor, axis=0, along=1, pivot=None):
    """Scale `axis` progressively along `along` — turns a box into a skirt / flare."""
    v = mesh.vertices.copy()
    lo, hi = v[:, along].min(), v[:, along].max()
    t = (v[:, along] - lo) / max(hi - lo, 1e-9)
    piv = v[:, axis].mean() if pivot is None else pivot
    s = 1.0 + (factor - 1.0) * (1.0 - t)
    v[:, axis] = piv + (v[:, axis] - piv) * s
    mesh.vertices = v
    return mesh
