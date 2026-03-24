import streamlit as st
import subprocess
import os
import sys
import time
import re

st.title("Étape G03 : Chaîne complète A2A (3 Agents)")

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
**Objectif : Démontrer un enchaînement complet (Agent-to-Agent Chaining) où un sous-agent en appelle un autre avant de répondre à l'Orchestrateur.**

1. **L'Orchestrateur (Nick Fury)** : Analyse la demande de l'utilisateur. S'il détecte une menace, il délègue l'intervention à l'équipe **Avengers** via le standard A2A (`HTTP POST`).
2. **L'Agent Tactique (Avengers)** : Reçoit l'ordre formel. Avant d'intervenir, il a besoin du dossier de la cible. Il devient donc lui-même **client A2A** et sollicite l'**Info Center**.
3. **L'Agent Expert (Info Center)** : Reçoit la requête, lit le dossier textuel (`vilain_XXX.txt`) en RAG local, le synthétise et renvoie le rapport au demandeur (les Avengers).
4. **L'Agent Tactique (Avengers) [Suite]** : Reçoit le rapport, l'analyse avec son propre LLM pour générer une simulation de combat tactique épique, puis renvoie ce rapport d'intervention finalisé à Nick Fury.
5. **Conclusion** : Nick Fury réceptionne cet inject final et formule sa réponse humanisée et rassurante à l'utilisateur.
''')

    st.subheader("Architecture G03 : Chaining A2A")
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, style=filled, fillcolor=lightgrey, fontname="Helvetica", penwidth=2];
            edge [fontname="Helvetica", fontsize=10];
            
            U [label="Utilisateur", shape=ellipse, fillcolor=lightblue];
            Orch [label="Orchestrateur\\n(Nick Fury)", fillcolor="#4a4a4a", fontcolor=white];
            
            subgraph cluster_agents {
                label="Réseau A2A Interne";
                style=dashed;
                color=grey;
                A_AV [label="Agent Tactique\\nAvengers\\n(Port 8081)", fillcolor="#ffcccc"];
                A_IC [label="Agent Expert\\nInfo Center\\n(Port 8082)", fillcolor="#ccffcc"];
            }
            
            DB [label="Fichiers Locaux\\n(vilains_XXX.txt)", shape=cylinder, fillcolor=orange];
            
            U -> Orch [label=" 1. 'On nous attaque !'"];
            Orch -> A_AV [label=" 2. Tool Call\\n(POST JSON-RPC)", color=blue, fontcolor=blue];
            A_AV -> A_IC [label=" 3. Demande de\\nRenseignement\\n(POST JSON-RPC)", color=blue];
            A_IC -> DB [label=" 4. Lecture Fiche"];
            DB -> A_IC [label=" 5. Contenu"];
            A_IC -> A_AV [label=" 6. Rapport Synthétisé", color=green, fontcolor=green];
            A_AV -> Orch [label=" 7. Rapport Combat", color=green, fontcolor=green, style=bold];
            Orch -> U [label=" 8. Réponse Réconfortante"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Pré-requis de la démo :**
Les DEUX serveurs (`Avengers` et `Info Center`) doivent être en ligne. 
Lancez-les via les boutons ci-dessous s'ils ne tournent pas déjà dans vos terminaux.
''')

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 Lancer Serveur Info Center (Port 8082)", use_container_width=True):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(['cmd.exe', '/c', 'start', 'run_G01b_infocenter.bat'], cwd=root_dir)
            st.toast("Terminal Info Center lancé !", icon="🧠")
            
    with col_btn2:
        if st.button("🚀 Lancer Serveur Avengers (Port 8081)", use_container_width=True):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(['cmd.exe', '/c', 'start', 'run_G01a_avengers.bat'], cwd=root_dir)
            st.toast("Terminal Avengers lancé !", icon="⚡")

    st.markdown("---")

    # Gestion du processus en tâche de fond via session_state
    if "g03_process" not in st.session_state:
        st.session_state.g03_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer la Chaîne Nick Fury", type="primary", use_container_width=True):
            if st.session_state.g03_process is None:
                with st.spinner("Démarrage de l'interface Terminal Nick Fury sur le port 8511..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App G03 en tâche de fond sur le port 8511...")
                    
                    # Lancement asynchrone (Popen)
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "G03_streamlit_chain.py", "--server.port", "8511", "--server.headless", "true"],
                        cwd=root_dir,
                    )
                    st.session_state.g03_process = process
                    time.sleep(3) # Attente que le serveur soit prêt
                    st.rerun()
            else:
                st.info("L'application chat est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter la Chaîne Nick Fury", use_container_width=True):
            if st.session_state.g03_process is not None:
                st.session_state.g03_process.terminate()
                st.session_state.g03_process = None
                print(f"[Demo_Cockpit] Arret de l'App G03\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    # Affichage de l'Iframe si le processus tourne
    st.markdown("---")
    if st.session_state.g03_process is not None:
        st.write("🔴 **Terminal Nick Fury en direct :**")
        st.components.v1.iframe("http://localhost:8511", height=700, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer la Chaîne' pour afficher l'interface principale.")

with tab_code:
    st.header("Aperçu du Code Source")
    
    st.subheader("1. L'Agent Avengers (Client & Serveur)")
    st.write("Il est un serveur A2A pour Nick Fury, et un client A2A pour requêter l'Info Center en plein milieu de son traitement.")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_py = os.path.join(root_dir, "a2a_agents_avengers", "avengers", "agent.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            content = f.read()
        st.code(content, language="python")
    except FileNotFoundError:
        st.error("Fichier agent.py Avengers introuvable.")

    st.subheader("2. L'Orchestrateur (G03_streamlit_chain.py)")
    st.write("Le chef d'orchestre attend que la cascade A2A redescende jusqu'à lui.")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_py = os.path.join(root_dir, "G03_streamlit_chain.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r"(@tool\ndef ask_avengers.*?)(?=\nclass NickFuryOrchestrator:)", content, re.DOTALL)
            if match:
                st.code(match.group(1), language="python")
            else:
                st.code(content, language="python")
    except FileNotFoundError:
        st.error("Fichier G03 introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.info('''
**Parallèle Entreprise : Multi-Agent Supply Chain**

Ce modèle "Chained Agents" est le Saint Graal des systèmes autonomes en entreprise :
*   **Orchestration Complexe** : L'Agent Support Utilisateur (Niveau 1) est contacté car un client signale un débit frauduleux.
*   **Délégation Analytique** : Le Support contacte l'Agent Anti-Fraude (Niveau 2).
*   **Investigation Technique** : L'Anti-Fraude contacte l'Agent Base de Données (Niveau 3) pour analyser les IP et les logs.
*   **Résolution** : Le Niveau 3 remonte les preuves, le Niveau 2 bloque la transaction, et le Niveau 1 annonce au client que la situation est sous contrôle.

L'utilisateur final n'a interagi qu'avec *un seul point d'entrée*, mais l'entreprise a mobilisé 3 intelligences artificielles distinctes et spécialisées via des canaux sécurisés M2M.
''')
