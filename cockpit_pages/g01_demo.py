import streamlit as st
import subprocess
import os
import sys
import time

st.title("Étape G01 : Découverte A2A (Discovery)")

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
**Objectif : Démontrer comment des Agents IA déclarent leur identité et leurs capacités via le protocole A2A (Agent-To-Agent) de Google, permettant à un orchestrateur de les découvrir de manière standardisée.**

Le protocole **A2A** définit des standards pour la communication entre agents. Avant de pouvoir échanger des requêtes ou des tâches, un agent a besoin de savoir à qui il s'adresse.

**Le Manifeste (AgentCard) :**
Chaque agent compatible A2A expose une **"Card"**. C'est sa carte d'identité numérique au format JSON, accessible via une requête HTTP GET standard (souvent à la racine `/` ou `/card`). Elle contient :
*   Le nom de l'agent.
*   Une description de ses capacités (crucial pour le routage de l'orchestrateur).
*   L'auteur et la version.

**Fonctionnement de la démo :**
1. Deux serveurs Agents (Avengers et Info Center) tournent en tâche de fond sur des ports séparés (`8081` et `8082`), utilisant l'ADK Google (`google-adk`).
2. Le terminal (l'interface Streamlit ci-dessous) joue le rôle de l'Orchestrateur (Nick Fury).
3. Au clic sur "Discovery", le terminal interroge les ports pour demander leurs `AgentCard`.
4. Le JSON brut est récupéré, validant le protocole A2A.
5. L'interface affiche ces données sous forme compréhensible.
''')

    st.info("💡 L'intérêt majeur est l'interopérabilité : l'orchestrateur n'a pas besoin de connaître l'Agent A à l'avance. Il interroge les ressources du réseau, lit les descriptions, et comprend dynamiquement qui sait faire quoi.")

    st.subheader("Architecture de Découverte")
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, style=filled, fillcolor=lightgrey, fontname="Helvetica", penwidth=2];
            edge [fontname="Helvetica", fontsize=10];
            
            Orch [label="Orchestrateur\\n(Terminal Nick Fury)", fillcolor="#4a4a4a", fontcolor=white];
            
            subgraph cluster_agents {
                label="Réseau A2A";
                style=dashed;
                color=grey;
                A_Av [label="Agent A2A\\nAvengers\\n(Port 8081)", fillcolor="#ffcccc"];
                A_IC [label="Agent A2A\\nInfo Center\\n(Port 8082)", fillcolor="#ccffcc"];
            }
            
            Orch -> A_Av [label=" 1. Discovery\\nGET /.well-known/agent-card.json", color=blue, fontcolor=blue];
            A_Av -> Orch [label=" 2. AgentCard (JSON)", color=green, fontcolor=green, style=bold];
            
            Orch -> A_IC [label=" 1. Discovery\\nGET /.well-known/agent-card.json", color=blue, fontcolor=blue];
            A_IC -> Orch [label=" 2. AgentCard (JSON)", color=green, fontcolor=green, style=bold];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Pré-requis de la démo :**
Les serveurs Agents (Avengers et Info Center) doivent être en ligne. Tu peux les lancer ci-dessous ou manuellement.
''')

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🚀 Lancer Serveur Avengers (Port 8081)", use_container_width=True):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(['cmd.exe', '/c', 'start', 'run_G01a_avengers.bat'], cwd=root_dir)
            st.toast("Terminal Avengers lancé !", icon="🦸‍♂️")
    with col_btn2:
        if st.button("🚀 Lancer Serveur Info Center (Port 8082)", use_container_width=True):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(['cmd.exe', '/c', 'start', 'run_G01b_infocenter.bat'], cwd=root_dir)
            st.toast("Terminal Info Center lancé !", icon="🧠")
            
    st.markdown("---")

    # Gestion du processus en tâche de fond via session_state
    if "g01_process" not in st.session_state:
        st.session_state.g01_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer l'App G01", type="primary", use_container_width=True):
            if st.session_state.g01_process is None:
                with st.spinner("Démarrage de l'interface Terminal Discovery sur le port 8509..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App G01 en tâche de fond sur le port 8509...")
                    
                    # Lancement asynchrone (Popen)
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "G01c_streamlit_discovery.py", "--server.port", "8509", "--server.headless", "true"],
                        cwd=root_dir,
                    )
                    st.session_state.g01_process = process
                    time.sleep(3) # Attente que le serveur soit prêt
                    st.rerun()
            else:
                st.info("L'application est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter l'App G01", use_container_width=True):
            if st.session_state.g01_process is not None:
                st.session_state.g01_process.terminate()
                st.session_state.g01_process = None
                print(f"[Demo_Cockpit] Arret de l'App G01\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    # Affichage de l'Iframe si le processus tourne
    st.markdown("---")
    if st.session_state.g01_process is not None:
        st.write("🔴 **Terminal Discovery en direct :**")
        st.components.v1.iframe("http://localhost:8509", height=600, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer l'App G01' pour afficher le terminal Nick Fury.")

with tab_code:
    st.header("Aperçu du Code Source")
    
    st.subheader("1. Code Serveur A2A (Agent Avengers)")
    st.write("Le framework ADK simplifie drastiquement la création de l'agent. Le manifeste est déclaré directement dans le constructeur :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_py = os.path.join(root_dir, "G01a_a2a_server_avengers.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        st.code(content, language="python")

    except FileNotFoundError:
        st.error("Fichier G01a_a2a_server_avengers.py introuvable.")
        
    st.subheader("2. Le Manifeste A2A (L'AgentCard Avengers)")
    st.write("Le fichier `agent.json` est le cœur de l'identité de l'agent. Il est lu nativement par le serveur ADK pour l'exposition A2A :")
    try:
        file_path_json = os.path.join(root_dir, "a2a_agents_avengers", "avengers", "agent.json")
        with open(file_path_json, "r", encoding="utf-8") as f:
            content_json = f.read()
        st.code(content_json, language="json")
    except FileNotFoundError:
        st.error("Fichier agent.json des avengers introuvable.")

    st.subheader("3. Code de Découverte (Terminal Nick Fury)")
    st.write("Le terminal découvre ces agents dynamiquement en effectuant de simples requêtes HTTP GET sur la route A2A standard :")
    st.code('''
# Fonction d'interrogation de l'AgentCard d'un A2A Agent
def fetch_agent_card(app_name, port):
    # La spec A2A impose l'accès à /.well-known/agent-card.json
    url = f"http://localhost:{port}/a2a/{app_name}/.well-known/agent-card.json"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # L'AgentCard est retournée !
    ''', language="python")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.info('''
**Parallèle Entreprise :**

Dans un SI moderne et industrialisé (par exemple autour d'une plateforme GCP et de Vertex AI) :
*   **Micro-services Multi-Agents** : Au lieu d'avoir un "God Agent" monolithique, l'entreprise crée de multiples petits agents spécialisés (Agent RH Congés, Agent Support IT, Agent Finance Facturation).
*   **Le Manifeste comme Contrat** : Chaque agent publie sa "Card" précisant ses inputs, ses outputs, et sa description sémantique.
*   **Orchestration Dynamique** : L'agent "Hub" (ou le orchestrateur principal d'accueil utilisateur) va découvrir dynamiquement ces agents. Si un nouveau service est ajouté, il est immédiatement détecté et utilisable par l'orchestrateur sans redéploiement global.
''')
