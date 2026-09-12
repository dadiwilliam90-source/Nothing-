"""Inject KHR_lights_punctual fixtures into the exported GLB.

trimesh writes geometry and materials but has no concept of lights, so the
lighting rig is added afterwards with pygltflib. Emissive geometry alone makes
a fixture look lit; only real punctual lights actually cast light onto the
floor and walls in a viewer, which is what produces the specular streaks along
a polished floor.
"""
from pygltflib import GLTF2, Node


def _light(kind, colour, intensity, rng=None, inner=None, outer=None, name=None):
    d = {"type": kind, "color": list(colour), "intensity": float(intensity)}
    if name:
        d["name"] = name
    if rng:
        d["range"] = float(rng)
    if kind == "spot":
        d["spot"] = {"innerConeAngle": inner, "outerConeAngle": outer}
    return d


def inject(path, downlights, strips, warm=(1.0, 0.955, 0.895)):
    """Add point lights for the recessed downlights and the linear coves.

    `downlights` are (x, y, z) positions; `strips` are (x, y, z0, z1) runs that
    get a line of lights spaced along them.
    """
    g = GLTF2().load(path)
    lights = []
    nodes = []

    def emit(pos, spec):
        lights.append(spec)
        n = Node(translation=[float(v) for v in pos],
                 extensions={"KHR_lights_punctual": {"light": len(lights) - 1}})
        g.nodes.append(n)
        nodes.append(len(g.nodes) - 1)

    for (x, y, z) in downlights:
        emit((x, y, z), _light("point", warm, 7.0, rng=8.0, name="downlight"))

    for (x, y, z0, z1) in strips:
        span = z1 - z0
        n = max(2, int(span / 3.2))
        for i in range(n):
            z = z0 + span * (i + 0.5) / n
            emit((x, y, z), _light("point", warm, 5.5, rng=10.0, name="cove"))

    # Daylight through the glazed end, as a wide soft source just outside it.
    for spec, pos in (
            (_light("point", (0.93, 0.96, 1.0), 88.0, rng=44.0, name="daylight"), (0, 2.2, 36.5)),
            (_light("point", (0.93, 0.96, 1.0), 34.0, rng=28.0, name="daylight_low"), (0, 0.9, 35.6))):
        emit(pos, spec)

    ext = {"lights": lights}
    g.extensions = dict(g.extensions or {})
    g.extensions["KHR_lights_punctual"] = ext
    used = list(g.extensionsUsed or [])
    if "KHR_lights_punctual" not in used:
        used.append("KHR_lights_punctual")
    g.extensionsUsed = used

    # Every light node must hang off the scene or viewers will ignore it.
    scene = g.scenes[g.scene or 0]
    scene.nodes = list(scene.nodes) + nodes
    g.save(path)
    return len(lights)
