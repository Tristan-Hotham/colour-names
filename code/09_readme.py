"""Step 9: README.md, LICENSE and reddit/post.md from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json")
S, P, W, F = R["source"], R["precision"], R["words"], R["families"]
assert R["families"]["cerro_colorado"] == R["top_names"][0][3]
readme = f"""# The colours of the world's place names

{S['main']:,} rivers, lakes, springs, hills, rocks, valleys and villages named after a colour (black, white, red, green, blue, yellow, and the East Asian blue-green 青) in {S['languages']} languages, picked out of GeoNames with a classifier written for each language and checked by hand, and mapped on a hand-inked world map.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24043682}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/colour-names/}}
Code and data: {REPO}

## Headline results

- White is the commonest colour in place names ({R['colour_pct']['white']:.1f}%), then red ({R['colour_pct']['red']:.1f}%) and black ({R['colour_pct']['black']:.1f}%); blue is last ({R['colour_pct']['blue']:.1f}%). Without Chinese and Japanese, black ({R['colour_pct_nozhja']['black']:.1f}%) and white ({R['colour_pct_nozhja']['white']:.1f}%) are level.
- Rivers are the blackest kind of place ({W['river_black_eq']:.1f}% black, languages weighted equally; blacker than their language's average in {R['rivers_blacker']['blacker']} of {R['rivers_blacker']['langs']} languages); springs and wells the whitest ({W['spring_white_eq']:.1f}%). Mountains are only weakly white ({W['mountain_white_eq']:.1f}% white, {W['mountain_black_eq']:.1f}% black).
- Each language has a favourite: svart in the Nordic languages ({F['nord_svart_pct']:.1f}%), siāh in Persian ({F['fa_siah_pct']:.1f}%), kara and ak in the Turkic languages ({F['tr_kara_ak_pct']:.1f}% together), bai and huang in Chinese ({F['zh_white_yellow_pct']:.1f}%). The commonest colour name of all is Cerro Colorado ({F['cerro_colorado']:,} places); in Spanish and Portuguese, rivers are whiter than black ({F['rio_blanco']} Río Blanco, {F['rio_negro']} Río Negro).
- In the {R['countries']['with30']} countries with at least 30 names the commonest colour is white in {R['countries']['top_count']['white']}, black in {R['countries']['top_count']['black']}, red in {R['countries']['top_count']['red']}, green in {R['countries']['top_count']['green']}, yellow in {R['countries']['top_count']['yellow']} and blue in none.
- {R['political']['eslav_pct']:.1f}% of East Slavic and {R['political']['zh_pct']:.1f}% of Chinese red names are revolutionary (Red October, Red Flag). Names of earth, soil and clay are no redder than names in general ({R['earth']['red_pct']:.1f}% red).
- Review: {P['sampled']:,} sampled names read by eye (up to 50 per colour and language), {P['overall_pct']}% judged correct after tuning the rules on them; for the second pass, 50 names per rule, {R['precision_supp']['correct']} of {R['precision_supp']['sampled']} correct.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`): the Inked World map style on MapLibre GL JS, a dot for every name, filters by colour, language and kind of place, country shading, search and popups. |
| `header.png` | Social card, 1200 x 630. |
| `data/colour_places.csv` | Every accepted name ({S['accepted_rows']:,} rows): GeoNames id, name, coordinates, country, feature class and code, kind of place, colour, matched word, language, flag (political, species) and whether it is in the main set. |
| `data/by_language.csv`, `data/by_feature.csv`, `data/by_country.csv`, `data/grid_2deg.csv` | Colour counts and shares by language, by kind of place (pooled and languages weighted equally), by country and on a 2 degree grid. |
| `data/review_sample.csv`, `data/precision.csv`, `data/review_supplement.csv`, `data/precision_supplement.csv` | The review samples with my verdicts, and precision by language and colour (first pass) and by rule (second pass). |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `data/points.json`, `data/countries.json` | Page data: the main set as compact rows; Natural Earth countries with colour counts. |
| other `data/*` files, `js/`, `fonts/` | The Inked World map style (engine, lettering fonts and basemap data), copied from the ink-map study. |
| `img/` | Figures on the page. |
| `code/` | Numbered scripts, the language rules (`rules.py`), my review verdicts (`review_verdicts.tsv`), page, paper and blog templates, `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, PNG) and post text. |

## Method in brief

- Candidates: {S['candidates']:,} GeoNames rows from two colour-word searches of the allCountries dump: a first pass ({S['candidates_first']:,} rows) and a wider second pass ({R['supplement']['rows']:,} rows) for English and Turkic compounds (Blackburn, Whitby, Aksu, Karakol), Norwegian kvit, Mongolian, Hindi and Urdu, and Korean.
- Classifier (`code/rules.py`): for each language, the colour word must be an adjective form or the first part of a compound with a landscape word, in a country where the language is spoken, and outside stop-lists (saints, possessives, family-name endings, states, plants and animals, Spanish negro and colorado in the US without a Spanish word beside them). Chinese and Japanese are read in their own characters; 青 is kept as blue-green. Plant and animal names are flagged and left out; revolutionary red is flagged and kept.
- Main set: natural features and settlements; buildings, farms, mines, hotels, parks, roads, admin areas and undersea features left out ({S['excluded_kind']:,} names).
- Review: up to 50 names per colour and language, in a fixed hash order, read by eye; the rules were tuned on them, so the precision is optimistic.
- Shares are given pooled and with languages weighted equally (languages with 30 or more names of a kind).
- Second-pass rules: English compounds must end in a place-name element (-burn, -pool, -by, -church); Red- only with -hill, -car, -cliff and a few more (Red- is often reed or Cornish rhyd); bare Whit- only in Britain and Ireland; surnames stopped in the New World. Turkic stems must start the word and meet a landscape word. Hindi and Urdu words only beside a landscape word; Korean only with the colour hanja or an unambiguous hangul compound.
- Caveats: GeoNames is much denser in some countries; Korean, Hindi and Urdu are covered only where the meaning is clear (so South Asia looks very black); Hungarian, Finnish, Greek, Malay, Pashto and African languages are missing; colour words can carry other meanings (family names; krasnyy once meant beautiful).

## How to rerun

Needs Python 3 with pandas, numpy, shapely, matplotlib, Pillow and fontTools, xelatex and pdftotext; node with Playwright for `code/qa.js`. Steps 01 to 03 read the two GeoNames candidate files (paths in `code/common.py`, not redistributed); from step 04 on only `data/` and the intermediate `main.csv` are needed. Intermediates go to `CN_WORK`.

```
python3 code/01_classify.py   # apply the language rules
python3 code/02_review.py     # review samples and precision
python3 code/03_analysis.py   # shares, countries, families, red
python3 code/04_results.py    # results.json, page data
python3 code/05_build_site.py # index.html
python3 code/06_figures.py    # figures and header
python3 code/07_paper.py      # paper PDF
python3 reddit/collage.py     # collage
python3 code/09_readme.py     # README, LICENSE, Reddit post
python3 code/08_release.py    # blog post, Zenodo files
```

## Sources and licences

- GeoNames (https://www.geonames.org/), allCountries dump, CC BY 4.0. Credit: GeoNames. The derived name lists here are shared under the same licence.
- Natural Earth 1:50m countries and land (public domain).
- Map style: the Inked World (ink-map study, MIT code), on OpenStreetMap data (© OpenStreetMap contributors, ODbL) served by OpenFreeMap (OpenMapTiles schema); RESOLVE Ecoregions 2017 (CC BY 4.0); Wikidata (CC0); AWS Terrain Tiles for elevation.
- Fonts: MedievalSharp and IM Fell (SIL Open Font License); Fraunces, Source Serif 4, IBM Plex Mono (SIL Open Font License).
- Berlin, B. and Kay, P. (1969) Basic Color Terms, for the order of colour terms.

## Citation

Hotham, T. (2026) The colours of the world's place names: black, white, red, green, blue and yellow in GeoNames. Zenodo. {{https://doi.org/10.5281/zenodo.24043682}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data: CC BY 4.0 (https://creativecommons.org/licenses/by/4.0/), Tristan Hotham, 2026.
Place names and positions: GeoNames (https://www.geonames.org/), CC BY 4.0.
Country outlines: Natural Earth, public domain.
Map style files in js/, fonts/ and the basemap data in data/ come from the ink-map study (code MIT; data credits in its README: OpenStreetMap ODbL, RESOLVE Ecoregions CC BY 4.0, Wikidata CC0, Natural Earth). Fonts under the SIL Open Font License (see fonts/ttf).
"""
post = f"""## Title

[OC] I mapped {S['main']:,} places named after a colour in {S['languages']} languages. Rivers are the blackest places ({W['river_black_eq']:.0f}% black), springs the whitest ({W['spring_white_eq']:.0f}%), and the most common colour name on Earth is Cerro Colorado ({F['cerro_colorado']:,} hills)

## Body

I went through GeoNames, the big open gazetteer, and picked out every river, lake, spring, hill, rock, valley and village named black, white, red, green, blue or yellow, in English, Spanish, Portuguese, French, German, Dutch, the Nordic languages, Polish, Russian, Turkic, Mongolian, Arabic, Persian, Hindi, Chinese, Japanese, Korean and more. Blackburn, Whitby and Karasu are in. Most of the work was throwing out false friends: Rotterdam is not red, Belovo is named after a Mr Belov, a Chinese Huang village is usually a family, and Negro Creek in the US is named for people. I hand-checked {P['sampled'] + R['precision_supp']['sampled']:,} names ({P['overall_pct']}% correct after tuning).

White is the commonest colour ({R['colour_pct']['white']:.0f}%), then black and red; blue is rare everywhere ({R['colour_pct']['blue']:.0f}%). Nordic maps are {F['nord_svart_pct']:.0f}% svart (black), Persian ones {F['fa_siah_pct']:.0f}% siāh. Spanish rivers are the odd ones out: {F['rio_blanco']} Río Blanco against {F['rio_negro']} Río Negro. And about a fifth of Russia's red names are revolutionary (Red October, Red Army, Red Star).

Caveats: GeoNames is much denser in some countries (US, Mexico, China, Norway, Iran), and Korean, Hindi and Urdu are only covered where the meaning is clear; Hungarian, Finnish and Greek are not in at all. Interactive map with a dot for every name: https://maps.tristanhotham.com/colour-names/

## Source comment

Source: GeoNames (CC BY 4.0), allCountries dump; country outlines from Natural Earth. Classifier, review samples and code: {REPO}

Tools: Python (pandas, shapely, matplotlib); MapLibre GL JS for the interactive map, in the Inked World hand-inked style on OpenStreetMap data.

Interactive version: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24043682}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/colour-names/}}
"""
for txt in (readme, post, lic):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in txt.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
os.makedirs(os.path.join(ROOT, "reddit"), exist_ok=True)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words; post title", len(post.splitlines()[2]), "chars")
