# 🦸 Demo LLM : Le Voyage de l'Apprenti AI-Agent

Bienvenue dans ce dépôt pédagogique conçu pour explorer et démontrer les capacités des Large Language Models (LLM) à travers un cas d'usage concret : l'univers **Marvel**.

Ce projet est structuré comme une progression par phases, partant d'un simple appel API pour aboutir à un **Agent Intelligent** utilisant le protocole MCP.

---

## 🏗️ Architecture & Philosophie
Le dépôt est organisé de manière incrémentale par **Phases**. Chaque étape est souvent auto-suffisante pour faciliter la lecture du code et la compréhension des concepts techniques.

**Technologies utilisées :**
- **LangChain** (Orchestration LLM & Tools)
- **LangGraph** (Routage complexe & Orchestration d'états)
- **FastAPI** (Service REST externe)
- **Streamlit** (Interfaces Web)
- **SQLite** (Données structurées)
- **FAISS** (Base de données vectorielle)
- **Model Context Protocol (MCP)** (Standardisation des outils)

---

## 🚀 Guide de Démarrage Rapide

1. **Configuration :** Créez un fichier `.env` à la racine avec les variables LLM.
2. **Installation :** Installez les dépendances via votre gestionnaire Python dans `.venv`.
   ```bash
   pip install langchain langchain-openai langchain-community langgraph streamlit pandas fastapi uvicorn fastembed faiss-cpu mcp
   ```

---

## 🪜 Structure de la Démo

### Phase A : Fondations et Intégration Directe
*   **A01 : Le Premier Appel** (`python A01_simple_api.py`) - Appel direct sans mémoire.
*   **A02 : Conversation en Terminal** (`python A02_chat_terminal.py`) - Introduction de la mémoire.
*   **A03 : Première Interface Graphique** (`streamlit run A03_streamlit_chat.py`) - Migration vers UI Web.

### Phase B : Contextualisation et Données Métier (RAG)
*   **B01 : Génération de Données** (`python B01_generate_data.py`) - Création de fiches .txt.
*   **B02 : Mise en place du RAG** 
    - `python B02a_create_vector_db.py` (Indexation)
    - `streamlit run B02c_streamlit_rag.py` (Interface)
*   **B03 : Routage Intelligent** (`streamlit run B03_langgraph_routing.py`) - Utilisation de LangGraph pour décider du flux.

### Phase C : Données Structurées et Intelligence Relationnelle (SQL)
*   **C01 : Text-to-SQL**
    - `python C01a_setup_marvel_sql.py` (Setup DB)
    - `streamlit run C01b_streamlit_sql.py` (Interface)
*   **C02 : Gouvernance & Catalogue**
    - `python C02a_setup_catalog.py` (Setup Catalog)
    - `streamlit run C02b_streamlit_catalog.py` (Interface)

### Phase D : Interaction et Action (Tool Calling)
*   **D01 : Tool Calling (API REST)**
    - `python D01a_combat_service.py` (Lancement API)
    - `streamlit run D01b_streamlit_tools.py` (Interface Agent)
*   **D02 : Visualisations Dynamiques** (`streamlit run D02_streamlit_charts.py`) - Graphiques générés par l'agent.

### Phase E : Model Context Protocol (MCP)
*   **E01 : Introduction au MCP**
    - `python E01a_mcp_server.py` (Serveur de Ressources/Tools)
    - `streamlit run E01b_streamlit_mcp.py` (Explorateur de capacités)

---

## 🎯 Note pour NotebookLM
Ce dépôt est optimisé pour être analysé par **NotebookLM** afin de reconstruire la logique pédagogique de l'évolution des agents.
