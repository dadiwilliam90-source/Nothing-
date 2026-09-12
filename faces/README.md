# faces/

Clean-line face textures and a way to see them on the avatars.

The style is deliberately plain: solid black shapes, one white glint per eye,
nothing else. No outlines, no shading, no scratch marks, no blush, no sweat —
at head size on a 3D avatar those details turn to mush, so there are none.

| face | look |
|------|------|
| `grin` | wide open smile, big round eyes — the default |
| `smug` | half-lidded eyes, one-sided smirk |
| `yell` | eyes screwed shut, mouth wide open |
| `deadpan` | small eyes, flat line mouth |

Each face is a `.svg` (source) plus a 1024x1024 `.png` with a transparent
background (what actually gets used).

## Changing or adding a face

Shapes live in `FACES` in `make_faces.py`, one SVG fragment each, drawn on a
512x512 grid — eyes around y=200, mouth around y=350. Add an entry and rerun:

```sh
python3 faces/make_faces.py          # -> faces/<name>.svg + .png
```

## Seeing it on an avatar

```sh
python3 scripts/render_face.py output/01_b_police_officer.glb faces/grin.png \
        faces/preview/out.png front,threequarter,side
python3 scripts/render_face.py output/01_b_police_officer.glb faces/grin.png \
        faces/preview/body.png front --full          # whole avatar
python3 scripts/render_face.py output/05_b_school_boy.glb \
        faces/grin.png,faces/smug.png,faces/yell.png,faces/deadpan.png \
        faces/preview/styles.png front --rig         # bare head, one per face
```

`render/face_viewer.html` hangs the texture on a quad in front of the head,
anchored to the fixed `Head` box in `assets/rig_anchors.json`. The quad is
bowed back at its edges so it sits on the rounded head instead of floating off
the corners, and it is nudged slightly below head centre — several of the hair
pieces hang low enough to cover eyes placed dead centre.

## What this does not touch

`scripts/build_all.py` is unchanged and the 50 GLBs in `output/` still have
blank faces, as the root README says. Faces are applied at render time only.
