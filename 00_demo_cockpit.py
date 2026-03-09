import streamlit as st

st.set_page_config(page_title="Marvel LLM Demo", page_icon="🦸", layout="wide")

try:
    # L'API st.navigation permet de créer une application multi-pages sans contrainte de dossiers
    # ou de renommage de fichiers complexes.
    pages = {
        "Introduction": [
            st.Page("cockpit_pages/home.py", title="Accueil", icon="🏠"),
        ],
        "Phase A : Fondations": [
            st.Page("cockpit_pages/a01_demo.py", title="A01 : API Simple", icon="1️⃣"),
            st.Page("cockpit_pages/a02_demo.py", title="A02 : Chat Terminal", icon="2️⃣"),
            st.Page("cockpit_pages/a03_demo.py", title="A03 : Streamlit Chat", icon="3️⃣"),
        ],
        "Phase B : RAG & Agent": [
            st.Page("cockpit_pages/b01_demo.py", title="B01 : Concept Data Gen", icon="💾"),
            st.Page("cockpit_pages/b02_demo.py", title="B02 : FAISS & RAG", icon="📚"),
            st.Page("cockpit_pages/b03_demo.py", title="B03 : Routage LangGraph", icon="🧭"),
        ],
        "Phase C : Base SQL & Gouvernance": [
            st.Page("cockpit_pages/c01_demo.py", title="C01 : Text-To-SQL", icon="🗄️"),
            st.Page("cockpit_pages/c02_demo.py", title="C02 : Agent Data Steward", icon="🏛️"),
        ],
        "Phase D : Agents Avancés & IA": [
            st.Page("cockpit_pages/d01_demo.py", title="D01 : Outils (Tool Calling)", icon="🛠️"),
            st.Page("cockpit_pages/d02_demo.py", title="D02 : Visualisations Dynamiques", icon="📊"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
    
except AttributeError:
    st.error("Cette architecture nécessite Streamlit 1.36+. Mettez à jour Streamlit (`pip install --upgrade streamlit`) pour utiliser `st.navigation`.")
