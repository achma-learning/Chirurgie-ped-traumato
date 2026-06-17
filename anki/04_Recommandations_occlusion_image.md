# Recommandations d'occlusion d'image (Image Occlusion)

Le paquet `.apkg` embarque déjà **140 radiographies/schémas** sur les cartes
d'**interprétation d'imagerie** (radiographie réelle → diagnostic). Ce document
recommande, en complément, des cartes **Image Occlusion** (occlusion de masque)
à créer à partir des **schémas légendés** du site — c'est-à-dire les figures
porteuses de repères/annotations, qui se prêtent au masquage de zones.

> Anki ≥ 23.10 intègre nativement le type de note **Image Occlusion**
> (*Ajouter → Type : Occlusion d'image*). Pour les versions antérieures, installer
> l'add-on *Image Occlusion Enhanced*.

## Pourquoi pas tout automatiser ?
L'occlusion d'image suppose de tracer manuellement les masques sur chaque
légende ; elle ne peut pas être générée fidèlement par script. Les figures
ci-dessous sont les **meilleures candidates** repérées dans le dépôt.

## Schémas prioritaires (haut rendement)

| Schéma | Fichier dans le dépôt | Masquer… | Tags suggérés |
|--------|-----------------------|----------|---------------|
| **CRITOE** — noyaux d'ossification du coude | `FRACTURES MS/img/` (figure « fig12 » de `prerequis/prerequis-ossification.html`) | chaque noyau (C,R,I,T,O,E) **et** son âge | `Imaging GrowthPlate Region::Coude BoardReview` |
| **Salter & Harris I–V** | figure de `FRACTURES MS/cas_clinique/cas3.html` (classification) | chaque type (trait + n°) | `SalterHarris GrowthPlate BoardReview` |
| **Angle de Baumann** | `FRACTURES MS/img/CC6/fig2.png` (et `fig3/fig4`) | les axes, la valeur 72°±5° | `Imaging Region::Coude Topic::CalVicieux` |
| **Lagrange-Rigault** (supracondylienne, stades) | figure « fig4 » de `FRACTURES MS/cas_clinique/cas7.html` | les 4 stades | `Topic::Supracondylienne Region::Coude` |
| **Milch** (condyle) | `FRACTURES MS/img/CC10/fig3.jpg` | types I / II | `Topic::CondyleLateral Region::Coude` |
| **Watson-Jones** (épitrochlée) | figure de `FRACTURES MS/cas_clinique/cas20.html` | stades I–III | `Topic::EpicondyleMedial Region::Coude` |
| **Fréquence des fractures de clavicule** | `FRACTURES MS/img/haykal.jpg` | les pourcentages 20 / 75 / 5 % par siège | `Topic::Clavicule Region::Clavicule` |
| **Meyers & McKeever** (épines tibiales) | schéma de `FRACTURES MI/cas_clinique/cas13.html` | types 1–4 | `Region::Genou` |
| **Anatomie du cartilage de croissance / périoste** | figures de `FRACTURES MI/resume/resume.html` (Figure 1 & 2) | zones de la physe, périoste | `GrowthPlate` |
| **Classification osseuse I–IV** (schéma générique) | `FRACTURES MS/img/3domaa.jpg` | les 4 stades | `BoardReview` |
| **Anatomie du coude / repères** | `FRACTURES MS/img/CC6/` | repères osseux et lignes | `Imaging Region::Coude` |

## Mode opératoire conseillé
1. *Ajouter → Occlusion d'image*, choisir l'image (depuis le dépôt cloné).
2. Tracer un masque par légende ; activer **« Masquer un, montrer les autres »** pour
   les listes ordonnées (CRITOE, Salter-Harris, stades).
3. Renseigner le champ *Back extra* avec le rappel (âge, pronostic, traitement).
4. Affecter le sous-paquet et les tags ci-dessus pour rester cohérent avec le deck.

## Radiographies (occlusion de repérage)
Les radiographies réelles du dépôt (p. ex. `FRACTURES MS/img/CC1/…` supracondylienne,
`FRACTURES MS/img/as.jpg` ECMES d'avant-bras, `FRACTURES MS/img/sdar.jpg` clavicule)
peuvent servir à des occlusions de **repérage** (« masquer puis nommer la structure /
le trait de fracture »), en complément des cartes d'interprétation déjà incluses.
