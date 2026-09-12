"""Emit the clean-line face textures. No deps: writes SVG, Chromium rasterises."""
import os, subprocess, sys

W = 512
INK = "#151515"
OUT = os.path.dirname(os.path.abspath(__file__))
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"


def eye_open(cx, cy, rx=46, ry=57, gx=-17, gy=-20, gr=16):
    return (f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{INK}"/>'
            f'<circle cx="{cx+gx}" cy="{cy+gy}" r="{gr}" fill="#fff"/>')


FACES = {
    # wide, delighted — the default
    "grin": f'''
  {eye_open(166, 198)}
  {eye_open(346, 198)}
  <path d="M132,300 C196,288 316,288 380,300 C382,378 328,424 256,424
           C184,424 130,378 132,300 Z" fill="{INK}"/>''',

    # half-lidded, one-sided smirk
    "smug": f'''
  <path d="M118,196 C118,196 176,190 226,204 C226,246 198,266 172,262
           C142,257 118,230 118,196 Z" fill="{INK}"/>
  <path d="M286,204 C336,190 394,196 394,196 C394,230 370,257 340,262
           C314,266 286,246 286,204 Z" fill="{INK}"/>
  <circle cx="160" cy="228" r="13" fill="#fff"/>
  <circle cx="334" cy="228" r="13" fill="#fff"/>
  <path d="M170,344 C218,392 316,388 358,326" fill="none" stroke="{INK}"
        stroke-width="24" stroke-linecap="round"/>''',

    # eyes screwed shut, mouth wide — the loud one
    "yell": f'''
  <path d="M112,214 C142,166 198,166 228,214" fill="none" stroke="{INK}"
        stroke-width="26" stroke-linecap="round"/>
  <path d="M284,214 C314,166 370,166 400,214" fill="none" stroke="{INK}"
        stroke-width="26" stroke-linecap="round"/>
  <path d="M150,300 C196,282 322,282 366,300 C388,352 350,430 256,430
           C162,430 128,352 150,300 Z" fill="{INK}"/>''',

    # flat, unimpressed
    "deadpan": f'''
  {eye_open(166, 198, 40, 40, -14, -14, 13)}
  {eye_open(346, 198, 40, 40, -14, -14, 13)}
  <path d="M186,356 L326,356" fill="none" stroke="{INK}"
        stroke-width="22" stroke-linecap="round"/>''',
}


def svg(body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {W}" '
            f'width="{W}" height="{W}">{body}\n</svg>\n')


def main(px=1024):
    for name, body in FACES.items():
        s = os.path.join(OUT, f"{name}.svg")
        open(s, "w").write(svg(body))
        html = os.path.join(OUT, f".{name}.html")
        open(html, "w").write(
            f'<style>html,body{{margin:0;width:{px}px;height:{px}px;overflow:hidden}}'
            f'svg{{width:{px}px;height:{px}px}}</style>' + svg(body))
        subprocess.run([CHROME, "--headless", "--disable-gpu", "--no-sandbox",
                        "--hide-scrollbars", "--default-background-color=00000000",
                        f"--window-size={px},{px}",
                        f"--screenshot={os.path.join(OUT, name + '.png')}",
                        "file://" + html], check=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        os.remove(html)
        print("wrote", name)


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 1024)
