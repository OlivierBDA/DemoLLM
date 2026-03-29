import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape C02 : Agent de Gouvernance (Catalogue & Sémantique)")

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
**Concept : Séparation Métier / Technique (Data Stewardship)**

Ici, le LLM ne connaît **pas** la structure des tables au départ. Lorsqu'il reçoit une question, il doit d'abord consulter un **Catalogue de Données** (Métadonnées) pour "comprendre" où chercher l'information.

**Pourquoi est-ce indispensable ?**
* Les données techniques sont souvent obscures (`revenue_mil`).
* Le métier utilise des termes fonctionnels ("Succès financier").
* Le catalogue dicte au LLM la règle métier officielle pour joindre ces deux mondes et l'empêche d'inventer des critères arbitraires.

**Processus de l'Agent de Gouvernance :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question Métier", shape=ellipse];
            CatG [label="Catalogue Global\\n(Exploration des Domaines)", style=filled, color=orange];
            CatD [label="Catalogue Détaillé\\n(Règles et Mappings)", style=filled, color=palegreen];
            SQL [label="Génération SQL Finale", style=filled, color=lightblue];
            
            Q -> CatG -> CatD -> SQL;
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**C02a : Peupler le Catalogue de Métadonnées**")
        if st.button("Initialiser le Catalogue (SQLite)", use_container_width=True):
            with st.spinner("Installation des références métiers..."):
                try:
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    result = subprocess.run(
                        [sys.executable, "C02a_setup_catalog.py"],
                        capture_output=True, text=True, cwd=root_dir, timeout=30
                    )
                    if result.returncode == 0:
                        st.success("Tables Catalogue de Gouvernance créées avec succès !")
                    else:
                        st.error("Erreur d'initialisation.")
                        st.code(result.stderr)
                except Exception as e:
                    st.error(f"Erreur : {e}")
    with col2:
        st.info("**C02b : Tester l'Intérogation par Catalogue**")
        st.markdown('''
        *Questions complexes gérées par le catalogue :*
        1. "Quels sont nos plus grands succès financiers ?" (Mapping "Succès" -> "Box Office")
        2. "Classe les héros par endurance."
        ''')

    st.divider()

    if "c02_process" not in st.session_state:
        st.session_state.c02_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Agent de Gouvernance", type="primary", use_container_width=True) and st.session_state.c02_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de C02b_streamlit_catalog.py en arrière-plan...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "C02b_streamlit_catalog.py", "--server.port", "8506", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.c02_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.c02_process is not None:
            print("[Demo_Cockpit] Arrêt de C02b_streamlit_catalog.py...")
            st.session_state.c02_process.terminate()
            st.session_state.c02_process = None
            st.rerun()

    if st.session_state.c02_process is not None:
        st.success("Application C02b en cours d'exécution sur le port 8506.")
        st.components.v1.iframe("http://localhost:8506", height=750, scrolling=True)
    else:
        st.warning("L'Agent est actuellement arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Ce code prouve que le LLM n'attaque pas la base directement. Il agit comme un \"Data Steward\" en deux phases distinctes construites par le code :")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_c02b = os.path.join(root_dir, "C02b_streamlit_catalog.py")
        
        with open(file_path_c02b, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("Étape 1 : Le LLM isole la Table via le Catalogue Global")
        snippet1 = "".join(lines[54:60])
        st.code(snippet1, language="python")

        st.subheader("Étape 2 : Le LLM construit sa requête via le Catalogue Détaillé (Lexique)")
        snippet2 = "".join(lines[82:91])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Le fichier C02b_streamlit_catalog.py est introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : La Couche Sémantique**

Les architectures modernes de données (Lakehouse, Data Mesh) reposent lourdement sur cette étape.
Les LLM sont désormais branchés sur des outils de Data Catalog du marché (ex: *Collibra, Alation, Microsoft Purview*).

Ainsi, quand un directeur commercial demande *"Fais-moi le top 10 des produits ayant généré le plus de churn le mois dernier"*, le LLM :
1. Cherche la définition officielle (gouvernée par l'entreprise) du mot "Churn" dans Collibra.
2. Comprend grâce au catalogue qu'il faut filtrer la colonne technique `status_id = 99` de la base Snowflake de Ventes.
3. Génère la requête SQL infaillible.

**C'est cette couche de métadonnées sémantiques qui transforme un gadget d'IA en outil décisionnel robuste.**
    
</div>
""", unsafe_allow_html=True)
