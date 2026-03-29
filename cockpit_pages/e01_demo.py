import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E01 : Le Contrat de Service Universel (Discovery)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Comprendre l'enjeu stratégique : Le Découplage")
    st.markdown("""
    **L'Objectif : Agilité et Interopérabilité**
    MCP (Model Context Protocol) permet de séparer totalement l'intelligence (l'IA) des capacités techniques (les outils métier). 
    
    **Ce que cette étape démontre :**
    1.  **Découverte Dynamique** : Le client ne "connaît" pas les outils à l'avance. Il interroge le serveur pour savoir ce qu'il sait faire.
    2.  **Contrat Standardisé** : Le serveur répond avec un schéma précis (Input/Output). C'est la "fiche technique" du service.
    3.  **Indépendance Totale** : Le serveur peut être mis à jour ou remplacé sans modifier le code de l'application cliente.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Client [label="Application Cliente\\n(Consommateur)", style=filled, color=lightblue];
            Server [label="Serveur MCP\\n(Fournisseur de Services)", style=filled, color=lightgrey];
            
            Client -> Server [label="1. Demande de capacités"];
            Server -> Client [label="2. Présentation des contrats (Tools/Schemas)"];
            Client -> Server [label="3. Appel d'un service spécifique"];
            Server -> Client [label="4. Résultat structuré"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**E01a : Lancer le Serveur MCP**")
        st.markdown("C'est le serveur qui expose les capacités via le protocole MCP (SSE/HTTP).")
        if st.button("🚀 Démarrer Serveur MCP (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E01a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur lancé sur le port 8000 !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**E01b : Exécuter le Client MCP**")
        st.markdown("Interrogez le serveur distant pour découvrir ses capacités (Discovery).")

    st.divider()

    if "e01_process" not in st.session_state:
        st.session_state.e01_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer Client MCP (E01b)", use_container_width=True) and st.session_state.e01_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E01b_streamlit_mcp.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E01b_streamlit_mcp.py", "--server.port", "8509", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e01_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e01_process is not None:
            print("[Demo_Cockpit] Arrêt de E01b_streamlit_mcp.py...")
            st.session_state.e01_process.terminate()
            st.session_state.e01_process = None
            st.rerun()

    if st.session_state.e01_process is not None:
        st.success("Client E01b en cours d'exécution sur le port 8509.")
        st.components.v1.iframe("http://localhost:8509", height=800, scrolling=True)
    else:
        st.warning("Client MCP arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le client implémente un client MCP standard pour lister les outils et les schémas via SSE.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e01 = os.path.join(root_dir, "E01b_streamlit_mcp.py")
        
        with open(file_path_e01, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("La phase de 'Discovery'")
        snippet = "".join(lines[22:34])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : L'Agilité par les Microservices IA**

Aujourd'hui, si une équipe métier crée un nouvel outil (ex: Calculateur d'empreinte carbone), elle doit demander à l'équipe IA de mettre à jour le code des agents pour l'utiliser :
`Agent -> [Code métier mis à jour] -> Outil Carbone`

**Avec MCP (Discovery) :**
L'agent interroge régulièrement la galaxie de services MCP pour demander : "Quoi de neuf ?". Dès que le Serveur Carbone est en ligne, l'Agent apprend son existence, comprend son schéma d'entrée/sortie, et peut l'utiliser **immédiatement**.

C'est l'équivalent IA du modèle **Pub/Sub** et des architectures orientées services (SOA) poussés à leur paroxysme.
    
</div>
""", unsafe_allow_html=True)
