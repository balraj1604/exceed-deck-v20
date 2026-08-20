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

| 10 | deck-wide | Design brief received (seminar in JP, DAMAC conference, projector) | see `docs/DESIGN-BRIEF.md` |
| 11 | deck-wide | Spotlight glow on blue slides only, position varies per slide | **DONE** — `.spot` with `--sx/--sy`, 17 slides, no two neighbours share a corner |
| 12 | deck-wide | Monogram inside the glow, topical per slide, skip on dense slides | **DONE** — 13 motifs; 22/23/7/21 get glow only |
| 13 | deck-wide | Projector font floor | **DONE** — 15px floor, 19 rules lifted; citations exempt |
| 14 | deck-wide | Running headers don't match chapters | **DONE** — re-derived from divider positions (6/27/35); 20 headers corrected |
| 15 | deck-wide | TOC page refs stale | **DONE** — P.05/26/34 → P.06/27/35 |
| 16 | 7 | red→amber→yellow descent ramp, 96% dominant | **DONE** |
| 17 | 25 | Remove the boxes | **DONE** — thin rules, figures up to 112px |
| 18 | 21 | `#1` → plain numerals, graded bars | **DONE** |
| 19 | 22 | Stronger Dubai treatment + independent-ranking note | **DONE** — solid accent band across all 3 tables |
| 20 | 23 | Visa table should dominate; clean rank markers | **DONE** |
| 21 | 20 | Overlaps, stray rule, off-plan vs secondary caveat, +77% leads | **DONE** |
| 22 | 10 | Recentre 2040, new metro image, Creek Tower asset, align text, implication lines | **DONE** — all 4 |
| 23 | 11 | 3 image cards + freehold as a policy strip, implication lines | **DONE** |
| 24 | 27 | Distinct divider image | **DONE** |

| 25 | 7 | Don't focus on 96% — make the three stats **equal** (supersedes the brief's "96% dominant") | doing |
| 26 | 12 | Fix alignment of the conclusion / +67万戸 block | doing |
| 27 | 17 | Add a 2020–2025 bar chart under the 35.2兆円 figure | doing |
| 28 | 18 | Text overlay — bar label collides with the rail figure | doing |
| 29 | maps | Bigger map, more visible lines, labelled accordingly | doing |
| 30 | 20 | Add the off-plan vs secondary line chart as a faded background | doing |
| 31 | 21 | Text overlay on 年間取引総額; nothing may overflow the slide | doing |
| 32 | 28 | Remove the JVC row highlight | doing |

| 33 | assets | TAKUMI mark supplied (screenshot) | **DONE** — extracted to transparent white + dark variants |
| 34 | assets | EXCEED logo supplied (vault `04-Renders-Images/exceed_company_logo.jpg`) | **DONE** — knocked out of navy, 4x upscaled, white + dark variants |
| 35 | 3 | Logos into the three reserved mark slots | **DONE** — EXCEED on panels 1+2, TAKUMI on panel 3 |
| 36 | 33 | TAKUMI logo on the slide | **DONE** |
| 37 | 11 | Lower the caption labelling | **DONE** — bottom 342 → 250, gradient follows |
| 38 | 36 | Add 2026 as a reference | queued |
| 39 | 39 | Airbnb logo; EXCEED in boxes 1+4; TAKUMI in box 3 | queued (logos now in hand) |
| 40 | 40 | Add visuals | queued |

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
