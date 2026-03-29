import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape D02 : Visualisations Dynamiques")

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
    **Concept : Visualisation "On-the-fly" & Multi-agents**
    Dans cette étape finale du cycle classique, l'agent ne se contente plus d'extraire des chiffres, il **propose** une visualisation adaptée à votre question, générant son propre tableau de bord.
    
    **Ce que fait la chaine LLM :**
    1. **Phase 1 (Agent SQL)** : Traduit votre question en requête métier (SQL) pour extraire le jeu de données depuis la base SQLite (`marvel_data.db`).
    2. **Phase 2 (Agent Data Viz)** : Analyse la question + les colonnes du tableau obtenu, et identifie si un graphique est pertinent (ex: comparer des forces, voir une évolution).
    3. **Action** : Le script Python lit la réponse JSON de la Phase 2 et configure automatiquement le composant Streamlit (`st.bar_chart`, `st.line_chart`, etc.).
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question", shape=ellipse];
            SQL [label="LLM (Phase 1: Agent SQL)", style=filled, color=orange];
            DB [label="SQLite DB", style=filled, color=palegreen];
            VIZ [label="LLM (Phase 2: Agent Viz)", style=filled, color=orange];
            Chart [label="Python Streamlit Chart", style=filled, color=lightblue];
            
            Q -> SQL;
            SQL -> DB [label="Requête SQL"];
            DB -> VIZ [label="Pandas DataFrame"];
            VIZ -> Chart [label="JSON Configuration"];
        }
    ''')
    st.image("https://img.icons8.com/fluency/96/combo-chart.png", width=50)

with tab_demo:
    st.header("Démonstration Technique")
    st.info("Cette étape requiert que la base de données `marvel_data.db` ait été créée lors de l'étape **C01a**.")
    
    st.markdown('''
        *Questions à tester :*
        1. "Compare la force et l'intelligence des héros dans un graphique à barres."
        2. "Montre le box-office des films par année sous forme de ligne d'évolution."
        3. "Quels sont nos héros les plus rapides ?"
    ''')

    st.divider()

    if "d02_process" not in st.session_state:
        st.session_state.d02_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'Agent Visualisation", use_container_width=True) and st.session_state.d02_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de D02_streamlit_charts.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "D02_streamlit_charts.py", "--server.port", "8508", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.d02_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.d02_process is not None:
            print("[Demo_Cockpit] Arrêt de D02_streamlit_charts.py...")
            st.session_state.d02_process.terminate()
            st.session_state.d02_process = None
            st.rerun()

    if st.session_state.d02_process is not None:
        st.success("Application D02 en cours d'exécution sur le port 8508.")
        st.components.v1.iframe("http://localhost:8508", height=800, scrolling=True)
    else:
        st.warning("L'Agent de visualisation est actuellement arrêté.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le secret de cette application est contraindre le LLM (lors de l'étape 2) à répondre **exclusivement au format JSON**, ce qui permet au code Python de le lire comme une configuration.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_d02 = os.path.join(root_dir, "D02_streamlit_charts.py")
        
        with open(file_path_d02, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("1. Le Prompt Data Viz (JSON Output)")
        snippet1 = "".join(lines[57:63])
        st.code(snippet1, language="python")

        st.subheader("2. Le Rendu Dynamique via Python")
        st.markdown("Côté interface, Streamlit lit ce JSON et appelle dynamiquement le bon composant visuel.")
        snippet2 = "".join(lines[188:195])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Le fichier D02_streamlit_charts.py est introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : L'Intelligence Décisionnelle (Executive Dashboards)**

Cette brique d'IA a la capacité de rendre la création de tableaux de bord PowerBI / Tableau obsolète pour les besoins ponctuels du quotidien.

**Cas Pratique au Comex :**
Au lieu de passer par le service IT Analytics pour créer un tableau de bord (Délai : 3 semaines) :
* Le Directeur Marketing demande à l'Agent : "Montre-moi l'évolution des ventes du produit Y en région PACA comparé à la Bretagne sur l'année dernière".
* L'IA :
  1. Trouve la bonne table de vente via son catalogue de gouvernance (Étape C02).
  2. Extrait les données avec une requête SQL (Étape C01).
  3. Formate automatiquement le graphique en courbe avec deux couleurs (Étape D02).
  4. L'affiche en 10 secondes sur l'ordinateur du directeur.

C'est là le véritable **"Graal" de l'Agentic Workspace** : transformer n'importe quel dirigeant en expert de la donnée temps réel.
    
</div>
""", unsafe_allow_html=True)
