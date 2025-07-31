import openai
import os
import re
from openai import OpenAI
from dotenv import load_dotenv

# --------------------------
# CONFIGURATION
# --------------------------
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
FICHIER_ENTREE = "echantillon.txt"
FICHIER_SORTIE = "echantillon_traduit.txt"
MODEL = "gpt-4"
MAX_TOKENS_PAR_BLOC = 2048

TRANSCODAGE = {
    "ê": "^", "à": "<", "é": ">", "è": "{",
    "ù": "}", "ô": "_", "î": "|", "â": "[",
    "À": "A", "É": "E"
}

client = OpenAI(api_key=API_KEY)

def is_english(line: str) -> bool:
    texte_sans_balises = re.sub(r"\[[^\]]*\]", "", line).strip()
    mots = texte_sans_balises.split()
    if not mots:
        return False
    return all(re.match(r"^[a-zA-Z0-9.,'!?\-]+$", mot) for mot in mots)

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
    lignes_nettoyees = [re.sub(r"\[[^\]]*\]", "", l).strip() for l in lines]
    joined = "\n".join(lignes_nettoyees)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "Tu es un traducteur professionnel. Traduis fidèlement chaque ligne de ce dialogue de jeu vidéo en français, sans toucher aux balises de type [A], [xxx] ou autres. Utilise toujours un E au lieu de É, et un A au lieu de À, même en majuscule."},
            {"role": "user", "content": joined}
        ],
        temperature=0.2,
        max_tokens=MAX_TOKENS_PAR_BLOC
    )
    return response.choices[0].message.content.splitlines()

def process_file():
    with open(FICHIER_ENTREE, encoding="utf-8") as f:
        lignes = f.readlines()

    resultat = []
    bloc_tags = []
    bloc_textes = []

    for ligne in lignes:
        if is_english(ligne):
            tags, texte = extract_text_and_tags(ligne)
            bloc_tags.append(tags)
            bloc_textes.append(texte)
        else:
            if bloc_textes:
                print("\n🔁 Traduction d'un bloc anglais...")
                traductions = translate_block(bloc_textes)
                for tags, trad in zip(bloc_tags, traductions):
                    resultat.append(rebuild_line(tags, trad))
                bloc_tags = []
                bloc_textes = []
            resultat.append(transcode(ligne.strip()) + "\n")

    if bloc_textes:
        print("\n🔁 Traduction finale d'un dernier bloc...")
        traductions = translate_block(bloc_textes)
        for tags, trad in zip(bloc_tags, traductions):
            resultat.append(rebuild_line(tags, trad))

    with open(FICHIER_SORTIE, "w", encoding="utf-8") as f:
        f.writelines(resultat)

    print(f"\n✅ Traduction terminée : voir {FICHIER_SORTIE}")

if __name__ == "__main__":
    process_file()
