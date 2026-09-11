# 50 Roblox-style avatars on one white rig

25 boys and 25 girls, each built on the supplied white R6 rig. The rig itself is
never modified — only flat-coloured clothing and head accessories differ between
avatars. Faces are left completely blank.

Output: `output/NN_<b|g>_<style>.glb` — 50 files.

## Rules this follows

- The white rig is byte-identical in every avatar (verified: 671 verts, same bounds).
- Clothing is solid colour only — no fabric textures anywhere.
- No facial features or expressions are ever added.
- Hair, caps and glasses sit on the head correctly, not floating or clipping.

## Rebuilding

```sh
pip install trimesh pygltflib numpy pillow scipy networkx
python3 scripts/build_all.py            # all 50 -> output/
python3 scripts/build_all.py police_officer school_girl   # just these
```

Previews (needs `playwright` + the bundled three.js in `render/`):

```sh
python3 scripts/render.py output/01_b_police_officer.glb preview/out.png
python3 scripts/contact_sheet.py 'output/*_b_*.glb' preview/boys.png 0.86
```

## How the rig was measured

`scripts/analyze_rig.py` splits the supplied `robox_rig.glb` into connected
components and recovers standard R6 proportions, which `scripts/rig.py` then
hard-codes as anchors:

| part  | centre                 | size              |
|-------|------------------------|-------------------|
| torso | (-5.39, 3.00, -9.852)  | 2.00 x 2.00 x 1.00 |
| head  | (-5.39, 4.50, -9.766)  | 1.20 x 1.20 x 1.02 |
| arm   | (±1.5 from centre)     | 1.00 x 2.00 x 1.00 |
| leg   | (±0.5 from centre)     | 1.00 x 2.00 x 1.00 |

The avatar faces **-Z**, up is **+Y**, its right hand is **+X**, feet at y = 0.

## Fitting the supplied accessories

This was the hard part. The hair/hat packs are authored at arbitrary scale,
position and yaw, so nothing can be placed by a fixed transform. Each item is
re-anchored from its own geometry (`scripts/accessories.py`):

- **Hair** — `_cap_profile` scans Y-slices of the upper mesh and finds the band
  that actually grips the skull, ignoring ponytails and length. Width is matched
  to the head plus a hair-thickness allowance, then clamped so no wig balloons
  past the head or towers over it. The front edge is anchored to the face, so
  hair always falls backwards instead of through it.
- **Caps** — measured by the crown band and parked a fixed distance below the
  top of the head, so they grip rather than hover.
- **Glasses** — the widest horizontal axis is detected (and rotated into place if
  the model was authored sideways), then seated on the front face at eye level.

Textured accessories are re-tinted through their own luminance
(`accessories.recolor`), so strand detail survives an arbitrary colour change
instead of being flattened.

## Clothing

`scripts/garments.py` builds every garment from rounded boxes whose corner radius
matches the rig's own bevel, so clothes never look like raw cubes. Padding is
applied **outward only** on sleeves, trousers and shoes, which keeps the
limb/torso seams readable instead of fusing the figure into one slab.

Pieces available: tee, polo, shirt, sweater, tank, kurta, uniform, hoodie,
blazer, jacket, coat, vest, dress; trousers, jeans, shorts, capri, skirts;
shoes, boots, sneakers, heels; collar, placket, buttons, lapels, tie, bow tie,
belt, pockets, epaulettes, badge, apron, scarf, socks, cuffs, hi-vis bands.

Headwear is procedural where the supplied packs had no equivalent: peaked
service cap, chef hat, hard hat, beanie, graduation cap, turban, headscarf,
visor cap. The supplied baseball cap and headband meshes are used directly.

Colours are converted **sRGB -> linear** before being written to
`baseColorFactor`; glTF stores that value in linear space, and skipping the
conversion is what makes flat colours look washed out.

## Layout

```
assets/raw/        the supplied GLBs, renamed
assets/items/      each accessory pack split into individual items
scripts/           rig measurement, garments, fitting, styles, build, render
render/            three.js viewer used for headless previews
output/            the 50 avatar GLBs
preview/           contact sheets from the review passes
```

## Credit

`assets/raw/base_rig.glb` is "Robox Rig" by
[thomaslfraser2018](https://sketchfab.com/thomaslfraser2018), CC-BY-4.0.
The other supplied packs carry their own licences in `assets/extracted/`.
