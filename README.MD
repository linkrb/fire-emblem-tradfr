# 🔥 Projet de traduction Fire Emblem 6 (GBA)

## 🎯 Objectif du projet

Ce dépôt regroupe les fichiers de travail pour un projet personnel de **traduction française** de *Fire Emblem: Fuuin no Tsurugi* (FE6), jamais sorti officiellement en Europe.

Le but est de proposer une version intégralement en français, tout en respectant les contraintes techniques du moteur de jeu GBA, à travers des outils de romhacking.

> ⚠️ Aucune ROM n’est incluse dans ce projet. Ce dépôt ne contient que des fichiers de travail (textes, palettes, scripts, etc.).

---

## 🧩 Table de transcodage des caractères accentués

La police utilisée dans la ROM ne permet pas nativement l’affichage des caractères accentués. Une convention de substitution est utilisée pour les intégrer dans les fichiers sources :

| Caractère | Code |
|-----------|------|
| ê         | `^`  |
| à         | `<`  |
| é         | `>`  |
| è         | `{`  |
| ù         | `}`  |
| ô         | `_`  |
| î         | `|`  |
| â         | `[`  |

> Exemple : le mot `t^te > l'{cole` sera affiché correctement en jeu sous forme `tête à l’école`.

---

## 🛠️ Outils utilisés

- **[FEBuilder GBA](https://github.com/FEBuilderGBA/FEBuilderGBA)**  
  Outil principal pour éditer la ROM, insérer les textes, gérer les palettes, portraits, animations, etc.

- **Notepad++ / VS Code**  
  Pour l’édition manuelle des fichiers texte avec coloration et numérotation

- **Python (optionnel)**  
  Pour automatiser la conversion des caractères accentués ou vérifier les longueurs des lignes

---


## 📁 Structure du dépôt

- `README.md` → Présentation du projet
- `.gitignore` → Fichiers ignorés par Git (.sav, .gba, .bak, etc.)

- `textes/`
  - `bruts/` → Fichiers texte originaux (ex: [EF], [F0]...)
  - `convertis/` → Fichiers avec transcodage appliqué

- `palettes/` → Palettes personnalisées utilisées pour les sprites
- `images/` → Portraits, sprites d’animation, assets modifiés
- `scripts/` → Scripts d'automatisation (accentuation, découpe, vérif)

---

## 🔎 Notes techniques

- Les lignes de texte doivent faire **47 caractères maximum**.
- Les balises `[EF]`, `[F0]` etc. correspondent à des sections numérotées pour l'insertion dans FEBuilder.
- La palette des sprites est limitée à **16 couleurs (transparence incluse)**.

---

## 🧪 Statut actuel

> Projet en cours — insertion manuelle des textes via FEBuilder + adaptation ligne par ligne avec conversion des caractères spéciaux.

---

## 🤝 Crédits

Projet personnel initié par Romain, dans un cadre privé, par passion pour *Fire Emblem*.  
Merci à la communauté romhack pour les outils incroyables mis à disposition.
