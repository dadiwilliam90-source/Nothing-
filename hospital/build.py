"""Assemble the hospital 2F elevator hall and reception bay into one GLB.

Layout, in metres, Y up:

    the main hall runs along +Z, 9.2 m wide, 3.18 m to the ceiling
    z = 40   full-height glazed curtain wall (the bright end of the corridor)
    z = 24..31  lift banks, three cars on each side wall
    z = 22..23.5 teal floor pier carrying the '2.' and the pictogram stack
    z = 17..23  the two grey double doors
    z = 12   suspended teal directional sign
    z = 3..10 opening in the +X wall into the reception bay
    z = 0    near end of the hall

Run:  python3 hospital/build.py [out.glb]
"""
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import kit
import textures as T
from kit import (Builder, Mat, box, rect, frame, quad, tube, rbox, rbox_mesh,
                 place, UV_FLAT)

# ----------------------------------------------------------- dimensions
HW = 4.6                  # half-width of the hall (wall at x = +/-HW)
CEIL = 3.18               # main ceiling height
SOFF = 3.02               # dropped perimeter soffit (a shallow step, not a bulkhead)
SOFF_D = 1.45             # how far the soffit reaches in from each wall
Z0, Z1 = 0.0, 34.0        # hall extent along Z
SKIRT = 0.095             # black recessed skirting
DOOR_H = 2.16             # grey double doors
LIFT_H = 2.25             # lift door opening
LIFT_W = 0.65             # half-width of a lift opening (1.30 m of door)

# Reception bay, opening off the -X wall. Looking down the hall (+Z) the
# -X wall is the one on the viewer's right, which is the detailed wall in
# every reference frame: lifts, teal pier, doors, kiosks and this opening.
RXF, RXI = -16.4, -HW          # far wall / corridor-side wall of the bay
RZ0, RZ1 = -1.2, 13.2
OPEN_Z0, OPEN_Z1 = 0.9, 3.3

# ------------------------------------------------------------ materials

def materials():
    wood = T.wood_veneer()
    return dict(
        floor=Mat("floor_terrazzo", tex=T.terrazzo(),
                  finish=dict(metallic=0.0, rough=0.22), repeat=1.8),
        ceil=Mat("ceiling_panel", tex=T.ceiling_panel(), finish=kit.MATTE, repeat=1.2),
        wood=Mat("wood_veneer", tex=wood, finish=kit.WOOD, repeat=0.62),
        woodc=Mat("wood_counter", tex=T.wood_counter(), finish=kit.WOOD, repeat=1.1),
        wall=Mat("wall_paint", tex=T.wall_paint(), finish=kit.WALLPAINT, repeat=2.0),
        steel=Mat("brushed_steel", tex=T.brushed_steel(),
                  finish=dict(metallic=0.75, rough=0.28), repeat=1.3),
        chrome=Mat("chrome", "#D2D5D8", kit.CHROME),
        dark=Mat("dark_reveal", "#141416", kit.MATTE),
        skirt=Mat("skirting", "#1A1A1C", kit.CERAMIC),
        transom=Mat("lift_transom", "#2B2B2F", dict(metallic=0.25, rough=0.07)),
        doorleaf=Mat("door_leaf", "#C7C7C5", kit.WALLPAINT),
        doorframe=Mat("door_frame", "#AFAFAD", kit.WALLPAINT),
        glass=Mat("glazing", "#DCE6EA", kit.GLASSY, alpha=0.18, double=True),
        vision=Mat("vision_glass", "#B9CCD4", kit.GLASSY, alpha=0.46, double=True),
        mullion=Mat("mullion", "#232326", kit.CERAMIC),
        teal=Mat("teal_paint", T.TEAL, kit.WALLPAINT),
        pier=Mat("teal_pier_art", tex=T.floor_pier(), finish=kit.WALLPAINT, repeat=1.0),
        sign=Mat("hanging_sign", tex=T.hanging_sign(), finish=kit.WALLPAINT,
                 emissive="#2A2A2A", etex=True, repeat=1.0, emissive_strength=0.45),
        signback=Mat("sign_back", T.TEAL, kit.WALLPAINT),
        lcd=Mat("lift_lcd", tex=T.lift_lcd(), finish=kit.GLASSY,
                emissive="#BFBFBF", etex=True, repeat=1.0, emissive_strength=0.55),
        kioskui=Mat("kiosk_screen", tex=T.kiosk_screen(), finish=kit.GLASSY,
                    emissive="#B4B4B4", etex=True, repeat=1.0, emissive_strength=0.55),
        plate=Mat("call_plate", tex=T.call_plate(), finish=kit.STEEL, repeat=1.0),
        indic=Mat("floor_indicator", tex=T.floor_indicator(), finish=kit.GLASSY,
                  emissive="#FFFFFF", etex=True, repeat=1.0, emissive_strength=0.55),
        ext=Mat("exterior_backdrop", tex=T.exterior(), finish=kit.MATTE,
                emissive="#8C8C8C", etex=True, repeat=1.0, double=True, emissive_strength=0.5),
        lightstrip=Mat("light_strip", "#FFF6E4", kit.GLASSY, emissive="#FFF3DC",
                       emissive_strength=0.45),
        downlight=Mat("downlight", "#FFF4E0", kit.GLASSY, emissive="#FFEFD2",
                      emissive_strength=0.45),
        kioskbody=Mat("kiosk_body", "#F0F1F0", kit.CERAMIC),
        kioskbase=Mat("kiosk_base", "#1F7F96", kit.CERAMIC),
        seat_tan=Mat("seat_tan", "#C2965F", kit.PLASTIC),
        seat_teal=Mat("seat_teal", "#74BFC9", kit.PLASTIC),
        seat_brown=Mat("seat_brown", "#6B5443", kit.PLASTIC),
        column=Mat("column_white", "#E9E8E5", kit.WALLPAINT),
    )


# ------------------------------------------------------------ wall runs

def panel_run(b, M, axis, at, z0, z1, normal, y0=0.0, y1=CEIL, pitch=1.05,
              mat=None, proud=0.022):
    """Wood panelling as discrete boards proud of a dark backing.

    Modelling the shadow gap as real geometry rather than a painted line is
    what gives the walls their grain of vertical joints under raking light.
    """
    mat = mat or M["wood"]
    gap = 0.008
    rect(b, M["dark"], axis, at, z0, z1, y0, y1, normal=normal)
    n = max(1, int(round((z1 - z0) / pitch)))
    step = (z1 - z0) / n
    d = proud * normal
    for i in range(n):
        a = z0 + i * step + gap / 2
        c = z0 + (i + 1) * step - gap / 2
        lo_x = min(at, at + d); hi_x = max(at, at + d)
        if axis == "x":
            box(b, mat, (lo_x, y0, a), (hi_x, y1, c),
                skip=("x-",) if normal > 0 else ("x+",))
        else:
            box(b, mat, (a, y0, lo_x), (c, y1, hi_x),
                skip=("z-",) if normal > 0 else ("z+",))


def skirting(b, M, axis, at, z0, z1, normal, h=SKIRT, proud=0.030):
    """Dark recessed base line that runs under every wall finish."""
    d = proud * normal
    lo = min(at, at + d); hi = max(at, at + d)
    if axis == "x":
        box(b, M["skirt"], (lo, 0.0, z0), (hi, h, z1))
    else:
        box(b, M["skirt"], (z0, 0.0, lo), (z1, h, hi))


# ------------------------------------------------------------- elements

def lift(b, M, at, zc, normal):
    """One lift: stainless doors, dark transom, indicator, jambs.

    `at` is the wall plane, `zc` the centre of the opening, `normal` the
    direction the doors face into the room.
    """
    d = 0.055 * normal                       # doors recessed into the wall
    w = LIFT_W
    z0, z1 = zc - w, zc + w
    inner = at + d

    # Recessed door pocket: back plane plus reveal returns.
    rect(b, M["steel"], "x", inner, z0, z1, 0.0, LIFT_H, normal=normal)
    lo = min(at, inner); hi = max(at, inner)
    box(b, M["steel"], (lo, 0.0, z0 - 0.055), (hi, LIFT_H + 0.055, z0), skip=())
    box(b, M["steel"], (lo, 0.0, z1), (hi, LIFT_H + 0.055, z1 + 0.055), skip=())
    box(b, M["steel"], (lo, LIFT_H, z0), (hi, LIFT_H + 0.055, z1), skip=())
    # Centre joint between the two door leaves.
    box(b, M["dark"], (inner - 0.004 * normal, 0.0, zc - 0.006),
        (inner + 0.004 * normal, LIFT_H, zc + 0.006))

    # Dark glossy transom from the door head up to the soffit.
    tz = 0.04 * normal
    lo = min(at, at + tz); hi = max(at, at + tz)
    box(b, M["transom"], (lo, LIFT_H + 0.055, z0 - 0.055),
        (hi, SOFF, z1 + 0.055), skip=("x-",) if normal > 0 else ("x+",))
    # Red car-position readout set into the transom, just above the doors.
    ind = at + (0.045 * normal)
    rect(b, M["indic"], "x", ind, zc - 0.20, zc + 0.20,
         LIFT_H + 0.12, LIFT_H + 0.32, normal=normal,
         decal=True)


def lift_side_kit(b, M, at, z, normal, lcd=True):
    """The vertical advert LCD and the call plate mounted on a lift pier."""
    p = at + 0.016 * normal
    if lcd:
        lo = min(at, p); hi = max(at, p)
        box(b, M["dark"], (lo, 1.28, z - 0.24), (hi, 1.98, z + 0.24))
        rect(b, M["lcd"], "x", p + 0.004 * normal, z - 0.215, z + 0.215,
             1.305, 1.955, normal=normal, decal=True)
    rect(b, M["plate"], "x", p, z - 0.055, z + 0.055, 1.00, 1.33,
         normal=normal, decal=True)


def lift_bank(b, M, at, zs, normal, pier_w=0.70):
    """A run of lifts with wood piers between and the screens on the piers."""
    for zc in zs:
        lift(b, M, at, zc, normal)
    lo, hi = min(zs) - LIFT_W, max(zs) + LIFT_W
    for i in range(len(zs) - 1):
        a = zs[i] + LIFT_W + 0.055
        c = zs[i + 1] - LIFT_W - 0.055
        panel_run(b, M, "x", at, a, c, normal, pitch=max(0.3, (c - a)))
        skirting(b, M, "x", at, a, c, normal)
        # Screen + call plate live on the pier, between the two cars.
        lift_side_kit(b, M, at + 0.022 * normal, (a + c) / 2, normal)
    return lo - 0.055, hi + 0.055


def double_door(b, M, at, zc, normal, w=1.90, h=DOOR_H):
    """Grey double door with a tall vision strip in each leaf and levers."""
    z0, z1 = zc - w / 2, zc + w / 2
    rec = 0.05 * normal
    p = at + rec
    lo = min(at, p); hi = max(at, p)
    # Reveal returns around the opening.
    box(b, M["doorframe"], (lo, 0.0, z0 - 0.06), (hi, h + 0.06, z0))
    box(b, M["doorframe"], (lo, 0.0, z1), (hi, h + 0.06, z1 + 0.06))
    box(b, M["doorframe"], (lo, h, z0), (hi, h + 0.06, z1))
    # Over-panel up to the ceiling.
    panel_run(b, M, "x", at, z0 - 0.06, z1 + 0.06, normal, y0=h + 0.06, y1=CEIL,
              mat=M["wall"], pitch=(z1 - z0 + 0.12), proud=0.004)

    leaf = (z1 - z0) / 2
    for i in range(2):
        a = z0 + i * leaf + 0.006
        c = z0 + (i + 1) * leaf - 0.006
        rect(b, M["doorleaf"], "x", p, a, c, 0.0, h, normal=normal)
        # Vision strip: dark frame with glass inset, set toward the leading edge.
        vc = c - leaf * 0.30 if i == 0 else a + leaf * 0.30
        vz0, vz1 = vc - 0.075, vc + 0.075
        vy0, vy1 = 0.86, 1.92
        frame(b, M["dark"], "x", p + 0.004 * normal, vz0 - 0.022, vz1 + 0.022,
              vy0 - 0.022, vy1 + 0.022, 0.022, normal=normal)
        rect(b, M["vision"], "x", p + 0.002 * normal, vz0, vz1, vy0, vy1, normal=normal)
    # Lever handles either side of the meeting stile.
    hx = p + 0.045 * normal
    for zz in (zc - 0.085, zc + 0.085):
        tube(b, M["chrome"], (p, 1.05, zz), (hx, 1.05, zz), 0.013, sections=10)
        s = -1 if zz < zc else 1
        tube(b, M["chrome"], (hx, 1.05, zz), (hx, 1.05, zz + s * 0.135), 0.011, sections=10)


def teal_pier(b, M, at, z0, z1, normal):
    """The full-height teal wayfinding pier carrying the floor number."""
    d = 0.030 * normal
    lo = min(at, at + d); hi = max(at, at + d)
    box(b, M["teal"], (lo, 0.0, z0), (hi, CEIL, z1),
        skip=("x-",) if normal > 0 else ("x+",))
    rect(b, M["pier"], "x", at + d + 0.003 * normal, z0, z1, 0.0, CEIL,
         normal=normal, decal=True)


def hanging_sign(b, M, zc, xc=0.25, w=4.40, h=0.545, t=0.10):
    """Suspended directional sign, hung on two thin rods from the ceiling."""
    x0, x1 = xc - w / 2, xc + w / 2
    y0, y1 = 2.40, 2.40 + h
    box(b, M["signback"], (x0, y0, zc - t / 2), (x1, y1, zc + t / 2))
    # Read from the near side (-Z), so the artwork is mirrored in U.
    rect(b, M["sign"], "z", zc - t / 2 - 0.003, x0, x1, y0, y1,
         normal=-1, decal=True)
    rect(b, M["sign"], "z", zc + t / 2 + 0.003, x0, x1, y0, y1,
         normal=+1, decal=True)
    for xx in (x0 + w * 0.18, x1 - w * 0.18):
        tube(b, M["chrome"], (xx, y1, zc), (xx, CEIL, zc), 0.011, sections=8)


def curtain_wall(b, M, z, x0, x1, bays=6):
    """Glazed end wall: black mullions, glass, and a lit backdrop beyond."""
    rect(b, M["glass"], "z", z, x0, x1, 0.0, CEIL, normal=-1)
    step = (x1 - x0) / bays
    for i in range(bays + 1):
        x = x0 + i * step
        box(b, M["mullion"], (x - 0.035, 0.0, z - 0.05), (x + 0.035, CEIL, z + 0.05))
    box(b, M["mullion"], (x0, 0.0, z - 0.05), (x1, 0.07, z + 0.05))
    box(b, M["mullion"], (x0, CEIL - 0.07, z - 0.05), (x1, CEIL, z + 0.05))
    # Bright hazy exterior a little way behind the glass.
    rect(b, M["ext"], "z", z + 3.2, x0 - 9, x1 + 9, -1.5, CEIL + 3.0,
         normal=-1, decal=True)


def kiosk(b, M, x, z, facing=-1):
    """Self-service terminal: white shell, teal base, tilted touchscreen."""
    d = 0.30
    # Base cabinet in teal, set back under the head.
    box(b, M["kioskbase"], (x - 0.02 * facing, 0.0, z - 0.29),
        (x + d * facing, 0.86, z + 0.29))
    box(b, M["skirt"], (x - 0.02 * facing, 0.0, z - 0.29),
        (x + d * facing, 0.055, z + 0.29))
    # White upper shell, slightly wider, with the screen raked back.
    shell = rbox_mesh((0.34, 0.80, 0.66), r=0.035)
    place(b, M["kioskbody"], shell, at=(x + (d * 0.55) * facing, 1.26, z))
    scr = rbox_mesh((0.045, 0.56, 0.50), r=0.012)
    place(b, M["kioskbody"], scr,
          at=(x + (d * 0.55 + 0.16) * facing, 1.34, z), rot=(-9, [0, 0, 1]))
    sx = x + (d * 0.55 + 0.186) * facing
    rect(b, M["kioskui"], "x", sx, z - 0.215, z + 0.215, 1.09, 1.585,
         normal=facing, decal=True)
    # Card reader / printer slots across the ledge below the screen.
    for dz, wz in ((-0.19, 0.10), (0.0, 0.13), (0.19, 0.10)):
        box(b, M["dark"], (sx - 0.012 * facing, 0.95, z + dz - wz / 2),
            (sx + 0.006 * facing, 1.00, z + dz + wz / 2))
    box(b, M["kioskbody"], (x + (d * 0.25) * facing, 0.86, z - 0.33),
        (x + (d * 0.55 + 0.20) * facing, 0.94, z + 0.33))


def bench(b, M, x, z, n=4, along="z", colours=None, pitch=0.55, face=1):
    """Beam seating: chrome frame, thin tilted pads, occasional teal accent.

    `face` is which way along the cross-axis the sitter looks (+1 or -1); the
    backs go on the opposite side.
    """
    colours = colours or ["seat_tan"] * n
    L = n * pitch
    ax = np.array([0, 0, 1.0]) if along == "z" else np.array([1.0, 0, 0])
    side = (np.array([1.0, 0, 0]) if along == "z" else np.array([0, 0, 1.0])) * face
    a0 = np.array([x, 0, z], dtype=float) - ax * L / 2

    for off in (-0.15, 0.15):                       # twin rails
        p0 = a0 + side * off + np.array([0, 0.375, 0])
        tube(b, M["chrome"], p0, p0 + ax * L, 0.019, sections=10)
    for t in (0.13, 0.87):                          # splayed legs
        base = a0 + ax * (L * t)
        for sg in (-1, 1):
            tube(b, M["chrome"], base + side * (0.34 * sg),
                 base + side * (0.12 * sg) + np.array([0, 0.40, 0]), 0.016, sections=8)

    pad = rbox_mesh((0.455, 0.038, 0.415), r=0.014)
    back = rbox_mesh((0.455, 0.400, 0.034), r=0.014)
    if along == "x":                                 # rotate the pads with the row
        R = kit.trimesh.transformations.rotation_matrix(np.radians(90), [0, 1, 0])
        pad = pad.copy(); pad.apply_transform(R)
        back = back.copy(); back.apply_transform(R)
    tilt_axis = [1, 0, 0] if along == "z" else [0, 0, 1]
    sgn = face if along == "z" else -face
    for i in range(n):
        pnt = a0 + ax * (pitch * (i + 0.5))
        m = M[colours[i % len(colours)]]
        place(b, m, pad, at=(pnt[0], 0.425, pnt[2]), rot=(3.0 * sgn, tilt_axis))
        bk = pnt - side * 0.195 + np.array([0, 0.655, 0])
        place(b, m, back, at=tuple(bk), rot=(-12.0 * sgn, tilt_axis))
        # Bracket from the rails up to the pad, and the stub carrying the back.
        for off in (-0.15, 0.15):
            q = pnt + side * off
            tube(b, M["chrome"], tuple(q + np.array([0, 0.375, 0])),
                 tuple(q + np.array([0, 0.418, 0])), 0.016, sections=6)
        tube(b, M["chrome"], tuple(pnt - side * 0.185 + np.array([0, 0.40, 0])),
             tuple(pnt - side * 0.20 + np.array([0, 0.62, 0])), 0.015, sections=8)
        if i < n - 1:                                # divider between seats
            q = a0 + ax * (pitch * (i + 1))
            tube(b, M["chrome"], tuple(q + side * 0.14 + np.array([0, 0.445, 0])),
                 tuple(q - side * 0.09 + np.array([0, 0.475, 0])), 0.012, sections=8)


# ------------------------------------------------------------- ceilings

def ceiling(b, M, x0, x1, z0, z1, strips_x=(), downlight_rows=()):
    """Flat ceiling with a dropped perimeter soffit and linear light coves."""
    sx0, sx1 = x0 + SOFF_D, x1 - SOFF_D
    rect(b, M["ceil"], "y", CEIL, sx0, sx1, z0, z1, normal=-1)     # centre field
    rect(b, M["ceil"], "y", SOFF, x0, sx0, z0, z1, normal=-1)      # soffits
    rect(b, M["ceil"], "y", SOFF, sx1, x1, z0, z1, normal=-1)
    for x in (sx0, sx1):                                            # fascia returns
        rect(b, M["ceil"], "x", x, z0, z1, SOFF, CEIL,
             normal=1 if x == sx0 else -1)
    # Continuous cove light where the soffit meets the fascia — the bright
    # unbroken lines that read most strongly in the reference.
    coves = []
    for x, s in ((sx0, 1), (sx1, -1)):
        box(b, M["lightstrip"], (x + 0.015 * s, SOFF - 0.020, z0),
            (x + 0.075 * s, SOFF - 0.003, z1))
        coves.append((x + 0.05 * s, SOFF - 0.10, z0, z1))
    for x in strips_x:                                              # centre strips
        box(b, M["lightstrip"], (x - 0.032, CEIL - 0.018, z0 + 1.0),
            (x + 0.032, CEIL - 0.002, z1 - 1.0))
        coves.append((x, CEIL - 0.10, z0 + 1.0, z1 - 1.0))
    lights = []
    for x in downlight_rows:
        zz = z0 + 1.4
        while zz < z1 - 0.6:
            rect(b, M["downlight"], "y", SOFF - 0.005, x - 0.072, x + 0.072,
                 zz - 0.072, zz + 0.072, normal=-1)
            lights.append((x, SOFF - 0.05, zz))
            zz += 2.35
    return lights, coves


# ------------------------------------------------------------- reception

def reception(b, M):
    """The adjoining reception hall: counter, glazed screen, queue displays."""
    xf, xi, z0, z1 = RXF, RXI, RZ0, RZ1          # far wall, corridor-side wall
    rect(b, M["floor"], "y", 0.0, xf, xi, z0, z1, normal=1)
    lights, coves = ceiling(b, M, xf, xi, z0, z1, strips_x=(xf + 5.4,),
                            downlight_rows=(xf + 0.9, xi - 0.9))

    for zz, nrm in ((z0, 1), (z1, -1)):
        panel_run(b, M, "z", zz, xf, xi - 0.2, nrm, mat=M["wall"], pitch=3.0, proud=0.004)
        skirting(b, M, "z", zz, xf, xi - 0.2, nrm)

    # The corridor-side wall, broken by the opening back into the hall.
    for a2, c2 in ((z0, OPEN_Z0), (OPEN_Z1, z1)):
        if c2 - a2 > 0.05:
            panel_run(b, M, "x", xi, a2, c2, -1)
            skirting(b, M, "x", xi, a2, c2, -1)

    # Counter along the far wall: wood front, stone top, glazed screen over.
    cx = xf + 0.62
    cz0, cz1 = z0 + 1.4, z1 - 1.4
    box(b, M["woodc"], (xf, 0.0, cz0), (cx, 1.02, cz1), skip=("x-",))
    box(b, M["skirt"], (xf, 0.0, cz0), (cx + 0.012, SKIRT, cz1), skip=("x-",))
    box(b, M["column"], (xf, 1.02, cz0), (cx + 0.07, 1.08, cz1), skip=("x-",))
    rect(b, M["vision"], "x", cx + 0.03, cz0, cz1, 1.14, 2.36, normal=1)
    box(b, M["wall"], (xf, 2.36, cz0), (cx + 0.10, SOFF, cz1), skip=("x-",))
    panel_run(b, M, "x", xf + 0.02, cz0, cz1, 1, y0=1.02, y1=2.36,
              mat=M["wall"], pitch=3.0, proud=0.004)

    # Red queue displays, one per window, hung under the bulkhead.
    msgs = ["Please proceed to window number 3",
            "Please go to window number 4",
            "Please go to window number 5 for number 238",
            "Please go to window number 6 for number 239",
            "Please go to window number 7"]
    span = (cz1 - cz0) / len(msgs)
    for i, msg in enumerate(msgs):
        zc = cz0 + span * (i + 0.5)
        m = Mat("led_%d" % i, tex=T.led_panel(msg), finish=kit.GLASSY,
                emissive="#FFFFFF", etex=True, repeat=1.0, emissive_strength=0.55)
        box(b, M["dark"], (cx + 0.06, 2.42, zc - span * 0.46),
            (cx + 0.14, 2.74, zc + span * 0.46))
        rect(b, m, "x", cx + 0.145, zc - span * 0.45, zc + span * 0.45,
             2.44, 2.72, normal=1, decal=True)
        if i:                                        # divider between windows
            box(b, M["column"], (xf + 0.2, 1.08, zc - span / 2 - 0.02),
                (cx + 0.05, 2.36, zc - span / 2 + 0.02))

    # Square column out in the floor, as in the reference.
    box(b, M["column"], (xf + 6.0, 0.0, z0 + 6.2), (xf + 6.9, SOFF, z0 + 7.1))
    box(b, M["skirt"], (xf + 5.99, 0.0, z0 + 6.19), (xf + 6.91, SKIRT, z0 + 7.11))

    # Rows of seating facing the counter (i.e. looking toward -X).
    tan, teal, brown = "seat_brown", "seat_teal", "seat_tan"
    for xx in (xf + 3.4, xf + 5.0, xf + 6.6):
        bench(b, M, xx, z0 + 4.4, n=6, along="z", face=-1,
              colours=[tan, tan, teal, tan, brown, tan])
        bench(b, M, xx, z0 + 8.6, n=6, along="z", face=-1,
              colours=[tan, teal, tan, tan, brown, tan])
    return lights, coves


# ------------------------------------------------------------------ hall

def hall(b, M):
    """The main elevator hall. The detailed wall is -X: looking down the hall
    along +Z that is the wall on the viewer's right, matching every reference.
    """
    rect(b, M["floor"], "y", 0.0, -HW, HW, Z0, Z1, normal=1)
    lights, coves = ceiling(b, M, -HW, HW, Z0, Z1, strips_x=(-1.15, 1.15),
                            downlight_rows=(-HW + 0.80, HW - 0.80))

    lifts_z = [22.05, 24.35, 26.65]
    D, N = -HW, +1                      # detail wall plane and its inward normal

    # ---- -X wall, near end to far end
    panel_run(b, M, "x", D, Z0, OPEN_Z0, N);  skirting(b, M, "x", D, Z0, OPEN_Z0, N)
    panel_run(b, M, "x", D, OPEN_Z1, 14.5, N); skirting(b, M, "x", D, OPEN_Z1, 14.5, N)
    double_door(b, M, D, 15.45, N)
    panel_run(b, M, "x", D, 16.40, 17.95, N); skirting(b, M, "x", D, 16.40, 17.95, N)
    double_door(b, M, D, 18.90, N)
    teal_pier(b, M, D, 19.85, 20.72, N)
    lo, hi = lift_bank(b, M, D, lifts_z, N)
    panel_run(b, M, "x", D, 20.72, lo, N);  skirting(b, M, "x", D, 20.72, lo, N)
    panel_run(b, M, "x", D, hi, Z1, N);     skirting(b, M, "x", D, hi, Z1, N)
    lift_side_kit(b, M, D + 0.022 * N, lo - 0.38, N, lcd=False)

    # ---- +X wall: mirrored lift bank, otherwise panelled
    lo2, hi2 = lift_bank(b, M, HW, lifts_z, -1)
    panel_run(b, M, "x", HW, Z0, lo2, -1);  skirting(b, M, "x", HW, Z0, lo2, -1)
    panel_run(b, M, "x", HW, hi2, Z1, -1);  skirting(b, M, "x", HW, hi2, Z1, -1)
    lift_side_kit(b, M, HW - 0.022, lo2 - 0.38, -1, lcd=False)

    # ---- near end wall
    panel_run(b, M, "z", Z0, -HW, HW, +1, mat=M["wall"], pitch=4.0, proud=0.004)
    skirting(b, M, "z", Z0, -HW, HW, +1)

    # ---- glazed end
    curtain_wall(b, M, Z1, -HW, HW)

    # ---- wood-clad piers framing the glazed end
    for sg in (-1, 1):
        for zz in (29.9, 32.3):
            x = sg * (HW - 0.55)
            box(b, M["dark"], (x - 0.44, 0.0, zz - 0.40), (x + 0.44, CEIL, zz + 0.40))
            panel_run(b, M, "x", x - 0.44, zz - 0.40, zz + 0.40, -1, pitch=0.80)
            panel_run(b, M, "x", x + 0.44, zz - 0.40, zz + 0.40, +1, pitch=0.80)
            panel_run(b, M, "z", zz - 0.40, x - 0.44, x + 0.44, -1, pitch=0.88)
            panel_run(b, M, "z", zz + 0.40, x - 0.44, x + 0.44, +1, pitch=0.88)
            box(b, M["skirt"], (x - 0.47, 0.0, zz - 0.43), (x + 0.47, SKIRT, zz + 0.43))

    # ---- projecting wood bulkhead at the near end, on the left of frame
    box(b, M["dark"], (HW - 1.5, 0.0, 4.2), (HW, CEIL, 8.2))
    panel_run(b, M, "x", HW - 1.5, 4.2, 8.2, -1)
    panel_run(b, M, "z", 4.2, HW - 1.5, HW, -1, pitch=0.75)
    panel_run(b, M, "z", 8.2, HW - 1.5, HW, +1, pitch=0.75)
    box(b, M["skirt"], (HW - 1.53, 0.0, 4.17), (HW, SKIRT, 8.23))

    # ---- suspended sign, kiosks, waiting seats
    hanging_sign(b, M, 10.0, xc=-0.25)
    kiosk(b, M, D + 0.06, 11.75, facing=+1)
    kiosk(b, M, D + 0.06, 13.30, facing=+1)
    bench(b, M, -2.95, 6.2, n=6, along="z", face=-1,
          colours=["seat_tan", "seat_tan", "seat_teal", "seat_tan", "seat_tan", "seat_teal"])
    bench(b, M, -2.95, 10.4, n=6, along="z", face=-1,
          colours=["seat_teal", "seat_tan", "seat_tan", "seat_teal", "seat_tan", "seat_tan"])
    bench(b, M, 2.75, 11.2, n=6, along="z", face=+1,
          colours=["seat_tan", "seat_teal", "seat_tan", "seat_tan", "seat_teal", "seat_tan"])
    return lights, coves


# ------------------------------------------------------------------ main

def build():
    b = Builder()
    M = materials()
    hl, hc = hall(b, M)
    rl, rc = reception(b, M)
    return b, M, hl + rl, hc + rc


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "output/hospital_corridor.glb"
    t = time.time()
    b, M, lights, coves = build()
    groups, tris = b.stats()
    sc = b.scene()
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    sc.export(out)
    import lights as lightrig
    n = lightrig.inject(out, lights, coves)
    mb = os.path.getsize(out) / 1e6
    print(f"{out}  {groups} materials  {tris} tris  {n} lights  {mb:.2f} MB"
          f"  ({time.time() - t:.1f}s)")
