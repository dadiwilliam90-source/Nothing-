"""Procedural flat-coloured clothing that hugs the white R6 rig.

Every garment is built from measured rig anchors, so nothing floats or clips.
No textures anywhere — solid colour plus PBR roughness does the work.
"""
import numpy as np
import rig as R
from geom import (rbox, cyl, sphere, ellipsoid, rotate, taper,
                  CLOTH, DENIM, LEATHER, METAL, GLOSS, RUBBER)

TX, TY, TZ = R.TORSO["center"]
TW, TH, TD = R.TORSO["size"]
SHOULDER = TY + TH / 2          # 4.0
WAIST = TY - TH / 2             # 2.0
FRONT_Z = TZ - TD / 2           # -10.352
BACK_Z = TZ + TD / 2            # -9.352

ARMS = [R.R_ARM, R.L_ARM]
LEGS = [R.R_LEG, R.L_LEG]

P_SHIRT = 0.045                 # base layer padding
P_OUTER = 0.115                 # jacket / coat padding


# ---------------------------------------------------------------- tops
def torso_shell(color, pad=P_SHIRT, y_lo=WAIST, y_hi=SHOULDER, finish=CLOTH, r=0.07):
    return rbox((TX, (y_lo + y_hi) / 2, TZ),
                (TW + 2 * pad, y_hi - y_lo, TD + 2 * pad),
                color, radius=r, finish=finish, name="top")


SEAM = 0.006   # inner-edge inset that keeps the limb/torso seam readable


def sleeves(color, length="long", pad=P_SHIRT, finish=CLOTH):
    """Sleeves pad outward only, so the shoulder seam is not swallowed by the shirt."""
    y_hi = SHOULDER + pad * 0.5
    y_lo = {"long": 2.04, "three_quarter": 2.55, "short": 3.22, "cap": 3.62}[length]
    out = []
    for a in ARMS:
        ax, _, az = a["center"]
        aw, _, ad = a["size"]
        outward = 1 if ax > TX else -1
        x_lo = ax - aw / 2 - (pad if outward < 0 else SEAM)
        x_hi = ax + aw / 2 + (pad if outward > 0 else SEAM)
        out.append(rbox(((x_lo + x_hi) / 2, (y_lo + y_hi) / 2, az),
                        (x_hi - x_lo, y_hi - y_lo, ad + 2 * pad),
                        color, radius=0.07, finish=finish, name="sleeve"))
    return out


def cuffs(color, y=2.12, h=0.17, pad=P_SHIRT + 0.022, finish=CLOTH):
    return [rbox((a["center"][0], y, a["center"][2]),
                 (a["size"][0] + 2 * pad, h, a["size"][2] + 2 * pad),
                 color, radius=0.05, finish=finish, name="cuff") for a in ARMS]


def collar(color, kind="shirt", pad=P_SHIRT + 0.03, finish=CLOTH):
    """Neckline band; 'shirt' adds two angled points at the front."""
    y = SHOULDER - 0.085
    out = [rbox((TX, y, TZ), (TW + 2 * pad, 0.19, TD + 2 * pad),
                color, radius=0.045, finish=finish, name="collar")]
    if kind == "shirt":
        for sx in (-1, 1):
            p = rbox((TX + sx * 0.30, y - 0.10, FRONT_Z - 0.035),
                     (0.46, 0.30, 0.07), color, radius=0.028, finish=finish, name="collar_pt")
            out.append(rotate(p, sx * 22, [0, 0, 1], (TX + sx * 0.30, y, FRONT_Z)))
    return out


def placket(color, finish=CLOTH):
    """Button strip down the shirt front."""
    return [rbox((TX, 3.05, FRONT_Z - P_SHIRT - 0.015), (0.17, 1.72, 0.05),
                 color, radius=0.022, finish=finish, name="placket")]


def buttons(color=(0.92, 0.92, 0.92), n=4, y0=3.62, dy=0.36, finish=GLOSS):
    return [cyl((TX, y0 - i * dy, FRONT_Z - P_SHIRT - 0.055), 0.048, 0.035,
                color, axis="z", finish=finish, name="button") for i in range(n)]


def lapels(color, finish=CLOTH):
    out = []
    for sx in (-1, 1):
        p = rbox((TX + sx * 0.335, 3.45, FRONT_Z - P_OUTER - 0.028),
                 (0.40, 0.86, 0.065), color, radius=0.03, finish=finish, name="lapel")
        out.append(rotate(p, sx * 15, [0, 0, 1], (TX + sx * 0.20, SHOULDER - 0.1, FRONT_Z)))
    return out


def jacket(color, shirt_color, open_front=True, length=0.0, finish=CLOTH):
    """Open blazer / coat: outer shell, inner shirt V, lapels."""
    y_lo = WAIST - length
    out = [torso_shell(color, pad=P_OUTER, y_lo=y_lo, y_hi=SHOULDER + 0.012,
                       finish=finish, r=0.085)]
    if open_front:
        out.append(rbox((TX, 3.30, FRONT_Z - P_OUTER - 0.005), (0.50, 1.42, 0.05),
                        shirt_color, radius=0.03, finish=CLOTH, name="shirt_v"))
        out += lapels(color, finish)
    return out


def hood(color, finish=CLOTH):
    hx, hy, hz = R.HEAD["center"]
    return [rbox((hx, hy + 0.02, hz + 0.60), (1.44, 1.22, 0.70),
                 color, radius=0.20, finish=finish, name="hood"),
            rbox((TX, SHOULDER - 0.02, TZ + 0.30), (1.52, 0.34, 0.60),
                 color, radius=0.12, finish=finish, name="hood_base")]


def zipper(color=(0.78, 0.79, 0.82), y_lo=2.05, y_hi=3.90, finish=METAL):
    return [rbox((TX, (y_lo + y_hi) / 2, FRONT_Z - P_OUTER - 0.02),
                 (0.085, y_hi - y_lo, 0.04), color, radius=0.02,
                 finish=finish, name="zip")]


def vest(color, finish=CLOTH):
    out = []
    for sx in (-1, 1):
        out.append(rbox((TX + sx * 0.615, 3.02, TZ),
                        (0.80, 1.90, TD + 2 * P_OUTER), color,
                        radius=0.07, finish=finish, name="vest"))
    out.append(rbox((TX, 3.02, BACK_Z + P_OUTER - 0.02), (TW + 2 * P_OUTER, 1.90, 0.13),
                    color, radius=0.055, finish=finish, name="vest_back"))
    return out


def apron(color, finish=CLOTH):
    return [rbox((TX, 2.55, FRONT_Z - P_SHIRT - 0.05), (1.42, 1.62, 0.08),
                 color, radius=0.05, finish=finish, name="apron"),
            rbox((TX, 3.60, FRONT_Z - P_SHIRT - 0.05), (0.72, 0.70, 0.07),
                 color, radius=0.045, finish=finish, name="apron_bib")]


def pockets(color, y=2.85, w=0.40, h=0.36, dx=0.46, finish=CLOTH, pad=P_SHIRT):
    return [rbox((TX + sx * dx, y, FRONT_Z - pad - 0.035), (w, h, 0.06),
                 color, radius=0.028, finish=finish, name="pocket") for sx in (-1, 1)]


def epaulettes(color, finish=CLOTH):
    return [rbox((TX + sx * 0.80, SHOULDER - 0.03, TZ), (0.44, 0.10, 0.62),
                 color, radius=0.035, finish=finish, name="epaulette") for sx in (-1, 1)]


def badge(color=(0.86, 0.70, 0.22), y=3.42, dx=-0.52, finish=METAL, pad=P_SHIRT):
    return [rbox((TX + dx, y, FRONT_Z - pad - 0.06), (0.20, 0.26, 0.05),
                 color, radius=0.03, finish=finish, name="badge")]


def tie(color, kind="tie", finish=GLOSS, pad=P_SHIRT):
    z = FRONT_Z - pad - 0.055
    if kind == "bow":
        out = [rbox((TX, 3.83, z), (0.17, 0.16, 0.07), color, radius=0.035,
                    finish=finish, name="bow_knot")]
        for sx in (-1, 1):
            out.append(rbox((TX + sx * 0.24, 3.83, z), (0.32, 0.26, 0.06),
                            color, radius=0.045, finish=finish, name="bow"))
        return out
    knot = rbox((TX, 3.80, z), (0.19, 0.20, 0.08), color, radius=0.035,
                finish=finish, name="knot")
    blade = rbox((TX, 3.14, z), (0.23, 1.16, 0.06), color, radius=0.028,
                 finish=finish, name="tie")
    taper(blade, 0.55, axis=0, along=1)
    return [knot, blade]


def scarf(color, finish=CLOTH):
    out = [rbox((TX, SHOULDER - 0.12, TZ), (TW + 0.22, 0.30, TD + 0.24),
                color, radius=0.10, finish=finish, name="scarf")]
    out.append(rbox((TX + 0.34, 3.32, FRONT_Z - 0.09), (0.26, 0.86, 0.10),
                    color, radius=0.05, finish=finish, name="scarf_tail"))
    return out


# ---------------------------------------------------------------- bottoms
def trousers(color, length="long", pad=P_SHIRT, finish=CLOTH):
    y_hi = WAIST + 0.06
    y_lo = {"long": 0.10, "capri": 0.72, "shorts": 1.08, "brief": 1.45}[length]
    out = []
    for lg in LEGS:
        lx, _, lz = lg["center"]
        lw, _, ld = lg["size"]
        outward = 1 if lx > TX else -1
        x_lo = lx - lw / 2 - (pad if outward < 0 else SEAM)
        x_hi = lx + lw / 2 + (pad if outward > 0 else SEAM)
        out.append(rbox(((x_lo + x_hi) / 2, (y_lo + y_hi) / 2, lz),
                        (x_hi - x_lo, y_hi - y_lo, ld + 2 * pad),
                        color, radius=0.07, finish=finish, name="trouser"))
    out.append(rbox((TX, WAIST + 0.02, TZ), (TW + 2 * pad, 0.30, TD + 2 * pad),
                    color, radius=0.06, finish=finish, name="hip"))
    return out


def skirt(color, length="short", flare=1.62, finish=CLOTH):
    y_hi = WAIST + 0.08
    y_lo = {"mini": 1.35, "short": 1.06, "midi": 0.62, "long": 0.18}[length]
    m = rbox((TX, (y_lo + y_hi) / 2, TZ),
             (TW + 0.14, y_hi - y_lo, TD + 0.14), color, radius=0.06,
             finish=finish, name="skirt")
    taper(m, flare, axis=0, along=1, pivot=TX)
    taper(m, flare, axis=2, along=1, pivot=TZ)
    return [m]


def belt(color, buckle=(0.83, 0.68, 0.25), pad=P_SHIRT + 0.03, finish=LEATHER):
    out = [rbox((TX, WAIST + 0.10, TZ), (TW + 2 * pad, 0.20, TD + 2 * pad),
                color, radius=0.04, finish=finish, name="belt")]
    if buckle:
        out.append(rbox((TX, WAIST + 0.10, FRONT_Z - pad - 0.035), (0.26, 0.20, 0.06),
                        buckle, radius=0.025, finish=METAL, name="buckle"))
    return out


def shoes(color, kind="shoe", finish=LEATHER):
    h = {"shoe": 0.26, "boot": 0.74, "sneaker": 0.30, "heel": 0.22}[kind]
    out = []
    for lg in LEGS:
        lx, _, lz = lg["center"]
        lw, _, ld = lg["size"]
        outward = 1 if lx > TX else -1
        x_lo = lx - lw / 2 - (0.05 if outward < 0 else SEAM)
        x_hi = lx + lw / 2 + (0.05 if outward > 0 else SEAM)
        out.append(rbox(((x_lo + x_hi) / 2, h / 2, lz - 0.10),
                        (x_hi - x_lo, h, ld + 0.30), color,
                        radius=0.075, finish=finish, name="shoe"))
        if kind == "sneaker":
            out.append(rbox((lx, 0.055, lz - 0.10), (lw + 0.14, 0.11, ld + 0.34),
                            (0.94, 0.94, 0.95), radius=0.045, finish=RUBBER, name="sole"))
        if kind == "heel":
            out.append(rbox((lx, 0.17, lz + 0.34), (0.14, 0.34, 0.14),
                            color, radius=0.035, finish=finish, name="heel"))
    return out


def socks(color, y_hi=0.92, finish=CLOTH):
    return [rbox((lg["center"][0], (0.12 + y_hi) / 2, lg["center"][2]),
                 (lg["size"][0] + 0.09, y_hi - 0.12, lg["size"][2] + 0.09),
                 color, radius=0.055, finish=finish, name="sock") for lg in LEGS]


# ---------------------------------------------------------------- procedural headwear
HX, HY, HZ = R.HEAD["center"]
HTOP = R.HEAD_TOP
HW, HD = R.HEAD["size"][0], R.HEAD["size"][2]
H_FRONT = R.HEAD_FRONT
H_BACK = HZ + HD / 2


def police_cap(color="#1B2740", band="#0C1120", peak="#0A0E18", emblem=(0.86, 0.70, 0.22)):
    """Peaked service cap: band grips the skull, crown flares, peak shades the face."""
    return [
        rbox((HX, HTOP - 0.24, HZ), (HW + 0.14, 0.30, HD + 0.14), band,
             radius=0.055, name="cap_band"),
        rbox((HX, HTOP + 0.03, HZ + 0.03), (HW + 0.24, 0.32, HD + 0.24), color,
             radius=0.10, name="cap_crown"),
        rbox((HX, HTOP - 0.30, H_FRONT - 0.22), (HW + 0.20, 0.09, 0.58), peak,
             radius=0.033, finish=GLOSS, name="cap_peak"),
        rbox((HX, HTOP - 0.01, H_FRONT - 0.07), (0.24, 0.26, 0.05), emblem,
             radius=0.028, finish=METAL, name="cap_badge"),
    ]


def chef_hat(color="#F4F5F7"):
    out = [cyl((HX, HTOP - 0.02, HZ), HW * 0.56, 0.46, color, axis="y", name="chef_band")]
    for i, (dx, dz, rr) in enumerate([(0, 0, 0.46), (-0.27, 0.09, 0.33), (0.27, 0.09, 0.33),
                                      (0, -0.27, 0.31), (0, 0.29, 0.30)]):
        out.append(sphere((HX + dx, HTOP + 0.44, HZ + dz), rr, color, name=f"chef_puff{i}"))
    return out


def hard_hat(color="#E8B411", brim=None):
    brim = brim or color
    return [
        sphere((HX, HTOP - 0.20, HZ + 0.02), 0.70, color, finish=GLOSS, name="helmet"),
        rbox((HX, HTOP - 0.23, HZ - 0.06), (HW + 0.30, 0.09, HD + 0.46), brim,
             radius=0.042, finish=GLOSS, name="helmet_brim"),
        rbox((HX, HTOP + 0.16, HZ + 0.02), (0.15, 0.22, HD + 0.24), color,
             radius=0.05, finish=GLOSS, name="helmet_ridge"),
    ]


def beanie(color="#3A4A63", cuff=None):
    cuff = cuff or color
    return [
        rbox((HX, HTOP - 0.18, HZ), (HW + 0.11, 0.62, HD + 0.11), color,
             radius=0.21, name="beanie"),
        rbox((HX, HTOP - 0.42, HZ), (HW + 0.16, 0.22, HD + 0.16), cuff,
             radius=0.085, name="beanie_cuff"),
        sphere((HX, HTOP + 0.16, HZ), 0.145, cuff, name="beanie_pom"),
    ]


def grad_cap(color="#14161E", tassel=(0.86, 0.70, 0.22)):
    return [
        rbox((HX, HTOP - 0.14, HZ), (HW + 0.09, 0.34, HD + 0.09), color,
             radius=0.075, name="grad_skull"),
        rbox((HX, HTOP + 0.065, HZ), (1.78, 0.07, 1.78), color,
             radius=0.03, name="grad_board"),
        rbox((HX + 0.60, HTOP + 0.155, HZ - 0.20), (0.06, 0.09, 0.06), tassel,
             radius=0.025, name="tassel_knot"),
        rbox((HX + 0.62, HTOP - 0.10, HZ - 0.22), (0.065, 0.42, 0.065), tassel,
             radius=0.028, name="tassel"),
    ]


def turban(color="#D8DCE4", knot=None):
    """One smooth wrapped dome plus a front knot — no visible stacking seams."""
    knot = knot or color
    dome = ellipsoid((HX, HTOP - 0.24, HZ), (HW + 0.30, 1.00, HD + 0.30), color, name="turban")
    band = rbox((HX, HTOP - 0.30, HZ), (HW + 0.32, 0.24, HD + 0.32), color,
                radius=0.10, name="turban_band")
    return [dome, band,
            rbox((HX, HTOP - 0.05, H_FRONT - 0.09), (0.30, 0.28, 0.17), knot,
                 radius=0.08, name="turban_knot")]


def headscarf(color="#8E3F56", trim=None):
    """Hijab-style wrap: one shell set back from the face, brow band, shoulder drape."""
    trim = trim or color
    return [
        ellipsoid((HX, HY - 0.04, HZ + 0.30), (HW + 0.38, 1.86, HD + 0.46), color,
                  name="scarf_shell"),
        rbox((HX, HTOP - 0.26, H_FRONT + 0.03), (HW + 0.30, 0.30, 0.24), trim,
             radius=0.10, name="scarf_brow"),
        rbox((HX, HY - 0.80, HZ + 0.26), (HW + 0.30, 0.66, HD + 0.44), color,
             radius=0.20, name="scarf_drape"),
    ]


def visor_cap(color="#243046", peak=None):
    """Simple procedural baseball-style cap (used when a mesh cap is not wanted)."""
    peak = peak or color
    return [
        rbox((HX, HTOP - 0.10, HZ + 0.02), (HW + 0.16, 0.46, HD + 0.16), color,
             radius=0.17, name="cap_crown"),
        rbox((HX, HTOP - 0.26, H_FRONT - 0.22), (HW - 0.04, 0.08, 0.54), peak,
             radius=0.035, name="cap_peak"),
        rbox((HX, HTOP + 0.11, HZ + 0.02), (0.09, 0.09, 0.09), peak,
             radius=0.035, name="cap_button"),
    ]
