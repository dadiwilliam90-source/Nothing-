"""Split the supplied accessory packs into individual items and catalogue them."""
import json, os
import numpy as np
import trimesh

PACKS = {
    "hair_1": "assets/raw/hair_1.glb",
    "hair_2": "assets/raw/hair_2.glb",
    "hair_3": "assets/raw/hair_3.glb",
    "hat_1": "assets/raw/hat_1.glb",
    "cap_baseball": "assets/raw/cap_baseball.glb",
    "glasses": "assets/extracted/glasses/scene.gltf",
    "hoodie": "assets/raw/hoodie.glb",
}

OUT = "assets/items"
os.makedirs(OUT, exist_ok=True)
catalog = []

for pack, path in PACKS.items():
    if not os.path.exists(path):
        continue
    scene = trimesh.load(path, force="scene", process=False)
    for name, geom in scene.geometry.items():
        # bake the node transform so bounds are world-correct
        try:
            T, _ = scene.graph.get(scene.graph.geometry_nodes[name][0])
        except Exception:
            T = np.eye(4)
        m = geom.copy()
        m.apply_transform(T)
        b = m.bounds
        size = (b[1] - b[0]).tolist()
        key = f"{pack}__{name}"
        item = dict(key=key, pack=pack, mesh=name, verts=int(len(m.vertices)),
                    size=[round(v, 4) for v in size],
                    center=[round(v, 4) for v in ((b[0] + b[1]) / 2).tolist()],
                    aspect=round(size[0] / max(size[1], 1e-6), 3))
        catalog.append(item)
        m.export(f"{OUT}/{key}.glb")

with open("assets/accessory_catalog.json", "w") as f:
    json.dump(catalog, f, indent=2)

print(f"{len(catalog)} items extracted to {OUT}/\n")
for c in catalog:
    flag = ""
    sx, sy, sz = c["size"]
    if max(sx, sy, sz) > 6:
        flag = "  <-- oversized / likely a prop or stand"
    if c["verts"] < 100:
        flag += "  <-- very low poly"
    print(f"  {c['key']:34s} v={c['verts']:6d} size={np.round(c['size'],2)}{flag}")
