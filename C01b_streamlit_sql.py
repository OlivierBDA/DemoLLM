import streamlit as st
import sqlite3
import pandas as pd
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==============================================================================
# Demo LLM - Phase C : Étape 1b : Interface SQL (Streamlit)
# ==============================================================================
# ASPECT CLÉ : Cette étape démontre la capacité du LLM à comprendre une structure
# de données relationnelle et à générer du code SQL valide.
# ==============================================================================

DB_PATH = os.path.join("data", "marvel_data.db")

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE SQL & LLM
# ------------------------------------------------------------------------------

def get_llm():
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0
    )

def get_db_schema():
    """Récupère la structure des tables pour aider le LLM."""
    if not os.path.exists(DB_PATH):
        return "Erreur : Base de données introuvable."
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Récupération du DDL des tables principales. 
    # Transmis au LLM pour qu'il puisse comprendre la structure de la base de données.
    schema = ""
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
    for table_name, sql in cursor.fetchall():
        schema += f"\nTable: {table_name}\nSchema: {sql}\n"
    
    conn.close()
    return schema

def execute_query(query: str):
    """Exécute une requête SQL et retourne les résultats dans un DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)

def generate_sql(llm, question: str, schema: str):
    """Transforme une question en SQL."""
    print(f"\n[ENTRY] Traduction de la question : '{question[:50]}...'")
    
    system_prompt = f"""Tu es un expert SQL. Ta tâche est de convertir des questions en requêtes SQLite valides.
    Utilise UNIQUEMENT les tables ci-dessous :
    {schema}
    
    CONSIGNES :
    - Réponds UNIQUEMENT avec la requête SQL. Aucun texte avant ou après.
    - Pas de blocs de code markdown (pas de ```sql).
    - Sois précis dans les jointures.
    - Si tu ne peux pas répondre avec les tables, réponds 'ERREUR: Inconnu'.
    """
    
    print("  [LLM CALL] Envoi du schéma et de la question au LLM...")
    response = llm.invoke([
        SystemMessage(content=system_prompt),
        HumanMessage(content=question)
    ])
    
    sql = response.content.strip().replace("```sql", "").replace("```", "").strip()
    print(f"[SQL GENERATED] {sql}")
    return sql

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Marvel SQL Explorer", page_icon="🗄️", layout="wide")

st.title("🛡️ Demo LLM - Étape 7 : Text-to-SQL")

# ENCART D'INFORMATION
with st.expander("ℹ️ À propos de cette étape : RAG Structuré", expanded=False):
    st.markdown("""
    **Concept :**
    Contrairement au RAG vectoriel (Step 5/6), ici le LLM interroge une base de données **relationnelle**. 
    Il traduit votre intention en langage SQL technique.
    
    **Schema de la démo :**
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question", shape=ellipse];
            LLM [label="LLM (SQL Expert)", style=filled, color=orange];
            DB [label="SQLite\\n(heroes, movies)", style=filled, color=palegreen];
            Res [label="Tableau de données", style=filled, color=lightblue];
            
            Q -> LLM [label="Natural Language"];
            LLM -> DB [label="SQL Query"];
            DB -> Res [label="Pandas DF"];
        }
    ''')
    st.markdown("""
    **Comment tester :**
    1. *"Quels sont les héros les plus intelligents ?"*
    2. *"Quel est le box-office total de tous les films ?"*
    3. *"Quels sont les films où apparaît Iron Man ?"*
    """)

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle recherche", use_container_width=True):
        st.session_state.sql_history = []
        st.rerun()

# Historique
if "sql_history" not in st.session_state:
    st.session_state.sql_history = []

# Affichage des résultats précédents
for entry in st.session_state.sql_history:
    with st.chat_message("user"): st.markdown(entry["question"])
    with st.chat_message("assistant"):
        st.code(entry["sql"], language="sql")
        st.table(entry["data"])

# Input
if prompt := st.chat_input("Posez une question sur les données Marvel (ex: top 3 héros par force)"):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        llm = get_llm()
        schema = get_db_schema()
        
        with st.spinner("Génération de la requête SQL..."):
            sql_query = generate_sql(llm, prompt, schema)
        
        if sql_query.startswith("ERREUR"):
            st.error("Désolé, je ne peux pas répondre à cette question avec les données disponibles.")
        else:
            st.code(sql_query, language="sql")
            
            with st.spinner("Exécution de la requête..."):
                print(f"[ACTION] Exécution SQL sur SQLite...")
                df, error = execute_query(sql_query)
                
            if error:
                st.error(f"Erreur SQL : {error}")
                print(f"[ERROR] {error}")
            else:
                print(f"[DATA] {len(df)} lignes récupérées.")
                if df.empty:
                    st.info("Aucun résultat trouvé dans la base.")
                else:
                    st.table(df)
                    # Sauvegarde pour l'historique
                    st.session_state.sql_history.append({
                        "question": prompt,
                        "sql": sql_query,
                        "data": df
                    })

if __name__ == "__main__":
    # Petit check de la DB au lancement
    if not os.path.exists(DB_PATH):
        st.warning("⚠️ La base de données `marvel_data.db` est introuvable. Veuillez lancer l'étape 07a d'abord.")
