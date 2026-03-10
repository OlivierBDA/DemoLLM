import streamlit as st
import asyncio
import os
import json
from dotenv import load_dotenv

from mcp import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.tools import StructuredTool

# ==>Utiliser LLM_MODEL=gemini-2.5-flash
# ==============================================================================
# Demo LLM - Phase E : Étape 7b : Client Prompts MCP
# ==============================================================================
# ASPECT CLÉ : Le client demande au serveur MCP un "Prompt" pré-formaté.
# Ce prompt inclut toutes les instructions et les données de contexte (fichiers).
# Ensuite, le client passe ce prompt prêt-à-l'emploi à son LLM Local.
# ==============================================================================

MCP_SERVER_URL = "http://127.0.0.1:8006/sse"

# --- FONCTIONS MCP ---
@st.cache_data(ttl=60)
def mcp_get_metadata():
    """Récupère la liste des prompts et des outils disponibles."""
    async def fetch():
        async with sse_client(url=MCP_SERVER_URL) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                prompts_res = await session.list_prompts()
                tools_res = await session.list_tools()
                return prompts_res.prompts, tools_res.tools
    try:
        return asyncio.run(fetch())
    except Exception as e:
        st.error(f"❌ Erreur de connexion au serveur MCP : {e}")
        return [], []

async def mcp_get_prompt(prompt_name, arguments):
    """Génère le prompt complet via le serveur MCP."""
    async with sse_client(url=MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.get_prompt(prompt_name, arguments)

async def mcp_call_tool(name, args):
    """Exécute un outil MCP."""
    actual_args = args.get('kwargs', args) if isinstance(args, dict) else args
    async with sse_client(url=MCP_SERVER_URL) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(name, actual_args)

# --- LANGCHAIN AGENT LOGIC ---
class MCPAgentWithPrompts:
    def __init__(self, mcp_tools_metadata):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL", "gemini-2.5-flash"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        
        # Wrap MCP Tools into LangChain StructuredTools
        self.lc_tools = []
        for t_meta in mcp_tools_metadata:
            def create_tool_func(tool_name):
                return lambda **kwargs: asyncio.run(mcp_call_tool(tool_name, kwargs))
            
            lc_tool = StructuredTool.from_function(
                func=create_tool_func(t_meta.name),
                name=t_meta.name,
                description=t_meta.description
            )
            self.lc_tools.append(lc_tool)
        
        # Bind tools to LLM
        if self.lc_tools:
            self.llm_with_tools = self.llm.bind_tools(self.lc_tools)
        else:
            self.llm_with_tools = self.llm
            
    def convert_mcp_prompt_to_lc(self, mcp_prompt_result: types.GetPromptResult):
        lc_messages = []
        if mcp_prompt_result.description:
            lc_messages.append(SystemMessage(content=f"Contexte fourni par le Serveur MCP: {mcp_prompt_result.description}"))
             
        for msg in mcp_prompt_result.messages:
            c = msg.content
            final_text = ""
            if isinstance(c, types.TextContent):
                final_text = c.text
            elif isinstance(c, types.EmbeddedResource):
                res_content = c.resource
                if isinstance(res_content, types.TextResourceContents):
                    # On met bien en évidence la ressource injectée
                    final_text = f"--- DÉBUT FICHIER INJECTÉ ({res_content.uri}) ---\n{res_content.text}\n--- FIN FICHIER INJECTÉ ---\n"
                else:
                    final_text = f"[Ressource non-texte ignorée: {res_content.uri}]"
                    
            if msg.role == "user":
                lc_messages.append(HumanMessage(content=final_text))
            elif msg.role == "assistant":
                lc_messages.append(AIMessage(content=final_text))
                
        return lc_messages

    def run_prompt(self, lc_messages):
        """Exécute l'agent Langchain avec les messages préparés."""
        print("\n" + "="*50)
        print("  [LLM CLIENT] START: DEBUT DE L'ANALYSE DU PROMPT")
        print("="*50)
        print("  [LLM CLIENT] Envoi du prompt prepare au LLM pour analyse initiale...")
        ai_msg = self.llm_with_tools.invoke(lc_messages)
        
        # S'il doit appeler un Tool (pour le combat)
        if hasattr(ai_msg, "tool_calls") and ai_msg.tool_calls:
            tool_call = ai_msg.tool_calls[0]
            tool_name = tool_call['name']
            tool_args = tool_call['args']
            
            print(f"  [LLM CLIENT] DECISION: Le LLM a choisi d'appeler l'outil MCP '{tool_name}'")
            print(f"  [LLM CLIENT] ARGUMENTS: {tool_args}")
            print(f"  [LLM CLIENT] REQUÊTE: Envoi de la commande d'execution au serveur MCP...")
            yield {"type": "status", "content": f"🛠️ Le LLM décide d'utiliser l'outil : `{tool_name}`"}
            
            raw_result = asyncio.run(mcp_call_tool(tool_name, tool_args))
            tool_output_text = raw_result.content[0].text if raw_result.content else "Aucun résultat"
            
            print(f"  [LLM CLIENT] RÉPONSE MCP: Resultat recu du serveur ({len(tool_output_text)} chars)")
            print(f"  [LLM CLIENT] SYNTHÈSE: Renvoi du resultat au LLM pour la synthese finale...")
            yield {"type": "status", "content": f"Retour de l'outil reçu : `{tool_output_text}`. Synthèse en cours..."}
            
            # Repasse la balle au LLM pour la synthèse avec le message standard Langchain
            lc_messages.append(ai_msg)
            lc_messages.append(ToolMessage(content=tool_output_text, tool_call_id=tool_call["id"]))
            
            final_resp = self.llm.invoke(lc_messages)
            print("  [LLM CLIENT] TERMINÉ: Synthese finale generee par le LLM.")
            print("="*50 + "\n")
            yield {"type": "result", "answer": final_resp.content}
            
        else:
            # Réponse directe (pour le JSON)
            print("  [LLM CLIENT] DECISION: Le LLM a genere une reponse directe (pas d'outil requis).")
            print("  [LLM CLIENT] TERMINÉ: Reponse finale prete.")
            print("="*50 + "\n")
            yield {"type": "result", "answer": ai_msg.content}


# --- STREAMLIT UI ---
def main():
    st.set_page_config(page_title="MCP Prompts", page_icon="📝", layout="wide")
    st.title("📝 E07 : MCP Prompts (Gabarits Côté Serveur)")
    st.markdown("Utilisez cette interface pour voir comment un serveur MCP fournit un **contexte préparé** (ressources et instructions) pour guider le LLM.")

    # L'encart didactique a été déplacé dans le Cockpit (Concept).
    st.markdown("---")

    # 1. Fetch Prompts & Tools
    prompts_meta, tools_meta = mcp_get_metadata()
    if not prompts_meta and not tools_meta:
        st.warning("Veuillez lancer `python E07a_mcp_server_prompts.py` dans un terminal séparé.")
        st.stop()

    prompt_options = {p.name: p for p in prompts_meta}
    
    st.sidebar.header("Configuration")
    selected_prompt_name = st.sidebar.selectbox("Choisissez un Prompt MCP", list(prompt_options.keys()))
    selected_prompt = prompt_options[selected_prompt_name]
    
    st.sidebar.markdown(f"**Description:** _{selected_prompt.description}_")
    
    # 2. Dynamic Form for Arguments
    st.subheader(f"Paramètres pour `{selected_prompt_name}`")
    user_args = {}
    
    with st.form("prompt_form"):
        for arg in selected_prompt.arguments:
            user_args[arg.name] = st.text_input(
                f"{arg.name} " + ("*" if arg.required else ""), 
                help=arg.description
            )
        
        submitted = st.form_submit_button("Générer et Analyser")
        
    if submitted:
        # Check required args
        missing = [arg.name for arg in selected_prompt.arguments if arg.required and not user_args[arg.name]]
        if missing:
            st.error(f"Veuillez remplir les champs obligatoires : {', '.join(missing)}")
            return
            
        st.divider()
        col1, col2 = st.columns([1, 1.2])
        
        with col1:
            st.markdown("### 🔍 1. Ce que le serveur MCP a renvoyé")
            st.info("Le client reçoit un objet `PromptMessage` prêt à être envoyé au LLM. Remarquez comment le serveur a inclus ses propres instructions ou fichiers.")
            
            with st.spinner("Récupération du prompt depuis le serveur MCP..."):
                try:
                    mcp_prompt_result = asyncio.run(mcp_get_prompt(selected_prompt_name, user_args))
                    
                    # Display Raw Messages
                    for i, msg in enumerate(mcp_prompt_result.messages):
                        content = msg.content
                        if isinstance(content, types.TextContent):
                            st.text_area(f"Message {i+1} ({msg.role})", content.text, height=200, disabled=True)
                        elif isinstance(content, types.EmbeddedResource):
                            res = content.resource
                            if isinstance(res, types.TextResourceContents):
                                st.text_area(f"Ressource Injectée ({msg.role}) : {res.uri}", res.text, height=150, disabled=True)
                except Exception as e:
                    st.error(f"Erreur lors de la récupération du prompt: {e}")
                    return
                            
        with col2:
            st.markdown("### 🤖 2. Réponse du LLM (LangChain)")
            st.info("Le LLM analyse le prompt ci-contre et utilise un outil MCP si demandé.")
            
            agent = MCPAgentWithPrompts(tools_meta)
            lc_messages = agent.convert_mcp_prompt_to_lc(mcp_prompt_result)
            
            status_container = st.empty()
            result_container = st.empty()
            
            try:
                for step in agent.run_prompt(lc_messages):
                    if step["type"] == "status":
                        status_container.warning(step["content"])
                    elif step["type"] == "result":
                        status_container.success("Analyse terminée !")
                        result_container.markdown(step["answer"])
            except Exception as e:
                st.error(f"Erreur lors de l'exécution du LLM: {e}")

if __name__ == "__main__":
    main()
