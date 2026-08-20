#!/usr/bin/env python3
"""Cream luxury textures for Chapter 2 — same idiom as the SpicyKiwi
gen-card-textures.py: real generated grayscale fields, low amplitude around a
neutral mid-grey, quantised, composited as a multiply wash over the cream so
the base colour always dominates. Full-frame (no tiling => no seams)."""
from PIL import Image, ImageFilter, ImageChops, ImageOps
import math, random, os

W, H = 1440, 810
OUT = "slides/assets/tex"
os.makedirs(OUT, exist_ok=True)
random.seed(7)

def noise(w=W, h=H, sigma=1.0, seed=None):
    im = Image.effect_noise((w, h), 48)
    if sigma: im = im.filter(ImageFilter.GaussianBlur(sigma))
    return im

def octaves(specs):
    """specs: [(downscale, blur, weight)] -> combined mid-grey field.
    ImageChops refuses mode F, so the octaves are summed in plain python."""
    tot = sum(w for _, _, w in specs)
    layers = []
    for ds, blur, wgt in specs:
        n = noise(max(8, W // ds), max(8, H // ds), blur).resize((W, H), Image.BICUBIC)
        layers.append((n.load(), wgt))
    out = Image.new("L", (W, H)); op = out.load()
    for y in range(H):
        for x in range(W):
            op[x, y] = int(sum(px[x, y] * w for px, w in layers) / tot)
    return out

def norm(im, lo=118, hi=138):
    im = ImageOps.autocontrast(im, cutoff=1)
    return im.point(lambda v: int(lo + v / 255 * (hi - lo)))

def save(im, name, levels=24):
    im.quantize(colors=levels).convert("L").save(f"{OUT}/{name}.png", optimize=True)
    print(f"  {name:<18} {os.path.getsize(f'{OUT}/{name}.png')//1024:>4} KB")

# 1 leather — pebbled cell grain, two octaves
lea = octaves([(3, 1.2, 1.0), (12, 2.4, .8), (48, 6, .5)])
lea = lea.filter(ImageFilter.EMBOSS).filter(ImageFilter.GaussianBlur(.6))
save(norm(lea, 116, 140), "leather")

# 2 marble — sinusoidal banding warped by turbulence
turb = octaves([(6, 2, 1.0), (24, 5, .9), (90, 10, .7)])
mar = Image.new("L", (W, H)); mp = mar.load(); tp = turb.load()
for y in range(H):
    for x in range(0, W):
        t = (tp[x, y] - 128) / 128.0
        v = math.sin((x * 0.010 + y * 0.004 + t * 2.6)) * 0.5 + 0.5
        mp[x, y] = int(120 + v * 16)
save(mar.filter(ImageFilter.GaussianBlur(.8)), "marble")

# 3 velvet — directional nap (vertical smear of fine noise)
vel = noise(sigma=0.4).filter(ImageFilter.GaussianBlur(0.3))
vel = vel.resize((W, H // 22), Image.BILINEAR).resize((W, H), Image.BICUBIC)
save(norm(vel, 118, 138), "velvet")

# 4 brushed gold — long horizontal streaks
br = noise(sigma=0).resize((W, 60), Image.BILINEAR).resize((W, H), Image.BICUBIC)
br = br.filter(ImageFilter.GaussianBlur(0.4))
save(norm(br, 116, 140), "brushed")

# 5 silk — fine moiré from two crossed low-freq waves
sk = Image.new("L", (W, H)); sp = sk.load()
for y in range(H):
    for x in range(W):
        v = (math.sin((x * .9 + y * .28) * .1) + math.sin((x * .22 - y * .8) * .07)) * .25 + .5
        sp[x, y] = int(120 + v * 15)
save(sk.filter(ImageFilter.GaussianBlur(.5)), "silk")

# 6 travertine — porous stone
tra = octaves([(2, .8, 1.0), (7, 1.8, .9), (26, 5, .7)])
save(norm(tra, 114, 141), "travertine")

# 7 suede — soft fine nap, no direction
sue = octaves([(4, 1.6, 1.0), (16, 3.5, .6)])
save(norm(sue, 120, 137), "suede")

# 8 pale oak — wood grain: stretched rings
oak = Image.new("L", (W, H)); op = oak.load(); tp2 = turb.load()
for y in range(H):
    for x in range(W):
        t = (tp2[x, y] - 128) / 128.0
        r = math.sin((y * 0.055) + t * 1.1) * .5 + .5
        op[x, y] = int(119 + r * 17)
save(oak.filter(ImageFilter.GaussianBlur(.7)), "oak")

# 9 washi — long irregular paper fibres
wa = noise(sigma=0.5)
wa = wa.resize((W // 3, H), Image.BILINEAR).resize((W, H), Image.BICUBIC)
wa = ImageChops.multiply(wa, octaves([(30, 8, 1.0)]))
save(norm(wa, 121, 137), "washi")

# 10 pearl — very low-frequency iridescent swell
pe = octaves([(60, 14, 1.0), (140, 26, .8)])
save(norm(pe, 122, 137), "pearl")

# 11 granite — coarse mineral speckle
gr = noise(sigma=0.2)
gr = ImageChops.multiply(gr, octaves([(18, 4, 1.0)]))
save(norm(gr, 115, 141), "granite")

# 12 damask — soft quilted diamond emboss
da = Image.new("L", (W, H)); dp = da.load()
for y in range(H):
    for x in range(W):
        v = (math.sin(x * .0295) * math.sin(y * .0295)) * .5 + .5
        dp[x, y] = int(121 + v * 14)
da = ImageChops.multiply(da, octaves([(10, 3, 1.0)]))
save(norm(da, 119, 138), "damask")
