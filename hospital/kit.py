"""Geometry + material kit for the hospital corridor.

Everything is authored in metres, Y up. The corridor runs along +Z, the far
glazed wall is at the +Z end, and +X is the wall with the teal floor pier.

Faces are accumulated per material and concatenated at export time, so the GLB
carries one primitive per material rather than one per object. Without that a
scene this size becomes thousands of draw calls and a much larger file.
"""
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

# ---------------------------------------------------------------- colour

def _srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hexs(h):
    """Hex -> sRGB 0-1 tuple. Use for texture pixel maths."""
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))


def hexc(h):
    """Hex sRGB -> linear RGB. glTF stores baseColorFactor linear, so convert.

    Skipping this is what makes a teal sign export as a washed-out mint.
    """
    return tuple(_srgb_to_linear(v) for v in hexs(h))


def shade(h, f=0.85):
    """Darken/lighten a hex colour in sRGB space, returned as hex."""
    r, g, b = hexs(h)
    return "#%02x%02x%02x" % tuple(int(max(0, min(1, v * f)) * 255) for v in (r, g, b))


# ------------------------------------------------------- surface finishes
# roughness/metalness pairs tuned so each material reads correctly under the
# soft interior lighting rather than defaulting to plastic.
MATTE     = dict(metallic=0.0,  rough=0.92)
WALLPAINT = dict(metallic=0.0,  rough=0.80)
WOOD      = dict(metallic=0.0,  rough=0.52)
POLISHED  = dict(metallic=0.0,  rough=0.18)   # terrazzo floor, high sheen
CERAMIC   = dict(metallic=0.0,  rough=0.30)
STEEL     = dict(metallic=0.92, rough=0.30)   # elevator doors
CHROME    = dict(metallic=1.0,  rough=0.10)   # seat frames
DARKGLOSS = dict(metallic=0.55, rough=0.12)   # elevator transom panels
GLASSY    = dict(metallic=0.0,  rough=0.06)
PLASTIC   = dict(metallic=0.0,  rough=0.45)


class Mat:
    """A material plus the UV scale that geometry should be mapped at.

    `repeat` is in metres per texture tile; geometry emitters divide world
    size by it so one texture keeps a constant physical scale everywhere it
    is used, regardless of the size of the surface it lands on.
    """

    __slots__ = ("name", "color", "finish", "alpha", "tex", "emissive", "etex",
                 "emissive_strength", "repeat", "double", "_pbr")

    def __init__(self, name, color="#ffffff", finish=MATTE, alpha=1.0, tex=None,
                 emissive=None, emissive_strength=1.0, repeat=1.0, double=False,
                 etex=None):
        self.name = name
        self.color = color
        self.finish = finish
        self.alpha = alpha
        self.tex = tex                      # PIL.Image or None
        self.emissive = emissive            # hex or None
        self.etex = etex                    # PIL.Image or True to reuse `tex`
        self.emissive_strength = emissive_strength
        self.repeat = repeat
        self.double = double
        self._pbr = None

    def pbr(self):
        if self._pbr is None:
            kw = {}
            if self.tex is not None:
                kw["baseColorTexture"] = self.tex
                # Texture supplies the colour; factor must stay white or it tints.
                base = [1.0, 1.0, 1.0, self.alpha]
            else:
                r, g, b = hexc(self.color)
                base = [r, g, b, self.alpha]
            if self.etex is not None:
                kw["emissiveTexture"] = self.tex if self.etex is True else self.etex
            if self.emissive is not None:
                k = self.emissive_strength
                kw["emissiveFactor"] = [c * k for c in hexc(self.emissive)]
            self._pbr = PBRMaterial(
                name=self.name,
                baseColorFactor=base,
                metallicFactor=self.finish["metallic"],
                roughnessFactor=self.finish["rough"],
                alphaMode="BLEND" if self.alpha < 1.0 else "OPAQUE",
                doubleSided=self.double,
                **kw)
        return self._pbr


# ------------------------------------------------------------- accumulator

class Builder:
    """Collects faces per material, then welds each group into one mesh."""

    def __init__(self):
        self._g = {}          # material name -> [mat, verts[], faces[], uvs[]]

    def add(self, mat, verts, faces, uvs):
        g = self._g.get(mat.name)
        if g is None:
            g = self._g[mat.name] = [mat, [], [], []]
        off = sum(len(v) for v in g[1])
        g[1].append(np.asarray(verts, dtype=np.float64))
        g[2].append(np.asarray(faces, dtype=np.int64) + off)
        g[3].append(np.asarray(uvs, dtype=np.float64))

    def add_mesh(self, mat, mesh, uvs=None):
        """Add a trimesh primitive; UVs default to a planar XZ projection."""
        v = mesh.vertices
        if uvs is None:
            uvs = np.column_stack([v[:, 0] / mat.repeat, v[:, 2] / mat.repeat])
        self.add(mat, v, mesh.faces, uvs)

    def scene(self):
        sc = trimesh.Scene()
        for name, (mat, vs, fs, uvs) in self._g.items():
            V = np.vstack(vs)
            F = np.vstack(fs)
            UV = np.vstack(uvs)
            m = trimesh.Trimesh(vertices=V, faces=F, process=False)
            m.visual = trimesh.visual.TextureVisuals(uv=UV, material=mat.pbr())
            sc.add_geometry(m, geom_name=name, node_name=name)
        return sc

    def stats(self):
        tris = sum(sum(len(f) for f in g[2]) for g in self._g.values())
        return len(self._g), tris


# --------------------------------------------------------------- emitters

def quad(b, mat, p0, p1, p2, p3, normal=None, uvs=None):
    """One rectangle from four corners, wound so its normal faces `normal`.

    `uvs` are given per corner and are permuted with the vertices when the
    winding is reversed, so the mapping stays welded to the surface.
    """
    P = [np.asarray(p, dtype=float) for p in (p0, p1, p2, p3)]
    UV = np.asarray(uvs, dtype=float) if uvs is not None else np.zeros((4, 2))
    n = np.cross(P[1] - P[0], P[3] - P[0])
    if normal is not None and np.dot(n, np.asarray(normal, dtype=float)) < 0:
        P = [P[0], P[3], P[2], P[1]]
        UV = UV[[0, 3, 2, 1]]
    b.add(mat, np.array(P), np.array([[0, 1, 2], [0, 2, 3]]), UV)


def rect(b, mat, axis, at, u0, u1, v0, v1, normal=1, decal=False, uv=None):
    """An axis-aligned rectangle — the workhorse for walls, floors and decals.

    axis 'x': plane x=at, spanning z in (u0,u1) and y in (v0,v1)
    axis 'y': plane y=at, spanning x in (u0,u1) and z in (v0,v1)
    axis 'z': plane z=at, spanning x in (u0,u1) and y in (v0,v1)

    UVs are derived from world position rather than corner order, so winding
    never mirrors the artwork. V runs with the surface's up direction, and U is
    mirrored on the facings where the viewer stands on the other side, which is
    what keeps signage readable on every wall:

        +X-facing wall  -> viewer looks -X, screen-right is -Z, so U mirrors
        -Z-facing wall  -> viewer looks +Z, screen-right is -X, so U mirrors

    `decal=True` maps the texture exactly once across the rectangle; otherwise
    it tiles at mat.repeat metres.
    """
    if axis == "x":
        pts = [(at, v0, u0), (at, v0, u1), (at, v1, u1), (at, v1, u0)]
        nrm = (normal, 0, 0)
        mirror = normal > 0
    elif axis == "y":
        pts = [(u0, at, v0), (u1, at, v0), (u1, at, v1), (u0, at, v1)]
        nrm = (0, normal, 0)
        mirror = False
    else:
        pts = [(u0, v0, at), (u1, v0, at), (u1, v1, at), (u0, v1, at)]
        nrm = (0, 0, normal)
        mirror = normal < 0
    if uv is not None:                      # explicit override, corner order
        (a0, b0), (a1, b1) = uv
        UV = [[a0, b0], [a1, b0], [a1, b1], [a0, b1]]
    else:
        du, dv = abs(u1 - u0), abs(v1 - v0)
        su = 1.0 if decal else du / mat.repeat
        sv = 1.0 if decal else dv / mat.repeat
        UV = []
        for (s, t) in ((0, 0), (1, 0), (1, 1), (0, 1)):
            uu = (1 - s) if mirror else s
            UV.append([uu * su, t * sv])
    quad(b, mat, *pts, normal=nrm, uvs=UV)


def box(b, mat, lo, hi, uv=None, skip=()):
    """Axis-aligned box from two opposite corners, all six faces outward."""
    x0, y0, z0 = [min(a, c) for a, c in zip(lo, hi)]
    x1, y1, z1 = [max(a, c) for a, c in zip(lo, hi)]
    if "x-" not in skip: rect(b, mat, "x", x0, z0, z1, y0, y1, normal=-1, uv=uv)
    if "x+" not in skip: rect(b, mat, "x", x1, z0, z1, y0, y1, normal=+1, uv=uv)
    if "y-" not in skip: rect(b, mat, "y", y0, x0, x1, z0, z1, normal=-1, uv=uv)
    if "y+" not in skip: rect(b, mat, "y", y1, x0, x1, z0, z1, normal=+1, uv=uv)
    if "z-" not in skip: rect(b, mat, "z", z0, x0, x1, y0, y1, normal=-1, uv=uv)
    if "z+" not in skip: rect(b, mat, "z", z1, x0, x1, y0, y1, normal=+1, uv=uv)


def frame(b, mat, axis, at, u0, u1, v0, v1, t, normal=1):
    """A rectangular border (four rects) — door reveals and window mullions."""
    rect(b, mat, axis, at, u0, u1, v0, v0 + t, normal=normal)
    rect(b, mat, axis, at, u0, u1, v1 - t, v1, normal=normal)
    rect(b, mat, axis, at, u0, u0 + t, v0 + t, v1 - t, normal=normal)
    rect(b, mat, axis, at, u1 - t, u1, v0 + t, v1 - t, normal=normal)


def tube(b, mat, p0, p1, r, sections=16):
    """Cylinder between two points — seat legs, handles, sign rods."""
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    d = p1 - p0
    h = np.linalg.norm(d)
    if h < 1e-9:
        return
    m = trimesh.creation.cylinder(radius=r, height=h, sections=sections)
    zax = np.array([0.0, 0.0, 1.0])
    ax = np.cross(zax, d / h)
    s = np.linalg.norm(ax)
    if s > 1e-9:
        ang = np.arctan2(s, np.dot(zax, d / h))
        m.apply_transform(trimesh.transformations.rotation_matrix(ang, ax / s))
    elif np.dot(zax, d / h) < 0:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation((p0 + p1) / 2)
    b.add_mesh(mat, m)


def rbox(b, mat, lo, hi, r=0.02, subdiv=1):
    """Rounded box via convex hull of corner spheres — seat pads, kiosk shells.

    Real furniture has no perfectly sharp arrises; the bevel is what stops
    seating and kiosks reading as raw blocks under a hard ceiling light.
    """
    lo = np.asarray(lo, float); hi = np.asarray(hi, float)
    size = hi - lo
    r = float(min(r, size.min() / 2.05))
    if r <= 1e-4:
        box(b, mat, lo, hi)
        return
    inner = size - 2 * r
    ico = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
    pts = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            for sz in (-1, 1):
                pts.append(ico.vertices + np.array([sx, sy, sz]) * inner / 2)
    m = trimesh.Trimesh(vertices=np.vstack(pts)).convex_hull
    m.apply_translation((lo + hi) / 2)
    b.add_mesh(mat, m)


# Kept only so callers can force an explicit corner-order mapping.
UV_FLAT = ((0.0, 0.0), (1.0, 1.0))


def rbox_mesh(size, r=0.02, subdiv=1):
    """Rounded box centred on the origin, as a raw trimesh for transforming."""
    size = np.asarray(size, float)
    r = float(min(r, size.min() / 2.05))
    if r <= 1e-4:
        return trimesh.creation.box(extents=size)
    inner = size - 2 * r
    ico = trimesh.creation.icosphere(subdivisions=subdiv, radius=r)
    pts = [ico.vertices + np.array([sx, sy, sz]) * inner / 2
           for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
    return trimesh.Trimesh(vertices=np.vstack(pts)).convex_hull


def place(b, mat, mesh, at=(0, 0, 0), rot=None):
    """Add a mesh rotated about its own centre then moved to `at`.

    rot is (degrees, axis) — used for the tilt on seat pads and backs.
    """
    m = mesh.copy()
    if rot is not None:
        deg, axis = rot
        m.apply_transform(trimesh.transformations.rotation_matrix(
            np.radians(deg), axis, [0, 0, 0]))
    m.apply_translation(np.asarray(at, float))
    b.add_mesh(mat, m)
    return m
