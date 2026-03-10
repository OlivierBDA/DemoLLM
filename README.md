# 🦸 Demo LLM : Le Voyage de l'Apprenti AI-Agent

Bienvenue dans ce dépôt pédagogique conçu pour explorer et démontrer les capacités des Large Language Models (LLM) à travers un cas d'usage fil rouge ludique : l'univers **Marvel**.

Ce projet est conçu pour être **didactique** et **progressif**. Il part d'un simple appel API pour aboutir à une architecture d'entreprise complexe utilisant des agents autonomes et le protocole **MCP (Model Context Protocol)**.

---

## 🏗️ Architecture & Philosophie : Le Cockpit Central

Le cœur de cette démonstration repose désormais sur le **Demo Cockpit**, une application Streamlit unifiée agissant comme un portail central d'apprentissage.
Plutôt que de lancer des dizaines de scripts manuellement, le Cockpit orchestre et lance tous les composants nécessaires.

*   **Séparation Logic/UI** : Distinguo clair entre le cerveau (Serveurs FastAPI, MCP) et les muscles (Streamlit Cockpit).
*   **Documentation Intégrée** : Chaque page du Cockpit contient un onglet "Concept" qui vulgarise la démonstration via du texte et des schémas d'architecture dynamiques.
*   **Indépendance** : Le Cockpit gère le lancement des services sous-jacents (bases de données vectorielles, serveurs Python etc.) dans des terminaux dédiés pour le parallélisme.

---

## 🚀 Guide de Démarrage Rapide

C'est très simple grâce à notre architecture unifiée :

1.  **Installation** :
    ```bash
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    ```
2.  **Configuration** :
    Créez un fichier `.env` :
    ```env
    LLM_MODEL=gpt-4o-mini
    LLM_API_KEY=sk-...
    ```
3.  **Lancement du Cockpit (Point d'Entrée Unique)** :
    ```bash
    streamlit run 00_demo_cockpit.py
    ```

👉 *Toutes les démos et explications ci-dessous sont accessibles et exécutables directement depuis l'interface de ce Cockpit.*

---

## 🪜 Détail des Phases (Explorables via le Cockpit)

### Phase A : Les Fondations (Prompting & Mémoire)
*Objectif : Comprendre comment envoyer une requête et gérer une conversation.*

*   **A01 : Simple API**
    Le point de départ. Une question, une réponse brute via l'API.
    ![Question et Réponse](doc/A01_simple_api_Question_et_reponse.png)

*   **A02 : Chat Terminal**
    Ajout de la mémoire. Le LLM se souvient des échanges précédents dans une boucle de chat en ligne de commande.
    ![Conversation Terminal](doc/A02_chat_terminal_conversation.png)

*   **A03 : Streamlit Chat**
    Passage au Web. Une interface de chat moderne, fluide et persistante.
    ![Interface Streamlit](doc/A03_streamlit_chat_conversation.png)
    *Architecture :*
    ![Diagramme A03](doc/A03_streamlit_chat_diagramme.png)

---

### Phase B : Connaissance & RAG (Retrieval Augmented Generation)
*Objectif : Connecter le LLM à vos propres documents (Fiches héros Marvel).*

*   **B01/B02 : RAG (Base de Données Vectorielle)**
    Le LLM "lit" des documents texte et répond en s'appuyant sur ces connaissances tierces.
    ![RAG en action](doc/B02_query_rag_conversation.png)
    *Fonctionnement :*
    ![Diagramme RAG](doc/B02_query_rag_diagramme.png)

*   **B03 : LangGraph Routing**
    Introduction à la logique d'Agent. Un routeur intelligent décide si la question nécessite le RAG ou une réponse directe.
    ![Routage Domaine](doc/B03_langgraph_routing_branche_domaine.png)
    ![Routage Hors-Domaine](doc/B03_langgraph_routing_branche_hors_domaine.png)
    *Logique du graphe :*
    ![Diagramme Routage](doc/B03_langgraph_routing_diagramme.png)

---

### Phase C : Données Structurées (Text-to-SQL)
*Objectif : Interroger des bases de données SQL d'entreprise en langage naturel.*

*   **C01 : Streamlit SQL**
    Le LLM convertit une demande ("Quels films pour Thor ?") en requête SQL complexe.
    ![Tableau SQL](doc/C01_streamlit_sql_tableau.png)
    *Flux :*
    ![Diagramme SQL](doc/C01_streamlit_sql_diagramme.png)

*   **C02 : Data Catalog Explorer**
    Le LLM explore d'abord un catalogue de métadonnées pour localiser l'information avant d'agir.
    ![Tableau Catalogue](doc/C02_streamlit_catalog_tableau.png)
    *Flux :*
    ![Diagramme Catalogue](doc/C02_streamlit_catalog_diagramme.png)

---

### Phase D : Action & Outils (Tool Calling)
*Objectif : Transformer le LLM en Agent capable d'agir sur le monde réel.*

*   **D01 : Agent avec Outils (Calculateur de Combat)**
    L'agent décide d'appeler un microservice backend externe (`D01a`) pour obtenir une donnée technique.
    ![Tool Calling](doc/D01_streamlit_tools_conversation.png)
    *Séquence :*
    ![Diagramme Tools](doc/D01_streamlit_tools_diagramme.png)

*   **D02 : Data Visualization Agent**
    L'agent génère dynamiquement du code JSON pour configurer un graphique de visualisation (Streamlit Charts) à la volée.
    ![Graphique](doc/D02_streamlit_charts_graphique.png)
    *Processus :*
    ![Diagramme Charts](doc/D02_streamlit_charts_diagramme.png)

---

### Phase E : Industrialisation avec MCP (Model Context Protocol)
*Objectif : Standardiser l'écosystème IA via protocole ouvert.*

*   **E01 : Discovery MCP (Outils dynamiques)**
    Le client découvre les capacités du serveur (outils) dynamiquement à la connexion.
    ![Discovery UI](doc/E01_MCP_ToolDiscovery_streamlit.png)
    *Flux :*
    ![Diagramme E01](doc/E01_MCP_ToolDiscovery_graphique.png)

*   **E02 : Agent Autonome MCP**
    Un agent orchestré par LangChain utilise les outils standardisés MCP.
    ![Agent UI](doc/E02_MCP_ToolAgentUse_streamlit.png)
    *Flux :*
    ![Diagramme E02](doc/E02_MCP_ToolAgentUse_graphique.png)

*   **E03 : Ressources MCP (Accès aux fichiers)**
    Lecture de fichiers via des URIs et le protocole standardisé.
    ![Resources UI](doc/E03_MCP_Resources_streamlit.png)
    *Flux :*
    ![Diagramme E03](doc/E03_MCP_Resources_graphique.png)

*   **E04 : Prompt Templates MCP**
    Utilisation de modèles paramétrables partagés par le serveur.
    ![Templates UI](doc/E04_MCP_ResourceTemplate_streamlit.png)
    *Flux :*
    ![Diagramme E04](doc/E04_MCP_ResourceTemplate_graphique.png)

*   **E05 : Async Monitoring & Progress MCP**
    Suivi de tâches longues asynchrones avec barres de progression temps réel.
    ![Progress UI](doc/E05_MCP_Async_streamlit.png)
    *Flux :*
    ![Diagramme E05](doc/E05_MCP_Async_graphique.png)

*   **E06 : Notifications Temps Réel (Server Push)**
    Le serveur pousse une notification de changement de données automatiquement aux clients.
    ![Notification UI](doc/E06_MCP_notification_maj.png)
    *Architecture :*
    ![Graphique E06](doc/E06_MCP_notification_graphique.png)

*   **E07 : Prompts MCP (Gabarits Côté Serveur)**
    Le serveur fournit des contextes pré-formatés (fichiers + instructions) prêts à être consommés par le LLM du client.
    ![Prompts UI](doc/E07_MCP_Prompts_streamlit.png)
    *Flux :*
    ![Diagramme E07](doc/E07_MCP_Prompts_graphique.png)

---

## 🛠️ Outils & Méthodologie
Ce projet a été modernisé avec l'assistance de **Google Antigravity** pour la structuration, le requêtage asynchrone et l'UI premium.
Le code utilise les derniers standards (LangChain, LangGraph, protocoles MCP, SSE Streams) pour illustrer une conception moderne.
