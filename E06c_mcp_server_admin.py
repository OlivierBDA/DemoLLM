import streamlit as st
import os
import httpx
import time

# Configuration
DATA_DIR = "data"
ENEMIES_FILE = os.path.join(DATA_DIR, "marvel_enemies.md")
SERVER_URL = "http://127.0.0.1:8004/admin/notify"

# ==============================================================================
# SECTION 1 : LOGIQUE ADMIN
# ==============================================================================

def main():
    st.set_page_config(page_title="MCP Admin", page_icon="🛠️")
    st.title("🛠️ E06 : Admin Console (Contrôleur)")
    st.markdown("Utilisez cette interface pour **simuler une mise à jour côté serveur** et déclencher une notification.")

    with st.expander("ℹ️ À propos de cette étape : Notifications Temps Réel (MCP)", expanded=False):
        st.markdown("""
        **Concept :**
        Le protocole MCP permet non seulement d'exposer des outils et des ressources, mais aussi de **notifier** les clients quand ces ressources changent.
        C'est essentiel pour garder les agents synchronisés avec un environnement mouvant.

        **Architecture de la démo :**
        1.  **Serveur MCP (E06a)** : Gère le catalogue.
        2.  **Client HTML (E06b)** : Écoute le serveur via SSE (Server-Sent Events) et met à jour une page Web (`E06_viewer.html`).
        3.  **Admin (E06c - Vous êtes ici)** : Agit comme un événement externe qui modifie les données et force le serveur à notifier ses clients.
        """)
        st.graphviz_chart('''
            digraph G {
                rankdir=LR;
                node [shape=box, fontname="Helvetica", fontsize=10];
                
                Admin [label="Admin (Streamlit)\\n(Modifie Data)", style=filled, color=lightcoral];
                Server [label="Serveur MCP\\n(Note changement)", style=filled, color=orange];
                Client [label="Client HTML\\n(Reçoit Notif)", style=filled, color=lightblue];
                Viewer [label="Navigateur Web\\n(Auto-refresh)", shape=ellipse, style=filled, color=lightgrey];
                
                Admin -> Server [label="POST /notify"];
                Server -> Client [label="SSE (ResourceListChanged)"];
                Client -> Server [label="list_resources()"];
                Client -> Viewer [label="Update HTML file"];
            }
        ''')
    
    # État du fichier
    file_exists = os.path.exists(ENEMIES_FILE)
    
    st.info(f"📁 **Fichier cible** : `{ENEMIES_FILE}`")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("État du Fichier", "✅ PRÉSENT" if file_exists else "❌ ABSENT")
    
    st.divider()

    if not file_exists:
        st.subheader("Action : Ajouter une nouvelle ressource")
        if st.button("➕ CRÉER 'Marvel Enemies'", type="primary", use_container_width=True):
            status_container = st.status("Exécution en cours...", expanded=True)
            
            # 1. Création du fichier
            status_container.write("📝 1. Création du fichier sur le disque...")
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(ENEMIES_FILE, "w", encoding="utf-8") as f:
                f.write("# Marvel Enemies\n\n- Thanos (Titan Fou)\n- Kang (Le Conquérant)\n- Doctor Doom (Latveria)")
            time.sleep(0.5)
            status_container.write("✅ Fichier créé.")
            
            # 2. Trigger notification
            status_container.write(f"📡 2. Notification du serveur MCP ({SERVER_URL})...")
            try:
                r = httpx.post(SERVER_URL, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    status_container.write(f"✅ Notification envoyée ! (Touchés : {data.get('broadcast_count', '?')} clients)")
                    status_container.update(label="Opération Terminée", state="complete", expanded=False)
                    st.success("La ressource a été ajoutée et les clients notifiés.")
                    time.sleep(1)
                    st.rerun()
                else:
                    status_container.write(f"❌ Erreur serveur : {r.status_code}")
                    status_container.update(label="Erreur", state="error")
            except Exception as e:
                status_container.write(f"❌ Impossible de joindre le serveur : {e}")
                status_container.update(label="Erreur Réseau", state="error")
            
    else:
        st.subheader("Action : Supprimer la ressource")
        if st.button("🗑️ SUPPRIMER 'Marvel Enemies'", type="primary", use_container_width=True):
            status_container = st.status("Exécution en cours...", expanded=True)
            
            # 1. Suppression
            status_container.write("🗑️ 1. Suppression du fichier...")
            try:
                os.remove(ENEMIES_FILE)
                time.sleep(0.5)
                status_container.write("✅ Fichier supprimé.")
            except Exception as e:
                status_container.write(f"❌ Erreur suppression : {e}")
            
            # 2. Trigger notification
            status_container.write(f"📡 2. Notification du serveur MCP ({SERVER_URL})...")
            try:
                r = httpx.post(SERVER_URL, timeout=5)
                if r.status_code == 200:
                    data = r.json()
                    status_container.write(f"✅ Notification envoyée ! (Touchés : {data.get('broadcast_count', '?')} clients)")
                    status_container.update(label="Opération Terminée", state="complete", expanded=False)
                    st.warning("La ressource a été supprimée et les clients notifiés.")
                    time.sleep(1)
                    st.rerun()
                else:
                    status_container.write(f"❌ Erreur serveur : {r.status_code}")
                    status_container.update(label="Erreur", state="error")
            except Exception as e:
                status_container.write(f"❌ Impossible de joindre le serveur : {e}")
                status_container.update(label="Erreur Réseau", state="error")
                
    st.caption("Observez les logs du serveur et du client pour voir le flux en temps réel.")

if __name__ == "__main__":
    main()
