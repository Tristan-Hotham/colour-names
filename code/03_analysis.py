"""Step 3: the analysis. Reads WORK/accepted_all.csv (step 1) and data/precision.csv (step 2) and writes the derived
data and the numbers that go into results.json (step 4 assembles results.json; this step writes WORK/analysis.json).

Main set: natural features and settlements (feature classes H, T, V, P and the natural L codes), without names taken
from a plant or animal (flag "species"). Revolutionary red (flag "political") stays in the main set as red, and is
also counted on its own.
Outputs: data/colour_places.csv (every accepted name, with an in_main column), data/by_country.csv,
data/by_language.csv, data/by_feature.csv, data/grid_2deg.csv, WORK/analysis.json.
"""
import collections
import numpy as np
import pandas as pd
from common import *

A = pd.read_csv(f"{WORK}/accepted_all.csv", keep_default_na=False)
A["in_main"] = ((A.ftype != "") & (A.flag != "species")).astype(int)
out = A[["geonameid", "name", "lat", "lon", "cc", "fclass", "fcode", "ftype", "colour", "word", "lang", "flag", "in_main", "src"]]
out.to_csv(f"{DATA}/colour_places.csv", index=False)
M = A[A.in_main == 1].copy()
Z = {}
rej = jload(f"{WORK}/rejections.json")
Z["source"] = {"candidates": rej["candidates"] + rej["supplement"], "candidates_first": rej["candidates"], "accepted_rows": int(len(A)), "accepted_places": int(A.geonameid.nunique()),
               "rejected": int(sum(rej["rejected"].values())), "rejected_by": rej["rejected"],
               "excluded_kind": int(((A.ftype == "")).sum()), "species": int(((A.ftype != "") & (A.flag == "species")).sum()),
               "main": int(len(M)), "main_places": int(M.geonameid.nunique()), "countries": int(M.cc.nunique()),
               "languages": int(M.lang.nunique()), "multi_colour_places": int(M[M.n_colours > 1].geonameid.nunique())}
Z["source"]["excluded_buildings"] = int(A[A.fclass.isin(["S", "R"])].shape[0])

# ---- precision
pr = pd.read_csv(f"{DATA}/precision.csv")
Z["precision"] = {"sampled": int(pr.sampled.sum()), "correct": int(pr.correct.sum()),
                  "overall": round(pr.correct.sum() / pr.sampled.sum(), 3),
                  "weighted": round(float((pr.precision * pr.accepted).sum() / pr.accepted.sum()), 3),
                  "cells": int(len(pr)), "min_cell": round(float(pr[pr.sampled >= 20].precision.min()), 3),
                  "by_lang": {l: round(g.correct.sum() / g.sampled.sum(), 3) for l, g in pr.groupby("lang")}}
seen = set(int(x) for x in open(os.path.join(ROOT, "code", "review_seen.txt")).read().split())
Z["precision"]["names_read"] = len(seen)
ps = pd.read_csv(f"{DATA}/precision_supplement.csv")
Z["precision_supp"] = {"sampled": int(ps.sampled.sum()), "correct": int(ps.correct.sum()), "overall": round(ps.correct.sum() / ps.sampled.sum(), 3),
                       "by_rule": {r.src: {"accepted": int(r.accepted), "sampled": int(r.sampled), "correct": int(r.correct), "precision": float(r.precision)} for r in ps.itertuples()}}
Z["supplement"] = {"rows": rej["supplement"], "by_tag": rej["supp_by_tag"], "main": int((M.src != "first").sum()),
                   "main_by_tag": {k: int(v) for k, v in M[M.src != "first"].src.value_counts().items()}}

# ---- colours overall and by language
Z["colour"] = {c: int((M.colour == c).sum()) for c in COLOURS}
Z["colour_pct"] = {c: round(100 * v / len(M), 1) for c, v in Z["colour"].items()}
L = M.groupby(["lang", "colour"]).size().unstack(fill_value=0).reindex(columns=COLOURS, fill_value=0)
L["n"] = L.sum(axis=1)
for c in COLOURS:
    L[c + "_pct"] = (100 * L[c] / L.n).round(1)
L["top"] = L[COLOURS].idxmax(axis=1)
L["black_white"] = (L.black / L.white.replace(0, np.nan)).round(2)
L.reset_index().assign(language=lambda x: x.lang.map(LANG_NAME)).to_csv(f"{DATA}/by_language.csv", index=False)
Z["lang"] = {l: {"n": int(r.n), "top": r.top, **{c: float(r[c + "_pct"]) for c in COLOURS}, "black_white": None if pd.isna(r.black_white) else float(r.black_white)}
             for l, r in L.iterrows()}
# without Chinese and Japanese (whose settlement lists dominate the counts)
W = M[~M.lang.isin(["zh", "ja"])]
Z["colour_pct_nozhja"] = {c: round(100 * (W.colour == c).mean(), 1) for c in COLOURS}
Z["n_nozhja"] = int(len(W))

# ---- by kind of place: share of each colour, all languages pooled and languages weighted equally
F = M.groupby(["ftype", "colour"]).size().unstack(fill_value=0).reindex(columns=COLOURS, fill_value=0)
F["n"] = F.sum(axis=1)
rows = []
for ft, _ in FTYPES:
    r = {"ftype": ft, "kind": FT_NAME[ft], "n": int(F.loc[ft, "n"])}
    for c in COLOURS:
        r[c + "_pct"] = round(100 * F.loc[ft, c] / F.loc[ft, "n"], 1)
    # equal weight to each language with at least 30 names of this kind (so Chinese villages do not swamp it)
    g = M[M.ftype == ft].groupby("lang")
    shares = [gg.colour.value_counts(normalize=True) for l, gg in g if len(gg) >= 30]
    eq = pd.concat(shares, axis=1).fillna(0).mean(axis=1) if shares else pd.Series(dtype=float)
    for c in COLOURS:
        r[c + "_eq"] = round(100 * float(eq.get(c, 0)), 1)
    r["langs_eq"] = len(shares)
    rows.append(r)
FT = pd.DataFrame(rows)
FT.to_csv(f"{DATA}/by_feature.csv", index=False)
Z["ftype"] = {r["ftype"]: r for r in rows}
nat = M[M.ftype != "settlement"]
Z["natural"] = {"n": int(len(nat)), **{c: round(100 * (nat.colour == c).mean(), 1) for c in COLOURS}}
st = M[M.ftype == "settlement"]
Z["settlement"] = {"n": int(len(st)), **{c: round(100 * (st.colour == c).mean(), 1) for c in COLOURS}}
# black against white in each kind, languages weighted equally
Z["bw_by_ftype"] = {r["ftype"]: round(r["black_eq"] / r["white_eq"], 2) if r["white_eq"] else None for r in rows}
# which kind of place is most often black, white, red ... (equal-weight share)
Z["kind_most"] = {c: max(rows, key=lambda r: r[c + "_eq"])["ftype"] for c in COLOURS if c != "grue"}

# ---- language by kind for the headline pairs (rivers black, mountains white)
def share(df, c):
    return round(100 * (df.colour == c).mean(), 1) if len(df) else None
LK = {}
for l in LANGS:
    g = M[M.lang == l]
    if len(g) < 200:
        continue
    LK[l] = {ft: {"n": int((g.ftype == ft).sum()), **{c: share(g[g.ftype == ft], c) for c in COLOURS}} for ft, _ in FTYPES}
Z["lang_ftype"] = LK
riv_black = {l: v["river"]["black"] for l, v in LK.items() if v["river"]["n"] >= 50}
mt_white = {l: v["mountain"]["white"] for l, v in LK.items() if v["mountain"]["n"] >= 50}
lang_black = {l: Z["lang"][l]["black"] for l in riv_black}
lang_white = {l: Z["lang"][l]["white"] for l in mt_white}
Z["rivers_blacker"] = {"langs": len(riv_black), "blacker": sum(riv_black[l] > lang_black[l] for l in riv_black)}
Z["mountains_whiter"] = {"langs": len(mt_white), "whiter": sum(mt_white[l] > lang_white[l] for l in mt_white)}

# ---- the great families
def cnt(q):
    return int(len(q))
es_pt_riv = M[M.lang.isin(["es", "pt"]) & (M.ftype == "river")]
tr = M[M.lang == "tr"]
zh = M[M.lang == "zh"]
de = M[M.lang == "de"]
Z["families"] = {
    "iberian_river_black": cnt(es_pt_riv[es_pt_riv.colour == "black"]), "iberian_river_white": cnt(es_pt_riv[es_pt_riv.colour == "white"]),
    "iberian_river_red": cnt(es_pt_riv[es_pt_riv.colour == "red"]), "iberian_river_n": cnt(es_pt_riv),
    "rio_negro": cnt(M[M.name.str.contains(r"^R[íi]o Negro$", regex=True)]), "rio_preto": cnt(M[M.name.str.contains(r"^R[íi]o Pr[eê]to$", regex=True)]),
    "rio_blanco": cnt(M[M.name.str.contains(r"^R[íi]o Blanco$", regex=True)]), "rio_branco": cnt(M[M.name.str.contains(r"^R[íi]o Branco$", regex=True)]),
    "cerro_colorado": cnt(M[M.name.str.contains(r"^Cerro Colorado$", regex=True)]), "cerro_blanco": cnt(M[M.name.str.contains(r"^Cerro Blanco$", regex=True)]),
    "cerro_negro": cnt(M[M.name.str.contains(r"^Cerro Negro$", regex=True)]),
    "tr_kara": cnt(tr[tr.colour == "black"]), "tr_ak": cnt(tr[tr.colour == "white"]), "tr_n": cnt(tr),
    "tr_kara_ak_pct": round(100 * cnt(tr[tr.colour.isin(["black", "white"])]) / max(1, cnt(tr)), 1),
    "tr_su": cnt(M[(M.lang == "tr") & M.name.str.contains(r"\b(?:Kara|Ak|Aq|Qara)[- ]?(?:Su|Suu|Suyu)\b", regex=True)]),
    "zh_hei": cnt(zh[zh.colour == "black"]), "zh_bai": cnt(zh[zh.colour == "white"]), "zh_huang": cnt(zh[zh.colour == "yellow"]),
    "zh_hong": cnt(zh[zh.colour == "red"]), "zh_qing": cnt(zh[zh.colour == "grue"]), "zh_n": cnt(zh),
    "de_schwarz": cnt(de[de.colour == "black"]), "de_weiss": cnt(de[de.colour == "white"]), "de_rot": cnt(de[de.colour == "red"]), "de_n": cnt(de),
    "fa_siah": cnt(M[(M.lang == "fa") & (M.colour == "black")]), "fa_n": cnt(M[M.lang == "fa"]),
    "nord_svart": cnt(M[(M.lang == "nord") & (M.colour == "black")]), "nord_n": cnt(M[M.lang == "nord"]),
}
# ---- revolutionary red
pol = M[M.flag == "political"]
Z["political"] = {"n": int(len(pol)), "eslav": int((pol.lang == "eslav").sum()), "zh": int((pol.lang == "zh").sum()),
                  "eslav_red": int(((M.lang == "eslav") & (M.colour == "red")).sum()), "zh_red": int(((M.lang == "zh") & (M.colour == "red")).sum())}
Z["political"]["eslav_pct"] = round(100 * Z["political"]["eslav"] / Z["political"]["eslav_red"], 1)
Z["political"]["zh_pct"] = round(100 * Z["political"]["zh"] / Z["political"]["zh_red"], 1)
Z["political"]["eslav_red_pct"] = Z["lang"]["eslav"]["red"]
Z["political"]["eslav_red_pct_without"] = round(100 * (Z["political"]["eslav_red"] - Z["political"]["eslav"]) / (Z["lang"]["eslav"]["n"] - Z["political"]["eslav"]), 1)

# ---- red earth: red names of soil, clay and earth
EARTH = r"\b(?:Tierras?|Terras?|Terre|Barro|Barros|Barreiro|Barrial|Glina|Glinka|Gliny|Khak|Khāk|Gel|Zemlja|Zemja|Erde|Kum|Toprak)\b"
red = M[M.colour == "red"]
earth = red[red.name.str.contains(EARTH, regex=True) | red.name.str.contains(r"Krasnaya Glina|Krasnoglin|Krasnozem", regex=True)]
alt = pd.read_csv(CAND, sep="\t", names=COLS, quoting=3, dtype=str, keep_default_na=False, usecols=[0, 3])
alt["gid"] = alt.geonameid.astype(int)
zhred = set(alt[alt.alternatenames.str.contains("红土|紅土|红泥|紅泥|赤土|红壤")].gid)
earth_zh = red[red.geonameid.isin(zhred)]
E = pd.concat([earth, earth_zh]).drop_duplicates("geonameid")
E_all = pd.concat([M[M.name.str.contains(EARTH, regex=True)], M[M.geonameid.isin(set(alt[alt.alternatenames.str.contains("土|泥")].gid)) & (M.lang == "zh")]]).drop_duplicates(["geonameid", "colour"])
Z["earth"] = {"n": int(len(E_all)), "red": int((E_all.colour == "red").sum()), "red_pct": round(100 * (E_all.colour == "red").mean(), 1),
              "black": int((E_all.colour == "black").sum()), "white": int((E_all.colour == "white").sum()), "yellow": int((E_all.colour == "yellow").sum()),
              "by_lang": {l: int(n) for l, n in E[E.colour == "red"].lang.value_counts().items()}}
Z["earth"]["red_vs_all_pct"] = Z["colour_pct"]["red"]
M["earth"] = M.geonameid.isin(set(E_all.geonameid)).astype(int)

# ---- countries
N = M.groupby("cc").colour.value_counts().unstack(fill_value=0).reindex(columns=COLOURS, fill_value=0)
N["n"] = N.sum(axis=1)
N["top"] = N[COLOURS].idxmax(axis=1)
N["top_pct"] = (100 * N[COLOURS].max(axis=1) / N.n).round(1)
N["second"] = N[COLOURS].apply(lambda r: r.sort_values(ascending=False).index[1], axis=1)
N["black_white"] = ((N.black + 0.5) / (N.white + 0.5)).round(2)
N["main_lang"] = M.groupby("cc").lang.agg(lambda s: s.value_counts().index[0])
ne = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
cname = {}
for f in ne["features"]:
    p = f["properties"]
    for k in ("ISO_A2_EH", "ISO_A2"):
        if p.get(k) and p[k] != "-99":
            cname.setdefault(p[k], p["NAME"])
cname.update({"XK": "Kosovo", "AQ": "Antarctica"})
N["country"] = [cname.get(c, c) for c in N.index]
N = N.sort_values("n", ascending=False)
N.reset_index().to_csv(f"{DATA}/by_country.csv", index=False)
big = N[N.n >= 30]
Z["countries"] = {"n": int(len(N)), "with30": int(len(big)), "top_count": {c: int((big.top == c).sum()) for c in COLOURS},
                  "most": {cc: {"cc": cc, "country": big.loc[cc, "country"], "n": int(big.loc[cc, "n"])} for cc in big.index[:12]},
                  "bw_blackest": [[cc, big.loc[cc, "country"], float(big.loc[cc, "black_white"])] for cc in big[big.n >= 100].black_white.sort_values(ascending=False).head(8).index],
                  "bw_whitest": [[cc, big.loc[cc, "country"], float(big.loc[cc, "black_white"])] for cc in big[big.n >= 100].black_white.sort_values().head(8).index],
                  "black_majority": int((big.black > big.white).sum()), "white_majority": int((big.white > big.black).sum())}
Z["country"] = {cc: {"country": r.country, "n": int(r.n), "top": r.top, "top_pct": float(r.top_pct), "black_white": float(r.black_white),
                     **{c: int(r[c]) for c in COLOURS}} for cc, r in big.iterrows()}

# ---- 2 degree grid: hotspots (count per cell) and the leading colour
M["gx"] = np.floor(M.lon / 2).astype(int) * 2
M["gy"] = np.floor(M.lat / 2).astype(int) * 2
G = M.groupby(["gx", "gy"]).colour.value_counts().unstack(fill_value=0).reindex(columns=COLOURS, fill_value=0)
G["n"] = G.sum(axis=1)
G["top"] = G[COLOURS].idxmax(axis=1)
G.reset_index().to_csv(f"{DATA}/grid_2deg.csv", index=False)
hot = {}
for c in COLOURS:
    if c == "grue":
        continue
    s = G[c].sort_values(ascending=False).head(1)
    (gx, gy), v = s.index[0], int(s.iloc[0])
    sub = M[(M.gx == gx) & (M.gy == gy) & (M.colour == c)]
    hot[c] = {"lon": gx + 1, "lat": gy + 1, "n": v, "cc": sub.cc.value_counts().index[0], "country": cname.get(sub.cc.value_counts().index[0], ""),
              "lang": sub.lang.value_counts().index[0]}
Z["hotspots"] = hot
Z["grid"] = {"cells": int(len(G)), "max": int(G.n.max())}

# ---- the most repeated colour names
top_names = M.groupby(["name", "colour", "lang"]).size().sort_values(ascending=False).head(25)
Z["top_names"] = [[n, c, l, int(v)] for (n, c, l), v in top_names.items()]
jsave(Z, f"{WORK}/analysis.json", indent=1)
M[["geonameid", "name", "lat", "lon", "cc", "fcode", "ftype", "colour", "word", "lang", "flag", "earth"]].to_csv(f"{WORK}/main.csv", index=False)
print(json.dumps({k: nonan(Z[k]) for k in ("source", "colour_pct", "colour_pct_nozhja", "natural", "settlement", "bw_by_ftype", "kind_most", "rivers_blacker", "mountains_whiter", "families", "political", "earth", "hotspots")}, indent=0, ensure_ascii=False)[:6000])
print(FT.to_string())
print(N.head(30)[["country", "n", "top", "top_pct", "black_white"]].to_string())
print(Z["countries"]["top_count"], Z["countries"]["bw_blackest"], Z["countries"]["bw_whitest"])
print(Z["top_names"])
