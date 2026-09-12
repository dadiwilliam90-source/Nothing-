# Pip

A simple 2D character with an idle loop. Thick black outlines, flat fills,
noodle limbs — drawn from scratch, not traced from anything.

| file | what it is |
|------|------------|
| `pip.svg` | the master. Vector + CSS animation, transparent, sharp at any size |
| `pip.gif` | 400x540, 40 frames, 2s loop — the one that plays anywhere |
| `pip.webp` | 800x1080 animated, transparent background |
| `pip.png` | 1200x1620 still, transparent |
| `pip_frames.png` | four poses from the loop, to check the motion at a glance |

## The loop

2 seconds: a bounce, the head tilting with it, arms swinging out of phase,
the ground shadow tightening as he rises, and one blink near the end.

Every animation shares that one 2s duration and carries **no delay of its
own** — per-element timing is baked into keyframe percentages instead. That
is what makes frame capture possible: pausing everything and setting a single
negative `animation-delay` freezes the whole character at any instant.

```css
.an{animation-play-state:paused; animation-delay:-1.15s}   /* frame at t=1.15s */
```

## Rebuilding

```sh
pip install playwright pillow
python3 character/build.py
```

Timing lives at the top of `build.py` (`LOOP`, `FPS`) and in the `@keyframes`
in `pip.svg`. Colours are the `#suit` gradient plus the flat fills in the
markup — change those and rerun.

## Limbs

Arms and legs are single paths stroked twice: a fat black stroke, then a
thinner coloured one over it. One path per limb, outline included, and the
round caps give the hands and feet their shape for free.
