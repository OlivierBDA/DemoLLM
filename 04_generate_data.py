import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

# ==============================================================================
# Demo LLM - Étape 4 : Génération de Données Sources pour le RAG
# ==============================================================================
# Ce programme génère des fiches descriptives détaillées sur l'univers MCU.
# ASPECT CLÉ : Chaque fichier est généré de manière autonome et incrémentale.
# Le but est de créer une base de connaissances textuelle qui sera utilisée
# lors de l'étape du RAG (Retrieval Augmented Generation).
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR LLM (Interaction spécifique pour la génération)
# ------------------------------------------------------------------------------

def init_llm():
    """Initialise le client LLM agnostique pour la génération de contenu."""
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7
    )

def generate_entity_content(llm, entity_name, entity_type):
    """
    Demande au LLM de générer un contenu très détaillé.
    ASPECT CLÉ : On utilise un prompt très directif pour obtenir un texte long et structuré.
    """
    if entity_type == "hero":
        prompt = f"""Génère une fiche ultra-détaillée sur le héros Marvel du MCU (film) : {entity_name}.
        La réponse doit être longue (environ 1000 mots minimum) et structurée avec les sections suivantes :
        1. Identité et Origines (Focus MCU)
        2. Capacités, Armes et Équipements techniques
        3. Parcours complet dans le MCU (de sa première apparition à Endgame ou plus tard)
        4. Relations clés et Alliances
        5. Importance stratégique dans la chronologie globale.
        
        Sois précis sur les noms des technologies, des lieux et des événements. 
        N'utilise pas de style Markdown complexe, juste des titres de sections clairs."""
    else:
        prompt = f"""Génère un dossier complet sur l'arc narratif/film du MCU : {entity_name}.
        La réponse doit être longue (environ 1000 mots minimum) et structurée avec les sections suivantes :
        1. Synopsis Détaillé
        2. Événements Clés et Points de Bascule
        3. Personnages Centraux et leurs enjeux
        4. Conséquences et Impact sur la suite du MCU
        5. Thématiques et secrets de production.
        
        Sois très exhaustif sur l'intrigue.
        N'utilise pas de style Markdown complexe, juste des titres de sections clairs."""

    print(f"   [LLM] Génération en cours pour : {entity_name}...")
    messages = [
        SystemMessage(content="Tu es un historien expert de l'univers Cinématographique Marvel (MCU)."),
        HumanMessage(content=prompt)
    ]
    
    response = llm.invoke(messages)
    return response.content

# ------------------------------------------------------------------------------
# SECTION 2 : GESTION DES FICHIERS ET PROCESSUS
# ------------------------------------------------------------------------------

def load_config():
    """Charge la liste des entités à générer depuis le fichier JSON."""
    with open("data_config.json", "r", encoding="utf-8") as f:
        return json.load(f)

def ensure_data_dir():
    """S'assure que le dossier de destination existe."""
    target_dir = os.path.join("data", "source_files")
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)
        print(f"[Info] Dossier créé : {target_dir}")
    return target_dir

def main():
    print("--- Demo LLM - Étape 4 : Générateur de Base de Connaissances ---")
    
    # 1. Initialisations
    try:
        config = load_config()
        llm = init_llm()
        target_dir = ensure_data_dir()
    except Exception as e:
        print(f"Erreur d'initialisation : {e}")
        return

    # 2. Traitement des héros
    print("\n--- Traitement des Héros ---")
    for hero in config.get("heroes", []):
        # ASPECT CLÉ : Assainissement du nom de fichier pour Windows (retrait des : et autres caractères invalides)
        clean_name = hero.replace(':', '').replace('(', '').replace(')', '').replace(' ', '_').lower()
        filename = f"hero_{clean_name}.txt"
        filepath = os.path.join(target_dir, filename)
        
        if os.path.exists(filepath):
            print(f" [OK] La fiche pour '{hero}' existe déjà. Skipping.")
        else:
            try:
                content = generate_entity_content(llm, hero, "hero")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f" [+] Fiche créée : {filename}")
            except Exception as e:
                print(f" [!] Erreur pour {hero} : {e}")

    # 3. Traitement des films
    print("\n--- Traitement des Films/Arcs ---")
    for movie in config.get("movies", []):
        # ASPECT CLÉ : Assainissement du nom de fichier pour Windows
        clean_name = movie.replace(':', '').replace('(', '').replace(')', '').replace(' ', '_').lower()
        filename = f"movie_{clean_name}.txt"
        filepath = os.path.join(target_dir, filename)
        
        if os.path.exists(filepath):
            print(f" [OK] La fiche pour '{movie}' existe déjà. Skipping.")
        else:
            try:
                content = generate_entity_content(llm, movie, "movie")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f" [+] Fiche créée : {filename}")
            except Exception as e:
                print(f" [!] Erreur pour {movie} : {e}")

    print("\n--- Terminé ! Vos fichiers sources sont prêts dans data/source_files/ ---")

if __name__ == "__main__":
    main()
