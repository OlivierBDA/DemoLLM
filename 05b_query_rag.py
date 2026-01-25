import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.messages import HumanMessage, SystemMessage

# ==============================================================================
# Demo LLM - Étape 5B : Question Réponse RAG (Version FastEmbed)
# ==============================================================================
# Aspect Clé : Utilisation de FastEmbed pour la recherche sémantique.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR RAG
# ------------------------------------------------------------------------------

def init_rag_components():
    """Charge l'index FAISS et initialise le LLM."""
    load_dotenv()
    
    # 1. Chargement du modèle d'embeddings FastEmbed
    # Doit être identique à celui utilisé lors de l'indexation (5A)
    embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # 2. Chargement de l'index FAISS
    index_dir = os.path.join("data", "faiss_index")
    if not os.path.exists(index_dir):
        raise FileNotFoundError(f"Index FAISS introuvable dans {index_dir}.")
    
    vector_db = FAISS.load_local(index_dir, embeddings, allow_dangerous_deserialization=True)
    
    # 3. Initialisation du LLM
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0
    )
    
    return llm, vector_db

def perform_rag_query(llm, vector_db, query):
    """Effectue la recherche sémantique et génère la réponse augmentée."""
    
    # Recherche sémantique
    docs = vector_db.similarity_search(query, k=3)
    context = "\n\n---\n\n".join([doc.page_content for doc in docs])
    
    # Construction du Prompt System spécifique au RAG
    system_prompt = f"""Tu es un assistant expert Marvel MCU. 
    Réponds à la question en utilisant UNIQUEMENT le contexte ci-dessous. 
    Si l'information n'est pas dans le contexte, dis précisément : "Désolé, je ne trouve pas cette information dans ma base Marvel."
    
    CONTEXTE :
    {context}"""
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=query)
    ]
    
    response = llm.invoke(messages)
    return response.content, docs

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE TERMINAL
# ------------------------------------------------------------------------------

def main():
    print("--- Demo LLM - Étape 5B : RAG (Interface FastEmbed) ---")
    
    try:
        llm, vector_db = init_rag_components()
    except Exception as e:
        print(f"Erreur d'initialisation : {e}")
        return

    while True:
        query = input("\nVotre question Marvel (exit pour quitter) : ")
        
        if query.lower() in ["exit", "quitter"]:
            break
            
        if not query.strip():
            continue

        print(f"\n[Recherche et Génération...]")
        
        try:
            answer, sources = perform_rag_query(llm, vector_db, query)
            
            # Affichage des sources
            print("\nSOURCES :")
            for i, doc in enumerate(sources):
                src = os.path.basename(doc.metadata.get('source', 'Inconnue'))
                print(f" - {src}")
            
            print("\nRÉPONSE :")
            print(answer)
            print("-" * 50)
            
        except Exception as e:
            print(f"Erreur : {e}")

if __name__ == "__main__":
    main()
