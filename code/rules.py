"""The colour-word classifier: one rule set per language, applied to the words of each GeoNames name.

A candidate row passes if one of its words is a colour word of a language spoken where the place is (the country code
decides the language area), in a form that language uses for the colour: a whole word, an inflected form, or the first
part of a compound whose second part is an ordinary landscape word (Schwarz-wald, Svart-berget, Krasno-yarsk). Chinese
and Japanese names are read in their own characters. Each rule was tuned on review samples of up to 50 names per colour
and language (02_review.py), and the stop-lists below record what the samples taught.

classify(row) returns (hits, reason): hits is a list of dicts {colour, word, lang, flag}; reason says why a row was
rejected when hits is empty. flag is "" for an ordinary colour name, "political" for the revolutionary red of Soviet
and Chinese names (Krasnyy Oktyabr', Hongqi), and "species" for English names taken from a plant or animal that is
itself named for a colour (Red Oak, Blackbird), which are kept but counted apart.
"""
import re
import unicodedata
from common import (ARAB, TURKIC, PERSIAN, EASTSLAV, SOUTHSLAV, GERMAN, DUTCH, NORDIC, POLISH, PORTUGUESE, ITALIAN,
                    ROMANIAN, CHINESE, JAPANESE)


def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))


def words(s):
    """Lower-case ASCII words; apostrophes, hamzas and ayns inside words are dropped (Hamra' -> hamra, Ko'k -> kok)."""
    s = re.sub(r"([a-z])([A-Z])", r"\1 \2", strip_accents(s)).lower().replace("ß", "ss").replace("ø", "o").replace("æ", "ae").replace("đ", "d").replace("ł", "l")
    s = re.sub(r"['`’ʼʻ‘]", "", s)
    return [w for w in re.split(r"[^a-z]+", s) if w]


def forms(stem, ends):
    return {stem + e for e in ends}


# ------------------------------------------------------------------ English
EN = {"black": "black", "white": "white", "red": "red", "green": "green", "blue": "blue", "yellow": "yellow"}
# second words that make the colour part of a plant or animal name (the place is named for the species)
EN_SPECIES = {
    "oak", "oaks", "pine", "pines", "cedar", "cedars", "gum", "gums", "walnut", "walnuts", "birch", "ash", "spruce", "maple",
    "poplar", "willow", "willows", "elm", "hickory", "cypress", "bud", "thorn", "mangrove", "mangroves", "ironbark",
    "box", "wattle", "fir", "firs", "sage", "clover", "bear", "bears", "fox", "foxes", "hawk", "hawks", "deer", "bird",
    "birds", "jay", "wing", "wings", "tail", "duck", "ducks", "swan", "swans", "heron", "eagle", "eagles", "crow",
    "crane", "cranes", "squirrel", "cow", "cows", "elephant", "sheep", "lizard", "dragon", "monkey", "lobster", "wolf", "jack", "jacket", "jackets", "fish", "salmon", "trout", "bass", "snapper",
    "horse", "horses", "cat", "dog", "mule", "bull", "bulls", "goose", "geese", "grouse", "buck", "cap", "rose",
    "roses", "lily", "lilies", "berry", "berries", "willow", "bass", "perch", "tip", "throat", "breast", "belly",
}
EN_SPECIES_PAIRS = {("blue", "grass"), ("black", "foot"), ("black", "feet"), ("yellow", "hammer"), ("white", "tail")}
EN_STOP_NEXT = {"cross", "crescent", "line", "star", "lion", "hart", "ribbon", "label", "dot", "carpet", "arrow", "planet",
                "chip", "chips", "chilli", "chili", "lantern", "bus", "rooster", "shield", "knight", "devil", "angel"}
EN_PEOPLE = {"mr", "mrs", "john", "jim", "tom", "joe", "bill", "ben", "sam", "jack", "fred"}

# ------------------------------------------------------------------ Romance
ES = {}
for st, c in (("negr", "black"), ("blanc", "white"), ("roj", "red"), ("colorad", "red"), ("amarill", "yellow")):
    for e in ("o", "a", "os", "as"):
        ES[st + e] = c
ES.update({"verde": "green", "verdes": "green", "azul": "blue", "azules": "blue"})
PT = {}
for st, c in (("pret", "black"), ("negr", "black"), ("branc", "white"), ("vermelh", "red"), ("amarel", "yellow")):
    for e in ("o", "a", "os", "as"):
        PT[st + e] = c
PT.update({"verde": "green", "verdes": "green", "azul": "blue", "azuis": "blue"})
IT = {}
for st, c in (("ner", "black"), ("bianc", "white"), ("ross", "red"), ("giall", "yellow")):
    for e in ("o", "a", "i", "e"):
        IT[st + e] = c
IT.update({"bianchi": "white", "bianche": "white", "verde": "green", "verdi": "green"})
FR = {"noir": "black", "noire": "black", "noirs": "black", "noires": "black", "blanc": "white", "blanche": "white",
      "blancs": "white", "blanches": "white", "rouge": "red", "rouges": "red", "vert": "green", "verte": "green",
      "verts": "green", "vertes": "green", "bleu": "blue", "bleue": "blue", "bleus": "blue", "bleues": "blue",
      "jaune": "yellow", "jaunes": "yellow"}
RO = {"verde": "green", "verzi": "green"}
SPANISH_CONTEXT = {"rio", "arroyo", "cerro", "canada", "canon", "mesa", "sierra", "loma", "lomas", "laguna", "agua", "aguas",
                   "ojo", "el", "la", "los", "las", "del", "de", "pena", "piedra", "piedras", "punta", "sierrita", "cienega",
                   "rito", "tinaja", "tinajas", "playa", "bahia", "isla", "valle", "llano", "cueva", "puerto", "rancho",
                   "casa", "tierra", "barranca", "charco", "pozo", "estero", "cerrito", "cerros", "monte", "morro"}
ROMANCE_SAINT = {"santa", "sainte", "ste", "san", "saint", "st", "dona", "don", "senora", "nuestra", "madame", "mme"}
ROMANCE_SURNAME_PREV = {"general", "ingeniero", "doctor", "dr", "coronel", "presidente", "colonia", "jose", "juan", "maria",
                        "pedro", "manuel", "fazenda", "familia", "hacienda", "estancia", "finca", "sitio", "chacra", "rua",
                        "avenida", "calle", "escola", "escuela", "colegio", "barrio", "ejido", "residencial"}

# ------------------------------------------------------------------ Germanic compounds
DE_STEMS = {"schwarz": "black", "weiss": "white", "weis": "white", "rot": "red", "roth": "red", "grun": "green",
            "gruen": "green", "blau": "blue", "gelb": "yellow"}
DE_INFL = ("", "e", "er", "es", "en", "em")
DE_ELEM = ("bach", "berg", "wald", "see", "stein", "burg", "feld", "au", "ach", "kopf", "horn", "wasser", "moor", "brunn",
           "quelle", "graben", "tal", "thal", "hof", "dorf", "heide", "haid", "buhl", "buehl", "bichl", "eck", "egg", "wand",
           "spitz", "kogel", "kofel", "alm", "alp", "kar", "fels", "grub", "weiher", "teich", "loch", "acker", "wies", "weg",
           "muhl", "muehl", "haus", "kirch", "ried", "moos", "hang", "lacke", "kamm", "joch", "scharte", "sand", "erd",
           "born", "siep", "bruch", "ufer", "insel", "werd", "wert", "holz", "busch", "beek", "eich", "tann", "buch",
           "fluh", "flue", "grat", "gletscher", "ferner", "kees", "kreuz", "platte", "stock", "hutte", "huette", "mauer",
           "riegel", "hugel", "huegel", "kuppe", "rucken", "ruecken", "kamp", "lehn", "leiten", "boden", "baum", "rain",
           "zell", "furt", "furth", "bronn", "reut", "bratt", "brett", "mann", "hausen", "ing", "lingen", "hahn", "kuhl", "wasser", "kirchen", "kogl", "pfuhl", "aar")
NL_STEMS = {"zwart": "black", "wit": "white", "rood": "red", "groen": "green", "blauw": "blue", "geel": "yellow"}
NL_INFL = {"zwart": ("", "e", "en"), "wit": ("", "te", "ten"), "rood": ("", "e"), "groen": ("", "e", "en"),
           "blauw": ("", "e"), "geel": ("", "e")}
NL_ELEM = ("water", "veen", "berg", "beek", "meer", "dijk", "hoek", "kerk", "broek", "bos", "bosch", "sluis", "zand", "polder",
           "ven", "horst", "wiel", "hof", "rak", "gat", "kamp", "schor", "rivier", "kop", "kloof", "kop", "krans", "fontein",
           "poort", "dal", "vlei", "pan", "heuvel", "rand", "klip", "bank", "stroom", "hoogte", "vallei", "plaas", "laagte",
           "vlakte", "duin", "molen", "haven", "kuil", "put", "bult", "kraal", "nek", "bloem", "bergs", "doorn", "sloot", "goor", "woud", "sand",
           "punt", "baken", "plaat", "singel", "rug", "klippe", "spruit", "draai", "water", "kom", "koppie", "krans")
NORD_STEMS = {"svart": "black", "sort": "black", "hvit": "white", "hvid": "white", "kvit": "white", "vit": "white", "rod": "red", "roed": "red",
              "raud": "red", "gronn": "green", "gron": "green", "groen": "green", "bla": "blue", "blaa": "blue", "gul": "yellow"}
NORD_INFL = ("", "e", "a", "t", "en", "ar", "er", "es", "s", "as", "es")
NORD_ELEM = ("berg", "fjell", "fjall", "skjer", "skjaer", "skjar", "vatn", "vann", "vand", "tjern", "tjonn", "tjarn", "tjorn",
             "sjo", "bekk", "baek", "elv", "aa", "stein", "sten", "haug", "hog", "holm", "nes", "ness", "naes", "fjord", "dal",
             "myr", "mosse", "kollen", "koll", "hammar", "hammer", "hamar", "vag", "vik", "sand", "klett", "knatt", "knut",
             "nut", "hogd", "hoyd", "ura", "lia", "lid", "lien", "mo", "rabb", "torp", "rygg", "horn", "tind", "egg", "poll", "odden", "holmen", "li", "vass", "vas", "hei", "slett", "lett", "kamp", "karr", "kaerr", "stryk", "putt", "kulp", "ufs", "fjedd", "tuv", "voll", "kobb", "asb", "asen", "ask", "asm", "ast", "aas",
             "grunn", "grund", "flu", "skar", "gjel", "botn", "kulle", "klint", "klipp", "hall", "hell", "bakk", "back",
             "sund", "fors", "kil", "varde", "foss", "fell", "jokul", "hnuk", "kamb", "ald", "hol", "bjerg", "hoj",
             "skov", "skog", "kjern", "aas", "asen", "bru", "brekk", "dok", "fjall", "grav", "hed", "jord",
             "kamm", "kjos", "kläpp", "lund", "mark", "nabb", "odde", "orn", "rev", "ror", "sel", "skall", "skallen",
             "stad", "strand", "tange", "tjonna", "tved", "uren", "vatnet", "vangen", "viken", "vatten", "ved")
NORD_END = {"a", "an", "aa", "en", "ar", "arna", "orna", "ane", "ana", "e", "er", "erne", "ene", "na", "as", "asen"}   # whole-word endings (Svarta, Rødan, Vitå)

# ------------------------------------------------------------------ Slavic
PL_STEMS = {"czarn": "black", "bial": "white", "czerwon": "red", "zielon": "green", "niebiesk": "blue", "zolt": "yellow"}
PL_BAD_END = ("ockiego", "ckiego", "ckiej", "ockiej", "ecki", "ecka", "iecki", "iecka", "eckie", "ieckie", "ecko", "inski", "inska", "owski", "owska", "kowski", "as", "asz")
ES_STEMS = {"chern": "black", "chorn": "black", "bel": "white", "bil": "white", "krasn": "red", "chervon": "red",
            "zelen": "green", "sin": "blue", "syn": "blue", "zhelt": "yellow", "zhovt": "yellow"}
ES_ADJ = ("yy", "aya", "oye", "yye", "yi", "iy", "aja", "oe", "ye", "ogo", "ykh", "yj", "ij", "yya", "aya", "uyu", "yy",
          "a", "e", "i", "o", "ya", "iye", "eye", "yaya", "ii", "ie", "ego", "yaja", "eje", "ije", "y", "ykh")
ES_DIM = ("enkiy", "enkaya", "enkoye", "enkiye", "enki", "enka", "enkoe", "enkoje", "enkij", "ushka", "yanka", "ukha", "ka", "ets",
          "oy", "uy", "ava", "ovets")
ES_SURNAME = re.compile(r"^(chernobyl|belov|chernov|krasnov|zelenov|sinits|chernysh|belous|belin|krasnik|chernyak|belyaev|belyak|zelenk|belash|belk|chernik|sinyak|beles|belg|belye[nv]|bilyk|syniak)")
ES_SAFE_BELO = re.compile(r"^(bel|chern|krasn|zelen|sin|zhelt|bil|chorn|chervon|zhovt|syn)o[a-z]{3,}$")
SS_STEMS = {"chern": "black", "cher": "black", "bel": "white", "zelen": "green", "sin": "blue"}
POLITICAL_RU = ("svobod", "gudok", "khimik", "koloni", "zorin", "kooperat", "trudovik", "voin", "kommunist", "gigant", "vostok", "oktyabr", "zvezd", "znam", "armey", "armii", "armiy", "gvard", "partizan", "pakhar", "proletar", "kommun",
                "sovet", "flot", "flag", "zarya", "zari", "put", "luch", "mayak", "voskhod", "kolkhoz", "perekop",
                "sotsial", "trud", "rabochi", "molot", "serp", "oktyabrsk", "komissar", "boyets", "geroy", "pobed",
                "kurs", "rassvet", "pervomay", "internatsional", "kazak", "zavod", "moryak", "shakht", "gorniak", "gornyak",
                "znamen", "lenin", "pioner", "partiza", "tekstil", "metallist", "pakhari", "pakhar", "zor", "polit",
                "styag", "kustar", "uzbek", "tadzhik", "turkmen", "kirgiz", "oktyabrya", "posev", "seyatel", "khimik",
                "stroitel", "ural", "moldavanin", "rybak", "ogorodnik", "dekabr", "ryad", "kavalerist", "kursant",
                "derevoobdelochnik", "les", "lesnik", "pakhat", "kolos", "niv", "pole")
POLITICAL_RU_ROOT = ("krasnoarm", "krasnogvard", "krasnoznam", "krasnoflot", "krasnopartiz", "krasnooktyabr",
                     "krasnozvezd", "krasnoperekop", "krasnokommun", "chervonoarm", "chervonozn", "chervonohrad",
                     "chervonopart", "chervonozavod")

# ------------------------------------------------------------------ Turkic, Arabic, Persian
TR = {"kara": "black", "qara": "black", "qareh": "black", "qarah": "black", "ak": "white", "aq": "white", "akh": "white",
      "kizil": "red", "kyzyl": "red", "qizil": "red", "qyzyl": "red", "qezel": "red", "qizl": "red", "kyzl": "red",
      "yesil": "green", "yashil": "green", "yeshil": "green", "gok": "blue", "kok": "blue", "kuk": "blue", "gog": "blue",
      "sari": "yellow", "sary": "yellow", "sariq": "yellow", "saryg": "yellow", "sarygh": "yellow", "sarygy": "yellow"}
TR_PREFIX = {"kara": "black", "kizil": "red", "kyzyl": "red", "qizil": "red", "yesil": "green", "sari": "yellow", "sary": "yellow", "gok": "blue",
             "goek": "blue", "gokce": "blue", "goekce": "blue", "akca": "white", "akce": "white", "kizilca": "red", "sarica": "yellow"}
TR_DIM = {"akca": "white", "akcа": "white", "gokce": "blue", "goekce": "blue", "kizilca": "red", "sarica": "yellow", "yesilce": "green"}   # the -ish forms, whole words
TR_ELEM = ("su", "dag", "dagh", "tau", "tag", "tagh", "tepe", "tobe", "kol", "kul", "gol", "bulak", "bulag", "pinar", "say",
           "kum", "qum", "tash", "tas", "yar", "jar", "kaya", "qaya", "deniz", "koy", "kyshlak", "kishlak", "aul", "chay",
           "cay", "irmak", "dere", "darya", "ova", "saray", "sehir", "hisar", "kent", "kend", "kand", "kurgan", "kale",
           "kala", "qala", "agac", "tal", "bel", "burun", "ada", "kir", "kuduk", "quduq", "ozen", "uzen", "kamys", "kamis",
           "yazi", "yurt", "oba", "pinar", "gol", "goller", "dagi", "tepesi", "deresi", "suyu", "kaya", "bayir", "yayla",
           "orman", "kiriz", "kuyu", "cesme", "ceshme", "bugaz", "bogaz", "ozek", "kamysh", "zhar", "zhal", "dzhar", "sor",
           "koey", "oren", "oeren", "cimen", "seki", "cukur", "cayir", "bulak", "pinar", "dag", "goel", "kul", "tobe", "tyube", "su")
TR_STOP_IR = {"sari"}       # Sari in Iran is the Persian city of Mazandaran, not "yellow"
AR = {}
for w, c in (("aswad", "black"), ("sawda", "black"), ("sawdah", "black"), ("suwayda", "black"), ("suwaydah", "black"),
             ("sud", "black"), ("abyad", "white"), ("bayda", "white"), ("baydah", "white"), ("bid", "white"), ("biyad", "white"),
             ("ahmar", "red"), ("hamra", "red"), ("hamrah", "red"), ("hamraa", "red"), ("humr", "red"), ("humayra", "red"),
             ("akhdar", "green"), ("khadra", "green"), ("khadrah", "green"), ("khudr", "green"), ("khudayra", "green"),
             ("azraq", "blue"), ("zarqa", "blue"), ("zarqah", "blue"), ("zurq", "blue"), ("asfar", "yellow"), ("safra", "yellow"),
             ("safrah", "yellow"), ("sufr", "yellow"), ("abiad", "white"), ("beida", "white"), ("beidha", "white"), ("baida", "white"),
             ("hamra", "red"), ("hamrat", "red"), ("lahmar", "red"), ("lakhdar", "green"), ("khedra", "green"), ("khadhra", "green"),
             ("lazreg", "blue"), ("zerga", "blue"), ("zarga", "blue"), ("sefra", "yellow"), ("safar", None), ("lebiod", "white"),
             ("labiad", "white"), ("lakhal", "black"), ("kahla", "black"), ("souda", "black"), ("sauda", "black"), ("aswed", "black")):
    if c:
        AR[w] = c
FA = {"siah": "black", "siyah": "black", "seyah": "black", "syah": "black", "siya": "black", "seyyah": None,
      "sefid": "white", "safid": "white", "sepid": "white", "sapid": "white", "safed": "white", "sufaid": "white", "sufed": "white",
      "sorkh": "red", "surkh": "red", "sorkheh": "red", "sabz": "green", "sabzi": "green", "sabzeh": "green", "zard": "yellow",
      "zardeh": "yellow", "kabud": "blue", "kabut": "blue",
      "sorkhi": "red", "siahi": "black", "zardi": "yellow", "sabzi": "green", "sefidi": "white"}
FA = {k: v for k, v in FA.items() if v}
FA_ELEM = ("ab", "rud", "kuh", "koh", "sang", "deh", "chashmeh", "cheshmeh", "abad", "kan", "dasht", "darreh", "dareh", "tappeh",
           "chal", "khani", "ali", "ban", "kamar", "posht", "sar", "mard", "kal", "gol", "gul", "bid", "ak")

# ------------------------------------------------------------------ Chinese and Japanese characters
ZH = {"黑": "black", "白": "white", "红": "red", "紅": "red", "绿": "green", "綠": "green", "蓝": "blue", "藍": "blue",
      "黄": "yellow", "黃": "yellow", "青": "grue"}
ZH_SURNAME = re.compile(r"[黑白红紅黄黃青蓝藍][家庄莊屋厝宅氏寨]")
ZH_STOP = re.compile(r"硫黄|硫黃|黄金|黃金|白蚁|白蟻|黄柏|黃柏|黄檗|白果|青年|青龙|青龍|白龙|白龍|黄龙|黃龍|红军|红旗|紅旗|红星|紅星|红光|紅光|红卫|紅衛|红专|红联|紅聯|红胜|紅勝|红跃|红进|红新|红丰|红岩村?")
ZH_POLITICAL = re.compile(r"红旗|紅旗|红星|紅星|红光|紅光|红卫|紅衛|红军|紅軍|红专|紅專|红联|紅聯|红胜|紅勝|红跃|紅躍|红进|紅進|红色|紅色|红太阳|红日|红阳|红新|红丰|紅豐|红卫兵|红心|红前|红江")
ZH_DRAGON = re.compile(r"青龙|青龍|白龙|白龍|黄龙|黃龍|黑龙|黑龍")   # the dragons of the four directions and Heilongjiang: kept, a colour name
JA = {"黒": "black", "白": "white", "赤": "red", "紅": "red", "緑": "green", "黄": "yellow", "青": "grue"}
JA_STOP = re.compile(r"硫黄|面白|白鳥|赤十字|黄金|白山神社")
CJK = re.compile(r"[぀-ヿ一-鿿]")


def native_name(alt, name, country):
    """The place's own name in Chinese or Japanese script: the longest alternate name written in it (GeoNames lists
    the short and full forms, such as 黄坪 and 黄坪镇)."""
    best = ""
    for a in alt.split(","):
        a = a.strip()
        if a and CJK.search(a) and not re.search(r"[A-Za-z]", a):
            if country == "JP" and re.fullmatch(r"[぀-ヿ・]+", a):
                continue   # kana spellings carry no colour character
            if len(a) > len(best):
                best = a
    return best


def compound(token, stems, infl, elems, min_rest=1):
    """(stem, colour) if token is stem + an inflection + a known landscape word, or stem + inflection alone."""
    for st, c in stems.items():
        if not token.startswith(st):
            continue
        rest = token[len(st):]
        for e in sorted(infl, key=len, reverse=True):
            if rest == e:
                return st, c
            if e and not rest.startswith(e):
                continue
            r2 = rest[len(e):]
            if len(r2) >= min_rest and any(r2.startswith(x) for x in elems):
                return st, c
    return None


def classify(r):
    """r: a dict-like row with name, asciiname, alternatenames, cc, fclass, fcode."""
    cc = r["cc"]
    raw = r["asciiname"] or r["name"]
    W = words(raw)
    hits = []

    def hit(colour, word, lang, flag=""):
        if not any(h["colour"] == colour for h in hits):
            hits.append({"colour": colour, "word": word, "lang": lang, "flag": flag})

    # ---- Chinese and Japanese: characters only (romanised syllables like bai or hong have too many other meanings)
    if cc in CHINESE or cc in JAPANESE:
        nat = native_name(r["alternatenames"], r["name"], cc)
        if not nat:
            return [], "no_native_script"
        if cc in CHINESE:
            if r["fcode"] == "GRAZ" or nat.startswith("姓"):
                return [], "transliteration"                       # Tibetan and Mongol pasture names written in sound
            s = ZH_SURNAME.sub("", nat)   # Huang-jia, Bai-jia ...: family names, not colours
            pol = bool(ZH_POLITICAL.search(nat))
            s2 = ZH_STOP.sub("", s) if not pol else s
            for ch, c in ZH.items():
                if ch in s2:
                    hit(c, ch, "zh", "political" if (pol and c == "red") else "")
            if not hits:
                return [], ("surname" if ZH_SURNAME.search(nat) else "stop_phrase" if ZH_STOP.search(nat) else "no_colour_char")
        else:
            s = JA_STOP.sub("", nat)
            for ch, c in JA.items():
                if ch in s:
                    hit(c, ch, "ja")
            if not hits:
                return [], "no_colour_char"
        # an English or other Latin colour word in a Chinese or Japanese name (hotels and the like) is not counted
        return hits, ""

    lower_name = raw.lower()
    for i, w in enumerate(W):
        prev = W[i - 1] if i else ""
        nxt = W[i + 1] if i + 1 < len(W) else ""

        # ---- English (anywhere; most rows outside the English-speaking world are hotels, which are not counted)
        if w in EN:
            c = EN[w]
            if re.search(r"\b" + w + r"[’']s\b", lower_name):
                continue                                           # White's Creek: a surname
            if prev in EN_PEOPLE or nxt in EN_STOP_NEXT:
                continue
            if c == "green" and cc in ("GB", "IE") and r["fclass"] == "P" and i == len(W) - 1 and i > 0:
                continue                                           # Bethnal Green: a village green, a common
            if (nxt in EN_SPECIES or (w, nxt) in EN_SPECIES_PAIRS):
                hit(c, w, "en", "species")
            else:
                hit(c, w, "en")
            continue

        # ---- Spanish, Portuguese, Italian, Romanian, French
        lang = None
        if cc in PORTUGUESE and w in PT:
            lang, c = "pt", PT[w]
        elif cc in ITALIAN and w in IT:
            lang, c = "it", IT[w]
        elif cc in ROMANIAN and w in RO:
            lang, c = "ro", RO[w]
        elif w in FR and cc not in PORTUGUESE:
            lang, c = "fr", FR[w]
        elif w in ES and cc not in PORTUGUESE and cc not in ITALIAN and cc not in ROMANIAN:
            lang, c = "es", ES[w]
        elif cc == "CH" and w in IT:
            lang, c = "it", IT[w]
        if lang:
            if prev in ROMANCE_SAINT:
                continue
            if w in ("negro", "negros", "negra", "negras", "preto", "pretos", "amarelos") and prev in ("do", "dos", "del", "da", "das", "de", "los"):
                continue                                           # Casa do Preto, Cruz del Negro: a person                                           # Santa Blanca, Sainte-Blanche: a saint
            if lang in ("es", "pt") and w in ("rojas", "rojo", "branco", "blanco", "preto", "negro") and prev in ROMANCE_SURNAME_PREV:
                continue                                           # Colonia Rojas, Fazenda Branco: surnames
            if lang == "es" and w == "rojas" and not prev.endswith("s"):
                continue                                           # Rojas is above all a surname
            if cc in ("US", "CA", "AU", "NZ", "GB") and lang == "es":
                ctx = set(W) & SPANISH_CONTEXT
                if w.startswith("negr") and not ctx:
                    continue                                       # "Negro Creek": named for people, not the colour
                if w.startswith("colorad") and not ctx and lower_name != "colorado river":
                    continue                                       # Colorado Springs, Colorado City: the state
            if lang == "it" and w in ("nero", "nera") and (W == [w] or prev in ("sul", "del", "di", "val", "valle")):
                continue                                           # the river Nera (Latin Nar) and Nero
            if lang == "fr" and w in ("blanche", "blanches") and set(W) & {"lake", "lady", "river", "creek", "mount", "island", "point", "mills", "street", "lakes"}:
                continue                                           # Lake Blanche, Lady Blanche: a woman's name in English
            if lang in ("it", "es", "pt") and r["fcode"] in ("VIN", "AMUS") :
                continue
            hit(c, w, lang)
            continue

        # ---- German
        if cc in GERMAN:
            m = compound(w, DE_STEMS, DE_INFL, DE_ELEM)
            if m and not w.startswith("rott") and w != "roth":
                hit(m[1], w, "de")
                continue
        # ---- Dutch and Afrikaans
        if cc in DUTCH:
            m = compound(w, NL_STEMS, ("", "e", "en", "te", "ten"), NL_ELEM)
            if m and w not in ("rode", "geel", "witt") and not (w == "wit" and W == [w]):
                hit(m[1], w, "nl")
                continue
        # ---- Nordic
        if cc in NORDIC:
            m = compound(w, NORD_STEMS, NORD_INFL, NORD_ELEM) or next(((st, c) for st, c in NORD_STEMS.items() if w.startswith(st) and w[len(st):] in NORD_END), None)
            if m and r["fclass"] == "P" and w in ("rod", "roed", "rode"):
                m = None                                           # Rød, Röd farms: rjóðr, a clearing
            if m and not w.startswith(("gull", "vitt", "blak", "gulf", "rodd", "blab", "sorte" + "r", "sortl", "vital", "vitak", "vitar", "vitan", "vitas" + "ari")) and not (cc == "FI" and re.search(r"(lahti|järvi|jarvi|joki|oja|suo|vaara|niemi|saari|kangas|mäki|maki|lampi|kallio|vuori|aapa|neva|harju|koski|salmi|selkä|selka|kylä|kyla|ikko|nen|la|pakka)$", w)):
                hit(m[1], w, "nord")
                continue
        # ---- Polish
        if cc in POLISH:
            for st, c in PL_STEMS.items():
                if w.startswith(st) and not w.endswith(PL_BAD_END) and len(w) > len(st) and not re.search(r"(ow|owo|owa|owice|ewo|in|yn|ynin|ocin|kowie|owizna|czyn|ek|ec|cz|ki|ko|kow|ezyn|owka)$", w[len(st):] if not w[len(st):] in ("y", "a", "e", "i", "ego", "ej", "ym", "ych", "ki", "ka", "ke") else "-"):
                    hit(c, w, "pl")
                    break
            continue
        # ---- Russian, Ukrainian, Belarusian (GeoNames' romanisation)
        if cc in EASTSLAV:
            matched = None
            for st, c in ES_STEMS.items():
                if not w.startswith(st):
                    continue
                rest = w[len(st):]
                if rest in ES_ADJ or rest in ES_DIM or ES_SAFE_BELO.match(w):
                    if ES_SURNAME.match(w) and not (rest in ES_ADJ):
                        continue
                    if rest not in ES_ADJ and re.search(r"(ov|ova|ovo|ev|eva|evo|ovka|evka|ovtsy|ovichi|ovich|ino|ina|ikha|yn|yna|evichi)$", w):
                        continue                                   # Belogurov, Zheltonogovo: from a family name
                    if st == "sin" and rest not in ("iy", "yaya", "eye", "iye", "ii", "ie", "yaja", "eje", "ije", "ego", "ey", "yaya", "yuyu", "ii", "ij", "ya") and not w.startswith(("sinegor", "sineozer", "sinerech", "sinevod", "sinyavin")):
                        continue
                    if st == "bil" and rest not in ("a", "e", "yi", "i", "yy", "ii", "ij") and not w.startswith(("bilo", "bilho")):
                        continue
                    if st == "syn" and rest not in ("ia", "ya", "ie", "ye", "ii", "iy", "yi", "i", "e"):
                        continue
                    matched = (c, st)
                    break
            if matched:
                c, st = matched
                flag = ""
                if c == "red":
                    if w.startswith(POLITICAL_RU_ROOT) or any(x.startswith(POLITICAL_RU) for x in W if x != w):
                        flag = "political"
                hit(c, w, "eslav", flag)
                continue
        # ---- Bulgarian, Serbian, Macedonian
        if cc in SOUTHSLAV:
            m = None
            for st, c, fs in (("chern", "black", ("a", "o", "i", "e", "ata", "ite", "iya")), ("cheren", "black", ("",)),
                              ("bel", "white", ("a", "o", "i", "e", "ata", "ite", "iya")), ("zelen", "green", ("", "a", "o", "i", "e", "ata", "ite")),
                              ("sin", "blue", ("ya", "yo", "i", "ia", "e"))):
                if w.startswith(st):
                    rest = w[len(st):]
                    if rest in fs or (st in ("chern", "bel", "zelen") and rest[:1] == "o" and len(rest) >= 5):
                        m = c
                        break
            if m:
                hit(m, w, "sslav")
                continue
        # ---- Turkic
        if cc in TURKIC:
            c = TR.get(w) or (TR_DIM.get(w) if cc == "TR" else None)
            if c and w == "gok" and re.search(r"\bGOK\b", raw):
                c = None                                           # GOK: a Russian mining-works acronym
            if c and w in ("sari",) and cc in ("RU", "IR", "AF", "GR", "CY"):
                c = None                                           # Sari: the Persian city; Finnic saari, island
            if c and not (cc == "IR" and w in TR_STOP_IR) and not (cc in ("IR", "AF") and w in ("kuk", "gog")):
                if not (w == "ak" and cc in ("CN",)) and not (cc in ARAB and w in ("sari", "sary")):
                    hit(c, w, "tr")
                    continue
            m = compound(w, TR_PREFIX, ("",), TR_ELEM, min_rest=2)
            if m and cc not in ("IR", "AF", "IQ", "SY") and not w.startswith(("karaman", "sarims", "sarimsak")):
                hit(m[1], w, "tr")
                continue
        # ---- Arabic
        if cc in ARAB or cc in ("IR", "TR"):
            c = AR.get(w) or (AR.get(w[2:]) if w.startswith(("al", "el")) and len(w) > 5 else None)
            if c and cc in ("IR", "TR") and not (set(W) & {"al", "el", "as", "az", "ash", "umm", "jabal", "wadi", "tall", "bir", "ras", "ain", "ayn"}):
                c = None
            if c and not (w == "bid" and cc not in ARAB) and not (w == "sud" and prev not in ("al", "as", "jibal", "jabal")):
                hit(c, w, "ar")
                continue
        # ---- Persian
        if cc in PERSIAN:
            c = FA.get(w)
            if not c:
                m = compound(w, {k: v for k, v in FA.items() if len(k) >= 4}, ("", "eh", "e"), FA_ELEM, min_rest=2)
                c = m[1] if m else None
            if c:
                hit(c, w, "fa")
                continue

    if hits:
        return hits, ""
    return [], "no_rule"


# ================================================================== the supplement (a second, wider GeoNames pass)
# Rows come tagged by the search that found them: en_compound, turkic_compound, nordic_kvit, mongolian, hindi_urdu,
# korean. Each tag has its own rule; all are stricter than the search, because a prefix match finds many false friends.

# ---- English compounds (Blackburn, Whitby, Redcar). The second part must be a landscape element of English place names,
# taken at the compound boundary; English Red- is often Old English hreod (reed) or a Celtic ryd/rhyd (ford), Whit- a
# personal name (Hwita), so those stems have their own, shorter lists; surnames are stopped in the New World.
EN_ELEM_ALL = ("water", "burn", "pool", "hill", "heath", "rock", "stone", "wood", "moor", "more", "mere", "field", "ford", "brook",
               "beck", "well", "cliff", "clough", "dale", "down", "fell", "head", "haven", "lake", "land", "law", "leaf", "ley", "lough",
               "marsh", "mount", "mountain", "pond", "ridge", "river", "sand", "sands", "scar", "shaw", "side", "tarn", "ton", "town",
               "vale", "wall", "wick", "wich", "worth", "bank", "banks", "bay", "bridge", "butte", "creek", "gate", "hall", "house",
               "island", "isle", "knob", "knoll", "point", "rocks", "spring", "springs", "stream", "top", "valley", "church", "cross",
               "combe", "comb", "by", "acre", "acres", "lea", "law", "loch", "edge", "hope", "how", "car", "carr", "ditch", "hithe",
               "fen", "fork", "run", "gill", "ghyll", "chapel", "castle", "stable", "lands", "rigg", "hurst")
EN_WHITE_GB = ("by", "church", "well", "stable", "burn", "field", "ley", "more", "wick", "haven", "combe", "ford", "acre", "chapel", "cliffe", "cliff", "side", "law", "hill", "kirk", "hough", "head", "craig", "rigg", "sand", "stone", "water", "wood", "lee")
EN_RED_OK = ("hill", "hills", "cliff", "cliffe", "car", "carr", "ditch", "bank", "banks", "rock", "rocks", "stone", "scar", "land", "lands", "bridge", "water", "creek", "lake", "mountain", "butte", "point", "head", "earth", "sand", "sands", "clay", "spring", "springs", "cliffs")
EN_SURNAME = {"blackburn", "blackwell", "blackmore", "blackman", "blackstone", "blackwood", "blackford", "blackledge", "blackmon", "blacklock",
              "blackshear", "blackley", "blacksher", "blackston", "blackton", "greenwood", "greenfield", "greenway", "greenberg", "greenhalgh",
              "greenhill", "greenland", "greenlee", "greenleaf", "greenough", "greenwell", "greenhouse", "greenland", "greenwalt", "greenville",
              "greensboro", "greensburg", "greenburg", "greening", "whitehead", "whiteman", "whitehouse", "whitfield", "whitford", "whitley",
              "whitmore", "whitworth", "whitby", "whitcomb", "whitwell", "whitburn", "whitlock", "whitmire", "whitten", "whitton", "whitehurst",
              "whitesell", "whiteside", "whitesides", "whitener", "redford", "redman", "redmond", "redding", "reddington", "redfield", "redmon",
              "bluestone", "whitacre", "whitaker", "whiteley", "blackburne", "greenhow", "redwine", "whitefield"}
EN_SPECIES_C = ("redwood", "redgum", "redbud", "redfish", "redcedar", "redtail", "redwing", "redhorse", "redstart", "redpoll", "bluebird",
                "bluebell", "bluegrass", "bluewing", "bluegill", "blueberry", "bluejay", "bluestem", "bluejoint", "blackbird", "blackberry",
                "blackbutt", "blackthorn", "blackjack", "blackhawk", "blackfoot", "blackfeet", "blackfish", "blackcap", "blackcock", "blackgum",
                "blackoak", "blackhaw", "blackwillow", "blacktail", "blacksmith", "blackfriars", "blackguard", "whitetail", "whitefish", "whitethorn",
                "whitebark", "whitefriars", "whiteoak", "whitepine", "greenbrier", "greenbriar", "greenhorn", "greenback",
                "greenleaf", "greenwing", "yellowjacket", "yellowhammer", "yellowtail", "yellowwood", "yellowlegs", "redbreast", "greenling", "blackmouth")
NEWWORLD = {"US", "CA", "AU", "NZ", "ZA"}
OLDWORLD = {"GB", "IE", "IM", "JE", "GG"}


def en_compound(r):
    W = words(r["asciiname"] or r["name"])
    cc = r["cc"]
    for w in W:
        if w.endswith("s") and w[:-1] in EN_SURNAME:
            continue
        if w.startswith(EN_SPECIES_C):
            return [], "species"
        if cc in NEWWORLD and (w in EN_SURNAME or re.search(r"(ville|burg|boro|borough|ton)$", w)):
            continue                                                # Blackwell, Greenville: a surname or a town named after one
        for st, c in (("black", "black"), ("white", "white"), ("whit", "white"), ("red", "red"), ("green", "green"), ("blue", "blue"), ("yellow", "yellow")):
            if not w.startswith(st):
                continue
            rest = w[len(st):]
            if st == "whit" and (rest.startswith("e") or cc not in OLDWORLD):
                break                                               # whit- alone only in Britain and Ireland (Whitby, Whitchurch)
            if st == "green" and rest.startswith(("e", "ock", "ough", "s")):
                break                                               # Greene (surname), Greenock (Gaelic grianaig)
            if st == "red" and rest.startswith(("d", "r", "ruth", "mi", "ma", "bo", "gr", "wi", "ford", "e", "ing", "an", "n")):
                break                                               # Redditch? see below; Redruth (Cornish rhyd), Redmire, Redbourn (hreod, reed)
            elems = EN_WHITE_GB if st == "whit" else EN_RED_OK if st == "red" else EN_ELEM_ALL
            if rest and any(rest == e or (rest.startswith(e) and len(rest) - len(e) <= 1) for e in elems):
                return [{"colour": c, "word": w, "lang": "en", "flag": ""}], ""
            break
        if w == "redditch":
            return [{"colour": "red", "word": w, "lang": "en", "flag": ""}], ""   # the red ditch, from its red clay
    return [], "no_rule"


# ---- Turkic compounds (Aksu, Karakol, Kızılırmak, Göksu, Sarıyer): the stem at the start of the word, the second part a
# Turkic (or, in Iran and Afghanistan, Persian) landscape word
TR_ST = (("kyzyl", "red"), ("qyzyl", "red"), ("kizil", "red"), ("qizil", "red"), ("qezel", "red"), ("kara", "black"), ("qara", "black"),
         ("qarah", "black"), ("qareh", "black"), ("yesil", "green"), ("yashil", "green"), ("goek", "blue"), ("gok", "blue"), ("kok", "blue"),
         ("koek", "blue"), ("kuk", "blue"), ("sary", "yellow"), ("sari", "yellow"), ("aq", "white"), ("ak", "white"))
TR_EL2 = TR_ELEM + ("tepa", "debe", "dara", "darya", "cicek", "dagh", "bel", "bulaq", "bulagh", "bolagh", "bolaq", "chay", "chai", "kand", "kend",
                    "darreh", "dareh", "tappeh", "cheshmeh", "chashma", "gol", "kol", "kul", "kuel", "goel", "koel", "suu", "ozen", "ozek", "zhal",
                    "zhar", "tas", "tash", "kamys", "kamysh", "kum", "qum", "sor", "kuduk", "quduq", "terek", "kain", "kaiyn", "kayin", "tal", "yar",
                    "jar", "jol", "yol", "kaya", "qaya", "ova", "uzen", "oy", "say", "sai", "soy", "bulak", "kol", "koey", "koy", "oren", "oeren",
                    "pinar", "punar", "saray", "sehir", "shahr", "kent", "kala", "qala", "qal", "agac", "agach", "aghach", "tau", "tag", "tagh",
                    "dag", "tepe", "tobe", "tyube", "deniz", "dere", "irmak", "su", "toprak", "kum", "yazi", "yayla", "oba", "kurgan", "ada",
                    "burun", "boyun", "bash", "bel", "togay", "tokay", "kemer", "cesme", "ceshme", "kopru", "guney", "mazar", "tuz",
                    "chal", "kamar", "kotal", "jilga", "dzhilga", "art", "kiya")
TR_STOP = ("karaca", "karaman", "karam", "akhund", "akhl", "akhi", "akar", "aqa", "akro", "aksent", "kokan", "kokol", "kokor", "sarim",
           "karabas", "karabash", "akhtar", "akbar", "karagoz", "karagoez")


def turkic_compound(r):
    cc = r["cc"]
    if cc in ("CN",) or cc not in TURKIC | {"CY", "UA", "MN"}:
        return [], "outside_area"
    for w in words(r["asciiname"] or r["name"]):
        if w.startswith(TR_STOP):
            continue
        for st, c in TR_ST:
            if not w.startswith(st):
                continue
            rest = w[len(st):]
            for infl in ("", "a", "e", "ca", "ce", "ja", "cha", "y", "i"):
                if not rest.startswith(infl):
                    continue
                r2 = rest[len(infl):]
                if len(r2) >= 2 and any(r2 == e or (r2.startswith(e) and len(e) >= 3) for e in TR_EL2):
                    if c == "blue" and st in ("kok", "kuk", "koek") and cc in ("IR", "AF", "TR"):
                        break
                    return [{"colour": c, "word": w, "lang": "tr", "flag": ""}], ""
            break
    return [], "no_rule"


# ---- Norwegian and Danish kvit, hvid (white)
def nordic_kvit(r):
    for w in words(r["asciiname"] or r["name"]):
        for st in ("kvit", "hvid"):
            if w.startswith(st) and not w.startswith(("kvitt", "hvidov")):
                rest = w[len(st):]
                if rest in NORD_END or rest == "" or compound(w, {st: "white"}, NORD_INFL, NORD_ELEM + ("ur", "ing", "gyr", "ku", "floy", "fonn", "hatt", "geit", "cohkk", "kal", "egg", "an", "aa", "e")):
                    return [{"colour": "white", "word": w, "lang": "nord", "flag": ""}], ""
    return [], "no_rule"


# ---- Mongolian (khar, tsagaan, ulaan, nogoon, khökh, shar), in Mongolia, Inner Mongolia, Buryatia, Kalmykia and Tuva
MN_W = {"khar": "black", "khara": "black", "har": "black", "hara": "black", "tsagaan": "white", "tsagan": "white", "tsaagan": "white",
        "sagan": "white", "tsagaany": "white", "ulaan": "red", "ulan": "red", "ulaany": "red", "nogoon": "green", "nogoony": "green",
        "khokh": "blue", "khukh": "blue", "hoh": "blue", "khoh": "blue", "kokh": "blue", "shar": "yellow", "shara": "yellow", "sharyn": "yellow"}
MN_EL = ("nuur", "nur", "gol", "us", "uul", "ula", "tolgoy", "tologoy", "bulag", "bulak", "hudag", "khudag", "ovoo", "obo", "tal", "khad", "had",
         "denzh", "davaa", "daban", "baatar", "ude", "khoto", "hot", "sum", "gorkhon", "usu", "elis", "ereg", "nuruu", "khushuu", "hushuu")


def mongolian(r):
    cc = r["cc"]
    raw = r["asciiname"] or r["name"]
    toks = words(raw)
    for i, w in enumerate(toks):
        c = MN_W.get(w)
        if c and cc == "RU":
            hyph = re.search(r"\b" + w + r"-", raw.lower()) or re.search(r"-" + w + r"\b", raw.lower())   # Buryat Khara-Gol; not Russian Matochkin Shar
            if w in ("shar", "khar", "har", "hara", "ulan", "sagan") and not hyph:
                c = None                                            # Russian shar, a strait (Matochkin Shar); Khar alone
            elif not hyph and w not in ("tsagaan", "tsagan", "ulaan", "nogoon"):
                c = None
        if c and cc not in ("MN", "RU", "CN"):
            c = None
        if c:
            pol = w.startswith("ulan") and ("ude" in toks or "baatar" in toks)
            return [{"colour": c, "word": w, "lang": "mn", "flag": "political" if pol else ""}], ""
        for st, cc2 in MN_W.items():
            if len(st) >= 5 and w.startswith(st) and any(w[len(st):].startswith(e) for e in MN_EL) and (cc == "MN" or (cc == "RU" and st in ("tsagaan", "tsagan", "ulaan", "nogoon"))):
                pol = w in ("ulaanbaatar", "ulanbator")
                return [{"colour": cc2, "word": w, "lang": "mn", "flag": "political" if pol else ""}], ""
    return [], "no_rule"


# ---- Hindi, Urdu, Nepali and Bengali (kala, lal, safed, hara, nila, pila): the colour word beside a landscape word, so that
# personal names (Lal Khan, Moti Lal, Hari Singh) and the goddess Kali are not counted
HI_W = {"kala": "black", "kali": "black", "kalo": "black", "kale": "black", "safed": "white", "sufaid": "white", "lal": "red", "hara": "green",
        "hari": "green", "harra": "green", "nila": "blue", "neela": "blue", "nilo": "blue", "pila": "yellow", "peela": "yellow", "pilo": "yellow"}
HI_EL = {"pani", "pahar", "pahari", "parbat", "nala", "nalla", "nadi", "dhar", "dhara", "khola", "gad", "gadh", "ban", "pathar", "patthar", "mitti",
         "tibba", "tal", "taal", "kund", "chashma", "koh", "sar", "jhil", "dongar", "dongri", "ghat", "khad", "khal", "dheri", "danda", "kot", "pul",
         "pokhri", "pokhar", "tilla", "tila", "talao", "tank", "darra", "jabba", "jheel", "chhara", "kuan", "parvat", "giri", "dhaura", "tanda"}


def hindi_urdu(r):
    if r["cc"] not in ("IN", "PK", "NP", "BD"):
        return [], "outside_area"
    W = words(r["asciiname"] or r["name"])
    for i, w in enumerate(W):
        c = HI_W.get(w)
        if c and i + 1 < len(W) and W[i + 1] in HI_EL:
            return [{"colour": c, "word": w + " " + W[i + 1], "lang": "hi", "flag": ""}], ""
    return [], "no_rule"


# ---- Korean: the colour hanja where GeoNames gives them (紅 for hong, as hong is also the family name 洪), otherwise only
# hangul compounds whose meaning is unambiguous (흑 black; 백사, 백석, 백운, 백두 white sand, stone, cloud, head; 청산, 청룡, 청송
# green hills, blue dragon, green pine; 황토, 황룡 yellow earth, yellow dragon)
KO_HANJA = {"黑": "black", "白": "white", "紅": "red", "綠": "green", "绿": "green", "黃": "yellow", "黄": "yellow", "靑": "grue", "青": "grue"}
KO_HANGUL = (("흑", "black"), ("백사", "white"), ("백석", "white"), ("백운", "white"), ("백두", "white"), ("백암", "white"), ("백설", "white"),
             ("청산", "grue"), ("청룡", "grue"), ("청송", "grue"), ("황토", "yellow"), ("황룡", "yellow"))


def korean(r):
    if r["cc"] not in ("KR", "KP"):
        return [], "outside_area"
    alts = [a.strip() for a in r["alternatenames"].split(",")]
    han = [a for a in alts if re.search(r"[一-鿿]", a) and not re.search(r"[A-Za-z぀-ヿ]", a)]
    if han:
        h = max(han, key=len)
        for ch, c in KO_HANJA.items():
            if ch in h and not re.search(ch + "[家氏]", h):
                return [{"colour": c, "word": ch, "lang": "ko", "flag": ""}], ""
        return [], "no_colour_char"
    hg = [a for a in alts if re.fullmatch(r"[가-힣\s]+", a)]
    for a in hg:
        for p, c in KO_HANGUL:
            if a.startswith(p):
                return [{"colour": c, "word": p, "lang": "ko", "flag": ""}], ""
    return [], "no_rule"


SUPP = {"en_compound": en_compound, "turkic_compound": turkic_compound, "nordic_kvit": nordic_kvit, "mongolian": mongolian,
        "hindi_urdu": hindi_urdu, "korean": korean}


def classify_supp(tag, r):
    if tag == "turkic_compound":
        hits, why = classify(r)                  # whole words the first pass did not see (Qarah Kol)
        if hits:
            return hits, why
    return SUPP[tag](r)
