import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape B03 : Routage Intelligent (LangGraph)")

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
**Ce qui est testé dans cette étape :**
L'utilisation de **LangGraph** pour orchestrer un flux de décision. L'agent n'est plus linéaire : il **réfléchit** au meilleur chemin en fonction de l'intention de l'utilisateur.

**Comment tester l'agent :**
1. Posez une question sur Marvel (ex: "Qui est Hulk ?") -> Le routeur doit activer la branche **RAG**.
2. Posez une question hors-sujet (ex: "Comment faire un gâteau ?") -> Le routeur doit activer la branche **Générale** (politesse et désengagement).

**Logique du Graphe d'Exécution :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, style=filled, fontname="Helvetica", fontsize=10];
            Start [shape=circle, style=filled, color=lightgrey, label="Début"];
            Router [shape=diamond, style=filled, color=orange, label="Routeur ?"];
            RAG [style=filled, color=palegreen, label="Branche RAG\\n(Marvel)"];
            General [style=filled, color=lightcoral, label="Branche Générale\\n(Autre)"];
            End [shape=circle, style=filled, color=lightgrey, label="Fin"];
            
            Start -> Router;
            Router -> RAG [label="Sujet Marvel", fontsize=10];
            Router -> General [label="Hors Sujet", fontsize=10];
            RAG -> End;
            General -> End;
        }
    ''')
    st.info("💡 Un \"Agent\" IA n'est souvent rien de plus qu'un grand graphe de décision où un outil (LLM) est utilisé pour choisir le prochain nœud à exécuter.")

with tab_demo:
    st.header("Démonstration Technique")
    
    if "b03_process" not in st.session_state:
        st.session_state.b03_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Agent LangGraph", type="primary", use_container_width=True) and st.session_state.b03_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de B03_langgraph_routing.py en arrière-plan...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "B03_langgraph_routing.py", "--server.port", "8504", "--server.headless", "true"],
                cwd=root_dir,
                stdout=sys.stdout,
                stderr=sys.stderr
            )
            st.session_state.b03_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.b03_process is not None:
            print("[Demo_Cockpit] Arrêt de l'application B03_langgraph_routing.py...")
            st.session_state.b03_process.terminate()
            st.session_state.b03_process = None
            st.rerun()

    if st.session_state.b03_process is not None:
        st.success("Application B03 en cours d'exécution sur le port 8504.")
        st.components.v1.iframe("http://localhost:8504", height=700, scrolling=True)
    else:
        st.warning("L'application Agent est actuellement arrêtée.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le routage est défini grâce aux fonctions de noeuds de LangGraph (`router_node`, etc.) et assemblé dans le `StateGraph`.")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "B03_langgraph_routing.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        st.markdown("**La définition du Routeur Intelligent :**")
        snippet1 = "".join(lines[88:117])
        st.code(snippet1, language="python")

        st.markdown("**L'Assemblage du Graphe :**")
        snippet2 = "".join(lines[138:152])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Fichier B03_langgraph_routing.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Le routage est l'étape fondatrice pour passer d'un simple "Chatbot RAG" à un **Bot Intelligent (Agentic Workflow)** dans une entreprise.

**Cas d'Usage Réels (Orchestration) :**
* **Support IT (Helpdesk) :** Si la question concerne le mot de passe, router vers l'API A. Si cela concerne un logiciel, router vers la Base Documentaire RAG B. Si c'est complexe, escalader vers le noeud "Agent Humain".
* **Sécurité & Conformité :** LangGraph sert très souvent à créer des garde-fous (Guardrails). Un noeud "Inspecteur" peut filtrer systématiquement la sortie du LLM pour s'assurer qu'il ne divulgue pas de PII (Données Personnelles) avant de l'envoyer à l'utilisateur.
* **Fiabilité :** Le graphe permet d'implémenter des redondances (Fallback). "Si l'API X échoue, exécute le Nœud Y pour la réparation".
    
</div>
""", unsafe_allow_html=True)
