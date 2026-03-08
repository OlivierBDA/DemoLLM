import os
import json
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv

# Imports LangChain & RAG
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Phase B : Étape 2c : Interface RAG (Streamlit)
# ==============================================================================
# ASPECT CLÉ : Cette interface combine le Chat et le RAG. Elle permet également
# de piloter l'ingestion des données depuis la barre latérale.
# ==============================================================================

# Configuration des dossiers
SOURCE_DIR = os.path.join("data", "source_files")
INDEX_DIR = os.path.join("data", "faiss_index")
TRACKING_FILE = os.path.join("data", "processed_files.json")

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR LLM & RAG
# ------------------------------------------------------------------------------

def get_llm():
    """Initialise le client LLM."""
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0,
        streaming=True
    )

def get_embeddings():
    """Initialise le modèle d'embeddings FastEmbed."""
    return FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_vector_db():
    """Charge l'index FAISS s'il existe."""
    embeddings = get_embeddings()
    if os.path.exists(INDEX_DIR):
        return FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
    return None

def ingest_new_files():
    """
    Logique d'ingestion incrémentale (issue de 05a).
    Retourne le nombre de nouveaux fichiers traités.
    """
    if not os.path.exists(SOURCE_DIR):
        return 0, "Dossier source introuvable."
    
    # 1. Tracking
    processed_files = {}
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            processed_files = json.load(f)
            
    all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
    new_files = [f for f in all_files if f not in processed_files]
    
    if not new_files:
        return 0, "Tous les fichiers sont déjà à jour."

    # 2. Processing
    embeddings = get_embeddings()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    
    new_docs = []
    for filename in new_files:
        loader = TextLoader(os.path.join(SOURCE_DIR, filename), encoding="utf-8")
        new_docs.extend(text_splitter.split_documents(loader.load()))
        processed_files[filename] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 3. FAISS
    if os.path.exists(INDEX_DIR):
        db = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        db.add_documents(new_docs)
    else:
        db = FAISS.from_documents(new_docs, embeddings)
    
    db.save_local(INDEX_DIR)
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_files, f, indent=2, ensure_ascii=False)
        
    return len(new_files), "Succès"

def get_rag_response_stream(llm, vector_db, messages):
    """
    Similaire à 05b, mais adapté pour le streaming de conversation.
    ASPECT CLÉ : On utilise le dernier message pour chercher dans la base,
    mais on garde l'historique pour la qualité de la réponse.
    """
    user_query = messages[-1].content
    
    # Recherche sémantique
    relevant_docs = vector_db.similarity_search(user_query, k=3)
    context = "\n\n---\n\n".join([d.page_content for d in relevant_docs])
    
    # On reconstruit le prompt système avec le contexte frais
    sys_message = SystemMessage(content=f"""Tu es un assistant expert Marvel MCU. 
    Réponds en utilisant UNIQUEMENT le contexte ci-dessous. 
    Si l'info manque, dis : "Désolé, l'information n'est pas dans ma base Marvel."
    
    CONTEXTE :
    {context}""")
    
    # On remplace temporairement le message système initial par notre message RAG
    # pour cet appel spécifique (ou on le rajoute)
    rag_messages = [sys_message] + [m for m in messages if not isinstance(m, SystemMessage)]
    
    return llm.stream(rag_messages), relevant_docs

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def main():
    st.set_page_config(page_title="Marvel RAG Explorer", page_icon="📚", layout="wide")

    # --- SIDEBAR : Pilotage des données ---
    with st.sidebar:
        st.title("⚙️ Pilotage RAG")
        if st.button("🔄 Mettre à jour la Vector DB", use_container_width=True):
            with st.spinner("Analyse des nouveaux fichiers..."):
                count, msg = ingest_new_files()
                if count > 0:
                    st.success(f"{count} fiches ajoutées !")
                else:
                    st.info(msg)
        
        st.divider()
        if st.button("🗑️ Effacer la conversation", use_container_width=True):
            st.session_state.messages = [SystemMessage(content="Expert Marvel")]
            st.rerun()
            
        st.divider()
        st.caption("Documents indexés :")
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, "r", encoding="utf-8") as f:
                tracking = json.load(f)
                file_list = sorted(list(tracking.keys()))
                if file_list:
                    st.selectbox("Liste des fichiers", file_list, label_visibility="collapsed")
                else:
                    st.text("Aucun document")

    st.title("🦸 Demo LLM : Assistant Marvel (Mode RAG)")
    
    # L'encart d'information a été déplacé dans le Cockpit principal (onglet Concept).
    st.markdown("---")

    # --- CHAT INTERFACE ---
    if "messages" not in st.session_state:
        st.session_state.messages = [SystemMessage(content="Expert Marvel")]

    # Chargement unique de la DB
    if "vector_db" not in st.session_state:
        st.session_state.vector_db = load_vector_db()

    # Affichage
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"): st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"): st.markdown(msg.content)

    # Entrée Chat
    if prompt := st.chat_input("Posez votre question sur les Avengers..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages.append(HumanMessage(content=prompt))

        with st.chat_message("assistant"):
            if st.session_state.vector_db is None:
                # Tentative de rechargement au cas où l'index vient d'être créé
                st.session_state.vector_db = load_vector_db()

            if st.session_state.vector_db is None:
                st.warning("La base de données vectorielle est vide. Cliquez sur 'Mettre à jour' dans la barre latérale.")
            else:
                placeholder = st.empty()
                full_response = ""
                
                llm = get_llm()
                stream, sources = get_rag_response_stream(llm, st.session_state.vector_db, st.session_state.messages)
                
                for chunk in stream:
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")
                placeholder.markdown(full_response)
                
                # Optionnel : Affichage des sources sous la réponse
                with st.expander("🔍 Sources consultées pour cette réponse"):
                    for d in sources:
                        src_name = os.path.basename(d.metadata.get('source', 'Inconnue'))
                        st.write(f"**Document :** {src_name}")
                        st.caption(d.page_content[:200] + "...")

                st.session_state.messages.append(AIMessage(content=full_response))

if __name__ == "__main__":
    main()
