import streamlit as st

st.set_page_config(page_title="Marvel LLM Demo", page_icon="🦸", layout="wide")

# Injection CSS globale - Charte Gulf Academy (Stitch)
st.markdown("""
<style>
/* Sidebar "No-Line" Rule & Background */
[data-testid="stSidebar"] {
    background-color: #eceef0 !important;
    border-right: none !important;
}

/* Hide native Streamlit separation lines */
header {
    border-bottom: none !important;
    box-shadow: none !important;
}

/* Tabs "GT" Style */
[data-baseweb="tab-list"] {
    gap: 1rem;
}
[data-baseweb="tab"] {
    padding-bottom: 0px !important;
    padding-top: 10px !important;
}
[data-baseweb="tab"] [aria-selected="true"] {
    border-bottom: 3px solid #fd8600 !important;
    color: #051b3b !important;
}

/* Global container styling */
div.ouverture-si-box {
    background-color: #bee9ff;
    padding: 1.5rem;
    border-radius: 8px;
    color: #051b3b;
    margin-top: 1rem;
    border-left: 5px solid #0d6683;
}

/* Code Blocks Styling */
[data-testid="stCode"] {
    background-color: #eef7fc !important;
    border-radius: 8px !important;
}
[data-testid="stCode"] pre {
    background-color: transparent !important;
}
[data-testid="stCode"] code {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

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
        ],
        "Phase E : Model Context Protocol": [
            st.Page("cockpit_pages/e01_demo.py", title="E01 : Contrat (Discovery)", icon="🔌"),
            st.Page("cockpit_pages/e02_demo.py", title="E02 : Agent Connecté", icon="🤖"),
            st.Page("cockpit_pages/e03_demo.py", title="E03 : Ressources", icon="📚"),
            st.Page("cockpit_pages/e04_demo.py", title="E04 : Modèles (Templates)", icon="🧩"),
            st.Page("cockpit_pages/e05_demo.py", title="E05 : Suivi (Progress)", icon="⏳"),
            st.Page("cockpit_pages/e06_demo.py", title="E06 : Notifications", icon="🔔"),
            st.Page("cockpit_pages/e07_demo.py", title="E07 : Prompts", icon="📝"),
        ],
        "Phase F : Skills & Frameworks": [
            st.Page("cockpit_pages/f01_demo.py", title="F01 : Expertise & Skills", icon="🛡️"),
            st.Page("cockpit_pages/f02_demo.py", title="F02 : Discovery & Routing", icon="🧠"),
        ],
        "Phase G : Protocole A2A (Multi-Agents)": [
            st.Page("cockpit_pages/g01_demo.py", title="G01 : Découverte A2A", icon="📡"),
            st.Page("cockpit_pages/g02_demo.py", title="G02 : Chat A2A", icon="💬"),
            st.Page("cockpit_pages/g03_demo.py", title="G03 : Chaîne A2A", icon="🔗"),
        ],
        "Phase H : Utilitaires": [
            st.Page("cockpit_pages/h01_demo.py", title="H01 : Monitoring (Phoenix)", icon="👁️"),
        ]
    }

    pg = st.navigation(pages)
    pg.run()
    
except AttributeError:
    st.error("Cette architecture nécessite Streamlit 1.36+. Mettez à jour Streamlit (`pip install --upgrade streamlit`) pour utiliser `st.navigation`.")
