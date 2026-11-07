"""Step 4: data/results.json (every number quoted anywhere) and the page data.

Page data: data/points.json (every name of the main set: position, colour, language, kind, country, name, matched
word, flag, GeoNames id; loaded after the map has drawn) and data/countries.json (Natural Earth 1:50m outlines,
simplified, with each country's colour counts, most common colour and black to white ratio).
"""
import pandas as pd
from shapely.geometry import shape, mapping
from common import *

Z = jload(f"{WORK}/analysis.json")
R = dict(Z)
R["meta"] = {"slug": SLUG, "page": PAGE, "repo": REPO, "geonames": GEONAMES_URL, "doi": "10.5281/zenodo.24043682", "year": 2026}
# shares quoted in round numbers in the text
f = Z["ftype"]
R["words"] = {
    "river_black_eq": f["river"]["black_eq"], "river_white_eq": f["river"]["white_eq"],
    "spring_white_eq": f["spring"]["white_eq"], "mountain_white_eq": f["mountain"]["white_eq"], "mountain_black_eq": f["mountain"]["black_eq"],
    "mountain_red_eq": f["mountain"]["red_eq"], "settlement_yellow": f["settlement"]["yellow_pct"],
}
fam = Z["families"]
R["families"]["iberian_river_black_pct"] = round(100 * fam["iberian_river_black"] / fam["iberian_river_n"], 1)
R["families"]["iberian_river_white_pct"] = round(100 * fam["iberian_river_white"] / fam["iberian_river_n"], 1)
R["families"]["zh_white_yellow_pct"] = round(100 * (fam["zh_bai"] + fam["zh_huang"]) / fam["zh_n"], 1)
R["families"]["nord_svart_pct"] = round(100 * fam["nord_svart"] / fam["nord_n"], 1)
R["families"]["fa_siah_pct"] = round(100 * fam["fa_siah"] / fam["fa_n"], 1)
tn = {(n, c): v for n, c, l, v in Z["top_names"]}
R["families"]["kuh_siah"] = tn[("Kūh-e Sīāh", "black")]
R["families"]["tierra_blanca"] = tn[("Tierra Blanca", "white")]
R["families"]["karasu"] = tn[("Karasu", "black")]
R["precision"]["overall_pct"] = round(100 * Z["precision"]["overall"])
R["first_pass"] = {"names_read": Z["precision"]["names_read"]}
V = pd.read_csv(os.path.join(ROOT, "code", "review_verdicts.tsv"), sep="\t", comment="#")
S = pd.read_csv(f"{DATA}/review_sample.csv")
R["precision"]["false_listed"] = int(len(V))
R["precision"]["false_in_sample"] = int((S.correct == 0).sum())
jsave(R, f"{DATA}/results.json", indent=1)

# ---- page data
M = pd.read_csv(f"{WORK}/main.csv", keep_default_na=False)
CI = {c: i for i, c in enumerate(COLOURS)}
LI = {l: i for i, l in enumerate(LANGS)}
FI = {k: i for i, (k, _) in enumerate(FTYPES)}
ccs = sorted(M.cc.unique())
KI = {c: i for i, c in enumerate(ccs)}
FL = {"": 0, "political": 1}
M = M.sample(frac=1, random_state=7)   # a random drawing order, so no colour is always on top
pts = [[int(round(r.lon * 1e4)), int(round(r.lat * 1e4)), CI[r.colour], LI[r.lang], FI[r.ftype], KI[r.cc], r.name, r.word, FL[r.flag], int(r.geonameid), int(r.earth)]
       for r in M.itertuples()]
bc = pd.read_csv(f"{DATA}/by_country.csv", keep_default_na=False)
cname = dict(zip(bc.cc, bc.country))
jsave({"colours": COLOURS, "cname": CNAME, "tint": TINT, "edge": EDGE, "langs": LANGS, "lang_name": LANG_NAME, "words": WORDS,
       "ftypes": [k for k, _ in FTYPES], "ftype_name": FT_NAME, "ccs": ccs, "country": [cname.get(c, c) for c in ccs],
       "fields": ["lonE4", "latE4", "colour", "lang", "kind", "country", "name", "word", "political", "geonameid", "earth"], "p": pts},
      f"{DATA}/points.json")
ne = jload(f"{GEO}/ne_50m_admin_0_countries.geojson")
by = {r.cc: r for r in bc.itertuples()}
feats = []
for ft in ne["features"]:
    p = ft["properties"]
    cc = p["ISO_A2_EH"] if p.get("ISO_A2_EH") not in (None, "-99") else p.get("ISO_A2")
    g = shape(ft["geometry"]).simplify(0.04, preserve_topology=True)
    q = {"cc": cc, "name": p["NAME"]}
    r = by.get(cc)
    if r is not None:
        q.update({"n": int(r.n), "top": r.top if r.n >= 30 else "", "bw": float(r.black_white) if r.n >= 30 else None,
                  **{c: int(getattr(r, c)) for c in COLOURS}})
    gj = mapping(g)
    def rnd(c):
        return [rnd(x) for x in c] if isinstance(c[0], (list, tuple)) else [round(c[0], 3), round(c[1], 3)]
    feats.append({"type": "Feature", "properties": q, "geometry": {"type": gj["type"], "coordinates": rnd(gj["coordinates"])}})
jsave({"type": "FeatureCollection", "features": feats}, f"{DATA}/countries.json")
print("results", len(json.dumps(R)), "points", len(pts), os.path.getsize(f"{DATA}/points.json") // 1024, "KB; countries", os.path.getsize(f"{DATA}/countries.json") // 1024, "KB")
