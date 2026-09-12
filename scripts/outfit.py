"""Turn a style spec into the mesh list for one dressed avatar."""
import garments as G
from geom import CLOTH, DENIM, LEATHER, GLOSS, RUBBER
from compose import base_rig_mesh
from accessories import fit_hair, fit_cap, fit_glasses
from catalog import HAIR, HAIR_COLORS

FINISH = {"cloth": CLOTH, "denim": DENIM, "leather": LEATHER, "gloss": GLOSS, "rubber": RUBBER}

HEADWEAR = {
    "police": G.police_cap,
    "chef": G.chef_hat,
    "hardhat": G.hard_hat,
    "beanie": G.beanie,
    "grad": G.grad_cap,
    "turban": G.turban,
    "headscarf": G.headscarf,
    "visor": G.visor_cap,
}
# Headwear that encloses the skull; a headband does not, so hair stays with it.
COVERING_HEADWEAR = {"police", "chef", "hardhat", "beanie", "grad", "turban",
                     "headscarf", "visor", "baseball"}

MESH_CAPS = {
    "baseball": ("cap_baseball__Object_0", {}),
    "headband": ("hat_1__Object_6", {"overlap": 0.52, "grip": 1.10}),
}


def _top(s):
    """Torso layer + sleeves, per the spec's `top` recipe."""
    kind = s.get("top", "tee")
    c = s["top_color"]
    inner = s.get("inner_color", "#F0F1F3")
    sleeve = s.get("sleeve", "short")
    fin = FINISH[s.get("top_finish", "cloth")]
    out = []

    if kind == "dress":
        out += [G.torso_shell(c, finish=fin)]
        out += G.sleeves(c, sleeve, finish=fin)
        out += G.skirt(c, s.get("dress_length", "midi"), flare=s.get("flare", 1.55), finish=fin)
        return out

    if kind in ("tee", "polo", "shirt", "sweater", "tank", "kurta", "uniform"):
        y_lo = G.WAIST - (0.34 if kind == "kurta" else 0.0)
        out.append(G.torso_shell(c, y_lo=y_lo, finish=fin))
        out += G.sleeves(c, "cap" if kind == "tank" else sleeve, finish=fin)
        if kind in ("polo", "shirt", "uniform"):
            out += G.collar(s.get("collar_color", c), "shirt")
        if kind in ("shirt", "uniform"):
            out += G.placket(s.get("placket_color", c))
            out += G.buttons(s.get("button_color", (0.9, 0.9, 0.92)))
        if kind == "sweater":
            out += G.ribbing(c, hem=G.WAIST + 0.06,
                             sleeve_hem={"long": 2.10, "three_quarter": 2.61,
                                         "short": 3.28, "cap": 3.68}[sleeve])
        elif kind in ("tee", "tank"):
            hem = None if s.get("top") == "dress" else G.WAIST + 0.06
            out += G.ribbing(c, hem=hem,
                             sleeve_hem={"long": 2.10, "three_quarter": 2.61,
                                         "short": 3.28, "cap": 3.68}[
                                 "cap" if kind == "tank" else sleeve])
        return out

    if kind == "hoodie":
        out.append(G.torso_shell(c, pad=G.P_OUTER, y_lo=G.WAIST - 0.18, finish=fin))
        out += G.sleeves(c, "long", pad=G.P_OUTER, finish=fin)
        out += G.hood(s.get("hood_color", c), finish=fin)
        out += G.cuffs(c, pad=G.P_OUTER + 0.02)
        if s.get("zip"):
            out += G.zipper()
        out += G.pockets(s.get("pocket_color", c), y=2.42, w=0.52, h=0.44,
                         dx=0.40, pad=G.P_OUTER)
        return out

    if kind in ("jacket", "coat", "blazer"):
        out.append(G.torso_shell(inner, y_lo=G.WAIST, finish=CLOTH))
        out += G.sleeves(inner, "long")
        out += G.collar(s.get("collar_color", inner), "shirt")
        out += G.jacket(c, inner, open_front=s.get("open", True),
                        length=0.55 if kind == "coat" else 0.0, finish=fin)
        out += G.sleeves(c, "long", pad=G.P_OUTER, finish=fin)
        return out

    if kind == "vest_over":
        out.append(G.torso_shell(inner, finish=CLOTH))
        out += G.sleeves(inner, sleeve)
        out += G.vest(c, finish=fin)
        return out

    raise ValueError(f"unknown top: {kind}")


def _bottom(s):
    kind = s.get("bottom")
    if not kind:
        return []
    c = s["bottom_color"]
    fin = FINISH[s.get("bottom_finish", "cloth")]
    if kind.startswith("skirt"):
        return G.skirt(c, kind.split("_")[1] if "_" in kind else "short",
                       flare=s.get("flare", 1.6), finish=fin)
    return G.trousers(c, {"trousers": "long", "jeans": "long", "shorts": "shorts",
                          "capri": "capri"}[kind], finish=fin)


OUTER_TOPS = {"jacket", "coat", "blazer", "vest_over", "hoodie"}


def _extras(s):
    """Details sit on whichever layer is outermost, so they are never buried."""
    pad = G.P_OUTER if s.get("top") in OUTER_TOPS else G.P_SHIRT
    out = []
    for item in s.get("extras", []):
        kind, arg = (item, None) if isinstance(item, str) else (item[0], item[1])
        if kind == "tie":
            out += G.tie(arg, pad=pad)
        elif kind == "bow":
            out += G.tie(arg, "bow", pad=pad)
        elif kind == "belt":
            out += G.belt(arg)
        elif kind == "badge":
            out += G.badge(arg, pad=pad) if arg else G.badge(pad=pad)
        elif kind == "epaulettes":
            out += G.epaulettes(arg)
        elif kind == "pockets":
            out += G.pockets(arg, pad=pad)
        elif kind == "apron":
            out += G.apron(arg)
        elif kind == "scarf":
            out += G.scarf(arg)
        elif kind == "socks":
            out += G.socks(arg)
        elif kind == "cuffs":
            out += G.cuffs(arg)
        elif kind == "hivis":
            out += G.hivis_bands(arg, pad=pad)
    return out


def build(spec):
    """Full mesh list for one avatar: white rig, clothes, hair, headwear, glasses."""
    meshes = [base_rig_mesh()]
    meshes += _top(spec)
    meshes += _bottom(spec)
    if spec.get("shoe"):
        meshes += G.shoes(spec.get("shoe_color", "#232730"), spec["shoe"])
    meshes += _extras(spec)

    head = spec.get("head")
    head_kind = (head if isinstance(head, str) else head[0]) if head else None

    # A hat that encloses the skull replaces the hair rather than sitting on top
    # of it — a wig squeezed under a cap bulges out and swallows the face.
    hair = spec.get("hair")
    covered = head_kind in COVERING_HEADWEAR or spec.get("top") == "hoodie"
    if hair and not covered:
        col = HAIR_COLORS.get(spec.get("hair_color", "dark_brown"), spec.get("hair_color"))
        meshes.append(fit_hair(hair, color=col, **HAIR.get(hair, {})))

    if head:
        kind, opts = (head, {}) if isinstance(head, str) else head
        if kind in HEADWEAR:
            meshes += HEADWEAR[kind](**opts)
        elif kind in MESH_CAPS:
            key, base = MESH_CAPS[kind]
            meshes.append(fit_cap(key, **{**base, **opts}))

    if spec.get("glasses"):
        meshes += fit_glasses(**(spec["glasses"] if isinstance(spec["glasses"], dict) else {}))
    return meshes
