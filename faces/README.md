# faces/

Standalone hand-inked face artwork. **Not** used by `scripts/build_all.py` — the
50 avatars in `output/` still ship with blank faces, exactly as the root README
says. These files are art assets you can upload as a decal yourself.

| file | what it is |
|------|------------|
| `scratch_manic.svg` / `.png` | the full picture: grey head + face, white background |
| `scratch_manic_decal.svg` / `.png` | face only, transparent background — this is the one to upload as a Roblox decal |

Style: flat 2D (no shading, no gradients), rough ink strokes wobbled with an SVG
turbulence/displacement filter, deliberately asymmetric. Everything is vector, so
re-render at any size:

```sh
chromium --headless --screenshot=out.png --window-size=1024,1024 \
         --default-background-color=00000000 faces/scratch_manic_decal.svg
```
