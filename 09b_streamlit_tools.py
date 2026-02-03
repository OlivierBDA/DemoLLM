import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==============================================================================
# Demo LLM - Étape 9B : Agent avec Appel d'Outils (Tool Calling)
# ==============================================================================
# ASPECT CLÉ : Cette étape montre comment un Agent décide d'utiliser un outil
# externe (API REST) pour accomplir une tâche spécifique.
# ==============================================================================

API_URL = "http://127.0.0.1:8000/simulate_combat"

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE DE L'AGENT ET DE L'OUTIL
# ------------------------------------------------------------------------------

class MarvelCombatAgent:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )

    def call_combat_api(self, h1: str, h2: str):
        """Appel réel à l'API REST."""
        print(f"  [TOOL CALL] Appel de l'API REST : {h1} VS {h2}")
        try:
            params = {"hero1": h1, "hero2": h2}
            response = requests.get(API_URL, params=params, timeout=5)
            if response.status_code == 200:
                print("  [TOOL SUCCESS] Données reçues de l'API.")
                return response.json()
            else:
                print(f"  [TOOL ERROR] Code d'erreur : {response.status_code}")
                return {"error": "L'API de combat a renvoyé une erreur."}
        except Exception as e:
            print(f"  [TOOL ERROR] Connexion impossible : {e}")
            return {"error": "Impossible de contacter l'API de combat (vérifiez qu'elle est lancée)."}

    def run(self, user_input: str):
        """Cycle de raisonnement de l'agent."""
        print(f"\n[ENTRY] Analyse de l'intention : '{user_input[:40]}...'")
        
        # Phase 1 : Détection du besoin d'outil
        # Pour rester didactique, on utilise un prompt qui demande au LLM d'extraire les paramètres
        system_detect = """Tu es un assistant Marvel capable d'organiser des combats.
        Ton rôle est d'analyser si l'utilisateur veut un combat entre deux personnages.
        
        Si oui, extrais les deux noms au format JSON: {"combat": true, "hero1": "...", "hero2": "..."}
        Si non, réponds simplement: {"combat": false}"""
        
        print("  [LLM CALL] Détection de l'intention de combat...")
        res_detect = self.llm.invoke([
            SystemMessage(content=system_detect),
            HumanMessage(content=user_input)
        ])
        
        try:
            decision = json.loads(res_detect.content.strip().replace("```json", "").replace("```", ""))
        except:
            decision = {"combat": False}

        if decision.get("combat"):
            h1, h2 = decision["hero1"], decision["hero2"]
            print(f"[DECISION] Action requise : Combat détecté ({h1} vs {h2})")
            
            # Appel de l'outil
            api_result = self.call_combat_api(h1, h2)
            
            # Phase 2 : Génération de la réponse finale avec les données de l'outil
            print("  [LLM CALL] Interprétation des résultats de l'API...")
            system_final = "Tu es un commentateur de tournoi Marvel. Utilise les données JSON du combat pour faire un compte-rendu épique."
            user_final = f"Résultat technique du combat: {json.dumps(api_result)}\n\nFais-en une réponse naturelle."
            
            res_final = self.llm.invoke([
                SystemMessage(content=system_final),
                HumanMessage(content=user_final)
            ])
            
            return {
                "type": "combat",
                "h1": h1, "h2": h2,
                "api_data": api_result,
                "answer": res_final.content
            }
        else:
            print("[DECISION] Pas de combat. Réponse standard.")
            res_std = self.llm.invoke([
                SystemMessage(content="Tu es un assistant expert Marvel."),
                HumanMessage(content=user_input)
            ])
            return {
                "type": "standard",
                "answer": res_std.content
            }

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Marvel Tool Agent", page_icon="🛠️", layout="wide")

st.title("🥊 Demo LLM - Étape 9 : Tool Calling (API REST)")

# ENCART D'INFORMATION
with st.expander("ℹ️ À propos de cette étape : L'Appel d'Outils", expanded=False):
    st.markdown("""
    **Concept : Connecter le LLM au monde réel**
    Un LLM seul ne peut pas "faire" des choses. Le **Tool Calling** permet à l'agent d'appeler des programmes externes (APIs, calculatrices, moteurs de recherche).
    
    **Architecture de cette démo :**
    - Un service **FastAPI** tourne indépendamment (Étape 9a).
    - L'Agent identifie s'il doit appeler ce service.
    - Il transforme le JSON technique de l'API en une réponse fluide.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur", shape=ellipse];
            Agent [label="Agent LLM", style=filled, color=orange];
            API [label="API REST Combat\\n(FastAPI)", style=filled, color=palegreen];
            
            User -> Agent [label="Organise un combat..."];
            Agent -> API [label="GET /simulate_combat"];
            API -> Agent [label="JSON Results"];
            Agent -> User [label="Réponse épique"];
        }
    ''')
    st.info("⚠️ Assurez-vous que le service `09a_combat_service.py` est bien lancé dans un terminal séparé !")

# Initialisation
if "combat_agent" not in st.session_state:
    st.session_state.combat_agent = MarvelCombatAgent()
    st.session_state.combat_history = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle discussion", use_container_width=True):
        st.session_state.combat_history = []
        st.rerun()
    st.divider()
    st.caption(f"Service API : {API_URL}")

# Historique
for msg in st.session_state.combat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("api_call"):
            st.json(msg["api_call"])

# Input
if prompt := st.chat_input("Faites combattre deux héros ! (ex: 'Fais battre Iron Man contre Thor')"):
    st.chat_message("user").markdown(prompt)
    st.session_state.combat_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("L'agent analyse votre demande...", expanded=True) as status:
            result = st.session_state.combat_agent.run(prompt)
            
            if result["type"] == "combat":
                st.write(f"🎯 **Intention détectée** : Combat entre {result['h1']} et {result['h2']}")
                st.write("📡 **Action** : Appel de l'API de simulation...")
                if "error" in result["api_data"]:
                    st.error(result["api_data"]["error"])
                else:
                    st.success(f"🏆 Vainqueur identifié : {result['api_data']['winner']}")
            else:
                st.write("💬 **Intention** : Discussion standard (pas de combat).")
            
            status.update(label="Analyse terminée", state="complete", expanded=False)

        st.markdown(result["answer"])
        
        # Si c'était un combat, on montre le JSON technique en dessous pour la démo
        api_data = result.get("api_data") if result["type"] == "combat" else None
        if api_data:
            with st.expander("🔍 Voir la réponse brute de l'API (JSON)"):
                st.json(api_data)

        st.session_state.combat_history.append({
            "role": "assistant", 
            "content": result["answer"],
            "api_call": api_data
        })
