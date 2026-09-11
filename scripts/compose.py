"""Assemble meshes into a scene and export a clean GLB."""
import os
import trimesh
import rig as R
from geom import pbr

# Matches the supplied rig's own Rig1Mtl (white, non-metallic, roughness 0.6).
SKIN_WHITE = "#F3F3F4"


def base_rig_mesh():
    m = R.load_base()
    m.visual = trimesh.visual.TextureVisuals(
        material=pbr(SKIN_WHITE, dict(metallic=0.0, rough=0.60), name="Rig1Mtl"))
    return m


def export(meshes, out, name="avatar"):
    scene = trimesh.Scene()
    for i, m in enumerate(meshes):
        if m is None or len(m.vertices) == 0:
            continue
        try:
            label = m.visual.material.name or "part"
        except Exception:
            label = "part"
        scene.add_geometry(m, node_name=f"{i:03d}_{label}", geom_name=f"{i:03d}_{label}")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    scene.export(out)
    return out
