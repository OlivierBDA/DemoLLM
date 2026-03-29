import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E02 : L'Agent Connecté via MCP")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Comprendre l'enjeu : L'Intelligence aux commandes")
    st.markdown("""
    **Concept : Le Triangle de l'Action**
    Ici, nous passons de la simple "Découverte" (E01) à l'exécution orchestrée par l'IA.
    
    1.  **Découverte (Discovery)** : Au chargement, l'agent explore le serveur MCP pour récupérer les outils.
    2.  **Raisonnement** : Le LLM analyse votre question et décide d'utiliser l'outil adéquat.
    3.  **Exécution Discrète** : Le client exécute l'ordre du LLM sur le serveur distant et transmet le résultat au LLM.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=TD;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            LLM [label="Intelligence (LLM)", style=filled, color=orange];
            Client [label="Application (Orchestrateur)", style=filled, color=lightblue];
            Server [label="Serveur MCP (Action)", style=filled, color=lightgrey];
            
            User -> Client [label="Question"];
            Client -> LLM [label="Demande d'analyse"];
            LLM -> Client [label="Ordre : 'Appelle Tool X'"];
            Client -> Server [label="Exécution via Réseau"];
            Server -> Client [label="Résultat structuré"];
            Client -> LLM [label="Consigne de synthèse"];
            LLM -> Client [label="Récit final"];
            Client -> User [label="Réponse épique"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.info("Cette étape accède au serveur Marvel Combat (E01a). Si vous l'avez lancé à l'étape E01, il n'est pas nécessaire de le relancer ici.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Démarrer Serveur MCP (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E01a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur E01a lancé !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.markdown('''
            Testez l'Agent MCP en le défiant (ex: *"Combat entre Hulk et Thor"*).
        ''')

    st.divider()

    if "e02_process" not in st.session_state:
        st.session_state.e02_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Agent MCP", use_container_width=True) and st.session_state.e02_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E02_streamlit_mcp_agent.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E02_streamlit_mcp_agent.py", "--server.port", "8510", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e02_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e02_process is not None:
            print("[Demo_Cockpit] Arrêt de E02_streamlit_mcp_agent.py...")
            st.session_state.e02_process.terminate()
            st.session_state.e02_process = None
            st.rerun()

    if st.session_state.e02_process is not None:
        st.success("Agent E02 en cours d'exécution sur le port 8510.")
        st.components.v1.iframe("http://localhost:8510", height=800, scrolling=True)
    else:
        st.warning("L'Agent (Orchestrateur) est arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le client Streamlit se charge de faire le pont entre l'intelligence (LangChain/LLM) et le service technique (MCP Server).")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e02 = os.path.join(root_dir, "E02_streamlit_mcp_agent.py")
        
        with open(file_path_e02, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("Transformation dynamique")
        st.markdown("Les outils MCP (standardisés) sont transformés à la volée en outils LangChain directement au démarrage.")
        snippet = "".join(lines[58:70])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : L'Orchestrateur Universel**

Ce que montre E02, c'est l'essence même de l'**Agentic Workspace** de demain. L'IA (ici LangChain) n'a qu'un unique "client de communication" : le protocole MCP. 

Plutôt que d'apprendre au LLM à parler à Jira via son API REST spécifique, à Salesforce via SOAP, et à GitHub via GraphQL, on intercale MCP :
`LLM -> MCP -> [Jira, Salesforce, GitHub]`

Cela permet aux équipes d'**Enterprise Architecture** de standardiser la gouvernance. Chaque système possède son "Traducteur MCP" (le Serveur), et le super-agent central vient simplement s'y brancher. 
    
</div>
""", unsafe_allow_html=True)
