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
                        [sys.executable, "-m", "streamlit", "run", "G02_streamlit_a2a.py", "--server.port", "8510", "--server.headless", "true"],
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
    st.header("Aperçu du Code Source (Points Clés)")
    
    st.subheader("1. L'Orchestrateur (Nick Fury) appelle l'Agent via A2A")
    st.write("Nick Fury utilise le Tool Calling LangChain pour déclencher une requête HTTP structurée au format **JSON-RPC 2.0**, le standard du protocole A2A.")
    st.code('''
@tool
def ask_info_center(hero_name: str) -> str:
    url = "http://localhost:8082/a2a/info_center"
    
    # Payload standard A2A (JSON-RPC)
    payload = {
        "jsonrpc": "2.0",
        "id": "uuid-requete",
        "method": "message/send",
        "params": {
            "message": {
                "messageId": "uuid-message",
                "role": "user",
                "parts": [{"kind": "text", "text": hero_name}]
            }
        }
    }
    
    # Appel transparent pour l'orchestrateur
    response = requests.post(url, json=payload)
    return extraire_texte_a2a(response.json())
''', language="python")

    st.subheader("2. L'Agent Expert intercepte la demande")
    st.write("Grâce au framework ADK, l'agent spécialisé intercepte la requête entrante avec un `callback`, effectue son traitement métier (RAG local), et court-circuite le llm par défaut.")
    st.code('''
def process_info_request(callback_context):
    # 1. Extraction de la demande
    user_text = callback_context.user_content.parts[0].text
    
    # 2. Traitement Métier Interne (RAG)
    fichier = lire_fichier_local(user_text)
    rapport = llm.invoke(f"Fais un rapport strict : {fichier}").content
    
    # 3. Renvoi direct dans le flux A2A (bypass du modèle standard)
    return types.Content(role="model", parts=[types.Part(text=rapport)])

# Déclaration de l'agent A2A
root_agent = Agent(
    name="SHIELD_InfoCenter",
    before_agent_callback=process_info_request
)
''', language="python")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : Architecture en Essaim (Swarm Architecture)**

Dans un Système d'Information moderne :
*   **Séparation des Rôles (SoC)** : Le Chatbot "Orchestrateur" qui interagit avec l'utilisateur RH n'a pas accès à la base de données comptables. 
*   **API Agnostique** : L'orchestrateur demande au sous-agent de comptabilité via le standard interne (A2A JSON-RPC ici, ou gRPC dans la vraie vie) de chercher les informations.
*   **Abstraction des sources** : L'orchestrateur se fiche de savoir si le sous-agent a lu un fichier TXT (comme ici), fait une requête SQL ou appelé Kafka. Il ne voit qu'une réponse standardisée "Rapport généré".
*   **Sécurité et RBAC** : Ce mécanisme permet de sécuriser chaque Agent avec ses propres habilitations.

</div>
""", unsafe_allow_html=True)
