"""The 50 avatar styles — 25 boys, 25 girls.

Colours are flat (no textures) but chosen as real garment colours so the
result reads as cloth, leather and hi-vis rather than as painted blocks.
"""

# ------------------------------------------------------------------ palette
NAVY = "#2C3E5C"; NAVY_D = "#1E2A42"; NAVY_X = "#151E30"
CHARCOAL = "#33383F"; CHARCOAL_D = "#23272C"
BLACK = "#1A1C21"; INK = "#111318"
WHITE = "#F2F3F5"; OFFWHITE = "#E6E8EC"; CREAM = "#EADFC8"
GREY = "#8B9098"; GREY_L = "#B9BEC6"; GREY_D = "#4A4F57"
DENIM = "#3F5A7D"; DENIM_D = "#2E4359"; DENIM_L = "#6E8CAE"
RED = "#A6323C"; RED_D = "#7E2029"; MAROON = "#5E2330"
GREEN = "#3E6B4A"; OLIVE = "#5A5F3C"; MINT = "#7FB39B"
TEAL = "#2F7C85"; TEAL_L = "#5FA3A8"
ORANGE = "#C4622A"; HIVIS = "#D9731F"; AMBER = "#D8A32C"
YELLOW = "#D9B63C"; GOLD = "#C9A23F"
PURPLE = "#5C4A7D"; PLUM = "#6B3A5C"; LILAC = "#9B8CBF"
PINK = "#C4798F"; BLUSH = "#D9A9AE"
BROWN = "#6B4A32"; TAN = "#A88356"; KHAKI = "#B8A177"
SKYBLUE = "#6E93BE"; ICE = "#C7D5E2"
STEEL = "#4E5A6B"; SILVER = "#C0C5CC"


def S(name, sex, **kw):
    return dict(name=name, sex=sex, **kw)


BOYS = [
    S("police_officer", "boy", top="uniform", top_color=NAVY, sleeve="long",
      collar_color=NAVY_D, placket_color=NAVY_X, button_color=GOLD,
      bottom="trousers", bottom_color=NAVY_D, shoe="boot", shoe_color=INK,
      extras=[("belt", INK), ("epaulettes", NAVY_D), ("badge", GOLD), ("pockets", NAVY_D)],
      hair="hair_1__Object_4", hair_color="black", head="police"),

    S("doctor", "boy", top="coat", top_color=WHITE, inner_color=SKYBLUE,
      collar_color=SKYBLUE, bottom="trousers", bottom_color=STEEL,
      shoe="shoe", shoe_color=WHITE,
      extras=[("pockets", OFFWHITE), ("badge", SILVER)],
      hair="hair_1__Object_5", hair_color="soft_black", glasses=True),

    S("chef", "boy", top="uniform", top_color=WHITE, sleeve="long",
      collar_color=OFFWHITE, placket_color=OFFWHITE, button_color=GREY_L,
      bottom="trousers", bottom_color=CHARCOAL, shoe="shoe", shoe_color=BLACK,
      extras=[("apron", "#D3D7DD")], hair="hair_1__Object_6",
      hair_color="brown", head="chef"),

    S("construction_worker", "boy", top="vest_over", top_color=HIVIS, inner_color=GREY_D,
      sleeve="long", bottom="jeans", bottom_color=DENIM_D, bottom_finish="denim",
      shoe="boot", shoe_color=BROWN,
      extras=[("hivis", "#E4D35A"), ("belt", BROWN)],
      hair="hair_1__Object_7", hair_color="dark_brown", head="hardhat"),

    S("school_boy", "boy", top="blazer", top_color=NAVY_D, inner_color=WHITE,
      collar_color=WHITE, bottom="trousers", bottom_color=GREY_D,
      shoe="shoe", shoe_color=BLACK, extras=[("tie", MAROON)],
      hair="hair_2__Object_4", hair_color="dark_brown"),

    S("businessman", "boy", top="blazer", top_color=CHARCOAL_D, inner_color=WHITE,
      collar_color=WHITE, bottom="trousers", bottom_color=CHARCOAL_D,
      shoe="shoe", shoe_color=BLACK, extras=[("tie", NAVY), ("belt", BLACK)],
      hair="hair_2__Object_5", hair_color="black"),

    S("casual_hoodie", "boy", top="hoodie", top_color=GREY, hood_color=GREY_D,
      pocket_color=GREY_D, zip=True, bottom="jeans", bottom_color=DENIM,
      bottom_finish="denim", shoe="sneaker", shoe_color=WHITE,
      hair="hair_2__Object_9", hair_color="ginger"),

    S("basketball_player", "boy", top="tank", top_color=ORANGE,
      bottom="shorts", bottom_color=ORANGE, shoe="sneaker", shoe_color=WHITE,
      extras=[("socks", WHITE)], hair="hair_2__Object_10", hair_color="black",
      head=("headband", dict(color=ORANGE))),

    S("delivery_driver", "boy", top="polo", top_color=BROWN, sleeve="short",
      collar_color=TAN, bottom="trousers", bottom_color=BROWN,
      shoe="boot", shoe_color=INK, extras=[("belt", INK), ("pockets", TAN)],
      hair="hair_1__Object_4", hair_color="brown", head=("baseball", dict(color=BROWN))),

    S("pilot", "boy", top="uniform", top_color=WHITE, sleeve="long",
      collar_color=OFFWHITE, placket_color=OFFWHITE, button_color=GOLD,
      bottom="trousers", bottom_color=NAVY_X, shoe="shoe", shoe_color=BLACK,
      extras=[("tie", NAVY_X), ("epaulettes", NAVY_X), ("belt", BLACK)],
      hair="hair_1__Object_5", hair_color="grey", head="police",
      glasses=dict(frame="#23262B", lens="#3E4C5E")),

    S("firefighter", "boy", top="jacket", top_color=CHARCOAL_D, inner_color=AMBER,
      collar_color=AMBER, open=False, bottom="trousers", bottom_color=CHARCOAL_D,
      shoe="boot", shoe_color=INK,
      extras=[("hivis", "#D9C24A"), ("belt", INK), ("badge", AMBER)],
      hair="hair_1__Object_6", hair_color="dark_brown", head=("hardhat", dict(color=RED_D))),

    S("mechanic", "boy", top="uniform", top_color=STEEL, sleeve="long",
      collar_color=GREY_D, placket_color=GREY_D, button_color=SILVER,
      bottom="trousers", bottom_color=STEEL, shoe="boot", shoe_color=BLACK,
      extras=[("belt", BLACK), ("pockets", GREY_D), ("badge", SILVER)],
      hair="hair_1__Object_7", hair_color="auburn", head=("baseball", dict(color=STEEL))),

    S("graduate", "boy", top="coat", top_color=INK, inner_color=WHITE,
      collar_color=WHITE, open=False, bottom="trousers", bottom_color=CHARCOAL_D,
      shoe="shoe", shoe_color=BLACK, extras=[("tie", MAROON)],
      hair="hair_2__Object_4", hair_color="black", head="grad"),

    S("waiter", "boy", top="vest_over", top_color=INK, inner_color=WHITE,
      sleeve="long", bottom="trousers", bottom_color=INK,
      shoe="shoe", shoe_color=BLACK, extras=[("bow", INK)],
      hair="hair_2__Object_5", hair_color="soft_black"),

    S("farmer", "boy", top="shirt", top_color=RED_D, sleeve="long",
      collar_color=RED_D, placket_color=MAROON, button_color=CREAM,
      bottom="jeans", bottom_color=DENIM_D, bottom_finish="denim",
      shoe="boot", shoe_color=BROWN, extras=[("belt", BROWN)],
      hair="hair_2__Object_9", hair_color="light_brown", head=("baseball", dict(color=DENIM_D))),

    S("soldier", "boy", top="uniform", top_color=OLIVE, sleeve="long",
      collar_color=OLIVE, placket_color="#4A4F31", button_color=OLIVE,
      bottom="trousers", bottom_color=OLIVE, shoe="boot", shoe_color="#3A3524",
      extras=[("belt", "#3A3524"), ("epaulettes", "#4A4F31"), ("pockets", "#4A4F31")],
      hair="hair_2__Object_10", hair_color="brown", head=("visor", dict(color=OLIVE))),

    S("skater", "boy", top="tee", top_color=PURPLE, sleeve="short",
      bottom="shorts", bottom_color=CHARCOAL, shoe="sneaker", shoe_color=BLACK,
      extras=[("socks", WHITE)], hair="hair_1__Object_4", hair_color="black",
      head=("beanie", dict(color=CHARCOAL_D, cuff=PURPLE))),

    S("teacher", "boy", top="sweater", top_color=GREEN, sleeve="long",
      bottom="trousers", bottom_color=KHAKI, shoe="shoe", shoe_color=BROWN,
      extras=[("belt", BROWN)], hair="hair_1__Object_5", hair_color="grey",
      glasses=True),

    S("security_guard", "boy", top="uniform", top_color=INK, sleeve="long",
      collar_color=BLACK, placket_color=BLACK, button_color=SILVER,
      bottom="trousers", bottom_color=INK, shoe="boot", shoe_color=BLACK,
      extras=[("belt", BLACK), ("badge", SILVER), ("epaulettes", BLACK)],
      hair="hair_1__Object_6", hair_color="black", head=("visor", dict(color=INK))),

    S("scientist", "boy", top="coat", top_color=WHITE, inner_color=TEAL_L,
      collar_color=TEAL_L, bottom="trousers", bottom_color=GREY_D,
      shoe="shoe", shoe_color=GREY_L, extras=[("pockets", OFFWHITE), ("badge", TEAL)],
      hair="hair_1__Object_7", hair_color="silver", glasses=True),

    S("runner", "boy", top="tank", top_color=TEAL, bottom="shorts",
      bottom_color=CHARCOAL_D, shoe="sneaker", shoe_color=TEAL_L,
      hair="hair_2__Object_4", hair_color="dark_brown",
      head=("headband", dict(color=TEAL_L))),

    S("winter_coat", "boy", top="coat", top_color=GREEN, inner_color=CREAM,
      collar_color=CREAM, open=False, bottom="jeans", bottom_color=DENIM_D,
      bottom_finish="denim", shoe="boot", shoe_color=BROWN,
      extras=[("scarf", RED_D), ("belt", BROWN)],
      hair="hair_2__Object_5", hair_color="chestnut",
      head=("beanie", dict(color=RED_D, cuff=CREAM))),

    S("cricketer", "boy", top="polo", top_color=WHITE, sleeve="long",
      collar_color=OFFWHITE, bottom="trousers", bottom_color=WHITE,
      shoe="sneaker", shoe_color=WHITE, extras=[("belt", OFFWHITE)],
      hair="hair_2__Object_9", hair_color="dark_brown",
      head=("visor", dict(color=NAVY_D))),

    S("kurta_traditional", "boy", top="kurta", top_color=CREAM, sleeve="long",
      bottom="trousers", bottom_color=CREAM, shoe="shoe", shoe_color=BROWN,
      hair="hair_2__Object_10", hair_color="black",
      head=("turban", dict(color=OFFWHITE, knot=GOLD))),

    S("postman", "boy", top="polo", top_color=DENIM_L, sleeve="short",
      collar_color=NAVY_D, bottom="shorts", bottom_color=NAVY_D,
      shoe="shoe", shoe_color=BLACK,
      extras=[("belt", BLACK), ("socks", OFFWHITE), ("pockets", NAVY_D)],
      hair="hair_1__Object_4", hair_color="light_brown", head=("baseball", dict(color=NAVY_D))),
]

GIRLS = [
    S("police_woman", "girl", top="uniform", top_color=NAVY, sleeve="long",
      collar_color=NAVY_D, placket_color=NAVY_X, button_color=GOLD,
      bottom="trousers", bottom_color=NAVY_D, shoe="boot", shoe_color=INK,
      extras=[("belt", INK), ("epaulettes", NAVY_D), ("badge", GOLD)],
      hair="hair_2__Object_2", hair_color="black", head="police"),

    S("doctor_woman", "girl", top="coat", top_color=WHITE, inner_color=TEAL_L,
      collar_color=TEAL_L, bottom="trousers", bottom_color=STEEL,
      shoe="shoe", shoe_color=WHITE, extras=[("pockets", OFFWHITE), ("badge", SILVER)],
      hair="hair_2__Object_6", hair_color="blonde", glasses=True),

    S("nurse", "girl", top="uniform", top_color=WHITE, sleeve="short",
      collar_color=TEAL_L, placket_color=TEAL_L, button_color=TEAL,
      bottom="trousers", bottom_color=TEAL_L, shoe="shoe", shoe_color=WHITE,
      extras=[("pockets", TEAL_L), ("badge", TEAL)],
      hair="hair_3__Object_1", hair_color="chestnut"),

    S("chef_woman", "girl", top="uniform", top_color=WHITE, sleeve="long",
      collar_color=OFFWHITE, placket_color=OFFWHITE, button_color=GREY_L,
      bottom="trousers", bottom_color=CHARCOAL, shoe="shoe", shoe_color=BLACK,
      extras=[("apron", "#D3D7DD")], hair="hair_2__Object_11",
      hair_color="auburn", head="chef"),

    S("school_girl", "girl", top="blazer", top_color=NAVY_D, inner_color=WHITE,
      collar_color=WHITE, bottom="skirt_short", bottom_color=MAROON, flare=1.5,
      shoe="shoe", shoe_color=BLACK, extras=[("tie", MAROON), ("socks", WHITE)],
      hair="hair_2__Object_1", hair_color="dark_brown"),

    S("businesswoman", "girl", top="blazer", top_color=CHARCOAL_D, inner_color=WHITE,
      collar_color=WHITE, bottom="skirt_short", bottom_color=CHARCOAL_D,
      shoe="heel", shoe_color=BLACK, extras=[("belt", BLACK)],
      hair="hair_1__Object_1", hair_color="soft_black"),

    S("casual_hoodie_girl", "girl", top="hoodie", top_color=BLUSH,
      hood_color=PINK, pocket_color=PINK, bottom="jeans", bottom_color=DENIM_L,
      bottom_finish="denim", shoe="sneaker", shoe_color=WHITE,
      hair="hair_1__Object_3", hair_color="ginger"),

    S("summer_dress", "girl", top="dress", top_color=MINT, sleeve="cap",
      dress_length="midi", flare=1.7, shoe="shoe", shoe_color=CREAM,
      extras=[("belt", CREAM)], hair="hair_3__Object_3", hair_color="light_blonde"),

    S("graduate_girl", "girl", top="coat", top_color=INK, inner_color=WHITE,
      collar_color=WHITE, open=False, bottom="skirt_short", bottom_color=CHARCOAL_D,
      shoe="shoe", shoe_color=BLACK, hair="hair_3__Object_4",
      hair_color="dark_brown", head="grad"),

    S("waitress", "girl", top="vest_over", top_color=INK, inner_color=WHITE,
      sleeve="long", bottom="skirt_short", bottom_color=INK,
      shoe="shoe", shoe_color=BLACK, extras=[("bow", RED_D), ("apron", "#D8DCE2")],
      hair="hair_2__Object_2", hair_color="black"),

    S("teacher_woman", "girl", top="sweater", top_color=PLUM, sleeve="long",
      bottom="skirt_midi", bottom_color=CHARCOAL, flare=1.45,
      shoe="shoe", shoe_color=BROWN, hair="hair_2__Object_6",
      hair_color="grey", glasses=True),

    S("scientist_woman", "girl", top="coat", top_color=WHITE, inner_color=LILAC,
      collar_color=LILAC, bottom="trousers", bottom_color=GREY_D,
      shoe="shoe", shoe_color=GREY_L, extras=[("pockets", OFFWHITE), ("badge", PURPLE)],
      hair="hair_3__Object_1", hair_color="platinum", glasses=True),

    S("athlete_girl", "girl", top="tank", top_color=RED, bottom="shorts",
      bottom_color=CHARCOAL_D, shoe="sneaker", shoe_color=WHITE,
      hair="hair_2__Object_11", hair_color="brown",
      head=("headband", dict(color=RED))),

    S("winter_coat_girl", "girl", top="coat", top_color=RED_D, inner_color=CREAM,
      collar_color=CREAM, open=False, bottom="skirt_midi", bottom_color=CHARCOAL_D,
      shoe="boot", shoe_color=BROWN, extras=[("scarf", CREAM), ("socks", GREY_D)],
      hair="hair_2__Object_1", hair_color="chestnut",
      head=("beanie", dict(color=CREAM, cuff=RED_D))),

    S("air_hostess", "girl", top="blazer", top_color=NAVY_X, inner_color=WHITE,
      collar_color=WHITE, bottom="skirt_short", bottom_color=NAVY_X,
      shoe="heel", shoe_color=NAVY_X, extras=[("scarf", RED), ("badge", GOLD)],
      hair="hair_1__Object_1", hair_color="soft_black"),

    S("traditional_girl", "girl", top="kurta", top_color=TEAL, sleeve="long",
      bottom="trousers", bottom_color=CREAM, shoe="shoe", shoe_color=TAN,
      hair="hair_1__Object_3", hair_color="black",
      head=("headscarf", dict(color=TEAL, trim=GOLD))),

    S("dancer", "girl", top="dress", top_color=BLUSH, sleeve="cap",
      dress_length="short", flare=1.72, shoe="shoe", shoe_color=BLUSH,
      hair="hair_3__Object_3", hair_color="light_brown"),

    S("artist", "girl", top="tee", top_color=WHITE, sleeve="short",
      bottom="jeans", bottom_color=DENIM, bottom_finish="denim",
      shoe="sneaker", shoe_color=CREAM, extras=[("apron", BROWN)],
      hair="hair_3__Object_4", hair_color="auburn"),

    S("security_woman", "girl", top="uniform", top_color=INK, sleeve="long",
      collar_color=BLACK, placket_color=BLACK, button_color=SILVER,
      bottom="trousers", bottom_color=INK, shoe="boot", shoe_color=BLACK,
      extras=[("belt", BLACK), ("badge", SILVER), ("epaulettes", BLACK)],
      hair="hair_2__Object_2", hair_color="black", head=("visor", dict(color=INK))),

    S("gym_girl", "girl", top="tank", top_color=PURPLE, bottom="capri",
      bottom_color=CHARCOAL_D, shoe="sneaker", shoe_color=LILAC,
      hair="hair_2__Object_6", hair_color="blonde",
      head=("headband", dict(color=LILAC))),

    S("party_dress", "girl", top="dress", top_color=PLUM, sleeve="cap",
      dress_length="short", flare=1.75, shoe="heel", shoe_color=INK,
      extras=[("belt", GOLD)], hair="hair_3__Object_1", hair_color="black"),

    S("gardener", "girl", top="shirt", top_color=GREEN, sleeve="three_quarter",
      collar_color=GREEN, placket_color="#33583D", button_color=CREAM,
      bottom="jeans", bottom_color=DENIM_D, bottom_finish="denim",
      shoe="boot", shoe_color=BROWN, extras=[("apron", KHAKI)],
      hair="hair_2__Object_11", hair_color="ginger",
      head=("beanie", dict(color=KHAKI, cuff=GREEN))),

    S("librarian", "girl", top="sweater", top_color=KHAKI, sleeve="long",
      bottom="skirt_long", bottom_color=BROWN, flare=1.4,
      shoe="shoe", shoe_color=BROWN, hair="hair_2__Object_1",
      hair_color="brown", glasses=True),

    S("cyclist", "girl", top="tee", top_color=AMBER, sleeve="short",
      bottom="capri", bottom_color=INK, shoe="sneaker", shoe_color=INK,
      hair="hair_1__Object_1", hair_color="ginger",
      head=("hardhat", dict(color=AMBER, brim=INK))),

    S("receptionist", "girl", top="shirt", top_color=ICE, sleeve="long",
      collar_color=WHITE, placket_color=WHITE, button_color=SILVER,
      bottom="skirt_short", bottom_color=NAVY_X, shoe="heel", shoe_color=NAVY_X,
      extras=[("belt", NAVY_X)], hair="hair_1__Object_3", hair_color="dark_brown"),
]

ALL = BOYS + GIRLS
assert len(BOYS) == 25 and len(GIRLS) == 25, (len(BOYS), len(GIRLS))
