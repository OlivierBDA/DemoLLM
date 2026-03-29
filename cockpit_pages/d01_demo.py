import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape D01 : Agent avec Outils (Tool Calling)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Concept et Explication")
    st.markdown("""
    **La 'vraie' méthode Agentique : L'Appel d'Outils Natifs (`bind_tools`)**
    
    Jusqu'à présent, le LLM répondait avec du texte ou générait du SQL qu'on exécutait "manuellement" dans le code. 
    Ici, le LLM possède **officiellement une boîte à outils** (des fonctions Python documentées).
    
    1. **Déclaration** : On donne la signature de la fonction technique au LLM.
    2. **Autonomie** : Le LLM décide seul s'il doit appeler l'outil ou s'il sait répondre directement ("Comment vas-tu ?").
    3. **Protocole de communication** : Le LLM demande l'exécution via une structure JSON spéciale (`tool_calls`), et on lui renvoie le résultat technique via un `ToolMessage`.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question Utilisateur\\n('Fais combattre Thor et Hulk')", shape=ellipse];
            LLM [label="LLM (avec bind_tools)", style=filled, color=orange];
            Tool [label="Fonction API\\n(simulate_combat)", style=filled, color=palegreen];
            Resp [label="Récit épique", style=filled, color=lightblue];
            
            Q -> LLM;
            LLM -> Tool [label=" JSON: {hero1: 'Thor', hero2: 'Hulk'}"];
            Tool -> LLM [label=" JSON: {winner: 'Thor', commentary: '...'}"];
            LLM -> Resp;
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**D01a : Lancer l'API Externe (L'Outil)**")
        st.markdown("Ce service simule un combat. C'est un pur programme classique, **sans lien initial avec l'IA**.")
        if st.button("🚀 Démarrer l'API Combat (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_D01a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("API de combat lancée sur le port 8000 !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**D01b : Interagir avec l'Agent**")
        st.markdown('''
        *Une fois l'API démarrée, testez l'agent :*
        1. "Fais s'affronter Hulk et Iron Man !"
        2. "Qui gagnerait entre Thor et Captain America ?"
        3. "Météo à Paris ?" *(Pour voir s'il tente d'utiliser l'outil à tort)*
        ''')

    st.divider()

    if "d01_process" not in st.session_state:
        st.session_state.d01_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Agent Tool Calling", use_container_width=True) and st.session_state.d01_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de D01b_streamlit_tools.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "D01b_streamlit_tools.py", "--server.port", "8507", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.d01_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.d01_process is not None:
            print("[Demo_Cockpit] Arrêt de D01b_streamlit_tools.py...")
            st.session_state.d01_process.terminate()
            st.session_state.d01_process = None
            st.rerun()

    if st.session_state.d01_process is not None:
        st.success("Application D01b en cours d'exécution sur le port 8507.")
        st.components.v1.iframe("http://localhost:8507", height=800, scrolling=True)
    else:
        st.warning("L'Agent est actuellement arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le moment magique où le LLM devient un programmeur capable d'utiliser des APIs.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_d01b = os.path.join(root_dir, "D01b_streamlit_tools.py")
        
        with open(file_path_d01b, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("1. La Déclaration de l'Outil (`@tool`)")
        st.markdown("La docstring est vitale : c'est elle qui explique au modèle **quand** et **comment** utiliser la fonction.")
        snippet1 = "".join(lines[25:31])
        st.code(snippet1, language="python")

        st.subheader("2. L'Attachement de la boîte à outils")
        snippet2 = "".join(lines[56:59])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Le fichier D01b_streamlit_tools.py est introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : L'Agent qui "Fait" au lieu de juste "Dire"**

Le Tool Calling (ou Function Calling) est ce qui permet de passer d'un simple "chatbot" (qui génère du texte) à un véritable **Agent Autonome** qui interagit avec le SI de l'entreprise.

**Exemples réels :**
*  **Agent RH** : Connecté à l'API de Workday (`poser_conges(date_debut, date_fin)`). L'utilisateur demande : "Je veux poser mon vendredi". L'agent comprend la date, appelle l'API, et vous confirme le jour posé.
*  **Agent DevOps** : Connecté à AWS ou GitHub. "Relance le pipeline du projet X". L'IA utilise l'outil `trigger_github_action('projet_X')`.
*  **Agent CRM** : "Crée un ticket Jira pour ce bug que je viens de t'expliquer". L'IA utilise `create_jira_ticket(title, description)`.

**Le grand défi** de l'ingénierie moderne est de sécuriser ces outils : si l'IA a l'outil `delete_database()`, elle pourrait l'utiliser par erreur. C'est pourquoi on introduit souvent une étape de confirmation humaine ("Human-in-the-loop") avant l'exécution finale.
    
</div>
""", unsafe_allow_html=True)
