import streamlit as st
import asyncio
import os
import sys
from mcp import ClientSession
from mcp.client.sse import sse_client

# ==============================================================================
# Demo LLM - Phase E : Étape 3b : L'Explorateur de Ressources (Version RÉSEAU)
# ==============================================================================
# ASPECT CLÉ : Le client interroge le serveur pour lister les "livres" disponibles
# et permet de les lire via une URI standardisée.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR MCP (Le "Tuyau" Technique)
# ------------------------------------------------------------------------------

# Déclaration de l'URL du serveur de ressources (Port 8001)
MCP_RESOURCES_URL = "http://127.0.0.1:8001/sse"

async def mcp_list_resources():
    """Effectue la phase de 'Discovery' pour les ressources."""
    print("  [MCP CLIENT] Discovery: Recherche des ressources disponibles...")
    async with sse_client(url=MCP_RESOURCES_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_resources()
            return result.resources

async def mcp_read_resource(uri):
    """Lit le contenu d'une ressource via son URI."""
    print(f"  [MCP CLIENT] Reading: Récupération de la ressource {uri}...")
    async with sse_client(url=MCP_RESOURCES_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.read_resource(uri)
            # result est généralement un objet ResourceContent
            return result.contents[0].text if result.contents else "Aucun contenu"

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def configure_page():
    """Configure les méta-données et l'encart didactique (Orientation Manager)."""
    st.set_page_config(page_title="MCP E03 : Resources", page_icon="📚", layout="wide")
    st.title("📚 Phase E : Étape 3 : La Bibliothèque Universelle (Resources)")

    with st.expander("ℹ️ L'intérêt stratégique des Ressources", expanded=True):
        st.markdown("""
        **Le Concept : Un Accès Standardisé au Savoir**
        Dans un SI, les données sont souvent éparpillées (fichiers, bases, API). 
        Le concept de **Resources** dans MCP permet d'exposer ces données comme des documents web (URIs).
        
        **Ce que cette étape démontre :**
        1.  **Uniformisation** : Peu importe où se trouve le fichier, le client y accède via une adresse universelle (`mcp://...`).
        2.  **Transparence** : L'IA peut explorer cette bibliothèque pour trouver le contexte dont elle a besoin pour répondre.
        3.  **Contrôle** : Le serveur décide exactement ce qu'il expose et comment.
        """)
        st.graphviz_chart('''
            digraph G {
                rankdir=LR;
                node [shape=box, fontname="Helvetica", fontsize=10];
                Client [label="Application Cliente", style=filled, color=lightblue];
                Server [label="Serveur de Ressources", style=filled, color=lightgrey];
                
                Client -> Server [label="1. Quelles sont les fiches dispo ?"];
                Server -> Client [label="2. Voici la liste (Timeline, Heroes)"];
                Client -> Server [label="3. Je veux lire 'mcp://marvel/timeline'"];
                Server -> Client [label="4. Envoi du document Markdown"];
            }
        ''')
    st.markdown("---")

def main():
    configure_page()

    # -- LOGS TERMINAL --
    print("\n[ENTRY] Chargement de l'Explorateur de Ressources")

    # Initialisation de la liste des ressources
    if "resources_list" not in st.session_state:
        with st.spinner("Connexion au serveur MCP (Port 8001)..."):
            try:
                st.session_state.resources_list = asyncio.run(mcp_list_resources())
                st.success(f"✅ {len(st.session_state.resources_list)} ressource(s) découverte(s).")
            except Exception as e:
                st.error(f"❌ Impossible de joindre le serveur MCP : {e}")
                st.info("Vérifiez que `E03a_mcp_server_resources.py` tourne sur le port 8001.")
                return

    # Affichage des ressources disponibles
    st.header("🛒 Catalogue des données disponibles")
    
    # Utilisation de colonnes pour un affichage "cartes"
    cols = st.columns(len(st.session_state.resources_list) if st.session_state.resources_list else 1)
    
    selected_uri = None

    for i, res in enumerate(st.session_state.resources_list):
        with cols[i]:
            st.subheader(res.name)
            st.caption(f"URI: `{res.uri}`")
            st.write(res.description)
            if st.button(f"📄 Lire la ressource", key=res.uri, use_container_width=True):
                selected_uri = res.uri

    st.markdown("---")

    # Zone d'affichage du contenu
    if selected_uri:
        st.header(f"📖 Lecture : {selected_uri}")
        with st.spinner("Chargement du contenu..."):
            try:
                content = asyncio.run(mcp_read_resource(selected_uri))
                st.markdown(content)
                
                # Note technique
                with st.sidebar:
                    st.subheader("⚙️ Détails Techniques")
                    st.write(f"**Ressource** : {selected_uri}")
                    st.write("**Type** : Markdown")
                    st.info("💡 Cette donnée a été récupérée via le protocole réseau MCP sans accès direct au système de fichiers par le client.")
            except Exception as e:
                st.error(f"Erreur lors de la lecture : {e}")
    else:
        st.info("Sélectionnez une ressource ci-dessus pour afficher son contenu.")

if __name__ == "__main__":
    main()
