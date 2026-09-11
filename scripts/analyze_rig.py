"""Segment the white base rig into named R6 body parts and dump anchor data."""
import json
import numpy as np
import trimesh

scene = trimesh.load("assets/raw/base_rig.glb", force="scene", process=False)
mesh = trimesh.util.concatenate([g for g in scene.dump()])
print("merged mesh:", len(mesh.vertices), "verts", len(mesh.faces), "faces")
print("bounds:\n", np.round(mesh.bounds, 4))

parts = mesh.split(only_watertight=False)
print(f"\nconnected components: {len(parts)}")
info = []
for i, p in enumerate(parts):
    b = p.bounds
    c = (b[0] + b[1]) / 2
    s = b[1] - b[0]
    info.append(dict(i=i, center=c.tolist(), size=s.tolist(), verts=len(p.vertices)))
    print(f"  [{i}] v={len(p.vertices):5d} center={np.round(c,3)} size={np.round(s,3)}")

# Classify using standard Roblox R6 layout.
# Y = up (height 0..5.1), X = left/right (width 4.0), Z = depth (1.2)
labels = {}
if len(parts) >= 6:
    ys = np.array([p.bounds.mean(axis=0)[1] for p in parts])
    xs = np.array([p.bounds.mean(axis=0)[0] for p in parts])
    widths = np.array([(p.bounds[1] - p.bounds[0])[0] for p in parts])

    order_y = np.argsort(-ys)
    head_i = int(order_y[0])
    labels[head_i] = "Head"

    remaining = [i for i in range(len(parts)) if i not in labels]
    # torso = widest remaining part in upper half
    upper = [i for i in remaining if ys[i] > ys.mean()]
    torso_i = int(max(upper, key=lambda i: widths[i])) if upper else int(
        max(remaining, key=lambda i: widths[i]))
    labels[torso_i] = "Torso"

    remaining = [i for i in range(len(parts)) if i not in labels]
    upper_rem = sorted([i for i in remaining if ys[i] > ys[torso_i] - 0.2], key=lambda i: xs[i])
    lower_rem = sorted([i for i in remaining if i not in upper_rem], key=lambda i: xs[i])
    if len(upper_rem) == 2:
        labels[upper_rem[0]] = "RightArm"
        labels[upper_rem[1]] = "LeftArm"
    if len(lower_rem) == 2:
        labels[lower_rem[0]] = "RightLeg"
        labels[lower_rem[1]] = "LeftLeg"

print("\n=== CLASSIFIED PARTS ===")
anchors = {}
for i, p in enumerate(parts):
    name = labels.get(i, f"Part{i}")
    b = p.bounds
    anchors[name] = dict(
        min=b[0].tolist(), max=b[1].tolist(),
        center=((b[0] + b[1]) / 2).tolist(), size=(b[1] - b[0]).tolist())
    print(f"  {name:10s} center={np.round((b[0]+b[1])/2,3)} size={np.round(b[1]-b[0],3)}")

anchors["_rig"] = dict(min=mesh.bounds[0].tolist(), max=mesh.bounds[1].tolist(),
                       size=(mesh.bounds[1] - mesh.bounds[0]).tolist())
with open("assets/rig_anchors.json", "w") as f:
    json.dump(anchors, f, indent=2)
print("\nwrote assets/rig_anchors.json")
