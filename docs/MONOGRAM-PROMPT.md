# Monogram generation prompt — EXCEED v20

Paste the block below into Gemini / Nano Banana / whichever image model, replacing
`{{MOTIF}}` with one line from the motif table. Generate one image per motif.

---

## PROMPT

```
Create a SEAMLESS REPEATING TILE PATTERN — a luxury fashion-house monogram, in the
style of a Gucci or Louis Vuitton repeat, but using the motif described below.

MOTIF: {{MOTIF}}

STRICT REQUIREMENTS — the image is unusable if any of these are broken:
1. SEAMLESSLY TILEABLE. The pattern must repeat edge-to-edge with no visible seam.
   Any motif touching an edge must continue exactly on the opposite edge.
2. FLAT SINGLE COLOUR on a fully TRANSPARENT background. Colour: #C9A84C (muted gold).
   No gradients, no shadows, no glow, no highlights, no 3D, no bevel.
3. THIN LINE ART ONLY — uniform stroke weight, roughly 6–8% of one motif's height.
   Outline style, not filled silhouettes.
4. DENSE and SMALL. Fit roughly 8 x 8 repeats of the motif in the square canvas.
   The motif should read as delicate texture, not as illustration.
5. EVENLY SPACED on a regular grid or a simple diagonal offset. Uniform spacing,
   no clustering, no random scatter, no focal point.
6. Square canvas, 1024 x 1024, PNG with alpha.
7. NO text, NO letters, NO numbers, NO logos, NO borders, NO frame, NO background shape.

The result will be tiled behind text at about 15% opacity, so clarity of the individual
motif matters more than detail.
```

---

## MOTIF TABLE — one generation per row

| Slide | `{{MOTIF}}` line to paste |
|---|---|
| 8 | a simple city skyline of 3–4 rectangular towers alongside a small globe with latitude and longitude lines |
| 12 | simple human pictograms — an adult standing figure, a figure in a skirt, a small child, and a wheelchair user, alternating |
| 13 | the Japanese yen symbol ¥ alternating with the Arabic dirham symbol د.إ |
| 14 | the Tokyo Tower silhouette alternating with the Burj Khalifa silhouette |
| 15 | small square apartment floor-plan outlines, each divided into two or three rooms |
| 16 | simple circle outlines of two or three different sizes, like soap bubbles |
| 17 | a stack of coins alongside a small ascending bar chart of three bars |
| 18 | a document sheet with a folded corner and three horizontal text lines |
| 19 | a passport booklet alternating with a small aeroplane in flight |
| 20 | the Burj Khalifa spire only — the tapered upper section with its stepped setbacks, no base |
| 24 | a heraldic shield outline alternating with a small key |
| 25 | a percent sign alternating with a passport and a coin |
| 26 | the Japanese yen symbol ¥ paired with a small upward arrow |

---

## After generating

Drop the PNGs in `slides/assets/mono/` named `s08.png`, `s12.png`, `s13.png` … and tell
me — I'll swap them in over the current SVG tiles in one pass.

## Honest note on this route

Image models are unreliable at true seamless tiling; expect visible seams on most
attempts and generate several per motif. The SVG tiles currently in the deck tile
perfectly by construction, stay crisp at any projector size, and recolour from one CSS
value. Worth comparing side by side before committing — generated raster will look
richer up close and worse on a 4m screen.
