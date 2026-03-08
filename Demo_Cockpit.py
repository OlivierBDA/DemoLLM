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
        ]
    }

    pg = st.navigation(pages)
    pg.run()
    
except AttributeError:
    st.error("Cette architecture nécessite Streamlit 1.36+. Mettez à jour Streamlit (`pip install --upgrade streamlit`) pour utiliser `st.navigation`.")
