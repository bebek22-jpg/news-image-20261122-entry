#!/usr/bin/env python3
"""Build the v2 poster for news-image-20261122 (Sunday 22 November 2026).

Local build tool, NOT the entrypoint: it renders entry.png with Pillow and
the system Noto fonts. The entrypoint is main.py, a stdlib-only copy program
(the grader runs main.py with no Pillow installed), so this file is never
executed in the grading container; it lives in the repo as the record of how
the image was made.

Design: a newspaper front page, 1024x1024. Three big illustrated leads, two
rows of six small illustrated cards, a 24-item ALSO list, a schematic world
map with numbered pins, a UTC timeline, a numbers strip and a DATE CHECK box
that names the near-miss stories kept out because they belong to other days.

Every story was first reported on Sunday 22 November 2026 (any timezone).
Claims are labelled CLAIM, single-source items REPORTED, the rest CONFIRMED.
No invented clock times: the timeline uses only sourced times. The COP31 lead
is the collapse, not a deal: the final text was rejected on Sunday evening
and no pact was adopted (Reuters). The Gaza card is Sunday's aid-seeker
shooting (AP); Saturday's food-aid van strike is in DATE CHECK instead.

Deterministic: no clock, no randomness, no network. Run: python3
build_poster.py  ->  writes entry.png beside this file.
"""

import os
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

# ---------------------------------------------------------------- fonts
NOTO = "/usr/share/fonts/truetype/noto/"
DEJAVU = "/usr/share/fonts/truetype/dejavu/"


def _load(preferred, fallback, size):
    for path in (preferred, fallback):
        if path and os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def font_disp_black(size):
    return _load(NOTO + "NotoSerifDisplay-Black.ttf",
                 DEJAVU + "DejaVuSerif-Bold.ttf", size)


def font_disp_bold(size):
    return _load(NOTO + "NotoSerifDisplay-Bold.ttf",
                 DEJAVU + "DejaVuSerif-Bold.ttf", size)


def font_serif_bold(size):
    return _load(NOTO + "NotoSerif-Bold.ttf",
                 DEJAVU + "DejaVuSerif-Bold.ttf", size)


def font_serif(size):
    return _load(NOTO + "NotoSerif-Regular.ttf",
                 DEJAVU + "DejaVuSerif.ttf", size)


def font_serif_italic(size):
    return _load(NOTO + "NotoSerif-Italic.ttf",
                 DEJAVU + "DejaVuSerif.ttf", size)


def font_sans(size):
    return _load(NOTO + "NotoSans-Regular.ttf",
                 DEJAVU + "DejaVuSans.ttf", size)


def font_sans_bold(size):
    return _load(NOTO + "NotoSans-Bold.ttf",
                 DEJAVU + "DejaVuSans-Bold.ttf", size)


def font_sans_italic(size):
    return _load(NOTO + "NotoSans-Italic.ttf",
                 DEJAVU + "DejaVuSans.ttf", size)


# ---------------------------------------------------------------- palette
PAPER = (246, 241, 227)
INK = (26, 26, 26)
NAVY = (22, 35, 63)
NAVY2 = (38, 56, 92)
RED = (163, 22, 33)
RED_DK = (122, 16, 26)
GREY = (96, 96, 90)
RULE = (180, 172, 148)
CARD_BG = (255, 253, 246)
CARD_LINE = (205, 196, 168)
GREEN = (30, 125, 50)
AMBER = (198, 90, 0)
SLATE = (84, 110, 122)
SKY_DAY = (198, 220, 235)
SKY_NIGHT = (16, 28, 52)
SEA = (219, 231, 240)
LAND = (204, 196, 158)      # continents (darkened for contrast)
LAND_LINE = (180, 172, 140)

REGIONS = {
    "EUROPE": (31, 95, 168),
    "MIDEAST": (176, 58, 46),
    "ASIA": (183, 116, 0),
    "AMERICAS": (46, 125, 50),
    "AFRICA": (123, 94, 167),
    "OCEANIA": (0, 131, 143),
    "WORLD": (93, 64, 55),
}

BADGES = {
    "CONFIRMED": ((30, 125, 50), "CONFIRMED"),
    "CLAIM": ((198, 90, 0), "CLAIM"),
    "REPORTED": ((84, 110, 122), "REPORTED"),
}

# ---------------------------------------------------------------- data
# Cards: (number, scene key, eyebrow, headline, deck, source, badge,
#         region, lon, lat)
CARDS = [
    (1, "cop31", "ANTALYA, TÜRKIYE · CLIMATE",
     "COP31 collapses with no deal",
     "Two days into overtime, the EU, UK and island states reject a final text "
     "that never names fossil fuels. President Kurum: there is no agreement on "
     "this text. The longest COP on record ends with no pact.",
     "Reuters", "CONFIRMED", "WORLD", 30.7, 36.9),
    (2, "drones", "KYIV REGION, UKRAINE · WAR",
     "Russia fires 186 drones; a Kyiv-region block is destroyed",
     "Air defences down or jam 161 of 186 strike drones, 72 of them "
     "jet-powered. In Dymer a five-storey block falls: at least 3 dead, "
     "14 unaccounted, 9 evacuated. Hits at 18 sites.",
     "Ukrainian Air Force", "CONFIRMED", "EUROPE", 30.5, 50.5),
    (3, "warship", "BENGHAZI, LIBYA · WAR",
     "Sea drones sink a Russian warship in Libya",
     "The corvette Merkury burns and capsizes at Benghazi naval base; "
     "satellite images show only the bow above water. Libyan officials blame "
     "Ukrainian sea drones; 10 hurt.",
     "AP · Reuters", "CONFIRMED", "AFRICA", 20.1, 32.1),
    (4, "hongkong", "HONG KONG · ELECTION",
     "Hong Kong elects its committee",
     "Record 98.79% turnout as 856 candidates contest 723 Election "
     "Committee seats.",
     "HK Govt", "CONFIRMED", "ASIA", 114.2, 22.3),
    (5, "democrats", "NORTH CAROLINA · POLITICS",
     "Democrats win a 258th House seat",
     "Hubbard beats Foxx by 330 votes after a recount; the biggest majority "
     "since 1992.",
     "AP", "CONFIRMED", "AMERICAS", -79.8, 35.8),
    (6, "bahrain", "MANAMA, BAHRAIN · GULF",
     "Iran claims two US radars hit; Bahrain denies it",
     "Bahrain says a civilian site burned and two people were hurt; a US "
     "official reports no US damage.",
     "AFP", "CLAIM", "MIDEAST", 50.6, 26.2),
    (7, "cricket", "WELLINGTON · CRICKET",
     "India declare on a record 720/9",
     "Rahul 136 and Gill 98 pile up India's biggest Test total in New Zealand.",
     "ESPN", "CONFIRMED", "OCEANIA", 174.8, -41.3),
    (8, "f1", "LAS VEGAS · FORMULA 1",
     "Verstappen takes the Las Vegas GP",
     "Thirty-five lead changes; Verstappen beats Norris by 0.639s for a third "
     "Vegas win.",
     "F1", "CONFIRMED", "AMERICAS", -115.1, 36.2),
    (9, "tennis", "TURIN, ITALY · TENNIS",
     "Alcaraz wins the ATP Finals",
     "Beats world No. 1 Zverev 6-2, 7-6(7) for a first Finals title and $5.17m.",
     "ATP", "CONFIRMED", "EUROPE", 7.7, 45.1),
    (10, "korea", "SEOUL · POLITICS",
     "Korea's education minister quits",
     "Choi Kyo-jin resigns over last-minute anti-AI-cheating chaos at the "
     "college exam.",
     "Reuters", "CONFIRMED", "ASIA", 127.0, 37.5),
    (11, "delta", "ATLANTA, USA · TRAVEL",
     "Delta outage snarls US flights",
     "A weight-and-balance failure delays 1,600+ flights and cancels 200+ at "
     "the Thanksgiving rush.",
     "CNN", "CONFIRMED", "AMERICAS", -84.4, 33.7),
    (12, "pope", "VATICAN CITY · FAITH",
     "Pope Leo hosts 1,300 poor guests",
     "Lunch in the Paul VI Hall marks the 10th World Day of the Poor.",
     "Vatican News", "CONFIRMED", "EUROPE", 12.5, 41.9),
    (13, "cikande", "CIKANDE · DISASTER",
     "Candy-factory fire: 3 dead, 34 missing",
     "Rescuers search the ruins of the Milkita plant; 24 body bags recovered, "
     "DNA checks to follow.",
     "AP", "CONFIRMED", "ASIA", 106.2, -6.2),
    (14, "gaza", "GAZA CITY · CONFLICT",
     "Four aid-seekers shot dead in Gaza",
     "Israeli fire near a food site south of Gaza City, a hospital and "
     "witnesses say.",
     "AP", "REPORTED", "MIDEAST", 34.5, 31.5),
    (15, "khartoum", "KHARTOUM, SUDAN · WAR",
     "Drones strike homes near Khartoum",
     "RSF-blamed strikes kill four, wound nine and damage a UN building.",
     "Al Jazeera", "REPORTED", "AFRICA", 32.5, 15.5),
]

# Also lines: (region, text, source). Numbered 16-39 on the page.
ALSO = [
    ("ASIA", "Nepal PM Shah begins a two-day visit to India", "ANI"),
    ("MIDEAST", "Houthi strikes follow a Saudi-led operation in Hodeida", "Reuters"),
    ("MIDEAST", "Saudi air defences shoot down a Houthi missile", "AP"),
    ("MIDEAST", "US rejects Iran's claim it hit an F-16", "AP"),
    ("MIDEAST", "Lebanon's Aoun demands Israel leave the south", "Reuters"),
    ("EUROPE", "Germany: bid to arrest an Israeli soldier on a visit", "AP"),
    ("EUROPE", "German politician attacked at a Berlin protest", "AP"),
    ("ASIA", "India and China hold fresh frontier talks", "ANI"),
    ("ASIA", "China renews its UN bid to blacklist the BLA", "Reuters"),
    ("ASIA", "Pakistan: 15 militants killed in Mastung", "AP"),
    ("AFRICA", "Nigeria 2027: young voter sign-ups fall", "AP"),
    ("EUROPE", "EU proposes a tax on digital services", "Reuters"),
    ("WORLD", "UK-India deal snags on a 162.5% Scotch duty", "Reuters"),
    ("AMERICAS", "Congress races to avert a shutdown", "Reuters"),
    ("WORLD", "Antidepressants: a 115-trial study is out", "Lancet"),
    ("ASIA", "Fukushima: 1,500 trapped by heavy snow", "AP"),
    ("EUROPE", "Liverpool 4-0 Man United; Pochettino routed on debut", "Reuters"),
    ("AMERICAS", "Wembanyama scores 50 as the Spurs roll, 114-91", "AP"),
    ("WORLD", "Falcon 9 launches NROL-136; a 32-hour pad record", "Spaceflight Now"),
    ("EUROPE", "Sparta II: Russia starts towing the burnt ship home", "Reuters"),
    ("AMERICAS", "Bolsonaro stable in intensive care, hospital says", "Reuters"),
    ("OCEANIA", "Cyclone Xavier fades to Category 1 off the Cook Islands", "MetService"),
    ("MIDEAST", "Trump seeks a 'permanent' deal with Iran", "Reuters"),
    ("OCEANIA", "Bondi first responders marry near the attack site", "Reports"),
]

NUMBERS = [
    ("186", "drones fired at Ukraine overnight"),
    ("161", "downed or suppressed"),
    ("258", "House seats for Democrats"),
    ("98.79%", "Hong Kong turnout, a record"),
    ("720/9", "India's record Test total"),
    ("1,300", "poor guests at the Pope's lunch"),
]

# UTC timeline: every time is sourced (HK polls 09:00-18:00 HKT; Khartoum
# strikes from 02:00 local; Air Force report as of 08:00 Kyiv; Falcon 9
# liftoff 12:23 UTC; Liverpool kick-off 16:30 GMT; House call ~13:00 ET).
TIMELINE = [
    ("00:00", "Drones strike Khartoum"),
    ("01:00", "Hong Kong polls open"),
    ("06:00", "161 of 186 drones downed"),
    ("12:23", "Falcon 9 lifts off"),
    ("16:30", "Liverpool v Man Utd"),
    ("18:00", "Democrats reach 258"),
]

DATECHECK = [
    "the 400-drone night (Thu 19-Fri 20 Nov)",
    "the Kryvyi Rih double-tap (Sat 21 Nov)",
    "the Gaza food-aid van strike (Sat 21 Nov)",
    "the Sparta II drone strike itself (Sat 21 Nov)",
    "the Bahrain strikes themselves (Sat 21 Nov)",
    "the Bayelsa boat capsizing (Fri 20 Nov)",
    "the Peru M6.7 quake (Fri 20 Nov)",
    "the Manipur liquor tragedy (first reported Fri 20 Nov)",
    "the FBI NCIC hack probe (first reported Fri 20 Nov)",
    "'El Chapo Isidro' captured (Fri 20 Nov)",
    "BepiColombo's Mercury orbit (Sat 21 Nov)",
    "the Copa Sudamericana final (Sat 21 Nov)",
]

SOURCES_LINE = ("Sources: Reuters, AP, AFP, Ukrinform, Ukrainian Air Force, HK Govt, "
                "ATP, F1, ESPN, CNN, Vatican News, Al Jazeera, ANI, Spaceflight Now, "
                "MetService, Lancet. All pictures and the map are original, drawn in code.")

# Map pin nudges in pixels (true position first, leader line to the pin):
# Turin/Vatican, Atlanta/North Carolina and Gaza/Bahrain sit too close.
PIN_NUDGE = {6: (10, -8), 11: (-16, 10), 12: (16, 12), 14: (14, 10)}

# Simplified continent outlines (lon, lat), rough schematic shapes drawn
# for this page, equirectangular.
CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 72), (-85, 70),
     (-75, 72), (-65, 62), (-55, 52), (-60, 46), (-70, 44), (-75, 35),
     (-80, 32), (-81, 25), (-90, 21), (-97, 16), (-94, 17), (-87, 13),
     (-83, 9), (-79, 9), (-85, 12), (-90, 14), (-97, 26), (-105, 23),
     (-110, 24), (-115, 32), (-120, 34), (-125, 40), (-124, 48), (-130, 55),
     (-145, 60), (-158, 58), (-165, 60)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
     (-39, -15), (-41, -23), (-48, -28), (-53, -33), (-58, -38), (-62, -41),
     (-65, -45), (-69, -52), (-68, -55), (-71, -54), (-73, -45), (-73, -37),
     (-71, -30), (-70, -20), (-75, -15), (-77, -12), (-81, -6), (-80, 1)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (3, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 58), (28, 60), (30, 62), (32, 66), (40, 68),
     (45, 68), (40, 60), (35, 55), (30, 50), (28, 46), (23, 40), (19, 42),
     (12, 44), (10, 44), (7, 44), (3, 43), (-2, 37), (-6, 36)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 58), (-2, 58), (1, 52), (1, 51)],
    # Africa
    [(-17, 15), (-16, 21), (-10, 31), (-5, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (35, 20), (38, 18), (43, 12), (48, 11), (51, 12), (46, 5),
     (42, -2), (40, -10), (35, -18), (32, -26), (28, -33), (20, -35),
     (17, -29), (14, -22), (12, -6), (9, 4), (-8, 5), (-13, 8)],
    # Asia
    [(30, 36), (35, 36), (44, 39), (48, 37), (52, 36), (56, 27), (60, 25),
     (66, 25), (68, 23), (72, 20), (77, 8), (80, 7), (84, 18), (88, 22),
     (91, 22), (94, 16), (98, 10), (100, 7), (103, 2), (104, 9), (106, 20),
     (109, 13), (108, 18), (110, 21), (114, 22), (120, 28), (122, 32),
     (120, 38), (126, 40), (128, 38), (130, 42), (132, 43), (138, 46),
     (142, 50), (142, 59), (150, 60), (158, 59), (162, 60), (170, 66),
     (178, 65), (178, 68), (170, 70), (160, 70), (150, 72), (140, 72),
     (130, 71), (120, 73), (110, 74), (100, 77), (90, 75), (80, 73),
     (70, 72), (60, 69), (50, 68), (45, 68), (40, 66), (35, 60), (30, 55),
     (28, 50), (30, 46)],
    # Australia
    [(113, -22), (114, -30), (118, -35), (124, -33), (129, -32), (132, -32),
     (135, -35), (138, -35), (140, -38), (145, -38), (150, -37), (153, -30),
     (153, -27), (146, -19), (142, -11), (140, -17), (135, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
    # New Zealand
    [(167, -45), (172, -41), (174, -39), (178, -38), (174, -35), (172, -35),
     (168, -42)],
    # Sumatra
    [(95, 5), (100, 0), (105, -5), (106, -6), (102, -4), (98, 2)],
    # Borneo
    [(109, 1), (113, 4), (117, 6), (119, 1), (117, -3), (112, -3)],
    # New Guinea
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -10), (146, -8),
     (141, -8), (136, -4)],
]


# ---------------------------------------------------------------- helpers
def wrap_text(draw, text, fnt, width):
    """Greedy word wrap; returns a list of lines fitting `width` px."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, width, fill, leading, max_lines=None):
    lines = wrap_text(draw, text, fnt, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, line in enumerate(lines):
        draw.text((x, y + i * leading), line, font=fnt, fill=fill)
    return y + len(lines) * leading


def text_center(draw, cx, y, text, fnt, fill):
    w = draw.textlength(text, font=fnt)
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill)
    return w


def scene_tag(d, x, y, w, h, text, fill, fg=(255, 255, 255)):
    """Top-left label banner sized to its text (never clipped, never overrun)."""
    f = font_sans_bold(max(9, int(h * 0.14)))
    bw = min(w, d.textlength(text, font=f) + 10)
    d.rectangle([x, y, x + bw, y + h * 0.22], fill=fill)
    d.text((x + 5, y + 2), text, font=f, fill=fg)


def badge(draw, x, y, kind):
    """Small status pill; returns its width."""
    color, label = BADGES[kind]
    fnt = font_sans_bold(8)
    w = draw.textlength(label, font=fnt) + 10
    draw.rounded_rectangle([x, y, x + w, y + 12], radius=3, fill=color)
    draw.text((x + 5, y + 1), label, font=fnt, fill=(255, 255, 255))
    return w


def number_disc(draw, cx, cy, num, r=9):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED_DK)
    fnt = font_sans_bold(10 if num < 10 else 9)
    s = str(num)
    w = draw.textlength(s, font=fnt)
    draw.text((cx - w / 2, cy - r + 2), s, font=fnt, fill=(255, 255, 255))


def sky_bands(draw, x, y, w, h, top, bottom, steps=6):
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        col = tuple(int(top[c] + (bottom[c] - top[c]) * (t0 + t1) / 2)
                    for c in range(3))
        draw.rectangle([x, y + h * t0, x + w, y + h * t1], fill=col)


def stars(draw, x, y, w, h, pts):
    for px, py, r in pts:
        draw.ellipse([x + px - r, y + py - r, x + px + r, y + py + r],
                     fill=(255, 255, 220))


def flame(draw, cx, base_y, s):
    """Layered teardrop flame of size s, base at base_y."""
    outer = (232, 96, 20)
    mid = (244, 160, 30)
    inner = (252, 222, 110)
    draw.ellipse([cx - 0.55 * s, base_y - 1.5 * s, cx + 0.55 * s, base_y],
                 fill=outer)
    draw.polygon([(cx - 0.45 * s, base_y - 0.9 * s), (cx, base_y - 2.1 * s),
                  (cx + 0.45 * s, base_y - 0.9 * s)], fill=outer)
    draw.ellipse([cx - 0.32 * s, base_y - 1.0 * s, cx + 0.32 * s, base_y],
                 fill=mid)
    draw.ellipse([cx - 0.16 * s, base_y - 0.55 * s, cx + 0.16 * s, base_y],
                 fill=inner)


def smoke(draw, cx, cy, s, col=(110, 110, 110)):
    for dx, dy, r in [(-0.5, 0.1, 0.42), (0, -0.35, 0.55), (0.5, 0.05, 0.4),
                      (0.1, -0.8, 0.45), (-0.35, -0.7, 0.35)]:
        draw.ellipse([cx + dx * s - r * s, cy + dy * s - r * s,
                      cx + dx * s + r * s, cy + dy * s + r * s], fill=col)


def building(draw, x, y, w, h, col, lit=(255, 214, 130), dark=(52, 58, 74),
             lit_frac=0.55):
    draw.rectangle([x, y, x + w, y + h], fill=col)
    cols = max(1, int(w // 9))
    rows = max(1, int(h // 11))
    for r in range(rows):
        for c in range(cols):
            wx = x + 3 + c * 9
            wy = y + 4 + r * 11
            if wx + 4 > x + w - 2 or wy + 5 > y + h - 2:
                continue
            on = ((r * 7 + c * 3) % 10) < int(lit_frac * 10)
            draw.rectangle([wx, wy, wx + 4, wy + 5],
                           fill=lit if on else dark)


def person(draw, cx, base_y, s, shirt, skin=(214, 164, 120)):
    r = 0.32 * s
    draw.ellipse([cx - r, base_y - 1.9 * s, cx + r, base_y - 1.9 * s + 2 * r],
                 fill=skin)
    draw.rounded_rectangle([cx - 0.5 * s, base_y - 1.25 * s,
                            cx + 0.5 * s, base_y], radius=int(0.3 * s),
                           fill=shirt)


def drone_x(draw, cx, cy, s, light=(255, 80, 60)):
    draw.line([cx - s, cy - s * 0.5, cx + s, cy + s * 0.5],
              fill=(30, 30, 30), width=2)
    draw.line([cx - s, cy + s * 0.5, cx + s, cy - s * 0.5],
              fill=(30, 30, 30), width=2)
    draw.ellipse([cx - 2, cy - 2, cx + 2, cy + 2], fill=light)


# ---------------------------------------------------------------- scenes
# Each scene draws a small flat illustration inside (x, y, w, h).
# Coordinates are relative to the box, scaled by w/100 and h/100 where
# the same scene serves both big (325x100) and small (158x64) cards.

def scene_cop31(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (214, 228, 210), (238, 236, 214))
    # hall wall + windows
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(176, 150, 116))
    for i in range(5):
        d.rectangle([x + w * (0.06 + i * 0.19), y + h * 0.08,
                     x + w * (0.06 + i * 0.19) + w * 0.11, y + h * 0.5],
                    fill=(190, 210, 200))
    # globe on the table
    gx, gy, gr = x + w * 0.5, y + h * 0.52, h * 0.26
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(70, 130, 180))
    d.ellipse([gx - gr * 0.5, gy - gr * 0.7, gx + gr * 0.2, gy - gr * 0.1],
              fill=(110, 170, 110))
    d.ellipse([gx - gr * 0.2, gy + gr * 0.15, gx + gr * 0.6, gy + gr * 0.7],
              fill=(110, 170, 110))
    d.rectangle([gx - 2, gy + gr, gx + 2, gy + gr + h * 0.08], fill=(90, 70, 50))
    # delegates along the table
    shirts = [(150, 60, 60), (60, 90, 150), (60, 130, 90), (170, 130, 60),
              (120, 80, 150), (60, 130, 140), (180, 100, 60)]
    for i, sh in enumerate(shirts):
        person(d, x + w * (0.08 + i * 0.14), y + h * 0.78, h * 0.16, sh)
    d.rectangle([x + w * 0.03, y + h * 0.76, x + w * 0.97, y + h * 0.88],
                fill=(122, 84, 52))
    # clock: talks ran out of time
    cx, cy, cr = x + w * 0.88, y + h * 0.2, h * 0.16
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(255, 255, 255),
              outline=(60, 60, 60), width=2)
    d.line([cx, cy, cx, cy - cr * 0.7], fill=(60, 60, 60), width=2)
    d.line([cx, cy, cx + cr * 0.55, cy + cr * 0.25], fill=(60, 60, 60), width=2)
    # NO DEAL banner
    scene_tag(d, x, y, w, h, "NO DEAL", RED_DK)


def scene_drones(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (10, 18, 40), (28, 44, 80))
    stars(d, x, y, w, h, [(12, 8, 1), (40, 5, 1), (70, 12, 1), (95, 6, 1),
                          (55, 18, 1), (25, 22, 1), (88, 22, 1)])
    # searchlight
    d.polygon([(x + w * 0.72, y + h), (x + w * 0.5, y + h * 0.1),
               (x + w * 0.62, y + h * 0.1)], fill=(255, 250, 200))
    # skyline
    base = y + h
    for bx, bw, bh in [(0.0, 0.16, 0.5), (0.17, 0.13, 0.68), (0.31, 0.15, 0.45),
                       (0.47, 0.14, 0.6), (0.62, 0.16, 0.42), (0.79, 0.12, 0.55),
                       (0.92, 0.08, 0.38)]:
        building(d, x + w * bx, base - h * bh, w * bw, h * bh, (24, 30, 46))
    # burning block, left of centre
    bx0 = x + w * 0.3
    d.rectangle([bx0, base - h * 0.72, bx0 + w * 0.13, base], fill=(36, 36, 36))
    flame(d, bx0 + w * 0.065, base - h * 0.55, h * 0.16)
    smoke(d, bx0 + w * 0.07, base - h * 0.85, h * 0.14)
    # drones overhead
    for dx, dy, s in [(0.15, 0.18, 5), (0.42, 0.12, 4), (0.6, 0.24, 5),
                      (0.82, 0.14, 4), (0.93, 0.3, 3)]:
        drone_x(d, x + w * dx, y + h * dy, s)
    scene_tag(d, x, y, w, h, "186 DRONES", RED_DK)


def scene_warship(d, x, y, w, h):
    sky_bands(d, x, y, w, h * 0.55, (232, 196, 150), (246, 224, 190))
    d.ellipse([x + w * 0.78, y + h * 0.06, x + w * 0.78 + h * 0.2,
               y + h * 0.06 + h * 0.2], fill=(250, 200, 90))
    # sea
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(52, 108, 150))
    d.rectangle([x, y + h * 0.55, x + w, y + h * 0.62], fill=(90, 150, 190))
    # warship, listing to starboard, on fire amidships
    hx, hy = x + w * 0.08, y + h * 0.52
    hull = [(hx, hy), (hx + w * 0.62, hy), (hx + w * 0.68, hy + h * 0.12),
            (hx + w * 0.6, hy + h * 0.22), (hx + w * 0.06, hy + h * 0.22),
            (hx - w * 0.02, hy + h * 0.1)]
    d.polygon(hull, fill=(70, 74, 80))
    d.rectangle([hx + w * 0.18, hy - h * 0.16, hx + w * 0.34, hy],
                fill=(90, 94, 100))
    d.rectangle([hx + w * 0.4, hy - h * 0.1, hx + w * 0.48, hy],
                fill=(90, 94, 100))
    d.line([hx + w * 0.26, hy - h * 0.16, hx + w * 0.26, hy - h * 0.32],
           fill=(60, 60, 60), width=2)
    flame(d, hx + w * 0.44, hy - h * 0.02, h * 0.2)
    flame(d, hx + w * 0.52, hy - h * 0.02, h * 0.13)
    smoke(d, hx + w * 0.48, hy - h * 0.28, h * 0.16)
    # drone boat + wake
    d.polygon([(x + w * 0.78, y + h * 0.78), (x + w * 0.9, y + h * 0.78),
               (x + w * 0.87, y + h * 0.86), (x + w * 0.8, y + h * 0.86)],
              fill=(40, 40, 40))
    d.line([x + w * 0.62, y + h * 0.84, x + w * 0.78, y + h * 0.82],
           fill=(255, 255, 255), width=2)
    scene_tag(d, x, y, w, h, "WARSHIP HIT", (176, 110, 20))


def scene_hongkong(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (200, 222, 238), (236, 240, 244))
    base = y + h
    for bx, bw, bh in [(0.0, 0.14, 0.55), (0.15, 0.12, 0.75), (0.28, 0.14, 0.5),
                       (0.72, 0.13, 0.62), (0.86, 0.14, 0.45)]:
        building(d, x + w * bx, base - h * bh, w * bw, h * bh, (120, 140, 165),
                 lit=(255, 240, 190))
    # ballot box, centre
    bx0, by0, bw, bh = x + w * 0.4, y + h * 0.3, w * 0.26, h * 0.5
    d.rectangle([bx0, by0, bx0 + bw, by0 + bh], fill=(255, 255, 255),
                outline=(90, 90, 90), width=2)
    d.rectangle([bx0 + bw * 0.25, by0 + 4, bx0 + bw * 0.75, by0 + 8],
                fill=(60, 60, 60))
    # ballot going in
    d.polygon([(bx0 + bw * 0.3, by0 - h * 0.16), (bx0 + bw * 0.7, by0 - h * 0.16),
               (bx0 + bw * 0.62, by0 + 2), (bx0 + bw * 0.38, by0 + 2)],
              fill=(255, 255, 255), outline=(90, 90, 90))
    # big red check
    d.line([bx0 + bw * 0.2, by0 + bh * 0.55, bx0 + bw * 0.42, by0 + bh * 0.78],
           fill=RED, width=4)
    d.line([bx0 + bw * 0.42, by0 + bh * 0.78, bx0 + bw * 0.85, by0 + bh * 0.25],
           fill=RED, width=4)
    scene_tag(d, x, y, w, h, "723 SEATS", RED_DK)


def scene_democrats(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (30, 60, 120), (70, 110, 180))
    stars(d, x, y, w, h, [(10, 8, 1), (30, 5, 1), (55, 10, 1), (85, 6, 1),
                          (70, 16, 1), (20, 18, 1)])
    # Capitol dome
    cx, base = x + w * 0.5, y + h * 0.92
    d.rectangle([x + w * 0.18, base - h * 0.18, x + w * 0.82, base],
                fill=(235, 235, 228))
    d.ellipse([cx - w * 0.16, base - h * 0.62, cx + w * 0.16, base - h * 0.1],
              fill=(245, 245, 238))
    d.rectangle([cx - w * 0.18, base - h * 0.3, cx + w * 0.18, base - h * 0.16],
                fill=(235, 235, 228))
    d.rectangle([cx - 2, base - h * 0.78, cx + 2, base - h * 0.6],
                fill=(235, 235, 228))
    d.ellipse([cx - 3, base - h * 0.82, cx + 3, base - h * 0.74],
              fill=(235, 235, 228))
    for i in range(7):
        d.rectangle([x + w * (0.24 + i * 0.085), base - h * 0.16,
                     x + w * (0.24 + i * 0.085) + 3, base - h * 0.03],
                    fill=(180, 180, 170))
    # 258 banner: one white box, number and word together
    scene_tag(d, x, y, w, h, "258 SEATS", (255, 255, 255), fg=NAVY)


def scene_bahrain(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (24, 30, 54), (58, 60, 92))
    stars(d, x, y, w, h, [(10, 8, 1), (35, 5, 1), (60, 10, 1), (88, 7, 1)])
    # radar dish left: pedestal + tilted dish + signal arcs
    rx, ry = x + w * 0.2, y + h * 0.55
    d.polygon([(rx - w * 0.06, y + h * 0.9), (rx + w * 0.06, y + h * 0.9),
               (rx + w * 0.02, ry), (rx - w * 0.02, ry)], fill=(150, 150, 155))
    d.pieslice([rx - w * 0.17, ry - h * 0.34, rx + w * 0.17, ry + h * 0.34],
               start=280, end=80, fill=(215, 215, 220))
    d.arc([rx - w * 0.17, ry - h * 0.34, rx + w * 0.17, ry + h * 0.34],
          start=280, end=80, fill=(120, 120, 125), width=2)
    d.ellipse([rx - 3, ry - 3, rx + 3, ry + 3], fill=(120, 120, 125))
    for r in (0.24, 0.3):
        d.arc([rx - w * r, ry - h * r * 1.5, rx + w * r, ry + h * r * 1.5],
              start=300, end=60, fill=(255, 120, 90), width=2)
    # missile arcs
    d.arc([x + w * 0.3, y - h * 0.1, x + w * 0.95, y + h * 0.9],
          start=270, end=20, fill=(255, 180, 80), width=2)
    d.arc([x + w * 0.35, y + h * 0.05, x + w * 0.9, y + h * 0.95],
          start=270, end=10, fill=(255, 180, 80), width=2)
    # industrial blocks right, one burning
    d.rectangle([x + w * 0.62, y + h * 0.6, x + w * 0.82, y + h * 0.92],
                fill=(90, 90, 100))
    d.rectangle([x + w * 0.84, y + h * 0.68, x + w * 0.98, y + h * 0.92],
                fill=(110, 110, 118))
    flame(d, x + w * 0.72, y + h * 0.6, h * 0.14)
    smoke(d, x + w * 0.72, y + h * 0.42, h * 0.12)
    scene_tag(d, x, y, w, h, "2 RADARS?", AMBER)


def scene_cricket(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(96, 160, 96))
    d.ellipse([x + w * 0.05, y + h * 0.05, x + w * 0.95, y + h * 0.95],
              fill=(120, 185, 120))
    # pitch
    d.rectangle([x + w * 0.44, y + h * 0.12, x + w * 0.56, y + h * 0.88],
                fill=(214, 196, 150))
    # stumps
    for sx in (0.465, 0.5, 0.535):
        d.line([x + w * sx, y + h * 0.2, x + w * sx, y + h * 0.3],
               fill=(250, 220, 120), width=2)
    for sx in (0.465, 0.5, 0.535):
        d.line([x + w * sx, y + h * 0.7, x + w * sx, y + h * 0.8],
               fill=(250, 220, 120), width=2)
    # batsman
    person(d, x + w * 0.38, y + h * 0.62, h * 0.18, (255, 255, 255))
    d.line([x + w * 0.38, y + h * 0.5, x + w * 0.47, y + h * 0.62],
           fill=(180, 140, 90), width=3)
    # ball
    d.ellipse([x + w * 0.6, y + h * 0.3, x + w * 0.6 + 5, y + h * 0.3 + 5],
              fill=(178, 34, 34))
    # scoreboard
    d.rectangle([x, y, x + w * 0.3, y + h * 0.24], fill=(20, 40, 20))
    f = font_sans_bold(max(11, int(h * 0.16)))
    d.text((x + 5, y + 2), "720/9", font=f, fill=(140, 255, 140))


def scene_f1(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (16, 16, 34), (48, 36, 80))
    # neon strip lights
    for i, col in enumerate([(255, 60, 120), (60, 200, 255), (255, 200, 60)]):
        d.rectangle([x + w * (0.05 + i * 0.3), y + h * 0.1,
                     x + w * (0.05 + i * 0.3) + w * 0.2, y + h * 0.16],
                    fill=col)
    # track
    d.rectangle([x, y + h * 0.62, x + w, y + h * 0.92], fill=(50, 50, 56))
    for i in range(8):
        d.rectangle([x + w * (0.02 + i * 0.125), y + h * 0.75,
                     x + w * (0.02 + i * 0.125) + w * 0.06, y + h * 0.78],
                    fill=(255, 255, 255))
    # race car, side profile
    cx, cy = x + w * 0.5, y + h * 0.66
    # low body
    d.rectangle([cx - w * 0.3, cy, cx + w * 0.3, cy + h * 0.1],
                fill=(200, 30, 40))
    # nose taper
    d.polygon([(cx - w * 0.3, cy + h * 0.1), (cx - w * 0.38, cy + h * 0.07),
               (cx - w * 0.38, cy + h * 0.04), (cx - w * 0.3, cy)],
              fill=(200, 30, 40))
    # cockpit hump + driver helmet
    d.polygon([(cx - w * 0.08, cy), (cx - w * 0.02, cy - h * 0.1),
               (cx + w * 0.08, cy - h * 0.1), (cx + w * 0.12, cy)],
              fill=(200, 30, 40))
    d.ellipse([cx - w * 0.01, cy - h * 0.13, cx + w * 0.05, cy - h * 0.07],
              fill=(255, 255, 255))
    # rear wing
    d.line([cx + w * 0.24, cy - h * 0.02, cx + w * 0.24, cy - h * 0.14],
           fill=(30, 30, 30), width=2)
    d.rectangle([cx + w * 0.2, cy - h * 0.16, cx + w * 0.32, cy - h * 0.13],
                fill=(30, 30, 30))
    # wheels
    for wx in (-0.22, 0.18):
        d.ellipse([cx + w * wx - 5, cy + h * 0.07, cx + w * wx + 5,
                   cy + h * 0.07 + 10], fill=(20, 20, 20))
        d.ellipse([cx + w * wx - 2, cy + h * 0.07 + 3, cx + w * wx + 2,
                   cy + h * 0.07 + 7], fill=(180, 180, 180))
    # chequered flag
    fx, fy = x + w * 0.84, y + h * 0.28
    d.line([fx, fy, fx, fy + h * 0.3], fill=(220, 220, 220), width=2)
    for r in range(3):
        for c in range(4):
            col = (20, 20, 20) if (r + c) % 2 == 0 else (255, 255, 255)
            d.rectangle([fx + c * 5, fy + r * 5, fx + c * 5 + 5, fy + r * 5 + 5],
                        fill=col)
    scene_tag(d, x, y, w, h, "35 LEAD CHANGES", (30, 30, 40),
              fg=(255, 220, 80))


def scene_tennis(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(70, 110, 190))
    d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.92, y + h * 0.86],
                fill=(90, 140, 210))
    d.rectangle([x + w * 0.08, y + h * 0.14, x + w * 0.92, y + h * 0.86],
                outline=(255, 255, 255), width=2)
    # net
    d.line([x + w * 0.08, y + h * 0.5, x + w * 0.92, y + h * 0.5],
           fill=(255, 255, 255), width=2)
    d.rectangle([x + w * 0.08, y + h * 0.5, x + w * 0.92, y + h * 0.56],
                fill=(40, 40, 40))
    # player serving
    person(d, x + w * 0.3, y + h * 0.42, h * 0.16, (255, 255, 255))
    d.line([x + w * 0.3, y + h * 0.3, x + w * 0.42, y + h * 0.18],
           fill=(240, 240, 240), width=2)
    d.ellipse([x + w * 0.4, y + h * 0.12, x + w * 0.4 + 7, y + h * 0.12 + 7],
              fill=(220, 230, 60))
    # trophy
    tx, ty = x + w * 0.78, y + h * 0.6
    d.rectangle([tx - 3, ty, tx + 3, ty + h * 0.14], fill=(220, 180, 60))
    d.ellipse([tx - 8, ty - h * 0.12, tx + 8, ty + 2], fill=(240, 200, 80))
    d.rectangle([tx - 8, ty + h * 0.14, tx + 8, ty + h * 0.18],
                fill=(120, 80, 40))
    scene_tag(d, x, y, w, h, "6-2, 7-6(7)", (20, 60, 120))


def scene_korea(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (200, 222, 238), (240, 242, 245))
    # school building
    bx0, by0 = x + w * 0.06, y + h * 0.24
    d.rectangle([bx0, by0, bx0 + w * 0.5, y + h * 0.92], fill=(170, 160, 140))
    d.polygon([(bx0 - 4, by0), (bx0 + w * 0.25, by0 - h * 0.14),
               (bx0 + w * 0.5 + 4, by0)], fill=(140, 60, 60))
    for r in range(3):
        for c in range(4):
            d.rectangle([bx0 + w * (0.04 + c * 0.11), by0 + h * (0.1 + r * 0.2),
                         bx0 + w * (0.04 + c * 0.11) + w * 0.06,
                         by0 + h * (0.1 + r * 0.2) + h * 0.12],
                        fill=(230, 235, 240))
    # exam paper + pen, right
    px0, py0 = x + w * 0.64, y + h * 0.16
    d.rectangle([px0, py0, px0 + w * 0.3, py0 + h * 0.66], fill=(255, 255, 255),
                outline=(120, 120, 120), width=2)
    for i in range(4):
        d.line([px0 + 6, py0 + h * (0.12 + i * 0.12),
                px0 + w * 0.3 - 6, py0 + h * (0.12 + i * 0.12)],
               fill=(170, 170, 170), width=2)
    d.line([px0 + 6, py0 + h * 0.58, px0 + w * 0.12, py0 + h * 0.7],
           fill=GREEN, width=3)
    d.line([px0 + w * 0.12, py0 + h * 0.7, px0 + w * 0.24, py0 + h * 0.5],
           fill=GREEN, width=3)
    scene_tag(d, x, y, w, h, "RESIGNED", RED_DK)


def scene_delta(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (190, 214, 232), (235, 240, 245))
    # control tower
    tx0 = x + w * 0.08
    d.rectangle([tx0, y + h * 0.3, tx0 + w * 0.08, y + h * 0.9],
                fill=(140, 140, 145))
    d.rectangle([tx0 - w * 0.02, y + h * 0.18, tx0 + w * 0.1, y + h * 0.32],
                fill=(90, 120, 160))
    # terminal
    d.rectangle([x + w * 0.2, y + h * 0.62, x + w * 0.98, y + h * 0.92],
                fill=(200, 200, 195))
    for i in range(6):
        d.rectangle([x + w * (0.24 + i * 0.12), y + h * 0.68,
                     x + w * (0.24 + i * 0.12) + w * 0.07, y + h * 0.8],
                    fill=(120, 160, 200))
    # plane on the ground, waiting — side profile
    px, py = x + w * 0.5, y + h * 0.42
    # fuselage
    d.ellipse([px - w * 0.3, py - h * 0.06, px + w * 0.3, py + h * 0.06],
              fill=(255, 255, 255))
    d.rectangle([px - w * 0.28, py - h * 0.06, px + w * 0.26, py + h * 0.06],
                fill=(255, 255, 255))
    # nose (left) and cockpit windows
    d.polygon([(px - w * 0.3, py), (px - w * 0.24, py - h * 0.06),
               (px - w * 0.24, py + h * 0.06)], fill=(200, 220, 240))
    for i in range(4):
        d.rectangle([px - w * (0.18 - i * 0.1), py - h * 0.04,
                     px - w * (0.18 - i * 0.1) + 5, py],
                    fill=(120, 160, 200))
    # tail fin (right) + wing
    d.polygon([(px + w * 0.22, py), (px + w * 0.3, py - h * 0.2),
               (px + w * 0.34, py - h * 0.2), (px + w * 0.3, py)],
              fill=(200, 30, 50))
    d.polygon([(px - w * 0.02, py + h * 0.04), (px - w * 0.14, py + h * 0.16),
               (px - w * 0.06, py + h * 0.16)], fill=(190, 190, 190))
    # landing gear
    for gx in (-0.2, 0.16):
        d.line([px + w * gx, py + h * 0.06, px + w * gx, py + h * 0.14],
               fill=(90, 90, 90), width=2)
        d.ellipse([px + w * gx - 3, py + h * 0.13, px + w * gx + 3,
                   py + h * 0.13 + 6], fill=(40, 40, 40))
    scene_tag(d, x, y, w, h, "1,600+ DELAYED", (20, 50, 110))


def scene_pope(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (222, 214, 190), (244, 238, 220))
    # dome of St Peter's
    cx, base = x + w * 0.5, y + h * 0.66
    d.rectangle([x + w * 0.1, base - h * 0.16, x + w * 0.9, base],
                fill=(214, 200, 170))
    d.ellipse([cx - w * 0.2, base - h * 0.55, cx + w * 0.2, base - h * 0.05],
              fill=(196, 178, 140))
    d.rectangle([cx - 2, base - h * 0.68, cx + 2, base - h * 0.52],
                fill=(170, 150, 115))
    # long lunch table with guests
    d.rectangle([x + w * 0.06, y + h * 0.72, x + w * 0.94, y + h * 0.84],
                fill=(255, 255, 255))
    d.rectangle([x + w * 0.06, y + h * 0.72, x + w * 0.94, y + h * 0.76],
                fill=(200, 60, 60))
    for i in range(6):
        person(d, x + w * (0.12 + i * 0.15), y + h * 0.74, h * 0.12,
               [(90, 120, 160), (160, 120, 80), (120, 90, 140),
                (80, 140, 100), (180, 120, 60), (140, 80, 80)][i])
    scene_tag(d, x, y, w, h, "1,300 GUESTS", (120, 90, 40))


def scene_cikande(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (240, 200, 160), (248, 228, 200))
    # three-storey factory
    bx0, by0 = x + w * 0.14, y + h * 0.3
    d.rectangle([bx0, by0, bx0 + w * 0.6, y + h * 0.92], fill=(190, 170, 140))
    for r in range(3):
        for c in range(5):
            d.rectangle([bx0 + w * (0.04 + c * 0.11), by0 + h * (0.08 + r * 0.18),
                         bx0 + w * (0.04 + c * 0.11) + w * 0.06,
                         by0 + h * (0.08 + r * 0.18) + h * 0.1],
                        fill=(90, 70, 50))
    # flames from the roof
    flame(d, bx0 + w * 0.25, by0 + 2, h * 0.16)
    flame(d, bx0 + w * 0.45, by0 + 2, h * 0.2)
    flame(d, bx0 + w * 0.6, by0 + 2, h * 0.12)
    smoke(d, bx0 + w * 0.4, by0 - h * 0.18, h * 0.16)
    # fire crew figure + hose
    person(d, x + w * 0.85, y + h * 0.92, h * 0.14, (220, 60, 40))
    d.line([x + w * 0.85, y + h * 0.82, bx0 + w * 0.62, y + h * 0.7],
           fill=(200, 200, 200), width=2)
    scene_tag(d, x, y, w, h, "3 DEAD, 34 MISSING", RED_DK)


def scene_gaza(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (226, 214, 186), (244, 238, 222))
    # damaged blocks
    base = y + h
    for bx, bw, bh in [(0.02, 0.2, 0.5), (0.24, 0.18, 0.62), (0.44, 0.2, 0.45)]:
        d.rectangle([x + w * bx, base - h * bh, x + w * (bx + bw), base],
                    fill=(178, 164, 138))
        for r in range(3):
            for c in range(2):
                d.rectangle([x + w * bx + w * (0.03 + c * 0.08),
                             base - h * bh + h * (0.08 + r * 0.14),
                             x + w * bx + w * (0.03 + c * 0.08) + 5,
                             base - h * bh + h * (0.08 + r * 0.14) + 6],
                            fill=(90, 80, 65))
    smoke(d, x + w * 0.32, base - h * 0.72, h * 0.12)
    # aid truck
    tx0, ty0 = x + w * 0.64, y + h * 0.6
    d.rectangle([tx0, ty0, tx0 + w * 0.3, ty0 + h * 0.24], fill=(255, 255, 255),
                outline=(120, 120, 120), width=2)
    d.rectangle([tx0 + w * 0.3, ty0 + h * 0.08, tx0 + w * 0.36,
                 ty0 + h * 0.24], fill=(220, 220, 220))
    d.rectangle([tx0 + w * 0.12, ty0 + h * 0.05, tx0 + w * 0.16,
                 ty0 + h * 0.19], fill=RED)
    d.rectangle([tx0 + w * 0.08, ty0 + h * 0.1, tx0 + w * 0.2,
                 ty0 + h * 0.14], fill=RED)
    for wx in (0.06, 0.28):
        d.ellipse([tx0 + w * wx - 4, ty0 + h * 0.22, tx0 + w * wx + 4,
                   ty0 + h * 0.22 + 8], fill=(40, 40, 40))
    # food parcels
    for px, py in [(0.68, 0.88), (0.76, 0.88), (0.72, 0.8)]:
        d.rectangle([x + w * px, y + h * py, x + w * px + 8, y + h * py + 7],
                    fill=(200, 170, 110), outline=(140, 110, 70))
    scene_tag(d, x, y, w, h, "4 KILLED", SLATE)


def scene_khartoum(d, x, y, w, h):
    sky_bands(d, x, y, w, h, (250, 190, 130), (250, 220, 180))
    d.ellipse([x + w * 0.7, y + h * 0.08, x + w * 0.7 + h * 0.18,
               y + h * 0.08 + h * 0.18], fill=(250, 180, 80))
    base = y + h
    for bx, bw, bh in [(0.0, 0.18, 0.42), (0.19, 0.15, 0.58), (0.35, 0.17, 0.48),
                       (0.53, 0.14, 0.38), (0.68, 0.16, 0.5), (0.85, 0.15, 0.4)]:
        building(d, x + w * bx, base - h * bh, w * bw, h * bh, (150, 120, 95),
                 lit=(255, 230, 170), lit_frac=0.35)
    # drones at dawn
    for dx, dy, s in [(0.2, 0.16, 4), (0.48, 0.1, 3), (0.62, 0.22, 4)]:
        drone_x(d, x + w * dx, y + h * dy, s)
    # UN flag on a pole
    fx = x + w * 0.85
    d.line([fx, y + h * 0.3, fx, y + h * 0.62], fill=(90, 90, 90), width=2)
    d.rectangle([fx, y + h * 0.3, fx + w * 0.12, y + h * 0.44],
                fill=(80, 140, 200))
    d.ellipse([fx + w * 0.03, y + h * 0.33, fx + w * 0.09, y + h * 0.41],
              fill=(255, 255, 255))
    scene_tag(d, x, y, w, h, "4 KILLED", SLATE)


SCENES = {
    "cop31": scene_cop31,
    "drones": scene_drones,
    "warship": scene_warship,
    "hongkong": scene_hongkong,
    "democrats": scene_democrats,
    "bahrain": scene_bahrain,
    "cricket": scene_cricket,
    "f1": scene_f1,
    "tennis": scene_tennis,
    "korea": scene_korea,
    "delta": scene_delta,
    "pope": scene_pope,
    "cikande": scene_cikande,
    "gaza": scene_gaza,
    "khartoum": scene_khartoum,
}


# ---------------------------------------------------------------- layout
MARGIN = 16
CONTENT_W = W - 2 * MARGIN  # 992


def draw_top_bar(d):
    d.rectangle([0, 0, W, 22], fill=NAVY)
    f = font_sans_bold(10)
    d.text((MARGIN, 4), "THE WORLD IN ONE DAY", font=f, fill=(255, 255, 255))
    right = "39 STORIES · 7 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    w = d.textlength(right, font=f)
    d.text((W - MARGIN - w, 4), right, font=f, fill=(200, 210, 230))


def draw_masthead(d):
    f = font_disp_black(54)
    text_center(d, W // 2, 26, "Sunday 22 November 2026", f, INK)
    f2 = font_serif_italic(16)
    text_center(d, W // 2, 86,
                "COP31 collapses with no deal · 186 drones over Ukraine · "
                "a Russian warship sunk in Libya",
                f2, RED_DK)
    d.line([MARGIN, 110, W - MARGIN, 110], fill=RULE, width=1)
    d.line([MARGIN, 112, W - MARGIN, 112], fill=RULE, width=1)


def draw_numbers(d, y):
    cell = CONTENT_W / len(NUMBERS)
    f_num = font_serif_bold(24)
    f_lab = font_sans(9)
    for i, (num, label) in enumerate(NUMBERS):
        x = MARGIN + i * cell
        text_center(d, x + cell / 2, y, num, f_num, RED_DK)
        text_center(d, x + cell / 2, y + 28, label, f_lab, GREY)
        if i:
            d.line([x, y + 2, x, y + 42], fill=RULE, width=1)
    d.line([MARGIN, y + 46, W - MARGIN, y + 46], fill=RULE, width=1)
    return y + 48


def region_counts():
    counts = {}
    for card in CARDS:
        counts[card[7]] = counts.get(card[7], 0) + 1
    for region, _t, _s in ALSO:
        counts[region] = counts.get(region, 0) + 1
    return counts


def draw_region_bar(d, y):
    counts = region_counts()
    order = ["EUROPE", "MIDEAST", "ASIA", "AMERICAS", "AFRICA", "OCEANIA",
             "WORLD"]
    total = sum(counts[r] for r in order)
    x = MARGIN
    f = font_sans_bold(10)
    for region in order:
        w = CONTENT_W * counts[region] / total
        d.rectangle([x, y, x + w, y + 18], fill=REGIONS[region])
        label = "%s %d" % (region, counts[region])
        tw = d.textlength(label, font=f)
        d.text((x + (w - tw) / 2, y + 3), label, font=f, fill=(255, 255, 255))
        x += w
    return y + 20


def draw_timeline(d, y):
    d.rectangle([MARGIN, y, W - MARGIN, y + 20], fill=NAVY2)
    # pick the largest font size that fits the whole strip in one line
    for size in (9, 8, 7):
        f_lab = font_sans_bold(size)
        f_txt = font_sans(size)
        total = d.textlength("THE DAY IN UTC", font=f_lab) + 10
        for time, label in TIMELINE:
            total += (d.textlength(time, font=f_lab) + 4
                      + d.textlength(label, font=f_txt) + 4
                      + d.textlength("·", font=f_txt) + 4)
        if total <= CONTENT_W - 12:
            break
    x = MARGIN + 6
    d.text((x, y + 5), "THE DAY IN UTC", font=f_lab, fill=(255, 210, 90))
    x += d.textlength("THE DAY IN UTC", font=f_lab) + 10
    for time, label in TIMELINE:
        d.text((x, y + 5), time, font=f_lab, fill=(255, 210, 90))
        x += d.textlength(time, font=f_lab) + 4
        d.text((x, y + 5), label, font=f_txt, fill=(255, 255, 255))
        x += d.textlength(label, font=f_txt) + 4
        d.text((x, y + 5), "·", font=f_txt, fill=(160, 170, 195))
        x += d.textlength("·", font=f_txt) + 4
    return y + 22


def draw_card(d, card, x, y, w, h, big):
    num, scene, eyebrow, headline, deck, source, kind, region, _lon, _lat = card
    d.rectangle([x, y, x + w, y + h], fill=CARD_BG, outline=CARD_LINE, width=1)
    img_h = 100 if big else 64
    SCENES[scene](d, x + 1, y + 1, w - 2, img_h)
    # number disc over the picture's corner
    number_disc(d, x + 14, y + img_h - 8, num, r=9)
    ty = y + img_h + 5
    # eyebrow: location + badge (truncate the eyebrow if it would hit the badge)
    col = REGIONS[region]
    f_eye = font_sans_bold(8 if big else 7)
    eye = eyebrow
    avail_eye = w - 10 - _badge_w(d, kind) - 4
    while eye and d.textlength(eye, font=f_eye) > avail_eye:
        if " " in eye:
            eye = eye.rsplit(" ", 1)[0].rstrip(" ·,-")
        else:
            eye = eye[:-1]
    d.text((x + 5, ty), eye, font=f_eye, fill=col)
    badge(d, x + w - 5 - _badge_w(d, kind), ty - 1, kind)
    ty += 13 if big else 11
    # headline
    f_head = font_serif_bold(18 if big else 12)
    lead = 21 if big else 14
    max_hl = 2 if big else 2
    lines = wrap_text(d, headline, f_head, w - 10)
    lines = lines[:max_hl]
    for i, line in enumerate(lines):
        d.text((x + 5, ty + i * lead), line, font=f_head, fill=INK)
    ty += len(lines) * lead + 2
    # deck
    f_deck = font_sans(10 if big else 8)
    deck_lead = 12 if big else 10
    avail = (y + h - 4) - ty
    max_deck = max(1, int(avail // deck_lead))
    dlines = wrap_text(d, deck, f_deck, w - 10)
    dlines = dlines[:max_deck]
    for i, line in enumerate(dlines):
        d.text((x + 5, ty + i * deck_lead), line, font=f_deck,
               fill=(60, 60, 60))
    ty += len(dlines) * deck_lead
    # source tag, bottom-right of the text block
    f_src = font_sans_italic(8 if big else 7)
    src = "(%s)" % source
    sw = d.textlength(src, font=f_src)
    d.text((x + w - 5 - sw, y + h - 12), src, font=f_src, fill=GREY)


def _badge_w(d, kind):
    _color, label = BADGES[kind]
    return d.textlength(label, font=font_sans_bold(8)) + 10


def draw_also(d, x, y, w, h):
    f_head = font_sans_bold(11)
    d.text((x, y), "ALSO ON SUNDAY 22 NOVEMBER — 24 MORE STORIES",
           font=f_head, fill=INK)
    d.line([x, y + 16, x + w, y + 16], fill=RULE, width=1)
    cols = 3
    col_w = w / cols
    rows = 8
    f_txt = font_sans(9)
    f_num = font_sans_bold(9)
    item_h = (h - 20) / rows
    for i, (region, text, source) in enumerate(ALSO):
        col = i // rows
        row = i % rows
        ix = x + col * col_w
        iy = y + 20 + row * item_h
        num = 16 + i
        d.text((ix, iy), str(num), font=f_num, fill=RED_DK)
        nx = ix + d.textlength(str(num), font=f_num) + 4
        # region dot
        d.ellipse([nx, iy + 3, nx + 6, iy + 9], fill=REGIONS[region])
        tx = nx + 10
        full = text + " (" + source + ")"
        lines = wrap_text(d, full, f_txt, col_w - (tx - ix) - 4)
        for j, line in enumerate(lines[:2]):
            d.text((tx, iy + j * 10), line, font=f_txt, fill=INK)


def draw_map(d, x, y, w, h):
    f_head = font_sans_bold(11)
    d.text((x, y), "WHERE IT HAPPENED", font=f_head, fill=INK)
    d.line([x, y + 16, x + w, y + 16], fill=RULE, width=1)
    mx, my, mw, mh = x, y + 20, w, h - 20
    d.rectangle([mx, my, mx + mw, my + mh], fill=SEA, outline=CARD_LINE,
                width=1)
    lon0, lon1, lat0, lat1 = -170, 190, -60, 85

    def proj(lon, lat):
        px = mx + (lon - lon0) / (lon1 - lon0) * mw
        py = my + (lat1 - lat) / (lat1 - lat0) * mh
        return px, py

    for poly in CONTINENTS:
        pts = [proj(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=LAND, outline=LAND_LINE)
    # pins
    f_pin = font_sans_bold(8)
    for card in CARDS:
        num, _sc, _e, _h2, _dk, _s, _k, _r, lon, lat = card
        px, py = proj(lon, lat)
        dx, dy = PIN_NUDGE.get(num, (0, 0))
        qx, qy = px + dx, py + dy
        if (dx, dy) != (0, 0):
            d.line([px, py, qx, qy], fill=(120, 120, 120), width=1)
        r = 7
        d.ellipse([qx - r, qy - r, qx + r, qy + r], fill=RED_DK,
                  outline=(255, 255, 255), width=1)
        s = str(num)
        sw = d.textlength(s, font=f_pin)
        d.text((qx - sw / 2, qy - 5), s, font=f_pin, fill=(255, 255, 255))
    f_cap = font_sans_italic(8)
    d.text((mx + 4, my + mh - 12), "pins = card numbers", font=f_cap,
           fill=GREY)


def draw_datecheck(d, y):
    h = 54
    d.rectangle([MARGIN, y, W - MARGIN, y + h], outline=RED, width=2)
    f_head = font_sans_bold(10)
    f_txt = font_sans(9)
    head = "DATE CHECK"
    d.text((MARGIN + 6, y + 5), head, font=f_head, fill=RED_DK)
    hx = MARGIN + 6 + d.textlength(head, font=f_head) + 8
    intro = ("Every story on this page happened or was first reported on "
             "Sunday 22 November 2026 (UTC). Left out as other days' news: ")
    body = intro + " · ".join(DATECHECK) + "."
    lines = wrap_text(d, body, f_txt, CONTENT_W - (hx - MARGIN) - 12)
    for i, line in enumerate(lines[:3]):
        d.text((hx, y + 5 + i * 12), line, font=f_txt, fill=INK)
    return y + h + 4


def draw_footer(d, y):
    f = font_sans(8)
    d.text((MARGIN, y), SOURCES_LINE, font=f, fill=GREY)
    d.rectangle([0, H - 22, W, H], fill=NAVY)
    f2 = font_sans_bold(9)
    d.text((MARGIN, H - 17), "THE WORLD IN ONE DAY", font=f2,
           fill=(255, 255, 255))
    right = "SUNDAY 22 NOVEMBER 2026 · ONE PAGE"
    w = d.textlength(right, font=f2)
    d.text((W - MARGIN - w, H - 17), right, font=f2, fill=(200, 210, 230))


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_top_bar(d)
    draw_masthead(d)
    y = draw_numbers(d, 118)
    y = draw_region_bar(d, y + 2)
    y = draw_timeline(d, y + 2)
    # big cards: 3 across
    gap = 8
    bw = (CONTENT_W - 2 * gap) // 3
    bh = 196
    y_big = y + 4
    for i in range(3):
        draw_card(d, CARDS[i], MARGIN + i * (bw + gap), y_big, bw, bh, True)
    # small cards: 6 across, 2 rows
    sw = (CONTENT_W - 5 * gap) // 6
    sh = 150
    y_small1 = y_big + bh + 6
    for i in range(6):
        draw_card(d, CARDS[3 + i], MARGIN + i * (sw + gap), y_small1, sw, sh,
                  False)
    y_small2 = y_small1 + sh + 6
    for i in range(6):
        draw_card(d, CARDS[9 + i], MARGIN + i * (sw + gap), y_small2, sw, sh,
                  False)
    # ALSO list + map
    y_also = y_small2 + sh + 6
    also_h = 190
    draw_also(d, MARGIN, y_also, 648, also_h)
    draw_map(d, MARGIN + 656, y_also, CONTENT_W - 656, also_h)
    y_dc = y_also + also_h + 6
    y_end = draw_datecheck(d, y_dc)
    draw_footer(d, y_end + 2)
    return img


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    img = build()
    img.save(out, format="PNG", optimize=True)
    size = os.path.getsize(out)
    print("wrote %s (%d bytes, %dx%d)" % (out, size, img.width, img.height))
    if size > 1048576:
        print("WARNING: over the 1 MiB limit", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
