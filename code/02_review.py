"""Step 2: review samples. Draws up to 50 accepted names per colour and language (the main set: natural features and
settlements), in a fixed order (an MD5 hash of the GeoNames id), and joins my verdicts from code/review_verdicts.tsv.

Each sample was read by eye: a name is a false positive when the matched word is not the colour there (a surname, a
saint, another word that looks the same, a name taken from a state or a person). The verdict file lists only the
false positives, by GeoNames id and colour, with the reason; every other sampled name was judged correct.
Output: data/review_sample.csv (every sampled name with its verdict) and data/precision.csv (per language and colour).
With --print, writes the samples to WORK/review_print.txt for reading.
"""
import hashlib, re, sys
import pandas as pd
from common import *
from rules import native_name

P = pd.read_csv(f"{WORK}/accepted_all.csv", keep_default_na=False)
P = P[(P.ftype != "") & (P.flag != "species")].copy()
Q = P[P.src != "first"].copy()          # the supplement: reviewed by rule, below
P = P[P.src == "first"].copy()
P["h"] = P.geonameid.map(lambda g: hashlib.md5(str(g).encode()).hexdigest())
S = P.sort_values("h").groupby(["lang", "colour"]).head(50).sort_values(["lang", "colour", "h"])
if "--print" in sys.argv:
    alt = pd.read_csv(CAND, sep="\t", names=COLS, quoting=3, dtype=str, keep_default_na=False, usecols=[0, 1, 3, 8])
    alt["gid"] = alt.geonameid.astype(int)
    alt = alt[alt.gid.isin(S[S.lang.isin(["zh", "ja"])].geonameid)].set_index("gid")
    with open(f"{WORK}/review_print.txt", "w") as f:
        for (l, c), g in S.groupby(["lang", "colour"], sort=False):
            f.write(f"## {l} {c} ({len(g)})\n")
            out = []
            seen = set(int(x) for x in open(os.path.join(ROOT, "code", "review_seen.txt")).read().split())
            for r in g.itertuples():
                if "--new" in sys.argv and r.geonameid in seen:
                    continue
                nm = r.name
                if l in ("zh", "ja"):
                    nm = native_name(alt.loc[r.geonameid, "alternatenames"], r.name, r.cc) + " " + r.name
                out.append(f"{r.geonameid}:{nm}[{r.cc} {r.fcode}]")
            f.write(" | ".join(out) + "\n")
    print("printed", len(S))
V = pd.read_csv(os.path.join(ROOT, "code", "review_verdicts.tsv"), sep="\t", comment="#", dtype={"geonameid": int})
fp = {(r.geonameid, r.colour): r.reason for r in V.itertuples()}
S["correct"] = [0 if (g, c) in fp else 1 for g, c in zip(S.geonameid, S.colour)]
S["reason"] = [fp.get((g, c), "") for g, c in zip(S.geonameid, S.colour)]
unused = set(fp) - set(zip(S.geonameid, S.colour))
print("verdicts no longer in the sample (rules now reject them):", len(unused))
seen = set(int(x) for x in open(os.path.join(ROOT, "code", "review_seen.txt")).read().split())
assert set(S.geonameid) <= seen, len(set(S.geonameid) - seen)
S[["lang", "colour", "geonameid", "name", "cc", "fcode", "word", "correct", "reason"]].to_csv(f"{DATA}/review_sample.csv", index=False)
n = P.groupby(["lang", "colour"]).size().rename("accepted")
pr = S.groupby(["lang", "colour"]).agg(sampled=("correct", "size"), correct=("correct", "sum")).join(n).reset_index()
pr["precision"] = (pr.correct / pr.sampled).round(3)
pr.to_csv(f"{DATA}/precision.csv", index=False)
print(len(S), "sampled;", int(S.correct.sum()), "correct;", f"{S.correct.mean():.3f}")
print(pr[pr.precision < 0.9].to_string())

# ---- the supplement: 50 names per rule (tag), in the same hash order
Q["h"] = Q.geonameid.map(lambda g: hashlib.md5(str(g).encode()).hexdigest())
SQ = Q.sort_values("h").groupby("src").head(50).sort_values(["src", "h"])
if "--print-supp" in sys.argv:
    alt = pd.read_csv(SUPP, sep="\t", names=["tag"] + COLS, quoting=3, dtype=str, keep_default_na=False, usecols=[1, 4])
    alt["gid"] = alt.geonameid.astype(int); alt = alt[alt.gid.isin(SQ.geonameid)].set_index("gid")
    with open(f"{WORK}/review_supp_print.txt", "w") as f:
        for t, g in SQ.groupby("src"):
            f.write(f"## {t} ({len(g)})\n")
            out = []
            for r in g.itertuples():
                a = alt.loc[r.geonameid, "alternatenames"] if t == "korean" else ""
                ko = " ".join(x for x in a.split(",") if re.search(r"[\u4e00-\u9fff\uac00-\ud7a3]", x))[:30]
                out.append(f"{r.geonameid}:{r.name} {ko}[{r.cc} {r.fcode} {r.colour}]")
            f.write(" | ".join(out) + "\n")
V2 = pd.read_csv(os.path.join(ROOT, "code", "review_verdicts_supp.tsv"), sep="\t", comment="#", dtype={"geonameid": int})
fp2 = {(r.geonameid, r.colour): r.reason for r in V2.itertuples()}
SQ["correct"] = [0 if (g, c) in fp2 else 1 for g, c in zip(SQ.geonameid, SQ.colour)]
SQ["reason"] = [fp2.get((g, c), "") for g, c in zip(SQ.geonameid, SQ.colour)]
SQ[["src", "lang", "colour", "geonameid", "name", "cc", "fcode", "word", "correct", "reason"]].to_csv(f"{DATA}/review_supplement.csv", index=False)
ps = SQ.groupby("src").agg(sampled=("correct", "size"), correct=("correct", "sum")).join(Q.groupby("src").size().rename("accepted")).reset_index()
ps["precision"] = (ps.correct / ps.sampled).round(3)
ps.to_csv(f"{DATA}/precision_supplement.csv", index=False)
print(ps.to_string())
