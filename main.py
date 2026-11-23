#!/usr/bin/env python3
"""Sunday 22 November 2026 in one picture.

A newspaper front page drawn entirely in code: 39 dated stories, a world
map with numbered pins, a UTC timeline, a numbers strip and a DATE CHECK
box. Pure Python 3.13 standard library, no network, no clock, no
randomness: two runs write byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---- palette -------------------------------------------------------------
PAPER = (247, 243, 234)   # newsprint cream
CARD = (255, 255, 255)    # card white
INK = (22, 22, 22)        # near-black ink
GREY = (110, 108, 100)    # secondary text
LINE = (180, 175, 162)    # hairlines
RED = (178, 34, 34)       # masthead red / date check
GREEN = (34, 120, 60)     # CONFIRMED badge
AMBER = (176, 110, 0)     # CLAIM badge
BLUE = (40, 80, 160)      # REPORTED badge
SKY = (168, 205, 225)     # map sea / sky
LAND = (196, 205, 168)    # map land
LAND2 = (178, 190, 150)
GOLD = (212, 160, 40)
DARKBLUE = (36, 58, 110)

# ---- framebuffer ---------------------------------------------------------
fb = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        fb[i] = c[0]
        fb[i + 1] = c[1]
        fb[i + 2] = c[2]


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        fb[i:i + len(row)] = row


def hline(x0, x1, y, c):
    if x1 < x0:
        x0, x1 = x1, x0
    rect(x0, y, x1 - x0 + 1, 1, c)


def vline(x, y0, y1, c):
    if y1 < y0:
        y0, y1 = y1, y0
    rect(x, y0, 1, y1 - y0 + 1, c)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            return
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c, fill=True):
    if fill:
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            hline(cx - dx, cx + dx, cy + dy, c)
    else:
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            px(cx - dx, cy + dy, c)
            px(cx + dx, cy + dy, c)


def ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        dx = int(rx * (1 - (dy * dy) / float(ry * ry)) ** 0.5)
        hline(cx - dx, cx + dx, cy + dy, c)


def poly(points, c):
    """Fill a simple polygon (list of (x, y))."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / float(y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            hline(int(xs[i]), int(xs[i + 1]), y, c)


def border(x, y, w, h, c, t=1):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


# ---- PNG encoder ---------------------------------------------------------
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += fb[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))

# ---- 5x7 bitmap font (written for this entry) ---------------------------
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {
"A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
"C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
"D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
"E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
"F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
"G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
"H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
"I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
"K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
"L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
"M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
"N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
"O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
"Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
"R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
"S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
"T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
"U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
"V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
"X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
"Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
"Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
"a": (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
"b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
"c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
"d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
"e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
"f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
"g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
"i": ("..#..", ".....", ".##..", "..#..", "..#..", "..#..", ".###."),
"j": ("...#.", ".....", "..##.", "...#.", "...#.", "...#.", ".##.."),
"k": ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
"l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
"m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
"n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
"o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
"p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
"q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
"r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
"s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
"t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
"u": (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
"v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
"w": (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
"x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
"y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
"z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
"0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
"1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
"2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
"3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
"4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
"5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
"6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
"7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
"8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
"9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
" ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
",": (".....", ".....", ".....", ".....", ".....", ".##..", ".#..."),
":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
"!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
"?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
"'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
'"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
"-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
"(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
"/": ("....#", "....#", "...#.", "...#.", "..#..", ".#...", "#...."),
"%": ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
"+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
"=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
"&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
"*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
"$": ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
"[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
"]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
"_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
">": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
"<": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
}

# middle dot and dash normalisation (drawn with glyphs above)
NORM = {"\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
        "\u201c": '"', "\u201d": '"', "\u00b7": "\u00b7"}
FONT["\u00b7"] = (".....", ".....", ".....", ".....", ".##..", ".##..", ".....")
FONT["\u00d7"] = (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", ".....")


def text_w(s, scale=1):
    return sum((6 if ch in FONT else 6) for ch in s) * scale - scale


def draw_text(x, y, s, scale=1, color=INK):
    cx = x
    for ch in s:
        ch = NORM.get(ch, ch)
        g = FONT.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    rect(cx + c * scale, y + r * scale, scale, scale, color)
        cx += 6 * scale
    return cx


def text_centre(x0, x1, y, s, scale=1, color=INK):
    w = text_w(s, scale)
    draw_text(x0 + (x1 - x0 - w) // 2, y, s, scale, color)


def wrap(s, max_w, scale=1):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    unit = 6 * scale
    max_chars = max(1, (max_w + scale) // unit)
    lines = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = wd
                while len(cur) > max_chars:
                    lines.append(cur[:max_chars])
                    cur = cur[max_chars:]
        if cur:
            lines.append(cur)
    return lines

# ---- flat illustrated icons (original drawings, 52x52 box) ---------------
def draw_icon(kind, x, y):
    cx, cy = x + 26, y + 26
    if kind == "cop":  # globe with a crack
        circle(cx, cy, 20, SKY)
        circle(cx, cy, 20, INK, fill=False)
        poly([(cx - 14, cy - 8), (cx - 2, cy - 14), (cx + 6, cy - 6),
              (cx - 2, cy + 2), (cx - 12, cy + 4)], LAND)
        poly([(cx + 4, cy + 8), (cx + 14, cy + 4), (cx + 16, cy + 14),
              (cx + 6, cy + 16)], LAND)
        line(cx - 16, cy - 18, cx + 4, cy + 2, RED)
        line(cx + 4, cy + 2, cx - 6, cy + 18, RED)
        line(cx - 20, cy, cx + 20, cy, (255, 255, 255))
    elif kind == "drone":  # three drones over a block
        for dx, dy in ((-14, -10), (6, -16), (12, 2)):
            rect(cx + dx - 5, cy + dy - 2, 10, 4, INK)
            hline(cx + dx - 9, cx + dx + 9, cy + dy - 5, GREY)
            hline(cx + dx - 9, cx + dx + 9, cy + dy + 4, GREY)
        rect(cx - 16, cy + 8, 32, 12, (120, 110, 100))
        for i in range(3):
            vline(cx - 10 + i * 10, cy + 8, cy + 20, INK)
        poly([(cx + 2, cy + 8), (cx + 8, cy + 2), (cx + 12, cy + 8)], (230, 120, 30))
    elif kind == "ship":  # corvette capsizing
        poly([(cx - 22, cy - 2), (cx + 20, cy - 14), (cx + 22, cy - 8),
              (cx + 2, cy + 6), (cx - 20, cy + 6)], (90, 90, 95))
        rect(cx - 2, cy - 20, 3, 10, INK)
        circle(cx + 8, cy - 18, 5, GREY)
        circle(cx + 14, cy - 24, 4, GREY)
        for wy in (cy + 12, cy + 17):
            for wx in range(cx - 24, cx + 24, 12):
                line(wx, wy, wx + 6, wy - 3, SKY)
                line(wx + 6, wy - 3, wx + 12, wy, SKY)
    elif kind == "ballot":  # ballot box
        rect(cx - 16, cy - 4, 32, 20, (70, 90, 140))
        rect(cx - 16, cy - 4, 32, 4, DARKBLUE)
        rect(cx - 4, cy - 14, 8, 10, CARD)
        line(cx - 12, cy + 8, cx - 4, cy + 14, CARD)
        line(cx - 4, cy + 14, cx + 12, cy - 2, CARD)
    elif kind == "capitol":  # house dome
        circle(cx, cy - 2, 12, DARKBLUE)
        rect(cx - 12, cy - 2, 24, 4, DARKBLUE)
        rect(cx - 16, cy + 2, 32, 16, (70, 90, 140))
        for i in range(4):
            vline(cx - 12 + i * 8, cy + 2, cy + 18, CARD)
        rect(cx - 18, cy + 18, 36, 3, INK)
    elif kind == "radar":  # radar dish, denied
        line(cx - 14, cy + 16, cx, cy + 2, INK)
        line(cx, cy + 2, cx + 14, cy + 16, INK)
        ellipse(cx, cy - 2, 16, 7, (120, 140, 170))
        line(cx - 16, cy - 6, cx + 16, cy - 6, INK)
        line(cx - 8, cy - 14, cx + 8, cy + 6, RED)
        line(cx + 8, cy - 14, cx - 8, cy + 6, RED)
    elif kind == "cricket":  # bat, ball, stumps
        line(cx - 12, cy + 16, cx + 8, cy - 14, (160, 120, 60))
        rect(cx + 4, cy - 18, 8, 12, (190, 150, 80))
        for i in range(3):
            vline(cx - 16 + i * 5, cy + 4, cy + 16, GOLD)
        circle(cx + 12, cy + 10, 5, RED)
    elif kind == "f1":  # race car
        poly([(cx - 20, cy + 6), (cx - 14, cy - 4), (cx + 2, cy - 6),
              (cx + 10, cy - 2), (cx + 20, cy + 2), (cx + 18, cy + 8),
              (cx - 18, cy + 8)], RED)
        circle(cx - 11, cy + 9, 5, INK)
        circle(cx + 11, cy + 9, 5, INK)
        circle(cx - 11, cy + 9, 2, GREY)
        circle(cx + 11, cy + 9, 2, GREY)
        for i in range(3):
            hline(cx - 24, cx - 18, cy - 8 + i * 4, GREY)
    elif kind == "tennis":  # racket and ball
        circle(cx - 4, cy - 6, 12, INK, fill=False)
        circle(cx - 4, cy - 6, 9, (200, 210, 220))
        line(cx - 4, cy + 6, cx + 4, cy + 18, (160, 120, 60))
        circle(cx + 12, cy + 10, 6, (210, 220, 60))
        line(cx - 12, cy - 6, cx + 4, cy - 6, INK)
        line(cx - 4, cy - 14, cx - 4, cy + 2, INK)
    elif kind == "quit":  # door with arrow out
        rect(cx - 14, cy - 16, 22, 34, (120, 100, 80))
        rect(cx - 10, cy - 12, 14, 26, PAPER)
        line(cx + 2, cy + 2, cx + 18, cy + 2, RED)
        poly([(cx + 18, cy + 2), (cx + 12, cy - 4), (cx + 12, cy + 8)], RED)
        rect(cx + 8, cy + 10, 10, 7, INK)
    elif kind == "plane":  # grounded plane
        poly([(cx - 22, cy), (cx - 6, cy - 6), (cx + 14, cy - 4),
              (cx + 22, cy), (cx + 14, cy + 3), (cx - 14, cy + 4)], (90, 110, 150))
        poly([(cx - 2, cy - 6), (cx + 2, cy - 14), (cx + 6, cy - 6)], (90, 110, 150))
        line(cx - 20, cy + 12, cx + 20, cy + 12, INK)
        line(cx - 16, cy + 12, cx - 20, cy + 16, RED)
        line(cx - 20, cy + 16, cx - 12, cy + 12, RED)
    elif kind == "pope":  # lunch table
        rect(cx - 20, cy - 2, 40, 4, (150, 110, 70))
        vline(cx - 16, cy + 2, cy + 16, INK)
        vline(cx + 16, cy + 2, cy + 16, INK)
        circle(cx - 10, cy - 6, 4, CARD)
        circle(cx + 10, cy - 6, 4, CARD)
        circle(cx, cy - 6, 4, CARD)
        line(cx, cy - 18, cx, cy - 8, GOLD)
        line(cx - 4, cy - 14, cx + 4, cy - 14, GOLD)
    elif kind == "factory":  # burning factory
        poly([(cx - 20, cy + 16), (cx - 20, cy - 2), (cx - 12, cy - 8),
              (cx - 4, cy - 2), (cx + 4, cy - 8), (cx + 12, cy - 2),
              (cx + 20, cy - 2), (cx + 20, cy + 16)], (130, 120, 110))
        rect(cx + 12, cy - 18, 5, 16, INK)
        poly([(cx - 6, cy - 6), (cx - 2, cy - 16), (cx + 2, cy - 8),
              (cx + 6, cy - 16), (cx + 8, cy - 6)], (235, 130, 30))
        poly([(cx - 2, cy - 6), (cx + 1, cy - 12), (cx + 4, cy - 6)], RED)
    elif kind == "aid":  # aid box
        rect(cx - 16, cy - 8, 32, 20, (190, 170, 120))
        rect(cx - 16, cy - 8, 32, 5, (160, 140, 95))
        rect(cx - 2, cy - 4, 4, 12, RED)
        rect(cx - 6, cy, 12, 4, RED)
        line(cx - 20, cy + 16, cx + 20, cy + 16, GREY)
    elif kind == "khartoum":  # buildings under drones
        rect(cx - 20, cy - 2, 12, 18, (140, 130, 115))
        rect(cx - 4, cy - 10, 12, 26, (160, 150, 135))
        rect(cx + 12, cy + 2, 10, 14, (140, 130, 115))
        rect(cx - 14, cy - 16, 10, 3, INK)
        hline(cx - 16, cx - 6, cy - 19, GREY)
        poly([(cx + 2, cy - 2), (cx + 8, cy - 8), (cx + 14, cy - 2)], (235, 130, 30))


# ---- story data (all first reported Sunday 22 November 2026) ------------
# (number, icon, place, beat, headline, deck, source, badge, lon, lat)
BADGE_COL = {"CONFIRMED": GREEN, "CLAIM": AMBER, "REPORTED": BLUE}
LEADS = [
(1, "cop", "ANTALYA, TURKIYE", "CLIMATE",
 "COP31 COLLAPSES WITH NO DEAL",
 "In overtime, the EU, UK and island states reject a text that never names fossil fuels. President Kurum: no agreement.",
 "Reuters", "CONFIRMED", 30.7, 36.9),
(2, "drone", "KYIV REGION, UKRAINE", "WAR",
 "RUSSIA FIRES 186 DRONES",
 "Defences down or jam 161 of 186 drones, 72 jet-powered. In Dymer a block falls: 3 dead, 14 unaccounted, 9 evacuated.",
 "Ukrainian Air Force", "CONFIRMED", 30.5, 50.5),
(3, "ship", "BENGHAZI, LIBYA", "WAR",
 "SEA DRONES SINK RUSSIAN WARSHIP",
 "The corvette Merkury burns and capsizes at Benghazi; only the bow above water. Libya blames Ukrainian sea drones; 10 hurt.",
 "AP - Reuters", "CONFIRMED", 20.1, 32.1),
(4, "ballot", "HONG KONG", "ELECTION",
 "HONG KONG ELECTS ITS COMMITTEE",
 "Record 98.79% turnout as 856 candidates contest 723 Election Committee seats.",
 "HK Govt", "CONFIRMED", 114.2, 22.3),
(5, "capitol", "NORTH CAROLINA, USA", "POLITICS",
 "DEMOCRATS WIN 258TH HOUSE SEAT",
 "Hubbard beats Foxx by 330 votes after a recount; the biggest majority since 1992.",
 "AP", "CONFIRMED", -79.8, 35.8),
(6, "radar", "MANAMA, BAHRAIN", "GULF",
 "IRAN CLAIMS TWO US RADARS HIT",
 "Bahrain says a civilian site burned and two people were hurt; a US official reports no US damage.",
 "AFP", "CLAIM", 50.6, 26.2),
(7, "cricket", "WELLINGTON, NZ", "CRICKET",
 "INDIA DECLARE ON RECORD 720/9",
 "Rahul 136 and Gill 98 pile up India's biggest Test total in New Zealand.",
 "ESPN", "CONFIRMED", 174.8, -41.3),
(8, "f1", "LAS VEGAS, USA", "FORMULA 1",
 "VERSTAPPEN TAKES LAS VEGAS GP",
 "Thirty-five lead changes; Verstappen beats Norris by 0.639s for a third Vegas win.",
 "F1", "CONFIRMED", -115.1, 36.2),
(9, "tennis", "TURIN, ITALY", "TENNIS",
 "ALCARAZ WINS THE ATP FINALS",
 "Beats world No. 1 Zverev 6-2, 7-6(7) for a first Finals title and $5.17m.",
 "ATP", "CONFIRMED", 7.7, 45.1),
(10, "quit", "SEOUL, SOUTH KOREA", "POLITICS",
 "KOREA'S EDUCATION MINISTER QUITS",
 "Choi Kyo-jin resigns over last-minute anti-AI-cheating chaos at the college exam.",
 "Reuters", "CONFIRMED", 127.0, 37.5),
(11, "plane", "ATLANTA, USA", "TRAVEL",
 "DELTA OUTAGE SNARLS US FLIGHTS",
 "A weight-and-balance failure delays 1,600+ flights and cancels 200+ at the Thanksgiving rush.",
 "CNN", "CONFIRMED", -84.4, 33.7),
(12, "pope", "VATICAN CITY", "FAITH",
 "POPE LEO HOSTS 1,300 POOR GUESTS",
 "Lunch in the Paul VI Hall marks the 10th World Day of the Poor.",
 "Vatican News", "CONFIRMED", 12.5, 41.9),
(13, "factory", "CIKANDE, INDONESIA", "DISASTER",
 "CANDY-FACTORY FIRE: 3 DEAD",
 "Rescuers search the ruins of the Milkita plant; 24 body bags recovered, DNA checks to follow.",
 "AP", "CONFIRMED", 106.2, -6.2),
(14, "aid", "GAZA CITY", "CONFLICT",
 "FOUR AID-SEEKERS SHOT DEAD",
 "Israeli fire near a food site south of Gaza City, a hospital and witnesses say.",
 "AP", "REPORTED", 34.5, 31.5),
(15, "khartoum", "KHARTOUM, SUDAN", "WAR",
 "DRONES STRIKE HOMES NEAR KHARTOUM",
 "RSF-blamed strikes kill four, wound nine and damage a UN building.",
 "Al Jazeera", "REPORTED", 32.5, 15.5),
]

ALSO = [
(16, "ASIA", "Nepal PM Shah begins a two-day visit to India", "ANI"),
(17, "MIDEAST", "Houthi strikes follow a Saudi-led operation in Hodeida", "Reuters"),
(18, "MIDEAST", "Saudi air defences shoot down a Houthi missile", "AP"),
(19, "MIDEAST", "US rejects Iran's claim it hit an F-16", "AP"),
(20, "MIDEAST", "Lebanon's Aoun demands Israel leave the south", "Reuters"),
(21, "EUROPE", "Germany: bid to arrest an Israeli soldier on a visit", "AP"),
(22, "EUROPE", "German politician attacked at a Berlin protest", "AP"),
(23, "ASIA", "India and China hold fresh frontier talks", "ANI"),
(24, "ASIA", "China renews its UN bid to blacklist the BLA", "Reuters"),
(25, "ASIA", "Pakistan: 15 militants killed in Mastung", "AP"),
(26, "AFRICA", "Nigeria 2027: young voter sign-ups fall", "AP"),
(27, "EUROPE", "EU proposes a tax on digital services", "Reuters"),
(28, "WORLD", "UK-India deal snags on a 162.5% Scotch duty", "Reuters"),
(29, "AMERICAS", "Congress races to avert a shutdown", "Reuters"),
(30, "WORLD", "Antidepressants: a 115-trial study is out", "Lancet"),
(31, "ASIA", "Fukushima: 1,500 trapped by heavy snow", "AP"),
(32, "EUROPE", "Liverpool 4-0 Man United; Pochettino routed on debut", "Reuters"),
(33, "AMERICAS", "Wembanyama scores 50 as the Spurs roll, 114-91", "AP"),
(34, "WORLD", "Falcon 9 launches NROL-136; a 32-hour pad record", "Spaceflight Now"),
(35, "EUROPE", "Sparta II: Russia starts towing the burnt ship home", "Reuters"),
(36, "AMERICAS", "Bolsonaro stable in intensive care, hospital says", "Reuters"),
(37, "OCEANIA", "Cyclone Xavier fades to Category 1 off the Cook Islands", "MetService"),
(38, "MIDEAST", "Trump seeks a 'permanent' deal with Iran", "Reuters"),
(39, "OCEANIA", "Bondi first responders marry near the attack site", "Reports"),
]

NUMBERS = [
("186", "drones fired at Ukraine overnight"),
("161", "drones downed or jammed"),
("258", "House seats for Democrats"),
("98.79%", "Hong Kong turnout - a record"),
("720/9", "India's record Test total"),
("1,300", "poor guests at the Pope's lunch"),
]

TIMELINE = [
("00:00", "Drones strike Khartoum"),
("01:00", "Hong Kong polls open"),
("06:00", "161 of 186 drones downed"),
("12:23", "Falcon 9 lifts off"),
("16:30", "Liverpool v Man Utd"),
("18:00", "Democrats reach 258"),
]

DATECHECK = [
("400-drone night", "Thu 19-Fri 20 Nov"),
("Kryvyi Rih double-tap", "Sat 21 Nov"),
("Gaza food-aid van strike", "Sat 21 Nov"),
("Sparta II drone strike itself", "Sat 21 Nov"),
("Bahrain strikes themselves", "Sat 21 Nov"),
("Bayelsa boat capsizing", "Fri 20 Nov"),
("Peru M6.7 quake", "Fri 20 Nov"),
("Manipur liquor tragedy", "first reported Fri 20 Nov"),
("FBI NCIC hack probe", "first reported Fri 20 Nov"),
("'El Chapo Isidro' captured", "Fri 20 Nov"),
("BepiColombo's Mercury orbit", "Sat 21 Nov"),
("Copa Sudamericana final", "Sat 21 Nov"),
]

# rough continent outlines (lon, lat) for the schematic map
CONTINENTS = [
[(-168, 66), (-140, 70), (-120, 72), (-95, 80), (-80, 73), (-60, 60),
 (-55, 47), (-70, 42), (-75, 35), (-80, 25), (-85, 20), (-90, 15),
 (-95, 18), (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60),
 (-160, 58), (-168, 66)],
[(-80, 10), (-60, 8), (-50, 0), (-40, -5), (-35, -8), (-40, -20),
 (-48, -28), (-58, -35), (-65, -41), (-70, -52), (-73, -50), (-73, -37),
 (-70, -18), (-77, -12), (-80, -3), (-80, 10)],
[(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28),
 (43, 12), (51, 11), (48, 0), (40, -10), (35, -25), (28, -33), (20, -35),
 (15, -27), (12, -18), (9, 4), (-8, 5), (-17, 15)],
[(-10, 36), (0, 44), (-5, 48), (0, 51), (5, 58), (10, 62), (18, 56),
 (21, 55), (28, 60), (30, 70), (40, 68), (60, 69), (80, 73), (100, 77),
 (120, 73), (140, 72), (160, 70), (178, 66), (170, 60), (162, 56),
 (158, 50), (142, 45), (135, 43), (130, 35), (127, 40), (122, 32),
 (120, 25), (110, 20), (105, 10), (100, 8), (95, 15), (90, 22), (80, 15),
 (75, 8), (72, 20), (65, 25), (60, 25), (55, 26), (50, 29), (48, 30),
 (43, 29), (40, 36), (35, 36), (30, 36), (26, 38), (22, 37), (18, 40),
 (12, 44), (8, 44), (3, 43), (0, 40), (-2, 37), (-9, 37), (-10, 36)],
[(113, -22), (114, -30), (115, -35), (124, -33), (130, -32), (137, -35),
 (140, -38), (147, -39), (150, -37), (153, -27), (146, -19), (142, -11),
 (136, -12), (132, -12), (126, -14), (122, -17), (114, -22)],
[(130, 31), (132, 33), (135, 34), (138, 35), (140, 38), (141, 41),
 (143, 42), (145, 44), (142, 44), (140, 40), (138, 36), (135, 33), (130, 31)],
[(167, -45), (170, -42), (174, -41), (176, -38), (178, -37), (175, -40),
 (172, -43), (167, -45)],
]

# ---- layout ----------------------------------------------------------------
def masthead():
    rect(0, 4, W, 3, RED)
    text_centre(0, W, 12, "THE WORLD IN ONE PAGE", 2, INK)
    text_centre(0, W, 30, "SUNDAY 22 NOVEMBER 2026", 6, RED)
    text_centre(0, W, 78,
                "39 stories from Sunday 22 November 2026 - every one first "
                "reported that day. Sources on every story.", 1, GREY)
    rect(0, 90, W, 2, INK)


def numbers_strip():
    y = 96
    text_centre(0, W, y, "THE DAY IN NUMBERS", 1, RED)
    col_w = 165
    for i, (num, label) in enumerate(NUMBERS):
        cx0 = 16 + i * col_w
        cx1 = cx0 + col_w
        text_centre(cx0, cx1, y + 12, num, 3, INK)
        lines = wrap(label, col_w - 8, 1)
        for j, ln in enumerate(lines[:2]):
            text_centre(cx0, cx1, y + 36 + j * 9, ln, 1, GREY)


def region_bar():
    rect(16, 150, 992, 18, INK)
    text_centre(16, 1008, 155,
                "EUROPE \u00b7 MIDDLE EAST \u00b7 ASIA \u00b7 AFRICA \u00b7 "
                "AMERICAS \u00b7 OCEANIA \u00b7 SPORT \u00b7 WORLD", 1, CARD)


def lead_card(x, y, story):
    (n, icon, place, beat, head, deck, src, badge, lon, lat) = story
    rect(x, y, 325, 96, CARD)
    border(x, y, 325, 96, LINE)
    rect(x, y, 325, 2, RED)
    # number badge + region tag
    rect(x + 6, y + 6, 16, 16, RED)
    num = str(n)
    draw_text(x + 6 + (16 - text_w(num, 1)) // 2, y + 10, num, 1, CARD)
    draw_text(x + 28, y + 10, place + " \u00b7 " + beat, 1, GREY)
    # illustration
    draw_icon(icon, x + 6, y + 26)
    # headline (up to 2 lines, scale 2)
    tx = x + 64
    tw = 325 - 64 - 8
    lines = wrap(head, tw, 2)
    for j, ln in enumerate(lines[:2]):
        draw_text(tx, y + 26 + j * 16, ln, 2, INK)
    # deck (up to 3 lines, scale 1)
    dlines = wrap(deck, tw, 1)
    for j, ln in enumerate(dlines[:3]):
        draw_text(tx, y + 58 + j * 9, ln, 1, INK)
    # source + badge
    sy = y + 86
    draw_text(tx, sy, src, 1, GREY)
    bx = tx + text_w(src, 1) + 6
    bw = text_w(badge, 1) + 6
    rect(bx, sy - 1, bw, 9, BADGE_COL[badge])
    draw_text(bx + 3, sy, badge, 1, CARD)


def also_list():
    y = 676
    draw_text(16, y, "ALSO ON SUNDAY 22 NOVEMBER", 2, INK)
    draw_text(760, y + 3, "24 MORE STORIES", 1, RED)
    hline(16, 1008, y + 18, INK)
    col_x = [16, 524]
    for k, (n, region, txt, src) in enumerate(ALSO):
        col = k // 12
        row = k % 12
        s = "%d. %s - %s (%s)" % (n, region, txt, src)
        draw_text(col_x[col], y + 26 + row * 10, s, 1, INK)


def world_map(x0, y0, w, h):
    # sea
    rect(x0, y0, w, h, (232, 238, 240))
    # graticule
    for lon in range(-180, 181, 60):
        gx = x0 + int((lon + 180) / 360.0 * w)
        vline(gx, y0, y0 + h - 1, (205, 212, 218))
    for lat in range(-60, 91, 30):
        gy = y0 + int((85 - lat) / 145.0 * h)
        hline(x0, x0 + w - 1, gy, (205, 212, 218))
    # continents
    for cont in CONTINENTS:
        pts = [(x0 + int((lon + 180) / 360.0 * w),
                y0 + int((85 - lat) / 145.0 * h)) for lon, lat in cont]
        poly(pts, LAND)
    border(x0, y0, w, h, LINE)
    # pins with label offsets for the crowded Middle East cluster
    off = {1: (-18, -12), 2: (8, -12), 3: (-24, -2), 5: (10, -10),
           6: (16, 10), 7: (-16, -4), 8: (-14, -12), 9: (-16, -10),
           11: (-22, 6), 12: (8, -4), 14: (12, 8), 15: (-20, 6)}
    for (n, icon, place, beat, head, deck, src, badge, lon, lat) in LEADS:
        px0 = x0 + int((lon + 180) / 360.0 * w)
        py0 = y0 + int((85 - lat) / 145.0 * h)
        circle(px0, py0, 5, RED)
        circle(px0, py0, 5, INK, fill=False)
        dx, dy = off.get(n, (8, -4))
        lx, ly = px0 + dx, py0 + dy
        label = str(n)
        rect(lx - 1, ly - 1, text_w(label, 1) + 2, 9, CARD)
        draw_text(lx, ly, label, 1, RED)


def bottom_panels():
    y0 = 826
    # map
    draw_text(16, y0 + 4, "WHERE IT HAPPENED", 2, INK)
    world_map(16, y0 + 22, 368, 140)
    # timeline
    draw_text(392, y0 + 4, "THE DAY IN UTC", 2, INK)
    hline(392, 648, y0 + 20, INK)
    for i, (t, txt) in enumerate(TIMELINE):
        ry = y0 + 28 + i * 23
        draw_text(392, ry, t, 2, RED)
        draw_text(458, ry + 3, txt, 1, INK)
    # date check
    x0, w = 656, 352
    border(x0, y0, w, 162, RED, 2)
    draw_text(x0 + 10, y0 + 6, "DATE CHECK", 2, RED)
    draw_text(x0 + 10, y0 + 24, "NOT 22 NOVEMBER - LEFT OUT ON PURPOSE", 1, RED)
    hline(x0 + 10, x0 + w - 10, y0 + 36, RED)
    for i, (name, date) in enumerate(DATECHECK):
        iy = y0 + 40 + i * 9
        draw_text(x0 + 10, iy, "- " + name, 1, INK)
        dw = text_w(date, 1)
        draw_text(x0 + w - 10 - dw, iy, date, 1, RED)
    draw_text(x0 + 10, y0 + 150,
              "Trump-Xi-Putin summit 19 Nov; Bahrain strikes 21 Nov.", 1, GREY)


def footer():
    draw_text(16, 994,
              "Sources: Reuters, AP, AFP, Ukrinform, Ukrainian Air Force, "
              "HK Govt, ATP, F1, ESPN, CNN, Vatican News, Al Jazeera, ANI, "
              "Spaceflight Now, MetService, Lancet.", 1, GREY)
    draw_text(16, 1004,
              "All pictures and the map are original, drawn in code. "
              "39 stories, all first reported Sunday 22 November 2026.",
              1, GREY)


def build():
    rect(0, 0, W, H, PAPER)
    masthead()
    numbers_strip()
    region_bar()
    for i, story in enumerate(LEADS):
        col = i % 3
        row = i // 3
        lead_card(16 + col * 333, 174 + row * 100, story)
    also_list()
    bottom_panels()
    footer()
    return png_bytes()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    data = build()
    with open(os.path.join(out_dir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
