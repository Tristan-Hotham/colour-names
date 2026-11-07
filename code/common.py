"""Shared paths, groupings and helpers for the colour-names study ("The colours of the world's place names").

Raw inputs (read in place, never modified; from step 03 on only data/ is needed):
  CAND  /home/claude/newdata/raw_new6/colours/geonames_colour_candidates.tsv.gz
        185,388 GeoNames rows in the allCountries format (geonameid, name, asciiname, alternatenames, latitude,
        longitude, feature class, feature code, country code, cc2, admin1 to admin4, population, elevation, dem,
        timezone, modification date; https://download.geonames.org/export/dump/readme.txt). They are the rows of
        allCountries.txt that a broad colour-word filter kept: whole words in English and the Romance languages, word
        starts in German, Dutch, the Nordic languages, Polish and Russian, whole words in the Turkic, Arabic and Persian
        romanisations, and the colour characters in the native-script alternate names. GeoNames, CC BY 4.0.
  SUPP  /home/claude/newdata/raw_new6/colours/geonames_colour_supplement.tsv.gz
        67,227 further GeoNames rows from a second, wider pass over allCountries, with a leading tag column naming the
        search that found them: en_compound (Blackburn, Whitby), turkic_compound (Aksu, Karakol), nordic_kvit (kvit, hvid),
        mongolian (khar, tsagaan, ulaan), hindi_urdu (kala, lal, safed) and korean (heuk, baek, hong). Disjoint from CAND.
  GEO   /home/claude/newdata/raw/geo/ne_50m_admin_0_countries.geojson, ne_50m_land.geojson (Natural Earth, public domain)
  FONTS /home/claude/ref/fonts (Fraunces, Source Serif 4, IBM Plex Mono); the Inked World's lettering fonts in fonts/ttf
"""
import json, gzip, os, re, math

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.environ.get("CN_CAND", "/home/claude/newdata/raw_new6/colours/geonames_colour_candidates.tsv.gz")
SUPP = os.environ.get("CN_SUPP", "/home/claude/newdata/raw_new6/colours/geonames_colour_supplement.tsv.gz")
GEO = os.environ.get("CN_GEO", "/home/claude/newdata/raw/geo")
FONTS = os.environ.get("CN_FONTS", "/home/claude/ref/fonts")
INKFONTS = os.path.join(ROOT, "fonts", "ttf")
DATA = os.path.join(ROOT, "data")
WORK = os.environ.get("CN_WORK", "/home/claude/work/new6/colour-names/work")   # intermediates, not in the repo
for d in (DATA, WORK):
    os.makedirs(d, exist_ok=True)

SLUG = "colour-names"
PAGE = f"https://maps.tristanhotham.com/{SLUG}/"
REPO = f"https://github.com/Tristan-Hotham/{SLUG}"
GEONAMES_URL = "https://www.geonames.org/"
GEONAMES_DUMP = "https://download.geonames.org/export/dump/"
AI = ("I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped "
      "prepare the analysis code. I reviewed and checked all text and results.")

COLS = ["geonameid", "name", "asciiname", "alternatenames", "lat", "lon", "fclass", "fcode", "cc", "cc2",
        "a1", "a2", "a3", "a4", "pop", "elev", "dem", "tz", "moddate"]

# The colours, in the order used everywhere, with the hand-tinted ink colours of the maps and figures.
# "grue" is the single East Asian character for blue and green (Chinese qing, Japanese ao), kept apart.
COLOURS = ["black", "white", "red", "green", "blue", "yellow", "grue"]
CNAME = {"black": "Black", "white": "White", "red": "Red", "green": "Green", "blue": "Blue", "yellow": "Yellow",
         "grue": "Blue-green (qing, ao)"}
TINT = {"black": "#2B2119", "white": "#FFFDF6", "red": "#B0301F", "green": "#55803A", "blue": "#3C6C9C",
        "yellow": "#D9A21E", "grue": "#3F8C84"}
EDGE = {"black": "#2B2119", "white": "#6B5A44", "red": "#7A1D12", "green": "#33542A", "blue": "#264A70",
        "yellow": "#8A6410", "grue": "#25605A"}

# Feature types: GeoNames feature codes grouped into the kinds of place compared in the study.
FTYPES = [
    ("river", "Rivers, streams and wadis"),
    ("lake", "Lakes, ponds and marshes"),
    ("spring", "Springs and wells"),
    ("sea", "Seas, bays and coasts"),
    ("mountain", "Mountains and hills"),
    ("rock", "Rocks, cliffs and islands"),
    ("valley", "Valleys, gorges and passes"),
    ("land", "Plains, deserts, woods and areas"),
    ("settlement", "Towns and villages"),
]
FT_NAME = dict(FTYPES)
_FT = {
    "river": "STM STMI STMS STMX STMA STMB STMC STMD STMH STMIX STMM STMQ STMSB WAD WADB WADJ WADM WADS WADX RPDS FLLS FLLSX CNFL STMMS",
    "lake": "LK LKS LKI LKN LKO LKX LKC LKSI LKSN LKSB LKSC LKNI LKOI PND PNDS PNDI PNDN PNDNI PNDSI PNDSN POOL POOLI RSV RSVT RSVI MRSH MRSHN SWMP BOG MOOR LGN LGNS LGNX PAN PANS SBKH SBED OVF",
    "spring": "SPNG SPNS SPNT WLL WLLS WLLQ WLLSQ OAS WTRH CSTN",
    "sea": "SEA BAY BAYS GULF COVE CHN CHNM CHNN CHNL STRT SD SND OCN INLT FJD FJDS HBR BGHT ANCH ESTY LBED RF RFC RFX SHOL BAR SHSU CRKT",
    "mountain": "MT MTS HLL HLLS PK PKS RDG RDGE SPUR MESA BUTE KNLL KNLS MND MNDS UPLD PLAT VLC VLCX CRTR CONE HMCK HMSD NTK NTKS CRQ CRQS CLDA SCRP DUNE DUNS SDL ERG GLCR CUET HDLD PROM TRR",
    "rock": "RK RKS CLF CLFS BLDR RKFL ISL ISLS ISLET ISLF ISLM ISLT ISLX ATOL CAPE PT PTS PEN PENX BCH BCHS SPIT STKR",
    "valley": "VAL VALS VALG VALX GRGE CNYN RVN DPR HLLW GAP PASS SINK CAVE GULCH CRDR",
    "land": "PLN PLNX DSRT AREA LCTY FLD GRAZ SLP BNCH PLDR RGN RGNE RGNL CULT MDW SAND SALT FRST FRSTF GROVE HTH SCRB TREE OCH PAL CLG LEV BNK",
}
FT_OF = {c: k for k, v in _FT.items() for c in v.split()}


def ftype(fclass, fcode):
    """Kind of place, or None for kinds left out of the main analysis (buildings and spots, roads, admin areas,
    undersea features)."""
    if fclass == "P":
        return "settlement"
    if fclass in ("S", "R", "A", "U", ""):
        return None
    if fcode in FT_OF:
        return FT_OF[fcode]
    return {"H": "lake", "T": "mountain", "V": "land"}.get(fclass)   # other land codes (parks, reserves, ports, industrial areas) are left out


# Country groupings used for the language areas (ISO 3166 alpha-2)
ARAB = set("SA YE OM AE QA BH KW IQ SY JO LB PS IL EG LY TN DZ MA EH MR SD SS SO DJ KM TD ER ML NE".split())
TURKIC = set("TR AZ TM UZ KZ KG RU CN MN AF IR TJ GE AM CY UA BG GR MK IQ SY".split())
PERSIAN = set("IR AF TJ PK".split())
EASTSLAV = set("RU UA BY KZ KG UZ TJ TM AZ AM GE MD LV LT EE MN".split())
SOUTHSLAV = set("BG RS MK BA ME XK".split())
GERMAN = set("DE AT CH LI LU IT BE NA".split())
DUTCH = set("NL BE SR CW AW SX BQ ZA NA".split())
NORDIC = set("NO SE DK FI IS FO GL SJ AX".split())
POLISH = {"PL"}
PORTUGUESE = set("BR PT AO MZ CV GW ST TL MO".split())
ITALIAN = set("IT SM VA MT".split())
ROMANIAN = set("RO MD".split())
CHINESE = set("CN TW HK MO".split())
JAPANESE = {"JP"}

LANG_NAME = {"en": "English", "es": "Spanish", "pt": "Portuguese", "fr": "French", "it": "Italian", "ro": "Romanian",
             "de": "German", "nl": "Dutch and Afrikaans", "nord": "Nordic languages", "pl": "Polish",
             "eslav": "Russian, Ukrainian and Belarusian", "sslav": "Bulgarian, Serbian and Macedonian",
             "tr": "Turkic languages", "ar": "Arabic", "fa": "Persian", "zh": "Chinese", "ja": "Japanese",
             "mn": "Mongolian", "hi": "Hindi, Urdu and Nepali", "ko": "Korean"}
LANGS = list(LANG_NAME)

# The colour words of each language as they appear in the page legend and the collage (dictionary forms)
WORDS = {
    "en": {"black": "black", "white": "white", "red": "red", "green": "green", "blue": "blue", "yellow": "yellow"},
    "es": {"black": "negro", "white": "blanco", "red": "rojo, colorado", "green": "verde", "blue": "azul", "yellow": "amarillo"},
    "pt": {"black": "preto, negro", "white": "branco", "red": "vermelho", "green": "verde", "blue": "azul", "yellow": "amarelo"},
    "fr": {"black": "noir", "white": "blanc", "red": "rouge", "green": "vert", "blue": "bleu", "yellow": "jaune"},
    "it": {"black": "nero", "white": "bianco", "red": "rosso", "green": "verde", "blue": "", "yellow": "giallo"},
    "ro": {"green": "verde"},
    "de": {"black": "schwarz", "white": "weiss", "red": "rot", "green": "grün", "blue": "blau", "yellow": "gelb"},
    "nl": {"black": "zwart", "white": "wit", "red": "rood", "green": "groen", "blue": "blauw", "yellow": "geel"},
    "nord": {"black": "svart", "white": "hvit, vit", "red": "rød, röd", "green": "grønn, grön", "blue": "blå", "yellow": "gul"},
    "pl": {"black": "czarny", "white": "biały", "red": "czerwony", "green": "zielony", "blue": "niebieski", "yellow": "żółty"},
    "eslav": {"black": "chërnyy", "white": "belyy", "red": "krasnyy", "green": "zelënyy", "blue": "siniy", "yellow": "zhëltyy"},
    "sslav": {"black": "cheren", "white": "bel", "green": "zelen", "blue": "sin"},
    "tr": {"black": "kara, qara", "white": "ak, aq", "red": "kızıl, kyzyl", "green": "yeşil", "blue": "gök, kök", "yellow": "sarı, sary"},
    "ar": {"black": "aswad, sawdāʼ", "white": "abyaḍ, bayḍāʼ", "red": "aḥmar, ḥamrāʼ", "green": "akhḍar, khaḍrāʼ", "blue": "azraq, zarqāʼ", "yellow": "aṣfar, ṣafrāʼ"},
    "fa": {"black": "siāh", "white": "sefid", "red": "sorkh", "green": "sabz", "yellow": "zard"},
    "zh": {"black": "黑 hei", "white": "白 bai", "red": "红 hong", "green": "绿 lü", "blue": "蓝 lan", "yellow": "黄 huang", "grue": "青 qing"},
    "mn": {"black": "khar", "white": "tsagaan", "red": "ulaan", "green": "nogoon", "blue": "khökh", "yellow": "shar"},
    "hi": {"black": "kala", "white": "safed", "red": "lal", "green": "hara", "blue": "nila", "yellow": "pila"},
    "ko": {"black": "黑 heuk", "white": "白 baek", "red": "紅 hong", "green": "綠 nok", "yellow": "黃 hwang", "grue": "靑 cheong"},
    "ja": {"black": "黒 kuro", "white": "白 shiro", "red": "赤 aka", "green": "緑 midori", "yellow": "黄 ki", "grue": "青 ao"},
}


def jload(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def nonan(v):
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return {k: nonan(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [nonan(x) for x in v]
    if hasattr(v, "item"):
        return nonan(v.item())
    return v


def jsave(obj, path, indent=None):
    obj = nonan(obj)
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent, separators=None if indent else (",", ":"))


def get(R, path):
    v = R
    for k in path.split("."):
        v = v[int(k)] if isinstance(v, list) else v[k]
    return v


def fmt(v, f=None):
    if f is None or f == "raw": return str(v)
    if f == "int": return f"{round(float(v)):,}"
    if f == "pc": return f"{round(float(v))}%"
    if f == "pc1": return f"{float(v):.1f}%"
    if f == "f1": return f"{float(v):.1f}"
    if f == "f2": return f"{float(v):.2f}"
    raise ValueError(f)
