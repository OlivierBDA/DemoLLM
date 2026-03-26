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
# Demo LLM - Phase G : Étape 2 : A2A Chat (Collaboration Inter-Agents)
# ==============================================================================

import hmac
import hashlib

SECRET_KEY = b"shield_ultimate_secret_key_2026"

def sign_clearance(trace_id, clearance_level):
    message = f"{trace_id}:{clearance_level}".encode('utf-8')
    return hmac.new(SECRET_KEY, message, hashlib.sha256).hexdigest()

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE ORCHESTRATEUR (NICK FURY) ET APPEL A2A
# ------------------------------------------------------------------------------

@tool
def ask_info_center(hero_name: str) -> str:
    """
    Consulte l'Agent A2A Info Center pour récupérer un dossier intellectuel sur un super-héros.
    À utiliser dès que l'utilisateur demande des informations précises sur un membre des Avengers ou une entité menaçante.
    """
    print(f"\n[ORCHESTRATEUR] 📡 Appel A2A HTTP POST vers Info Center pour: {hero_name}")
    url = "http://localhost:8082/a2a/info_center"
    
    trace_id = f"TX-{uuid.uuid4().hex[:8].upper()}"
    clearance_level = "LEVEL_10"
    signature = sign_clearance(trace_id, clearance_level)
    
    envelope = {
        "trace_id": trace_id,
        "clearance_level": clearance_level,
        "signature": signature,
        "max_hops": 2, 
        "path": "Orchestrateur(NickFury)",
        "query": hero_name
    }
    
    # Payload JSON-RPC 2.0 standard selon la spec A2A
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
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                 return f"Erreur de l'agent A2A Info Center : {data['error']}"
                 
            # Le résultat A2A est typiquement dans data['result']['messages'][...]['parts'][...]['text']
            # On navigue de manière robuste ou on dump le json entier
            result = data.get("result", {})
            try:
                # La réponse d'une tâche A2A place le contenu du before_agent_callback soit 
                # dans "artifacts", soit dans le dernier message de l'"history".
                if result.get("artifacts") and isinstance(result["artifacts"], list) and len(result["artifacts"]) > 0:
                    extracted = result["artifacts"][0].get("parts", [{}])[0].get("text")
                elif result.get("history") and isinstance(result["history"], list) and len(result["history"]) > 0:
                    # On prend le dernier message de l'agent
                    agent_msgs = [m for m in result["history"] if m.get("role") == "agent"]
                    if agent_msgs:
                        extracted = agent_msgs[-1].get("parts", [{}])[0].get("text")
                    else:
                        extracted = json.dumps(result, indent=2)
                else:
                    # Fallback sur un autre format
                    text_fallback = result.get("status", {}).get("message", {}).get("parts", [{}])[0].get("text")
                    extracted = text_fallback if text_fallback else json.dumps(result, indent=2)
            except Exception:
                extracted = json.dumps(result, indent=2)
                
            try:
                env_resp = json.loads(extracted)
                if "error" in env_resp:
                    final_text = env_resp["error"]
                else:
                    final_text = env_resp.get("data", extracted)
            except Exception:
                final_text = extracted
                
            return json.dumps({
                "raw_json": data,
                "extracted_text": final_text
            })
        else:
            return f"Erreur réseau : Code {response.status_code}"
    except Exception as e:
        return f"Échec de connexion A2A : L'Agent Info Center n'est probablement pas démarré. ({e})"

class NickFuryOrchestrator:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        
        self.tools = [ask_info_center]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = """Tu es Nick Fury, l'ancien directeur du SHIELD. Tu parles avec la gravité et l'autorité qui te caractérisent. Tu es concis.
Si l'utilisateur te demande des informations ou le dossier d'un super-héros précis, tu DOIS ABSOLUMENT utiliser l'outil 'ask_info_center' pour contacter la base de données via le protocole A2A.
Dès que tu reçois le rapport de l'Info Center, reformule-le pour l'utilisateur en y ajoutant ta touche personnelle de commandement."""

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
            
            tool_output_str = ask_info_center.invoke(tool_call["args"])
            
            try:
                output_data = json.loads(tool_output_str)
                raw_json_str = json.dumps(output_data.get("raw_json", {}), indent=2)
                extracted_text = output_data.get("extracted_text", tool_output_str)
            except Exception:
                raw_json_str = tool_output_str
                extracted_text = tool_output_str
            
            messages.append(ai_msg)
            messages.append(ToolMessage(extracted_text, tool_call_id=tool_call["id"]))
            
            print("[ORCHESTRATEUR] 📥 Réponse de l'Info Center reçue. Synthèse finale en cours...")
            synthesis_prompt = f"""Voici le rapport reçu de ton sous-agent Info Center :
            ---
            {extracted_text}
            ---
            Rédige ta réponse finale."""

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
                "answer": final_response.content
            }
        else:
            print("[ORCHESTRATEUR] 🤖 Décision prise : Réponse directe sans consultation.")
            return {
                "type": "standard",
                "answer": ai_msg.content
            }

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Terminal Nick Fury - A2A", page_icon="👁️", layout="wide")

st.title("👁️ Terminal Sécurisé : Nick Fury")
st.markdown("Interface directe avec le Directeur Fury. Il est connecté à la grille A2A du SHIELD.")

if "g02_agent" not in st.session_state:
    st.session_state.g02_agent = NickFuryOrchestrator()
    st.session_state.g02_history = []

with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle Conversation", use_container_width=True):
        st.session_state.g02_history = []
        st.rerun()

for msg in st.session_state.g02_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: 'Nick, que sais-tu sur Iron Man ?'"):
    st.chat_message("user").markdown(prompt)
    st.session_state.g02_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="👁️"):
        with st.status("Traitement par l'Orchestrateur...", expanded=True) as status:
            result = st.session_state.g02_agent.run(prompt)
            
            if result["type"] == "tool":
                st.write(f"📡 **Protocole A2A Initié** : Appel à l'Agent `{result['tool_name']}`")
                st.write(f"📝 **Entité ciblée** : `{result['args']}`")
                with st.expander("Contenu du dossier (Markdown)"):
                    st.markdown(result["extracted_text"])
                with st.expander("Message A2A Brut (JSON-RPC)"):
                    st.code(result["raw_json"], language="json")
            
            status.update(label="Analyse terminée", state="complete", expanded=False)

        st.markdown(result["answer"])
        st.session_state.g02_history.append({"role": "assistant", "content": result["answer"]})
