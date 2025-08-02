import openai
import os
import re
from openai import OpenAI
from dotenv import load_dotenv
from tqdm import tqdm  # Ajout de tqdm pour la progress bar

# --------------------------
# CONFIGURATION
# --------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
FICHIER_ENTREE = "part1.txt"
FICHIER_SORTIE = "part1-traduit.txt"
MODEL = "gpt-4o"
MAX_TOKENS_PAR_BLOC = 2048
TAILLE_BLOC = 40  # Nombre de lignes anglaises traitées par lot

TRANSCODAGE = {
    "ê": "^", "à": "<", "é": ">", "è": "{",
    "ù": "}", "ô": "_", "î": "|", "â": "[",
    "À": "A", "É": "E"
}

client = OpenAI(api_key=API_KEY)

def transcode(text: str) -> str:
    return ''.join(TRANSCODAGE.get(c, c) for c in text)

def extract_text_and_tags(line):
    tags = re.findall(r"\[[^\]]*\]", line)
    texte = re.sub(r"\[[^\]]*\]", "", line)
    return tags, texte

def rebuild_line(tags, texte):
    new_tags = tags[:]
    fin = ""
    if new_tags and new_tags[-1] == "[A]":
        new_tags = tags[:-1]
        fin = "[A]"
    content = transcode(texte.strip())
    return "".join(new_tags) + content + fin + "\n"

def translate_block(lines):
    lignes_indexees = [f"{i+1}. {re.sub(r'\[[^\]]*\]', '', l).strip()}" for i, l in enumerate(lines)]
    prompt = "\n".join(lignes_indexees)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Tu es un traducteur professionnel. Traduis fidèlement chaque ligne de ce dialogue de jeu vidéo en français, sans toucher aux balises comme [A], [xxx] ou autres. Utilise toujours un E au lieu de É, et un A au lieu de À, même en majuscule. Ne fusionne jamais les lignes, garde exactement le même nombre de lignes, une par numéro."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS_PAR_BLOC
    )
    lignes_trad = response.choices[0].message.content.splitlines()
    return [re.sub(r"^\d+\. ", "", ligne).strip() for ligne in lignes_trad]

def process_file():
    with open(FICHIER_ENTREE, encoding="utf-8") as f:
        lignes = f.readlines()

    total_blocs = (len(lignes) + TAILLE_BLOC - 1) // TAILLE_BLOC
    resultat = []
    bloc_tags = []
    bloc_textes = []

    pbar = tqdm(total=total_blocs, desc="Traduction en cours", ncols=80)

    for ligne in lignes:
        tags, texte = extract_text_and_tags(ligne)
        bloc_tags.append(tags)
        bloc_textes.append(texte)
        if len(bloc_textes) >= TAILLE_BLOC:
            traductions = translate_block(bloc_textes)
            for tags, trad in zip(bloc_tags, traductions):
                resultat.append(rebuild_line(tags, trad))
            bloc_tags = []
            bloc_textes = []
            pbar.update(1)

    if bloc_textes:
        traductions = translate_block(bloc_textes)
        for tags, trad in zip(bloc_tags, traductions):
            resultat.append(rebuild_line(tags, trad))
        pbar.update(1)

    pbar.close()

    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.writelines(resultat)

    print(f"\n✅ Traduction terminée : voir {FICHIER_SORTIE}")

if __name__ == "__main__":
    process_file()
