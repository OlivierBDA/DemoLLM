import streamlit as st
import subprocess
import os
import sys
import time

st.title("Étape A03 : Streamlit Chat")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Concept et Explication")
    st.markdown('''
**Objectif : Créer une interface utilisateur conversationnelle moderne et persistante (Sortir du terminal).**

Cette étape introduit **Streamlit**, un framework qui permet de transformer des scripts Python en applications web interactives.

**Fonctionnement :**
*   **Mémoire (State) :** Streamlit garde l'historique des messages en mémoire le temps de la session utilisateur via `st.session_state`.
*   **Streaming :** Les réponses de l'IA s'affichent mot par mot, ce qui réduit considérablement la latence perçue par l'utilisateur (effet machine à écrire).
''')

    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            UI [label="Streamlit Chat", style=filled, color=lightblue];
            LLM [label="LLM (OpenAI/Gemini)", style=filled, color=orange];
            
            User -> UI [label="Question"];
            UI -> LLM [label="Historique + Prompt"];
            LLM -> UI [label="Réponse (Stream)"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Note d'architecture :** La démo ci-dessous est l'application d'origine exécutée en tâche de fond et incrustée ici. 
Elle tourne de manière totalement isolée sur le port `8502`.
''')

    # Gestion du processus en tâche de fond via session_state
    # Gestion du processus en tâche de fond via session_state
    if "a03_process" not in st.session_state:
        st.session_state.a03_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer l'App A03", type="primary", use_container_width=True):
            if st.session_state.a03_process is None:
                with st.spinner("Démarrage de l'application Streamlit sur le port 8502..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App A03 en tâche de fond sur le port 8502...")
                    
                    # Lancement asynchrone (Popen). On laisse stdout et stderr s'afficher directement
                    # dans le terminal père (celui qui a lancé Demo_Cockpit.py)
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "A03_streamlit_chat.py", "--server.port", "8502", "--server.headless", "true"],
                        cwd=root_dir,
                        # stdout et stderr héritent par défaut du processus parent
                    )
                    st.session_state.a03_process = process
                    time.sleep(3) # Attente que le serveur soit prêt
                    st.rerun()
            else:
                st.info("L'application est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter l'App A03", use_container_width=True):
            if st.session_state.a03_process is not None:
                st.session_state.a03_process.terminate()
                st.session_state.a03_process = None
                print(f"[Demo_Cockpit] Arret de l'App A03\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    # Affichage de l'Iframe si le processus tourne
    st.markdown("---")
    if st.session_state.a03_process is not None:
        st.write("🔴 **Application en direct :**")
        st.components.v1.iframe("http://localhost:8502", height=700, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer l'App A03' pour afficher l'interface de chat.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Voici les extraits clés qui gèrent l'historique et le streaming (lignes 36 à 47) :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "A03_streamlit_chat.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Gestion historique et stream
        st.markdown("**Gestion de l'historique et appel en streaming :**")
        snippet = "".join(lines[35:48])
        st.code(snippet, language="python")

    except FileNotFoundError:
        st.error("Fichier A03_streamlit_chat.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Des interfaces de ce type sont idéales pour :
* **Chatbots internes :** Assistance aux employés (RH, IT Support).
* **Copilotes Métier :** Un assistant qui accompagne un gestionnaire sur son application métier.

**À retenir :** 
L'historique est ici gardé en mémoire vive (`st.session_state`). Dans un "vrai" SI, afin de garantir la scalabilité (si l'utilisateur change de serveur) et la persistance (si le serveur redémarre), cet historique doit être stocké en base de données (ex: Redis ou PostgreSQL).

</div>
""", unsafe_allow_html=True)
