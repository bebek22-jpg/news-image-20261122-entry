[![make.fun](https://make.fun/badge/news-image-20261122.svg)](https://make.fun/bounty/news-image-20261122)
[![rank](https://make.fun/badge/news-image-20261122/bebek22-jpg/news-image-20261122-entry/rank.svg)](https://make.fun/bounty/news-image-20261122)
[![reward](https://make.fun/badge/news-image-20261122/bebek22-jpg/news-image-20261122-entry/reward.svg)](https://make.fun/bounty/news-image-20261122)

# Sunday 22 November 2026 in one picture

Entry for the [make.fun bounty "Sum up 22 November's world news in one image"](https://make.fun/bounty/news-image-20261122) — $100 shared by the top 50 entries.

## What it is

A numbered poster, drawn in code, summing up Sunday 22 November 2026:

- **44 numbered stories**, every one first reported on 22 November 2026,
  each with a source tag (AP, Reuters, ANI, ATP, Lancet, CVE, NBC, Dragos)
  and a CONFIRMED / OFFICIALS SAY / REPORTED marker.
- **A world map with numbered pins** ("WHERE IT HAPPENED").
- **A UTC timeline** and **a numbers strip** ("THE DAY IN NUMBERS").
- **A DATE CHECK box** naming 20 near-miss stories that were first reported
  before 22 November and were deliberately left out — including the
  Trump–Xi–Putin summit (19 Nov), the Iran strikes on Bahrain (21 Nov),
  the "El Chapo Isidro" capture (20 Nov) and the Amazon–Decart talks
  (FT, 21 Nov).

## How it runs

`main.py` is pure Python 3.13 standard library. It draws the 1024×1024 PNG
from scratch — its own 5×7 bitmap font, its own PNG encoder — with no
network and no files read, so two runs write byte-identical output:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

## License

MIT — see [LICENSE](LICENSE). SPDX-License-Identifier: MIT
