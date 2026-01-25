import os
import json
from datetime import datetime
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain_community.vectorstores import FAISS

# ==============================================================================
# Demo LLM - Étape 5A : Construction de la Base Vectorielle (FAISS + FastEmbed)
# ==============================================================================
# Aspect Clé : Utilisation de FastEmbed (ONNX) à la place de PyTorch pour 
# éviter les erreurs de DLL sur Windows. C'est plus léger et rapide.
# ==============================================================================

# Dossiers de travail
SOURCE_DIR = os.path.join("data", "source_files")
INDEX_DIR = os.path.join("data", "faiss_index")
TRACKING_FILE = os.path.join("data", "processed_files.json")

def load_processed_files():
    """Charge la liste des fichiers déjà intégrés dans la DB."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_processed_files(processed_files):
    """Sauvegarde la liste mise à jour des fichiers traités."""
    with open(TRACKING_FILE, "w", encoding="utf-8") as f:
        json.dump(processed_files, f, indent=2, ensure_ascii=False)

def main():
    print("--- Demo LLM - Étape 5A : Vectorisation avec FastEmbed ---")
    
    # 1. Préparation
    processed_files = load_processed_files()
    all_files = [f for f in os.listdir(SOURCE_DIR) if f.endswith(".txt")]
    new_files = [f for f in all_files if f not in processed_files]
    
    if not new_files:
        print("[Info] Aucun nouveau fichier à traiter. La base est à jour.")
        return

    print(f"[Info] {len(new_files)} nouveau(x) fichier(s) détecté(s).")

    # 2. Initialisation du modèle d'embeddings (FastEmbed)
    # ASPECT CLÉ : FastEmbed utilise ONNX Runtime, beaucoup plus stable sur Windows.
    # Il téléchargera le modèle all-MiniLM-L6-v2 par défaut si non spécifié.
    print(f"[Info] Initialisation de FastEmbed (Modèle : all-MiniLM-L6-v2)...")
    embeddings = FastEmbedEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # 3. Chargement et Découpage des nouveaux documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    
    new_documents = []
    for filename in new_files:
        print(f"   - Chargement et découpage de : {filename}")
        loader = TextLoader(os.path.join(SOURCE_DIR, filename), encoding="utf-8")
        docs = loader.load()
        chunks = text_splitter.split_documents(docs)
        new_documents.extend(chunks)
        
        # Marquer comme traité
        processed_files[filename] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 4. Création ou Mise à jour de l'index FAISS
    if os.path.exists(INDEX_DIR):
        print("[Info] Mise à jour de l'index FAISS existant...")
        vector_db = FAISS.load_local(INDEX_DIR, embeddings, allow_dangerous_deserialization=True)
        vector_db.add_documents(new_documents)
    else:
        print("[Info] Création d'un nouvel index FAISS...")
        vector_db = FAISS.from_documents(new_documents, embeddings)

    # 5. Sauvegarde
    print(f"[Info] Sauvegarde de l'index dans : {INDEX_DIR}")
    vector_db.save_local(INDEX_DIR)
    save_processed_files(processed_files)
    
    print("\n--- Terminé ! Base vectorielle générée avec succès. ---")

if __name__ == "__main__":
    main()
