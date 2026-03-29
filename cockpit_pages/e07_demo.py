import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E07 : MCP Prompts (Gabarits Côté Serveur)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("À propos de cette étape : Les Prompts MCP")
    st.markdown("""
    **Concept :**
    Le protocole MCP propose une primitive `prompts`. Un serveur peut exposer des modèles de requêtes préparés à l'avance.
    Cela permet de stocker la **complexité du Prompt Engineering** côté serveur (Logique métier, injection de fichiers) plutôt que de laisser le client s'en charger.
    
    Exemple : Au lieu que l'utilisateur ou le client télécharge un fichier puis écrive "Résume ce fichier", le client demande simplement le prompt `create_hero_card`. Le serveur s'occupe de lire le fichier, de le formatter et d'imposer les instructions strictes au LLM.

    **Architecture de la démo :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            
            User [label="Utilisateur"];
            Client [label="Client (Streamlit)\\n+ LLM", style=filled, color=lightblue];
            Server [label="Serveur MCP\\n(Prompts & Tools)", style=filled, color=orange];
            
            User -> Client [label="Choisit un Prompt"];
            Client -> Server [label="get_prompt(name, args)"];
            Server -> Client [label="Retourne le Prompt généré\\n(incl. fichiers & règles)"];
            Client -> Client [label="Passe le prompt au LLM"];
            Client -> Server [label="(Optionnel) Appelle Outil combat"];
            Client -> User [label="Affiche le Résultat Final"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**E07a : Serveur de Prompts**")
        st.markdown("Ce serveur expose des Prompts paramétrables. Par exemple, donnez un nom de héros, et il construira le prompt avec son fichier markdown joint.")
        if st.button("🚀 Démarrer Serveur Prompts (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E07a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur E07a lancé !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**E07b : LLM Exécuteur**")
        st.markdown("Cette interface interroge le serveur MCP pour récupérer les bons vieux Prompts pré-fabriqués et les passe à LangChain.")

    st.divider()

    if "e07_process" not in st.session_state:
        st.session_state.e07_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer Client Prompts (E07b)", use_container_width=True) and st.session_state.e07_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E07b_streamlit_mcp_prompts.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E07b_streamlit_mcp_prompts.py", "--server.port", "8514", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e07_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e07_process is not None:
            print("[Demo_Cockpit] Arrêt de E07b_streamlit_mcp_prompts.py...")
            st.session_state.e07_process.terminate()
            st.session_state.e07_process = None
            st.rerun()

    if st.session_state.e07_process is not None:
        st.success("Application E07b en cours d'exécution sur le port 8514.")
        st.components.v1.iframe("http://localhost:8514", height=800, scrolling=True)
    else:
        st.warning("Client arrêté.")

with tab_code:
    st.header("Aperçu du Code Source (Client)")
    st.write("Le client implémente une conversion magique : il prend l'objet `Prompt` du serveur MCP, et le convertit en format interprétable par LangChain (SystemMessage, HumanMessage).")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e07b = os.path.join(root_dir, "E07b_streamlit_mcp_prompts.py")
        
        with open(file_path_e07b, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        snippet = "".join(lines[87:111])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : La Gouvernance des Prompts Métiers**

Aujourd'hui, chaque développeur d'une équipe IA va écrire son propre prompt : 
* "Tu es un assistant juridique expert en droit du travail, analyse ci-dessous ... blabla ... ne réponds pas aux questions médicales".

Ce prompt est codé en dur dans l'application cliente.

**Avec MCP Prompts :**
Le serveur "Legal Service" centralise le prompt. Le développeur frontend demande juste : `get_prompt("analyze_contract", {"contract_id": 123})`.
Si la réglementation juridique change, l'expert métier met à jour le Prompt sur le serveur MCP, et **toutes les applications clientes de l'entreprise utilisant ce prompt sont automatiquement à jour**.

C'est la fin du développement en silo.
    
</div>
""", unsafe_allow_html=True)
