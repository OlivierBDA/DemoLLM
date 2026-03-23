import streamlit as st
import subprocess
import os
import sys
import time

st.title("Étape G02 : Chat Inter-Agents A2A")

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
**Objectif : Démontrer une conversation et une délégation de tâche transparentes entre un Orchestrateur et un sous-agent expert via le protocole A2A et un environnement RAG local.**

1. **L'Orchestrateur (Nick Fury)** : Analyse la demande de l'utilisateur. S'il détecte que la demande concerne un dossier super-héros précis, il ne perd pas de temps à halluciner. Il délègue immédiatement la demande via un appel d'outil (Tool Calling) au standard A2A (`HTTP POST`).
2. **L'Agent Expert (Info Center)** : Il n'a pas d'interface utilisateur Web. Il reçoit la requête raw au format JSON-RPC. Son moteur d'intelligence artificielle interne (LLM de traitement) l'analyse, puis va lire le fichier de renseignement local correspondant (`data/source_files/hero_XXX.txt`).
3. **La Synthèse et le Renvoi** : L'Agent Info Center synthétise le fichier de manière ultra-formelle (façon rapport SHIELD) et renvoie la chaîne via le réseau A2A.
4. **Conclusion** : Nick Fury réceptionne cet inject et formule sa réponse humanisée finale à l'utilisateur.
''')

    st.subheader("Architecture de Délégation")
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, style=filled, fillcolor=lightgrey, fontname="Helvetica", penwidth=2];
            edge [fontname="Helvetica", fontsize=10];
            
            U [label="Utilisateur", shape=ellipse, fillcolor=lightblue];
            Orch [label="Orchestrateur\\n(Nick Fury)", fillcolor="#4a4a4a", fontcolor=white];
            
            subgraph cluster_agents {
                label="Réseau A2A";
                style=dashed;
                color=grey;
                A_IC [label="Agent A2A\\nInfo Center\\n(Port 8082)", fillcolor="#ccffcc"];
            }
            
            DB [label="Fichiers Locaux\\n(RAG)", shape=cylinder, fillcolor=orange];
            
            U -> Orch [label=" 1. 'Infos sur Hulk ?'"];
            Orch -> A_IC [label=" 2. Tool Call\\n(POST JSON-RPC)", color=blue, fontcolor=blue];
            A_IC -> DB [label=" 3. Lecture hero_hulk.txt"];
            DB -> A_IC [label=" 4. Contenu Brut"];
            A_IC -> Orch [label=" 5. Rapport Synthétisé", color=green, fontcolor=green, style=bold];
            Orch -> U [label=" 6. Réponse Finale"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Pré-requis de la démo :**
Le serveur Agent Info Center doit être en ligne pour répondre aux appels de l'Orchestrateur. Tu peux le lancer ci-dessous ou manuellement via le terminal.
''')

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 Lancer Serveur Info Center (Port 8082)", use_container_width=True):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(['cmd.exe', '/c', 'start', 'run_G01b_infocenter.bat'], cwd=root_dir)
            st.toast("Terminal Info Center lancé !", icon="🧠")
            
    st.markdown("---")

    # Gestion du processus en tâche de fond via session_state
    if "g02_process" not in st.session_state:
        st.session_state.g02_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer le Chat Nick Fury", type="primary", use_container_width=True):
            if st.session_state.g02_process is None:
                with st.spinner("Démarrage de l'interface Terminal Nick Fury sur le port 8510..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App G02 en tâche de fond sur le port 8510...")
                    
                    # Lancement asynchrone (Popen)
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "G02c_streamlit_chat.py", "--server.port", "8510", "--server.headless", "true"],
                        cwd=root_dir,
                    )
                    st.session_state.g02_process = process
                    time.sleep(3) # Attente que le serveur soit prêt
                    st.rerun()
            else:
                st.info("L'application chat est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter le Chat Nick Fury", use_container_width=True):
            if st.session_state.g02_process is not None:
                st.session_state.g02_process.terminate()
                st.session_state.g02_process = None
                print(f"[Demo_Cockpit] Arret de l'App G02\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    # Affichage de l'Iframe si le processus tourne
    st.markdown("---")
    if st.session_state.g02_process is not None:
        st.write("🔴 **Terminal Nick Fury en direct :**")
        st.components.v1.iframe("http://localhost:8510", height=700, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer le Chat' pour afficher le terminal Nick Fury.")

with tab_code:
    st.header("Aperçu du Code Source")
    
    st.subheader("1. Intelligence de l'Info Center (agent.py)")
    st.write("L'Info Center intercepte la demande A2A avec un `before_agent_callback`, contacte son LLM, cherche le fichier texte (RAG) et rédige un rapport.")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_py = os.path.join(root_dir, "a2a_agents_infocenter", "info_center", "agent.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            content = f.read()
        st.code(content, language="python")
    except FileNotFoundError:
        st.error("Fichier agent.py introuvable.")

    st.subheader("2. Requête A2A de Nick Fury (G02c_streamlit_chat.py)")
    st.write("L'outil attaché à Nick Fury utilise un simple `requests.post` pour formater un payload standard JSON-RPC 2.0 (compatible Google ADK).")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_py = os.path.join(root_dir, "G02c_streamlit_chat.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            content = f.read()
            # Extract just the tool for clarity
            import re
            match = re.search(r"(@tool\ndef ask_info_center.*?)(?=\nclass NickFuryOrchestrator:)", content, re.DOTALL)
            if match:
                st.code(match.group(1), language="python")
            else:
                st.code(content, language="python")
    except FileNotFoundError:
        st.error("Fichier G02c_streamlit_chat.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.info('''
**Parallèle Entreprise : Architecture en Essaim (Swarm Architecture)**

Dans un Système d'Information moderne :
*   **Séparation des Rôles (SoC)** : Le Chatbot "Orchestrateur" qui interagit avec l'utilisateur RH n'a pas accès à la base de données comptables. 
*   **API Agnostique** : L'orchestrateur demande au sous-agent de comptabilité via le standard interne (A2A JSON-RPC ici, ou gRPC dans la vraie vie) de chercher les informations.
*   **Abstraction des sources** : L'orchestrateur se fiche de savoir si le sous-agent a lu un fichier TXT (comme ici), fait une requête SQL ou appelé Kafka. Il ne voit qu'une réponse standardisée "Rapport généré".
*   **Sécurité et RBAC** : Ce mécanisme permet de sécuriser chaque Agent avec ses propres habilitations.
''')
