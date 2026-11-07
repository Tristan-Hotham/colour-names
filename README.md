# The colours of the world's place names

138,453 rivers, lakes, springs, hills, rocks, valleys and villages named after a colour (black, white, red, green, blue, yellow, and the East Asian blue-green 青) in 20 languages, picked out of GeoNames with a classifier written for each language and checked by hand, and mapped on a hand-inked world map.

Interactive page: https://maps.tristanhotham.com/colour-names/
Paper: https://doi.org/10.5281/zenodo.24043682
Blog post: https://blog.tristanhotham.com/2026/10/31/colour-names/
Code and data: https://github.com/Tristan-Hotham/colour-names

## Headline results

- White is the commonest colour in place names (26.5%), then red (20.6%) and black (23.2%); blue is last (5.5%). Without Chinese and Japanese, black (27.3%) and white (25.7%) are level.
- Rivers are the blackest kind of place (37.2% black, languages weighted equally; blacker than their language's average in 14 of 17 languages); springs and wells the whitest (42.7%). Mountains are only weakly white (28.4% white, 27.6% black).
- Each language has a favourite: svart in the Nordic languages (45.1%), siāh in Persian (42.4%), kara and ak in the Turkic languages (67.7% together), bai and huang in Chinese (58.8%). The commonest colour name of all is Cerro Colorado (1,084 places); in Spanish and Portuguese, rivers are whiter than black (428 Río Blanco, 309 Río Negro).
- In the 102 countries with at least 30 names the commonest colour is white in 35, black in 35, red in 21, green in 8, yellow in 2 and blue in none.
- 21.9% of East Slavic and 29.8% of Chinese red names are revolutionary (Red October, Red Flag). Names of earth, soil and clay are no redder than names in general (20.4% red).
- Review: 4,370 sampled names read by eye (up to 50 per colour and language), 99% judged correct after tuning the rules on them; for the second pass, 50 names per rule, 299 of 300 correct.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`): the Inked World map style on MapLibre GL JS, a dot for every name, filters by colour, language and kind of place, country shading, search and popups. |
| `header.png` | Social card, 1200 x 630. |
| `data/colour_places.csv.gz` | Every accepted name (176,831 rows): GeoNames id, name, coordinates, country, feature class and code, kind of place, colour, matched word, language, flag (political, species) and whether it is in the main set. |
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

- Candidates: 252,615 GeoNames rows from two colour-word searches of the allCountries dump: a first pass (185,388 rows) and a wider second pass (67,227 rows) for English and Turkic compounds (Blackburn, Whitby, Aksu, Karakol), Norwegian kvit, Mongolian, Hindi and Urdu, and Korean.
- Classifier (`code/rules.py`): for each language, the colour word must be an adjective form or the first part of a compound with a landscape word, in a country where the language is spoken, and outside stop-lists (saints, possessives, family-name endings, states, plants and animals, Spanish negro and colorado in the US without a Spanish word beside them). Chinese and Japanese are read in their own characters; 青 is kept as blue-green. Plant and animal names are flagged and left out; revolutionary red is flagged and kept.
- Main set: natural features and settlements; buildings, farms, mines, hotels, parks, roads, admin areas and undersea features left out (35,478 names).
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

Hotham, T. (2026) The colours of the world's place names: black, white, red, green, blue and yellow in GeoNames. Zenodo. https://doi.org/10.5281/zenodo.24043682

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
