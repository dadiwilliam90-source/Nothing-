"""Preview faces/ textures on an avatar head. Sibling of render.py."""
import os, sys, urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from playwright.sync_api import sync_playwright
from render import ROOT, CHROME, _start_server


def render_faces(glb, faces, out, views="front", w=420, h=480,
                 full=False, rigonly=False):
    """One cell per (face, view). Paths are repo-relative."""
    port = _start_server()
    rel = os.path.relpath(os.path.abspath(glb), ROOT).replace(os.sep, "/")
    q = urllib.parse.urlencode(dict(
        src="../" + rel, faces=",".join("../" + f for f in faces),
        views=views, w=w, h=h,
        full="1" if full else "0", rigonly="1" if rigonly else "0"))
    url = f"http://127.0.0.1:{port}/render/face_viewer.html?{q}"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    cells = max(1, len(faces)) * len(views.split(","))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=CHROME,
            args=["--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader", "--no-sandbox"])
        page = browser.new_page(viewport={"width": w * cells, "height": h},
                                device_scale_factor=2)
        page.goto(url)
        page.wait_for_function("window.__READY__ === true", timeout=90000)
        err = page.evaluate("window.__ERROR__ || null")
        if err:
            raise RuntimeError(err)
        page.locator("canvas").screenshot(path=out)
        browser.close()
    return out


if __name__ == "__main__":
    a = [x for x in sys.argv[1:] if not x.startswith("--")]
    flags = [x for x in sys.argv[1:] if x.startswith("--")]
    glb = a[0] if a else "output/05_b_school_boy.glb"
    faces = a[1].split(",") if len(a) > 1 else ["faces/grin.png"]
    out = a[2] if len(a) > 2 else "faces/preview/out.png"
    views = a[3] if len(a) > 3 else "front"
    print(render_faces(glb, faces, out, views=views,
                       full="--full" in flags, rigonly="--rig" in flags))
