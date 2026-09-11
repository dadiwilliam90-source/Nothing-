"""Headless GLB previews via three.js in Chromium. Used to visually verify fit."""
import os, sys, threading, functools, http.server, socketserver, urllib.parse
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
_server = None
_port = None


def _start_server():
    global _server, _port
    if _server:
        return _port
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    _server = socketserver.TCPServer(("127.0.0.1", 0), handler)
    _port = _server.server_address[1]
    threading.Thread(target=_server.serve_forever, daemon=True).start()
    return _port


def render(glb, out, views="front,threequarter,side,back", w=420, h=560, head=False):
    """Render one GLB to a PNG contact strip. Returns the output path."""
    port = _start_server()
    rel = os.path.relpath(os.path.abspath(glb), ROOT).replace(os.sep, "/")
    q = urllib.parse.urlencode(
        dict(src="../" + rel, views=views, w=w, h=h, head="1" if head else "0"))
    url = f"http://127.0.0.1:{port}/render/viewer.html?{q}"
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            executable_path=CHROME,
            args=["--use-gl=angle", "--use-angle=swiftshader",
                  "--enable-unsafe-swiftshader", "--no-sandbox"])
        page = browser.new_page(viewport={"width": w * len(views.split(",")), "height": h},
                                device_scale_factor=2)
        errs = []
        page.on("pageerror", lambda e: errs.append(str(e)))
        page.goto(url)
        page.wait_for_function("window.__READY__ === true", timeout=90000)
        err = page.evaluate("window.__ERROR__ || null")
        if err:
            raise RuntimeError(f"load error for {glb}: {err}")
        page.locator("canvas").screenshot(path=out)
        browser.close()
    if errs:
        print("  js errors:", errs[:2], file=sys.stderr)
    return out


if __name__ == "__main__":
    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "preview/out.png"
    head = "--head" in sys.argv
    print(render(src, dst, head=head,
                 views="front,threequarter,side" if head else "front,threequarter,side,back"))
