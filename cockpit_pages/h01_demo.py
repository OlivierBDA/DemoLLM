import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape H01 : Monitoring et Traces (Arize Phoenix)")

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
**Concept : Observabilité des LLM (LLMOps)**

Lorsque nous utilisons des agents ou passons des requêtes complexes aux LLMs, il est indispensable de comprendre ce qu'il se passe "sous le capot" :
* Combien de tokens ont été consommés ?
* Quelle était la latence d'une étape de l'agent ?
* Quel est l'historique complet (et le prompt injecté) avant l'appel à l'API ?

**Arize Phoenix** est un outil de monitoring open-source. En instrumentant notre code (avec un simple `LangChainInstrumentor().instrument()`), toutes les traces sont envoyées à un serveur d'observation.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            Chat [label="Application Chat", style=filled, color=lightblue];
            LLM [label="Modèle IA", style=filled, color=orange];
            Phoenix [label="Phoenix Dashboard\\n(Port 6006)", style=filled, color=palegreen];
            
            User -> Chat;
            Chat -> LLM [label="Requête"];
            Chat -> Phoenix [label="Envoie les Traces\\n(OpenTelemetry)", style="dashed"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.info("Ici, nous allons démarrer deux services : le serveur Phoenix pour la collecte des traces, et l'application Chat.")
    
    if "phoenix_server_process" not in st.session_state:
        st.session_state.phoenix_server_process = None
    if "phoenix_chat_process" not in st.session_state:
        st.session_state.phoenix_chat_process = None

    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        if st.button("▶️ Démarrer Serveur Phoenix", type="primary", use_container_width=True) and st.session_state.phoenix_server_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de H00_phoenix_server.py dans un terminal externe...")
            try:
                subprocess.Popen(f'start cmd /k ""{sys.executable}" H00_phoenix_server.py"', shell=True, cwd=root_dir)
                st.session_state.phoenix_server_process = "EXTERNAL_TERMINAL_RUNNING"
                
                # Ouverture dans un nouvel onglet Chrome/Navigateur
                import webbrowser
                webbrowser.open_new_tab("http://localhost:6006")
                
                time.sleep(3) # Un peu de temps pour assurer le lancement du serveur avant reload
                st.rerun()
            except Exception as e:
                st.error(f"Impossible de lancer le terminal : {e}")
            
    with col_btn2:
        if st.button("▶️ Démarrer App Chat", type="primary", use_container_width=True) and st.session_state.phoenix_chat_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de H01_phoenix_chat.py sur le port 8507...")
            
            # Forcer l'encodage UTF-8 pour éviter le crash `UnicodeEncodeError` (Emojis sous Windows DEVNULL)
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "H01_phoenix_chat.py", "--server.port", "8507", "--server.headless", "true"],
                cwd=root_dir, env=env
            )
            st.session_state.phoenix_chat_process = process
            time.sleep(3)
            st.rerun()
            
    with col_btn3:
        if st.button("⏹️ Tout Arrêter", use_container_width=True):
            if st.session_state.phoenix_server_process is not None:
                if st.session_state.phoenix_server_process != "EXTERNAL_TERMINAL_RUNNING":
                    st.session_state.phoenix_server_process.terminate()
                else:
                    st.info("⚠️ Le serveur Phoenix s'est lancé dans un terminal externe, merci de le fermer manuellement.")
                st.session_state.phoenix_server_process = None
            if st.session_state.phoenix_chat_process is not None:
                st.session_state.phoenix_chat_process.terminate()
                st.session_state.phoenix_chat_process = None
            st.rerun()

    st.divider()

    # Affichage de l'iframe Chat en mode plein écran
    if st.session_state.phoenix_chat_process is not None:
        st.subheader("💬 Chat")
        if st.session_state.phoenix_server_process is None:
            st.warning("⚠️ Le serveur Phoenix n'a pas été démarré. Les traces ne seront pas collectées.")
            
        st.components.v1.iframe("http://localhost:8507", height=800, scrolling=True)
    else:
        if st.session_state.phoenix_server_process is not None:
            st.info("✔️ Le serveur Phoenix est lancé en tâche de fond (disponible dans le nouvel onglet). Cliquez sur 'Démarrer App Chat' pour ouvrir l'interface.")
        else:
            st.info("💡 Démarrez le Serveur puis le Chat pour afficher l'interface.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Voici les trois lignes magiques permettant d'instrumenter n'importe quel code LangChain :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "H01_phoenix_chat.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.code("".join(lines[18:21]), language="python") # Ajustement aux lignes
        st.write("Toutes les invocations suivantes du LLM seront tracées.")
        
    except FileNotFoundError:
        st.error("Le fichier H01_phoenix_chat.py est introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : LLMOps et MLOps**

Dans un Système d'Information d'entreprise, une application IA ne peut pas être déployée sans supervision (LLMOps). 
* **Débogage de l'Agent :** Un agent LLM peut faire des boucles infinies ou halluciner à cause d'un mauvais outil. Les traces permettent de voir exactement ce qui a été demandé et retourné à chaque étape.
* **Maîtrise des Coûts :** Les traces agrègent le nombre de tokens utilisés (Prompt + Completion).
* **Sécurité & Conformité :** Prouver a posteriori quelles données ont été injectées dans le prompt envoyé au fournisseur cloud.

Des outils équivalents dans l'écosystème entreprise incluent *LangSmith*, *Datadog LLM Observability*, *Dynatrace*, etc.
    
</div>
""", unsafe_allow_html=True)
