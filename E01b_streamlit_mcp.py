import streamlit as st
import asyncio
import os
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Étape 11 : Model Context Protocol (MCP)
# ==============================================================================
# ASPECT CLÉ : Le client dérive ses capacités par l'inspection du serveur via MCP.
# ==============================================================================

# --- CONFIGURATION INITIALE ---
load_dotenv()

def init_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
    )

async def get_mcp_capabilities():
    """Se connecte au serveur et inspecte ses capacités (Discovery)."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["E01a_mcp_server.py"],
        env=os.environ.copy()
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # Discovery Phase
            tools = await session.list_tools()
            resources = await session.list_resources()
            prompts = await session.list_prompts()
            
            return {
                "tools": tools,
                "resources": resources,
                "prompts": prompts
            }

async def call_mcp_tool(tool_name, arguments):
    """Appelle un outil sur le serveur MCP."""
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["E01a_mcp_server.py"],
        env=os.environ.copy()
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Step 11 : MCP Explorer", page_icon="🔌", layout="wide")

st.title("🔌 Phase E : Étape 1 : Model Context Protocol (MCP)")

# ENCART DIDACTIQUE
with st.expander("ℹ️ À propos du MCP (Model Context Protocol)", expanded=True):
    st.markdown("""
    **MCP** est un protocole ouvert qui permet de connecter des sources de données et des outils à des modèles d'IA de manière standardisée.
    
    1.  **Discovery** : Le client (cette UI) interroge le serveur pour savoir ce qu'il peut faire.
    2.  **Resources** : Accès à des données (ex: fichiers de personnages).
    3.  **Tools** : Capacités d'exécution (ex: SQL, calculs).
    4.  **Prompts** : Modèles de requêtes pré-définis.
    
    *Ici, le serveur `11a_mcp_server.py` tourne en arrière-plan et expose ses capacités à ce client.*
    """)

# INITIALISATION DU STATE
if "mcp_data" not in st.session_state:
    with st.spinner("📦 Connexion au serveur MCP et découverte des capacités..."):
        st.session_state.mcp_data = asyncio.run(get_mcp_capabilities())

mcp_data = st.session_state.mcp_data

# MISE EN PAGE : 2 COLONNES
col_discovery, col_demo = st.columns([1, 2])

with col_discovery:
    st.header("🔍 Discovery Phase")
    
    st.subheader("🛠️ Tools exposés")
    for tool in mcp_data["tools"].tools:
        st.info(f"**{tool.name}**\n\n{tool.description}")
        
    st.subheader("📚 Resources disponibles")
    for res in mcp_data["resources"].resources:
        st.code(f"{res.uri}\n({res.name})")

    st.subheader("📝 Prompts enregistrés")
    for p in mcp_data["prompts"].prompts:
        st.warning(f"**{p.name}** : {p.description}")

with col_demo:
    st.header("🚀 Utilisation du Protocole")
    
    tabs = st.tabs(["Lire Ressource", "Appeler Tool", "Chat (Simulé)"])
    
    with tabs[0]:
        st.write("Demande de lecture directe via URI")
        selected_res = st.selectbox("Choisir une ressource", [r.uri for r in mcp_data["resources"].resources])
        if st.button("Lire la ressource"):
            # Simulation d'appel ressource (read_resource n'est pas utilisé directement ici par simplicité mais le concept y est)
            st.success(f"Lecture de {selected_res}...")
            st.info("Dans un flux réel, le LLM déciderait d'utiliser cette URI comme contexte.")
            
    with tabs[1]:
        st.write("Exécution d'un outil standardisé")
        tool_to_call = st.selectbox("Choisir un tool", ["calculate_power_level", "query_marvel_db"])
        
        if tool_to_call == "calculate_power_level":
            h_name = st.text_input("Nom du héros", "Spider-Man")
            if st.button("Lancer le calcul"):
                res = asyncio.run(call_mcp_tool("calculate_power_level", {"hero_name": h_name}))
                st.json(res)
        
        elif tool_to_call == "query_marvel_db":
            q_sql = st.text_area("Requête SQL", "SELECT * FROM heroes LIMIT 3")
            if st.button("Exécuter SQL"):
                res = asyncio.run(call_mcp_tool("query_marvel_db", {"sql_query": q_sql}))
                st.markdown(res[0].text)

    with tabs[2]:
        st.write("Interaction Agent + MCP")
        st.markdown("""
        Dans un environnement final (ex: Claude Desktop), le LLM recevrait automatiquemebnt les définitions JSON des outils ci-contre.
        Il traduirait votre question : 
        *'Quels sont les films où apparaît Iron Man ?'* 
        
        En un appel MCP :
        ```json
        {
          "method": "tools/call",
          "params": {
            "name": "query_marvel_db",
            "arguments": { "sql_query": "SELECT movie_title FROM hero_appearances WHERE hero_name='Iron Man'" }
          }
        }
        ```
        """)
        st.button("Démarrer une session Agent (Coming Soon in A2A step)")

st.sidebar.markdown("---")
st.sidebar.title("⚙️ Debug Console")
if st.sidebar.button("Ré-init Discovery"):
    del st.session_state.mcp_data
    st.rerun()

st.sidebar.write("Logs de connexion :")
st.sidebar.text("STDIO Stream: OPEN\nProtocol Version: 2024-11-05\nReady.")
