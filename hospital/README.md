# Hospital 2F elevator hall — 3D model

`output/hospital_corridor.glb` — a reconstruction of the hospital circulation
floor shown in the five supplied renders: the elevator hall with its teal
wayfinding pier, the suspended directional sign, the self-service kiosks and
waiting seating, and the adjoining reception hall with its queue displays.

    python3 hospital/build.py output/hospital_corridor.glb   # build the GLB
    python3 hospital/shots.py output/hospital_corridor.glb preview/hospital

| | |
|---|---|
| triangles | 26,314 |
| materials | 37, one draw call each |
| textures | 28, all generated procedurally at build time |
| lights | 93 real `KHR_lights_punctual` fixtures |
| size | 1.83 MB |
| units | metres, Y up, hall along +Z |

## What is and is not claimed

The supplied images are renders of an existing 3D scene. No tool can recover
that scene's original meshes from five JPEGs — photogrammetry needs far more
coverage and cannot invert a render's lighting — so this is **not** the
original file. It is a fresh model built to match what the images show:
the same layout and sequence of elements along each wall, the same
proportions, the same palette, the same signage wording, and an equivalent
lighting rig.

Two differences are renderer-side rather than model-side. The references were
made with a global-illumination renderer, so their polished floor mirrors the
walls and their shadows are softly bounced. The GLB carries the materials that
produce that (a 0.22-roughness floor, real light fixtures); how much of it you
see depends on the viewer. Opened in a path tracer such as Blender's Cycles it
comes much closer than it does in the real-time preview in `preview/hospital/`.

## Layout

Everything is in metres. The hall is 9.2 m wide and 3.18 m to the ceiling.

```
z = 34      glazed curtain wall, six bays, lit backdrop beyond
z = 30,32   wood-clad piers framing the glazed end
z = 22..27  lift banks, three cars on each side wall
z = 19.9    teal pier carrying the '2.' and the pictogram stack
z = 18.9    grey double door
z = 15.5    grey double door
z = 11..13  self-service kiosks
z = 10      suspended teal directional sign
z = 6..11   waiting seating, held to the sides so the centre stays clear
z = 0.9..3.3 passage into the reception bay (off the -X side)
```

The detailed wall is **-X**. Looking down the hall along +Z, screen-right is
-X, and that is the wall carrying the lifts, pier, doors and kiosks in every
reference frame. Getting this backwards mirrors the whole composition, so it
is verified by render (`preview/hospital/b_hall.png`) rather than reasoned
about.

## Files

```
hospital/kit.py        geometry emitters, materials, per-material batching
hospital/textures.py   every texture, drawn with PIL at build time
hospital/build.py      the scene: dimensions, elements, assembly
hospital/lights.py     injects KHR_lights_punctual after export
hospital/shots.py      headless renders from the five reference angles
render/interior.html   three.js interior viewer used for those renders
```

## Notes on the tricky parts

**UV orientation.** Signage must read correctly on a wall whichever way that
wall faces, and it kept coming out mirrored. Deriving UVs from corner order is
the trap: `quad` reverses the winding when a face's normal points the wrong
way, and the texture then reads from behind. `rect` therefore derives UVs from
**world position**, and mirrors U on exactly the two facings where the viewer
stands on the other side (+X-facing and -Z-facing walls). The rule was settled
by rendering a known-asymmetric texture on all four facings rather than by
reasoning, after two wrong guesses.

**Texture V direction.** trimesh flips V on GLB export, so V runs with the
surface's up direction here. Written the other way, every sign is upside down.

**Colour space.** Flat colours go through `hexc`, sRGB to linear, because
glTF stores `baseColorFactor` linear. Skipping it turns the deep teal pier
into pale mint.

**Metals need something to reflect.** The lift doors and chrome first rendered
black: a metallic surface with no environment reflects nothing. The viewer
synthesises a small interior environment with `PMREMGenerator`, since no
`RoomEnvironment` is vendored here.

**Lighting balance.** 93 fixtures at nominal candela blew the whole hall to
white. The fix was not exposure — a file that needs the viewer stopped down
two thirds is a broken file — so both the punctual intensities and the
emissive factors were scaled down until the model reads correctly at exposure
1.0. The floor went last: it faces the ceiling, so the hemisphere light and
the environment's luminous ceiling were both landing on it at full strength
while the walls looked right.

**Panel joints are geometry.** Wood panelling is discrete boards standing
22 mm proud of a dark backing, not a painted line, so the shadow gaps behave
under raking light.

## Textures

No photographs: oak veneer (vertical grain with cathedral figures), terrazzo
(9,000 aggregate chips), brushed stainless, ceiling tile, wall paint, hazy
exterior, and the drawn artwork — the teal pier, the directional sign, five
red dot-matrix queue displays, the lift advert screens, the kiosk UI, the call
plates and the car-position readouts. Latin text is Liberation Sans, CJK is
WenQuanYi Zen Hei.

The directional sign auto-shrinks its three labels to fit the span left of the
`2F` cap, so no label can collide with it.
