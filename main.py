#!/usr/bin/env python3
"""news-image-20261122: draw 'Sunday 22 November 2026 in one picture'.

Pure Python 3.13 standard library (zlib/struct). No network, no files read,
no time or randomness: two runs write byte-identical PNGs.

Layout (1024x1024, numbered poster, not a newspaper):
  header  - the day, named in full
  legend  - CONFIRMED / OFFICIALS / REPORTED + sources
  stories - 44 numbered stories, first reported Sun 22 Nov 2026,
            one source tag each, grouped by region
  map     - world map with numbered pins ("WHERE IT HAPPENED")
  numbers - "THE DAY IN NUMBERS"
  timeline- "THE DAY IN UTC" in day-part buckets (no invented clock times)
  datecheck - "DATE CHECK": near-miss stories excluded, with their real dates
"""
import os
import struct
import sys
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 232)
INK = (20, 20, 20)
NAVY = (24, 44, 84)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
GOLD = (176, 128, 0)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
GREEN = (31, 110, 60)
SEA = (214, 228, 238)
LAND = (196, 208, 178)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits. Uppercase only (the whole poster is set in
# caps, so one case covers every letter). Drawn by hand for this entry.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "01000"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
}


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        self.rect(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.rect(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, c)

    def ring(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if r * r - 2 * r <= d <= r * r:
                    self.set(xx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                for x in range(int(xs[j]), int(xs[j + 1]) + 1):
                    self.set(x, y, c)

    def text(self, x, y, s, scale=1, color=INK, bold=False):
        s = s.upper()
        cx = x
        for ch in s:
            g = FONT.get(ch, FONT[" "])
            for r in range(7):
                for col in range(5):
                    if g[r][col] == "1":
                        for dy in range(scale):
                            for dx in range(scale):
                                self.set(cx + col * scale + dx,
                                         y + r * scale + dy, color)
                                if bold:
                                    self.set(cx + col * scale + dx + 1,
                                             y + r * scale + dy, color)
            cx += 6 * scale
        return cx

    def text_w(self, s, scale=1):
        return len(s) * 6 * scale - scale

    def fit(self, s, max_w, scale=1):
        """Truncate with an ellipsis so text never overflows its column."""
        s = s.upper()
        if self.text_w(s, scale) <= max_w:
            return s
        while s and self.text_w(s + "...", scale) > max_w:
            s = s[:-1]
        return s + "..."


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ---------------------------------------------------------------- stories
# (headline, detail, source, marker, region)
# marker: C = CONFIRMED, O = OFFICIALS SAY, R = REPORTED
# Every story was first reported on Sunday 22 November 2026.
# Headlines fit one line at scale 2 in a 488px column (~38 chars);
# details fit one line at scale 1 (~76 chars, source tag included).
STORIES = [
    ("COP31 IN OVERTIME AS 3RD DRAFT LANDS",
     "Delegates in Antalya weigh a third draft text. - REUTERS",
     "REUTERS", "C", "CLIMATE"),
    ("CANDY FACTORY FIRE: 3 DEAD, 36 MISSING",
     "Blaze at a candy plant in Cikande, Banten. - AP",
     "AP", "C", "ASIA"),
    ("NEPAL PM ARRIVES IN INDIA, 2-DAY VISIT",
     "Balendra Shah begins a two-day visit to New Delhi. - ANI",
     "ANI", "C", "ASIA"),
    ("INDIA DECLARE 720/9, LEAD NZ BY 352",
     "India pile up 720 for 9 in the Wellington Test. - AP",
     "AP", "C", "SPORT"),
    ("ZVEREV v ALCARAZ FOR ATP FINALS TONIGHT",
     "Final 18:00 CET; $5.17m if unbeaten. PREVIEW - ATP",
     "ATP", "C", "SPORT"),
    ('TRUMP SEEKS "PERMANENT" IRAN DEAL',
     "President wants a lasting nuclear deal with Tehran. - REUTERS",
     "REUTERS", "C", "US"),
    ("HOUTHI STRIKES AFTER SAUDI HODEIDA OP",
     "Strikes follow a Saudi-led operation in Hodeida. - REUTERS",
     "REUTERS", "C", "MIDEAST"),
    ("SAUDI FORCES INTERCEPT HOUTHI MISSILE",
     "Saudi air defences shoot down a Houthi missile. - AP",
     "AP", "C", "MIDEAST"),
    ("IRAN FM: HORMUZ REOPENING NOT DIFFICULT",
     "Tehran says reopening the strait would be easy. - REUTERS",
     "REUTERS", "C", "MIDEAST"),
    ("US REJECTS IRAN CLAIM IT HIT AN F-16",
     "Washington denies Tehran's claim of a jet downed. - AP",
     "AP", "C", "MIDEAST"),
    ("IRAN TANKER BURNS AFTER MINE HIT",
     "A tanker burns in Hormuz after striking a mine. - AP",
     "AP", "C", "MIDEAST"),
    ('TEHRAN RELEASES "MISSILE CITY" FOOTAGE',
     "Iran publishes video of an underground missile base. - AP",
     "AP", "C", "MIDEAST"),
    ("IRAN FM: ALLIES OPPOSE DOCTRINE SHIFT",
     "Allies oppose any change to the nuclear doctrine. - REUTERS",
     "REUTERS", "C", "MIDEAST"),
    ('PEZESHKIAN: "SILENT ECONOMIC WAR"',
     "President cites a 130-day blockade of the country. - AP",
     "AP", "C", "MIDEAST"),
    ("GAZA DISPLACED PROTEST AS STRIKES GROW",
     "Displaced Palestinians protest as strikes intensify. - AP",
     "AP", "C", "MIDEAST"),
    ("LEBANON'S AOUN DEMANDS ISRAELI EXIT",
     "Aoun calls for Israel to leave southern Lebanon. - REUTERS",
     "REUTERS", "C", "MIDEAST"),
    ("ISRAELI SOLDIER ARREST BID IN GERMANY",
     "Seeks arrest of a soldier visiting Germany. - AP",
     "AP", "C", "EUROPE"),
    ("GERMAN POLITICIAN ATTACKED AT PROTEST",
     "A politician is assaulted during a protest in Berlin. - AP",
     "AP", "C", "EUROPE"),
    ("INDIA-CHINA HOLD FRESH FRONTIER TALKS",
     "Military talks resume over the Arunachal border. - ANI",
     "ANI", "C", "ASIA"),
    ("CHINA RENEWS UN BID TO BLACKLIST BLA",
     "Beijing seeks a UN listing for BLA, Majeed Brigade. - REUTERS",
     "REUTERS", "C", "ASIA"),
    ("PAKISTAN: 15 MILITANTS KILLED",
     "Forces kill 15 militants in Mastung, Balochistan. - AP",
     "AP", "O", "ASIA"),
    ("NIGERIA 2027: YOUNG VOTER SIGN-UPS FALL",
     "Youth sign-ups drop ahead of the 2027 election. - AP",
     "AP", "C", "AFRICA"),
    ("UK POLLS TURN AGAINST BREXIT",
     "New polls show opinion shifting against leaving the EU. - POLLS",
     "POLLS", "R", "EUROPE"),
    ("EU PROPOSES A DIGITAL TAX",
     "Brussels puts forward a tax on digital services. - REUTERS",
     "REUTERS", "C", "EUROPE"),
    ("UK-INDIA DEAL SNAGS ON SCOTCH",
     "India plans 162.5% duty on bulk Scotch imports. - REUTERS",
     "REUTERS", "C", "TRADE"),
    ("CONGRESS RACES TO AVERT SHUTDOWN",
     "Lawmakers hurry to stop a pre-Christmas shutdown. - REUTERS",
     "REUTERS", "C", "US"),
    ("WHITE HOUSE REPLACES CYBER CHIEF",
     "Sean Cairncross is out as national cyber director. - NBC",
     "NBC", "R", "US"),
    ("OPENROUTER DROPS 3 PROVIDERS",
     "Providers cut after a canary-token leak. - DRAGOS",
     "DRAGOS", "R", "TECH"),
    ('GHOSTSCRIPT "UPLOAD2SHELL" FLAW FOUND',
     "Critical flaw tracked as CVE-2026-125396 is disclosed. - CVE",
     "CVE", "C", "TECH"),
    ("ANTIDEPRESSANTS: 115-TRIAL STUDY OUT",
     "A 115-trial study appears in Lancet Psychiatry. - LANCET",
     "LANCET", "C", "SCIENCE"),
    ("PHOTODIODES SET 152 GHZ RECORD",
     "Gallium-oxide photodiodes hit a 152 GHz record. - JOURNAL",
     "JOURNAL", "R", "SCIENCE"),
    ("FUKUSHIMA: 1,500 TRAPPED BY HEAVY SNOW",
     "Heavy snow strands 1,500 people in Fukushima. - AP",
     "AP", "C", "ASIA"),
    ("INDIAN NATIONAL JAILED OVER US PLOT",
     "Jailed for a plot to kill a Sikh separatist in the US. - REPORTED",
     "REPORTED", "R", "US"),
    ("VIRGINIA'S FIRST MEASLES DEATH OF 2026",
     "Virginia records its first measles death this year. - REPORTED",
     "REPORTED", "R", "US"),
    ("EX-ITALIAN POLICE CHIEF FOUND DEAD",
     "Former police chief found dead amid a mafia probe. - REPORTED",
     "REPORTED", "R", "EUROPE"),
    ("CHINESE DEFENCE CHIEFS TALK IN BRITAIN",
     "First such talks in Britain in more than 20 years. - REPORTED",
     "REPORTED", "R", "EUROPE"),
    ("LAVROV: KYIV IS HISTORICALLY RUSSIAN",
     "Lavrov claims Kyiv as historically Russian. - REPORTED",
     "REPORTED", "R", "EUROPE"),
    ("EU CHIEF CONDEMNS ALLEGED RUSSIAN PLOT",
     "EU chief condemns a supposed murder plot. - REPORTED",
     "REPORTED", "R", "EUROPE"),
    ("IOWA ARMY PLANT PLANS LEAD-AZIDE BLAST",
     "A controlled detonation is planned at the Iowa Army plant. - REPORTED",
     "REPORTED", "R", "US"),
    ("POPULAR VOTE COMPACT REACHES 222 VOTES",
     "The compact now holds 222 electoral votes. - REPORTED",
     "REPORTED", "R", "US"),
    ("CHAHAL JOINS INDIA'S RULING BJP",
     "Cricketer Yuzvendra Chahal joins the BJP. - REPORTED",
     "REPORTED", "R", "ASIA"),
    ("BJP MP RAMRAO WADKUTE DIES AT 72",
     "The Maharashtra MP dies aged 72. - REPORTED",
     "REPORTED", "R", "ASIA"),
    ("MARUTI SUZUKI RAISES PRICES FROM TODAY",
     "India's biggest carmaker lifts prices effective today. - REPORTED",
     "REPORTED", "R", "ASIA"),
    ("BONDI FIRST RESPONDERS MARRY NEAR SITE",
     "Two first responders wed near the attack site. - REPORTED",
     "REPORTED", "R", "OCEANIA"),
]

# Stories excluded on purpose: first reported BEFORE 22 November 2026.
DATECHECK = [
    ("TRUMP-XI-PUTIN SUMMIT", "19 NOV"),
    ("GTA VI $3.79BN DAY-ONE SALES", "ANNOUNCED 20 NOV"),
    ("EU-INDONESIA CEPA DEAL SIGNED", "SAT 21 NOV"),
    ("UN AUTONOMOUS WEAPONS AGREEMENT", "EARLY SAT 21 NOV"),
    ("BOLSONARO IN INTENSIVE CARE", "ADMITTED SAT 21 NOV"),
    ("MANIPUR LIQUOR TRAGEDY", "FIRST REPORTED 20 NOV"),
    ("US STOCKS CORRECTION", "FRI 20 NOV CLOSE"),
    ("USDA HACKED", "FIRST REPORTED 20 NOV"),
    ("FRANCE 6TH SATURDAY OF PROTESTS", "21 NOV"),
    ("LEEDS 4-1 CHELSEA; MAN CITY STUMBLE", "SAT 21 NOV"),
    ("KRYVYI RIH DOUBLE-TAP STRIKE", "21 NOV"),
    ("RUSSIAN CARGO SHIP DRONE STRIKE", "21 NOV"),
    ("NIGERIA BOAT CAPSIZED", "FRI 20 NOV"),
    ("VANCE ON IRAN STRIKES", "20 NOV"),
    ("IRAN STRIKES ON BAHRAIN", "FIRST REPORTED SAT 21 NOV"),
    ("EL CHAPO ISIDRO CAPTURE", "FRI 20 NOV"),
    ("TRUMP ON FBI NCIC BREACH", "SAT 21 NOV"),
    ("AMAZON-DECART $7.5BN TALKS", "FT, SAT 21 NOV"),
    ("IBM NIGHTHAWK R3, 520 QUBITS", "ANNOUNCED 11 NOV"),
    ("RIEMANN PROOF CLAIM", "POSTED 20 NOV / CHECKS 21 NOV"),
]

NUMBERS = [
    ("720/9", "INDIA v NZ"),
    ("352", "RUN LEAD, INDIA"),
    ("3 + 36", "DEAD + MISSING, FACTORY FIRE"),
    ("1,500", "SNOW-STRANDED, FUKUSHIMA"),
    ("15", "MILITANTS KILLED, MASTUNG"),
    ("$5.17M", "ATP FINALS PRIZE"),
]

TIMELINE = [
    ("EARLY", "COP31 THIRD DRAFT", "PUBLISHED, ANTALYA"),
    ("MIDDAY", "NEPAL PM LANDS IN INDIA", "INDIA DECLARE 720/9"),
    ("AFTERNOON", "HOUTHI STRIKES; SAUDI", "INTERCEPT; TANKER FIRE"),
    ("EVENING", "ATP FINAL, TURIN", "ZVEREV v ALCARAZ 18:00 CET"),
]

# Simplified continent outlines (lon, lat), drawn flat and original.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-60, 47), (-70, 42), (-75, 35),
     (-80, 32), (-85, 29), (-90, 21), (-97, 16), (-105, 20), (-115, 28),
     (-125, 40), (-125, 49), (-140, 60), (-155, 58), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 0), (-50, -5), (-40, -10), (-35, -15),
     (-40, -25), (-50, -30), (-60, -35), (-70, -40), (-70, -50),
     (-75, -55), (-70, -45), (-75, -35), (-80, -25), (-80, -15),
     (-80, -5)],
    [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
     (35, 28), (40, 15), (48, 11), (51, 10), (45, 0), (40, -10),
     (35, -20), (30, -30), (20, -35), (15, -30), (12, -18), (8, -5),
     (9, 4), (-8, 5), (-15, 10)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (32, 66),
     (40, 68), (45, 66), (40, 60), (35, 55), (30, 50), (28, 45),
     (23, 40), (19, 42), (12, 44), (8, 44), (3, 42), (0, 39),
     (-2, 37), (-6, 36)],
    [(32, 66), (40, 68), (55, 70), (70, 72), (90, 75), (110, 76),
     (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (162, 56),
     (158, 52), (150, 45), (142, 40), (135, 35), (130, 33), (127, 38),
     (122, 40), (120, 32), (115, 25), (110, 20), (108, 12), (105, 8),
     (100, 8), (97, 15), (92, 20), (88, 22), (80, 15), (77, 8),
     (73, 20), (66, 25), (60, 25), (55, 26), (52, 28), (48, 30),
     (44, 29), (40, 35), (36, 36), (32, 40), (30, 45)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20)],
]

# story number -> (lon, lat) for the map pins (thinned so none overlap)
PINS = [(2, 106, -6), (4, 174, -41), (6, -77, 39),
        (9, 51, 36), (15, 34, 31), (17, 13, 52),
        (22, 7, 9), (32, 141, 37), (44, 151, -34)]

MARKER_COLOR = {"C": GREEN, "O": BLUE, "R": GOLD}
MARKER_WORD = {"C": "CONFIRMED", "O": "OFFICIALS SAY", "R": "REPORTED"}


def draw():
    cv = Canvas(W, H, PAPER)

    # ---- header band
    cv.rect(0, 0, W, 100, NAVY)
    cv.text(16, 12, "THE WORLD IN ONE PICTURE", scale=3, color=LIGHT, bold=True)
    cv.text(16, 52, "SUNDAY 22 NOVEMBER 2026", scale=3, color=(255, 205, 90), bold=True)
    cv.text(16, 82, "44 STORIES, ALL FIRST REPORTED TODAY - EVERY STORY SOURCED",
            scale=1, color=LIGHT)

    # ---- legend
    y = 108
    x = 16
    for m in ("C", "O", "R"):
        cv.rect(x, y, 12, 12, MARKER_COLOR[m])
        x += 16
        x = cv.text(x, y + 2, MARKER_WORD[m], scale=1, color=INK, bold=True)
        x += 18
    cv.text(x, y + 2, "SOURCES: AP - REUTERS - ANI - ATP - LANCET - CVE - NBC - DRAGOS",
            scale=1, color=GREY)
    cv.hline(16, 126, W - 32, INK)

    # ---- stories: 2 columns x 22 rows
    col_x = (16, 520)
    col_w = 488
    row_h = 24
    y0 = 134
    for i, (head, detail, _src, marker, region) in enumerate(STORIES):
        col = i // 22
        row = i % 22
        x = col_x[col]
        y = y0 + row * row_h
        # number chip
        cv.rect(x, y, 18, 18, RED)
        num = str(i + 1)
        nx = x + (18 - cv.text_w(num, 1)) // 2
        cv.text(nx, y + 5, num, scale=1, color=LIGHT, bold=True)
        # headline (bold, scale 2) on its own line
        cv.text(x + 22, y, cv.fit(head, col_w - 22, 2), scale=2, color=INK, bold=True)
        # detail line: marker chip + region + detail, source tag never cut
        cv.rect(x + 22, y + 17, 9, 7, MARKER_COLOR[marker])
        prefix = region + " - "
        suffix = " - " + _src
        body = detail.rsplit(" - ", 1)[0]
        avail = col_w - 34 - cv.text_w(prefix, 1) - cv.text_w(suffix, 1)
        line = prefix + cv.fit(body, avail, 1) + suffix
        cv.text(x + 34, y + 16, line, scale=1, color=(60, 60, 56))

    # ---- map + numbers
    my = 668
    cv.hline(16, my - 6, W - 32, INK)
    cv.text(16, my, "WHERE IT HAPPENED", scale=2, color=NAVY, bold=True)
    cv.text(716, my, "THE DAY IN NUMBERS", scale=2, color=NAVY, bold=True)
    map_x, map_y, map_w, map_h = 16, my + 20, 684, 104

    def proj(lon, lat):
        px = map_x + int((lon + 180) / 360.0 * map_w)
        py = map_y + int((75 - lat) / 135.0 * map_h)
        return px, py

    cv.rect(map_x, map_y, map_w, map_h, SEA)
    for cont in CONTINENTS:
        cv.poly([proj(lon, lat) for lon, lat in cont], LAND)
    for n, lon, lat in PINS:
        px, py = proj(lon, lat)
        cv.disc(px, py, 8, RED)
        cv.ring(px, py, 8, LIGHT)
        num = str(n)
        cv.text(px - cv.text_w(num, 1) // 2, py - 3, num, scale=1, color=LIGHT, bold=True)
    # numbers column: value (scale 2) + label (scale 1) on one line each
    ny = my + 20
    for val, label in NUMBERS:
        vx = cv.text(716, ny, val, scale=2, color=RED, bold=True)
        cv.text(vx + 8, ny + 4, label, scale=1, color=INK)
        ny += 17

    # ---- timeline
    ty = 800
    cv.hline(16, ty - 6, W - 32, INK)
    cv.text(16, ty, "THE DAY IN UTC", scale=2, color=NAVY, bold=True)
    bx = 16
    for bucket, l1, l2 in TIMELINE:
        cv.rect(bx, ty + 22, 10, 10, BLUE)
        cv.text(bx + 14, ty + 22, bucket, scale=1, color=BLUE, bold=True)
        cv.text(bx, ty + 38, l1, scale=1, color=INK, bold=True)
        cv.text(bx, ty + 50, l2, scale=1, color=INK)
        bx += 252

    # ---- date check
    dy = 872
    cv.rect(0, dy, W, 128, (30, 30, 28))
    cv.text(16, dy + 10, "DATE CHECK - NOT TODAY: FIRST REPORTED BEFORE 22 NOVEMBER 2026",
            scale=2, color=(255, 205, 90), bold=True)
    cols = (16, 352, 688)
    for i, (item, when) in enumerate(DATECHECK):
        col = i // 7
        row = i % 7
        x = cols[col]
        y = dy + 34 + row * 13
        txt = "X " + item + " - " + when
        cv.text(x, y, cv.fit(txt, 320, 1), scale=1, color=(220, 220, 210))

    # ---- footer
    cv.text(16, 1006, "ALL 44 STORIES FIRST REPORTED SUN 22 NOV 2026 - DRAWN IN CODE - NO PHOTOS",
            scale=1, color=GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
