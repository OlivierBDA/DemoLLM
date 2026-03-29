import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape E04 : Les Modèles de Ressources (Templates)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Pourquoi utiliser des Modèles (Templates) ?")
    st.markdown("""
    **L'Enjeu : Le passage à l'échelle (Scalability)**
    Lister 10 000 ou 1 million de fichiers individuellement lors de la phase de "Discovery" (E03) est lent et inefficace. 
    Le **Resource Template** permet de déclarer une règle d'accès générique.
    
    **Avantages :**
    1. **Économie de bande passante** : Le catalogue reste ultra-léger.
    2. **Flexibilité** : On accède à la donnée uniquement quand on en a le besoin ("Just-in-Time" ou "On-demand").
    3. **Standardisation** : L'URL devient une interface universelle entre l'IA et vos données de masse.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Client [label="Application Cliente"];
            Server [label="Serveur MCP"];
            Files [label="Base de données ou\\nDossier immense", style=dotted];
            
            Client -> Server [label="1. Liste les templates"];
            Server -> Client [label="2. 'mcp://marvel/heroes/{name}'"];
            Client -> Server [label="3. Je veux 'mcp://marvel/heroes/hulk'"];
            Server -> Files [label="4. Recherche de donnée ciblée"];
            Server -> Client [label="5. Envoi du texte brut"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**E04a : Lancer le Serveur Templates**")
        st.markdown("Ce serveur expose quelques fiches génériques, et surtout un connecteur via Template.")
        if st.button("🚀 Démarrer Serveur Templates (Terminal)", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_E04a.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.success("Serveur E04a lancé sur le port 8002 !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    with col2:
        st.info("**E04b : L'Explorateur Paramétré**")
        st.markdown("Naviguez dans les ressources statiques et utilisez les formulaires pour instancier des Modèles (ex: tapez 'thor' ou 'hulk').")

    st.divider()

    if "e04_process" not in st.session_state:
        st.session_state.e04_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer Explorateur Modèles (E04b)", use_container_width=True) and st.session_state.e04_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de E04b_streamlit_mcp_templates.py...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "E04b_streamlit_mcp_templates.py", "--server.port", "8512", "--server.headless", "true"],
                cwd=root_dir, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            st.session_state.e04_process = process
            time.sleep(3)
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.e04_process is not None:
            print("[Demo_Cockpit] Arrêt de E04b_streamlit_mcp_templates.py...")
            st.session_state.e04_process.terminate()
            st.session_state.e04_process = None
            st.rerun()

    if st.session_state.e04_process is not None:
        st.success("Application E04b en cours d'exécution sur le port 8512.")
        st.components.v1.iframe("http://localhost:8512", height=800, scrolling=True)
    else:
        st.warning("Client arrêté.")

with tab_code:
    st.header("Aperçu du Code Source (Serveur)")
    st.write("Ce qui est intéressant, c'est comment le serveur déclare un modèle (`@server.list_resource_templates()`) puis gère la lecture générique (`@server.read_resource()`).")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e04s = os.path.join(root_dir, "E04a_mcp_server_templates.py")
        
        with open(file_path_e04s, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        st.subheader("La déclaration du modèle")
        snippet1 = "".join(lines[36:44])
        st.code(snippet1, language="python")

        st.subheader("Le Parsage de la requête")
        snippet2 = "".join(lines[58:65])
        st.code(snippet2, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : Interfacer une Base de Données Monstrueuse**

Imaginez que vous ayez une base de données Cloud (Snowflake/BigQuery) avec des millions de fiches clients.
Au lieu de créer un outil fastidieux `search_client_by_id`, on expose un **Template MCP** :
`mcp://crm/clients/{client_id}`

Si le LLM "Agent Support Client" voit qu'un email indique `Client ID : 49581A`, il comprend qu'il peut instantanément requêter `mcp://crm/clients/49581A` pour obtenir la fiche complète avant même de commencer à rédiger sa réponse.

C'est extrêmement puissant pour l'intégration de gros volumes de données avec une latence quasi nulle en phase de découverte.
    
</div>
""", unsafe_allow_html=True)
