import streamlit as st
import requests
import json
import time

# ==============================================================================
# Demo LLM - Phase G : Étape 1 : Découverte A2A
# ==============================================================================
# Ce script simule le terminal de Nick Fury. Il effectue une découverte
# sur les ports des Agents A2A et affiche leurs "AgentCard" (Manifesto).
# ==============================================================================

st.set_page_config(page_title="A2A Discovery Terminal", page_icon="📡", layout="wide")

st.title("📡 Terminal SHIELD : Découverte A2A (Discovery)")
st.markdown("Ce terminal permet d'interroger le réseau pour découvrir les Agents disponibles via le standard **Agent-To-Agent (A2A)**.")

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE DE DÉCOUVERTE (ORCHESTRATEUR)
# ------------------------------------------------------------------------------

# Ports et noms des applications (simule une découverte réseau locale)
AGENTS = {
    "avengers": {"name": "Avengers", "port": 8081},
    "info_center": {"name": "Info Center", "port": 8082}
}

def fetch_agent_card(app_name, port):
    """Effectue une requête HTTP GET pour récupérer le manifeste de l'agent."""
    # La spec A2A impose l'accès à /.well-known/agent-card.json
    url = f"http://localhost:{port}/a2a/{app_name}/.well-known/agent-card.json"
    try:
        response = requests.get(url, timeout=2)
        if response.status_code == 200:
            return response.json()
        return {"error": f"Erreur HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

def display_agent_card_ui(agent_display_name, card_data):
    """Affiche de manière stylisée les informations du manifeste."""
    if "error" in card_data:
        st.error(f"Impossible de contacter l'agent **{agent_display_name}** : {card_data['error']}")
        return
        
    # L'ADK structure la réponse différemment selon la version, la racine inclut généralement 'agent'
    # Fallback pour la démo si la spec exacte n'est pas remplie
    name = card_data.get("agent_name", card_data.get("name", card_data.get("agent", {}).get("name", "Inconnu")))
    desc = card_data.get("description", card_data.get("agent", {}).get("description", "Aucune description"))
    version = card_data.get("version", card_data.get("agent", {}).get("version", "N/A"))
    
    # Choix de l'avatar
    avatar = "🦸" if "Avengers" in name else "🧠" if "InfoCenter" in name else "🤖"
    
    with st.container(border=True):
        col1, col2 = st.columns([1, 4])
        with col1:
            st.markdown(f"<h1 style='text-align: center; font-size: 4em;'>{avatar}</h1>", unsafe_allow_html=True)
        with col2:
            st.subheader(f"{name} (v{version})")
            st.markdown(f"**Description :** {desc}")
            st.markdown("**(Statut : En Ligne ✅)**")

# Interface de déclenchement
if st.button("Lancer le protocole de Découverte (Discovery) 🔍", type="primary", use_container_width=True):
    with st.spinner("Analyse des fréquences réseau SHIELD..."):
        time.sleep(1) # Simulation de recherche réseau
        
        cols = st.columns(len(AGENTS))
        
        for idx, (app_name, agent_info) in enumerate(AGENTS.items()):
            with cols[idx]:
                st.markdown(f"### Port Cible : `{agent_info['port']}`")
                card = fetch_agent_card(app_name, agent_info['port'])
                
                # Onglets pour montrer le brut vs le rendu UI
                tab_ui, tab_json = st.tabs(["📇 Carte Identité", "⚙️ JSON Brut (Protocole)"])
                
                with tab_ui:
                    display_agent_card_ui(agent_info['name'], card)
                    
                with tab_json:
                    if "error" in card:
                        st.json(card)
                    else:
                        st.json(card)
