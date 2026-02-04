import streamlit as st
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==============================================================================
# Demo LLM - Étape 8 : SQL Avancé avec Catalogue de Métadonnées
# ==============================================================================
# ASPECT CLÉ : Cette étape montre comment un LLM peut naviguer dans une base
# inconnue en utilisant une couche sémantique (Catalogue de données).
# ==============================================================================

#"Quels sont nos plus grands succès financiers ?" (Test du mapping Succès financier -> Box Office).
#"Liste les films où Iron Man est présent." (Test de la jointure via le catalogue).
#"Classe les héros par endurance." (Test des caractéristiques métier).

DB_PATH = os.path.join("data", "marvel_data.db")

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE CŒUR (Analyse et Gouvernance)
# ------------------------------------------------------------------------------

class DataCatalogAgent:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )

    def get_global_catalog(self):
        """Récupère la description globale de toutes les tables."""
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT * FROM table_catalog", conn)
        conn.close()
        return df.to_string(index=False)

    def get_detailed_catalog(self, table_name):
        """Récupère la documentation technique et métier d'une table spécifique."""
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM column_catalog WHERE table_name = '{table_name}'", conn)
        conn.close()
        return df.to_string(index=False)

    def discover_table(self, question):
        """ÉTAPE 1 : Identification de la table via le catalogue global."""
        print(f"\n[ENTRY] Phase de Découverte : '{question[:40]}...'")
        catalog = self.get_global_catalog()
        
        system_instructions = f"""Tu es un Data Steward. En utilisant UNIQUEMENT le catalogue global ci-dessous, identifie quelle table technique est nécessaire pour répondre à la question.
        
        CATALOGUE :
        {catalog}
        
        Réponds UNIQUEMENT avec le nom de la table technique (ex: 'movies'). Si plusieurs sont nécessaires, sépare-les par une virgule."""

        user_question = f"Question de l'utilisateur : {question}\nTable(s) :"
        
        print("  [LLM CALL] Consultation du Catalogue Global...")
        response = self.llm.invoke([
            SystemMessage(content=system_instructions),
            HumanMessage(content=user_question)
        ])
        table_name = response.content.strip().lower()
        print(f"[EXIT] Table(s) identifiée(s) : {table_name}")
        return table_name

    def generate_sql_with_catalog(self, question, table_names):
        """ÉTAPE 2 : Construction du SQL via le catalogue détaillé."""
        print(f"\n[ENTRY] Phase de Raffinement pour : {table_names}")
        
        # On récupère le catalogue de colonnes pour les tables sélectionnées
        context_metadata = ""
        for table in table_names.split(","):
            context_metadata += f"\n--- STRUCTURE DE LA TABLE {table.strip().upper()} ---\n"
            context_metadata += self.get_detailed_catalog(table.strip())
            
        system_instructions = f"""Tu es un expert SQL. Crée une requête SQLite pour répondre à la question en utilisant le catalogue technique/métier ci-dessous.
        
        CATALOGUE DES COLONNES :
        {context_metadata}
        
        AIDE : 
        - Utilise les noms techniques (column_name) pour le SQL.
        - Utilise les business_label pour comprendre la question métier.
        - Respecte les jointures indiquées dans 'relationships' si plusieurs tables sont utilisées."""
        
        user_query = f"Question : {question}\nSQL :"

        print("  [LLM CALL] Génération du SQL basé sur le Catalogue Métier...")
        response = self.llm.invoke([
            SystemMessage(content=system_instructions),
            HumanMessage(content=user_query)
        ])
        sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
        print(f"[EXIT] SQL SQL généré : {sql}")
        return sql

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Marvel Data Governance", page_icon="🏛️", layout="wide")

st.title("🛡️ Demo LLM - Étape 8 : Catalogue & Gouvernance")

# ENCART D'INFORMATION
with st.expander("ℹ️ À propos de cette étape : L'Agent de Gouvernance", expanded=False):
    st.markdown("""
    **Concept : Séparation Métier / Technique**
    Ici, le LLM ne connaît pas les tables au départ. Il doit d'abord consulter un **Catalogue de Données** (Métadonnées) pour "comprendre" où chercher.
    
    **Pourquoi c'est important ?**
    - En entreprise, les noms de tables sont souvent obscurs (ex: `TBL_FIN_01_XYZ`).
    - Le catalogue permet de faire le pont entre "Succès financier" (terme métier) et `box_office_revenue` (nom technique).
    
    **Processus de l'Agent :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question Métier", shape=ellipse];
            CatG [label="Catalogue Global\\n(Exploration)", style=filled, color=orange];
            CatD [label="Catalogue Détail\\n(Contexte)", style=filled, color=palegreen];
            SQL [label="Génération SQL", style=filled, color=lightblue];
            
            Q -> CatG -> CatD -> SQL;
        }
    ''')

# Initialisation
agent = DataCatalogAgent()

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle recherche", use_container_width=True):
        st.session_state.catalog_history = []
        st.rerun()
    st.divider()
    st.caption("Base de données active : `marvel_data.db`")

# Historique
if "catalog_history" not in st.session_state:
    st.session_state.catalog_history = []

for entry in st.session_state.catalog_history:
    with st.chat_message("user"): st.markdown(entry["question"])
    with st.chat_message("assistant"):
        st.info(f"📍 Table identifiée : `{entry['table']}`")
        st.code(entry["sql"], language="sql")
        st.table(entry["data"])

# Input
if prompt := st.chat_input("Posez une question métier (ex: 'Qui sont les héros les plus résistants ?')"):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        # Étape 1 : Découverte
        with st.status("Agent : Consultation du catalogue global...", expanded=True) as status:
            table_name = agent.discover_table(prompt)
            st.write(f"✅ J'ai identifié que votre demande concerne les données de : **{table_name}**")
            
            # Étape 2 : Raffinement & SQL
            st.write("📖 Analyse du catalogue métier détaillé...")
            sql_query = agent.generate_sql_with_catalog(prompt, table_name)
            status.update(label="Analyse terminée !", state="complete", expanded=False)
        
        # Rendu visuel des étapes
        st.info(f"🧭 **Catalogue utilisé** : Table `{table_name.upper()}`")
        st.code(sql_query, language="sql")
        
        # Exécution
        with st.spinner("Exécution de la requête métier..."):
            conn = sqlite3.connect(DB_PATH)
            try:
                df = pd.read_sql_query(sql_query, conn)
                if df.empty:
                    st.warning("Aucun résultat trouvé pour cette recherche.")
                else:
                    st.table(df)
                    st.session_state.catalog_history.append({
                        "question": prompt,
                        "table": table_name,
                        "sql": sql_query,
                        "data": df
                    })
            except Exception as e:
                st.error(f"Erreur d'exécution : {e}")
            finally:
                conn.close()
