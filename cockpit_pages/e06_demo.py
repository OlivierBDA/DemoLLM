import streamlit as st
import os
import subprocess
import time

st.title("Étape E06 : Notifications (Server-to-Client)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Comprendre l'enjeu : L'Événementiel (Event-Driven)")
    st.markdown("""
    **Le Concept : Le Serveur prend l'initiative**
    Jusqu'ici, le client devait demander (Discovery) "Quelles sont tes ressources ?".
    Mais que se passe-t-il si une ressource est ajoutée ou modifiée sur le serveur *après* la connexion ? C'est le rôle des **Notifications**.
    
    Le serveur dit : *"Attention, ma liste de ressources a changé, mets-toi à jour !"*
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Admin [label="Administrateur"];
            Server [label="Serveur MCP"];
            Client [label="Client HTML"];
            
            Server -> Client [label="1. Connexion SSE établie", style=dotted];
            Admin -> Server [label="2. Ajoute 'Enemies'"];
            Server -> Client [label="3. 🔔 Notification\\nResourceListChanged", color=red, penwidth=2];
            Client -> Server [label="4. list_resources()"];
            Server -> Client [label="5. Nouveau catalogue"];
            Client -> Client [label="6. Met à jour l'UI"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.warning("Cette démonstration utilise des fenêtres de terminal externes car l'écoute asynchrone est plus visible.")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("**1. Serveur Central (E06a)**")
        st.markdown("Héberge le catalogue.")
        if st.button("🚀 Serveur E06a", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(f'start cmd /k "{os.path.join(root_dir, "run_E06a.bat")}"', shell=True, cwd=root_dir)
            st.success("Serveur lancé sur le port 8004 !")
            
    with col2:
        st.info("**2. Client Écouteur (E06b)**")
        st.markdown("Reçoit les notifications et met à jour `E06_viewer.html`.")
        if st.button("▶️ Lancer Client E06b", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(f'start cmd /k "{os.path.join(root_dir, "run_E06b_client.bat")}"', shell=True, cwd=root_dir)
            st.success("Client en écoute !")
            
    with col3:
        st.info("**3. Panneau Admin (E06c)**")
        st.markdown("Permet d'ajouter une ressource (déclenche la notification).")
        if st.button("🛡️ Lancer Admin E06c", type="primary"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            subprocess.Popen(f'start cmd /k "{os.path.join(root_dir, "run_E06c_admin.bat")}"', shell=True, cwd=root_dir)
            st.success("Admin prêt !")

    st.divider()
    st.subheader("Résultat en temps réel (E06_viewer.html)")
    st.markdown("Cette vue (un simple fichier HTML généré par E06b) se mettra à jour automatiquement dès que le serveur enverra la notification.")

    # Affichage de l'iframe pointant vers le fichier local ou lecture du fichier
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    html_file = os.path.join(root_dir, "E06_viewer.html")
    
    # On utilise un iframe Base64 ou la balise HTML pour que ça s'affiche proprement et refresh
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            html_data = f.read()
        st.components.v1.html(html_data, height=400, scrolling=True)
        
        # Astuce technique pour forcer le rafraîchissement côté Streamlit si on le souhaite
        if st.button("Rafraîchir manuellement la vue"):
            st.rerun()
    else:
        st.warning("Le fichier `E06_viewer.html` n'a pas encore été généré par le Client E06b.")

with tab_code:
    st.header("Aperçu du Code Source (Client)")
    st.write("Le client MCP gère un écouteur asynchrone qui intercepte l'événement envoyé par le serveur.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path_e06b = os.path.join(root_dir, "E06b_mcp_client_html.py")
        
        with open(file_path_e06b, "r", encoding="utf-8") as f:
            lines = f.readlines()
            
        snippet = "".join(lines[100:106])
        st.code(snippet, language="python")
    except FileNotFoundError:
        st.error("Fichier introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.success('''
**Parallèle Entreprise : L'Intranet "Vivant"**

Un contexte très classique : L'utilisateur utilise un Agent IA connecté à Confluence. 
Pendant qu'il discute avec l'Agent, un collègue met à jour la page Confluence sur les règles de congés payés.

Sans notification : L'Agent continue de s'appuyer sur l'ancienne version cachée en mémoire (Risque d'hallucination ou de fausse information).
Avec MCP Notifications : Le serveur Confluence envoie un ping à l'Agent `ResourceListChanged`. L'Agent rafraîchit son contexte de lui-même et utilise instantanément la nouvelle règle, le tout en plein milieu de la conversation.
    ''')
