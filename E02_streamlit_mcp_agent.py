import streamlit as st
import asyncio
import os
import sys
import json
from dotenv import load_dotenv
from mcp import ClientSession
from mcp.client.sse import sse_client
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import StructuredTool

# ==============================================================================
# Demo LLM - Phase E : Étape 2 : L'Agent Connecté (Intelligence & Action)
# ==============================================================================
# ASPECT CLÉ : Le LLM découvre dynamiquement les outils via le protocole MCP
# et les utilise pour répondre à l'utilisateur.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR MCP & AGENT
# ------------------------------------------------------------------------------

MCP_SERVER_URL = "http://127.0.0.1:8000/sse"

async def mcp_list_tools():
    """Découvre les outils disponibles sur le serveur MCP."""
    async with sse_client(url=MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.list_tools()
            return result.tools

async def mcp_call_tool(name, args):
    """Exécute un outil sur le serveur MCP."""
    # Correction : Si LangChain a encapsulé les arguments dans une clé 'kwargs'
    actual_args = args.get('kwargs', args) if isinstance(args, dict) else args
    
    print(f"  [MCP CLIENT] Transmission: Envoi de la requête MCP vers {name}...")
    print(f"               Paramètres: {actual_args}")
    
    async with sse_client(url=MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(name, actual_args)
            return result

class MCPConnectedAgent:
    def __init__(self, mcp_tools_metadata):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        
        # TRANSFORMATION : On transforme les outils MCP en outils LangChain
        self.lc_tools = []
        for t_meta in mcp_tools_metadata:
            # On utilise une fonction de fabrique pour éviter les problèmes de fermeture (closures)
            def create_tool_func(tool_name):
                return lambda **kwargs: asyncio.run(mcp_call_tool(tool_name, kwargs))
            
            lc_tool = StructuredTool.from_function(
                func=create_tool_func(t_meta.name),
                name=t_meta.name,
                description=t_meta.description
            )
            self.lc_tools.append(lc_tool)
        
        print(f"  [MCP CLIENT] Configuration: {len(self.lc_tools)} outils liés au LLM.")
        
        # Liaison des outils au LLM
        self.llm_with_tools = self.llm.bind_tools(self.lc_tools)
        
        self.system_prompt = """Tu es un assistant expert Marvel connecté à des services externes via MCP.
        Utilise les outils à ta disposition pour répondre avec précision.
        Si l'outil renvoie du JSON, interprète-le pour faire une réponse naturelle et épique."""

    def chat(self, user_input, history):
        messages = [SystemMessage(content=self.system_prompt)]
        for msg in history:
            messages.append(msg)
        messages.append(HumanMessage(content=user_input))

        # 1. Analyse et décision de l'IA
        print(f"\n[ENTRY] Agent MCP confronté à : '{user_input[:50]}'")
        print("  [LLM CALL] Le modèle analyse la demande...")
        ai_msg = self.llm_with_tools.invoke(messages)
        
        if ai_msg.tool_calls:
            tool_call = ai_msg.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"[DECISION] Le LLM a choisi d'appeler l'outil MCP: {tool_name}")
            
            # 2. Exécution via MCP
            status_text = f"🛠️ Appel du service MCP : `{tool_name}`..."
            yield {"type": "status", "content": status_text}
            
            raw_result = asyncio.run(mcp_call_tool(tool_name, tool_args))
            
            # Extraction du texte pour le LLM
            tool_output_text = raw_result.content[0].text if raw_result.content else "Aucun résultat"
            print(f"  [RESULT] Réponse du serveur MCP reçue ({len(tool_output_text)} caractères).")
            
            # 3. Synthèse finale
            synthesis_prompt = f"""Le service technique a répondu : {tool_output_text}. 
            Fais-en une synthèse épique pour l'utilisateur."""
            
            messages.append(ai_msg)
            messages.append(ToolMessage(content=tool_output_text, tool_call_id=tool_call["id"]))
            
            print("  [LLM CALL] Génération du récit final...")
            final_resp = self.llm.invoke(messages + [HumanMessage(content=synthesis_prompt)])
            
            yield {
                "type": "result",
                "tool_name": tool_name,
                "args": tool_args,
                "raw_result": tool_output_text,
                "answer": final_resp.content
            }
        else:
            print("[DECISION] Pas d'outil MCP requis. Réponse directe.")
            yield {
                "type": "result",
                "answer": ai_msg.content
            }

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="MCP E02 : Connected Agent", page_icon="🤖", layout="wide")
    st.title("🤖 Phase E : Étape 2 : L'Agent Connecté (Intelligence & Action)")

    # ENCART DIDACTIQUE
    with st.expander("ℹ️ Comprendre l'enjeu : L'Intelligence aux commandes", expanded=False):
        st.markdown("""
        **Concept : Le Triangle de l'Action**
        Ici, nous passons de la simple "Découverte" à l'exécution orchestrée par l'IA.
        
        1.  **Découverte (Discovery)** : Au chargement, l'agent explore le serveur MCP.
        2.  **Raisonnement** : Le LLM analyse votre question et décide d'utiliser l'outil adéquat.
        3.  **Exécution Discrète** : Le client exécute l'ordre du LLM sur le serveur distant.
        """)
        st.graphviz_chart('''
            digraph G {
                rankdir=TD;
                node [shape=box, fontname="Helvetica", fontsize=10];
                User [label="Utilisateur"];
                LLM [label="Intelligence (LLM)", style=filled, color=orange];
                Client [label="Application (Orchestrateur)", style=filled, color=lightblue];
                Server [label="Serveur MCP (Action)", style=filled, color=lightgrey];
                
                User -> Client [label="Question"];
                Client -> LLM [label="Demande d'analyse"];
                LLM -> Client [label="Ordre : 'Appelle Tool X'"];
                Client -> Server [label="Exécution via Réseau"];
                Server -> Client [label="Résultat structuré"];
                Client -> LLM [label="Consigne de synthèse"];
                LLM -> Client [label="Récit final"];
                Client -> User [label="Réponse épique"];
            }
        ''')

    # INITIALISATION DYNAMIQUE
    if "mcp_agent" not in st.session_state:
        with st.spinner("Connexion au serveur MCP et découverte des outils..."):
            try:
                tools_meta = asyncio.run(mcp_list_tools())
                st.session_state.mcp_agent = MCPConnectedAgent(tools_meta)
                st.session_state.mcp_history = []
                st.success(f"✅ {len(tools_meta)} outil(s) MCP découvert(s) et prêt(s) !")
            except Exception as e:
                st.error(f"❌ Impossible de joindre le serveur MCP : {e}")
                st.info("Vérifiez que `E01a_mcp_server.py` est bien lancé sur le port 8000.")
                return

    # AFFICHAGE CHAT
    for msg in st.session_state.mcp_history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    # INPUT
    if prompt := st.chat_input("Défiez l'IA (ex: Combat entre Hulk et Thor)..."):
        st.chat_message("user").markdown(prompt)
        
        with st.chat_message("assistant"):
            status_container = st.empty()
            
            for step in st.session_state.mcp_agent.chat(prompt, st.session_state.mcp_history):
                if step["type"] == "status":
                    status_container.info(step["content"])
                
                if step["type"] == "result":
                    status_container.empty()
                    if "tool_name" in step:
                        with st.status(f"🛠️ Service utilisé : {step['tool_name']}", expanded=False):
                            st.write(f"**Arguments** : `{step['args']}`")
                            st.code(step["raw_result"])
                    
                    st.markdown(step["answer"])
                    
                    # Mise à jour historique
                    st.session_state.mcp_history.append(HumanMessage(content=prompt))
                    st.session_state.mcp_history.append(AIMessage(content=step["answer"]))

if __name__ == "__main__":
    main()
