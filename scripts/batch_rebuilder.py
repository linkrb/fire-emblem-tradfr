import json
import re

# --------------------------
# CONFIGURATION
# --------------------------
FICHIER_MAPPING = "mapping_support.json"
FICHIER_RESULTATS = "support_fr.jsonl"
FICHIER_SORTIE = "support_traduit.txt"

TRANSCODAGE = {
    "ê": "^", "à": "<", "é": ">", "è": "{",
    "ù": "}", "ô": "_", "î": "|", "â": "[",
    "À": "A", "É": "E"
}

REMPLACEMENTS_SPECIFIQUES = {
    "Bern": "Biran",
    "bern": "biran"
}

def transcode(text):
    text = ''.join(TRANSCODAGE.get(c, c) for c in text)
    for mot, remplacement in REMPLACEMENTS_SPECIFIQUES.items():
        text = text.replace(mot, remplacement)
    return text

def parse_resultats(path_resultats):
    with open(path_resultats, encoding="utf-8") as f:
        lignes = [json.loads(l) for l in f if l.strip() != ""]

    resultat_par_bloc = {}
    for item in lignes:
        bloc_id = item["custom_id"]
        try:
            content = item["response"]["body"]["choices"][0]["message"]["content"]
            if content.startswith("```plaintext"):
                content = content.removeprefix("```plaintext").removesuffix("```").strip()
            elif content.startswith("```"):
                content = content.removeprefix("```").removesuffix("```").strip()

            lignes = content.splitlines()
            lignes = [re.sub(r"^\d+\.\s*", "", l).strip() for l in lignes if l.strip() and l.strip() != "```"]
            resultat_par_bloc[bloc_id] = lignes
        except Exception as e:
            print(f"⚠️ Erreur bloc {bloc_id} : {e}")
    return resultat_par_bloc

def reconstruire(mapping_path, resultats):
    with open(mapping_path, encoding="utf-8") as f:
        mapping = json.load(f)

    lignes_finales = []
    for bloc_id in sorted(mapping.keys()):
        bloc_source = mapping[bloc_id]
        bloc_traduit = resultats.get(bloc_id, [])

        if len(bloc_source) != len(bloc_traduit):
            print(f"⚠️ Décalage ligne pour {bloc_id} : {len(bloc_source)} balises vs {len(bloc_traduit)} lignes traduites")

        for i, ligne_src in enumerate(bloc_source):
            if i >= len(bloc_traduit):
                print(f"⚠️ Ligne manquante dans bloc {bloc_id} à l'index {i}")
                continue
            texte = transcode(bloc_traduit[i])
            lignes_finales.append(texte + "\n")

    return lignes_finales

def main():
    resultats = parse_resultats(FICHIER_RESULTATS)
    lignes = reconstruire(FICHIER_MAPPING, resultats)
    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.writelines(lignes)
    print(f"✅ Fichier reconstruit : {FICHIER_SORTIE}")

if __name__ == "__main__":
    main()
