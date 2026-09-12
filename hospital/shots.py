"""Headless renders of the corridor from the five reference camera angles."""
import os, sys, threading, functools, http.server, socketserver, urllib.parse
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# Cameras chosen to line up with the five supplied renders.
SHOTS = {
    # 1: three-quarter view onto the +X lift bank and the teal pier
    "a_lifts":    dict(pos=(2.45, 1.62, 14.2), tgt=(-4.60, 1.42, 23.6), fov=52),
    # 2: symmetric view down the hall to the glazed end, sign overhead
    "b_hall":     dict(pos=(0.10, 1.62, 2.6),  tgt=(0.15, 1.42, 40.0), fov=58),
    # 3: kiosks and the near waiting area
    "c_kiosks":   dict(pos=(0.30, 1.32, 6.4),  tgt=(-4.60, 1.12, 14.4), fov=54),
    # 4: wider, seating in the foreground
    "d_seating":  dict(pos=(1.60, 1.50, 3.4),  tgt=(-3.40, 1.14, 13.2), fov=60),
    # 5: reception counter and queue displays
    "e_reception": dict(pos=(-7.40, 1.55, 11.6), tgt=(-15.8, 1.22, 4.4), fov=56),
}


def _serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv.server_address[1]


def render(glb, outdir, names=None, w=1000, h=600, **over):
    port = _serve()
    rel = os.path.relpath(os.path.abspath(glb), ROOT).replace(os.sep, "/")
    os.makedirs(outdir, exist_ok=True)
    picks = names or list(SHOTS)
    out = []
    with sync_playwright() as pw:
        br = pw.chromium.launch(executable_path=CHROME,
                                args=["--use-gl=angle", "--use-angle=swiftshader",
                                      "--enable-unsafe-swiftshader", "--no-sandbox"])
        page = br.new_page(viewport={"width": w, "height": h})
        for name in picks:
            s = dict(SHOTS[name]); s.update(over)
            q = urllib.parse.urlencode(dict(
                src="../" + rel, w=w, h=h, fov=s["fov"],
                pos=",".join(str(v) for v in s["pos"]),
                tgt=",".join(str(v) for v in s["tgt"]),
                **{k: v for k, v in s.items()
                   if k in ("expo", "amb", "hemi", "sun", "env", "lint", "emi")}))
            page.goto(f"http://127.0.0.1:{port}/render/interior.html?{q}")
            page.wait_for_function("window.__READY__ === true", timeout=120000)
            err = page.evaluate("window.__ERROR__ || null")
            if err:
                raise RuntimeError(f"{name}: {err}")
            p = os.path.join(outdir, f"{name}.png")
            page.locator("canvas").screenshot(path=p)
            out.append(p)
            print("  ", p, "lights:", page.evaluate("window.__LIGHTS__"))
        br.close()
    return out


if __name__ == "__main__":
    glb = sys.argv[1] if len(sys.argv) > 1 else "output/hospital_corridor.glb"
    outd = sys.argv[2] if len(sys.argv) > 2 else "preview/hospital"
    names = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    render(glb, outd, names)
