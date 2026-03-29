import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E05 : Suivi de Progression (Progress Tracking)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Pourquoi le Progress Tracking est-il crucial ?")
    st.markdown("""
    **Le Problème : L'Effet "Tunnel"**
    Dans un appel API HTTP classique, l'interface se fige en attendant la réponse. L'utilisateur (ou l'IA) ne sait pas si ça plante ou si ça calcule.
    
    **La Solution MCP : La Notification "Out-of-Band"**
    Le serveur envoie des messages asynchrones `notifications/progress` *pendant* l'exécution du service.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Client [label="Frontend (Streamlit)"];
            Server [label="Serveur MCP"];
            
            Client -> Server [label="1. call_tool(progToken='TX1')"];
            Server -> Client [label="2. [Prog] Round 1 (TX1)", style=dashed, color=blue];
            Server -> Client [label="3. Resultat Final", color=green, penwidth=2];
        }
    ''')
    st.info("💡 Utile pour le chargement de données, les analyses RAG complexes ou toute tâche dépassant 2 secondes.")

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**E05a : Serveur de Combat Progressif**")
        st.markdown("Ce serveur prend son temps (5 secondes intentionnelles) pour simuler et notifier chaque étape.")
        if st.button("🚀 Démarrer Serveur Progress (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E05a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur E05a lancé sur le port 8003 !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**E05b : Client avec Barre de Progression**")
        st.markdown("Lancez un combat et observez que l'UI ne gèle pas ; elle vous parle en temps réel.")

    st.divider()

    if "e05_process" not in st.session_state:
        st.session_state.e05_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer Client Progressif (E05b)", use_container_width=True) and st.session_state.e05_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E05b_streamlit_mcp_progress.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E05b_streamlit_mcp_progress.py", "--server.port", "8513", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e05_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e05_process is not None:
            print("[Demo_Cockpit] Arrêt de E05b_streamlit_mcp_progress.py...")
            st.session_state.e05_process.terminate()
            st.session_state.e05_process = None
            st.rerun()

    if st.session_state.e05_process is not None:
        st.success("Application E05b en cours d'exécution sur le port 8513.")
        st.components.v1.iframe("http://localhost:8513", height=800, scrolling=True)
    else:
        st.warning("Client arrêté.")

with tab_code:
    st.header("Aperçu du Code Source (Serveur)")
    st.write("Le serveur gère le `meta.progressToken` envoyé par la requête.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e05s = os.path.join(root_dir, "E05a_mcp_server_progress.py")
        
        with open(file_path_e05s, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        snippet = "".join(lines[41:51])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : L'Expérience Utilisateur des Agents (UX)**

Les agents IA sont souvent lents car ils font beaucoup de requêtes réseau (RAG, Web Search, API métier). 
Si l'Agent dit "Je cherche sur SAP..." et qu'il ne se passe rien pendant 15 secondes, l'utilisateur ferme la page en pensant que le système est planté.

Avec MCP Progress :
`0s` : "Je cherche sur SAP..." (Progress = 10%)
`3s` : "J'ai trouvé la facture, analyse en cours..." (Progress = 50%)
`8s` : "Extraction des lignes tarifaires..." (Progress = 80%)
`12s` : Affichage de la réponse.

C'est ce niveau de feedback qui transforme un "gadget" anxiogène en un outil professionnel fiable aux yeux des collaborateurs.
    
</div>
""", unsafe_allow_html=True)
