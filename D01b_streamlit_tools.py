import streamlit as st
import requests
import os
import json
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage, AIMessage
from langchain_core.tools import tool

# ==============================================================================
# Demo LLM - Étape 9B : Agent avec Appel d'Outils Natifs (Native Tool Calling)
# ==============================================================================
# ASPECT CLÉ : Cette étape montre comment le LLM "découvre" un outil et décide
# de l'appeler de lui-même grâce à la fonctionnalité bind_tools.
# ==============================================================================
# .venv\Scripts\python.exe -m streamlit run 09b_streamlit_tools.py
# "Fais s'affronter Hulk et Iron Man !"
# "Qui gagnerait dans un duel entre Thor et Captain America ?"

API_URL = "http://127.0.0.1:8000/simulate_combat"

# ------------------------------------------------------------------------------
# SECTION 1 : DÉFINITION DE L'OUTIL (TOOL)
# ------------------------------------------------------------------------------

@tool
def simulate_combat(hero1_name: str, hero2_name: str) -> str:
    """
    Simule un combat entre deux super-héros Marvel et retourne le résultat JSON.
    Utilisez cet outil dès que l'utilisateur demande qui gagnerait un duel ou un combat.
    """
    print(f"  [EXECUTION TOOL] Appel API pour : {hero1_name} VS {hero2_name}")
    try:
        params = {"hero1": hero1_name, "hero2": hero2_name}
        response = requests.get(API_URL, params=params, timeout=5)
        if response.status_code == 200:
            return json.dumps(response.json(), indent=2)
        return "Erreur : L'API a répondu avec un code d'erreur."
    except Exception as e:
        return f"Erreur : Impossible de contacter le service de combat ({e})"

# ------------------------------------------------------------------------------
# SECTION 2 : CLASSE AGENT AVEC BIND_TOOLS
# ------------------------------------------------------------------------------

class MarvelNativeToolAgent:
    def __init__(self):
        load_dotenv()
        # Initialisation du LLM
        self.llm = ChatOpenAI(
            model=os.getenv("LLM_MODEL"),
            api_key=os.getenv("LLM_API_KEY"),
            base_url=os.getenv("LLM_BASE_URL"),
            temperature=0
        )
        
        # ON LIE L'OUTIL AU MODÈLE
        self.tools = [simulate_combat]
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        self.system_prompt = """Tu es un assistant expert de l'univers Marvel.
        Tu as accès à un outil de simulation de combat. 
        Si l'utilisateur demande un duel ou un combat, utilise l'outil 'simulate_combat'.
        Interprète ensuite les résultats JSON pour faire un récit épique."""

    def run(self, user_input: str):
        print(f"\n[ENTRY] Analyse de la question : '{user_input[:40]}...'")
        
        # Les messages pour l'agent
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=user_input)
        ]

        # 1. PREMIER APPEL : Le LLM décide s'il utilise un outil
        print("  [LLM CALL] Le modèle analyse s'il doit utiliser un outil...")
        ai_msg = self.llm_with_tools.invoke(messages)
        
        # Est-ce qu'il y a des appels d'outils ?
        if ai_msg.tool_calls:
            print(f"[DECISION] Le LLM appelle l'outil : {ai_msg.tool_calls[0]['name']}")
            
            # 2. EXÉCUTION DE L'OUTIL
            tool_call = ai_msg.tool_calls[0]
            # On cherche l'outil correspondant (ici on n'en a qu'un)
            selected_tool = simulate_combat
            
            tool_output = selected_tool.invoke(tool_call["args"])
            
            # On ajoute la décision de l'IA et le résultat de l'outil à l'historique
            messages.append(ai_msg)
            messages.append(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            
            # 3. DEUXIÈME APPEL (HYBRIDE) : Synthèse finale
            print("  [LLM CALL] Le modèle génère le récit final avec les données de l'outil...")
            
            # Pour éviter l'erreur Gemini "thought_signature", on ne renvoie pas l'objet technical tool_call.
            # On crée un nouveau prompt de synthèse qui donne le résultat à l'IA.
            synthesis_prompt = f"""L'utilisateur a demandé un combat. Voici les résultats obtenus via l'outil technique :
            {tool_output}
            
            Rédige un compte-rendu épique de ce combat pour l'utilisateur."""

            final_response = self.llm.invoke([
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=user_input),
                HumanMessage(content=synthesis_prompt)
            ])
            
            return {
                "type": "tool",
                "tool_name": tool_call["name"],
                "args": tool_call["args"],
                "raw_result": tool_output,
                "answer": final_response.content
            }
        else:
            print("[DECISION] Pas d'outil requis. Réponse directe.")
            return {
                "type": "standard",
                "answer": ai_msg.content
            }

# ------------------------------------------------------------------------------
# SECTION 3 : INTERFACE STREAMLIT
# ------------------------------------------------------------------------------

st.set_page_config(page_title="Native Tool Calling", page_icon="🤖", layout="wide")

st.title("🤖 Demo LLM - Phase D : Étape 1b : Agent avec Tool Calling")

with st.expander("ℹ️ À propos de l'Appel d'Outils Natifs", expanded=False):
    st.markdown("""
    **La 'vraie' méthode : bind_tools**
    Ici le LLM possède officiellement une boîte à outils.
    
    1. **Déclaration** : On donne la signature de la fonction au LLM.
    2. **Autonomie** : Le LLM décide seul s'il doit appeler l'outil ou répondre directement.
    3. **Protocole** : Utilisation des structures `tool_calls` et `ToolMessage` de LangChain.
    """)
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Q [label="Question", shape=ellipse];
            LLM [label="LLM (avec bind_tools)", style=filled, color=orange];
            Tool [label="Fonction simulate_combat", style=filled, color=palegreen];
            Resp [label="Réponse Finale", style=filled, color=lightblue];
            
            Q -> LLM;
            LLM -> Tool [label="tool_call"];
            Tool -> LLM [label="tool_result"];
            LLM -> Resp;
        }
    ''')
    st.info("💡 Testez: 'Qui gagnerait entre Iron Man et Thor ?' vs 'Comment tu vas ?'")

# Initialisation
if "native_agent" not in st.session_state:
    st.session_state.native_agent = MarvelNativeToolAgent()
    st.session_state.native_history = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Contrôles")
    if st.button("🆕 Reset", use_container_width=True):
        st.session_state.native_history = []
        st.rerun()
    st.divider()
    st.caption("Méthode : Native `bind_tools` (LangChain)")

# Historique
for msg in st.session_state.native_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
if prompt := st.chat_input("Défiez l'agent ou posez une question..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.native_history.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.status("L'agent réfléchit...", expanded=True) as status:
            result = st.session_state.native_agent.run(prompt)
            
            if result["type"] == "tool":
                st.write(f"🛠️ **Outil utilisé** : `{result['tool_name']}`")
                st.write(f"📝 **Arguments identifiés** : `{result['args']}`")
                with st.expander("Données brutes de l'outil"):
                    st.code(result["raw_result"], language="json")
            
            status.update(label="Analyse terminée", state="complete", expanded=False)

        st.markdown(result["answer"])
        st.session_state.native_history.append({"role": "assistant", "content": result["answer"]})
