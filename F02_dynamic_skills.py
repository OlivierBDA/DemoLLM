import os
import json
import streamlit as st
from dotenv import load_dotenv
from typing import Annotated, TypedDict, List
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# ==============================================================================
# Demo LLM - Phase F : Étape 2 : Chargement Dynamique de Compétences
# ==============================================================================
# Ce programme démontre une architecture d'entreprise pour les Skills (Niveau 2).
# L'Agent connaît un "Manifeste" (catalogue de skills) et décide lui-même
# s'il doit charger une Skill spécifique pour répondre à la question.
#
# ASPECT CLÉ : Le contexte de la Skill est "Éphémère". Il n'est pas sauvegardé
# dans l'historique global pour ne pas polluer les questions suivantes.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR LLM (LangGraph & Tools)
# ------------------------------------------------------------------------------

def load_manifest():
    """Charge le catalogue des Skills disponibles."""
    filepath = os.path.join(os.path.dirname(__file__), "skills", "manifest.json")
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"skills": []}

def load_skill_content(filename):
    """Charge le contenu d'un fichier Markdown de Skill."""
    filepath = os.path.join(os.path.dirname(__file__), "skills", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return None

# Initialisation du LLM
load_dotenv()
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL"),
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL"),
    temperature=0.7,
    streaming=True
)

# --- DÉFINITION DE L'OUTIL (Pour que le LLM puisse demander une Skill) ---
@tool
def fetch_skill(skill_id: str) -> str:
    """
    Charge le contenu complet d'une compétence (Skill) spécifique à partir de son ID.
    Utilisez cet outil uniquement si la question nécessite l'expertise décrite dans le manifeste.
    """
    manifest = load_manifest()
    for skill in manifest.get("skills", []):
        if skill["id"] == skill_id:
            content = load_skill_content(skill["file"])
            if content:
                # Notification Streamlit (UI-bound)
                st.session_state.current_skill_loaded = skill["name"]
                return f"CONTENU DE LA SKILL '{skill['name']}' CHARGÉ AVEC SUCCÈS:\n\n{content}"
            else:
                return "Erreur : Fichier de la skill introuvable."
    return f"Erreur : Skill ID '{skill_id}' non reconnue."

# On lie l'outil au LLM
llm_with_tools = llm.bind_tools([fetch_skill])

# --- DÉFINITION DU GRAPHE D'ÉTAT (LangGraph) ---
# Nous utilisons LangGraph pour pouvoir manipuler l'historique avant de répondre au user
class State(TypedDict):
    messages: list
    # Stockage temporaire de la skill pour ne pas polluer 'messages'
    ephemeral_skill_context: str

def agent_node(state: State):
    """Le noeud principal qui réfléchit (avec accès aux outils)."""
    messages = state["messages"]
    
    # Construction du prompt système avec le MANIFESTE
    manifest = load_manifest()
    manifest_str = json.dumps(manifest, indent=2, ensure_ascii=False)
    
    system_prompt = (
        "Vous êtes un super-assistant de l'univers Marvel.\n"
        "Voici le catalogue des compétences (Skills) spécialisées à votre disposition :\n"
        f"{manifest_str}\n\n"
        "SI ET SEULEMENT SI la question de l'utilisateur correspond **exactement** à l'une de ces expertises, "
        "VOUS DEVEZ UTILISER l'outil `fetch_skill` en passant l'ID approprié pour charger le framework d'instruction.\n"
        "Sinon, répondez normalement et de manière enthousiaste sans utiliser d'outil.\n"
    )
    
    # ------------------------------------------------------------------------
    # FIX GEMINI "thought_signature" ERROR:
    # Si le dernier message est un retour d'outil, on masque l'appel technique 
    # au LLM pour éviter le crash lié à la validation stricte des tool_calls.
    # ------------------------------------------------------------------------
    if messages and (getattr(messages[-1], "type", "") == "tool" or type(messages[-1]).__name__ == "ToolMessage"):
        tool_msg = messages[-1]
        
        # On supprime le AIMessage(tool_call) et le ToolMessage de l'historique
        clean_messages = messages[:-2]
        
        # On crée un prompt forçant l'utilisation de la skill
        synthesis_prompt = (
            "Pour répondre à ma question précédente, TU DOIS IMPÉRATIVEMENT appliquer le "
            f"framework de compétence suivant :\n\n{tool_msg.content}"
        )
        
        full_call_messages = [SystemMessage(content=system_prompt)] + clean_messages + [HumanMessage(content=synthesis_prompt)]
        
        # Appel au LLM NORMAL (sans les outils reliés) pour éviter toute boucle infinie
        response = llm.invoke(full_call_messages)
        
        # On ajoute la réponse finale à l'historique propre
        return {"messages": clean_messages + [response]}
        
    else:
        # Mode : Analyse standard (peut décider d'appeler un outil)
        full_call_messages = [SystemMessage(content=system_prompt)] + messages
        response = llm_with_tools.invoke(full_call_messages)
        return {"messages": messages + [response]}

def tool_node(state: State):
    """Le noeud qui exécute l'outil demandé par le LLM."""
    from langchain_core.messages import ToolMessage
    messages = state["messages"]
    last_message = messages[-1]
    
    # On sait qu'il y a un tool_call car on vient ici
    tool_calls = last_message.tool_calls
    # Exécution de l'outil (fetch_skill)
    tool_output = fetch_skill.invoke(tool_calls[0]["args"])
    
    tool_message = ToolMessage(content=str(tool_output), tool_call_id=tool_calls[0]["id"])
    return {"messages": messages + [tool_message]}

def should_continue(state: State):
    """Décide s'il faut appeler un outil ou terminer."""
    messages = state["messages"]
    last_message = messages[-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return END

# Construction du graphe
workflow = StateGraph(State)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")

app_graph = workflow.compile()


# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def configure_page():
    st.set_page_config(page_title="Demo LLM - Dynamic Skills", page_icon="🧠", layout="wide")
    st.subheader("🧠 Demo LLM : Agent Autonome & Skills Éphémères")
    st.markdown("---")

def render_sidebar():
    with st.sidebar:
        st.title("⚙️ Le Manifeste (Niveau 1)")
        st.info("L'Agent connaît l'existence de ces compétences mais n'a pas leur code. Il les chargera dynamiquement si besoin.")
        
        manifest = load_manifest()
        for skill in manifest.get("skills", []):
            with st.expander(f"📦 {skill['name']} ({skill['id']})", expanded=True):
                st.write(f"*{skill['description']}*")
                st.caption(f"Fichier cible : `{skill['file']}`")

        st.markdown("---")
        if st.button("🗑️ Nouvelle Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

def render_chat_history():
    """Affiche uniquement les messages Humains et IA finaux (masque les appels d'outils)."""
    for msg in st.session_state.messages:
        # Affichage conditionnel pour une UI propre (Cacher la cuisine interne)
        if hasattr(msg, "role") and msg.role == "user":
            st.chat_message("user").write(msg.content)
        elif hasattr(msg, "role") and msg.role == "assistant":
            st.chat_message("assistant").write(msg.content)
        elif isinstance(msg, HumanMessage):
             st.chat_message("user").write(msg.content)
        elif isinstance(msg, AIMessage):
             # On n'affiche que s'il y a du contenu (pas un appel d'outil vide)
             if msg.content:
                 st.chat_message("assistant").write(msg.content)

def handle_user_interaction():
    if prompt := st.chat_input("Posez une question (Tactique OU Légale OU Normale)..."):
        # Ajout direct UI
        st.chat_message("user").write(prompt)
        
        # Ajout à l'historique de session
        st.session_state.messages.append(HumanMessage(content=prompt))
        
        # Réinitialisation du flag de notification UI
        st.session_state.current_skill_loaded = None
        
        with st.chat_message("assistant"):
            with st.spinner("L'Agent réfléchit au contexte..."):
                # On passe UNIQUEMENT l'historique épuré (les vraies questions/réponses précédentes)
                # Le passage d'outil de la question N-1 n'est PAS renvoyé au graphe pour la question N
                final_state = app_graph.invoke({"messages": list(st.session_state.messages)})
                
                # Récupération du dernier message (la réponse finale de l'IA)
                final_message = final_state["messages"][-1]
                
                # UI : Si une skill a été chargée pendant l'exécution du graphe
                if st.session_state.get("current_skill_loaded"):
                    st.success(f"⚡ L'Agent a décidé de charger dynamiquement la Skill : **{st.session_state.current_skill_loaded}** pour vous répondre.", icon="🧠")
                
                # Affichage de la réponse
                st.write(final_message.content)
                
                # SAUVEGARDE ÉPURÉE : On ne garde en mémoire que la question et la réponse finale.
                # On Jette littéralement tout le contexte de la Skill, ToolCall, etc généré par LangGraph
                # pour garantir l'isolation des futures questions.
                st.session_state.messages.append(AIMessage(content=final_message.content))

def main():
    configure_page()
    render_sidebar()
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    render_chat_history()
    handle_user_interaction()

if __name__ == "__main__":
    main()
