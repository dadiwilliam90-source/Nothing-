"""Curated accessory catalogue.

Props and duplicates from the source packs are excluded. Each entry carries the
per-item fit corrections found by rendering the item on the actual rig head.
"""

# key -> fit overrides (yaw / scale / dy / dz / grip)
HAIR = {
    "hair_1__Object_3": {},
    "hair_1__Object_4": {},
    "hair_1__Object_5": {},
    "hair_1__Object_6": {},
    "hair_1__Object_7": {},
    "hair_2__Object_2": {"grip": 1.58, "dy": -0.12},
    "hair_2__Object_4": {"grip": 1.46, "dy": -0.06},
    "hair_2__Object_6": {},
    "hair_2__Object_11": {},
    "hair_3__Object_1": {},
    "hair_3__Object_3": {},
    "hair_3__Object_4": {"grip": 1.56, "dy": -0.14},
}

# Sorted by how the fitted wig actually reads on the rig, not by pack order.
BOY_HAIR = ["hair_1__Object_4", "hair_1__Object_5", "hair_1__Object_6",
            "hair_1__Object_7", "hair_2__Object_4"]
GIRL_HAIR = ["hair_2__Object_2", "hair_2__Object_6", "hair_3__Object_1",
             "hair_2__Object_11",
             "hair_1__Object_3", "hair_3__Object_3", "hair_3__Object_4"]

HAIR_COLORS = {
    "black": "#15120F",
    "soft_black": "#221C18",
    "dark_brown": "#3B2418",
    "brown": "#5C3A22",
    "chestnut": "#7A4A28",
    "light_brown": "#9C6B3C",
    "auburn": "#6E2C18",
    "ginger": "#B5551F",
    "blonde": "#C9A44C",
    "light_blonde": "#DFC684",
    "platinum": "#DCD3BC",
    "grey": "#9A9A9A",
    "silver": "#B9BDC4",
}
