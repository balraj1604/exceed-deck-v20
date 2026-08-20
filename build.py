#!/usr/bin/env python3
"""EXCEED_Dubai_営業資料_v20 : Google Slides -> pixel-faithful HTML.

One .html per slide, absolutely positioned, real text (no OCR, no mojibake).
Reads source/deck.json (Slides API v1 presentations.get output).
"""
import json, os, re, html, base64, hashlib, urllib.request, concurrent.futures

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(ROOT, "source", "deck.json")
OUT  = os.path.join(ROOT, "slides")
IMG  = os.path.join(OUT, "img")

W_PX = 1920.0                      # render width
EMU_PER_IN = 914400.0

deck   = json.load(open(SRC))
PW_EMU = deck["pageSize"]["width"]["magnitude"]
PH_EMU = deck["pageSize"]["height"]["magnitude"]
SCALE  = W_PX / PW_EMU             # EMU -> px
H_PX   = PH_EMU * SCALE
# points -> px  (1pt = 1/72in)
PT = (EMU_PER_IN / 72.0) * SCALE

# ---------------------------------------------------------------- colours
SCHEME = {}
for m in deck.get("masters", []):
    for c in m.get("pageProperties", {}).get("colorScheme", {}).get("colors", []):
        SCHEME.setdefault(c["type"], c.get("color", {}))

def _rgb(d):
    r = round(d.get("red", 0) * 255); g = round(d.get("green", 0) * 255); b = round(d.get("blue", 0) * 255)
    return (r, g, b)

def color_of(opt, alpha=None):
    """OpaqueColor / OptionalColor -> css rgb()/rgba() or None."""
    if not opt: return None
    c = opt.get("opaqueColor", opt)
    if "rgbColor" in c:
        r, g, b = _rgb(c["rgbColor"])
    elif "themeColor" in c:
        t = SCHEME.get(c["themeColor"])
        if t is None: return None
        r, g, b = _rgb(t)
    else:
        return None
    if alpha is not None and alpha < 1:
        return f"rgba({r},{g},{b},{round(alpha,3)})"
    return f"rgb({r},{g},{b})"

def fill_css(fill):
    if not fill or fill.get("propertyState") == "NOT_RENDERED": return None
    sf = fill.get("solidFill")
    if not sf: return None
    return color_of(sf.get("color"), sf.get("alpha", 1))

# ---------------------------------------------------------------- geometry
# AffineTransform  ->  matrix (a c e / b d f):
#   a=scaleX  b=shearY  c=shearX  d=scaleY  e=translateX  f=translateY
IDENT = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

def mat(t):
    # proto3: numeric fields equal to 0 are omitted from the JSON, so an absent
    # scaleX/scaleY means 0 — NOT 1. Horizontal rules arrive as scaleY absent.
    if not t: return IDENT
    return (t.get("scaleX", 0.0), t.get("shearY", 0.0), t.get("shearX", 0.0),
            t.get("scaleY", 0.0), t.get("translateX", 0.0), t.get("translateY", 0.0))

def mul(P, C):
    """Compose: apply C first, then P (P o C) — group children are child-relative."""
    pa, pb, pc, pd, pe, pf = P
    ca, cb, cc, cd, ce, cf = C
    return (pa*ca + pc*cb,
            pb*ca + pd*cb,
            pa*cc + pc*cd,
            pb*cc + pd*cd,
            pa*ce + pc*cf + pe,
            pb*ce + pd*cf + pf)

def box(el, parent=IDENT):
    """-> (left, top, width, height, css-transform) in px, in page space."""
    a, b, c, d, e, f = mul(parent, mat(el.get("transform")))
    sz = el.get("size", {})
    w = sz.get("width", {}).get("magnitude", 0)
    h = sz.get("height", {}).get("magnitude", 0)
    if b or c:                                        # rotated / skewed
        return (e * SCALE, f * SCALE, w * SCALE, h * SCALE,
                f"matrix({round(a,6)},{round(b,6)},{round(c,6)},{round(d,6)},0,0)")
    return (e * SCALE, f * SCALE, w * a * SCALE, h * d * SCALE, None)

# ---------------------------------------------------------------- images
os.makedirs(IMG, exist_ok=True)
_jobs = {}
def image_src(url):
    if not url: return None
    key = hashlib.md5(url.split("?")[0].encode()).hexdigest()[:16]
    if key not in _jobs: _jobs[key] = url
    return f"img/{key}"

def fetch_all():
    def go(item):
        key, url = item
        for ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ""):
            p = os.path.join(IMG, key + ext)
            if os.path.exists(p) and os.path.getsize(p) > 0: return key, ext
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=60) as r:
                data = r.read()
                ct = r.headers.get("Content-Type", "")
            ext = ".png"
            if "jpeg" in ct or "jpg" in ct: ext = ".jpg"
            elif "gif" in ct: ext = ".gif"
            elif "webp" in ct: ext = ".webp"
            elif "svg" in ct: ext = ".svg"
            open(os.path.join(IMG, key + ext), "wb").write(data)
            return key, ext
        except Exception as e:
            return key, None
    res = {}
    with concurrent.futures.ThreadPoolExecutor(16) as ex:
        for key, ext in ex.map(go, list(_jobs.items())):
            res[key] = ext
    return res

# ---------------------------------------------------------------- text
FONT_STACK = {
    "Noto Sans JP": "'Noto Sans JP','Hiragino Sans','Hiragino Kaku Gothic ProN','Yu Gothic',sans-serif",
    "Arial":        "Arial,'Helvetica Neue',Helvetica,'Hiragino Sans',sans-serif",
    "Calibri":      "Calibri,Carlito,'Segoe UI','Hiragino Sans',sans-serif",
    "Georgia":      "Georgia,'Times New Roman',serif",
}
def font_css(name):
    if not name: return None
    return FONT_STACK.get(name, f"'{name}','Hiragino Sans',sans-serif")

ALIGN = {"START": "left", "CENTER": "center", "END": "right", "JUSTIFIED": "justify"}
VALIGN = {"TOP": "flex-start", "MIDDLE": "center", "BOTTOM": "flex-end"}

def run_style(st):
    o = []
    f = font_css(st.get("fontFamily"))
    if f: o.append(f"font-family:{f}")
    fs = st.get("fontSize", {}).get("magnitude")
    if fs: o.append(f"font-size:{round(fs*PT,2)}px")
    if st.get("bold"): o.append("font-weight:700")
    if st.get("italic"): o.append("font-style:italic")
    deco = []
    if st.get("underline"): deco.append("underline")
    if st.get("strikethrough"): deco.append("line-through")
    if deco: o.append("text-decoration:" + " ".join(deco))
    c = color_of(st.get("foregroundColor", {}).get("opaqueColor"))
    if c: o.append(f"color:{c}")
    bg = color_of(st.get("backgroundColor", {}).get("opaqueColor"))
    if bg: o.append(f"background-color:{bg}")
    bo = st.get("baselineOffset")
    if bo == "SUPERSCRIPT": o.append("vertical-align:super;font-size:0.7em")
    elif bo == "SUBSCRIPT": o.append("vertical-align:sub;font-size:0.7em")
    ls = st.get("weightedFontFamily", {}).get("weight")
    if ls and ls >= 700 and not st.get("bold"): o.append("font-weight:700")
    return ";".join(o)

def para_style(ps):
    o = []
    a = ALIGN.get(ps.get("alignment"))
    if a: o.append(f"text-align:{a}")
    lsp = ps.get("lineSpacing")
    if lsp: o.append(f"line-height:{round(lsp/100.0,3)}")
    for k, css in (("spaceAbove", "margin-top"), ("spaceBelow", "margin-bottom")):
        v = ps.get(k, {}).get("magnitude")
        if v: o.append(f"{css}:{round(v*PT,2)}px")
    for k, css in (("indentStart", "padding-left"), ("indentEnd", "padding-right")):
        v = ps.get(k, {}).get("magnitude")
        if v: o.append(f"{css}:{round(v*PT,2)}px")
    fi = ps.get("indentFirstLine", {}).get("magnitude")
    if fi: o.append(f"text-indent:{round(fi*PT,2)}px")
    d = ps.get("direction")
    if d == "RIGHT_TO_LEFT": o.append("direction:rtl")
    return ";".join(o)

def render_text(text, lists=None):
    """TextContent -> list of <p> strings."""
    if not text: return []
    lists = text.get("lists", {})
    out, cur, cur_ps, cur_bullet = [], [], "", None
    def flush():
        if cur_ps or cur:
            tag_open = f'<p style="{cur_ps}">' if cur_ps else "<p>"
            body = "".join(cur)
            out.append(tag_open + (body if body else "<br>") + "</p>")
    for te in text.get("textElements", []):
        if "paragraphMarker" in te:
            if cur or cur_ps: flush()
            cur, cur_ps = [], para_style(te["paragraphMarker"].get("style", {}))
            b = te["paragraphMarker"].get("bullet")
            cur_bullet = b
            if b:
                glyph = b.get("glyph")
                bs = run_style(b.get("bulletStyle", {}))
                lvl = b.get("nestingLevel", 0)
                pad = round((18 + lvl * 18) * (W_PX / 1920.0), 2)
                cur_ps = (cur_ps + ";" if cur_ps else "") + f"padding-left:{pad}px;position:relative"
                if glyph:
                    cur.append(f'<span class="bul" style="{bs}">{html.escape(glyph)}</span>')
        elif "textRun" in te:
            tr = te["textRun"]
            c = tr.get("content", "")
            if c == "": continue
            st = run_style(tr.get("style", {}))
            link = tr.get("style", {}).get("link", {}).get("url")
            esc = html.escape(c).replace("\n", "").replace("", "<br>")
            if esc == "": continue
            frag = f'<span style="{st}">{esc}</span>' if st else esc
            if link: frag = f'<a href="{html.escape(link)}" style="color:inherit">{frag}</a>'
            cur.append(frag)
        elif "autoText" in te:
            at = te["autoText"]
            st = run_style(at.get("style", {}))
            cur.append(f'<span style="{st}">{html.escape(at.get("content",""))}</span>')
    flush()
    return out

# ---------------------------------------------------------------- shapes
ROUND = {"ROUND_RECTANGLE", "ROUNDED_RECTANGLE"}
def shape_geo_css(stype, w, h):
    o = []
    if stype in ROUND:
        o.append(f"border-radius:{round(min(w,h)*0.14,2)}px")
    elif stype == "ELLIPSE":
        o.append("border-radius:50%")
    elif stype == "TRIANGLE":
        o.append("clip-path:polygon(50% 0,100% 100%,0 100%)")
    elif stype == "RIGHT_ARROW":
        o.append("clip-path:polygon(0 30%,60% 30%,60% 0,100% 50%,60% 100%,60% 70%,0 70%)")
    elif stype == "DIAMOND":
        o.append("clip-path:polygon(50% 0,100% 50%,50% 100%,0 50%)")
    return ";".join(o)

def outline_css(ol):
    if not ol or ol.get("propertyState") == "NOT_RENDERED": return None
    c = fill_css(ol.get("outlineFill", {}))
    wv = ol.get("weight", {}).get("magnitude")
    if not c and not wv: return None
    px = max(round((wv or 9525) * SCALE, 2), 0.5)
    dash = ol.get("dashStyle", "SOLID")
    style = {"DASH": "dashed", "DOT": "dotted", "LONG_DASH": "dashed",
             "DASH_DOT": "dashed", "LONG_DASH_DOT": "dashed"}.get(dash, "solid")
    return f"border:{px}px {style} {c or 'rgb(0,0,0)'}"

def shadow_css(sh):
    if not sh or sh.get("propertyState") != "RENDERED": return None
    a = sh.get("alpha", 0.4)
    c = color_of(sh.get("color"), a) or "rgba(0,0,0,.4)"
    br = round(sh.get("blurRadius", {}).get("magnitude", 0) * SCALE, 2)
    t = sh.get("transform", {})
    dx = round(t.get("translateX", 0) * SCALE, 2); dy = round(t.get("translateY", 0) * SCALE, 2)
    return f"box-shadow:{dx}px {dy}px {br}px {c}"

# ---------------------------------------------------------------- elements
def plain_text(el):
    tes = el.get("shape", {}).get("text", {}).get("textElements", [])
    return "".join(r["textRun"]["content"] for r in tes if "textRun" in r).strip()

def is_chrome(el, parent=IDENT):
    """Per Balraj (2026-08-20): every slide drops the gold top rail, the
    'EXCEED REAL ESTATE L.L.C · Dubai Real Estate Investment' footer, and the
    page number. Page numbers get re-added once the deck is final."""
    if "shape" not in el: return False
    a, _b, _c, d, e, f = mul(parent, mat(el.get("transform")))
    sz = el.get("size", {})
    w = sz.get("width", {}).get("magnitude", 0) * a
    h = sz.get("height", {}).get("magnitude", 0) * d
    txt = plain_text(el)
    # 1. full-bleed rail hugging the top edge
    if not txt and f <= 12000 and 0 < h <= 70000 and w >= PW_EMU * 0.97:
        return True
    # 2. footer lockup
    if "Dubai Real Estate Investment" in txt:
        return True
    # 3. page number: bare digits parked bottom-right
    if re.fullmatch(r"\d{1,3}", txt) and e > PW_EMU * 0.83 and f > PH_EMU * 0.90:
        return True
    return False

def el_html(el, parent=IDENT, depth=0):
    if is_chrome(el, parent): return ""
    l, t, w, h, tf = box(el, parent)
    base = f"left:{round(l,2)}px;top:{round(t,2)}px;width:{round(w,2)}px;height:{round(h,2)}px"
    if tf: base += f";transform:{tf};transform-origin:0 0"
    oid = el.get("objectId", "")

    if "shape" in el:
        sh = el["shape"]; sp = sh.get("shapeProperties", {})
        stype = sh.get("shapeType", "RECTANGLE")
        css = [base]
        f = fill_css(sp.get("shapeBackgroundFill"))
        if f: css.append(f"background:{f}")
        o = outline_css(sp.get("outline"));  css.append(o) if o else None
        d = shadow_css(sp.get("shadow"));    css.append(d) if d else None
        g = shape_geo_css(stype, w, h);      css.append(g) if g else None
        va = VALIGN.get(sp.get("contentAlignment", "TOP"), "flex-start")
        css.append(f"justify-content:{va}")
        ins = sh.get("text", {})
        paras = render_text(ins)
        pad = round(7.2 * PT * 0 + 0, 2)   # Slides default insets applied below
        # default text insets: 0.1in L/R, 0.05in T/B
        css.append(f"padding:{round(0.05*EMU_PER_IN*SCALE,2)}px 0px")
        body = "".join(paras)
        return f'<div class="sh" data-id="{oid}" style="{";".join(css)}">{body}</div>'

    if "image" in el:
        im = el["image"]
        src = image_src(im.get("contentUrl") or im.get("sourceUrl"))
        ip = im.get("imageProperties", {})
        css = [base, "overflow:hidden"]
        o = outline_css(ip.get("outline"));  css.append(o) if o else None
        d = shadow_css(ip.get("shadow"));    css.append(d) if d else None
        crop = ip.get("cropProperties", {})
        istyle = "width:100%;height:100%;object-fit:fill;display:block"
        if crop:
            lo = crop.get("leftOffset", 0); ro = crop.get("rightOffset", 0)
            to = crop.get("topOffset", 0);  bo = crop.get("bottomOffset", 0)
            if any((lo, ro, to, bo)):
                sw = 100 / max(1e-6, (1 - lo - ro)); shh = 100 / max(1e-6, (1 - to - bo))
                istyle = (f"position:absolute;width:{round(sw,4)}%;height:{round(shh,4)}%;"
                          f"left:{round(-lo*sw,4)}%;top:{round(-to*shh,4)}%;object-fit:fill")
        filt = []
        if ip.get("transparency"): filt.append(f"opacity:{round(1-ip['transparency'],3)}")
        if ip.get("brightness"): filt.append(f"brightness({1+ip['brightness']})")
        if filt: istyle += ";" + ";".join(f for f in filt if ":" in f)
        return (f'<div class="im" data-id="{oid}" style="{";".join(css)}">'
                f'<img src="{src}" alt="" style="{istyle}" loading="lazy"></div>')

    if "line" in el:
        ln = el["line"]; lp = ln.get("lineProperties", {})
        c = fill_css(lp.get("lineFill", {})) or "rgb(0,0,0)"
        wv = lp.get("weight", {}).get("magnitude", 9525)
        px = max(round(wv * SCALE, 2), 0.6)
        ma, mb, mc, md, me, mf = mul(parent, mat(el.get("transform")))
        sz = el.get("size", {})
        w0 = sz.get("width", {}).get("magnitude", 0); h0 = sz.get("height", {}).get("magnitude", 0)
        x1, y1 = me, mf
        x2 = me + w0 * ma + h0 * mc
        y2 = mf + w0 * mb + h0 * md
        dash = lp.get("dashStyle", "SOLID")
        da = {"DASH": "10,8", "DOT": "2,6", "LONG_DASH": "18,8",
              "DASH_DOT": "12,6,3,6"}.get(dash)
        dattr = f' stroke-dasharray="{da}"' if da else ""
        return (f'<svg class="ln" data-id="{oid}" style="left:0;top:0;width:{round(W_PX,2)}px;'
                f'height:{round(H_PX,2)}px;overflow:visible">'
                f'<line x1="{round(x1*SCALE,2)}" y1="{round(y1*SCALE,2)}" '
                f'x2="{round(x2*SCALE,2)}" y2="{round(y2*SCALE,2)}" '
                f'stroke="{c}" stroke-width="{px}" stroke-linecap="round"{dattr}/></svg>')

    if "table" in el:
        tb = el["table"]
        rows = tb.get("tableRows", [])
        colw = [c.get("columnWidth", {}).get("magnitude", 0) for c in tb.get("tableColumns", [])]
        tot = sum(colw) or 1
        # A table's `size` is a dummy 3000000x3000000 box — its true extent is the
        # sum of the column widths / row heights, scaled by the transform.
        ma, mb, mc, md, me, mf = mul(parent, mat(el.get("transform")))
        tw = tot * ma * SCALE
        th = sum(r.get("rowHeight", {}).get("magnitude", 0) for r in rows) * md * SCALE
        base = (f"left:{round(me*SCALE,2)}px;top:{round(mf*SCALE,2)}px;"
                f"width:{round(tw,2)}px;height:{round(th,2)}px")
        out = [f'<div class="tb" data-id="{oid}" style="{base}">',
               '<table style="width:100%;height:100%;border-collapse:collapse;table-layout:fixed">',
               "<colgroup>"]
        for cw in colw: out.append(f'<col style="width:{round(cw/tot*100,4)}%">')
        out.append("</colgroup><tbody>")
        for r in rows:
            rh = r.get("rowHeight", {}).get("magnitude")
            rs = f' style="height:{round(rh*SCALE,2)}px"' if rh else ""
            out.append(f"<tr{rs}>")
            for cell in r.get("tableCells", []):
                if cell.get("rowSpan", 1) == 0 or cell.get("columnSpan", 1) == 0: continue
                cp = cell.get("tableCellProperties", {})
                cs = []
                f = fill_css(cp.get("tableCellBackgroundFill"))
                if f: cs.append(f"background:{f}")
                va = {"TOP": "top", "MIDDLE": "middle", "BOTTOM": "bottom"}.get(
                    cp.get("contentAlignment", "TOP"), "top")
                cs.append(f"vertical-align:{va}")
                cs.append(f"padding:{round(0.05*EMU_PER_IN*SCALE,2)}px {round(0.05*EMU_PER_IN*SCALE,2)}px")
                span = ""
                if cell.get("rowSpan", 1) > 1: span += f' rowspan="{cell["rowSpan"]}"'
                if cell.get("columnSpan", 1) > 1: span += f' colspan="{cell["columnSpan"]}"'
                out.append(f'<td{span} style="{";".join(cs)}">' + "".join(render_text(cell.get("text"))) + "</td>")
            out.append("</tr>")
        out.append("</tbody></table></div>")
        return "".join(out)

    if "elementGroup" in el:
        gm = mul(parent, mat(el.get("transform")))     # children are group-relative
        return "".join(el_html(c, gm, depth + 1)
                       for c in el["elementGroup"].get("children", []))

    return ""

# ---------------------------------------------------------------- page
CSS = """
@import url("fonts/noto.css");
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#1a1a1a}
.slide{position:relative;width:%(W)spx;height:%(H)spx;background:#fff;overflow:hidden;
  margin:0 auto;transform-origin:top center}
.sh{position:absolute;display:flex;flex-direction:column;overflow:visible}
.sh p{width:100%%;font-family:'Noto Sans JP','Hiragino Sans',sans-serif;
  font-size:%(BASE)spx;line-height:1.2;color:#000;word-break:normal;overflow-wrap:normal;white-space:pre-wrap;
  font-feature-settings:"palt" 1;font-kerning:normal;line-break:strict}
.sh .bul{position:absolute;left:0}
.im{position:absolute}
.ln{position:absolute;pointer-events:none}
.tb{position:absolute}
.tb p{font-family:'Noto Sans JP','Hiragino Sans',sans-serif;font-size:%(BASE)spx;
  line-height:1.25;color:#000;white-space:pre-wrap;word-break:normal;overflow-wrap:normal;
  font-feature-settings:"palt" 1;line-break:strict}
""" % {"W": round(W_PX, 2), "H": round(H_PX, 2), "BASE": round(14 * PT, 2)}

PAGE = """<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>%(title)s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<style>%(css)s
html,body{height:100%%;overflow:hidden}
#stage{position:absolute;inset:0;display:grid;place-items:center}
#fitbox{position:relative}
#fitbox .slide{position:absolute;left:0;top:0;transform-origin:0 0;margin:0}
</style></head><body>
<div id="stage"><div id="fitbox"><div class="slide" id="s%(n)s" style="background:%(bg)s">%(body)s</div></div></div>
<script>
(function(){var W=%(W)s,H=%(H)s,fb=document.getElementById('fitbox'),
s=fb.firstElementChild;
function fit(){var k=Math.min(innerWidth/W,innerHeight/H);
fb.style.width=(W*k)+'px';fb.style.height=(H*k)+'px';
s.style.transform='scale('+k+')';}
addEventListener('resize',fit);fit();
addEventListener('keydown',function(e){var m=location.pathname.match(/slide-(\\d+)/);
if(!m)return;var n=+m[1],t=null;
if(e.key==='ArrowRight'||e.key===' ')t=Math.min(%(N)s,n+1);
if(e.key==='ArrowLeft')t=Math.max(1,n-1);
if(t&&t!==n)location.href='slide-'+String(t).padStart(2,'0')+'.html';});})();
</script></body></html>"""

LAYOUTS = {l["objectId"]: l for l in deck.get("layouts", [])}
MASTERS = {m["objectId"]: m for m in deck.get("masters", [])}

def page_bg(s):
    """Slide background: own fill, else layout's, else master's (INHERIT chain)."""
    sp = s.get("slideProperties", {})
    chain = [s,
             LAYOUTS.get(sp.get("layoutObjectId"), {}),
             MASTERS.get(sp.get("masterObjectId"), {})]
    for p_ in chain:
        f = p_.get("pageProperties", {}).get("pageBackgroundFill", {})
        if not f or f.get("propertyState") == "INHERIT":
            continue
        c = fill_css(f)
        if c: return c
    # master may store the fill un-nested
    for p_ in chain:
        c = fill_css(p_.get("pageProperties", {}))
        if c: return c
    return "#fff"

OVR = os.path.join(ROOT, "overrides")

def override(i):
    """overrides/slide-NN.html replaces the generated body for that slide.
    First line may be   <!--bg: <css-colour> -->   to set the page background."""
    p = os.path.join(OVR, f"slide-{i:02d}.html")
    if not os.path.exists(p): return None
    t = open(p, encoding="utf-8").read()
    m = re.match(r"\s*<!--\s*bg:\s*(.+?)\s*-->", t)
    return (t, m.group(1) if m else None)

def slide_order():
    """order.txt maps FINAL slide number -> source, so slides can be inserted,
    dropped or reordered without the deck numbering drifting from Canva's.
        4 = src:3     final slide 4 renders deck["slides"][2]
        3 = new       final slide 3 has no source; overrides/slide-03.html supplies it
    Absent file  ->  identity (1:1 with deck["slides"])."""
    p = os.path.join(ROOT, "order.txt")
    if not os.path.exists(p):
        return [(i, i) for i in range(1, len(deck["slides"]) + 1)]
    out = []
    for raw in open(p, encoding="utf-8"):
        line = raw.split("#")[0].strip()
        if not line: continue
        final, _, src = (x.strip() for x in line.partition("="))
        out.append((int(final), None if src == "new" else int(src.split(":")[1])))
    return sorted(out)

MISSING = ('<div style="position:absolute;inset:0;display:grid;place-items:center;'
           'background:#3a0d0d;color:#ffb4b4;font:600 34px/1.4 sans-serif;text-align:center">'
           'slide %d has no source and no overrides/slide-%02d.html</div>')

def build():
    os.makedirs(OUT, exist_ok=True)
    order = slide_order()
    pages = []
    edited = []
    for final, src in order:
        s = deck["slides"][src - 1] if src else None
        o = override(final)
        if o:
            body = o[0]
            bg = o[1] or (page_bg(s) if s else "#fff")
            edited.append(final)
        elif s:
            body, bg = "".join(el_html(e) for e in s.get("pageElements", [])), page_bg(s)
        else:
            body, bg = MISSING % (final, final), "#3a0d0d"
        pages.append((final, s["objectId"] if s else "new", body, bg))
    exts = fetch_all()
    def fix(b):
        def r(m):
            k = m.group(1); e = exts.get(k)
            return f'src="img/{k}{e}"' if e else 'src="" data-missing="1"'
        return re.sub(r'src="img/([0-9a-f]{16})"', r, b)
    names = []
    for i, oid, body, bg in pages:
        body = fix(body)
        name = f"slide-{i:02d}.html"
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(
            PAGE % {"title": f"EXCEED v20 — {i}/{len(pages)}", "css": CSS, "n": i, "bg": bg,
                    "body": body, "W": round(W_PX, 2), "H": round(H_PX, 2),
                    "N": len(pages)})
        names.append((i, name, oid))
    # ---- index: every slide stacked, scroll-through
    allbody = []
    for i, oid, body, bg in pages:
        allbody.append(f'<div class="wrap"><div class="num">{i} / {len(pages)} &nbsp;·&nbsp; {oid}</div>'
                       # the id matters: every override scopes its layout CSS to #sN,
                       # so without it the index renders unpositioned soup.
                       f'<div class="slide" id="s{i}" style="background:{bg}">{fix(body)}</div></div>')
    idx = """<!DOCTYPE html><html lang="ja"><head><meta charset="utf-8">
<title>EXCEED_Dubai_営業資料_v20 — HTML</title><style>%(css)s
body{padding:28px 0}
.wrap{margin:0 auto 34px;width:%(W)spx}
.num{color:#8a8a8a;font:12px/1.6 -apple-system,'Hiragino Sans',sans-serif;margin:0 0 6px 2px;letter-spacing:.06em}
.slide{box-shadow:0 10px 40px rgba(0,0,0,.55)}
@media(max-width:1960px){body{zoom:.62}}
</style></head><body>%(b)s</body></html>""" % {
        "css": CSS, "W": round(W_PX, 2), "b": "".join(allbody)}
    open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(idx)
    ok = sum(1 for v in exts.values() if v)
    print(f"slides: {len(pages)}   images: {ok}/{len(exts)}   "
          f"overrides: {edited or '-'}   -> {OUT}")
    dropped = sorted(set(range(1, len(deck["slides"]) + 1)) - {v for _, v in order if v})
    ins = [f for f, v in order if v is None]
    if ins:     print(f"  inserted (no source): {ins}")
    if dropped: print(f"  dropped from source:  {dropped}")
    miss = [k for k, v in exts.items() if not v]
    if miss: print("image fetch failed:", len(miss))

if __name__ == "__main__":
    build()
