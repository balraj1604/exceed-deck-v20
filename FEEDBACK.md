# Balraj feedback log — EXCEED v20 HTML deck

Running list. Each item: what he said → what I did.

## 2026-08-20

| # | Slide | Feedback | Status |
|---|---|---|---|
| 1 | index | Combined view rendered as unpositioned soup | **FIXED** — index template omitted `id="sN"`; every override scopes layout to `#sN` |
| 2 | 27/41 | Use the image at https://share.google/a7x8tNRLCHEYHMlXV for the Chapter 2 divider | open — need the resolved asset |
| 3 | all maps | Marking style: Google-Maps-style area highlight — soft translucent fill, thin stroke, irregular boundary, point dots | **FIXED** — slides 28/29/30/31 reshaped to organic polygons + centre dots |
| 4 | 14/41 | Lot of empty space (lower half unused) | **FIXED** — waterfall + comparison column rescaled to fill the frame |
| 5 | 22,23 (+15,16,21,25,26) | Add country flag / mini city visual to city rows | **FIXED** — flag emoji added to every city table and bar chart |
| 6 | 7/41 | Move 2,800発以上 + 20件程度 under the 96% block | **FIXED** — both now sit in the left column under the meter |
| 7 | 10/41 | Use `dubai_2040_high_quality.png` for the Dubai 2040 panel | **FIXED** — 1024×1536 asset swapped in |
| 8 | 11/41 | Use `disney-abu-dhabi-high-quality.png` for the Disney panel | **FIXED** — 1023×1537 asset swapped in |
| 9 | 12/41 | Background too boring — wanted texture variations to pick from | **FIXED** — 6 variants shown, he chose **B (gold+blue radial glow)**; added as reusable `.glow` class in theme.css, applied to slide 12 |

## Standing rules (apply to every slide, don't re-ask)

- No gold rail across the top of any slide.
- No `EXCEED REAL ESTATE L.L.C · Dubai Real Estate Investment` footer lockup.
- No page numbers until the very end — they get added in one pass once the deck is final.
- Only trust the reference screenshots for real numbers.
- Chapter 1 = navy `#0B1522`, Chapter 2 = cream `#F4F1EA`, Chapter 3 = teal `#0C2B2B`. Gold `#C9A84C` is the constant across all three.
- Slide numbering follows Canva/his numbering via `order.txt`; deck is 41 slides.

## Open items

- EXCEED monogram (slide 3, panels 1–2) + TAKUMI mark (slide 3, panel 3) — awaiting files.
- Slide 10 panel 4 (クリークタワー) has no photo — grey placeholder with `IMAGE PENDING`.
- Slide 36: source deck contradicts itself — KPI says 年間取引額 60億円, chart says 2025 = 111億円.
  Currently rendering 111億円 (chart series) with a visible note. Needs his ruling.
- Slides 5 (目次) and 6 (Chapter 1 divider) kept simple on his instruction — revisit after full deck.
