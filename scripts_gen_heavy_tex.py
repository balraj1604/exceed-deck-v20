#!/usr/bin/env python3
"""Heavy material textures — real structure, not noise washes.
Leather uses jittered-grid Voronoi (actual pore cells); silk uses a woven
warp/weft with directional sheen and slubs. Rendered small then upscaled,
which is what gives the grain its softness."""
from PIL import Image, ImageFilter, ImageChops, ImageOps
import math, random, os
OUT="slides/assets/tex"; os.makedirs(OUT,exist_ok=True)
W,H=1440,810
random.seed(11)

def voronoi(cell=9, w=480, h=270, jitter=0.85):
    """distance-to-nearest-seed on a jittered grid -> leather pore cells"""
    gx,gy = w//cell+2, h//cell+2
    seeds=[[(ix*cell+random.uniform(-jitter,jitter)*cell,
             iy*cell+random.uniform(-jitter,jitter)*cell) for ix in range(gx)]
           for iy in range(gy)]
    im=Image.new("L",(w,h)); px=im.load()
    for y in range(h):
        iy=y//cell
        for x in range(w):
            ix=x//cell
            best=1e9
            for jy in range(max(0,iy-1),min(gy,iy+2)):
                for jx in range(max(0,ix-1),min(gx,ix+2)):
                    sx,sy=seeds[jy][jx]
                    d=(sx-x)**2+(sy-y)**2
                    if d<best: best=d
            px[x,y]=min(255,int(math.sqrt(best)/cell*300))
    return im

def emboss(im, depth=1.0, blur=1.1):
    im=im.filter(ImageFilter.GaussianBlur(blur))
    e=im.filter(ImageFilter.EMBOSS)
    return Image.blend(Image.new("L",im.size,128), e, depth)

def fin(im, lo, hi, name, levels=32):
    im=im.resize((W,H), Image.LANCZOS)
    im=ImageOps.autocontrast(im, cutoff=1).point(lambda v:int(lo+v/255*(hi-lo)))
    im.quantize(colors=levels).convert("L").save(f"{OUT}/{name}.png", optimize=True)
    print(f"  {name:<22} {os.path.getsize(f'{OUT}/{name}.png')//1024:>4} KB")

# ---- 1 pebbled leather: big pores, deep relief ----------------------------
v=voronoi(cell=11)
fin(emboss(v, 1.0, 1.3), 70, 186, "hv-leather-pebble")

# ---- 2 full-grain leather: fine pores + creases ---------------------------
v2=voronoi(cell=6, jitter=0.95)
cre=Image.effect_noise((240,135),64).resize((480,270),Image.BICUBIC).filter(ImageFilter.GaussianBlur(3))
mix=ImageChops.multiply(v2, ImageOps.autocontrast(cre))
fin(emboss(mix, 1.0, 1.0), 74, 182, "hv-leather-grain")

# ---- 3 saffiano: cross-hatch pressed leather ------------------------------
sa=Image.new("L",(480,270)); sp=sa.load()
for y in range(270):
    for x in range(480):
        a=math.sin((x+y)*0.62); b=math.sin((x-y)*0.62)
        sp[x,y]=int(128+(a*b)*66)
fin(emboss(sa,0.9,0.5), 76, 180, "hv-leather-saffiano")

# ---- 4 silk charmeuse: woven warp/weft + directional sheen ----------------
sk=Image.new("L",(720,405)); kp=sk.load()
slub=[random.random() for _ in range(720)]
for y in range(405):
    for x in range(720):
        weave = 34 if ((x//3 + y//3) % 2) else -34          # over / under
        sheen = math.sin((x*0.55 + y*1.9)*0.02)*30          # long diagonal lustre
        thread= slub[x]*16 - 8                              # slubs in the warp
        kp[x,y]=max(0,min(255,int(128+weave*0.55+sheen+thread)))
fin(sk.filter(ImageFilter.GaussianBlur(0.7)), 72, 184, "hv-silk-charmeuse")

# ---- 5 dupioni raw silk: heavy irregular slubs ----------------------------
du=Image.new("L",(720,405)); dp=du.load()
sl=[random.gauss(0,1) for _ in range(405)]
for y in range(405):
    row=sl[y]*26
    for x in range(720):
        weave = 26 if (x//2)%2 else -26
        dp[x,y]=max(0,min(255,int(128+weave*0.6+row+math.sin(x*0.09)*10)))
fin(du.filter(ImageFilter.GaussianBlur(0.8)), 70, 186, "hv-silk-dupioni")

# ---- 6 heavy woven cloth: visible basket weave ----------------------------
cl=Image.new("L",(480,270)); cp=cl.load()
for y in range(270):
    for x in range(480):
        warp = math.sin(x*0.78)*44
        weft = math.sin(y*0.78)*44
        over = warp if ((x//4+y//4)%2) else weft
        cp[x,y]=max(0,min(255,int(128+over)))
fin(emboss(cl,0.85,0.6), 74, 182, "hv-cloth-basket")
