import os
from pathlib import Path
from google.adk import Agent
from google.genai import types
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

def process_info_request(callback_context):
    """Callback ADK appelé à la réception d'une requête A2A."""
    user_text = ""
    # On récupère le contenu de la requête A2A entrante via la propriété user_content
    if callback_context.user_content and callback_context.user_content.parts:
        user_text = callback_context.user_content.parts[0].text
    
    if not user_text:
        return types.Content(role="model", parts=[types.Part(text="[Erreur SHIELD] Requête vide ou non formatée.")])
        
    print(f"\n[INFO CENTER] 📩 Requête A2A reçue : {user_text[:50]}...")

    # 1. Init LLM
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0
    )
    
    # 2. Extract Hero Name securely
    extract_prompt = f"Tu es un extracteur d'entités. Donne uniquement le nom du héros Marvel principal mentionné dans le texte suivant, sous forme d'un seul mot clé, en minuscules, sans espace ni ponctuation sauf tiret (ex: iron_man, captain_america, hulk, thor, black_widow, spider-man, docteur_strange). Si tu ne trouves pas, réponds INCONNU.\nTexte: {user_text}"
    hero_slug = llm.invoke([HumanMessage(content=extract_prompt)]).content.strip().lower()
    
    # Nettoyage classique
    hero_slug = hero_slug.replace(" ", "_")
    print(f"[INFO CENTER] 🧠 Entité identifiée : {hero_slug}")
    
    if hero_slug == "inconnu":
         return types.Content(role="model", parts=[types.Part(text="[Erreur SHIELD] Aucune entité indexée n'a été identifiée dans la requête.")])
    
    # 3. Read File
    root_dir = Path(__file__).parent.parent.parent
    file_path = root_dir / "data" / "source_files" / f"hero_{hero_slug}.txt"
    
    if not file_path.exists():
         print(f"[INFO CENTER] ❌ Fichier introuvable : {file_path}")
         return types.Content(role="model", parts=[types.Part(text=f"[Dossier Classifié] Aucun dossier d'intervention trouvé pour l'entité : {hero_slug}")])
         
    with open(file_path, "r", encoding="utf-8") as f:
         file_content = f.read()
         
    # 4. Synthesize Formal Report
    print(f"[INFO CENTER] 📄 Dossier trouvé. Synthèse en cours...")
    system_msg = "Tu es l'agent analytique principal du SHIELD (Info Center). À partir du dossier brut suivant, rédige un rapport de synthèse ultra-formel, hautement structuré, froid et clinique destiné à l'Orchestrateur (Nick Fury). Ne fais pas de salutations introductives. Utilise des listes à puces claires et va droit au but (Maximum 200 mots)."
    
    final_report = llm.invoke([
         SystemMessage(content=system_msg),
         HumanMessage(content=f"DOSSIER BRUT:\n{file_content}\n\nQUESTION DU DEMANDEUR:\n{user_text}")
    ]).content
    
    print(f"[INFO CENTER] ✅ Synthèse terminée. Renvoi de la réponse A2A.")
    
    # Le retour de cette fonction outrepasse l'appel au modèle standard (gemini) de l'ADK
    return types.Content(role="model", parts=[types.Part(text=final_report)])

root_agent = Agent(
    name="SHIELD_InfoCenter",
    description="Base de données centrale des super-humains, entités cosmiques, et menaces mondiales.",
    before_agent_callback=process_info_request
)
