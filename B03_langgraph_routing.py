import streamlit as st
import os
import json
from typing import Annotated, TypedDict, Literal
from dotenv import load_dotenv

# Imports LangChain & LangGraph
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END

# ==============================================================================
# Demo LLM - Phase B : Étape 3 : Routage Intelligent (LangGraph)
# ==============================================================================
# ASPECT CLÉ : Cette étape est AUTO-SUFFISANTE. Toute la logique (RAG, Graphe,
# Routage et UI) est contenue dans ce fichier pour faciliter la compréhension.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE RAG ET LLM (Extraite de l'étape 5)
# ------------------------------------------------------------------------------

def get_llm():
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0
    )

def get_embeddings():
    return FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_vector_db():
    embeddings = get_embeddings()
    index_dir = os.path.join("data", "faiss_index")
    if os.path.exists(index_dir):
        return FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    return None

def get_rag_response_internal(query, history=None):
    """Effectue une recherche RAG complète."""
    db = load_vector_db()
    if not db:
        return {"answer": "Erreur : Base de données vectorielle introuvable.", "source_documents": []}
    
    llm = get_llm()
    relevant_docs = db.similarity_search(query, k=3)
    context = "\n\n---\n\n".join([d.page_content for d in relevant_docs])
    
    sys_prompt = f"""Tu es un assistant expert Marvel. 
    Réponds en utilisant UNIQUEMENT le contexte ci-dessous. 
    Si l'info manque, dis : "Désolé, l'information n'est pas dans ma base Marvel."
    
    CONTEXTE :
    {context}"""
    
    messages = [SystemMessage(content=sys_prompt)]
    # Ajout de l'historique si présent
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))
    
    messages.append(HumanMessage(content=query))
    response = llm.invoke(messages)
    
    return {
        "answer": response.content,
        "source_documents": relevant_docs
    }

# ------------------------------------------------------------------------------
# SECTION 2 : LOGIQUE DU GRAPHE D'AGENT (LangGraph)
# ------------------------------------------------------------------------------

class AgentState(TypedDict):
    question: str
    history: list
    route_decision: str  # 'rag' ou 'general'
    response: str
    source_documents: list

def router_node(state: AgentState) -> dict:
    """Analyse si la question concerne Marvel, en tenant compte du contexte."""
    print(f"\n[ENTRY] Nœud 'router' - Entrée: '{state['question'][:40]}...'")
    llm = get_llm()
    
    # ASPECT CLÉ : Prise en compte de l'historique pour résoudre le contexte (ex: "il")
    history_context = ""
    if state['history']:
        last_exchanges = state['history'][-2:] # On prend les 2 derniers échanges
        history_context = "Historique récent :\n" + "\n".join([f"{m['role']}: {m['content']}" for m in last_exchanges])

    prompt = f"""Tu es un expert en classification d'intentions.
    {history_context}
    
    Question actuelle de l'utilisateur : "{state['question']}"
    
    Tâche : Détermine si cette question (en tenant compte de l'historique si nécessaire) concerne l'univers MARVEL.
    - Si la question utilise des pronoms (il, lui, ils) faisant référence à un héros Marvel cité juste avant, c'est 'rag'.
    - Si la question est une salutation ou un sujet totalement différent, c'est 'general'.
    
    Réponds EXCLUSIVEMENT par 'rag' ou 'general'.
    Decision :"""
    
    print("  [LLM CALL] Demande de décision au routeur...")
    resp = llm.invoke([HumanMessage(content=prompt)])
    decision = resp.content.strip().lower()
    
    route = "rag" if "rag" in decision else "general"
    print(f"[EXIT] Nœud 'router' - Décision: {route}")
    return {"route_decision": route}

def rag_branch_node(state: AgentState) -> dict:
    """Exécute la recherche sémantique."""
    print(f"\n[ENTRY] Nœud 'rag_branch' - Question: '{state['question'][:40]}...'")
    print("  [ACTION] Interrogation de la base FAISS et du LLM (RAG)...")
    result = get_rag_response_internal(state['question'], state['history'])
    print("[EXIT] Nœud 'rag_branch' - Réponse générée.")
    return {"response": result["answer"], "source_documents": result["source_documents"]}

def general_branch_node(state: AgentState) -> dict:
    """Réponse polie de désengagement."""
    print(f"\n[ENTRY] Nœud 'general_branch' - Question: '{state['question'][:40]}...'")
    llm = get_llm()
    prompt = f"Explique poliment que tu es un expert Marvel et que tu ne réponds pas à : {state['question']}"
    
    print("  [LLM CALL] Demande de réponse polie (Désengagement)...")
    resp = llm.invoke([HumanMessage(content=prompt)])
    print("[EXIT] Nœud 'general_branch' - Réponse polie envoyée.")
    return {"response": resp.content, "source_documents": []}

def create_marvel_agent():
    workflow = StateGraph(AgentState)
    workflow.add_node("router", router_node)
    workflow.add_node("rag_branch", rag_branch_node)
    workflow.add_node("general_branch", general_branch_node)
    
    workflow.set_entry_point("router")
    workflow.add_conditional_edges(
        "router",
        lambda x: x["route_decision"],
        {"rag": "rag_branch", "general": "general_branch"}
    )
    workflow.add_edge("rag_branch", END)
    workflow.add_edge("general_branch", END)
    return workflow.compile()

# ------------------------------------------------------------------------------
# SECTION 3 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Demo LLM - Étape 6", page_icon="🧭", layout="wide")

# TITRE UNIFIÉ
st.title("🦸 Demo LLM - Assistant Marvel")

# ENCART D'INFORMATION (ASPECT CLÉ)
with st.expander("ℹ️ À propos de cette étape : Routage Intelligent", expanded=False):
    st.markdown("""
    **Ce qui est testé dans cette étape :**
    L'utilisation de **LangGraph** pour orchestrer un flux de décision. L'agent n'est plus linéaire : il réfléchit au meilleur chemin.
    
    **Comment tester :**
    1. Posez une question sur Marvel (ex: "Qui est Hulk ?") -> L'agent doit activer la branche **RAG**.
    2. Posez une question hors-sujet (ex: "Comment faire un gâteau ?") -> L'agent doit activer la branche **Générale**.
    
    **Logique du Graphe :**
    """)
    # ASPECT CLÉ : Utilisation de Graphviz pour un rendu natif dans Streamlit
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, style=filled, fontname="Helvetica", fontsize=10];
            Start [shape=circle, style=filled, color=lightgrey, label="Début"];
            Router [shape=diamond, style=filled, color=orange, label="Routeur ?"];
            RAG [style=filled, color=palegreen, label="Branche RAG\\n(Marvel)"];
            General [style=filled, color=lightcoral, label="Branche Générale\\n(Autre)"];
            End [shape=circle, style=filled, color=lightgrey, label="Fin"];
            
            Start -> Router;
            Router -> RAG [label="Marvel", fontsize=10];
            Router -> General [label="Autre", fontsize=10];
            RAG -> End;
            General -> End;
        }
    ''')

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle Conversation", use_container_width=True):
        st.session_state.messages_06 = []
        st.rerun()

# État de la session
if "messages_06" not in st.session_state:
    st.session_state.messages_06 = []

# Affichage des messages
for msg in st.session_state.messages_06:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "decision" in msg:
            st.caption(f"🧭 Décision Agent : **{msg['decision'].upper()}**")

# Interaction
if prompt := st.chat_input("Défiez l'agent Marvel !"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages_06.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("L'agent analyse le graphe..."):
            agent = create_marvel_agent()
            initial_state = {
                "question": prompt,
                "history": st.session_state.messages_06[:-1],
                "route_decision": "",
                "response": "",
                "source_documents": []
            }
            final_state = agent.invoke(initial_state)
            
            decision = final_state["route_decision"]
            response = final_state["response"]
            
            if decision == "rag":
                st.success("🎯 Sujet Marvel identifié. Utilisation de la base de connaissances.")
            else:
                st.warning("👋 Sujet hors-domaine identifié. Branche de politesse activée.")
            
            st.markdown(response)
            
            if final_state["source_documents"]:
                with st.expander("📚 Sources"):
                    for d in final_state["source_documents"]:
                        st.write(f"- {os.path.basename(d.metadata.get('source', 'Index'))}")

    st.session_state.messages_06.append({
        "role": "assistant", 
        "content": response,
        "decision": decision
    })
