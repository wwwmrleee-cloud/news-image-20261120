#!/usr/bin/env python3
"""news-image-20261120: draw one 1024x1024 PNG summing up the world news of
Friday 20 November 2026. Pure Python standard library only (math, os,
struct, zlib): no fonts, no images, no network, no time, no randomness, so
two runs write byte-identical files. Run: python3 main.py (writes
$MAKEFUN_OUTPUT_DIR/entry.png, default /output/entry.png).

The day, as reported on 20 November 2026: Trump pushes the Iran war
decision to 2027, saying he will see what happens after Jan 1; Trump, Xi
and Putin issue a four-point statement after their Shenzhen summit;
Anthropic debuts on Nasdaq, priced $83, soaring to $111.50; Bitcoin nears
$60,000 as ETF outflows pass $2.5bn in 2026; Cyclone Akvan nears landfall
in India with 80,000 evacuated; Voyager 1 nears one light-day out.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

# --- 5x7 pixel font, typed by hand. Each glyph is 7 rows of 5 bits. ---
FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "00010"),
    "*": ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
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
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "00000", "01100", "01100", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
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
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "11110", "10001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "11110", "10001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "11110", "10001", "11110", "10000", "10000"),
    "q": ("00000", "00000", "01111", "10001", "01111", "00001", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
}

PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (18, 38, 66)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
GOLD = (176, 124, 22)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
SKY = (178, 214, 235)
SEA = (28, 68, 110)
GREEN = (34, 120, 60)
AMBER = (200, 110, 20)


class Canvas:
    def __init__(self):
        self.pix = bytearray(PAPER * W * H)

    def px(self, x, y, c):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.pix[i], self.pix[i + 1], self.pix[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(W, x + w), min(H, y + h)
        for yy in range(y0, y1):
            i = (yy * W + x0) * 3
            for xx in range(x0, x1):
                self.pix[i], self.pix[i + 1], self.pix[i + 2] = c
                i += 3

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int(math.sqrt(max(0, r * r - (yy - cy) ** 2)))
            for xx in range(cx - dx, cx + dx + 1):
                self.px(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, w=1):
        dx, dy = x1 - x0, y1 - y0
        steps = max(abs(dx), abs(dy), 1)
        r = w // 2
        for s in range(steps + 1):
            x = x0 + dx * s // steps
            y = y0 + dy * s // steps
            if w <= 1:
                self.px(x, y, c)
            else:
                self.disc(x, y, r, c)

    def poly(self, pts, c):
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(math.ceil(xs[k])), int(xs[k + 1]) + 1):
                    self.px(x, y, c)

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def text(self, x, y, s, scale, c):
        for ch in s:
            g = FONT.get(ch, FONT["?"])
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(x + col * scale, y + row * scale,
                                  scale, scale, c)
            x += 6 * scale
        return x

    def wrap(self, s, scale, maxw):
        words = s.split(" ")
        lines, cur = [], ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if self.text_width(trial, scale) <= maxw or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, maxw, c, leading=None):
        lh = leading if leading is not None else 9 * scale
        for ln in self.wrap(s, scale, maxw):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


def png_bytes(cv):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(cv.pix[y * W * 3:(y + 1) * W * 3])
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", comp) + chunk(b"IEND", b"")


# --- small flat icons, drawn in white inside a coloured band ---
def icon_chip(cv, cx, cy):
    cv.rect(cx - 13, cy - 13, 26, 26, LIGHT)
    cv.rect(cx - 6, cy - 6, 12, 12, NAVY)
    for dx in (-8, 0, 8):
        cv.line(cx + dx, cy - 20, cx + dx, cy - 13, LIGHT, 2)
        cv.line(cx + dx, cy + 13, cx + dx, cy + 20, LIGHT, 2)
    for dy in (-8, 0, 8):
        cv.line(cx - 20, cy + dy, cx - 13, cy + dy, LIGHT, 2)
        cv.line(cx + 13, cy + dy, cx + 20, cy + dy, LIGHT, 2)


def icon_scales(cv, cx, cy):
    cv.line(cx, cy - 16, cx, cy + 14, LIGHT, 3)
    cv.line(cx - 20, cy - 14, cx + 20, cy - 14, LIGHT, 3)
    cv.line(cx - 20, cy - 14, cx - 24, cy + 2, LIGHT, 2)
    cv.line(cx - 20, cy - 14, cx - 16, cy + 2, LIGHT, 2)
    cv.line(cx + 20, cy - 14, cx + 16, cy + 2, LIGHT, 2)
    cv.line(cx + 20, cy - 14, cx + 24, cy + 2, LIGHT, 2)
    cv.disc(cx - 20, cy + 6, 5, LIGHT)
    cv.disc(cx + 20, cy + 6, 5, LIGHT)
    cv.rect(cx - 12, cy + 12, 24, 3, LIGHT)


def icon_coin(cv, cx, cy, band):
    cv.disc(cx, cy, 15, LIGHT)
    cv.disc(cx, cy, 11, band)
    cv.text(cx - 6, cy - 7, "B", 2, LIGHT)


def icon_flags(cv, cx, cy):
    # three small flags on poles: the Shenzhen three-way summit
    for i, fc in enumerate(((179, 38, 30), (240, 196, 90), (29, 78, 137))):
        fx = cx - 20 + i * 16
        cv.line(fx, cy - 16, fx, cy + 14, LIGHT, 2)
        cv.rect(fx, cy - 16, 12, 9, fc)


def icon_storm(cv, cx, cy):
    # a cloud with rain: Cyclone Akvan
    cv.disc(cx - 10, cy - 4, 10, LIGHT)
    cv.disc(cx + 4, cy - 8, 12, LIGHT)
    cv.disc(cx + 12, cy + 2, 8, LIGHT)
    cv.rect(cx - 20, cy - 2, 40, 8, LIGHT)
    for dx in (-14, -4, 6, 16):
        cv.line(cx + dx, cy + 10, cx + dx - 3, cy + 20, LIGHT, 2)


def icon_satellite(cv, cx, cy):
    # Voyager 1: body, two panels, dish
    cv.rect(cx - 18, cy - 4, 12, 8, LIGHT)
    cv.rect(cx + 6, cy - 4, 12, 8, LIGHT)
    cv.rect(cx - 5, cy - 6, 10, 12, LIGHT)
    cv.line(cx, cy - 6, cx + 8, cy - 16, LIGHT, 2)
    cv.disc(cx + 9, cy - 17, 3, LIGHT)
    cv.line(cx - 5, cy + 8, cx - 12, cy + 16, LIGHT, 2)


ICONS = {"chip": icon_chip, "scales": icon_scales,
         "flags": icon_flags, "storm": icon_storm,
         "satellite": icon_satellite}


def draw_lead_scene(cv, x, y, w, h):
    # A 2027 calendar page: the Iran decision is pushed to next year.
    cv.rect(x, y, w, h, SKY)
    # calendar sheet
    cv.rect(x + 30, y + 16, 280, 168, LIGHT)
    cv.rect(x + 30, y + 16, 280, 40, RED)
    cv.text(x + 124, y + 22, "2027", 4, LIGHT)
    cv.text(x + 129, y + 66, "JANUARY", 2, INK)
    gx, gy, cw, ch = x + 44, y + 92, 32, 18
    for r in range(4):
        for c in range(7):
            cx0, cy0 = gx + c * cw, gy + r * ch
            if r == 0 and c == 0:
                cv.rect(cx0, cy0, cw - 2, ch - 2, RED)
                cv.text(cx0 + 11, cy0 + 2, "1", 2, LIGHT)
            else:
                cv.rect(cx0, cy0, cw - 2, ch - 2, (232, 220, 190))
    # red banner under the calendar
    cv.rect(x + 30, y + 196, 280, 48, RED)
    cv.text(x + 72, y + 210, "AFTER JAN 1", 3, LIGHT)
    cv.text(x + 57, y + 252, "NO RUSH, SAYS TRUMP", 2, INK)


def draw_cell(cv, x, y, w, h, story):
    cv.rect(x, y, w, h, LIGHT)
    cv.rect(x, y, w, 34, story["band"])
    cv.text(x + 12, y + 10, story["kicker"], 2, LIGHT)
    fn = ICONS.get(story["icon"])
    if fn:
        fn(cv, x + w - 32, y + 17)
    elif story["icon"] == "coin":
        icon_coin(cv, x + w - 32, y + 17, story["band"])
    cv.rect(x, y, w, 3, RED)
    yy = y + 46
    for ln in cv.wrap(story["headline"], 4, w - 24):
        cv.text(x + 12, yy, ln, 4, INK)
        yy += 34
    yy += 4
    for ln in cv.wrap(story["deck"], 3, w - 24):
        cv.text(x + 12, yy, ln, 3, (60, 60, 58))
        yy += 25


STORIES = [
    {"kicker": "SHENZHEN", "band": NAVY, "icon": "flags",
     "headline": "SUMMIT ISSUES JOINT STATEMENT",
     "deck": "Four-point pact on nuclear arms."},
    {"kicker": "MARKETS", "band": TEAL, "icon": "chip",
     "headline": "ANTHROPIC SHARES SOAR ON DEBUT",
     "deck": "$83 to $111.50. Worth $1.5tn."},
    {"kicker": "CRYPTO", "band": AMBER, "icon": "coin",
     "headline": "BITCOIN NEARS $60,000",
     "deck": "BTC $61,635. Fear index 10."},
    {"kicker": "WEATHER", "band": BLUE, "icon": "storm",
     "headline": "CYCLONE AKVAN HITS INDIA",
     "deck": "80,000 evacuated. Noon landfall."},
    {"kicker": "SPACE", "band": NAVY, "icon": "satellite",
     "headline": "VOYAGER 1 NEARS ONE LIGHT-DAY",
     "deck": "Farthest human object ever."},
    {"kicker": "JUSTICE", "band": RED, "icon": "scales",
     "headline": "MYANMAR GENOCIDE RULING",
     "deck": "Court finds intent to destroy."},
]


def build():
    cv = Canvas()
    # masthead
    cv.rect(0, 0, W, 10, RED)
    cv.rect(0, 10, W, 94, NAVY)
    cv.text(28, 26, "THE WORLD IN ONE DAY", 6, LIGHT)
    cv.text(28, 72, "FRIDAY, 20 NOVEMBER 2026", 3, (240, 196, 90))
    cv.disc(948, 57, 27, (240, 196, 90))
    cv.text(948 - cv.text_width("20", 4) // 2, 43, "20", 4, NAVY)
    # subline
    cv.text(28, 114, "Trump delays Iran to 2027, a record AI debut, a cyclone, Bitcoin near $60,000.", 2, GREY)
    # lead story
    cv.text(28, 148, "IRAN DECISION - LEAD STORY", 2, RED)
    yy = 176
    for ln in ("TRUMP PUTS IRAN", "DECISION OFF", "TO 2027"):
        cv.text(28, yy, ln, 5, INK)
        yy += 45
    cv.para(28, 312,
            "Trump says there is no rush: he will see what happens after Jan 1. The decision moves to 2027.",
            3, 612, INK)
    draw_lead_scene(cv, 660, 150, 340, 270)
    # divider
    cv.rect(24, 448, 976, 2, GREY)
    # grid: 2 rows x 3 columns
    xs = (24, 354, 684)
    ys = (462, 702)
    for i, st in enumerate(STORIES):
        draw_cell(cv, xs[i % 3], ys[i // 3], 316, 230, st)
    # footer
    cv.rect(24, 946, 976, 2, RED)
    cv.text(24, 958, "ALSO TODAY", 2, RED)
    cv.para(24, 978,
            "Fed signals more rate hikes | Seoul court clears ex-PM Han | Fiji declares drought disaster | Nicholls 113* as NZ hit 243/5",
            2, 976, INK)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(build())
    with open(os.path.join(outdir, "entry.png"), "wb") as f:
        f.write(data)


if __name__ == "__main__":
    main()
