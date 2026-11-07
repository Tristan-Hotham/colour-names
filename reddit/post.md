## Title

[OC] I mapped 138,453 places named after a colour in 20 languages. Rivers are the blackest places (37% black), springs the whitest (43%), and the most common colour name on Earth is Cerro Colorado (1,084 hills)

## Body

I went through GeoNames, the big open gazetteer, and picked out every river, lake, spring, hill, rock, valley and village named black, white, red, green, blue or yellow, in English, Spanish, Portuguese, French, German, Dutch, the Nordic languages, Polish, Russian, Turkic, Mongolian, Arabic, Persian, Hindi, Chinese, Japanese, Korean and more. Blackburn, Whitby and Karasu are in. Most of the work was throwing out false friends: Rotterdam is not red, Belovo is named after a Mr Belov, a Chinese Huang village is usually a family, and Negro Creek in the US is named for people. I hand-checked 4,670 names (99% correct after tuning).

White is the commonest colour (26%), then black and red; blue is rare everywhere (6%). Nordic maps are 45% svart (black), Persian ones 42% siāh. Spanish rivers are the odd ones out: 428 Río Blanco against 309 Río Negro. And about a fifth of Russia's red names are revolutionary (Red October, Red Army, Red Star).

Caveats: GeoNames is much denser in some countries (US, Mexico, China, Norway, Iran), and Korean, Hindi and Urdu are only covered where the meaning is clear; Hungarian, Finnish and Greek are not in at all. Interactive map with a dot for every name: https://maps.tristanhotham.com/colour-names/

## Source comment

Source: GeoNames (CC BY 4.0), allCountries dump; country outlines from Natural Earth. Classifier, review samples and code: https://github.com/Tristan-Hotham/colour-names

Tools: Python (pandas, shapely, matplotlib); MapLibre GL JS for the interactive map, in the Inked World hand-inked style on OpenStreetMap data.

Interactive version: https://maps.tristanhotham.com/colour-names/
Paper: https://doi.org/10.5281/zenodo.24043682
Blog post: https://blog.tristanhotham.com/2026/10/31/colour-names/
