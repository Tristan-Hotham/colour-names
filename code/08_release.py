"""Step 8: blog post and meta (release/blog), Zenodo files and metadata (release/zenodo).
10.5281/zenodo.24043682, https://doi.org/10.5281/zenodo.24043682 and https://blog.tristanhotham.com/2026/10/31/colour-names/ stay as placeholders for the publisher."""
import json as _json, shutil, zipfile
from common import *

R = jload(f"{DATA}/results.json")
REL = os.path.join(ROOT, "release"); NAME = "Hotham_Colour_Names"
KEEP = {"DOI", "DOI_URL", "BLOG_URL"}

# numbers and facts in words in the blog and alt text
L = R["lang"]
assert 40 < L["nord"]["black"] < 50 and 38 < L["fa"]["black"] < 45 and 38 < L["tr"]["black"] < 45 and L["mn"]["top"] == "white" and L["ar"]["red"] > 44 and L["eslav"]["red"] > 44
assert L["sslav"]["top"] == "white" and L["nl"]["top"] == "white" and L["es"]["top"] == "white"
assert max((l for l in L if L[l]["n"] >= 2000), key=lambda l: L[l]["white"]) == "es"      # "the whitest of the big languages"
f = R["ftype"]
assert 33 < f["river"]["black_eq"] < 40 and 28 < f["lake"]["black_eq"] < 35 and 40 < f["spring"]["white_eq"] < 46
assert sum(1 for v in L.values() if v["n"] >= 300) == 17
for cc in ("TR", "KZ"): assert R["country"][cc]["top"] == "black"
assert R["families"]["zh_white_yellow_pct"] > 50 and 18 < R["political"]["eslav_pct"] < 25 and 25 < R["political"]["zh_pct"] < 33
assert R["earth"]["white"] > R["earth"]["red"] and R["earth"]["yellow"] > R["earth"]["red"]
for cc, c in (("US", "black"), ("CA", "black"), ("AU", "black"), ("GB", "black"), ("NO", "black"), ("SE", "black"), ("IR", "black"), ("AF", "black"),
              ("MX", "white"), ("RS", "white"), ("ZA", "white"), ("RU", "red"), ("SA", "red"), ("DZ", "red"), ("CN", "yellow")):
    assert R["country"][cc]["top"] == c, cc

post = open(os.path.join(ROOT, "code", "blog_template.html"), encoding="utf-8").read()
post = re.sub(r"\{\{(?!IMG)([^}|]+)(\|(\w+))?\}\}", lambda m: m.group(0) if m.group(1) in KEEP else fmt(get(R, m.group(1)), m.group(3)), post)
used = re.findall(r"\{\{IMG\|([^|]+)\|", post)
assert 5 <= len(used) <= 8, len(used)
assert all(re.search(r"^\{\{IMG\|" + re.escape(u_), post, re.M) for u_ in used) and "wp:image" not in post
from PIL import Image
for img in used:
    assert os.path.exists(f"{REL}/blog/{img}"), img
    assert Image.open(f"{REL}/blog/{img}").size[0] == 1800, img
for fn in os.listdir(f"{REL}/blog"):
    if fn.startswith("b_") and fn not in used:
        os.remove(f"{REL}/blog/{fn}")
assert set(re.findall(r"\{\{([^|}]+)\}\}", post)) <= KEEP
vis = re.sub(r"<!--.*?-->", "", post, flags=re.S)
for bad in ("\u2014", "\u2013", "--", "DSIT", "DCMS"):
    assert bad not in vis, bad
open(f"{REL}/blog/post.html", "w", encoding="utf-8").write(post)
words = len(re.sub(r"<[^>]+>|\{\{IMG\|[^}]*\}\}", " ", vis).split())
S = R["source"]
meta = {"title": "Black rivers, white springs: the colours of the world's place names",
        "slug": "colour-names",
        "excerpt": f"I found {S['main']:,} places named after a colour, in {S['languages']} languages. Rivers run black, springs run white, the commonest colour name on Earth is Cerro Colorado, and a fifth of Russia's red is revolutionary.",
        "seo_description": f"{S['main']:,} places named black, white, red, green, blue or yellow in {S['languages']} languages, mapped: black rivers, white springs, red flags.",
        "tags": ["maps", "place names", "toponymy", "colour", "language", "GeoNames", "data visualisation", "geography"],
        "header_alt": f"Title card reading 'The colours of the world's place names' in black and red on parchment, beside a world map covered in small dots in black, white, red, green, blue and yellow, with the lines '{S['main']:,} colour names in {S['languages']} languages', '{R['words']['river_black_eq']:.0f}% of rivers are black' and '{R['words']['spring_white_eq']:.0f}% of springs are white'."}
assert len(meta["seo_description"]) < 160, len(meta["seo_description"])
jsave(meta, f"{REL}/blog/meta.json", indent=2)

# Zenodo
Z = f"{REL}/zenodo"; os.makedirs(Z, exist_ok=True)
for fn in os.listdir(Z):
    os.remove(os.path.join(Z, fn))
shutil.copy(f"{REL}/paper/{NAME}.pdf", f"{Z}/{NAME}.pdf")
zp = f"{Z}/colour-names_data_and_code.zip"
OWN = ["colour_places.csv", "by_country.csv", "by_language.csv", "by_feature.csv", "grid_2deg.csv", "precision.csv", "review_sample.csv", "results.json", "countries.json"]
with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
    for fn in sorted(os.listdir(os.path.join(ROOT, "code"))):
        if fn.endswith(".pyc") or fn == "__pycache__":
            continue
        z.write(os.path.join(ROOT, "code", fn), f"colour-names/code/{fn}")
    for fn in OWN:
        z.write(os.path.join(DATA, fn), f"colour-names/data/{fn}")
    for fn in ("README.md", "LICENSE", "index.html"):
        z.write(os.path.join(ROOT, fn), f"colour-names/{fn}")
    z.write(os.path.join(ROOT, "reddit", "collage.py"), "colour-names/reddit/collage.py")
tex = open(f"{REL}/paper/{NAME}.tex", encoding="utf-8").read()
ab = re.search(r"\\begin\{center\}\\textbf\{Abstract\}\\end\{center\}\n(.*?)\n\n\\textbf\{Keywords", tex, re.S).group(1)
ab = ab.replace("\\%", "%").replace("\\&", "&")
ab = re.sub(r"\\textit\{([^}]*)\}", r"\1", ab)
zmeta = {"title": "The Colours of the World's Place Names: Black, White, Red, Green, Blue and Yellow in GeoNames",
         "upload_type": "publication", "publication_type": "workingpaper",
         "description": f"<p>{ab}</p><p>Interactive version: <a href=\"{PAGE}\">{PAGE}</a>. Data and code: <a href=\"{REPO}\">{REPO}</a>. Blog post: {{https://blog.tristanhotham.com/2026/10/31/colour-names/}}.</p><p>Sources: GeoNames (CC BY 4.0); Natural Earth (public domain); map style on OpenStreetMap data (ODbL) via OpenFreeMap. Derived data CC BY 4.0, code MIT.</p>",
         "creators": [{"name": "Hotham, Tristan", "affiliation": "Independent researcher", "orcid": "0000-0003-4931-9349"}],
         "keywords": ["toponymy", "place names", "colour terms", "basic color terms", "GeoNames", "historical geography", "maps", "open data"],
         "license": "cc-by-4.0", "language": "eng",
         "related_identifiers": [{"identifier": REPO, "relation": "isSupplementedBy", "resource_type": "software"},
                                 {"identifier": PAGE, "relation": "isSupplementedBy", "resource_type": "other"},
                                 {"identifier": GEONAMES_URL, "relation": "isDerivedFrom", "resource_type": "dataset"},
                                 {"identifier": "https://www.naturalearthdata.com/", "relation": "isDerivedFrom", "resource_type": "dataset"}],
         "files": sorted(os.listdir(Z))}
sj = _json.dumps(zmeta, ensure_ascii=False) + _json.dumps(meta, ensure_ascii=False)
assert "\u2014" not in sj and "\u2013" not in sj and "--" not in sj
jsave(zmeta, f"{Z}/metadata.json", indent=2)
print("blog words", words, "figures", len(used), "; zenodo", sorted(os.listdir(Z)), os.path.getsize(zp) // 1024, "KB zip")
