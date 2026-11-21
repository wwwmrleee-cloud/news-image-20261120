# 44 stories — 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/wwwmrleee-cloud/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/wwwmrleee-cloud/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

One 1024x1024 image that sums up the world news of Friday 20 November 2026: **44 stories across 7 regions** (North America 9, South America 6, Middle East 5, Europe 7, Africa 5, Asia 9, Oceania 3). Every story carries its source and a confidence label on the same line (HIGH = two or more outlets or a primary source, MED = one outlet). A UTC timeline strip orders the day's turning points, and a date-check line states that all 44 stories are dated 20 November 2026 in some time zone.

Headlines include Trump putting the Iran decision off to 2027, the Shenzhen summit's four-point nuclear pact, Anthropic's shares soaring to $111.50 on debut, Bitcoin at $61,635, Cyclone Akvan's landfall, and the ICJ ruling on Myanmar. Stories are grouped under coloured region bands, with alternating row shading so each of the 44 one-line rows stays readable at a glance.

The program is pure Python 3 standard library: it draws the poster with a hand-typed 5x7 pixel font and its own PNG encoder. No fonts, no images, no network, no clock, no randomness — two runs write byte-identical files.

Run it:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

That writes `out/entry.png` (1024x1024).
