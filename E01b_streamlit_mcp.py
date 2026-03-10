import streamlit as st
import asyncio
import os
import sys
import json
from mcp import ClientSession
from mcp.client.sse import sse_client

# ==============================================================================
# Demo LLM - Phase E : Étape 1b : Le Client MCP (Version RÉSEAU)
# ==============================================================================
# ASPECT CLÉ : Le client se connecte à une URL distante via SSE.
# Il n'y a plus de dépendance au script Python local pour l'exécution.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR MCP (Le "Tuyau" Technique)
# ------------------------------------------------------------------------------

# Déclaration de l'URL du serveur MCP
MCP_SERVER_URL = "http://127.0.0.1:8000/sse"

async def discover_capabilities(url):
    """
    Effectue la phase de 'Discovery' via le protocole réseau SSE.
    """
    async with sse_client(url=url) as (read, write):
        async with ClientSession(read, write) as session:
            # Lifecycle : Initialisation de la connexion (Negotiation JSON-RPC)
            await session.initialize()
            
            # Feature : Discovery (Interrogation des outils disponibles)
            tools_result = await session.list_tools()
            return tools_result


# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def configure_page():
    """Configure les méta-données et l'encart didactique (Orientation Manager)."""
    st.set_page_config(page_title="MCP E01 : Discovery", page_icon="🔌", layout="wide")
    st.subheader("🔌 Phase E : Étape 1 : Le Contrat de Service Universel")
    
    # L'encart didactique a été déplacé dans le Cockpit (Concept).
    st.markdown("---")

def render_server_info():
    """Affiche les informations techniques du serveur déclaré."""
    st.info("### 🌎 Serveur MCP Distant")
    st.code(f"URL : {MCP_SERVER_URL}\nTransport : SSE (Server-Sent Events)")

def render_discovery_ui():
    """Gère le bouton de découverte et l'affichage des schémas."""
    if st.button("🔍 Interroger le serveur MCP distant (Discovery)", use_container_width=True):
        with st.spinner("Connexion au serveur via HTTP..."):
            try:
                # Appelle la logique technique de la SECTION 1
                capabilities = asyncio.run(discover_capabilities(MCP_SERVER_URL))
                
                st.success("✅ Capacités découvertes avec succès !")
                
                st.header("🛠️ Services (Tools) identifiés")
                for tool in capabilities.tools:
                    with st.expander(f"Service : {tool.name}", expanded=True):
                        st.markdown(f"**Description :** {tool.description}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.subheader("📥 Contrat d'Entrée")
                            st.json(tool.inputSchema)
                        
                        with col2:
                            st.subheader("📤 Contrat de Sortie (v2025)")
                            if hasattr(tool, 'outputSchema') and tool.outputSchema:
                                st.json(tool.outputSchema)
                            else:
                                st.warning("Aucun schéma de sortie défini.")
                        
                        st.info("💡 **Note d'Architecte** : L'échange se fait via des flux HTTP asynchrones.")

                with st.sidebar:
                    st.subheader("🔐 Coulisses HTTP")
                    st.write("Le client a ouvert un flux EventSource vers :")
                    st.code(f"GET {MCP_SERVER_URL}")
                    st.write("Et envoie des messages via :")
                    st.code("POST /messages/")

            except Exception as e:
                st.error(f"Erreur de connexion réseau : {e}")
                st.warning("Assurez-vous que le serveur (E01a) tourne sur le port 8000.")
    else:
        st.write("Cliquez pour simuler une découverte client-serveur réelle via le réseau.")

def main():
    configure_page()
    render_server_info()
    render_discovery_ui()
    
    st.markdown("---")
    st.markdown("""
    > [!IMPORTANT]
    > Ici, le client Streamlit ne sait PAS que le serveur est écrit en Python. 
    > Il communique uniquement via des standards Web (HTTP, JSON, SSE).
    """)

if __name__ == "__main__":
    main()
