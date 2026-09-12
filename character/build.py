"""Render pip.svg to a still, an animated GIF and an animated WebP.

Every animation in the SVG shares one 2s duration and carries no delay of its
own, so a frame is captured by pausing all of them and setting a single
negative animation-delay.
"""
import os, shutil, sys
from PIL import Image
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
SRC = "pip.svg"
W, H = 400, 540
LOOP, FPS = 2.0, 20
BG = (62, 127, 146)


def capture(scale, out_dir, n):
    """Transparent RGBA frames, one per step of the loop."""
    html = os.path.join(HERE, ".build.html")
    open(html, "w").write(
        f'<style>html,body{{margin:0;width:{W}px;height:{H}px;'
        f'background:transparent;overflow:hidden}}</style>'
        + open(os.path.join(HERE, SRC)).read())
    paths = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME, args=["--no-sandbox"])
        pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
        pg.goto("file://" + html)
        pg.add_style_tag(content=".an{animation-play-state:paused!important;"
                                 "animation-delay:var(--t)!important}")
        for i in range(n):
            pg.evaluate("t => document.documentElement.style.setProperty('--t', t)",
                        f"-{i / FPS:.4f}s")
            p = os.path.join(out_dir, f"f{i:03d}.png")
            pg.screenshot(path=p, omit_background=True)
            paths.append(p)
        b.close()
    os.remove(html)
    return paths


def flatten(im, bg):
    out = Image.new("RGB", im.size, bg)
    out.paste(im, mask=im.split()[3])
    return out


def main():
    tmp = os.path.join(HERE, ".frames")
    shutil.rmtree(tmp, ignore_errors=True)
    os.makedirs(tmp)
    n = int(round(LOOP * FPS))
    delay = int(round(1000 / FPS))

    shutil.move(capture(3, tmp, 1)[0], os.path.join(HERE, "pip.png"))
    print(f"pip.png    {W*3}x{H*3}  transparent still")

    frames = [Image.open(p).convert("RGBA") for p in capture(2, tmp, n)]

    frames[0].save(os.path.join(HERE, "pip.webp"), save_all=True,
                   append_images=frames[1:], duration=delay, loop=0,
                   quality=92, method=6)
    print(f"pip.webp   {frames[0].width}x{frames[0].height}  transparent, {n} frames")

    # GIF has no soft alpha, so flatten onto a background before quantising
    gw = 400
    gif = [flatten(f, BG).resize((gw, round(gw * H / W)), Image.LANCZOS)
           .quantize(colors=96, method=Image.MEDIANCUT, dither=Image.FLOYDSTEINBERG)
           for f in frames]
    gif[0].save(os.path.join(HERE, "pip.gif"), save_all=True,
                append_images=gif[1:], duration=delay, loop=0, optimize=True)
    print(f"pip.gif    {gif[0].width}x{gif[0].height}  {n} frames @ {FPS}fps")

    # contact strip, to eyeball that the pose actually changes across the loop
    picks = [frames[i] for i in (0, n // 4, n // 2, 3 * n // 4)]
    strip = Image.new("RGB", (picks[0].width * 4, picks[0].height), BG)
    for i, f in enumerate(picks):
        strip.paste(f, (i * f.width, 0), f)
    strip.resize((strip.width // 2, strip.height // 2), Image.LANCZOS) \
         .save(os.path.join(HERE, "pip_frames.png"))
    print("pip_frames.png  4 poses from the loop")

    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
