import streamlit as st
import requests
import json
import os
import uuid
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool

# ==============================================================================
# Demo LLM - Phase G : Étape 3 : Chaîne A2A (3 Agents)
# ==============================================================================
import hmac
import hashlib

SECRET_KEY = b"shield_ultimate_secret_key_2026"

def sign_clearance(trace_id, clearance_level):
    message = f"{trace_id}:{clearance_level}".encode('utf-8')
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()

@tool
def ask_avengers(villain_name: str) -> str:
    """
    Ordonne à l'équipe des Avengers d'intervenir contre une menace ou un super-vilain.
    """
    print(f"\n[ORCHESTRATEUR] 📡 Appel A2A HTTP POST vers Avengers pour intervention sur : {villain_name}")
    url = "http://localhost:8081/a2a/avengers"
    
    trace_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
    clearance_level = "LEVEL_10"
    signature = sign_clearance(trace_id, clearance_level)
    
    envelope = {
        "trace_id": trace_id,
        "clearance_level": clearance_level,
        "signature": signature,
        "max_hops": 4, # TTL de 4 agents max
        "path": "Orchestrateur(NickFury)",
        "query": villain_name
    }
    print(f"[ORCHESTRATEUR] 🛡️ [TRAÇABILITÉ] Trace ID: {trace_id} | Path envoyé: Orchestrateur(NickFury)")
    
    payload = {
        "jsonrpc": "2.0",
        "id": str(uuid.uuid4()),
        "method": "message/send",
        "params": {
            "message": {
                "messageId": str(uuid.uuid4()),
                "role": "user",
                "parts": [{"kind": "text", "text": json.dumps(envelope)}]
            }
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60) # 1 minute car la chaîne sollicite 2 agents + 2 LLM
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                 return json.dumps({
                     "raw_json": data,
                     "extracted_text": f"Erreur de l'agent A2A Avengers : {data['error']}",
                     "trace_path": "Inconnu",
                     "trace_id": trace_id
                 })
                 
            result = data.get("result", {})
            try:
                if result.get("artifacts") and isinstance(result["artifacts"], list) and len(result["artifacts"]) > 0:
                    extracted = result["artifacts"][0].get("parts", [{}])[0].get("text")
                elif result.get("history") and isinstance(result["history"], list) and len(result["history"]) > 0:
                    agent_msgs = [m for m in result["history"] if m.get("role") == "agent"]
                    if agent_msgs:
                        extracted = agent_msgs[-1].get("parts", [{}])[0].get("text")
                    else:
                        extracted = json.dumps(result, indent=2)
                else:
                    text_fallback = result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text")
                    extracted = text_fallback if text_fallback else json.dumps(result, indent=2)
            except Exception:
                extracted = json.dumps(result, indent=2)
            
            # Essayer de lire l'enveloppe de retour
            try:
                env_resp = json.loads(extracted)
                if "error" in env_resp:
                    final_text = env_resp["error"]
                else:
                    final_text = env_resp.get("data", extracted)
                final_path = env_resp.get("path", "Inconnu")
                final_trace = env_resp.get("trace_id", trace_id)
                final_hops = env_resp.get("hops_used", "Inconnu")
            except Exception:
                final_text = extracted
                final_path = "Inconnu"
                final_trace = trace_id
                final_hops = "Inconnu"
                
            return json.dumps({
                "raw_json": data,
                "extracted_text": final_text,
                "trace_path": final_path,
                "trace_id": final_trace,
                "hops_used": final_hops
            })
        else:
            return f"Erreur réseau : Code {response.status_code}"
    except Exception as e:
        return f"Échec de connexion A2A : L'Agent Avengers n'est probablement pas démarré. ({e})"

class NickFuryOrchestrator:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        
        self.tools = [ask_avengers]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = """Tu es Nick Fury, l'ancien directeur du SHIELD.
Si un utilisateur signale une attaque de super-vilain ou une menace majeure, tu DOIS utiliser l'outil 'ask_avengers' pour envoyer l'équipe.
Une fois le rapport d'intervention des Avengers reçu, fais une synthèse rassurante à l'utilisateur."""

    def run(self, user_input: str):
        print(f"\n[ORCHESTRATEUR] 🗣️ Réception demande : '{user_input[:40]}...'")
        
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]

        ai_msg = self.llm_with_tools.invoke(messages)
        
        if ai_msg.tool_calls:
            print(f"[ORCHESTRATEUR] 🤖 Décision prise : Délégation à un sous-agent via A2A ({ai_msg.tool_calls[0]['name']})")
            tool_call = ai_msg.tool_calls[0]
            
            tool_output_str = ask_avengers.invoke(tool_call["args"])
            
            try:
                output_data = json.loads(tool_output_str)
                raw_json_str = json.dumps(output_data.get("raw_json", {}), indent=2)
                extracted_text = output_data.get("extracted_text", tool_output_str)
                trace_path = output_data.get("trace_path", "Inconnu")
                trace_id = output_data.get("trace_id", "Inconnu")
                hops_used = output_data.get("hops_used", "Inconnu")
            except Exception:
                raw_json_str = tool_output_str
                extracted_text = tool_output_str
                trace_path = "Inconnu"
                trace_id = "Inconnu"
                hops_used = "Inconnu"
            
            messages.append(ai_msg)
            messages.append(ToolMessage(extracted_text, tool_call_id=tool_call["id"]))
            
            print("[ORCHESTRATEUR] 📥 Réponse des Avengers reçue. Rapport final au civil...")
            print(f"[ORCHESTRATEUR] 🛡️ [TRAÇABILITÉ] Path final reçu: {trace_path}")
            synthesis_prompt = f"""Voici le rapport d'intervention de l'équipe Avengers :
            ---
            {extracted_text}
            ---
            Rédige ta réponse finale au citoyen pour le rassurer."""

            final_response = self.llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input),
                HumanMessage(content=synthesis_prompt)
            ])
            
            return {
                "type": "tool",
                "tool_name": tool_call["name"],
                "args": tool_call["args"],
                "raw_json": raw_json_str,
                "extracted_text": extracted_text,
                "trace_path": trace_path,
                "trace_id": trace_id,
                "hops_used": hops_used,
                "answer": final_response.content
            }
        else:
            print("[ORCHESTRATEUR] 🤖 Décision prise : Réponse directe sans consultation.")
            return {
                "type": "standard",
                "answer": ai_msg.content
            }

# ------------------------------------------------------------------------------
# INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Terminal Fury - Chaîne A2A", page_icon="🔗", layout="wide")

st.title("🔗 Terminal Sécurisé : Nick Fury (Chaîne de Commandement)")
st.markdown("Interface directe avec le Directeur Fury. Il coordonne les Avengers, qui eux-mêmes consultent l'Info Center.")

if "g03_agent" not in st.session_state:
    st.session_state.g03_agent = NickFuryOrchestrator()
    st.session_state.g03_history = []

with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle Conversation", use_container_width=True):
        st.session_state.g03_history = []
        st.rerun()

for msg in st.session_state.g03_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: 'Nick, Venom attaque le centre-ville !'"):
    st.chat_message("user").markdown(prompt)
    st.session_state.g03_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="👁️"):
        with st.status("Traitement par la chaîne de commandement...", expanded=True) as status:
            result = st.session_state.g03_agent.run(prompt)
            
            if result["type"] == "tool":
                st.write(f"📡 **Protocole A2A Initié** : Ordre aux `{result['tool_name']}`")
                st.write(f"📝 **Cible identifiée** : `{result['args']}`")
                
                st.info(f"**🛡️ Traçabilité d'Entreprise (Security & Routing)**\n\n"
                        f"- **ID de Session A2A** : `{result.get('trace_id', 'Inconnu')}`\n"
                        f"- **Sauts A2A (TTL)** : `il reste {result.get('hops_used', 'Inconnu')} saut(s) sur 4 max`\n"
                        f"- **Chemin Parcouru** : `{result.get('trace_path', 'Inconnu')}`")
                
                with st.expander("Rapport de Combat des Avengers (Markdown)"):
                    st.markdown(result["extracted_text"])
                with st.expander("Message A2A Brut (JSON-RPC) renvoyé par les Avengers au SHIELD"):
                    st.code(result["raw_json"], language="json")
            
            status.update(label="Chaîne opérationnelle terminée", state="complete", expanded=False)

        st.markdown(result["answer"])
        st.session_state.g03_history.append({"role": "assistant", "content": result["answer"]})
