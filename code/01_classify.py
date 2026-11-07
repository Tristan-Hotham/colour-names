"""Step 1: read the GeoNames candidates, apply the colour-word rules (rules.py) and write the accepted names.

Output: data/colour_places.csv, one row per place and colour (a few names carry two colours), with the GeoNames id,
name, coordinates, country, feature class and code, kind of place, colour, the matched word, the language and a flag
(political red, plant or animal name); and WORK/rejections.json, counts of the candidates turned down and why.
"""
import collections
import pandas as pd
from common import *
from rules import classify, classify_supp

d = pd.read_csv(CAND, sep="\t", names=COLS, quoting=3, dtype=str, keep_default_na=False)
assert len(d) == 185388, len(d)
d["lat"] = d.lat.astype(float); d["lon"] = d.lon.astype(float)
sp = pd.read_csv(SUPP, sep="\t", names=["tag"] + COLS, quoting=3, dtype=str, keep_default_na=False)
assert len(sp) == 67227, len(sp)
assert not set(sp.geonameid) & set(d.geonameid)
sp["lat"] = sp.lat.astype(float); sp["lon"] = sp.lon.astype(float)
d["tag"] = "first"
rows, why = [], collections.Counter()
why_tag = collections.Counter()
for r in pd.concat([d, sp]).to_dict("records"):
    hits, reason = classify(r) if r["tag"] == "first" else classify_supp(r["tag"], r)
    if not hits:
        why[reason] += 1
        why_tag[r["tag"]] += 1
        continue
    for h in hits:
        rows.append({"geonameid": int(r["geonameid"]), "name": r["name"], "asciiname": r["asciiname"],
                     "lat": round(r["lat"], 5), "lon": round(r["lon"], 5), "cc": r["cc"], "fclass": r["fclass"],
                     "fcode": r["fcode"], "ftype": ftype(r["fclass"], r["fcode"]) or "", "colour": h["colour"],
                     "word": h["word"], "lang": h["lang"], "flag": h["flag"], "n_colours": len(hits),
                     "pop": int(r["pop"] or 0), "src": r["tag"]})
P = pd.DataFrame(rows)
P.to_csv(f"{WORK}/accepted_all.csv", index=False)
jsave({"candidates": len(d), "supplement": len(sp), "supp_by_tag": sp.tag.value_counts().to_dict(), "rejected_by_tag": dict(why_tag), "rejected": dict(why), "accepted_rows": len(P), "accepted_places": int(P.geonameid.nunique())},
      f"{WORK}/rejections.json", indent=1)
print(len(d) + len(sp), "candidates;", P.geonameid.nunique(), "places accepted;", len(P), "place-colour rows;", dict(why))
print(P.groupby(["lang", "colour"]).size().unstack(fill_value=0))
print(P.ftype.value_counts())
