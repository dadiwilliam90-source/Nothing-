"""Procedural textures for the corridor, generated with PIL at build time.

Nothing here is a photograph — grain, speckle, signage and screen UI are all
synthesised, so the GLB carries no third-party image rights and every texture
can be retuned by changing a constant.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

from kit import hexs

LATIN = "/usr/share/fonts/truetype/liberation/LiberationSans-%s.ttf"
CJK = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
_cache = {}


def font(size, bold=False, cjk=False):
    key = (size, bold, cjk)
    if key not in _cache:
        path = CJK if cjk else LATIN % ("Bold" if bold else "Regular")
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def _rgb(h):
    return tuple(int(v * 255) for v in hexs(h))


def _noise(w, h, octaves=((4, 1.0), (16, 0.5), (64, 0.25)), seed=0):
    """Cheap multi-octave value noise in 0..1 by upsampling random grids."""
    rng = np.random.default_rng(seed)
    acc = np.zeros((h, w), dtype=np.float32)
    total = 0.0
    for res, amp in octaves:
        gh, gw = max(2, h // res), max(2, w // res)
        g = rng.random((gh, gw)).astype(np.float32)
        img = Image.fromarray((g * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
        acc += np.asarray(img, dtype=np.float32) / 255.0 * amp
        total += amp
    acc /= total
    return (acc - acc.min()) / max(float(np.ptp(acc)), 1e-6)


def _tint(gray, dark, light):
    """Map a 0..1 field onto a colour ramp between two hex colours."""
    d = np.array(_rgb(dark), dtype=np.float32)
    l = np.array(_rgb(light), dtype=np.float32)
    out = d[None, None, :] + gray[:, :, None] * (l - d)[None, None, :]
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))


# ------------------------------------------------------------- materials

def wood_veneer(size=768, seed=3):
    """Light oak veneer: fine vertical grain with a few stronger cathedral lines.

    Tiles along the panel height; the grain runs vertically as in the
    reference, which is what makes the piers read as veneer rather than paint.
    """
    rng = np.random.default_rng(seed)
    w = h = size
    x = np.arange(w, dtype=np.float32)
    # Base streaks: 1D noise across the grain, stretched down the panel.
    base = _noise(w, 8, octaves=((2, 1.0), (8, 0.6), (28, 0.35)), seed=seed)[0]
    field = np.repeat(base[None, :], h, axis=0)
    # Gentle waviness so lines are not perfectly straight.
    wob = np.sin(np.linspace(0, 5.0, h))[:, None] * 3.0
    idx = np.clip((x[None, :] + wob).astype(int), 0, w - 1)
    field = np.take_along_axis(field, idx, axis=1)
    # A handful of darker cathedral figures.
    for _ in range(7):
        c = rng.integers(0, w)
        wdt = rng.integers(4, 16)
        prof = np.exp(-((x - c) ** 2) / (2 * wdt ** 2))
        field -= prof[None, :] * rng.uniform(0.10, 0.26)
    field += (_noise(w, h, octaves=((3, 1.0), (11, 0.5)), seed=seed + 1) - 0.5) * 0.10
    field = np.clip(field, 0, 1)
    img = _tint(field, "#A67E4E", "#D6BB92")
    return img.filter(ImageFilter.GaussianBlur(0.4))


def wood_counter(size=512):
    """Slightly warmer, denser veneer for the reception counter front."""
    f = _noise(size, size, octaves=((2, 1.0), (9, 0.55), (30, 0.3)), seed=11)
    f = np.clip(f * 0.8 + 0.15, 0, 1)
    return _tint(f, "#C09A6A", "#E4CCA4").filter(ImageFilter.GaussianBlur(0.5))


def terrazzo(size=512, seed=7):
    """Polished speckled floor: pale warm grey with fine dark/light chips."""
    rng = np.random.default_rng(seed)
    w = h = size
    base = _noise(w, h, octaves=((24, 1.0), (80, 0.4)), seed=seed)
    arr = np.asarray(_tint(base * 0.5 + 0.4, "#9C9A95", "#B6B4AF"), dtype=np.float32)
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    # Aggregate chips. Small and low-contrast: the floor reads near-plain at
    # human distance and only shows its speckle close up, as in the reference.
    for _ in range(9000):
        cx, cy = rng.integers(0, w), rng.integers(0, h)
        r = rng.uniform(0.6, 2.1)
        g = rng.normal(0.5, 0.26)
        if g < 0.34:
            col = _rgb("#7E7C77")
        elif g > 0.72:
            col = _rgb("#C8C6C1")
        else:
            col = _rgb("#A6A49F")
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    return img.filter(ImageFilter.GaussianBlur(0.35))


def ceiling_panel(size=256):
    """Near-white metal ceiling tile with a faint tonal drift."""
    f = _noise(size, size, octaves=((16, 1.0), (48, 0.3)), seed=21)
    return _tint(f * 0.35 + 0.6, "#DAD8D4", "#ECEBE8")


def wall_paint(size=256):
    f = _noise(size, size, octaves=((20, 1.0),), seed=31)
    return _tint(f * 0.3 + 0.65, "#E6E4E0", "#F4F3F1")


def exterior(w=1024, h=512):
    """Hazy daylight backdrop seen through the curtain wall.

    The reference shows a flat, overcast, low-contrast view — distant slab
    blocks in fog. Keeping it desaturated stops the glazing from stealing
    attention from the interior.
    """
    img = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(img)
    for y in range(h):
        t = y / h
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip(_rgb("#D8DDE2"), _rgb("#C3C8CC")))
        d.line([(0, y), (w, y)], fill=c)
    rng = np.random.default_rng(5)
    horizon = int(h * 0.72)
    # Distant buildings, fading into haze with distance.
    for depth, (fade, hmax) in enumerate([(0.30, 0.30), (0.55, 0.22), (0.85, 0.14)]):
        x = -20
        while x < w:
            bw = rng.integers(40, 130)
            bh = int(h * rng.uniform(0.06, hmax))
            col = tuple(int(a + (b - a) * (1 - fade)) for a, b in
                        zip(_rgb("#9AA3AC"), _rgb("#CDD3D8")))
            d.rectangle([x, horizon - bh, x + bw, horizon], fill=col)
            x += bw + rng.integers(6, 40)
    d.rectangle([0, horizon, w, h], fill=_rgb("#CFD2D3"))       # apron / paving
    d.rectangle([0, horizon, w, horizon + 6], fill=_rgb("#BFC4C7"))
    return img.filter(ImageFilter.GaussianBlur(1.6))


# -------------------------------------------------------------- signage

TEAL = "#0C5155"
TEAL_LIGHT = "#12676B"


def _pictogram(d, kind, x, y, s, col=(255, 255, 255)):
    """Small white wayfinding glyphs, drawn from primitives at any size."""
    def E(cx, cy, r): d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)
    def R(a, b, c, e): d.rectangle([a, b, c, e], fill=col)
    if kind == "toilet":                       # two figures side by side
        R(x + .22 * s, y + .34 * s, x + .34 * s, y + .70 * s)
        E(x + .28 * s, y + .22 * s, .09 * s)
        d.polygon([(x + .52 * s, y + .34 * s), (x + .74 * s, y + .34 * s),
                   (x + .80 * s, y + .70 * s), (x + .46 * s, y + .70 * s)], fill=col)
        E(x + .63 * s, y + .22 * s, .09 * s)
    elif kind == "lift":                       # car with up/down arrows
        R(x + .20 * s, y + .18 * s, x + .80 * s, y + .82 * s)
        d.rectangle([x + .26 * s, y + .24 * s, x + .74 * s, y + .76 * s],
                    fill=_rgb(TEAL))
        d.polygon([(x + .38 * s, y + .46 * s), (x + .31 * s, y + .58 * s),
                   (x + .45 * s, y + .58 * s)], fill=col)
        d.polygon([(x + .62 * s, y + .58 * s), (x + .55 * s, y + .46 * s),
                   (x + .69 * s, y + .46 * s)], fill=col)
    elif kind == "stairs":                      # figure descending steps
        for i in range(3):
            R(x + (.18 + .18 * i) * s, y + (.42 + .14 * i) * s,
              x + (.40 + .18 * i) * s, y + (.50 + .14 * i) * s)
        E(x + .30 * s, y + .22 * s, .07 * s)
        R(x + .26 * s, y + .30 * s, x + .36 * s, y + .46 * s)
    elif kind == "wheelchair":
        E(x + .50 * s, y + .20 * s, .08 * s)
        R(x + .44 * s, y + .30 * s, x + .54 * s, y + .52 * s)
        d.ellipse([x + .28 * s, y + .42 * s, x + .76 * s, y + .88 * s],
                  outline=col, width=max(2, int(.05 * s)))
        R(x + .44 * s, y + .50 * s, x + .70 * s, y + .57 * s)


def floor_pier(w=448, h=1700):
    """The tall teal pier: pictogram stack, big '2.', small blue plate.

    Laid out in fractions of the panel so the artwork stays correct if the
    pier is resized in the model. Icon column sits right, numeral left, their
    vertical centres aligned — as in the reference.
    """
    img = Image.new("RGB", (w, h), _rgb(TEAL))
    d = ImageDraw.Draw(img)

    icon = int(w * 0.30)
    ix = int(w * 0.58)
    gap = icon * 1.32
    iy = int(h * 0.085)
    for i, k in enumerate(("toilet", "lift", "stairs", "wheelchair")):
        _pictogram(d, k, ix, iy + i * gap, icon)

    # Numeral centred on the icon stack, with its full stop tight to the glyph.
    stack_mid = iy + (1.5 * gap) + icon * 0.5
    f = font(int(w * 0.58), bold=False)
    num_x = int(w * 0.10)
    d.text((num_x, stack_mid), "2", font=f, fill=(255, 255, 255), anchor="lm")
    nw = d.textlength("2", font=f)
    dot = w * 0.052
    d.ellipse([num_x + nw + dot * 0.35, stack_mid + f.size * 0.30,
               num_x + nw + dot * 0.35 + dot, stack_mid + f.size * 0.30 + dot],
              fill=(255, 255, 255))

    # Small pale-blue service plate low on the pier.
    d.rounded_rectangle([int(w * 0.20), int(h * 0.615), int(w * 0.60), int(h * 0.645)],
                        radius=int(w * 0.025), fill=_rgb("#9FCBD6"))
    return img


def hanging_sign(w=2048, h=268):
    """Suspended directional sign, white on teal, with a bold 2F end cap.

    The three labels are measured and auto-shrunk to fit the span left of the
    2F cap, so no label can ever collide with it.
    """
    img = Image.new("RGB", (w, h), _rgb(TEAL))
    d = ImageDraw.Draw(img)
    white = (255, 255, 255)
    cy = h // 2
    cap_x = w - int(w * 0.115)               # divider rule before the 2F cap
    x_start = int(w * 0.035)
    avail = cap_x - x_start - int(w * 0.03)

    items = [("Discharge and admission", "left"),
             ("Elevator hall", "up"),
             ("Reception area", "right")]

    # Shrink until the three labels plus their arrows and gaps fit the span.
    size = int(h * 0.245)
    while size > 8:
        f = font(size)
        s = h * 0.15
        gap = w * 0.035
        total = sum(d.textlength(t, font=f) + s * 2.4 for t, _ in items) + gap * 2
        if total <= avail:
            break
        size -= 2
    f = font(size)
    s = h * 0.15
    gap = (avail - sum(d.textlength(t, font=f) + s * 2.4 for t, _ in items)) / 2

    def arrow(cx, direction):
        if direction == "left":
            d.polygon([(cx - s, cy), (cx - s * 0.30, cy - s * 0.62),
                       (cx - s * 0.30, cy + s * 0.62)], fill=white)
            d.rectangle([cx - s * 0.34, cy - s * 0.15, cx + s * 0.82, cy + s * 0.15], fill=white)
        elif direction == "right":
            d.polygon([(cx + s, cy), (cx + s * 0.30, cy - s * 0.62),
                       (cx + s * 0.30, cy + s * 0.62)], fill=white)
            d.rectangle([cx - s * 0.82, cy - s * 0.15, cx + s * 0.34, cy + s * 0.15], fill=white)
        else:
            d.polygon([(cx, cy - s), (cx - s * 0.62, cy - s * 0.30),
                       (cx + s * 0.62, cy - s * 0.30)], fill=white)
            d.rectangle([cx - s * 0.15, cy - s * 0.34, cx + s * 0.15, cy + s * 0.82], fill=white)

    x = x_start
    for text, direction in items:
        tw = d.textlength(text, font=f)
        if direction == "right":
            d.text((x, cy), text, font=f, fill=white, anchor="lm")
            arrow(x + tw + s * 1.3, "right")
        else:
            arrow(x + s, direction)
            d.text((x + s * 2.4, cy), text, font=f, fill=white, anchor="lm")
        x += tw + s * 2.4 + gap

    d.line([(cap_x, int(h * 0.17)), (cap_x, int(h * 0.83))], fill=(148, 186, 189), width=2)
    d.text(((cap_x + w) / 2, cy + int(h * 0.02)), "2F", font=font(int(h * 0.62)),
           fill=white, anchor="mm")
    return img


def led_panel(text, w=768, h=168, scale=1.0):
    """Red dot-matrix queue display on black, wrapped to fit the panel."""
    img = Image.new("RGB", (w, h), (12, 10, 10))
    d = ImageDraw.Draw(img)
    red = (232, 42, 28)
    size = int(h * 0.265 * scale)
    f = font(size, bold=True)
    words, lines, cur = text.split(), [], ""
    for wd in words:
        t = (cur + " " + wd).strip()
        if d.textlength(t, font=f) > w * 0.92 and cur:
            lines.append(cur); cur = wd
        else:
            cur = t
    lines.append(cur)
    lines = lines[:3]
    lh = size * 1.30
    y0 = h / 2 - lh * (len(lines) - 1) / 2
    for i, ln in enumerate(lines):
        d.text((w * 0.04, y0 + i * lh), ln, font=f, fill=red, anchor="lm")
    # Scanline gaps so it reads as an LED matrix rather than printed text.
    for y in range(0, h, 3):
        d.line([(0, y), (w, y)], fill=(6, 5, 5))
    return img


def floor_indicator(text="7", w=256, h=128):
    """Small red car-position readout above each lift door."""
    img = Image.new("RGB", (w, h), (16, 15, 15))
    d = ImageDraw.Draw(img)
    f = font(int(h * 0.66), bold=True)
    red = (236, 40, 26)
    d.text((w * 0.40, h * 0.52), text, font=f, fill=red, anchor="mm")
    cx, cy, s = w * 0.66, h * 0.52, h * 0.24
    d.polygon([(cx, cy + s), (cx - s * 0.62, cy - s * 0.15),
               (cx + s * 0.62, cy - s * 0.15)], fill=red)
    for y in range(0, h, 3):
        d.line([(0, y), (w, y)], fill=(8, 7, 7))
    return img


def lift_lcd(w=512, h=768):
    """The vertical advert screen beside each lift: a light medical promo."""
    img = Image.new("RGB", (w, h), (236, 246, 250))
    d = ImageDraw.Draw(img)
    for y in range(int(h * 0.62)):                       # sky-blue gradient top
        t = y / (h * 0.62)
        c = tuple(int(a + (b - a) * t) for a, b in
                  zip(_rgb("#37A6D8"), _rgb("#BFE4F2")))
        d.line([(0, y), (w, y)], fill=c)
    rng = np.random.default_rng(9)
    for _ in range(16):                                   # soft bokeh circles
        cx, cy = rng.integers(0, w), rng.integers(0, int(h * 0.6))
        r = rng.integers(10, 46)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=_rgb("#8FD2EC"))
    # Stylised clinician group along the lower third.
    for i, (cx, col) in enumerate([(0.24, "#F2F6F8"), (0.5, "#E8F0F4"), (0.76, "#F2F6F8")]):
        x = w * cx
        d.ellipse([x - w * .085, h * .50, x + w * .085, h * .50 + w * .17],
                  fill=_rgb("#F6D9BE"))
        d.polygon([(x - w * .15, h * .78), (x + w * .15, h * .78),
                   (x + w * .11, h * .62), (x - w * .11, h * .62)], fill=_rgb(col))
    d.rectangle([0, int(h * 0.78), w, h], fill=_rgb("#F4FAFC"))
    d.rectangle([0, int(h * 0.78), w, int(h * 0.795)], fill=_rgb("#1B8FC4"))
    f = font(int(h * 0.048), cjk=True)
    d.text((w / 2, h * 0.845), "健康服务 关爱生命", font=f, fill=_rgb("#0E6E99"), anchor="mm")
    d.text((w / 2, h * 0.915), "门诊服务中心", font=font(int(h * 0.038), cjk=True),
           fill=_rgb("#6E8896"), anchor="mm")
    return img


def kiosk_screen(w=768, h=1024):
    """Self-service terminal UI: header, colourful function grid, footer."""
    img = Image.new("RGB", (w, h), (244, 248, 250))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, int(h * 0.13)], fill=_rgb("#1C7FA8"))
    d.text((w / 2, h * 0.065), "自助服务终端", font=font(int(h * 0.052), cjk=True),
           fill=(255, 255, 255), anchor="mm")
    tiles = [("#3FAE6A", "挂号"), ("#2E86C8", "缴费"), ("#E8873B", "查询"),
             ("#D6558E", "报告"), ("#26A9A2", "预约"), ("#E2B93B", "充值"),
             ("#7B68C4", "建档"), ("#4FA8D8", "打印"), ("#E06666", "退费")]
    pad, cols = w * 0.045, 3
    tw = (w - pad * (cols + 1)) / cols
    th = tw * 0.86
    for i, (col, label) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = pad + c * (tw + pad)
        y = h * 0.19 + r * (th + pad * 0.8)
        d.rounded_rectangle([x, y, x + tw, y + th], radius=int(tw * 0.12), fill=_rgb(col))
        d.text((x + tw / 2, y + th * 0.66), label,
               font=font(int(th * 0.20), cjk=True), fill=(255, 255, 255), anchor="mm")
        d.rounded_rectangle([x + tw * .36, y + th * .16, x + tw * .64, y + th * .42],
                            radius=int(tw * .05), fill=(255, 255, 255))
    d.rounded_rectangle([pad, h * 0.88, w - pad, h * 0.955],
                        radius=int(w * 0.02), fill=_rgb("#CFE0EA"))
    d.text((w / 2, h * 0.917), "请点击您需要办理的业务",
           font=font(int(h * 0.032), cjk=True), fill=_rgb("#2A607C"), anchor="mm")
    return img


def call_plate(w=128, h=384):
    """Lift call station: brushed plate, two buttons, small floor readout."""
    img = Image.new("RGB", (w, h), _rgb("#C8CACC"))
    d = ImageDraw.Draw(img)
    for y in range(h):                                   # faint brushed banding
        if y % 4 == 0:
            d.line([(0, y), (w, y)], fill=_rgb("#BFC2C4"))
    d.rounded_rectangle([w * .12, h * .06, w * .88, h * .30],
                        radius=int(w * .08), fill=(24, 24, 26))
    d.text((w / 2, h * .18), "7", font=font(int(h * .17), bold=True),
           fill=(232, 48, 30), anchor="mm")
    for i, cy in enumerate((0.48, 0.72)):
        d.ellipse([w * .22, h * (cy - .085), w * .78, h * (cy + .085)],
                  fill=_rgb("#E8E9EA"), outline=_rgb("#9DA0A2"), width=2)
        s = w * .16
        cx, yy = w / 2, h * cy
        if i == 0:
            d.polygon([(cx, yy - s * .55), (cx - s * .55, yy + s * .35),
                       (cx + s * .55, yy + s * .35)], fill=_rgb("#3E7FA8"))
        else:
            d.polygon([(cx, yy + s * .55), (cx - s * .55, yy - s * .35),
                       (cx + s * .55, yy - s * .35)], fill=_rgb("#3E7FA8"))
    return img


def brushed_steel(size=512):
    """Vertically brushed stainless for lift doors and jambs."""
    rng = np.random.default_rng(13)
    col = rng.normal(0.5, 0.055, size=(1, size)).astype(np.float32)
    arr = np.repeat(np.clip(col, 0, 1), size, axis=0)
    arr += (_noise(size, size, octaves=((6, 1.0),), seed=17) - 0.5) * 0.07
    return _tint(np.clip(arr, 0, 1), "#7C8084", "#A9ACAF")
