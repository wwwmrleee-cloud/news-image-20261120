#!/usr/bin/env python3
"""news-image-20261120: one 1024x1024 PNG summing up the world news of
Friday 20 November 2026 — 44 stories, 7 regions, every story sourced and
confidence-labelled, plus a UTC timeline and a date check.

Pure Python standard library only (os, struct, zlib): a hand-typed 5x7
pixel font, its own PNG encoder, no fonts, no images, no network, no
clock, no chance, so two runs write byte-identical files.
Run: mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import os
import struct
import zlib

W, H = 1024, 1024

# --- 5x7 pixel font, typed by hand. Each glyph is 7 rows of 5 bits. ---
FONT = {
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
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
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
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
    "|": ("00100", "00100", "00100", "00100", "00100", "00100", "00100"),
    "~": ("00000", "00000", "01001", "10110", "00000", "00000", "00000"),
}

PAPER = (247, 243, 232)
INK = (20, 20, 20)
NAVY = (18, 38, 66)
RED = (179, 38, 30)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
ORANGE = (196, 96, 16)
GREEN = (34, 120, 60)
PURPLE = (90, 60, 140)
GREY = (90, 90, 86)
LIGHT = (255, 255, 255)
CREAM = (232, 222, 190)
GOLD = (212, 164, 44)

# (region, headline, source, confidence). HIGH = 2+ outlets or a primary
# source; MED = one outlet. 44 stories in all.
STORIES = [
    # NORTH AMERICA — 9
    ("NORTH AMERICA", "TRUMP PUTS IRAN DECISION OFF TO 2027", "REUTERS", "HIGH"),
    ("NORTH AMERICA", "ANTHROPIC SHARES SOAR TO $111.50 ON DEBUT", "CNN", "HIGH"),
    ("NORTH AMERICA", "FED MINUTES: MORE HIKES LIKELY, 50BP IN DEC", "FED", "HIGH"),
    ("NORTH AMERICA", "BITCOIN $61,635 AS ETF OUTFLOWS TOP $2.5BN", "FOOL", "HIGH"),
    ("NORTH AMERICA", "GPT-6.2 ASTRA GETS TOP AI RISK RATING", "AI-BRIEF", "MED"),
    ("NORTH AMERICA", "OPENAI AGENTS DO 46% OF 2-4H RESEARCH", "CENTURY", "MED"),
    ("NORTH AMERICA", "CODEX FINDS OPENJDK FLAW FOR UNDER $200", "ACTCAL", "MED"),
    ("NORTH AMERICA", "CALIFORNIA SEEKS KILL-SWITCH FOR RISKY AI", "CENTURY", "MED"),
    ("NORTH AMERICA", "KNICKS EDGE WOLVES 102-99, 3RD STRAIGHT", "APEX", "MED"),
    # SOUTH AMERICA — 6
    ("SOUTH AMERICA", "TESLA OPENS FIRST STORE IN ARGENTINA", "REUTERS", "HIGH"),
    ("SOUTH AMERICA", "BRAZIL SCRAPS SMALL-PARCEL TAX", "WHYIT", "MED"),
    ("SOUTH AMERICA", "CORREIOS UNIONS CALL STRIKE FROM 26 NOV", "WHYIT", "MED"),
    ("SOUTH AMERICA", "BRAZIL TOURISM BEATS TARGET: 7.59M VISITS", "TRAVEL", "MED"),
    ("SOUTH AMERICA", "BUKELE REGISTERS FOR 3RD TERM IN 2027", "BREIT", "MED"),
    ("SOUTH AMERICA", "US, VENEZUELA RESTORE MILITARY TIES", "PENTAGON", "HIGH"),
    # MIDDLE EAST — 5
    ("MIDDLE EAST", "GAZA CEASEFIRE ON BRINK OF COLLAPSE", "UNSC", "MED"),
    ("MIDDLE EAST", "IRAN STILL HOLDS 2,500+ MISSILES: WSJ", "WSJ", "MED"),
    ("MIDDLE EAST", "TANKER STRUCK, ON FIRE IN STRAIT OF HORMUZ", "UKMTO", "MED"),
    ("MIDDLE EAST", "IRAN READIES TANKER CONVOY AT KHARG", "EURONEWS", "MED"),
    ("MIDDLE EAST", "UAE CONDEMNS SOMALIA'S HOSTILE APPROACH", "BIZINS", "MED"),
    # EUROPE — 7
    ("EUROPE", "EU ADOPTS 1BN EURO MILITARY AID TO UKRAINE", "EU", "HIGH"),
    ("EUROPE", "30+ UKRAINE ALLIES MEET IN BERLIN", "HUMMINI", "MED"),
    ("EUROPE", "ESTONIA TO SHUT BORDER WITH RUSSIA", "EURONEWS", "MED"),
    ("EUROPE", "ITALY STRIKES OVER LIVING COSTS", "EURONEWS", "MED"),
    ("EUROPE", "ZELENSKYY CALLS PUTIN A 'KILLER'", "EURONEWS", "MED"),
    ("EUROPE", "MEDVEDEV BEATS TIAFOE, INTO ATP SEMIS", "IANS", "MED"),
    ("EUROPE", "BARCA 6-0, LYONNES 2-0 IN WOMEN'S UCL", "APEX", "MED"),
    # AFRICA — 5
    ("AFRICA", "GAMBIA INTERCEPTS 491 WOULD-BE MIGRANTS", "PANA", "MED"),
    ("AFRICA", "TUNISIA JAILS RIGHTS DEFENDER 5 YEARS", "AMNESTY", "HIGH"),
    ("AFRICA", "GUINEA NOW 3RD IRON ORE EXPORTER", "BIZINS", "MED"),
    ("AFRICA", "ZIMBABWE: LITHIUM MINERS MUST BUY LOCAL", "BIZINS", "MED"),
    ("AFRICA", "CHAWINGA UP FOR GLOBE SOCCER AWARD", "MALAWI", "MED"),
    # ASIA — 9
    ("ASIA", "SHENZHEN SUMMIT: 4-POINT NUCLEAR PACT", "CBS", "HIGH"),
    ("ASIA", "CYCLONE AKVAN LANDFALL DUE, 80,000 FLEE", "TOI", "HIGH"),
    ("ASIA", "ICJ: MYANMAR LIKELY MEANT TO DESTROY ROHINGYA", "ICJ", "HIGH"),
    ("ASIA", "S. KOREA COURT CLEARS EX-PM HAN", "COURT", "HIGH"),
    ("ASIA", "N. KOREA EXPANDS YONGBYON ENRICHMENT", "IAEA", "HIGH"),
    ("ASIA", "MODI MEETS PRINCE AND PRINCESS OF WALES", "TOI", "HIGH"),
    ("ASIA", "NVIDIA HALTS SOME AI CHIP SALES TO CHINA", "NEURON", "MED"),
    ("ASIA", "BINANCE HACKER WALLET MOVES 137,602 ETH", "KWIZERA", "MED"),
    ("ASIA", "RIPPLE CEO: ANTHROPIC IPO DRAINED CRYPTO", "CNBC", "MED"),
    # OCEANIA — 3
    ("OCEANIA", "FIJI DECLARES DROUGHT DISASTER", "FIJI", "MED"),
    ("OCEANIA", "NICHOLLS 175 AS NZ POST 368 VS INDIA", "APEX", "HIGH"),
    ("OCEANIA", "AUSTRALIA SANCTIONS ISRAELI SETTLERS", "JAGRAN", "MED"),
]

REGION_ORDER = [
    ("NORTH AMERICA", 9, NAVY),
    ("SOUTH AMERICA", 6, TEAL),
    ("MIDDLE EAST", 5, RED),
    ("EUROPE", 7, BLUE),
    ("AFRICA", 5, ORANGE),
    ("ASIA", 9, GREEN),
    ("OCEANIA", 3, PURPLE),
]

TITLE = "THE WORLD IN ONE DAY"
SUBTITLE = "44 STORIES - FRIDAY, 20 NOVEMBER 2026"
TAGLINE = "7 REGIONS | EVERY STORY SOURCED | CONFIDENCE ON EVERY LINE"
TIMELINE = [
    "UTC TIMELINE: 21:36 UTC 19 NOV TRUMP ON IRAN | ~07:00 UTC SHENZHEN",
    "06:30 UTC CYCLONE LANDFALL DUE | 14:30 UTC ANTHROPIC OPENS ON NASDAQ",
]
DATECHECK = [
    "DATE CHECK: ALL 44 STORIES DATED 20 NOV 2026 IN SOME TIME ZONE.",
    "HIGH = 2+ OUTLETS OR PRIMARY SOURCE. MED = ONE OUTLET.",
]

LX, RX = 24, 1000
HEADER_H = 104
BODY_Y = 110
BAND_H = 17
ROW_H = 16
GROUP_GAP = 1


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

    def glyph(self, x, y, ch, scale, colour):
        rows = FONT.get(ch)
        if rows is None:
            raise ValueError("character not in font: %r" % ch)
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


def draw_page(cv):
    # Masthead.
    cv.fill_rect(0, 0, W, 6, RED)
    cv.fill_rect(0, 6, W, HEADER_H - 6, NAVY)
    cv.text(24, 18, TITLE, 5, LIGHT)
    cv.text(24, 58, SUBTITLE, 3, GOLD)
    cv.text(24, 84, TAGLINE, 2, LIGHT)
    cv.hline(LX, 108, RX - LX, RED)
    # Story list, grouped by region.
    y = BODY_Y
    n = 0
    for region, count, band in REGION_ORDER:
        group = [s for s in STORIES if s[0] == region]
        assert len(group) == count, (region, len(group), count)
        cv.fill_rect(LX, y, RX - LX, BAND_H, band)
        cv.text(LX + 8, y + 2, "%s - %d STORIES" % (region, count), 2, LIGHT)
        y += BAND_H
        for region_, headline, source, conf in group:
            n += 1
            if n % 2 == 0:
                cv.fill_rect(LX, y, RX - LX, ROW_H, CREAM)
            left = "%02d. %s" % (n, headline)
            cv.text(LX, y + 1, left, 2, INK)
            right = "%s %s" % (source, conf)
            cv.text(RX - cv.text_w(right, 2), y + 1, right, 2,
                    RED if conf == "HIGH" else GREY)
            y += ROW_H
        y += GROUP_GAP
    assert n == 44, n
    # UTC timeline strip.
    cv.hline(LX, y + 4, RX - LX, RED)
    ty = y + 10
    for ln in TIMELINE:
        cv.text(LX, ty, ln, 2, INK)
        ty += 17
    # Date-check lines.
    ty += 4
    for ln in DATECHECK:
        cv.text(LX, ty, ln, 2, GREY)
        ty += 17
    assert ty <= H, ty
    return ty


def main():
    assert len(STORIES) == 44, len(STORIES)
    for region, count, _band in REGION_ORDER:
        got = sum(1 for s in STORIES if s[0] == region)
        assert got == count, (region, got, count)
    for _region, headline, source, conf in STORIES:
        assert source and conf in ("HIGH", "MED"), (headline, source, conf)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    cv = Canvas()
    draw_page(cv)
    with open(os.path.join(out, "entry.png"), "wb") as f:
        f.write(cv.png_bytes())


if __name__ == "__main__":
    main()
