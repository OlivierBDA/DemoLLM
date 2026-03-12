import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Phase F : Étape 1 : Injection de Compétences (Skills)
# ==============================================================================
# Ce programme démontre comment modifier le comportement d'un LLM
# en injectant un fichier Markdown (Skill Framework) dans le contexte système.
#
# ASPECT CLÉ : Sans aucune modification de code, l'IA adopte un tout
# nouveau mode de raisonnement métier.
# ==============================================================================

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR LLM (LangChain)
# ------------------------------------------------------------------------------

def init_llm():
    """Charge la config et initialise le client LLM."""
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7,
        streaming=True
    )

def load_skill_content(filename="tactical_analysis.md"):
    """Lit le contenu du fichier de compétence Markdown."""
    filepath = os.path.join(os.path.dirname(__file__), "skills", filename)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "ERREUR : Fichier de Skill introuvable."

def get_session_starter_messages(use_skill=False):
    """Définit le contexte initial, avec ou sans le framework de compétence."""
    if use_skill:
        # Injection de la Skill (Le Framework)
        skill_content = load_skill_content("tactical_analysis.md")
        system_prompt = (
            "Tu es une IA tactique de niveau 7 du SHIELD.\n\n"
            "INSTRUCTIONS STRICTES :\n"
            "Tu dois IMPÉRATIVEMENT appliquer le framework S.T.A.R.K. défini ci-dessous pour CHACUNE de tes réponses.\n"
            "Commence toujours tes réponses par '[PROTOCOL ATA v2.1 ACTIVÉ]'.\n\n"
            f"--- DEBUT DU FRAMEWORK ---\n{skill_content}\n--- FIN DU FRAMEWORK ---\n"
        )
    else:
        # Prompt Générique ("Vanilla")
        system_prompt = "Tu es un assistant virtuel fan de l'univers Marvel. Tu fais des réponses enthousiastes, simples et sans structure particulière."
        
    return [SystemMessage(content=system_prompt)]

def add_message_to_history(history, role, text):
    """Ajoute dynamiquement un message à l'historique."""
    if role == "user":
        history.append(HumanMessage(content=text))
    elif role == "assistant":
        history.append(AIMessage(content=text))
    return history

def get_llm_response_stream(llm, message_history):
    """Déclenche l'appel au LLM et retourne le flux de streaming."""
    return llm.stream(message_history)


# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def configure_page():
    """Configure l'interface."""
    st.set_page_config(page_title="Demo LLM - Skills Injection", page_icon="🛡️", layout="wide")
    st.subheader("🛡️ Demo LLM : Expert Tacticien (SHIELD Protocol)")
    st.markdown("---")

def render_sidebar():
    """Affiche les contrôles dans la barre latérale."""
    with st.sidebar:
        st.title("⚙️ Injection de Compétence")
        st.info("Observez comment l'activation d'un fichier Markdown modifie le comportement.")
        
        # Le Toggle (Bouton d'activation de la Skill)
        skill_active = st.toggle("Activer la Skill : Tactical Analysis", value=st.session_state.get("use_skill", False))
        
        # Si le toggle change, on réinitialise la conversation pour appliquer le nouveau contexte
        if skill_active != st.session_state.get("use_skill", False):
            st.session_state.use_skill = skill_active
            st.session_state.messages = get_session_starter_messages(use_skill=skill_active)
            st.rerun()

        if skill_active:
            st.success("✅ Fichier `tactical_analysis.md` chargé dans le contexte système.")
            with st.expander("Voir le contenu de la Skill"):
                st.markdown(load_skill_content())
        else:
            st.warning("❌ Mode Générique : Assistant classique.")
            
        st.markdown("---")
        if st.button("🗑️ Nouvelle Conversation", use_container_width=True):
            st.session_state.messages = get_session_starter_messages(use_skill=st.session_state.get("use_skill", False))
            st.rerun()

def render_chat_history():
    """Affiche les messages (sans le message système masqué)."""
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

def handle_user_interaction(llm):
    """Gère la boucle de chat."""
    if prompt := st.chat_input("Posez votre question sur une situation tactique (ex: Attaque de Sentinelles à Paris)..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        
        st.session_state.messages = add_message_to_history(st.session_state.messages, "user", prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            
            try:
                for chunk in get_llm_response_stream(llm, st.session_state.messages):
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                st.session_state.messages = add_message_to_history(st.session_state.messages, "assistant", full_response)
                
            except Exception as e:
                st.error(f"Erreur LLM : {e}")

def main():
    configure_page()
    
    # Initialisation de l'état du Toggle
    if "use_skill" not in st.session_state:
        st.session_state.use_skill = False
        
    render_sidebar()
    
    # 2. Initialisation du State (Core LLM)
    if "messages" not in st.session_state:
        st.session_state.messages = get_session_starter_messages(use_skill=st.session_state.use_skill)
    
    # 3. Initialisation du LLM (Core LLM)
    llm_client = init_llm()

    # 4. Rendu de l'interface
    render_chat_history()
    handle_user_interaction(llm_client)

if __name__ == "__main__":
    main()
