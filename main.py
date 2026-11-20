#!/usr/bin/env python3
"""news-image-20261120: draw one 1024x1024 PNG that sums up the world news
of Friday 20 November 2026. Pure Python standard library only (math, os,
struct, zlib): a hand-typed 5x7 pixel font, its own PNG encoder, no fonts,
no images, no network, no clock, no chance, so two runs write
byte-identical files. Run: python3 main.py (writes
$MAKEFUN_OUTPUT_DIR/entry.png, default /output/entry.png).

The day, as reported on 20 November 2026: Trump puts the Iran decision
off to 2027, saying he will see what happens after Jan 1; Trump, Xi and
Putin issue a four-point joint statement in Shenzhen; Anthropic shares
soar from $83 to $111.50 on debut, worth about $1.5tn; Bitcoin nears
$60,000 at $61,635 with the fear index at 10; Cyclone Akvan forces
80,000 to evacuate ahead of a midday landfall; Voyager 1 nears one
light-day from Earth; the ICJ rules on Myanmar and the Rohingya.
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
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
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
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    ">": ("01000", "00100", "00010", "00001", "00010", "00100", "01000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
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
    "[": ("01110", "01000", "01000", "01000", "01000", "01000", "01110"),
    "\\": ("10000", "01000", "01000", "00100", "00010", "00010", "00001"),
    "]": ("01110", "00010", "00010", "00010", "00010", "00010", "01110"),
    "^": ("00100", "01010", "10001", "00000", "00000", "00000", "00000"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    "`": ("00100", "00100", "00010", "00000", "00000", "00000", "00000"),
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
    "{": ("00110", "01000", "01000", "11100", "01000", "01000", "00110"),
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "}": ("01100", "00010", "00010", "00111", "00010", "00010", "01100"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (18, 38, 66)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
ORANGE = (196, 96, 16)
GOLD = (212, 164, 44)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
SKY = (178, 214, 235)
CREAM = (232, 222, 190)
GREEN = (34, 120, 60)

STORIES = [
    {"kicker": "SHENZHEN", "band": NAVY,
     "headline": "SUMMIT ISSUES JOINT STATEMENT",
     "deck": "Four-point pact on nuclear arms, energy."},
    {"kicker": "MARKETS", "band": TEAL,
     "headline": "ANTHROPIC SHARES SOAR ON DEBUT",
     "deck": "$83 to $111.50. Worth $1.5tn."},
    {"kicker": "CRYPTO", "band": ORANGE,
     "headline": "BITCOIN NEARS $60,000",
     "deck": "BTC $61,635. Fear index 10."},
    {"kicker": "WEATHER", "band": BLUE,
     "headline": "CYCLONE AKVAN NEARS INDIA",
     "deck": "80,000 evacuated. Noon landfall."},
    {"kicker": "SPACE", "band": NAVY,
     "headline": "VOYAGER 1 NEARS ONE LIGHT-DAY",
     "deck": "Farthest human object ever."},
    {"kicker": "JUSTICE", "band": RED,
     "headline": "MYANMAR GENOCIDE RULING",
     "deck": "Court finds likely intent to destroy."},
]

LEAD_KICKER = "IRAN DECISION - LEAD STORY"
LEAD_HEAD = ["TRUMP PUTS IRAN", "DECISION OFF", "TO 2027"]
LEAD_TEXT = ("Trump says there is no rush: he will see what happens "
             "after Jan 1. The decision moves to 2027.")
SUBLINE = ("Trump delays Iran to 2027, a record AI debut, a cyclone, "
           "Bitcoin near $60,000.")
FOOTER = ("Fed signals more rate hikes | Seoul court clears ex-PM Han | "
          "Fiji declares drought disaster | Nicholls 113* as NZ hit 243/5")


class Canvas:
    """An RGB pixel buffer with tiny drawing helpers."""

    def __init__(self):
        self.pix = bytearray(PAPER * (W * H))

    def px(self, x, y, colour):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.pix[i:i + 3] = bytes(colour)

    def fill_rect(self, x, y, w, h, colour):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, colour)

    def hline(self, x, y, w, colour):
        self.fill_rect(x, y, w, 1, colour)

    def vline(self, x, y, h, colour):
        self.fill_rect(x, y, 1, h, colour)

    def line(self, x0, y0, x1, y1, colour):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.px(x0, y0, colour)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                    self.px(xx, yy, colour)

    def ring(self, cx, cy, r, colour):
        for a in range(360):
            t = math.radians(a)
            self.px(cx + int(r * math.cos(t)), cy + int(r * math.sin(t)),
                   colour)

    def glyph(self, x, y, ch, scale, colour):
        rows = FONT.get(ch)
        if rows is None:
            return
        for ry, row in enumerate(rows):
            for rx, bit in enumerate(row):
                if bit == "1":
                    self.fill_rect(x + rx * scale, y + ry * scale,
                                   scale, scale, colour)

    def text(self, x, y, s, scale, colour):
        for i, ch in enumerate(s):
            self.glyph(x + i * 6 * scale, y, ch, scale, colour)

    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale if s else 0

    def centre(self, cx, y, s, scale, colour):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, colour)

    def wrap(self, text, scale, width):
        """Greedy word wrap; returns a list of lines fitting width."""
        per = max(1, width // (6 * scale))
        lines = []
        for raw in text.split("\n"):
            words = raw.split(" ")
            cur = ""
            for wd in words:
                while len(wd) > per:
                    if cur:
                        lines.append(cur)
                        cur = ""
                    lines.append(wd[:per])
                    wd = wd[per:]
                trial = wd if not cur else cur + " " + wd
                if len(trial) <= per:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = wd
            if cur or not lines:
                lines.append(cur)
        return lines

    def para(self, x, y, text, scale, width, colour):
        """Draw wrapped text; returns the y just below the last line."""
        lines = self.wrap(text, scale, width)
        for i, ln in enumerate(lines):
            self.text(x, y + i * 9 * scale, ln, scale, colour)
        return y + len(lines) * 9 * scale

    def png_bytes(self):
        raw = bytearray()
        for yy in range(H):
            raw.append(0)
            raw += self.pix[yy * W * 3:(yy + 1) * W * 3]

        def chunk(tag, data):
            return (struct.pack(">I", len(data)) + tag + data +
                    struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))

        ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
                chunk(b"IDAT", zlib.compress(bytes(raw), 9)) +
                chunk(b"IEND", b""))


def draw_icon(cv, kind, x, y, colour):
    """A small pictogram inside a kicker band, drawn from primitives."""
    if kind == "flags":
        for i, c in enumerate((RED, GOLD, LIGHT)):
            cv.vline(x + i * 12, y + 2, 20, colour)
            cv.fill_rect(x + i * 12 + 1, y + 2, 9, 7, c)
    elif kind == "chip":
        cv.fill_rect(x + 6, y + 6, 16, 16, colour)
        cv.fill_rect(x + 11, y + 11, 6, 6, LIGHT)
        for i in range(3):
            cv.hline(x, y + 9 + i * 5, 5, colour)
            cv.hline(x + 23, y + 9 + i * 5, 5, colour)
    elif kind == "coin":
        cv.ring(x + 14, y + 14, 12, colour)
        cv.text(x + 10, y + 7, "B", 2, colour)
    elif kind == "cloud":
        cv.disc(x + 10, y + 18, 7, colour)
        cv.disc(x + 20, y + 14, 9, colour)
        cv.fill_rect(x + 8, y + 18, 18, 7, colour)
        cv.vline(x + 12, y + 26, 5, colour)
        cv.vline(x + 20, y + 26, 5, colour)
    elif kind == "sat":
        cv.line(x + 2, y + 26, x + 26, y + 2, colour)
        cv.fill_rect(x + 11, y + 11, 7, 7, colour)
        cv.fill_rect(x + 2, y + 20, 8, 5, colour)
        cv.fill_rect(x + 19, y + 4, 8, 5, colour)
    elif kind == "scales":
        cv.vline(x + 14, y + 4, 22, colour)
        cv.hline(x + 4, y + 6, 20, colour)
        cv.line(x + 4, y + 6, x + 1, y + 20, colour)
        cv.line(x + 4, y + 6, x + 7, y + 20, colour)
        cv.line(x + 24, y + 6, x + 21, y + 20, colour)
        cv.line(x + 24, y + 6, x + 27, y + 20, colour)
        cv.hline(x + 1, y + 20, 6, colour)
        cv.hline(x + 21, y + 20, 6, colour)


def draw_cell(cv, st, x, y, w, icon):
    """One story cell: coloured kicker band, headline, deck."""
    cv.fill_rect(x, y, w, 34, st["band"])
    cv.hline(x, y + 34, w, RED)
    cv.text(x + 10, y + 10, st["kicker"], 2, LIGHT)
    draw_icon(cv, icon, x + w - 40, y + 3, LIGHT)
    cv.fill_rect(x, y + 36, w, 196, LIGHT)
    hl = cv.wrap(st["headline"], 4, 292)
    for i, ln in enumerate(hl):
        cv.text(x + 10, y + 46 + i * 34, ln, 4, INK)
    dk = cv.wrap(st["deck"], 3, 292)
    dy = y + 46 + len(hl) * 34 + 4
    for i, ln in enumerate(dk):
        cv.text(x + 10, dy + i * 25, ln, 3, INK)


def draw_calendar(cv, x, y, w, h):
    """Lead illustration: a 2027 January calendar, Jan 1 picked out."""
    cv.fill_rect(x, y, w, h, SKY)
    cv.fill_rect(x + 14, y + 12, w - 28, 46, RED)
    cv.centre(x + w // 2, y + 20, "2027", 5, LIGHT)
    cv.fill_rect(x + 14, y + 58, w - 28, 96, LIGHT)
    cv.centre(x + w // 2, y + 66, "JANUARY", 3, INK)
    gx, gy = x + 30, y + 92
    cw, chh = 40, 18
    for r in range(3):
        for c in range(7):
            cx = gx + c * (cw + 2)
            cy = gy + r * (chh + 2)
            if r == 0 and c == 0:
                cv.fill_rect(cx, cy, cw, chh, RED)
                cv.text(cx + 4, cy + 2, "1", 2, LIGHT)
            else:
                cv.fill_rect(cx, cy, cw, chh, CREAM)
    cv.fill_rect(x + 14, y + 168, w - 28, 44, RED)
    cv.centre(x + w // 2, y + 178, "AFTER JAN 1", 4, LIGHT)
    cv.centre(x + w // 2, y + 224, "NO RUSH, SAYS TRUMP", 2, INK)


def draw_page(cv):
    # Masthead.
    cv.fill_rect(0, 0, W, 10, RED)
    cv.fill_rect(0, 10, W, 108, NAVY)
    cv.text(24, 28, "THE WORLD IN ONE DAY", 7, LIGHT)
    cv.disc(950, 64, 36, GOLD)
    cv.text(928, 50, "20", 4, NAVY)
    cv.text(24, 88, "FRIDAY, 20 NOVEMBER 2026", 3, GOLD)
    # One-line standfirst.
    cv.text(24, 132, SUBLINE, 2, GREY)
    # Lead story, left; calendar illustration, right.
    cv.text(28, 164, LEAD_KICKER, 2, RED)
    for i, ln in enumerate(LEAD_HEAD):
        cv.text(28, 190 + i * 54, ln, 6, INK)
    cv.para(28, 356, LEAD_TEXT, 3, 612, INK)
    draw_calendar(cv, 648, 164, 352, 276)
    # Divider, then the six-cell grid.
    cv.hline(24, 452, 976, INK)
    icons = ["flags", "chip", "coin", "cloud", "sat", "scales"]
    xs = [24, 352, 680]
    for i, st in enumerate(STORIES):
        draw_cell(cv, st, xs[i % 3], 470 + (i // 3) * 244, 312, icons[i])
    # Footer strip.
    cv.hline(24, 958, 976, RED)
    cv.text(24, 966, "ALSO TODAY", 2, RED)
    cv.para(24, 986, FOOTER, 2, 976, INK)


def main():
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    cv = Canvas()
    draw_page(cv)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(cv.png_bytes())


if __name__ == "__main__":
    main()
