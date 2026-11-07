"""Step 7: the paper. Fills code/paper_template.tex from data/results.json, adds tables and compiles with xelatex.
Output: release/paper/Hotham_Colour_Names.pdf and .tex, beside the f_*.png figures. The DOI stays as 10.5281/zenodo.24043682."""
import subprocess
import pandas as pd
from common import *

R = jload(f"{DATA}/results.json")
OUT = os.path.join(ROOT, "release", "paper"); NAME = "Hotham_Colour_Names"
tex = lambda s: str(s).replace("\\", "").replace("&", "\\&").replace("%", "\\%").replace("_", "\\_").replace("#", "\\#").replace("$", "\\$")
cjk = lambda s: re.sub(r"([\u3040-\u30ff\u4e00-\u9fff]+)", r"{\\cjk \1}", s)

# statements made in words in the paper
L = R["lang"]
big = {l: v for l, v in L.items() if v["n"] >= 300}
assert all(v["black"] + v["white"] + v["red"] > 50 for v in big.values())
six = ["black", "white", "red", "green", "blue", "yellow"]
for l, v in big.items():
    assert sorted(six, key=lambda c: v[c]).index("blue") <= 2, l
LF = R["lang_ftype"]
whiter = sorted(l for l in LF if LF[l]["mountain"]["n"] >= 50 and LF[l]["mountain"]["white"] > L[l]["white"])
assert whiter == sorted(["zh", "ja", "mn", "nl", "eslav", "nord", "fr"]), whiter
assert all(LF[l]["mountain"]["white"] < L[l]["white"] for l in ("es", "de", "en", "fa", "tr"))
assert R["country"]["IN"]["black_white"] > 10 and R["country"]["PK"]["black_white"] > 10 and R["country"]["MN"]["top"] == "white"
assert R["lang"]["mn"]["white"] > R["lang"]["mn"]["black"] > R["lang"]["mn"]["red"] > max(R["lang"]["mn"][c] for c in ("green", "blue", "yellow"))
assert R["kind_most"]["red"] == "rock" and R["hotspots"]["green"]["cc"] == "NO" and R["hotspots"]["blue"]["cc"] == "NO"
assert R["countries"]["with30"] >= 97
for cc, c in (("BY", "red"), ("CN", "yellow"), ("SE", "black"), ("FI", "black"), ("RS", "white")):
    assert R["country"][cc]["top"] == c, cc


def tfmt(v, f):
    if f == "int": return f"{int(round(float(v))):,}"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    return tex(str(v))


F = pd.read_csv(f"{DATA}/by_feature.csv")
rows = "".join(f"{tex(r.kind)} & {int(r.n):,} & " + " & ".join(f"{r[c + '_eq']:.1f}" for c in COLOURS) + "\\\\\n" for _, r in F.iterrows())
TK = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Colour by kind of place: names in the main set, and the share of each colour (\\%) with languages weighted equally. BG: blue-green.}\\label{tab:kinds}"
      "\\begin{tabular}{lrrrrrrrr}\\toprule Kind & Names & Black & White & Red & Green & Blue & Yellow & BG\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
B = pd.read_csv(f"{DATA}/by_language.csv")
pr = R["precision"]["by_lang"]
rows = "".join(f"{tex(LANG_NAME[r.lang])} & {int(r.n):,} & " + " & ".join(f"{r[c + '_pct']:.0f}" for c in COLOURS) + f" & {100 * pr.get(r.lang, float('nan')):.0f}\\\\\n" for _, r in B.sort_values("n", ascending=False).iterrows())
TL = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{Colour names by language: names in the main set, share of each colour (\\%) and the share of review-sample names judged correct (\\%).}\\label{tab:langs}"
      "\\begin{tabular}{lrrrrrrrrr}\\toprule Language & Names & Black & White & Red & Green & Blue & Yellow & BG & Correct\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
AREA = {"en": "anywhere", "es": "anywhere outside the Portuguese and Italian areas; in the US, Canada and Australia only with a Spanish word beside it",
        "pt": "Brazil, Portugal, Angola, Mozambique, Cape Verde and other Lusophone countries", "fr": "anywhere", "it": "Italy, San Marino, Switzerland",
        "ro": "Romania, Moldova", "de": "Germany, Austria, Switzerland, Liechtenstein, Luxembourg, Italy, Belgium, Namibia",
        "nl": "Netherlands, Belgium, Suriname, the Dutch Caribbean, South Africa, Namibia", "nord": "Norway, Sweden, Denmark, Finland, Iceland, the Faroes, Greenland",
        "pl": "Poland", "eslav": "the former Soviet Union and Mongolia", "sslav": "Bulgaria, Serbia, North Macedonia, Bosnia, Montenegro, Kosovo",
        "tr": "Turkey, the Caucasus, Central Asia, Russia, Iran, Afghanistan, China, Mongolia and the Balkans", "ar": "the Arab world, Chad, Mali, Niger, Iran, Turkey (with an Arabic word beside it)",
        "fa": "Iran, Afghanistan, Tajikistan, Pakistan", "mn": "Mongolia, Inner Mongolia, Buryatia, Kalmykia, Tuva", "hi": "India, Pakistan, Nepal, Bangladesh (beside a landscape word)",
        "ko": "South and North Korea (hanja, or unambiguous hangul compounds)", "zh": "China, Taiwan, Hong Kong, Macau (characters)", "ja": "Japan (characters)"}
rows = "".join(f"{tex(LANG_NAME[l])} & {cjk(tex('; '.join(f'{c}: {w}' for c, w in WORDS[l].items() if w)))} & {tex(AREA[l])}\\\\\n" for l in LANGS)
TR_ = ("{\\footnotesize\\setlength{\\tabcolsep}{4pt}\\begin{longtable}{p{2.6cm}p{6.6cm}p{5.4cm}}\\caption{Colour words (dictionary forms; inflected and compound forms are also matched) and the countries where each rule applies.}\\label{tab:rules}\\\\"
       "\\toprule Language & Words & Where\\\\\\midrule\\endfirsthead\\toprule Language & Words & Where\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
rows = "".join(f"{cjk(tex(n))} & {tex(c)} & {tex(LANG_NAME[l])} & {v:,}\\\\\n" for n, c, l, v in R["top_names"])
TT = ("{\\footnotesize\\begin{longtable}{llll}\\caption{The 25 most repeated colour names in the main set.}\\label{tab:top}\\\\"
      "\\toprule Name & Colour & Language & Places\\\\\\midrule\\endfirsthead\\toprule Name & Colour & Language & Places\\\\\\midrule\\endhead\n" + rows + "\\bottomrule\\end{longtable}}")
SN = {"en_compound": "English compounds", "turkic_compound": "Turkic compounds", "nordic_kvit": "Norwegian kvit, Danish hvid", "mongolian": "Mongolian",
      "hindi_urdu": "Hindi, Urdu and Nepali", "korean": "Korean"}
PS = R["precision_supp"]["by_rule"]
rows = "".join(f"{SN[k]} & {R['supplement']['by_tag'][k]:,} & {v['accepted']:,} & {v['correct']} of {v['sampled']}\\\\\n" for k, v in sorted(PS.items(), key=lambda x: -x[1]["accepted"]))
TS = ("\\begin{table}[tbp]\\centering\\footnotesize\\caption{The second pass: candidate rows found by each search, names accepted into the main set, and review sample judged correct.}\\label{tab:supp}"
      "\\begin{tabular}{lrrr}\\toprule Rule & Candidates & Accepted & Correct\\\\\\midrule\n" + rows + "\\bottomrule\\end{tabular}\\end{table}")
t = open(os.path.join(ROOT, "code", "paper_template.tex"), encoding="utf-8").read()
for k in ("page", "repo"):
    t = t.replace("\\url{{{meta.%s}}}" % k, "\\url{%s}" % R["meta"][k])
t = t.replace("\\href{https://doi.org/{{meta.doi}}}{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = t.replace("\\url{https://doi.org/{{meta.doi}}}", "https://doi.org/\\{\\{DOI\\}\\}")
t = re.sub(r"\{\{(?!TABLE_)([^}|]+)(\|(\w+))?\}\}", lambda m: tfmt(get(R, m.group(1)), m.group(3) or "raw"), t)
for k, v in (("KINDS", TK), ("LANGS", TL), ("RULES", TR_), ("TOP", TT), ("SUPP", TS)):
    t = t.replace("{{TABLE_%s}}" % k, v)
t = t.replace("\u02bc", "\u2019")
assert "{{" not in t.replace("\\{\\{DOI\\}\\}", "") and "--" not in t and "\u2014" not in t and "\u2013" not in t, re.findall(r"\{\{[^}]*\}\}", t)[:4]
os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, NAME + ".tex"), "w", encoding="utf-8").write(t)
for _ in range(3):
    r = subprocess.run(["xelatex", "-interaction=nonstopmode", NAME + ".tex"], cwd=OUT, capture_output=True, text=True)
log = open(os.path.join(OUT, NAME + ".log"), encoding="utf-8", errors="ignore").read()
print([l for l in log.splitlines() if "Missing character" in l or "undefined" in l.lower() or "Overfull" in l][:12])
for ext in (".aux", ".log", ".out", ".bbl", ".blg"):
    q = os.path.join(OUT, NAME + ext)
    if os.path.exists(q): os.remove(q)
txt = subprocess.run(["pdftotext", os.path.join(OUT, NAME + ".pdf"), "-"], capture_output=True, text=True).stdout
pages = subprocess.run(["pdfinfo", os.path.join(OUT, NAME + ".pdf")], capture_output=True, text=True).stdout
print("paper", r.returncode, len(txt.split()), "words;", [l for l in pages.splitlines() if l.startswith("Pages")], "dashes:", txt.count("\u2014") + txt.count("\u2013") + txt.count("--"))
