import os
import re
import json
from dotenv import load_dotenv
from tqdm import tqdm

# --------------------------
# CONFIGURATION
# --------------------------
load_dotenv()
FICHIER_ENTREE = "part1.txt"
FICHIER_BATCH = "demande_batch.jsonl"
FICHIER_MAPPING = "mapping.json"
TAILLE_BLOC = 40

TRANSCODAGE = {
    "ê": "^", "à": "<", "é": ">", "è": "{",
    "ù": "}", "ô": "_", "î": "|", "â": "[",
    "À": "A", "É": "E"
}

INSTRUCTIONS_SYSTEM = (
    "Tu es un traducteur professionnel. Traduis fidèlement chaque ligne de ce dialogue de jeu vidéo en français, sans toucher aux balises comme [A], [xxx], ou autres. "
    "Garde les balises à leur place. Utilise un E au lieu de É et un A au lieu de À, même en majuscule. "
    "Ajoute les balises [A] à la fin de chaque réplique au bon endroit, là où un joueur appuierait pour continuer. Ne modifie pas le nombre de lignes."
)

def parser_lignes(file_path):
    lignes = []
    with open(file_path, encoding="utf-8") as f:
        for ligne in f:
            if ligne.strip() == "":
                continue
            lignes.append({"ligne": ligne.strip()})
    return lignes

def split_en_blocs(data, taille_bloc):
    return [data[i:i+taille_bloc] for i in range(0, len(data), taille_bloc)]

def creer_batch_et_mapping(blocs, jsonl_path, mapping_path):
    with open(jsonl_path, "w", encoding="utf-8") as f_jsonl, open(mapping_path, "w", encoding="utf-8") as f_map:
        mapping = {}
        for i, bloc in enumerate(blocs):
            prompt = "\n".join(f"{j+1}. {ligne['ligne']}" for j, ligne in enumerate(bloc))
            custom_id = f"bloc_{i:04}"
            entry = {
                "custom_id": custom_id,
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4",
                    "messages": [
                        {"role": "system", "content": INSTRUCTIONS_SYSTEM},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2
                }
            }
            f_jsonl.write(json.dumps(entry, ensure_ascii=False) + "\n")
            mapping[custom_id] = bloc

        json.dump(mapping, f_map, ensure_ascii=False, indent=2)

    print(f"✅ Batch prêt : {jsonl_path}")
    print(f"🗂️ Mapping des balises : {mapping_path}")

def main():
    lignes = parser_lignes(FICHIER_ENTREE)
    blocs = split_en_blocs(lignes, TAILLE_BLOC)
    creer_batch_et_mapping(blocs, FICHIER_BATCH, FICHIER_MAPPING)

if __name__ == "__main__":
    main()
