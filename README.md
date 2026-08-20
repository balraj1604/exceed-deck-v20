# EXCEED Dubai 営業資料 v20 — HTML deck

41 slides, rebuilt as HTML from the Google Slides source. Real text (no rasterised
type, no mojibake), Noto Sans JP embedded locally so it renders identically offline.

**View:** [slides/index.html](slides/index.html) — scroll through all 41,
or open `slides/slide-01.html` and use ← / → to page.

## Layout

| path | what |
|---|---|
| `slides/` | built output — one file per slide, plus `index.html` (all 41 stacked) |
| `slides/theme.css` | shared design system: 3 chapter palettes + table / bar / KPI components |
| `slides/fonts/` | Noto Sans JP, 496 subset files, embedded for offline rendering |
| `overrides/slide-NN.html` | hand-authored slides — these replace the generated body |
| `order.txt` | final slide number → source slide. Lets slides be inserted or dropped without the numbering drifting |
| `build.py` | Google Slides JSON → HTML. Run `python3 build.py` to rebuild |
| `FEEDBACK.md` | running feedback log + standing design rules |

## Chapters

- **1 · なぜ今 (7–26)** — navy `#0B1522`
- **2 · どう選ぶか (27–34)** — cream `#F4F1EA`
- **3 · なぜEXCEEDか (35–41)** — teal `#0C2B2B`

Gold `#C9A84C` is constant across all three.

## Known open items

- Slide 36: the source deck contradicts itself — 年間取引額 60億円 (KPI) vs 111億円 (chart).
  Currently rendering 111億円 with a visible note. Needs confirmation.
- Slide 3: EXCEED monogram + TAKUMI mark not yet supplied.
- Slide 10 panel 4 (クリークタワー): no photo yet, shows a placeholder.
- Map area boundaries are approximate (`概略`), not survey data.
- Page numbers are deliberately absent — added in one pass once the deck is final.
