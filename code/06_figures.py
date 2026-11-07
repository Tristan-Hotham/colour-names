"""Step 6: figures. Blog (release/blog/b_*.png, 1800 px wide), paper (release/paper/f_*.png), page (img/*.png, 1400 px)
and the social card (header.png, 1200 x 630). Numbers from data/results.json; dots from WORK/main.csv."""
import shutil
import pandas as pd
import matplotlib.patheffects as pe
from matplotlib.patches import Patch, Rectangle
from figstyle import *

R = jload(f"{DATA}/results.json")
M = pd.read_csv(f"{WORK}/main.csv", keep_default_na=False)
BC = pd.read_csv(f"{DATA}/by_country.csv", keep_default_na=False)
BL = os.path.join(ROOT, "release", "blog"); PA = os.path.join(ROOT, "release", "paper"); IM = os.path.join(ROOT, "img")
for d in (BL, PA, IM):
    os.makedirs(d, exist_ok=True)
HALO = [pe.withStroke(linewidth=3, foreground=PAPER)]
CL = [c for c in COLOURS]
LBL = {c: ("Blue-green (qing, ao)" if c == "grue" else CNAME[c]) for c in COLOURS}


PHOTO = {"world", "families", "countries", "bw"}      # map figures: JPEG in the paper, to keep the PDF small


def save(fig, name, page=True):
    if name in PHOTO:
        fig.savefig(f"{WORK}/tmp.png", dpi=200, facecolor=fig.get_facecolor())
        Image.open(f"{WORK}/tmp.png").convert("RGB").save(os.path.join(PA, "f_" + name + ".jpg"), quality=84, optimize=True)
        if os.path.exists(os.path.join(PA, "f_" + name + ".png")):
            os.remove(os.path.join(PA, "f_" + name + ".png"))
    else:
        fig.savefig(os.path.join(PA, "f_" + name + ".png"), dpi=200, facecolor=fig.get_facecolor())
    fig.savefig(os.path.join(BL, "b_" + name + ".png"), dpi=150, facecolor=fig.get_facecolor())
    if page:
        fig.savefig(os.path.join(IM, name + ".png"), dpi=116.67, facecolor=fig.get_facecolor())
    plt.close(fig)


def title(fig, t, sub=None, y=0.965):
    fig.text(0.03, y, t, fontproperties=DISP, fontsize=24, color=INK, va="top")
    if sub:
        fig.text(0.03, y - 0.055, sub, fontproperties=FELLI, fontsize=15, color=MUT, va="top")


def legend_row(fig, y=0.035, x0=0.03, cols=COLOURS, fs=11):
    lax = fig.add_axes([0, 0, 1, 1], zorder=10); lax.set_axis_off(); lax.set_xlim(0, 1); lax.set_ylim(0, 1)
    x = x0
    for c in cols:
        lax.scatter([x + 0.006], [y + 0.009], s=95, c=TINT[c], edgecolors=EDGE[c], linewidths=1.1)
        lax.text(x + 0.018, y, LBL[c], fontsize=fs, color=INK, va="bottom")
        x += 0.03 + 0.0085 * len(LBL[c])


def credit(fig, t="Data: GeoNames (CC BY 4.0), Natural Earth · maps.tristanhotham.com/colour-names", y=0.012):
    fig.text(0.97, y, t, fontsize=9, color=MUT, ha="right", va="bottom")


# ---------------------------------------------------------------- 1. the world in dots
fig = plt.figure(figsize=(12, 6.6), facecolor=PAPER)
ax = fig.add_axes([0.01, 0.07, 0.98, 0.8])
inkmap(ax, ext=(-180, 180, -58, 84))
dots(ax, M, s=1.0)
title(fig, "Every colour name in the world's gazetteer", f"{R['source']['main']:,} rivers, hills, springs and villages named for a colour, each a dot in its colour")
legend_row(fig); credit(fig)
save(fig, "world")

# ---------------------------------------------------------------- 2. colour mix by language
L = pd.read_csv(f"{DATA}/by_language.csv")
L = L[L.n >= 300].copy()
L["dark"] = L.black_pct
L = L.sort_values("black_pct")
fig = plt.figure(figsize=(12, 7.4), facecolor=PAPER)
ax = fig.add_axes([0.3, 0.1, 0.62, 0.74]); ax.set_facecolor(PAPER)
for i, r in enumerate(L.itertuples()):
    x = 0
    for c in CL:
        v = getattr(r, c + "_pct")
        ax.barh(i, v, left=x, color=TINT[c], edgecolor=INK if c == "white" else EDGE[c], lw=0.6, height=0.72)
        if v >= 8:
            ax.text(x + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=9.5, color="#FFFDF6" if c in ("black", "red", "blue", "green", "grue") else INK)
        x += v
    ax.text(-1.5, i, f"{LANG_NAME[r.lang]}", ha="right", va="center", fontsize=11.5, color=INK)
    ax.text(101.5, i, f"{r.n:,}", ha="left", va="center", fontsize=9.5, color=MUT)
ax.set_xlim(0, 100); ax.set_ylim(-0.6, len(L) - 0.4); ax.set_yticks([]); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0", "25", "50", "75", "100%"])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
title(fig, "Each language has its favourite colour", "Share of each colour among a language's colour names (number of names at right), sorted by black")
legend_row(fig); credit(fig)
save(fig, "mix")

# ---------------------------------------------------------------- 3. by kind of place (languages weighted equally)
F = pd.read_csv(f"{DATA}/by_feature.csv")
fig = plt.figure(figsize=(12, 6.6), facecolor=PAPER)
ax = fig.add_axes([0.3, 0.11, 0.62, 0.72]); ax.set_facecolor(PAPER)
F = F.iloc[::-1].reset_index(drop=True)
for i, r in F.iterrows():
    x = 0
    tot = sum(r[c + "_eq"] for c in CL)
    for c in CL:
        v = 100 * r[c + "_eq"] / tot
        ax.barh(i, v, left=x, color=TINT[c], edgecolor=INK if c == "white" else EDGE[c], lw=0.6, height=0.72)
        if v >= 8:
            ax.text(x + v / 2, i, f"{v:.0f}", ha="center", va="center", fontsize=9.5, color="#FFFDF6" if c in ("black", "red", "blue", "green", "grue") else INK)
        x += v
    ax.text(-1.5, i, r.kind, ha="right", va="center", fontsize=11.5)
    ax.text(101.5, i, f"{int(r.n):,}", ha="left", va="center", fontsize=9.5, color=MUT)
ax.set_xlim(0, 100); ax.set_ylim(-0.6, len(F) - 0.4); ax.set_yticks([]); ax.set_xticks([0, 25, 50, 75, 100]); ax.set_xticklabels(["0", "25", "50", "75", "100%"])
for s in ("top", "right", "left"):
    ax.spines[s].set_visible(False)
title(fig, "Black rivers, white springs, red rocks", "Colour of the name by kind of place, each language with 30 or more such names weighted equally")
legend_row(fig); credit(fig)
save(fig, "kinds")

# ---------------------------------------------------------------- 4. three colour families
fig = plt.figure(figsize=(12, 5.4), facecolor=PAPER)
panels = [("The Turkic and Persian lands", (25, 95, 25, 55), ["tr", "fa"], "Kara, ak, siāh, sefid"),
          ("Latin America", (-118, -34, -56, 33), ["es", "pt"], "Negro, blanco, colorado, preto, branco"),
          ("China", (73, 135, 18, 54), ["zh"], "黑 hei, 白 bai, 红 hong, 黄 huang, 青 qing")]
for k, (t, ext, langs, w) in enumerate(panels):
    ax = fig.add_axes([0.01 + k * 0.33, 0.1, 0.32, 0.72])
    lat0 = (ext[2] + ext[3]) / 2
    pr = lambda lo, la, lat0=lat0: plate(lo, la, lat0)
    inkmap(ax, proj=pr, ext=ext, lw=0.5)
    sub = M[M.lang.isin(langs) & (M.lon.between(ext[0], ext[1])) & (M.lat.between(ext[2], ext[3]))]
    dots(ax, sub, proj=pr, s=1.6 if k != 2 else 0.9, lw=0.12)
    ax.set_title(t, fontproperties=HAND, fontsize=16, color=RED, pad=4)
    ax.text(0.5, -0.04, w, transform=ax.transAxes, ha="center", va="top", fontsize=10, color=MUT, fontproperties=FELL if k != 2 else None)
title(fig, "Three great colour families", None, y=0.975)
legend_row(fig, y=0.012, fs=10)
save(fig, "families")

# ---------------------------------------------------------------- 5. most common colour by country
big = BC[BC.n >= 30]
cmap = {r.cc: (TINT[r.top], 1) for r in big.itertuples()}
fig = plt.figure(figsize=(12, 6.6), facecolor=PAPER)
ax = fig.add_axes([0.01, 0.07, 0.98, 0.8])
inkmap(ax, ext=(-180, 180, -58, 84), countries=cmap, borders=True)
title(fig, "The most common colour in each country's place names", f"{R['countries']['with30']} countries with 30 or more colour names; pale ochre: fewer")
legend_row(fig, cols=["black", "white", "red", "green", "yellow"]); credit(fig)
save(fig, "countries")

# ---------------------------------------------------------------- 6. black against white
def bwcol(v):
    t = np.clip((np.log(max(v, 0.01)) + 2.3) / 4.6, 0, 1)
    a = np.array([0xFF, 0xFD, 0xF6]) / 255; b = np.array([0x2B, 0x21, 0x19]) / 255
    return tuple(a + (b - a) * t)
cm2 = {r.cc: (bwcol(r.black_white), 1) for r in big.itertuples()}
fig = plt.figure(figsize=(12, 6.6), facecolor=PAPER)
ax = fig.add_axes([0.01, 0.07, 0.98, 0.8])
inkmap(ax, ext=(-180, 180, -58, 84), countries=cm2, borders=True)
title(fig, "Black or white?", "Ratio of black to white colour names, countries with 30 or more")
cax = fig.add_axes([0.06, 0.05, 0.3, 0.025])
g = np.linspace(-2.3, 2.3, 200)
cax.imshow([[bwcol(np.exp(v)) for v in g]], aspect="auto", extent=(-2.3, 2.3, 0, 1)); cax.set_yticks([])
cax.set_xticks([-2.3, 0, 2.3]); cax.set_xticklabels(["10 white : 1 black", "even", "10 black : 1 white"], fontsize=9.5)
for s in cax.spines.values():
    s.set_edgecolor(INK)
credit(fig)
save(fig, "bw")

# ---------------------------------------------------------------- 7. red: revolution and earth
P, E = R["political"], R["earth"]
fig = plt.figure(figsize=(12, 5.4), facecolor=PAPER)
ax1 = fig.add_axes([0.08, 0.16, 0.36, 0.6]); ax2 = fig.add_axes([0.6, 0.16, 0.36, 0.6])
for ax in (ax1, ax2):
    ax.set_facecolor(PAPER); spines(ax)
vals = [("Russian, Ukrainian\nand Belarusian", P["eslav_red"], P["eslav"]), ("Chinese", P["zh_red"], P["zh"])]
for i, (n, tot, pol) in enumerate(vals):
    ax1.barh(i, tot - pol, color=TINT["red"], edgecolor=EDGE["red"], height=0.6)
    ax1.barh(i, pol, left=tot - pol, color="#F1C9BF", edgecolor=EDGE["red"], hatch="////", height=0.6)
    ax1.text(tot + 80, i, f"{100 * pol / tot:.0f}% revolutionary", va="center", fontsize=10.5)
ax1.set_yticks([0, 1]); ax1.set_yticklabels([v[0] for v in vals]); ax1.set_xlabel("red names")
ax1.set_xlim(0, max(v[1] for v in vals) * 1.45)
ax1.set_title("Red October, Red Flag, Red Star", fontproperties=HAND, fontsize=15, color=RED, loc="left")
ec = [(c, E[c]) for c in ("white", "yellow", "red", "black")]
ax2.bar(range(4), [v for _, v in ec], color=[TINT[c] for c, _ in ec], edgecolor=[INK if c == "white" else EDGE[c] for c, _ in ec], lw=1)
ax2.set_xticks(range(4)); ax2.set_xticklabels([CNAME[c] for c, _ in ec]); ax2.set_ylabel("names")
for i, (_, v) in enumerate(ec):
    ax2.text(i, v + 15, f"{v:,}", ha="center", fontsize=10)
ax2.set_title("Earth, soil and clay: not mostly red", fontproperties=HAND, fontsize=15, color=RED, loc="left")
title(fig, "Not every red is the colour of the ground", None, y=0.975)
credit(fig)
save(fig, "red")

# ---------------------------------------------------------------- 8. precision (paper only)
pr = pd.read_csv(f"{DATA}/precision.csv")
g = pr.groupby("lang").agg(s=("sampled", "sum"), c=("correct", "sum")).reset_index()
g["p"] = 100 * g.c / g.s
g = g.sort_values("p")
fig = plt.figure(figsize=(10, 5.4), facecolor=PAPER)
ax = fig.add_axes([0.3, 0.12, 0.64, 0.74]); ax.set_facecolor(PAPER); spines(ax)
ax.hlines(range(len(g)), 90, g.p, color=RULE, lw=2)
ax.scatter(g.p, range(len(g)), s=40, color=RED, zorder=3)
ax.set_yticks(range(len(g))); ax.set_yticklabels([f"{LANG_NAME[l]} ({s})" for l, s in zip(g.lang, g.s)], fontsize=10)
ax.set_xlim(90, 100.5); ax.set_xlabel("names judged correct in the review sample (%)")
title(fig, "Review samples by language", "Up to 50 names per colour and language, after tuning the rules", y=0.975)
fig.savefig(os.path.join(PA, "f_precision.png"), dpi=200, facecolor=PAPER); plt.close(fig)

# ---------------------------------------------------------------- header card 1200 x 630
fig = plt.figure(figsize=(12, 6.3), dpi=100, facecolor=PAPER)
ax = fig.add_axes([0.33, 0.04, 0.66, 0.92])
inkmap(ax, ext=(-170, 180, -56, 80), lw=0.4)
dots(ax, M, s=0.7)
fig.text(0.035, 0.86, "The colours", fontproperties=DISP, fontsize=40, color=INK, va="top")
fig.text(0.035, 0.74, "of the world's", fontproperties=HAND, fontsize=34, color=RED, va="top")
fig.text(0.035, 0.62, "place names", fontproperties=DISP, fontsize=40, color=INK, va="top")
fig.text(0.035, 0.44, f"{R['source']['main']:,} colour names\nin {R['source']['languages']} languages", fontsize=14, color=INK, va="top", linespacing=1.4)
fig.text(0.035, 0.28, f"{R['words']['river_black_eq']:.0f}% of rivers are black\n{R['words']['spring_white_eq']:.0f}% of springs are white", fontsize=14, color=RED, va="top", linespacing=1.4)
y = 0.1
hax = fig.add_axes([0, 0, 1, 1], zorder=10); hax.set_axis_off(); hax.set_xlim(0, 1); hax.set_ylim(0, 1)
for i, c in enumerate(["black", "white", "red", "green", "blue", "yellow"]):
    hax.scatter([0.045 + i * 0.04], [y], s=260, c=TINT[c], edgecolors=EDGE[c], linewidths=1.4)
fig.text(0.035, 0.03, "Dr Tristan Hotham · maps.tristanhotham.com/colour-names", fontsize=10, color=MUT)
fig.savefig(os.path.join(ROOT, "header.png"), dpi=100, facecolor=PAPER); plt.close(fig)
im = Image.open(os.path.join(ROOT, "header.png")); assert im.size == (1200, 630), im.size
print("figures done", sorted(os.listdir(BL)))
