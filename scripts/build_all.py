"""Build every avatar GLB from styles.py into output/."""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from outfit import build
from compose import export
from styles import ALL
import rig as R

OUT = os.path.join(R.ROOT, "output")


def main(only=None):
    os.makedirs(OUT, exist_ok=True)
    t0 = time.time()
    for i, spec in enumerate(ALL, 1):
        if only and spec["name"] not in only:
            continue
        tag = "b" if spec["sex"] == "boy" else "g"
        path = os.path.join(OUT, f"{i:02d}_{tag}_{spec['name']}.glb")
        export(build(spec), path)
        print(f"  [{i:2d}/50] {spec['sex']:4s} {spec['name']:22s} "
              f"{os.path.getsize(path)/1024:6.0f} KB")
    print(f"done in {time.time()-t0:.0f}s -> {OUT}")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
