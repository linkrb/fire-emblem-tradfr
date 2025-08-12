import os
import json
from dotenv import load_dotenv

# --------------------------
# CONFIGURATION
# --------------------------
load_dotenv()
FICHIER_ENTREE = "part5.txt"
FICHIER_BATCH = "demande_batch_part5.jsonl"
FICHIER_MAPPING = "mapping_part5.json"
TAILLE_BLOC = 120  # Plus gros blocs = moins d'appels API (coûts ↓)
MAX_CAR_PAR_LIGNE = 45  # Limite stricte par ligne demandée
MODEL = "gpt-4o-mini"  # Modèle nettement moins cher
TEMP = 0.2

TRANSCODAGE = {
    "ê": "^", "à": "<", "é": ">", "è": "{",
    "ù": "}", "ô": "_", "î": "|", "â": "[",
    "À": "A", "É": "E"
}

# Prompt système compact (pour économiser des tokens)
INSTRUCTIONS_SYSTEM = (
    "Traducteur FR. Traduis chaque ligne fidèlement en gardant toutes les balises ([A], [xxx], etc.) au bon endroit, sans en créer ni en supprimer. "
    "Utilise 'E' au lieu de 'É' et 'A' au lieu de 'À' (même en majuscules). "
    f"Chaque ligne doit faire ≤ {MAX_CAR_PAR_LIGNE} caractères. "
    "Ajoute [A] à la fin de chaque réplique là où le joueur appuierait pour continuer. "
    "Ne change pas le nombre de lignes. Réponds ligne à ligne dans le même ordre."
)


def parser_lignes(file_path):
    lignes = []
    with open(file_path, encoding="utf-8") as f:
        for ligne in f:
            s = ligne.strip()
            if not s:
                continue
            lignes.append({"ligne": s})
    return lignes


def split_en_blocs(data, taille_bloc):
    return [data[i:i+taille_bloc] for i in range(0, len(data), taille_bloc)]


def creer_batch_et_mapping(blocs, jsonl_path, mapping_path):
    mapping = {}
    with open(jsonl_path, "w", encoding="utf-8") as f_jsonl:
        for i, bloc in enumerate(blocs):
            # Prompt utilisateur compact: numerotation + \n (moins de tokens)
            prompt = "\n".join(f"{j+1}. {ligne['ligne']}" for j, ligne in enumerate(bloc))
            custom_id = f"bloc_{i:04}"
            body = {
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": INSTRUCTIONS_SYSTEM},
                    {"role": "user", "content": prompt}
                ],
                "temperature": TEMP
                # Pas de max_tokens pour laisser l'output passer, mais blocs plus gros = coût/ligne ↓
            }
            entry = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": body
            }
            f_jsonl.write(json.dumps(entry, ensure_ascii=False) + "\n")
            mapping[custom_id] = bloc

    with open(mapping_path, "w", encoding="utf-8") as f_map:
        json.dump(mapping, f_map, ensure_ascii=False, indent=2)

    print(f"✅ Batch prêt : {jsonl_path}")
    print(f"🗂️ Mapping : {mapping_path}")


def main():
    lignes = parser_lignes(FICHIER_ENTREE)
    blocs = split_en_blocs(lignes, TAILLE_BLOC)
    creer_batch_et_mapping(blocs, FICHIER_BATCH, FICHIER_MAPPING)


if __name__ == "__main__":
    main()
