"""Render a labelled contact sheet of accessory items so they can be judged visually."""
import os, sys, json, glob, urllib.parse
from PIL import Image, ImageDraw
from render import _start_server, CHROME, ROOT
from playwright.sync_api import sync_playwright

COLS, CELL = 8, 230


def sheet(paths, out, angle=0.78, cols=COLS, cell=CELL, focus=""):
    port = _start_server()
    rel = ["../" + os.path.relpath(os.path.abspath(p), ROOT).replace(os.sep, "/") for p in paths]
    rows = (len(paths) + cols - 1) // cols
    q = urllib.parse.urlencode(dict(items=json.dumps(rel), cols=cols, cell=cell,
                                    angle=angle, focus=focus))
    url = f"http://127.0.0.1:{port}/render/contact.html?{q}"
    tmp = out + ".raw.png"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=CHROME,
                               args=["--use-gl=angle", "--use-angle=swiftshader",
                                     "--enable-unsafe-swiftshader", "--no-sandbox"])
        pg = b.new_page(viewport={"width": cols * cell, "height": rows * cell},
                        device_scale_factor=1.6)
        pg.goto(url)
        pg.wait_for_function("window.__READY__ === true", timeout=180000)
        pg.locator("canvas").screenshot(path=tmp)
        b.close()

    img = Image.open(tmp).convert("RGB")
    sc = img.width / (cols * cell)
    d = ImageDraw.Draw(img)
    for i, p in enumerate(paths):
        c, r = i % cols, i // cols
        x, y = c * cell * sc, r * cell * sc
        label = os.path.basename(p).replace(".glb", "")
        label = label.replace("Object_", "O").replace("__", " ")
        d.rectangle([x, y, x + cell * sc, y + 19], fill=(24, 28, 36))
        d.text((x + 5, y + 5), f"{i:02d} {label}", fill=(255, 255, 255))
        d.rectangle([x, y, x + cell * sc - 1, y + cell * sc - 1], outline=(196, 202, 212))
    img.save(out)
    os.remove(tmp)
    return out


if __name__ == "__main__":
    pats = sys.argv[1]
    out = sys.argv[2]
    angle = float(sys.argv[3]) if len(sys.argv) > 3 else 0.78
    focus = "head" if "--head" in sys.argv else ""
    paths = sorted(glob.glob(pats))
    print(sheet(paths, out, angle=angle, focus=focus), len(paths), "items")
