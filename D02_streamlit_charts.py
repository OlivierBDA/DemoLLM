import streamlit as st
import sqlite3
import pandas as pd
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# ==============================================================================
# Demo LLM - Phase D : Étape 2 : Visualisations Dynamiques
# ==============================================================================
# ASPECT CLÉ : Cette étape montre comment le LLM peut non seulement extraire
# des données mais aussi choisir la meilleure façon de les représenter.
# ==============================================================================
# Affiche les caractéristiques agrégées de chaque super héros. Chacune des caractéristiques doit avoir une couleur distincte.

DB_PATH = os.path.join("data", "marvel_data.db")

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE DE L'AGENT VISUEL
# ------------------------------------------------------------------------------

class MarvelVisualAgent:
    def __init__(self):
        load_dotenv()
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        self.db_schema = """
        Table: heroes (superhero_name, real_name, intelligence, strength, speed, durability, energy_projection, fighting_skills)
        Table: movies (title, release_year, box_office_revenue_mil)
        Table: hero_appearances (hero_id, movie_id)
        """

    def generate_sql(self, question: str):
        """Phase 1 : Extraction SQL des données."""
        print(f"\n[ENTRY] Phase SQL pour : '{question[:40]}...'")
        system_prompt = f"""Tu es un expert SQL. Convertis la question en SQLite.
        Schéma : {self.db_schema}
        Réponds UNIQUEMENT avec le SQL (pas de markdown)."""
        
        print("  [LLM CALL] Génération de la requête SQL...")
        res = self.llm.invoke([SystemMessage(content=system_prompt), HumanMessage(content=question)])
        sql = res.content.strip().replace("```sql", "").replace("```", "").strip()
        print(f"[SQL] {sql}")
        return sql

    def decide_visualization(self, question: str, data: pd.DataFrame):
        """Phase 2 : Choix du graphique optimal."""
        if data.empty or len(data.columns) < 2:
            return None, "Pas assez de données pour un graphique."
        
        print(f"  [ENTRY] Phase Choix Visuel...")
        system_viz = """Tu es un expert en Data Viz. Analyse la question et les colonnes de données.
        Détermine si un graphique est pertinent.
        Types possibles : 'bar' (comparaisons), 'line' (évolution temporelle), 'area', 'none'.
        
        Réponds en JSON : {"viz_type": "...", "reasoning": "...", "x_axis": "nom_colonne", "y_axis": "nom_colonne_ou_liste"}
        - Pour y_axis, si plusieurs colonnes sont nécessaires (ex: comparer plusieurs stats), fournis une liste ou les noms séparés par des virgules. """
        
        context = f"Question: {question}\nColonnes dispo: {list(data.columns)}"
        
        print("  [LLM CALL] Demande de recommandation visuelle...")
        res = self.llm.invoke([SystemMessage(content=system_viz), HumanMessage(content=context)])
        try:
            viz_config = json.loads(res.content.strip().replace("```json", "").replace("```", ""))
            print(f"[VIZ] Type choisi : {viz_config.get('viz_type')}")
            return viz_config, None
        except:
            return None, "Erreur d'analyse visuelle."

# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Marvel Data Visualizer", page_icon="📊", layout="wide")

st.title("📊 Demo LLM - Étape 10 : Visualisations Dynamiques")

# ENCART D'INFORMATION
# L'encart d'information a été déplacé dans le Cockpit principal (onglet Concept).
st.markdown("---")

# Initialisation
if "visual_agent" not in st.session_state:
    st.session_state.visual_agent = MarvelVisualAgent()
    st.session_state.viz_history = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Nouvelle visualisation", use_container_width=True):
        st.session_state.viz_history = []
        st.rerun()
    st.divider()
    st.caption("Base : `marvel_data.db`")

# Historique
for entry in st.session_state.viz_history:
    with st.chat_message("user"): st.markdown(entry["question"])
    with st.chat_message("assistant"):
        # 1. Graphique d'abord
        if entry["viz"]:
            # Préparation des colonnes Y (cas multi-colonnes)
            y_cols = entry["viz"]["y_axis"]
            if isinstance(y_cols, str) and "," in y_cols:
                y_cols = [c.strip() for c in y_cols.split(",")]

            if entry["viz"]["viz_type"] == "bar":
                st.bar_chart(entry["data"].set_index(entry["viz"]["x_axis"])[y_cols], height=400)
            elif entry["viz"]["viz_type"] == "line":
                st.line_chart(entry["data"].set_index(entry["viz"]["x_axis"])[y_cols], height=400)
            
            # 2. Explication ensuite
            st.info(f"💡 **Raisonnement** : {entry['viz']['reasoning']}")
        
        # 3. Tableau à la fin dans un expander
        with st.expander("📊 Voir les données brutes", expanded=False):
            st.table(entry["data"])

# Input
if prompt := st.chat_input("Demandez une analyse (ex: 'Compare la force et l'intelligence des héros dans un graphique')"):
    st.chat_message("user").markdown(prompt)
    
    with st.chat_message("assistant"):
        agent = st.session_state.visual_agent
        
        with st.status("Analyse en cours...", expanded=True) as status:
            # 1. SQL
            st.write("🔍 Génération de la requête SQL...")
            sql = agent.generate_sql(prompt)
            
            # 2. Exécution
            st.write("⏳ Récupération des données...")
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql_query(sql, conn)
            conn.close()
            
            if df.empty:
                st.error("Aucune donnée trouvée pour cette requête.")
                status.update(label="Échec", state="error")
            else:
                # 3. Choix Visuel
                st.write("🎨 Sélection du meilleur graphique...")
                viz_config, error = agent.decide_visualization(prompt, df)
                status.update(label="Analyse terminée", state="complete", expanded=False)

        if not df.empty:
            # 1. AFFICHAGE : GRAPHIQUE D'ABORD
            if viz_config and viz_config.get("viz_type") != "none":
                try:
                    x = viz_config["x_axis"]
                    y_cols = viz_config["y_axis"]
                    
                    # Gestion multi-colonnes (string -> list)
                    if isinstance(y_cols, str) and "," in y_cols:
                        y_cols = [c.strip() for c in y_cols.split(",")]
                        
                    plot_df = df.set_index(x)
                    
                    if viz_config["viz_type"] == "bar":
                        st.bar_chart(plot_df[y_cols], height=400)
                    elif viz_config["viz_type"] == "line":
                        st.line_chart(plot_df[y_cols], height=400)
                    elif viz_config["viz_type"] == "area":
                        st.area_chart(plot_df[y_cols], height=400)
                    
                    # 2. AFFICHAGE : RAISONNEMENT
                    st.info(f"💡 **Pourquoi ce graphique ?** {viz_config['reasoning']}")
                except Exception as e:
                    st.warning(f"Note : Je n'ai pas pu tracer le graphique (Erreur: {e}).")
            
            # 3. AFFICHAGE : TABLEAU EN DERNIER (COLLAPSÉ)
            with st.expander("📊 Voir les données brutes", expanded=False):
                st.table(df)

            # Sauvegarde historique
            st.session_state.viz_history.append({
                "question": prompt,
                "data": df,
                "viz": viz_config if viz_config and viz_config.get("viz_type") != "none" else None
            })
