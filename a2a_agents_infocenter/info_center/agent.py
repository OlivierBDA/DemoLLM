import os
import json
import hmac
import hashlib
from pathlib import Path
from google.adk import Agent
from google.genai import types
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = b"shield_ultimate_secret_key_2026"

def verify_clearance(trace_id, clearance_level, signature):
    message = f"{trace_id}:{clearance_level}".encode('utf-8')
    expected = hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

def process_info_request(callback_context):
    """Callback ADK appelé à la réception d'une requête A2A."""
    user_text = ""
    if callback_context.user_content and callback_context.user_content.parts:
        user_text = callback_context.user_content.parts[0].text
    
    try:
        envelope = json.loads(user_text)
        trace_id = envelope.get("trace_id", "UNKNOWN")
        clearance = envelope.get("clearance_level", "LEVEL_1")
        signature = envelope.get("signature", "")
        max_hops = int(envelope.get("max_hops", 0))
        path = envelope.get("path", "") + " ➔ Info Center"
        query = envelope.get("query", user_text)
    except Exception:
        trace_id, clearance, signature, max_hops, path, query = "UNKNOWN", "LEVEL_1", "", 10, "Info Center", user_text

    if max_hops <= 0:
        return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": "[Sécurité] Boucle infinie détectée: TTL à 0."}))])

    # 1. Contrôle RBAC
    if clearance != "LEVEL_10":
         return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": f"Accès Refusé. Clearance insuffisante ({clearance}). Requis: LEVEL_10."}))])
         
    if not verify_clearance(trace_id, clearance, signature):
         return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": f"Accès Refusé. Falsification de signature critique détectée (Trace {trace_id})."}))])

    print(f"\n[INFO CENTER] 📩 Requête Sécurisée reçue pour : {query[:40]}")
    print(f"[INFO CENTER] 🛡️ [TRAÇABILITÉ] Trace ID: {trace_id} | TTL Hops: {max_hops}/4 | Clearance validée: {clearance}")
    print(f"[INFO CENTER] 🛡️ [TRAÇABILITÉ] Path reçu: {envelope.get('path', 'UNKNOWN')}")

    # 1. Init LLM
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0
    )
    
    # 2. Extract Entity securely (Hero or Villain)
    extract_prompt = f"Tu es un analyseur d'entités Marvel. Identifie l'entité principale mentionnée dans le texte. Réponds STRICTEMENT au format 'TYPE:nom_entite' où TYPE est soit HERO soit VILAIN, et nom_entite est en minuscules avec des tirets bas (ex: HERO:iron_man, VILAIN:venom, VILAIN:thanos). Si introuvable, réponds INCONNU.\nTexte: {query}"
    ai_response = llm.invoke([HumanMessage(content=extract_prompt)]).content.strip()
    
    if ai_response == "INCONNU" or ":" not in ai_response:
         return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": "[Erreur SHIELD] Aucune entité indexée n'a été identifiée dans la requête."}))])
         
    entity_type, entity_slug = ai_response.split(":", 1)
    entity_slug = entity_slug.strip().lower().replace(" ", "_")
    prefix = "vilain" if entity_type.strip().upper() == "VILAIN" else "hero"
    
    print(f"[INFO CENTER] 🧠 Entité identifiée : {prefix}_{entity_slug}")
    
    # 3. Read File
    root_dir = Path(__file__).parent.parent.parent
    file_path = root_dir / "data" / "source_files" / f"{prefix}_{entity_slug}.txt"
    
    if not file_path.exists():
         print(f"[INFO CENTER] ❌ Fichier introuvable : {file_path}")
         return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": f"[Dossier Classifié] Aucun dossier trouvé pour l'entité : {entity_slug}"}))])
         
    with open(file_path, "r", encoding="utf-8") as f:
         file_content = f.read()
         
    # 4. Synthesize Formal Report
    print(f"[INFO CENTER] 📄 Dossier trouvé. Synthèse en cours...")
    system_msg = "Tu es l'agent analytique principal du SHIELD (Info Center). À partir du dossier brut suivant, rédige un rapport de synthèse ultra-formel, hautement structuré, froid et clinique destiné à l'Orchestrateur (Nick Fury). Ne fais pas de salutations introductives. Utilise des listes à puces claires et va droit au but (Maximum 200 mots)."
    
    final_report = llm.invoke([
         SystemMessage(content=system_msg),
         HumanMessage(content=f"DOSSIER BRUT:\n{file_content}\n\nQUESTION DU DEMANDEUR:\n{query}")
    ]).content
    
    print(f"[INFO CENTER] ✅ Synthèse terminée. Renvoi de la réponse A2A sécurisée.")
    print(f"[INFO CENTER] 🛡️ [TRAÇABILITÉ] Path renvoyé: {path}")
    
    ic_envelope = {
        "trace_id": trace_id,
        "path": path,
        "data": final_report
    }
    
    # Le retour de cette fonction outrepasse l'appel au modèle standard (gemini) de l'ADK
    return types.Content(role="model", parts=[types.Part(text=json.dumps(ic_envelope))])

root_agent = Agent(
    name="SHIELD_InfoCenter",
    description="Base de données centrale des super-humains, entités cosmiques, et menaces mondiales.",
    before_agent_callback=process_info_request
)
