import streamlit as st
import os
import subprocess
import sys
import time

st.title("Étape B02 : R.A.G (Retrieval Augmented Generation)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Concept et Explication")
    st.markdown("""
**Objectif : Donner une base de connaissances métier au LLM.**

L'IA ne répond plus seulement avec ses connaissances générales publiques. Elle consulte une **base de données vectorielle** (Vector DB) sécurisée avant de formuler sa réponse. C'est l'approche reine en entreprise.
    """)
    
    st.subheader("1. Le processus d'Indexation (Ingestion)")
    st.markdown("""
Pour que le LLM puisse chercher dans nos fichiers textes (B01), il faut d'abord les transformer en langage mathématique.
C'est le rôle du **Chunking** (découper les textes en petits bouts) et de l'**Embedding** (transformer ces bouts en listes de nombres, ou vecteurs, représentant leur sens).
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Doc [label="Document\\n(ex: Iron Man.txt)", shape=note];
            Chunks [label="Chunks\\n(Paragraphes)", style=dashed];
            Embed [label="Modèle d'Embedding\\n(ex: sentence-transformers)", style=filled, color=lightblue];
            Vectors [label="Vecteurs\\n[0.12, -0.45, ...]", style=dotted];
            DB [label="Base Vectorielle\\n(FAISS)", style=filled, color=palegreen];
            
            Doc -> Chunks [label=" Splitter"];
            Chunks -> Embed;
            Embed -> Vectors;
            Vectors -> DB [label=" Sauvegarde"];
        }
    ''')

    st.subheader("2. Le processus de Recherche Générative (RAG)")
    st.markdown("""
Une fois la base de données prête, voici ce qu'il se passe quand vous posez une question :
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question Utilisateur", shape=ellipse];
            DB [label="Vector DB (FAISS)", style=filled, color=palegreen];
            LLM [label="LLM (Context Aware)", style=filled, color=orange];
            Resp [label="Réponse Sourcée", style=filled, color=lightblue];
            
            Q -> DB [label="Recherche Sémantique"];
            DB -> LLM [label="Contexte extrait"];
            Q -> LLM [label="Prompt"];
            LLM -> Resp;
        }
    ''')
    st.info("💡 Ainsi, l'IA construit sa réponse *exclusivement* à partir des documents trouvés, limitant massivement les hallucinations.")

with tab_demo:
    st.header("Démonstration Technique")
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("**B02a : Créer / Mettre à jour l'Index**")
        if st.button("Lancer l'Indexation Vectorielle (FAISS)", use_container_width=True):
            with st.spinner("Indexation en cours..."):
                try:
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    result = subprocess.run(
                        [sys.executable, "B02a_create_vector_db.py"],
                        capture_output=True, text=True, cwd=root_dir, timeout=60
                    )
                    if result.returncode == 0:
                        st.success("Base vectorielle FAISS créée/mise à jour ! (data/faiss_index)")
                    else:
                        st.error("Erreur lors de l'indexation.")
                        st.code(result.stderr)
                except Exception as e:
                    st.error(f"Erreur : {e}")

    with col2:
        st.info("**B02b : Tester dans le Terminal (Optionnel)**")
        st.markdown("*Testez la version 'brute' interactive en console :*")
        
        if st.button("🚀 Ouvrir B02b_query_rag.py (Terminal)"):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bat_file = os.path.join(root_dir, "run_B02b.bat")
            try:
                subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
                st.toast("Terminal RAG lancé !")
            except Exception as e:
                st.error(f"Erreur : {e}")

    st.divider()
    st.subheader("Interface RAG Interactive (B02c)")

    if "b02_process" not in st.session_state:
        st.session_state.b02_process = None

    col_start, col_stop = st.columns(2)
    with col_start:
        if st.button("▶️ Démarrer l'application RAG", type="primary", use_container_width=True) and st.session_state.b02_process is None:
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            print("[Demo_Cockpit] Lancement de l'application Streamlit B02c en arrière-plan...")
            process = subprocess.Popen(
                [sys.executable, "-m", "streamlit", "run", "B02c_streamlit_rag.py", "--server.port", "8503", "--server.headless", "true"],
                cwd=root_dir,
                stdout=subprocess.DEVNULL, # Muter les logs classiques Streamlit pour éviter le spam, on redirigera plus tard si besoin.
                stderr=subprocess.DEVNULL
            )
            st.session_state.b02_process = process
            time.sleep(3) # Attendre que le serveur démarre
            st.rerun()

    with col_stop:
        if st.button("⏹️ Arrêter", use_container_width=True) and st.session_state.b02_process is not None:
            print("[Demo_Cockpit] Arrêt de l'application Streamlit B02c...")
            st.session_state.b02_process.terminate()
            st.session_state.b02_process = None
            st.rerun()

    if st.session_state.b02_process is not None:
        st.success("Application B02c en cours d'exécution sur le port 8503.")
        st.components.v1.iframe("http://localhost:8503", height=700, scrolling=True)
    else:
        st.warning("L'application RAG est actuellement arrêtée.")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le code de l'interface graphique (B02c) masque la complexité de LangChain sous le capot.")
    
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Extrait B02a (Indexation)
        file_path_b02a = os.path.join(root_dir, "B02a_create_vector_db.py")
        with open(file_path_b02a, "r", encoding="utf-8") as f:
            lines_a = f.readlines()
            
        st.subheader("1. L'Indexation dans la base FAISS (B02a)")
        st.markdown("**Le découpage (Chunking) et la Vectorisation :**")
        snippet_a1 = "".join(lines_a[51:67])
        st.code(snippet_a1, language="python")
        
        st.markdown("**La sauvegarde dans FAISS :**")
        snippet_a2 = "".join(lines_a[71:79])
        st.code(snippet_a2, language="python")

        # Extrait B02c (Recherche)
        st.divider()
        file_path_b02c = os.path.join(root_dir, "B02c_streamlit_rag.py")
        with open(file_path_b02c, "r", encoding="utf-8") as f:
            lines_c = f.readlines()
            
        st.subheader("2. La Recherche et Génération (RAG) (B02c)")
        st.markdown("**La récupération sémantique et la construction du contexte :**")
        snippet_c = "".join(lines_c[101:114])
        st.code(snippet_c, language="python")

    except FileNotFoundError:
        st.error("Les fichiers B02a ou B02c sont introuvables.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Le processus illustré ici (Chunking -> Embedding -> FAISS -> LLM) est le standard absolu de l'IA d'entreprise aujourd'hui.

**Défis SI :**
* **Mise à l'échelle (Scale) :** FAISS est excellent localement (ce que nous utilisons), mais en entreprise sur des millions de documents, on optera pour des bases vectorielles dédiées (Pinecone, Qdrant) ou l'extension vectorielle de bases existantes (pgvector pour PostgreSQL, Azure AI Search).
* **Gestion des Droits (RBAC) :** Le RAG ne doit pas permettre à un employé de chercher dans un document RH s'il n'en a pas les droits. La recherche vectorielle doit donc être pré-filtrée par les habilitations de l'utilisateur actif.
* **Complexité des Formats :** Récupérer du texte brut comme dans l'étape B01 est facile. Extraire le texte de PDF scannés, de tableaux Excel ou de présentations PPTX demande des pipelines d'extraction (ETL / OCR) beaucoup plus lourds.
    
</div>
""", unsafe_allow_html=True)
