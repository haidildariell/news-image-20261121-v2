[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v2/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/haidildariell/news-image-20261121-v2/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)

# THE WORLD IN ONE DAY — Saturday 21 November 2026

A one-page picture newspaper: **33 verified stories from Saturday 21
November 2026, across 7 regions** — everything that happened, or was first
reported, on that one day, in at least one time zone.

## What's on the page

- **Masthead + giant date** — "Saturday 21 November 2026", with the four
  biggest threads in the sub-headline.
- **Stat strip** — 3 Houthi missiles over Riyadh · 9 killed in Kyiv bridge
  strikes · 6bn miles (BepiColombo's Mercury trip) · 19 wickets on Ashes
  Day 1 · 51,531 record Perth Ashes crowd · M6.7 Peru quake.
- **Region strip** — EUROPE 13 · AMERICAS 6 · ASIA-PAC 1 · MIDEAST 3 ·
  AFRICA 1 · OCEANIA 7 · WORLD-SPACE 2. All 7 regions covered.
- **3 lead stories** (illustrated): Riyadh missile intercepts, BepiColombo's
  Mercury orbit insertion, COP31 in overtime with no deal.
- **10 feature stories** (small illustrations): Kyiv bridges, Kryvyi Rih,
  Ashes Day 1, Gaza, Wellington Test, Turin ATP semis, Las Vegas GP, Rutte
  in Warsaw, Peru quake, SpaceX USSF-317.
- **ALSO ON SATURDAY — 20 more stories**, numbered 14–33, two columns.
- **WHERE IT HAPPENED** — hand-drawn world map with numbered pins 1–13
  (2 = Mercury, in the legend).
- **HOW WE DATE** — the dating rule, stated on the page.
- **DATE CHECK** — Friday 20 November (or earlier) stories deliberately
  excluded, so the page is honest about what is *not* Saturday news.
- **Footer** — "Every story here happened, or was first reported, on
  Saturday 21 November 2026 in at least one time zone. Claims are
  attributed, not stated as fact."

## v2 vs v1

v1 had 14 stories / 5 regions and carried five stories that, on re-check,
were first reported on **Friday 20 November**: the NSE becoming the world's
5th-largest exchange, Indonesia fire losses "could reach $30bn", Malaysia
resettling 10,000 Rohingya in Türkiye, four cheetah cubs born at Kuno, and
the Nepal PM's India visit. Those five were removed from the page and moved
to the DATE CHECK box. v2 has 33 stories / 7 regions, all Saturday-dated,
with the Friday-evening strikes (Kyiv, Kryvyi Rih) shown only with their
Saturday casualty updates.

## Dating rule

A story counts as Saturday's if it happened, or was first reported, on
21 November 2026 in **at least one time zone**. That is why the two NBA Cup
games played Friday night in the US (Saturday 00:30 UTC / Saturday AEDT)
count, and why the Kyiv/Kryvyi Rih strikes — launched Friday night — are
shown with the casualty tolls updated on Saturday. BepiColombo's Mercury
orbit insertion is scheduled for 19:24 CET Saturday and is phrased as such.

## Build

Deterministic, Pillow only, no network at run time:

```bash
python3 build_image.py   # writes entry.png (1024x1024, < 1 MiB)
```

## Run

```bash
python3 main.py          # copies entry.png to $MAKEFUN_OUTPUT_DIR (default /output)
```

Two runs produce byte-identical output (verified, see SOURCES.md for the
hash).

## Files

- `build_image.py` — the renderer (all art is original flat vector drawn
  with Pillow; no photos, no external assets).
- `main.py` — entrypoint: copies `entry.png` to the harness output dir.
- `entry.png` — the entry, 1024×1024.
- `SOURCES.md` — every story with its source, plus the Friday stories that
  were excluded and why.
- `LICENSE` — MIT.

## Sources

Reuters, AFP, AP, BBC, ESA, UN News, and others — the full list is in
SOURCES.md.
