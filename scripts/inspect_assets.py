"""Deep inspection of every supplied asset: bounds, parts, materials, textures."""
import os, glob, json
import numpy as np
import trimesh

FILES = sorted(glob.glob("assets/raw/*.glb")) + [
    "assets/extracted/glasses/scene.gltf",
    "assets/extracted/classschool/source/class school.obj",
]


def describe(path):
    print("=" * 78)
    print(path, f"({os.path.getsize(path)/1024:.0f} KB)")
    print("=" * 78)
    try:
        scene = trimesh.load(path, force="scene", process=False)
    except Exception as exc:
        print("  LOAD FAILED:", exc)
        return

    geoms = scene.geometry
    print(f"  geometries: {len(geoms)}   nodes: {len(scene.graph.nodes)}")
    try:
        b = scene.bounds
        print(f"  scene bounds min {np.round(b[0],3)}  max {np.round(b[1],3)}")
        print(f"  size {np.round(b[1]-b[0],3)}")
    except Exception:
        pass

    total_v = 0
    for name, g in list(geoms.items())[:12]:
        nv = len(g.vertices) if hasattr(g, "vertices") else 0
        total_v += nv
        mat_desc = "-"
        tex = "no"
        try:
            m = g.visual.material
            base = getattr(m, "baseColorFactor", None)
            if base is None:
                base = getattr(m, "diffuse", None)
            if base is not None:
                base = np.round(np.asarray(base, dtype=float), 3).tolist()
            img = getattr(m, "baseColorTexture", None) or getattr(m, "image", None)
            tex = "YES" if img is not None else "no"
            mat_desc = f"{getattr(m,'name','?')} base={base}"
        except Exception:
            pass
        gb = g.bounds if hasattr(g, "bounds") else None
        gbs = f"size={np.round(gb[1]-gb[0],2)}" if gb is not None else ""
        print(f"    - {name[:38]:38s} v={nv:6d} tex={tex:3s} {gbs}")
        print(f"        mat: {mat_desc}")
    if len(geoms) > 12:
        print(f"    ... and {len(geoms)-12} more")
    print(f"  total vertices (first 12): {total_v}")
    print()


for f in FILES:
    if os.path.exists(f):
        describe(f)
