"""Step 5: index.html from code/page_template.html, filled from data/results.json, with the full-screen snippet.
https://doi.org/10.5281/zenodo.24043682 and https://blog.tristanhotham.com/2026/10/31/colour-names/ stay as placeholders for the publisher."""
from common import *

R = jload(f"{DATA}/results.json")
KEEP = {"DOI_URL", "BLOG_URL", "DOI"}
# facts stated in words on the page
assert R["colour_pct"]["white"] == max(R["colour_pct"].values())
assert R["kind_most"]["black"] == "river" and R["kind_most"]["white"] == "spring"
assert R["ftype"]["mountain"]["white_eq"] > R["ftype"]["mountain"]["black_eq"] > R["ftype"]["mountain"]["red_eq"]
assert R["colour_pct"]["blue"] == min(v for k, v in R["colour_pct"].items() if k != "grue")
assert R["countries"]["top_count"]["blue"] == 0
assert R["families"]["rio_blanco"] > R["families"]["rio_negro"] and R["families"]["iberian_river_white"] > R["families"]["iberian_river_black"]
assert R["top_names"][0][0] == "Cerro Colorado"
assert abs(R["earth"]["red_pct"] - R["colour_pct"]["red"]) < 3 and R["earth"]["white"] > R["earth"]["red"] and R["earth"]["yellow"] > R["earth"]["red"]
assert R["country"]["KR"]["top"] == "grue" and R["countries"]["top_count"]["grue"] == 1 and R["country"]["MN"]["top"] == "white"
assert R["colour_pct_nozhja"]["black"] > R["colour_pct_nozhja"]["white"] > R["colour_pct_nozhja"]["red"]
assert R["colour_pct"]["white"] > R["colour_pct"]["black"] > R["colour_pct"]["red"]
assert all(R["country"][c]["top"] == "black" for c in ("TR", "KZ", "KG", "UZ", "TM"))
assert R["lang"]["hi"]["black"] > 60
for cc, c in (("US", "black"), ("GB", "black"), ("AU", "black"), ("CA", "black"), ("NO", "black"), ("IR", "black"), ("AF", "black"), ("MX", "white"),
              ("AR", "white"), ("PE", "white"), ("ZA", "white"), ("PL", "white"), ("RU", "red"), ("YE", "red")):
    assert R["country"][cc]["top"] == c, (cc, R["country"][cc]["top"])
assert R["lang"]["ar"]["top"] == "red" and R["lang"]["eslav"]["top"] == "red" and R["lang"]["sslav"]["top"] == "white"
t = open(os.path.join(ROOT, "code", "page_template.html"), encoding="utf-8").read()
t = t.replace("{{FULLSCREEN}}", open(os.path.join(ROOT, "code", "fullscreen_snippet.html"), encoding="utf-8").read())
t = t.replace("{{REPO}}", REPO).replace("{{AI}}", AI)
t = re.sub(r"\{\{([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), t)
left = set(re.findall(r"\{\{([^}]+)\}\}", t))
assert left <= KEEP, left
vis = re.sub(r"<script.*?</script>|<style.*?</style>|<!--.*?-->", "", t, flags=re.S)
for bad in ("—", "–", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(t)
print("index.html", len(t) // 1024, "KB")
