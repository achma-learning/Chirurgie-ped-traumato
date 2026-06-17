# Anki — Traumatologie orthopédique pédiatrique

Paquet Anki **haut rendement** extrait de l'intégralité du site (cas cliniques,
prérequis, commentaires) des deux thèses de la Faculté de Médecine et de Pharmacie
de Marrakech :

- **Thèse N°55-18** — *Support pédagogique pour les fractures du membre supérieur de l'enfant*
- **Thèse N°53-18** — *Les fractures du membre inférieur de l'enfant*

Public cible : **résident en orthopédie pédiatrique (PGY 1–5)** et fellow.
Langue : **français** (fidèle à la source).

---

## 📦 Le fichier à importer

➡️ **[`Pediatrie_Orthopedie_Traumatologie_Enfant.apkg`](./Pediatrie_Orthopedie_Traumatologie_Enfant.apkg)** (≈ 20 Mo, autonome, images incluses)

Dans Anki : *Fichier → Importer* puis sélectionner le `.apkg`. Les sous-paquets,
les notes (Basique + Texte à trous) et les **140 radiographies/schémas** sont inclus.
Aucune dépendance externe.

| | |
|---|---|
| **Notes** | 502 |
| **Cartes** (cloze multiples inclus) | 519 |
| **Cas cliniques exploités** | 52 (30 membre supérieur, 22 membre inférieur) |
| **Questions-réponses source** | 181 |
| **Images embarquées** | 140 (radiographies, TDM, schémas de classification) |
| **Sous-paquets** | 15 |

---

## 🧬 Types de cartes (502 notes)

| Type | Nombre | Description |
|------|-------:|-------------|
| Raisonnement clinique | 131 | Vignette complète + question source → réponse + commentaire |
| Interprétation d'imagerie | 49 | Radiographie réelle du cas → diagnostic |
| Reconnaissance | 42 | Présentation condensée → diagnostic le plus probable |
| Prise en charge | 35 | Diagnostic → traitement de référence |
| Cloze (commentaires) | 117 | Faits clés des commentaires (texte source, occlusion ciblée) |
| Cloze (notions de base) | 26 | Physiologie de croissance, danger anatomique, épidémiologie |
| Cartes de synthèse / notions curées | 102 | Classifications, principes, pearls (rédigées à partir de la source) |

---

## 🗂️ Fichiers de ce dossier

| Fichier | Contenu |
|---------|---------|
| `Pediatrie_Orthopedie_Traumatologie_Enfant.apkg` | **Le paquet Anki** (à importer) |
| `cartes_basiques.csv` | Toutes les cartes Basique (Recto, Verso, Commentaire, Source, Tags) — prêtes pour import CSV |
| `cartes_cloze.csv` | Toutes les cartes Texte à trous (Texte, Extra, Source, Tags) |
| `01_Carte_des_connaissances.md` | Carte des connaissances (conditions, classifications, complications) |
| `02_Objectifs_pedagogiques.md` | Liste des objectifs pédagogiques |
| `03_Structure_du_deck.md` | Structure des sous-paquets et taxonomie des tags |
| `04_Recommandations_occlusion_image.md` | Recommandations d'occlusion d'image |
| `build/` | Pipeline reproductible (extraction HTML → JSON → génération du `.apkg`) |

---

## 🏷️ Tags

Chaque note porte les tags demandés (filtrables dans Anki) : `Pediatrics`,
`Orthopedics`, `Traumatology`, `UpperExtremity` / `LowerExtremity`, `GrowthPlate`,
`SalterHarris`, `Imaging`, `ClinicalReasoning`, `SurgicalManagement`,
`NonOperativeManagement`, `Complications`, `BoardReview`, `CaseBasedLearning`,
plus des tags hiérarchiques `Region::*`, `Topic::*` et `Mechanism::*`.
Voir `03_Structure_du_deck.md`.

---

## 🔁 Reproductibilité

Le paquet est entièrement régénérable :

```bash
pip install genanki beautifulsoup4 Pillow
python build/extract_all.py        # cas cliniques  → build/cases.json
python build/extract_prereq.py     # prérequis/résumés → build/prereq.json
python build/build_deck.py         # → .apkg + CSV
```

Les cartes de raisonnement, d'imagerie, de reconnaissance, de prise en charge et
les cloze de commentaires sont **extraites fidèlement** du texte source. Les cartes
de synthèse (« Notions de base », « Synthèse haut rendement ») ont été **rédigées à
partir du contenu vérifié** des pages *prérequis*, *résumé* et *commentaires*.

## ⚠️ Limites / périmètre
- Contenu fidèle à la source : certaines notions classiques **absentes du site**
  (p. ex. lésion de **Galeazzi**, pronation douloureuse, maltraitance détaillée)
  n'ont **pas** été inventées — voir la note dans `01_Carte_des_connaissances.md`.
- La source est une thèse pédagogique (CHU Marrakech) ; quelques cas comportent des
  imperfections rédactionnelles d'origine, filtrées au mieux lors de l'extraction.
- Vérifiez toujours les conduites thérapeutiques avec un référentiel à jour avant
  application clinique.
