"""Exact anchor geometry of the supplied white R6 base rig (measured, not guessed)."""
import os
import numpy as np
import trimesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_RIG = os.path.join(ROOT, "assets/raw/base_rig.glb")

# Measured from assets/raw/base_rig.glb via scripts/analyze_rig.py.
# The model faces +Z — confirmed by rendering the supplied reference avatar
# (face, hoodie zip and logo all sit on +Z) and the supplied cap (peak and
# logo on +Z, snapback strap on -Z). Up is +Y; the avatar's right is -X.
# Feet sit on Y = 0.
CX = -5.39          # body centre line in X
CZ = -9.852         # body centre line in Z (torso/limbs)
FRONT = -9.352      # torso front face (max Z)
BACK = -10.352      # torso back face (min Z)

TORSO = dict(center=(CX, 3.0, CZ), size=(2.0, 2.0, 1.0))
HEAD = dict(center=(CX, 4.5, -9.766), size=(1.198, 1.202, 1.024))
R_ARM = dict(center=(-3.89, 3.0, CZ), size=(1.0, 2.0, 1.0))
L_ARM = dict(center=(-6.89, 3.0, CZ), size=(1.0, 2.0, 1.0))
R_LEG = dict(center=(-4.89, 1.0, CZ), size=(1.0, 2.0, 1.0))
L_LEG = dict(center=(-5.89, 1.0, CZ), size=(1.0, 2.0, 1.0))

HEAD_TOP = HEAD["center"][1] + HEAD["size"][1] / 2      # 5.101
HEAD_BOTTOM = HEAD["center"][1] - HEAD["size"][1] / 2   # 3.899
HEAD_FRONT = HEAD["center"][2] + HEAD["size"][2] / 2    # -9.254
HEAD_BACK = HEAD["center"][2] - HEAD["size"][2] / 2     # -10.278
HEAD_W = HEAD["size"][0]
EYE_Y = HEAD["center"][1] + 0.12                        # eye line on the blank face

TOTAL_HEIGHT = 5.1012


def load_base():
    """Return the untouched white rig as a single mesh (geometry never altered)."""
    scene = trimesh.load(BASE_RIG, force="scene", process=False)
    return trimesh.util.concatenate(list(scene.dump()))


def box(center, size, color):
    """Axis-aligned flat-coloured box — the building block for all garments."""
    m = trimesh.creation.box(extents=np.asarray(size, dtype=float))
    m.apply_translation(np.asarray(center, dtype=float))
    m.visual = trimesh.visual.ColorVisuals(
        mesh=m, face_colors=np.tile(np.array(color + (255,), dtype=np.uint8), (len(m.faces), 1)))
    return m


def shell(part, pad, color, y_lo=None, y_hi=None, z_pad=None):
    """A garment layer hugging a body part, optionally clipped in Y.

    pad grows the part in X/Z so the cloth sits just outside the white skin.
    y_lo / y_hi are absolute world heights for where the garment starts/ends.
    """
    cx, cy, cz = part["center"]
    sx, sy, sz = part["size"]
    zp = pad if z_pad is None else z_pad
    lo = cy - sy / 2 if y_lo is None else y_lo
    hi = cy + sy / 2 if y_hi is None else y_hi
    return box((cx, (lo + hi) / 2, cz), (sx + 2 * pad, hi - lo, sz + 2 * zp), color)
