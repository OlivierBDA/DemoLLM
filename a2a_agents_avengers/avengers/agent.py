import os
import requests
import json
import uuid
from google.adk import Agent
from google.genai import types
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

def extract_a2a_text(data: dict) -> str:
    result = data.get("result", {})
    try:
        if result.get("artifacts") and isinstance(result["artifacts"], list) and len(result["artifacts"]) > 0:
            return result["artifacts"][0].get("parts", [{}])[0].get("text", "")
        elif result.get("history") and isinstance(result["history"], list) and len(result["history"]) > 0:
            agent_msgs = [m for m in result["history"] if m.get("role") == "agent"]
            if agent_msgs:
                return agent_msgs[-1].get("parts", [{}])[0].get("text", "")
        # fallback
        return result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text", "")
    except Exception:
        return json.dumps(data)

def process_avengers_request(callback_context):
    user_text = ""
    if callback_context.user_content and callback_context.user_content.parts:
        user_text = callback_context.user_content.parts[0].text
        
    if not user_text:
        return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": "[Erreur Avengers] Cible non spécifiée."}))])
        
    try:
        envelope = json.loads(user_text)
        trace_id = envelope.get("trace_id", "UNKNOWN")
        clearance = envelope.get("clearance_level", "LEVEL_1")
        signature = envelope.get("signature", "")
        max_hops = int(envelope.get("max_hops", 0))
        path = envelope.get("path", "") + " ➔ Avengers"
        query = envelope.get("query", "")
    except Exception:
        # Fallback si pas d'enveloppe
        trace_id, clearance, signature, max_hops, path, query = "UNKNOWN", "LEVEL_1", "", 10, "Avengers", user_text

    if max_hops <= 0:
        return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": "[Sécurité] Boucle infinie détectée: TTL à 0."}))])

    print(f"\n[AVENGERS] ⚡ Intervention requise pour : {query}")
    print(f"[AVENGERS] 🛡️ [TRAÇABILITÉ] Trace ID: {trace_id} | TTL Hops: {max_hops}/4 | Clearance reçue: {clearance}")
    print(f"[AVENGERS] 🛡️ [TRAÇABILITÉ] Path reçu: {envelope.get('path', 'UNKNOWN')}")
    print(f"[AVENGERS] 📡 Sollicitation de l'Info Center via A2A...")
    
    # Prépare l'enveloppe avec 1 hop en moins
    new_envelope = {
        "trace_id": trace_id,
        "clearance_level": clearance,
        "signature": signature,
        "max_hops": max_hops - 1,
        "path": path,
        "query": query
    }
    print(f"[AVENGERS] 🛡️ [TRAÇABILITÉ] Path envoyé: {path}")
    
    url = "http://localhost:8082/a2a/info_center"
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"kind": "text", "text": json.dumps(new_envelope)}]
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        if "error" in data:
            dossier = f"Erreur Info Center : {data['error']}"
        else:
            extracted = extract_a2a_text(data)
            try:
                ic_env = json.loads(extracted)
                if "error" in ic_env:
                     return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": f"[Info Center]: {ic_env['error']}"}))])
                dossier = ic_env.get("data", extracted)
                path = ic_env.get("path", path)
            except Exception:
                dossier = extracted
    except Exception as e:
         return types.Content(role="model", parts=[types.Part(text=json.dumps({"error": f"[Avengers] Communication avec Info Center rompue. ({e})"}))])
         
    print(f"[AVENGERS] 📥 Dossier reçu de l'Info Center. Analyse tactique en cours...")
    print(f"[AVENGERS] 🛡️ [TRAÇABILITÉ] Path de retour reçu: {path}")
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7
    )
    
    sys_msg = """Tu incarnes le centre de commandement tactique des Avengers. 
Tu viens de recevoir le dossier classifié d'une menace de l'Info Center.
Génère un rapport de combat (en 150 mots max) décrivant comment l'équipe des Avengers a affronté cette menace en exploitant précisément les faiblesses mentionnées dans le dossier.
Le style doit être épique, bourré d'action, mais structuré comme un rapport militaire. Ne mets pas de salutations."""

    combat_report = llm.invoke([
         SystemMessage(content=sys_msg),
         HumanMessage(content=f"DOSSIER DE LA MENACE:\n{dossier}")
    ]).content

    print(f"[AVENGERS] ⚔️ Combat résolu. Envoi du rapport à l'Orchestrateur.")
    print(f"[AVENGERS] 🛡️ [TRAÇABILITÉ] Path final renvoyé: {path + ' ➔ Avengers'}")
    
    final_envelope = {
        "trace_id": trace_id,
        "path": path + " ➔ Avengers",
        "hops_used": 1,
        "data": combat_report
    }
    return types.Content(role="model", parts=[types.Part(text=json.dumps(final_envelope))])

root_agent = Agent(
    name="Avengers_Team",
    description="Équipe d'intervention rapide sur le terrain. Spécialisée dans la résolution de conflits.",
    before_agent_callback=process_avengers_request
)
