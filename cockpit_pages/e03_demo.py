import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E03 : La Bibliothèque Universelle (Resources)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("L'intérêt stratégique des Ressources")
    st.markdown("""
    **Le Concept : Un Accès Standardisé au Savoir**
    Dans un SI, les données sont souvent éparpillées (fichiers, bases, API). 
    Le concept de **Resources** dans MCP permet d'exposer ces données comme des documents web (URIs).
    
    **Ce que cette étape démontre :**
    1.  **Uniformisation** : Peu importe où se trouve le fichier, le client y accède via une adresse universelle (`mcp://...`).
    2.  **Transparence** : L'IA peut explorer cette bibliothèque pour trouver le contexte dont elle a besoin pour répondre.
    3.  **Contrôle** : Le serveur décide exactement ce qu'il expose et comment.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Client [label="Application Cliente", style=filled, color=lightblue];
            Server [label="Serveur de Ressources", style=filled, color=lightgrey];
            
            Client -> Server [label="1. Quelles sont les fiches dispo ?"];
            Server -> Client [label="2. Voici la liste (Timeline, Heroes)"];
            Client -> Server [label="3. Je veux lire 'mcp://marvel/timeline'"];
            Server -> Client [label="4. Envoi du document Markdown"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**E03a : Lancer le Serveur de Ressources**")
        st.markdown("Ce serveur expose des fichiers Markdown (Timeline et MCU Roster) via le protocole MCP.")
        if st.button("🚀 Démarrer Serveur Ressources (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E03a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur E03a lancé sur le port 8001 !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**E03b : L'Explorateur Client**")
        st.markdown("C'est l'application UI qui vient interroger la bibliothéque et afficher son contenu.")

    st.divider()

    if "e03_process" not in st.session_state:
        st.session_state.e03_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Explorateur (E03b)", use_container_width=True) and st.session_state.e03_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E03b_streamlit_mcp_resources.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E03b_streamlit_mcp_resources.py", "--server.port", "8511", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e03_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e03_process is not None:
            print("[Demo_Cockpit] Arrêt de E03b_streamlit_mcp_resources.py...")
            st.session_state.e03_process.terminate()
            st.session_state.e03_process = None
            st.rerun()

    if st.session_state.e03_process is not None:
        st.success("Explorateur E03b en cours d'exécution sur le port 8511.")
        st.components.v1.iframe("http://localhost:8511", height=800, scrolling=True)
    else:
        st.warning("L'explorateur est actuellement arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le code client montre comment utiliser `session.list_resources()` et `session.read_resource(uri)`.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e03 = os.path.join(root_dir, "E03b_streamlit_mcp_resources.py")
        
        with open(file_path_e03, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("Lecture de ressource via URI MCP")
        snippet = "".join(lines[31:40])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.success('''
**Parallèle Entreprise : L'Intranet "AI-Ready"**

Imaginez un serveur MCP branché sur Confluence, SharePoint Docs ou Google Drive.
L'utilisateur de l'agent IA pose une question complexe sur les processus RH de l'entreprise.
Au lieu de fouiller lui-même dans les dossiers, l'Agent :
1. Demande au Serveur MCP RH la liste des documents disponibles.
2. Identifie `mcp://hr/policies/onboarding_2025.pdf`.
3. Lit le contenu *à la volée*.
4. Fournit une réponse exacte et contextualisée.

C'est "l'Intranet" vu par les yeux d'une Machine, sans avoir besoin d'exporter ou copier la donnée manuellement.
    ''')
