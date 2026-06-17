#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a high-yield French Anki deck (.apkg) for pediatric orthopedic trauma
from the parsed Marrakech thesis websites (membre supérieur & inférieur)."""
import json, re, os, html, hashlib, csv, io
import genanki
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))          # anki/build/
ROOT = os.path.dirname(os.path.dirname(HERE))             # repo root
OUT  = os.path.join(ROOT, "anki")
MEDIA_DIR = os.path.join(HERE, "media")
os.makedirs(OUT, exist_ok=True)
os.makedirs(MEDIA_DIR, exist_ok=True)
os.chdir(ROOT)                                            # image paths are repo-relative

cases  = json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))
prereq = json.load(open(os.path.join(HERE, "prereq.json"), encoding="utf-8"))

# ---------------------------------------------------------------- helpers
def esc(t):
    return html.escape(t).replace("\n", "<br>")

def nl2br(t):
    # turn bullet/line structure into HTML
    t = html.escape(t)
    lines = [l.strip() for l in t.split("\n") if l.strip()]
    out = []
    for l in lines:
        if l.startswith("- "):
            out.append("<li>%s</li>" % l[2:])
        else:
            out.append(l)
    # wrap consecutive <li> in <ul>
    htmlout = []
    inul = False
    for l in out:
        if l.startswith("<li>"):
            if not inul:
                htmlout.append("<ul>"); inul = True
            htmlout.append(l)
        else:
            if inul:
                htmlout.append("</ul>"); inul = False
            htmlout.append(l)
    if inul: htmlout.append("</ul>")
    return "<br>".join(x for x in htmlout).replace("</ul><br>", "</ul>").replace("<br><ul>", "<ul>")

# ------------------------------------------------------- media (resize)
_media_cache = {}
_media_files = set()
def add_media(path):
    if not path or not os.path.exists(path):
        return None
    if path in _media_cache:
        return _media_cache[path]
    h = hashlib.md5(path.encode()).hexdigest()[:10]
    fname = "potec_%s.jpg" % h
    dest = os.path.join(MEDIA_DIR, fname)
    try:
        im = Image.open(path)
        im = im.convert("RGB")
        w, h2 = im.size
        if w > 1000:
            im = im.resize((1000, int(h2 * 1000 / w)), Image.LANCZOS)
        im.save(dest, "JPEG", quality=82, optimize=True)
    except Exception as e:
        print("  media err", path, e); return None
    _media_cache[path] = fname
    _media_files.add(dest)
    return fname

def img_tags(paths, cls="rad"):
    out = []
    for p in paths:
        f = add_media(p)
        if f:
            out.append('<img class="%s" src="%s">' % (cls, f))
    return "".join(out)

# ------------------------------------------------------- classification
REGION_MS = {"Epaule": ("Epaule", "Clavicule"), "Bras": ("Bras",),
             "Coude": ("Coude",), "Avant-bras": ("AvantBras",), "Poignet": ("Poignet",)}
REGION_KW = [
    ("Bassin",  r"bassin|iliaque|pubien|sacrum|cotyl|ac[ée]tabul|anneau pelvien|sacro-iliaque"),
    ("Femur",   r"f[ée]mur|f[ée]moral|trochant[ée]r|col f[ée]moral|diaphyse f[ée]morale|sous-troch"),
    ("Genou",   r"genou|rotul|patell|[ée]pine tibiale|condyle f[ée]moral|plateau tibial|ligament crois|TPM"),
    ("Jambe",   r"\bjambe\b|tibia|p[ée]ron|fibula|diaphyse tibiale|deux os de la jambe"),
    ("Cheville",r"cheville|mall[ée]ol|astragale|\btalus\b|tibio-tarsienne|tibio-p[ée]ron"),
    ("Pied",    r"\bpied\b|m[ée]tatars|calcan[ée]um|phalange|orteil"),
]
TOPIC_KW = [
    ("Supracondylienne",  r"supra.?condyl"),
    ("CondyleLateral",    r"condyle (lat[ée]ral|externe)"),
    ("EpicondyleMedial",  r"[ée]picondyle (m[ée]dial|interne)|[ée]pitrochl"),
    ("Monteggia",         r"monteggia"),
    ("Galeazzi",          r"galeazzi"),
    ("Clavicule",         r"clavicul"),
    ("ColRadius",         r"col du radius|col radial|t[êe]te radiale"),
    ("Olecrane",          r"ol[ée]cr[âa]ne"),
    ("DecollementEpiphysaire", r"d[ée]collement [ée]piphys|[ée]piphysiolyse|salter|cartilage de croissance|[ée]piphysaire"),
    ("SyndromeDeLoge",    r"syndrome (de|des) loges?|compartiment"),
    ("FractureOuverte",   r"fracture\w* ouvert|ouverture cutan|peau ouverte|cauchoix|gustilo|perte de substance"),
    ("Pseudarthrose",     r"pseudarthrose"),
    ("CalVicieux",        r"cal vicieux|cubitus varus|cubitus valgus|malunion|d[ée]formation r[ée]siduelle"),
    ("Neurovasculaire",   r"paralysie|volkmann|sensitivo|nerf (radial|ulnaire|cubital|m[ée]dian|interosseux|sciatique)|"
                          r"(atteinte|l[ée]sion|compression|contusion) (du nerf|nerveuse|art[ée]rielle|vasculo)|"
                          r"art[èe]re (hum[ée]rale|poplit[ée]e|f[ée]morale|radiale|brachiale)|d[ée]ficit (moteur|sensiti)"),
    ("Maltraitance",      r"maltrait|s[ée]vices|non accidentel|secou[ée]"),
    ("Toddler",           r"fracture en cheveu|sous-p[ée]riost|motte de beurre"),
    ("BoisVert",          r"bois.?vert"),
]
def detect(text, table):
    t = text.lower()
    return [tag for tag, pat in table if re.search(pat, t, re.I)]

def region_of(case):
    if case["section"] == "MS":
        r = case["region"].lower()
        for k in sorted(REGION_MS, key=len, reverse=True):   # 'Avant-bras' before 'Bras'
            if k.lower() in r:
                return REGION_MS[k][0]
        return "MembreSuperieur"
    # MI: the diagnosis is the most reliable localiser; fall back to whole case
    diag = ""
    for q in case["qa"]:
        if re.search(r"diagnostic|de quel type|type de fracture|s'agit", q["q"] + q["answer"], re.I) and q["answer"]:
            diag = q["answer"]; break
    found = detect(diag, REGION_KW)
    if found:
        return found[0]
    blob = case["vignette"] + " " + " ".join(q["answer"] + " " + q["comment"] for q in case["qa"])
    found = detect(blob, REGION_KW)
    return found[0] if found else "MembreInferieur"

def mechanism_of(text):
    t = text.lower(); tags = []
    if re.search(r"\bavp\b|voie publique|heurt|v[ée]hicule|moto", t): tags.append("AVP")
    if re.search(r"chute", t): tags.append("Chute")
    if re.search(r"sport|football|match|jeu", t): tags.append("Sport")
    if re.search(r"nouveau.?n[ée]|accouchement|naissance|dystoci", t): tags.append("Obstetrical")
    return tags

def qtype_tags(q, a):
    blob = (q + " " + a).lower(); tags = []
    if re.search(r"diagnostic|interpr[ée]tez|quelle? l[ée]sion|de quel type", blob):
        tags.append("ClinicalReasoning")
    if re.search(r"chirurg|embrochage|broche|ost[ée]osynth|vissage|\bvis\b|plaque|enclouage|ecmes|"
                 r"r[ée]duction sanglante|arthrotomie|foyer ouvert|fixateur|op[ée]ratoire", blob):
        tags.append("SurgicalManagement")
    if re.search(r"orthop[ée]dique|pl[âa]tre|immobilis|contention|attelle|anneau|"
                 r"r[ée]duction orthop[ée]dique|blount|traction|fonctionnel", blob):
        tags.append("NonOperativeManagement")
    if re.search(r"complication|redout|risque|s[ée]quelle|craint|pronostic", blob):
        tags.append("Complications")
    if re.search(r"examen (para)?clinique|radiograph|scanner|irm|[ée]chograph|bilan|incidence de", blob):
        tags.append("Imaging")
    return tags

def case_diagnosis(case):
    for q in case["qa"]:
        if re.search(r"diagnostic|de quel type|quelle? l[ée]sion|type de fracture", q["q"], re.I) and q["answer"]:
            return re.split(r"(?<=[.])\s", q["answer"])[0]
    return case["qa"][0]["answer"] if case["qa"] else ""

BASE = ["Pediatrics", "Orthopedics", "Traumatology"]
def case_tags(case, q=None, a=None, extra=()):
    t = list(BASE)
    t.append("UpperExtremity" if case["section"] == "MS" else "LowerExtremity")
    t.append("CaseBasedLearning")
    reg = region_of(case); t.append("Region::" + reg)
    # topic/mechanism scanned on card-specific text + the case diagnosis (primary topic),
    # NOT on every commentary in the case (avoids tag inflation)
    blob = case["vignette"] + " " + case_diagnosis(case) + " " + (q or "") + " " + (a or "")
    for tp in detect(blob, TOPIC_KW):
        t.append("Topic::" + tp)
        if tp in ("DecollementEpiphysaire",):
            t += ["GrowthPlate", "SalterHarris"]
        if tp in ("SyndromeDeLoge", "Neurovasculaire", "Pseudarthrose", "CalVicieux", "FractureOuverte"):
            t.append("Complications")
    for m in mechanism_of(case["vignette"]):
        t.append("Mechanism::" + m)
    if q is not None:
        t += qtype_tags(q, a or "")
    t += list(extra)
    return sorted(set(t))

# ------------------------------------------------------- genanki models
CSS = """
.card{font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;
 font-size:19px;line-height:1.5;color:#1a2330;background:#f7f9fc;text-align:left;padding:14px}
.vignette{background:#eef3fb;border-left:4px solid #2f6fb0;padding:10px 14px;border-radius:6px;margin-bottom:10px}
.qline{font-weight:600;color:#0b3d6b;margin-top:6px}
.ans{background:#eafbf0;border-left:4px solid #2e9d5b;padding:10px 14px;border-radius:6px}
.label{font-size:13px;letter-spacing:.5px;text-transform:uppercase;color:#6b7a90;font-weight:700}
.extra{margin-top:12px;font-size:16px;color:#33414f;background:#fff;border:1px solid #e1e7ef;border-radius:6px;padding:10px 14px}
.src{margin-top:12px;font-size:12px;color:#94a2b3}
ul{margin:6px 0 6px 4px;padding-left:20px}
img.rad{max-width:100%;max-height:430px;border-radius:6px;margin:6px 4px;border:1px solid #d4dbe6;background:#000}
hr#answer{border:none;border-top:1px solid #cfd8e6;margin:14px 0}
.cloze{font-weight:700;color:#2f6fb0}
"""

BASIC = genanki.Model(
    1748210501, "POTEC Basique (image)",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}, {"name": "Source"}],
    templates=[{
        "name": "Carte",
        "qfmt": '{{Front}}',
        "afmt": '{{FrontSide}}<hr id="answer">{{Back}}'
                '{{#Extra}}<div class="extra"><span class="label">Commentaire</span><br>{{Extra}}</div>{{/Extra}}'
                '{{#Source}}<div class="src">{{Source}}</div>{{/Source}}',
    }],
    css=CSS)

CLOZE = genanki.Model(
    1748210502, "POTEC Cloze",
    fields=[{"name": "Text"}, {"name": "Extra"}, {"name": "Source"}],
    model_type=genanki.Model.CLOZE,
    templates=[{
        "name": "Cloze",
        "qfmt": "{{cloze:Text}}",
        "afmt": "{{cloze:Text}}"
                '{{#Extra}}<div class="extra">{{Extra}}</div>{{/Extra}}'
                '{{#Source}}<div class="src">{{Source}}</div>{{/Source}}',
    }],
    css=CSS)

# ------------------------------------------------------- deck assembly
DECK_ROOT = "Pédiatrie · Orthopédie-Traumatologie"
decks = {}
def get_deck(sub):
    name = "%s::%s" % (DECK_ROOT, sub)
    if name not in decks:
        did = int(hashlib.md5(name.encode()).hexdigest()[:8], 16)
        decks[name] = genanki.Deck(did, name)
    return decks[name]

rows = []        # for CSV (basic)
cloze_rows = []  # for CSV (cloze)
def guid_for(*parts):
    return genanki.guid_for(*parts)

def _plain(t):
    # strip tags + decode entities for human-readable CSV
    t = re.sub(r"<img[^>]*>", "[image]", t)
    t = re.sub("<[^>]+>", " ", t)
    return re.sub(r"[ ]{2,}", " ", html.unescape(t)).strip()

def add_basic(deck, front, back, extra, source, tags, gkey):
    note = genanki.Note(model=BASIC, fields=[front, back, extra or "", source or ""],
                        tags=tags, guid=guid_for(gkey))
    deck.add_note(note)
    rows.append([_plain(front), _plain(back), _plain(extra or ""), source or "", " ".join(tags)])

def add_cloze(deck, text, extra, source, tags, gkey):
    text = re.sub(r"^[\s,;:.\-–·•>»]+", "", text).strip()
    if text and text[0].islower():
        text = text[0].upper() + text[1:]
    note = genanki.Note(model=CLOZE, fields=[text, extra or "", source or ""],
                        tags=tags, guid=guid_for(gkey))
    deck.add_note(note)
    cloze_rows.append([html.unescape(text), _plain(extra or ""), source or "", " ".join(tags)])

SRC_MS = "Thèse N°55-18 (FMP Marrakech) — Fractures du membre supérieur de l'enfant"
SRC_MI = "Thèse N°53-18 (FMP Marrakech) — Fractures du membre inférieur de l'enfant"
def src_of(case):
    return SRC_MS if case["section"] == "MS" else SRC_MI

print("models ok")

# ============================================================ CARD BUILDERS
def strip_figrefs(t):
    t = re.sub(r"\([^)]*[Ff]ig[^)]*\)", "", t)        # (fig3) (Figure 4 et 5)
    t = re.sub(r"\s*\b[Ff]igure?s?\.?\s*\d+( et \d+)?\b\s*", " ", t)
    t = re.sub(r"[ ]{2,}", " ", t).strip()
    return t

MCQ = re.compile(r"^[A-E]([ ,/]+[A-E])*\.?$")
# off-topic septic-arthritis/osteomyelitis text mis-copied into a few fracture
# commentaries in the source -> drop it (answers themselves stay untouched)
CONTAM = re.compile(r"ponction articulaire|arthrite septique|flucloxacilline|staphylocoque|bith[ée]rapie large", re.I)
def clean_comment(c):
    return "" if CONTAM.search(c) else c
n_reason = n_imaging = n_qskip = 0
seen_answers = {}

for case in cases:
    src = src_of(case)
    vign_html = '<div class="vignette">%s</div>' % nl2br(case["vignette"])
    vimgs = case["vignette_imgs"]
    region = region_of(case)
    deck = get_deck(("Membre supérieur" if case["section"] == "MS" else "Membre inférieur") + " — " + region)
    prev_ans = None
    for q in case["qa"]:
        qtext = q["q"].strip()
        ans = strip_figrefs(q["answer"]).strip()
        comment = clean_comment(strip_figrefs(q["comment"]).strip())
        if not ans or len(qtext) < 5:
            n_qskip += 1; continue
        if MCQ.match(ans.replace("\n", " ").strip()):
            n_qskip += 1; continue
        if ans == prev_ans:                 # consecutive source copy-paste duplicate
            n_qskip += 1; continue
        prev_ans = ans
        tags = case_tags(case, qtext, ans + " " + comment, extra=("BoardReview",) if region in
               ("Coude","Genou","Bassin") else ())
        is_img = bool(vimgs) and ("Imaging" in tags or "ClinicalReasoning" in tags) and \
                 re.search(r"diagnostic|interpr|type de l|type de fracture|de quel type", qtext, re.I)
        front = vign_html
        if is_img:
            front += '<div class="qline">%s</div>%s' % (esc(qtext), img_tags(vimgs))
            if "Imaging" not in tags: tags.append("Imaging")
            n_imaging += 1
        else:
            front += '<div class="qline">%s</div>' % esc(qtext)
            n_reason += 1
        back = '<div class="ans"><span class="label">Réponse</span><br>%s</div>' % nl2br(ans)
        aimg = [p for p in q["answer_imgs"] if p not in vimgs]
        if aimg:
            back += img_tags(aimg)
        add_basic(deck, front, back, nl2br(comment) if comment else "", src,
                  sorted(set(tags)), case["id"] + "_q%d" % q["n"])

print("reasoning:", n_reason, "| imaging:", n_imaging, "| skipped Q:", n_qskip)

# ---------------------------------------------------- CLOZE from commentaries
EPONYMS = (r"Blount|M[ée]taizeau|Watson[- ]?Jones|Torode|Zieg|Cauchoix|Duparc|Salter|Harris|"
           r"Meyers|Mc\s?Keever|Baumann|Monteggia|Bado|Volkmann|Judet|Picchio|Lagrange|Rigault|Gartland")
def _wrap(s, a, b, n=1):
    return s[:a] + "{{c%d::" % n + s[a:b].strip() + "}}" + s[b:]
def make_cloze_sentence(sent):
    s = sent.strip().rstrip(":")
    if not (28 <= len(s) <= 240): return None
    # 1: percentage
    m = re.search(r"\d+\s?(?:à|-|et)?\s?\d*\s?%", s)
    if m: return _wrap(s, m.start(), m.end())
    # 2: incidence X cas/100.000
    m = re.search(r"\d[\d.,\s]*cas\s*/\s*\d[\d.\s]*\d", s)
    if m: return _wrap(s, m.start(), m.end())
    # 3: eponym (classification/méthode/signe de X)  OR bare eponym anywhere
    m = re.search(r"(?:classification|m[ée]thode|technique|man[œo]euvre|signe|fracture|l[ée]sion|angle)\s+"
                  r"(?:de\s+|d['e]|selon\s+)([A-ZÉÈ][\wéèêàç']+(?:[\s-]+(?:et|&|-)?\s*[A-ZÉÈ][\wéèêàç']+)?)", s)
    if m: return _wrap(s, m.start(1), m.end(1))
    m = re.search(EPONYMS, s)
    if m: return _wrap(s, m.start(), m.end())
    # 4: degrees / measurements
    m = re.search(r"\d+\s?(?:à|-|et|±|\+/-)?\s?\d*\s?°", s)
    if m: return _wrap(s, m.start(), m.end())
    # 5: "le/la plus fréquent(e)" -> hide subject
    m = re.search(r"^(.{6,90}?)\s+(?:est|sont|repr[ée]sente|constitue)\s+(?:la|le|les)?\s*(?:plus\s+\w+|fr[ée]quent)", s, re.I)
    if m and re.search(r"fr[ée]quent|plus", s, re.I):
        return "{{c1::" + m.group(1).strip() + "}}" + s[m.end(1):]
    # 6: contraindication
    m = re.search(r"contre-indication\w*\s+(?:absolue\s+)?(?:à|de|est)?\s*(.{6,80})", s, re.I)
    if m:
        seg = m.group(1).strip().rstrip(".")
        if not re.search(r"dont|cite|suivant|comme suit|plusieurs|cette m[ée]thode", seg, re.I):
            return s.replace(seg, "{{c1::" + seg + "}}", 1)
    # 7: duration in weeks
    m = re.search(r"(?:pendant|pour une dur[ée]e de|durant|à garder)\s+([^.,;]*?\d+\s?(?:à|-)?\s?\d*\s?semaines?)", s, re.I)
    if m: return _wrap(s, m.start(1), m.end(1))
    # 8: age window
    m = re.search(r"\b\d{1,2}\s?(?:à|-|et)\s?\d{1,2}\s?ans?\b", s)
    if m: return _wrap(s, m.start(), m.end())
    # 9: nerve/artery at risk (stop before verbs)
    m = re.search(r"(?:nerf|art[èe]re)\s+(?!est|sont|peut|doit|reste)([a-zéèêàç-]+(?:\s+(?!est|sont|peut|doit)[a-zéèêàç-]+)?)", s, re.I)
    if m and len(s) < 170: return _wrap(s, m.start(), m.end())
    return None

def extra_patterns(s):
    return None

n_cloze = 0
seen_comment = set()
for case in cases:
    src = src_of(case); region = region_of(case)
    deck = get_deck("Notions clés (cloze) — " + ("MS" if case["section"]=="MS" else "MI"))
    for q in case["qa"]:
        c = clean_comment(strip_figrefs(q["comment"]).strip())
        if not c: continue
        key = re.sub(r"\s+", " ", c).strip().lower()
        if key in seen_comment: continue
        seen_comment.add(key)
        sents = [x for x in re.split(r"(?<=[.;:])\s+|\n", c) if x.strip()]
        made = 0
        for sent in sents:
            if made >= 6: break
            cz = make_cloze_sentence(sent) or extra_patterns(sent.strip())
            if cz and "{{c1::" in cz and len(cz) < 320:
                tags = case_tags(case, q["q"], c, extra=("BoardReview",))
                add_cloze(deck, cz, "", src, sorted(set(tags)),
                          case["id"] + "_cz%d_%s" % (q["n"], hashlib.md5(sent.encode()).hexdigest()[:6]))
                n_cloze += 1; made += 1
print("commentary cloze:", n_cloze)
print("subtotal notes:", n_reason + n_imaging + n_cloze)

# ============================================================ CURATED CARDS
SRC_REF = "Thèses N°53-18 & N°55-18 (FMP Marrakech) — fractures de l'enfant"
def cb(sub, q, a, tags, g, extra=""):
    add_basic(get_deck(sub), '<div class="qline">%s</div>' % esc(q),
              '<div class="ans"><span class="label">Réponse</span><br>%s</div>' % nl2br(a),
              nl2br(extra) if extra else "", SRC_REF, sorted(set(BASE + tags)), "cur_" + g)
def cz(sub, text, tags, g, extra=""):
    add_cloze(get_deck(sub), text, nl2br(extra) if extra else "", SRC_REF,
              sorted(set(BASE + tags)), "cur_" + g)

F = "Notions de base"           # foundational
H = "Synthèse haut rendement"   # high-yield synthesis
n_cur0 = len(rows) + len(cloze_rows)

# ---- Épidémiologie / particularités de l'os de l'enfant
cb(F, "Quelle est la place de la traumatologie dans la morbi-mortalité de l'enfant ?",
   "1ère cause de décès, 1ère cause de séquelles et d'indemnisation du dommage corporel, et 1er motif d'hospitalisation de l'enfant.",
   ["LowerExtremity","UpperExtremity","BoardReview"], "epi1")
cz(F, "Les garçons présentent plus de fractures que les filles : {{c1::60%}} contre {{c2::40%}}.",
   ["BoardReview"], "epi2")
cz(F, "Le risque de fracture durant l'enfance est de {{c1::40%}} pour les garçons et de {{c2::27%}} pour les filles.",
   ["BoardReview"], "epi3")
cb(F, "Pourquoi l'os de l'enfant se fracture-t-il plus facilement que celui de l'adulte ?",
   "Sa structure est différente : il est plus chargé en eau, moins résistant mécaniquement.",
   [], "os1")
cb(F, "Quel est le rôle du périoste dans les fractures de l'enfant ?",
   "Le périoste est épais et résistant ; lors d'une fracture il est souvent incomplètement rompu, ce qui guide la réduction et stabilise le foyer. Il produit rapidement (2–3 semaines) un cal périosté externe.",
   ["NonOperativeManagement"], "os2")
cz(F, "Le cal périosté externe apparaît rapidement chez l'enfant, en {{c1::2 à 3 semaines}}.",
   [], "os2b")
cb(F, "Quelles sont les propriétés mécaniques du cartilage de croissance ?",
   "Il est mécaniquement faible : peu résistant aux forces de traction axiale et de torsion. Beaucoup de fractures de l'enfant passent par lui.",
   ["GrowthPlate"], "os3")
cb(F, "Quelle est la complication la plus grave d'une atteinte du cartilage de croissance ?",
   "La création d'un pont d'épiphysiodèse (destruction partielle/totale du cartilage) → arrêt de croissance, perte de longueur et désaxation. D'autant plus grave que l'enfant est jeune et le cartilage actif.",
   ["GrowthPlate","Complications"], "os4")
cz(F, "Les cartilages de croissance les plus actifs sont situés {{c1::près du genou et loin du coude}}.",
   ["GrowthPlate","BoardReview"], "os5")
cb(F, "Pourquoi les luxations sont-elles rares et les décollements épiphysaires fréquents chez l'enfant ?",
   "Parce que les structures capsulo-ligamentaires de l'enfant sont plus solides que les structures ostéo-cartilagineuses.",
   ["GrowthPlate"], "os6")
cz(F, "Chez l'enfant, la croissance en largeur dépend du {{c1::périoste}} et la croissance en longueur du {{c2::cartilage de croissance}}.",
   ["GrowthPlate"], "os7")

# ---- Fractures spécifiques de l'enfant
cb(F, "Définissez la fracture en motte de beurre.",
   "Une plicature plastique d'une corticale métaphysaire (fracture torus).",
   ["BoardReview"], "ft1")
cb(F, "Définissez la fracture en bois-vert.",
   "Une corticale est conservée alors que l'autre est rompue ; fracture incomplète, uni-corticale, souvent avec angulation.",
   ["BoardReview"], "ft2")
cb(F, "Qu'est-ce qu'une déformation plastique ?",
   "Il n'y a pas de trait de fracture mais une courbure plastique s'étendant sur toute la longueur de l'os (typiquement fibula, ulna).",
   [], "ft3")
cb(F, "Qu'est-ce qu'une fracture sous-périostée et quel en est le piège diagnostique ?",
   "L'os est fracturé mais le périoste reste intact ; l'enfant peut parfois marcher malgré une fracture du fémur ou du tibia. La radiographie initiale est souvent normale ; le diagnostic est porté sur une boiterie + douleur à la percussion, et confirmé par l'apparition d'un cal osseux 15 jours à 3 semaines plus tard.",
   ["LowerExtremity","Topic::Toddler"], "ft4")

# ---- Salter-Harris
cb(F, "Décollement épiphysaire Salter-Harris type I : description et pronostic ?",
   "Décollement épiphysaire pur (le trait passe entièrement dans le cartilage de croissance). Pronostic de croissance bon.",
   ["GrowthPlate","SalterHarris","BoardReview"], "sh1")
cb(F, "Salter-Harris type II : description et pronostic ?",
   "Le trait emprunte le cartilage de croissance puis remonte en zone métaphysaire (coin métaphysaire). Pronostic habituellement bon. C'est le type le plus fréquent.",
   ["GrowthPlate","SalterHarris","BoardReview"], "sh2")
cb(F, "Salter-Harris type III : description et pronostic ?",
   "Le trait emprunte le cartilage de croissance puis devient épiphysaire (intra-articulaire). Pronostic de croissance compromis, surtout s'il persiste un défaut de réduction même mineur.",
   ["GrowthPlate","SalterHarris","BoardReview"], "sh3")
cb(F, "Salter-Harris type IV : description et pronostic ?",
   "Le trait sépare un fragment épiphyso-métaphysaire (traverse métaphyse, physe et épiphyse). Pronostic souvent mauvais, même si la réduction paraît satisfaisante.",
   ["GrowthPlate","SalterHarris","BoardReview"], "sh4")
cb(F, "Salter-Harris type V : description et particularité diagnostique ?",
   "Écrasement du cartilage de croissance par compression. Non identifiable initialement : diagnostic a posteriori sur sa complication (pont d'épiphysiodèse).",
   ["GrowthPlate","SalterHarris","BoardReview"], "sh5")
cz(F, "Les décollements épiphysaires à haut risque de trouble de croissance sont les Salter-Harris {{c1::III, IV et V}}.",
   ["GrowthPlate","SalterHarris","Complications","BoardReview"], "sh6")
cb(F, "Quel suivi proposer pour dépister un trouble de croissance après une fracture épiphysaire ?",
   "Un contrôle radiologique 1 an après la fracture (surtout pour les décollements Salter-Harris III, IV et V), en ayant prévenu les parents de cette éventualité.",
   ["GrowthPlate","SalterHarris","Complications"], "sh7")

# ---- CRITOE
cb(F, "Quel moyen mnémotechnique donne l'ordre d'apparition des noyaux d'ossification du coude ?",
   'La règle « CRITOE » : Capitellum, tête Radiale, épicondyle Interne (épitrochlée), Trochlée, Olécrane, épicondyle Externe.',
   ["UpperExtremity","Region::Coude","Imaging","BoardReview"], "crit1")
cz(F, "Ordre CRITOE des noyaux d'ossification du coude : {{c1::Capitellum}} → tête {{c2::Radiale}} → épicondyle {{c3::Interne}} → {{c4::Trochlée}} → {{c5::Olécrane}} → épicondyle {{c6::Externe}}.",
   ["UpperExtremity","Region::Coude","BoardReview"], "crit2")
cz(F, "Âges d'apparition (CRITOE) : Capitellum {{c1::6 mois–2 ans}}, tête radiale {{c2::3–6 ans}}, épicondyle interne {{c3::5–7 ans}}, trochlée {{c4::7–10 ans}}, olécrane {{c5::8–10 ans}}, épicondyle externe {{c6::11–12 ans}}.",
   ["UpperExtremity","Region::Coude","BoardReview"], "crit3")
cb(F, "Pourquoi le diagnostic des fractures du coude est-il difficile chez l'enfant ?",
   "Parce que l'épiphyse est en grande partie cartilagineuse : seuls les noyaux d'ossification sont visibles, et ils apparaissent successivement (règle CRITOE). À la naissance, seules les métaphyses sont ossifiées au coude.",
   ["UpperExtremity","Region::Coude","Imaging"], "crit4")

# ---- Principes thérapeutiques
cb(F, "Quel est le traitement de choix des fractures de l'enfant et pourquoi ?",
   "Le traitement orthopédique : il respecte le mieux les processus de consolidation, sans risque de complications thrombo-emboliques ni infectieuses.",
   ["NonOperativeManagement","BoardReview"], "tx1")
cb(F, "La rééducation est-elle nécessaire après immobilisation d'une fracture chez l'enfant ?",
   "Non : la raideur articulaire est exceptionnelle chez l'enfant, donc la rééducation après immobilisation est sans intérêt.",
   ["NonOperativeManagement"], "tx2")
cb(F, "Quand et comment immobiliser un membre traumatisé aux urgences ?",
   "Dès l'arrivée de l'enfant, avant toute imagerie, idéalement par une attelle radio-transparente (sinon une attelle plâtrée retirée pour l'imagerie). But : éviter l'aggravation lésionnelle (déplacement osseux lésant vaisseau/nerf) et diminuer la douleur.",
   ["NonOperativeManagement"], "tx3")
cb(F, "Comment se fait le remodelage d'un cal vicieux chez l'enfant ?",
   "Par apposition périostée du côté de la concavité du cal vicieux et résorption du côté de la convexité.",
   ["NonOperativeManagement"], "tx4")
cb(F, "Comment évaluer la douleur chez l'enfant traumatisé ?",
   "Par une échelle visuelle analogique (chez les grands) ou une échelle comportementale (chez les petits). La présence et la distraction par les parents aident à diminuer la détresse.",
   [], "tx5")

# ---- Synthèse haut rendement par localisation
cb(H, "Quelle est la fracture la plus fréquente de l'enfant, et quel en est le siège le plus fréquent ?",
   "La fracture de la clavicule ; le tiers moyen (diaphysaire) est de loin le plus fréquent.",
   ["UpperExtremity","Region::Clavicule","Topic::Clavicule","BoardReview"], "cl1")
cb(H, "Traitement habituel d'une fracture diaphysaire de clavicule chez l'enfant ?",
   "Traitement orthopédique : contention par anneaux en 8 pendant 3 à 4 semaines. Chirurgie exceptionnelle (complication vasculo-nerveuse, menace d'ouverture cutanée).",
   ["UpperExtremity","Region::Clavicule","Topic::Clavicule","NonOperativeManagement"], "cl2")
cz(H, "Les fractures supra-condyliennes représentent {{c1::60%}} des fractures du coude de l'enfant et surviennent vers l'âge de {{c2::7 ans}}.",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","BoardReview"], "sc1")
cb(H, "En quoi consiste la méthode de Blount et quelle en est la contre-indication absolue ?",
   "Immobilisation du coude en hyper-flexion (la réduction d'une fracture supra-condylienne en extension n'est stable qu'en flexion à angle aigu), à condition que le pouls radial reste perçu. Contre-indication absolue : un œdème important (risque de compression vasculo-nerveuse par plicature cutanée).",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","NonOperativeManagement","BoardReview"], "sc2")
cb(H, "Quelle déformation séquellaire redoute-t-on après une fracture supra-condylienne mal réduite ?",
   "Le cubitus varus (déformation en varus du coude), séquelle d'un cal vicieux.",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","Topic::CalVicieux","Complications"], "sc3")
cz(H, "L'angle de Baumann, qui évalue le cubitus varus, a une valeur physiologique de {{c1::72° ± 5°}}.",
   ["UpperExtremity","Region::Coude","Imaging","Topic::CalVicieux","BoardReview"], "baum1")
cz(H, "Les fractures de l'épitrochlée représentent {{c1::10%}} des fractures du coude et se produisent par un mécanisme en {{c2::valgus}} de l'avant-bras.",
   ["UpperExtremity","Region::Coude","Topic::EpicondyleMedial","BoardReview"], "ep1")
cb(H, "Classification de Watson-Jones des fractures de l'épitrochlée ?",
   "Stade I : fracture peu ou pas déplacée. Stade II : fracture déplacée (en arrière ou, le plus souvent, en bas). Stade III : incarcération de l'épitrochlée dans l'articulation huméro-cubitale.",
   ["UpperExtremity","Region::Coude","Topic::EpicondyleMedial","BoardReview"], "ep2")
cb(H, "Qu'est-ce qu'une lésion de Monteggia ?",
   "Une fracture de l'ulna (tiers supérieur) associée à une luxation de la tête radiale.",
   ["UpperExtremity","Region::AvantBras","Topic::Monteggia","BoardReview"], "mo1")
cb(H, "Quel est le piège de la lésion de Monteggia et le principe de son traitement ?",
   "Le piège est la méconnaissance de la luxation de la tête radiale. La réduction du cubitus (ulna) est primordiale ; 90% des lésions de Monteggia sont accessibles au traitement orthopédique.",
   ["UpperExtremity","Region::AvantBras","Topic::Monteggia","NonOperativeManagement","BoardReview"], "mo2")
cz(H, "La lésion de Monteggia représente environ {{c1::2%}} des fractures de l'avant-bras de l'enfant.",
   ["UpperExtremity","Region::AvantBras","Topic::Monteggia"], "mo3")
cb(H, "Pourquoi le traitement orthopédique est-il privilégié dans les fractures des deux os de l'avant-bras de l'enfant ?",
   "Grâce aux importantes propriétés de remodelage de l'os en croissance, un alignement anatomique parfait n'est pas toujours nécessaire.",
   ["UpperExtremity","Region::AvantBras","NonOperativeManagement"], "fa1")
cb(H, "Qu'est-ce que l'embrochage centro-médullaire élastique stable (ECMES) de Métaizeau ?",
   "Une ostéosynthèse à foyer fermé par broches élastiques introduites en intra-médullaire, méthode de référence pour stabiliser de nombreuses fractures diaphysaires de l'enfant (avant-bras, fémur).",
   ["UpperExtremity","SurgicalManagement","BoardReview"], "fa2")
cb(H, "Définissez le syndrome de Volkmann.",
   "L'association d'une rétraction des muscles de la loge antérieure de l'avant-bras et d'une paralysie plus ou moins étendue des muscles de la main. C'est une conséquence d'une ischémie (séquelle d'un syndrome de loge).",
   ["UpperExtremity","Topic::SyndromeDeLoge","Topic::Neurovasculaire","Complications","BoardReview"], "vk1")
cb(H, "Quel est le signe le plus important à rechercher pour dépister un syndrome de loge ?",
   "L'apparition et l'extension de la douleur (douleur disproportionnée, majorée à l'étirement passif). Prévention : plâtre non compressif, surélévation du membre, surveillance neuro-vasculaire.",
   ["Topic::SyndromeDeLoge","Complications","BoardReview"], "vk2")
cb(H, "Quelle est la 3ème localisation la plus fréquente des fractures de l'enfant ?",
   "La diaphyse fémorale (fractures diaphysaires du fémur).",
   ["LowerExtremity","Region::Femur","BoardReview"], "fem1")
cb(H, "Fractures des épines tibiales : quelle structure est avulsée et quelle classification utilise-t-on ?",
   "Le fragment détaché correspond à la zone d'insertion osseuse du ligament croisé antérieur (LCA). Classification de Meyers et McKeever (types 1 à 4).",
   ["LowerExtremity","Region::Genou","BoardReview"], "ti1")
cz(H, "Les fractures des épines tibiales touchent surtout les adolescents sportifs entre {{c1::8 et 17 ans}}.",
   ["LowerExtremity","Region::Genou"], "ti2")
cb(H, "Classification de Meyers et McKeever des fractures des épines tibiales ?",
   "Type 1 : fracture sans déplacement ou minime. Type 2 : déplacement avec charnière postérieure cartilagineuse (soulèvement antérieur). Type 3 : séparation complète du fragment. Type 4 : fracture comminutive.",
   ["LowerExtremity","Region::Genou","BoardReview"], "ti3")
cz(H, "Les lésions traumatiques du bassin sont rares chez l'enfant ({{c1::5%}} des fractures) et s'accompagnent de lésions associées dans {{c2::75%}} des cas (surtout uro-génitales).",
   ["LowerExtremity","Region::Bassin","Complications","BoardReview"], "pe1")
cb(H, "Quelle classification utilise-t-on pour les fractures de l'anneau pelvien de l'enfant ?",
   "La classification de Torode et Zieg.",
   ["LowerExtremity","Region::Bassin","BoardReview"], "pe2")
cb(H, "Quel bilan d'imagerie devant une lésion instable de l'anneau pelvien ?",
   "Au minimum une radiographie du bassin de face, complétée par une tomodensitométrie (scanner) qui précise à la fois le bilan osseux et le bilan viscéral.",
   ["LowerExtremity","Region::Bassin","Imaging"], "pe3")
cb(H, "Quelle classification est utilisée pour les fractures ouvertes (ouverture cutanée) ?",
   "La classification de Cauchoix et Duparc, fondée sur l'importance de l'ouverture cutanée.",
   ["Topic::FractureOuverte","Complications","BoardReview"], "of1")

n_cur = len(rows) + len(cloze_rows) - n_cur0
print("curated cards:", n_cur)

# ============================================================ PREREQ CLOZE (didactic)
# all didactic pages; a relevance filter keeps only high-yield sentences (danger
# structures, angles, ossification, epidemiology) and drops descriptive anatomy.
RELEVANT = re.compile(r"art[èe]re|\bnerf|vascularis|rapport [ée]troit|l[èe]se|risque|"
                      r"\d+\s?°|\d+\s?%|noyau|ossif|fr[ée]quent|semaines?|\bans?\b|"
                      r"salter|[ée]piphys|p[ée]rioste|consolidation|remodelage|cal\b", re.I)
PAGE_REGION = [("prerequis2", "Genou"), ("prerequis1", "Femur"), ("prerequis3", "Cheville")]
seen_cloze = set(re.sub(r"\s+", " ", t[0]).lower() for t in cloze_rows)
def page_region_tags(f):
    for key, reg in PAGE_REGION:
        if key in f:
            return ["Region::" + reg]
    return []
n_pcloze = 0
for f, txt in prereq.items():
    sec = "MS" if "FRACTURES MS" in f else "MI"
    src = SRC_MS if sec == "MS" else SRC_MI
    deck = get_deck("Notions de base (cloze)")
    made = 0
    for sent in [x for x in re.split(r"(?<=[.;])\s+|\n", txt) if x.strip()]:
        if made >= 12: break
        if not RELEVANT.search(sent):
            continue
        czt = make_cloze_sentence(sent)
        if not czt or "{{c1::" not in czt or len(czt) > 300:
            continue
        norm = re.sub(r"\s+", " ", re.sub(r"\{\{c\d+::|\}\}", "", czt)).lower().strip()
        if any(norm[:45] == x[:45] for x in seen_cloze):
            continue
        seen_cloze.add(norm)
        tags = ["UpperExtremity" if sec == "MS" else "LowerExtremity", "BoardReview"] + page_region_tags(f)
        if re.search(r"salter|[ée]piphys|cartilage de croissance", czt, re.I):
            tags += ["GrowthPlate", "SalterHarris"]
        add_cloze(deck, czt, "", src, sorted(set(BASE + tags)),
                  "pcz_%s" % hashlib.md5((f + sent).encode()).hexdigest()[:10])
        n_pcloze += 1; made += 1
print("prereq cloze:", n_pcloze)

# ============================================================ RECOGNITION cards (concise pattern)
# condensed clinical stem (mechanism + key exam, radiograph reveal trimmed) -> diagnosis
def condense_vignette(v):
    v = re.sub(r"\s*La radiographie.*$", "", v, flags=re.I | re.S)
    v = re.sub(r"\s*Une radiographie.*$", "", v, flags=re.I | re.S)
    v = re.sub(r"\s*Le bilan radiologique.*$", "", v, flags=re.I | re.S)
    return re.sub(r"\s+", " ", v).strip()

DIAG_Q = re.compile(r"diagnostic|de quel type|quelle? l[ée]sion|type de fracture", re.I)
n_recog = 0
for case in cases:
    diag = None
    for q in case["qa"]:
        if DIAG_Q.search(q["q"]) and q["answer"] and not MCQ.match(q["answer"].replace("\n"," ").strip()):
            diag = q["answer"]; break
    if not diag:
        continue
    stem = condense_vignette(case["vignette"])
    if len(stem) < 30:
        continue
    diag1 = strip_figrefs(re.split(r"(?<=[.])\s", diag)[0]).strip()
    if len(diag1) < 6:
        continue
    region = region_of(case)
    deck = get_deck(("Membre supérieur" if case["section"]=="MS" else "Membre inférieur") + " — " + region)
    tags = case_tags(case, "diagnostic", diag, extra=("BoardReview",))
    tags = [t for t in tags if t != "Imaging"]   # this is the text/recognition variant
    front = ('<div class="vignette">%s</div><div class="qline">Diagnostic le plus probable&nbsp;?</div>'
             % esc(stem))
    back = '<div class="ans"><span class="label">Diagnostic</span><br>%s</div>' % nl2br(diag1)
    add_basic(deck, front, back, "", src_of(case), sorted(set(tags + ["ClinicalReasoning"])),
              case["id"] + "_recog")
    n_recog += 1
print("recognition:", n_recog)

total = len(rows) + len(cloze_rows)
print("=" * 40)
print("TOTAL NOTES:", total, "| basic:", len(rows), "| cloze:", len(cloze_rows))

# ============================================================ CURATED BATCH 2
# Obstetrical / birth
cb(H, "Quel enfant est surtout concerné par les fractures obstétricales et quels en sont les facteurs favorisants ?",
   "Surtout le nouveau-né à terme (80–90% des cas), rarement le prématuré. Facteurs favorisants : présentation anormale (siège, face) source de dystocie, et macrosomie.",
   ["LowerExtremity","UpperExtremity","Mechanism::Obstetrical","BoardReview"], "ob1")
cz(H, "Les traumatismes obstétricaux concernent surtout le nouveau-né à terme ({{c1::80 à 90 %}} des cas), rarement le prématuré.",
   ["Mechanism::Obstetrical"], "ob2")
# Radial neck / head
cz(H, "Les fractures du col radial sont peu fréquentes : elles ne représentent que {{c1::5%}} des fractures du coude de l'enfant.",
   ["UpperExtremity","Region::Coude","Topic::ColRadius","BoardReview"], "rn1")
cb(H, "Pourquoi les fractures du col radial sont-elles rares chez l'enfant ?",
   "Grâce à la structure cartilagineuse de l'épiphyse radiale qui amortit les chocs, et au retard d'apparition du noyau d'ossification (vers 5 ans). Elles sont associées à d'autres lésions dans 50% des cas.",
   ["UpperExtremity","Region::Coude","Topic::ColRadius"], "rn2")
# Elbow dislocation
cb(H, "Quelle est la luxation la plus fréquente chez l'enfant et quel est son pronostic ?",
   "La luxation du coude (le plus souvent postérieure). Sa réduction est simple si elle est faite rapidement et ne donne pas de séquelles à distance dans les formes isolées.",
   ["UpperExtremity","Region::Coude","BoardReview"], "lux1")
# Humeral shaft + radial nerve
cb(H, "Quelle est l'évolution habituelle d'une paralysie radiale constatée d'emblée lors d'une fracture de la diaphyse humérale ?",
   "Elle est dans la majorité des cas due à une contusion du nerf radial dont les effets sont régressifs (récupération spontanée) ; l'attitude est donc le plus souvent expectative.",
   ["UpperExtremity","Region::Bras","Topic::Neurovasculaire","Complications","BoardReview"], "hr1")
# Carrying angle / cubitus
cz(H, "Le valgus physiologique du coude (carrying angle) est plus important chez la fille : en moyenne {{c1::8°}} chez le garçon et {{c2::11°}} chez la fille.",
   ["UpperExtremity","Region::Coude"], "cv1")
cb(H, "Qu'est-ce que le cubitus varus et quelle en est la cause habituelle ?",
   "Une déformation du coude en varus (inversion du valgus physiologique), séquelle classique d'un cal vicieux d'une fracture supra-condylienne mal réduite. Sa valeur est évaluée par l'angle de Baumann.",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","Topic::CalVicieux","Complications","BoardReview"], "cv2")
# Radial nerve exam
cb(H, "Comment tester le nerf radial à l'examen d'un traumatisme du membre supérieur ?",
   "Motricité : extension du poignet (flexion dorsale) et extension des métacarpo-phalangiennes. Sensibilité : tabatière anatomique (zone sensitive privilégiée du nerf radial).",
   ["UpperExtremity","Topic::Neurovasculaire","ClinicalReasoning"], "rad1")
# Compartment syndrome surveillance
cb(H, "Quels paramètres surveiller en post-opératoire pour dépister un syndrome de loge ?",
   "L'apparition/extension de la douleur (signe le plus important), la mobilité et la sensibilité des doigts (déficit neurologique), et la coloration et la chaleur des extrémités.",
   ["Topic::SyndromeDeLoge","Complications","BoardReview"], "cs1")
# Septic arthritis (differential)
cb(H, "Quel est le geste clé du diagnostic d'une arthrite septique et comment doit-il être réalisé ?",
   "La ponction articulaire : geste réalisé en urgence au bloc opératoire, en conditions d'asepsie chirurgicale, sous anesthésie générale, et avant toute antibiothérapie.",
   ["LowerExtremity","Topic::SepticArthritis","BoardReview"], "sa1")
# Pelvic polytrauma priority
cb(H, "Quelle est la priorité de prise en charge devant une fracture du bassin chez un enfant polytraumatisé ?",
   "L'évaluation et la stabilisation hémodynamique, respiratoire et neurologique : tout enfant hémodynamiquement instable relève de la réanimation (risque d'hémorragie rétro-péritonéale), avant la prise en charge de la fracture elle-même.",
   ["LowerExtremity","Region::Bassin","Complications","BoardReview"], "pp1")
# Distal radius physis
cz(H, "Parmi les fractures du poignet de l'enfant, environ {{c1::20%}} intéressent le cartilage de croissance (décollements épiphysaires du radius).",
   ["UpperExtremity","Region::Poignet","GrowthPlate","SalterHarris"], "dr1")
# Open fracture management
cb(H, "Principes de prise en charge d'une fracture ouverte chez l'enfant ?",
   "Urgence chirurgicale : parage-lavage, antibiothérapie, prophylaxie antitétanique, et stabilisation du foyer. La classification de Cauchoix et Duparc évalue la gravité de l'ouverture cutanée.",
   ["Topic::FractureOuverte","SurgicalManagement","Complications","BoardReview"], "of2")
# Remodeling limits
cb(F, "De quoi dépend le potentiel de remodelage d'un cal vicieux chez l'enfant ?",
   "De l'âge (d'autant meilleur que l'enfant est jeune), de la proximité du cartilage de croissance le plus actif, et du caractère dans le plan de mobilité de l'articulation adjacente (les défauts d'angulation se corrigent mieux que les défauts de rotation).",
   ["NonOperativeManagement","GrowthPlate"], "rm1")
# Consolidation
cb(F, "Particularités de la consolidation osseuse chez l'enfant ?",
   "Le cal périphérique produit par le périoste est volumineux et rapide ; il englobe le foyer et permet la réalisation plus tardive du cal central. Les délais de consolidation sont plus courts que chez l'adulte.",
   ["NonOperativeManagement"], "co1")

# ============================================================ CURATED BATCH 3
# Supracondylar classification & complications
cb(H, "Selon quelle classification décrit-on les fractures supra-condyliennes en extension de l'enfant ?",
   "La classification de Lagrange et Rigault (stades de gravité croissante selon le déplacement).",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","BoardReview"], "scl1")
cz(H, "Les fractures supra-condyliennes en flexion sont rares ({{c1::5%}} des fractures supra-condyliennes).",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne"], "scl2")
cb(H, "Quelle est la complication précoce la plus redoutée d'une fracture supra-condylienne déplacée ?",
   "L'atteinte vasculo-nerveuse (artère humérale, nerf médian/interosseux antérieur, nerf radial) et le syndrome de loge pouvant évoluer vers un syndrome de Volkmann. Le pouls radial et l'examen neurologique doivent être systématiquement vérifiés.",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","Topic::Neurovasculaire","Topic::SyndromeDeLoge","Complications","BoardReview"], "scl3")
# Lateral condyle
cb(H, "Quels sont les critères d'appréciation des résultats des fractures du condyle latéral et le repère radiographique utilisé ?",
   "Les critères de Marion et Lagrange. L'angle de Baumann (axe diaphysaire huméral / ligne parallèle au cartilage de croissance du condyle latéral) est le repère ; valeur moyenne ~72–75° ± 5°.",
   ["UpperExtremity","Region::Coude","Topic::CondyleLateral","Imaging","BoardReview"], "lc1")
# Ankle Salter-Harris
cb(H, "Conduite devant une fracture-décollement épiphysaire (Salter-Harris III) de la malléole médiale ?",
   "Réduction chirurgicale par abord du côté du fragment épiphysaire et synthèse par vis (fracture intra-articulaire déplacée → réduction anatomique nécessaire pour préserver la croissance et la congruence articulaire).",
   ["LowerExtremity","Region::Cheville","GrowthPlate","SalterHarris","SurgicalManagement","BoardReview"], "ank1")
cz(H, "Une fracture malléolaire de l'enfant est habituellement immobilisée pendant {{c1::4 à 6 semaines}}.",
   ["LowerExtremity","Region::Cheville","NonOperativeManagement"], "ank2")
# Monteggia Trillat
cb(H, "Selon quelle classification décompose-t-on la lésion de Monteggia ?",
   "La classification de Trillat (qui distingue plusieurs groupes selon le sens de la luxation de la tête radiale et le déplacement de l'ulna).",
   ["UpperExtremity","Region::AvantBras","Topic::Monteggia","BoardReview"], "mo4")
# Femoral head vascularization / AVN
cb(H, "Pourquoi une fracture du col fémoral expose-t-elle à un risque de nécrose de la tête fémorale chez l'enfant ?",
   "Parce que la tête fémorale est vascularisée surtout par un pédicule postéro-supérieur (issu de l'artère circonflexe postérieure) irriguant les trois quarts supérieurs de la tête ; ce réseau précaire est facilement lésé par la fracture.",
   ["LowerExtremity","Region::Femur","Topic::Neurovasculaire","Complications","BoardReview"], "avn1")
# Popliteal artery / knee
cb(H, "Quel rapport vasculaire explique le risque de lésion artérielle dans les fractures de l'extrémité supérieure du tibia ?",
   "La face postérieure du tibia est en rapport étroit avec l'artère poplitée, qui peut être lésée par les fragments fracturés.",
   ["LowerExtremity","Region::Genou","Topic::Neurovasculaire","Complications","BoardReview"], "pop1")
# Most active physis
cb(F, "Quelles localisations de cartilage de croissance sont les plus actives, et quelle en est l'implication ?",
   "Celles « près du genou et loin du coude » (extrémité inférieure du fémur, extrémité supérieure du tibia, extrémité supérieure de l'humérus, extrémité inférieure du radius). Une atteinte y entraîne les troubles de croissance les plus importants.",
   ["GrowthPlate","BoardReview"], "phys1")
# Treatment by fracture type
cb(F, "Quel traitement pour une fracture en motte de beurre (torus) du poignet ?",
   "Fracture stable et bénigne : simple immobilisation (attelle/plâtre) sans réduction, consolidation rapide et sans séquelle.",
   ["UpperExtremity","Region::Poignet","NonOperativeManagement"], "txt1")
cb(F, "Comment traite-t-on une fracture en bois-vert avec angulation ?",
   "Réduction orthopédique (correction de l'angulation, parfois en complétant la rupture de la corticale intacte) puis immobilisation plâtrée, en surveillant le déplacement secondaire.",
   ["NonOperativeManagement","Topic::BoisVert"], "txt2")
# Clavicle ends
cb(H, "Traitement d'une lésion de la clavicule à déplacement postérieur du quart interne ?",
   "Il peut être nécessaire de réduire le déplacement sous anesthésie générale et d'assurer une stabilisation chirurgicale (risque de compression des structures médiastinales/vasculo-nerveuses).",
   ["UpperExtremity","Region::Clavicule","Topic::Clavicule","SurgicalManagement"], "cl3")
# Forearm both-bone complication
cb(H, "Quelle complication aiguë redouter après une fracture des deux os de l'avant-bras ?",
   "Le syndrome de loge (de la loge antérieure de l'avant-bras), pouvant évoluer vers un syndrome de Volkmann en l'absence de prise en charge.",
   ["UpperExtremity","Region::AvantBras","Topic::SyndromeDeLoge","Complications","BoardReview"], "fa3")
# Pseudarthrosis lateral condyle
cb(H, "Pourquoi la fracture du condyle latéral expose-t-elle particulièrement à la pseudarthrose ?",
   "Parce qu'il s'agit d'une fracture articulaire, souvent instable, baignée de liquide synovial qui gêne la consolidation ; une réduction-fixation anatomique est requise si déplacement.",
   ["UpperExtremity","Region::Coude","Topic::CondyleLateral","Topic::Pseudarthrose","Complications","BoardReview"], "lc2")
# Reduction criteria forearm
cb(H, "Quelles déformations se corrigent le mieux par remodelage, et lesquelles se corrigent mal ?",
   "Les angulations dans le plan de mobilité de l'articulation adjacente et chez le jeune enfant se corrigent bien ; les défauts de rotation (décalage) ne se corrigent pas par remodelage.",
   ["NonOperativeManagement","GrowthPlate","BoardReview"], "rem2")
# Polytrauma pelvis associated injuries
cb(H, "Quelles lésions associées rechercher systématiquement devant une fracture de l'anneau pelvien ?",
   "Surtout des lésions du tractus uro-génital (rupture de l'urètre, de la vessie, plaies périnéales/vaginales/rectales) et des lésions vasculaires ; bilan d'un polytraumatisé (crâne, thorax, abdomen).",
   ["LowerExtremity","Region::Bassin","Complications","BoardReview"], "pp2")
# Examen clinique pelvis
cb(H, "Comment rechercher cliniquement une instabilité de l'anneau pelvien ?",
   "Par la palpation des repères osseux et la recherche d'une instabilité en écartant et rapprochant les épines iliaques antéro-supérieures ; compléter par examen vasculaire, neurologique (sensibilité périnéale) et bilan urologique.",
   ["LowerExtremity","Region::Bassin","ClinicalReasoning"], "pp3")
print("curated total now:", len(rows) + len(cloze_rows))  # informational

# ============================================================ MANAGEMENT RECALL (derived)
# "diagnosis -> reference management" cards, built from each case's own answers
TREAT_Q = re.compile(r"traitement|optez|prise en charge|proposez|attitude th[ée]rapeutique|conduite", re.I)
n_mgmt = 0
for case in cases:
    diag = treat = None; tq = ""
    for q in case["qa"]:
        a = strip_figrefs(q["answer"]).strip()
        if not a or MCQ.match(a.replace("\n", " ").strip()):
            continue
        if diag is None and DIAG_Q.search(q["q"]):
            diag = a
        if treat is None and TREAT_Q.search(q["q"]):
            treat = a; tq = q["q"]
    if not (diag and treat):
        continue
    diag1 = strip_figrefs(re.split(r"(?<=[.])\s", diag)[0]).strip()
    if len(diag1) < 6 or len(treat) < 12 or diag1 == treat:
        continue
    region = region_of(case)
    deck = get_deck(("Membre supérieur" if case["section"]=="MS" else "Membre inférieur") + " — " + region)
    tags = case_tags(case, tq, treat, extra=("BoardReview",))
    tags = [t for t in tags if t != "Imaging"]
    front = ('<div class="vignette"><span class="label">Prise en charge</span><br>%s</div>'
             '<div class="qline">Traitement de référence&nbsp;?</div>' % esc(diag1))
    back = '<div class="ans"><span class="label">Traitement</span><br>%s</div>' % nl2br(treat)
    add_basic(deck, front, back, "", src_of(case), sorted(set(tags)), case["id"] + "_mgmt")
    n_mgmt += 1
print("management recall:", n_mgmt)

# ============================================================ CURATED BATCH 4
cb(H, "Particularités des fractures de l'extrémité supérieure de l'humérus (décollements épiphysaires) chez l'enfant ?",
   "Très fréquentes, souvent de type Salter-Harris I ou II. Le cartilage de croissance proximal de l'humérus assure ~80% de la croissance de l'os : énorme potentiel de remodelage, d'où un traitement le plus souvent orthopédique même en cas de déplacement important.",
   ["UpperExtremity","Region::Epaule","GrowthPlate","SalterHarris","NonOperativeManagement","BoardReview"], "ph1")
cb(H, "Traitement d'une fracture stable de l'anneau pelvien chez l'enfant ?",
   "Le plus souvent orthopédique : repos au lit pendant quelques jours puis reprise de la marche en décharge.",
   ["LowerExtremity","Region::Bassin","NonOperativeManagement"], "pp4")
cb(H, "Quelle est la prise en charge d'une fracture des épines tibiales selon le type (Meyers-McKeever) ?",
   "Types 1–2 : traitement orthopédique (réduction par extension du genou puis immobilisation cruro-pédieuse). Types 3–4 (et type 2 irréductible) : réduction et ostéosynthèse chirurgicale (arthroscopie ou arthrotomie).",
   ["LowerExtremity","Region::Genou","SurgicalManagement","NonOperativeManagement","BoardReview"], "ts1")
cb(F, "Quel est le cartilage de croissance qui assure la plus grande part de la croissance au membre supérieur et au membre inférieur ?",
   "Membre supérieur : physe proximale de l'humérus et physe distale du radius (les plus actives, « loin du coude »). Membre inférieur : physes autour du genou (fémur distal, tibia proximal).",
   ["GrowthPlate","BoardReview"], "phys2")
cb(F, "Pourquoi prévenir les parents lors d'une fracture passant par le cartilage de croissance ?",
   "Parce qu'un trouble de croissance (épiphysiodèse, désaxation, inégalité de longueur) peut apparaître à distance ; une information claire les rend attentifs et justifie un contrôle radiologique à 1 an.",
   ["GrowthPlate","Complications"], "info1")
cb(H, "Mécanisme typique d'une fracture supra-condylienne en extension de l'enfant ?",
   "Une chute sur la main, coude en extension (hyper-extension forcée), favorisée par l'hyperlaxité physiologique du coude de l'enfant.",
   ["UpperExtremity","Region::Coude","Topic::Supracondylienne","Mechanism::Chute","BoardReview"], "scm1")
cb(H, "Que faut-il toujours vérifier et documenter devant un traumatisme du coude chez l'enfant ?",
   "L'état vasculo-nerveux distal : pouls radial, coloration/chaleur de la main, et fonction des nerfs médian (dont interosseux antérieur), ulnaire et radial — avant et après toute manœuvre de réduction.",
   ["UpperExtremity","Region::Coude","Topic::Neurovasculaire","ClinicalReasoning","BoardReview"], "scm2")
cb(H, "Quel est le traitement de référence d'une fracture diaphysaire déplacée des deux os de l'avant-bras chez le grand enfant ?",
   "Réduction et embrochage centro-médullaire élastique stable (ECMES / technique de Métaizeau) ; le traitement orthopédique (réduction + plâtre brachio-anté-brachio-palmaire) reste possible pour les formes peu déplacées grâce au remodelage.",
   ["UpperExtremity","Region::AvantBras","SurgicalManagement","NonOperativeManagement","BoardReview"], "fa4")
cb(H, "Quel délai de surveillance impose une fracture déplacée traitée orthopédiquement (plâtre) chez l'enfant ?",
   "Une surveillance rapprochée du déplacement secondaire par radiographies de contrôle (typiquement à J8 puis régulièrement), et une surveillance immédiate de la tolérance du plâtre (douleur, doigts).",
   ["NonOperativeManagement","Imaging"], "surv1")
cb(F, "Qu'est-ce qui distingue une fracture de l'enfant d'une fracture de l'adulte ?",
   "Des particularités anatomiques (cartilage de croissance, périoste épais), biomécaniques (os plus déformable, plus chargé en eau) et physiologiques (remodelage important), d'où des difficultés diagnostiques, des indications thérapeutiques et une évolution propres.",
   ["BoardReview"], "gen1")
cb(H, "Quelle complication tardive redoute-t-on après une fracture du condyle latéral en pseudarthrose ?",
   "Un cubitus valgus progressif, pouvant se compliquer d'une paralysie ulnaire tardive (par étirement chronique du nerf ulnaire).",
   ["UpperExtremity","Region::Coude","Topic::CondyleLateral","Topic::Pseudarthrose","Topic::Neurovasculaire","Complications","BoardReview"], "lc3")
cb(H, "Devant un traumatisme à haute énergie chez l'enfant, quelle lésion osseuse doit être systématiquement suspectée et pourquoi ?",
   "Une lésion de l'anneau pelvien : le pronostic vital peut être engagé par la fracture elle-même (hémorragie rétro-péritonéale) ou par les lésions viscérales associées.",
   ["LowerExtremity","Region::Bassin","Complications","BoardReview"], "pp5")
cb(F, "Quelle imagerie de première intention devant une suspicion de fracture chez l'enfant, et quand compléter ?",
   "Des radiographies standard de face et de profil prenant les articulations sus- et sous-jacentes. Compléter par un scanner (lésions articulaires/complexes, bassin) ou une échographie/IRM selon le contexte (épiphyses non ossifiées, parties molles).",
   ["Imaging","ClinicalReasoning"], "img1")
cb(F, "Pourquoi une radiographie initiale normale n'élimine-t-elle pas une fracture chez le jeune enfant ?",
   "À cause des fractures sous-périostées et des décollements épiphysaires sur épiphyse cartilagineuse (peu/pas visibles) : un cal apparaît 15 jours à 3 semaines plus tard. Des clichés comparatifs ou différés et l'examen clinique (douleur à la percussion, boiterie) sont utiles.",
   ["Imaging","GrowthPlate","Topic::Toddler","ClinicalReasoning","BoardReview"], "img2")

print("curated total (final):", len(rows) + len(cloze_rows))

# ============================================================ ASSEMBLE .apkg + CSV
total = len(rows) + len(cloze_rows)
print("=" * 46)
print("FINAL TOTAL NOTES:", total, "| basic:", len(rows), "| cloze:", len(cloze_rows),
      "| decks:", len(decks), "| media:", len(_media_files))

pkg = genanki.Package(list(decks.values()))
pkg.media_files = sorted(_media_files)
apkg_path = os.path.join(OUT, "Pediatrie_Orthopedie_Traumatologie_Enfant.apkg")
pkg.write_to_file(apkg_path)
sz = os.path.getsize(apkg_path) / 1e6
print("WROTE", apkg_path, "(%.1f MB)" % sz)

with open(os.path.join(OUT, "cartes_basiques.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Recto", "Verso", "Commentaire", "Source", "Tags"])
    for r in rows:
        w.writerow(r)
with open(os.path.join(OUT, "cartes_cloze.csv"), "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["Texte_cloze", "Extra", "Source", "Tags"])
    for r in cloze_rows:
        w.writerow(r)
print("WROTE CSVs")

# tag + deck stats for the docs
from collections import Counter
tagc = Counter()
for r in rows + cloze_rows:
    for t in r[-1].split():
        tagc[t] += 1
json.dump({"total": total, "basic": len(rows), "cloze": len(cloze_rows),
           "decks": {k: len(v.notes) for k, v in decks.items()},
           "tags": dict(tagc.most_common())},
          open(os.path.join(HERE, "stats.json"), "w"), ensure_ascii=False, indent=1)
print("WROTE stats")
