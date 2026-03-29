import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape C01 : Agent SQL Basique (Text-to-SQL)")

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
**Concept : RAG sur Données Structurées**
Contrairement au RAG vectoriel (Phase B) qui cherche dans du texte libre, ici le LLM interroge une base de données **relationnelle**. Il traduit votre intention (langage naturel) en langage SQL technique.

**Schéma de fonctionnement :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question", shape=ellipse];
            LLM [label="LLM (SQL Expert)", style=filled, color=orange];
            DB [label="SQLite\\n(heroes, movies)", style=filled, color=palegreen];
            Res [label="Tableau de Données", style=filled, color=lightblue];
            
            Q -> LLM [label="Langage Naturel"];
            LLM -> DB [label="Requête SQL Valide"];
            DB -> Res [label="Résultats (Pandas)"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**C01a : Créer / Mettre à jour la Base SQLite**")
        if st.button("Initialiser la Base de Données (SQLite)", use_container_width=True):
            with st.spinner("Création de la base à partir des CSV..."):
                try:
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    result = subprocess.run(
                        [sys.executable, "C01a_setup_marvel_sql.py"],
                        capture_output=True, text=True, cwd=root_dir, timeout=30
                    )
                    if result.returncode == 0:
                        st.success("Base SQLite (marvel_data.db) créée avec succès !")
                    else:
                        st.error("Erreur d'initialisation.")
                        st.code(result.stderr)
                except Exception as e:
                    st.error(f"Erreur : {e}")
    with col2:
        st.info("**C01b : Tester l'Interface Text-to-SQL**")
        st.markdown('''
        *Questions à tester :*
        1. "Quels sont les héros les plus intelligents ?"
        2. "Quel est le box-office total de tous les films ?"
        ''')

    st.divider()

    if "c01_process" not in st.session_state:
        st.session_state.c01_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'application Text-to-SQL", type="primary", use_container_width=True) and st.session_state.c01_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de C01b_streamlit_sql.py en arrière-plan...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "C01b_streamlit_sql.py", "--server.port", "8505", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.c01_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.c01_process is not None:
            print("[Demo_Cockpit] Arrêt de l'application C01b_streamlit_sql.py...")
            st.session_state.c01_process.terminate()
            st.session_state.c01_process = None
            st.rerun()

    if st.session_state.c01_process is not None:
        st.success("Application C01b en cours d'exécution sur le port 8505.")
        st.components.v1.iframe("http://localhost:8505", height=700, scrolling=True)
    else:
        st.warning("L'application SQL est actuellement arrêtée.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le secret de cette application réside dans la transmission du schéma de la base (le DDL) au LLM pour qu'il comprenne l'architecture.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_c01b = os.path.join(root_dir, "C01b_streamlit_sql.py")
        
        with open(file_path_c01b, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("1. Extraction du Schéma SQL (SQLite_Master)")
        snippet1 = "".join(lines[39:46])
        st.code(snippet1, language="python")

        st.subheader("2. Le Prompt d'Expertise SQL")
        snippet2 = "".join(lines[63:73])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Le fichier C01b_streamlit_sql.py est introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Le "Text-to-SQL" brut est un excellent outil interne pour les analystes de données, mais il est **complexe à déployer à grande échelle** pour deux raisons majeures :
1. **Les Hallucinations Systémiques :** Si vous posez une question faisant appel à un concept métier vague ("Quels sont nos bons clients ?"), le modèle va tenter d'inventer une règle SQL (`WHERE age < 40` ou `WHERE revenu > 1000`) sans aucune base logique.
2. **La Complexité des Bases :** Dans un SI réel (ex: SAP, Salesforce), une base de données peut contenir 500 tables avec des noms obscurs (`TBL_USR_HST_001`). Le LLM ne pourra jamais ingérer un tel schéma dans son prompt, ni deviner le sens caché d'une colonne abrégée.

*C'est pour cela que l'étape C02 (Le Catalogue de Données) est absolument vitale pour fiabiliser l'IA en entreprise !*
    
</div>
""", unsafe_allow_html=True)
