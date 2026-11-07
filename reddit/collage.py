"""Reddit collage (r/dataisbeautiful style): the world's colour names as dots, the most common colour in each country,
and the colour words of each language. Light parchment background, 2400 px wide. Run after code/03 and code/04."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "code"))
import pandas as pd
import matplotlib.patheffects as pe
from figstyle import *

R = jload(f"{DATA}/results.json")
M = pd.read_csv(f"{WORK}/main.csv", keep_default_na=False)
BC = pd.read_csv(f"{DATA}/by_country.csv", keep_default_na=False)
OUT = os.path.join(ROOT, "reddit", "colour_names_collage.png")
W, H = 24, 27   # inches at 100 dpi: 2400 x 2700 px
fig = plt.figure(figsize=(W, H), dpi=100, facecolor=PAPER)
HALO = [pe.withStroke(linewidth=5, foreground=PAPER)]

# title
fig.text(0.035, 0.975, "The colours of the world's place names", fontproperties=DISP, fontsize=64, color=INK, va="top")
fig.text(0.035, 0.935, f"{R['source']['main']:,} rivers, hills, springs and villages named black, white, red, green, blue or yellow, in {R['source']['languages']} languages. One dot per name.",
         fontproperties=FELLI, fontsize=30, color=MUT, va="top")

# big world map
ax = fig.add_axes([0.01, 0.5, 0.98, 0.375])
inkmap(ax, ext=(-170, 180, -56, 82), lw=0.7)
dots(ax, M, s=3.2)
xy = lambda lon, lat: eqearth(lon, lat)
# callouts: beside their region on open sea, or on the paper strip above the map with a thin leader straight down
notes = [(-150, 22, "United States:\nBlack Creek,\nWhite River, Red Hill"),
         (-128, -32, "Latin America:\nCerro Colorado ×" + f"{R['families']['cerro_colorado']:,}" + ",\nRío Blanco, Río Negro"),
         (65, 9, "Arabic:\nnearly\nhalf red"),
         (157, 16, "China: bai 白 (white)\nand huang 黄 (yellow)")]
for lon, lat, t in notes:
    x, y = xy(lon, lat)
    ax.text(x, y, t, fontsize=20, color=INK, ha="center", va="center", zorder=9, linespacing=1.2, path_effects=HALO)
x, y = xy(50, 21); ax.plot([xy(59, 14)[0], x], [xy(59, 14)[1], y], color=INK, lw=1.1, zorder=8); ax.scatter([x], [y], s=18, color=INK, zorder=8)
top = [(0.40, "Norway: svart (black)\non every tarn and fell", (10, 63)),
       (0.565, "Russian: nearly half red,\na fifth of it revolutionary", (45, 62)),
       (0.74, "Turkic world: Karasu ×" + f"{R['families']['karasu']}" + ",\nAksu, Karakol", (70, 46))]
for lon, t, (lo2, la2) in top:
    fx = lon
    ax.annotate(t, xy=xy(lo2, la2), xytext=(fx, 0.905), textcoords="figure fraction", ha="center", va="center", fontsize=18, color=INK,
                linespacing=1.2, zorder=9, arrowprops=dict(arrowstyle="-", color=INK, lw=1.1, shrinkA=22, shrinkB=0), annotation_clip=False)
    ax.scatter([xy(lo2, la2)[0]], [xy(lo2, la2)[1]], s=18, color=INK, zorder=8)

# legend of colours
lax = fig.add_axes([0, 0, 1, 1], zorder=10); lax.set_axis_off(); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
x = 0.04
for c in COLOURS:
    lab = "Blue-green (青, qing / ao)" if c == "grue" else CNAME[c]
    lax.scatter([x], [0.487], s=520, c=TINT[c], edgecolors=EDGE[c], linewidths=2)
    t = f"{lab} {R['colour_pct'][c]:.0f}%"
    lax.text(x + 0.014, 0.487, t, fontsize=20, va="center", color=INK)
    x += 0.033 + 0.0099 * len(t)

# country map
ax2 = fig.add_axes([0.01, 0.12, 0.5, 0.33])
big = BC[BC.n >= 30]
inkmap(ax2, ext=(-170, 180, -56, 82), countries={r.cc: (TINT[r.top], 1) for r in big.itertuples()}, borders=True, lw=0.5)
fig.text(0.03, 0.455, "The most common colour in each country", fontproperties=DISPB, fontsize=30, color=INK, va="top")
fig.text(0.03, 0.43, f"White leads in {R['countries']['top_count']['white']}, black in {R['countries']['top_count']['black']}, red in {R['countries']['top_count']['red']} of {R['countries']['with30']} countries; blue in none",
         fontsize=17, color=MUT, va="top")

# kinds of place panel
ax3 = fig.add_axes([0.58, 0.30, 0.39, 0.105]); ax3.set_facecolor(PAPER)
F = pd.read_csv(f"{DATA}/by_feature.csv").set_index("ftype")
rows = [("river", "Rivers"), ("spring", "Springs"), ("mountain", "Mountains"), ("settlement", "Villages")]
for i, (k, lab) in enumerate(rows[::-1]):
    xx = 0; tot = sum(F.loc[k, c + "_eq"] for c in COLOURS)
    for c in COLOURS:
        v = 100 * F.loc[k, c + "_eq"] / tot
        ax3.barh(i, v, left=xx, color=TINT[c], edgecolor=INK if c == "white" else EDGE[c], lw=0.8, height=0.72)
        if v >= 12:
            ax3.text(xx + v / 2, i, f"{v:.0f}%", ha="center", va="center", fontsize=15, color="#FFFDF6" if c in ("black", "red") else INK)
        xx += v
    ax3.text(-1.5, i, lab, ha="right", va="center", fontsize=19)
ax3.set_xlim(0, 100); ax3.set_axis_off()
fig.text(0.58, 0.455, "Black rivers, white springs", fontproperties=DISPB, fontsize=30, color=INK, va="top")
fig.text(0.58, 0.43, "Colour by kind of place (each language weighted equally)", fontsize=17, color=MUT, va="top")

# word table
WD = [("en", "English"), ("es", "Spanish"), ("pt", "Portuguese"), ("fr", "French"), ("de", "German"), ("nord", "Nordic"), ("eslav", "Russian"),
      ("tr", "Turkic"), ("mn", "Mongolian"), ("ar", "Arabic"), ("fa", "Persian"), ("zh", "Chinese"), ("ja", "Japanese")]
fig.text(0.58, 0.285, "The words", fontproperties=DISPB, fontsize=30, color=INK, va="top")
cols6 = ["black", "white", "red", "green", "blue", "yellow"]
y0 = 0.255; dy = 0.0122
xs = [0.58] + [0.66 + k * 0.053 for k in range(6)]
for k, c in enumerate(cols6):
    lax.scatter([xs[k + 1] + 0.004], [y0 + 0.002], s=300, c=TINT[c], edgecolors=EDGE[c], linewidths=1.6)
for j, (l, nm) in enumerate(WD):
    y = y0 - (j + 1) * dy
    fig.text(xs[0], y, nm, fontsize=15, color=INK, va="center")
    for k, c in enumerate(cols6):
        w = WORDS[l].get(c, "")
        w = w.split(",")[0].strip() if w else "·"
        if l == "zh" and c == "blue":
            w = "蓝 lan"
        fig.text(xs[k + 1], y, w, fontsize=14 if len(w) < 9 else 12, color=INK, va="center")
fig.text(0.58, y0 - 14.3 * dy, "Chinese and Japanese 青 (qing, ao) means both blue and green.", fontsize=13, color=MUT, va="center")

# footer
fig.text(0.035, 0.035, f"Method: colour words matched per language in GeoNames names (natural features and settlements; buildings, farms and roads left out). "
         f"\n{R['precision']['sampled'] + R['precision_supp']['sampled']:,} names hand-checked, {R['precision']['overall_pct']}% correct after tuning. The gazetteer is far denser in some countries (US, Mexico, China,\nNorway, Iran); Korean, Hindi and Urdu count only where the meaning is clear, and Hungarian, Finnish and Greek are not included.",
         fontsize=15, color=MUT, va="bottom", linespacing=1.4)
fig.text(0.035, 0.012, "Source: GeoNames (CC BY 4.0), Natural Earth  ·  Dr Tristan Hotham  ·  maps.tristanhotham.com/colour-names", fontsize=17, color=INK, va="bottom")
fig.savefig(OUT, dpi=100, facecolor=PAPER)
im = Image.open(OUT); print(OUT, im.size)
