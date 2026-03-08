import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Phase A : Étape 3 : Interface Graphique (Streamlit)
# ==============================================================================
# Ce programme offre une interface web professionnelle pour la conversation.
# ASPECT CLÉ : Séparation stricte entre le "Core LLM" et l'interface "Streamlit".
# ==============================================================================
# python -m streamlit run 03_streamlit_chat.py

# ------------------------------------------------------------------------------
# SECTION 1 : LOGIQUE COEUR LLM (LangChain)
# ------------------------------------------------------------------------------

def init_llm():
    """Charge la config et initialise le client LLM agnostique."""
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7,
        streaming=True
    )

def get_session_starter_messages():
    """Définit le contexte initial de la conversation."""
    return [
        SystemMessage(content="Tu es un assistant expert de l'univers Marvel. Tu fais des réponses courtes et concises.")
    ]

def add_message_to_history(history, role, text):
    """Ajoute dynamiquement un message à la structure de données LangChain."""
    if role == "user":
        history.append(HumanMessage(content=text))
    elif role == "assistant":
        history.append(AIMessage(content=text))
    return history

def get_llm_response_stream(llm, message_history):
    """Déclenche l'appel au LLM et retourne le flux de streaming (générateur)."""
    # ASPECT CLÉ : C'est ici que la continuité se fait en envoyant l'historique complet.
    return llm.stream(message_history)


# ------------------------------------------------------------------------------
# SECTION 2 : INTERFACE UTILISATEUR (Streamlit)
# ------------------------------------------------------------------------------

def configure_page():
    """Configure les méta-données et le style de la page."""
    st.set_page_config(page_title="Demo LLM - Marvel UI", page_icon="🦸", layout="wide")
    st.title("🦸 Demo LLM : Assistant Marvel")
    
    # L'encart d'information a été déplacé dans le Cockpit principal (onglet Concept).
    st.markdown("---")

def render_sidebar():
    """Affiche les paramètres techniques dans la barre latérale."""
    with st.sidebar:
        st.title("⚙️ Configuration")
        load_dotenv()
        st.info(f"**Modèle :** {os.getenv('LLM_MODEL')}\n\n**Endpoint :** {os.getenv('LLM_BASE_URL')}")
        
        if st.button("🗑️ Nouvelle Conversation", use_container_width=True):
            # Réinitialisation via le Core LLM
            st.session_state.messages = get_session_starter_messages()
            st.rerun()

def render_chat_history():
    """Affiche les messages stockés en ignorant les messages système."""
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

def handle_user_interaction(llm):
    """Gère la saisie utilisateur et la réponse streamée de l'IA."""
    if prompt := st.chat_input("Posez votre question sur les super-héros..."):
        # UI : Affichage utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Core : Mise à jour historique
        st.session_state.messages = add_message_to_history(st.session_state.messages, "user", prompt)

        # UI & Core : Réponse en streaming
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            
            try:
                # Appel au générateur du Core LLM
                for chunk in get_llm_response_stream(llm, st.session_state.messages):
                    full_response += chunk.content
                    placeholder.markdown(full_response + "▌")
                
                placeholder.markdown(full_response)
                
                # Core : Mémorisation de la réponse AI
                st.session_state.messages = add_message_to_history(st.session_state.messages, "assistant", full_response)
                
            except Exception as e:
                st.error(f"Erreur LLM : {e}")

def main():
    # 1. Configuration Initiale
    configure_page()
    render_sidebar()
    
    # 2. Initialisation du State (Core LLM)
    if "messages" not in st.session_state:
        st.session_state.messages = get_session_starter_messages()
    
    # 3. Initialisation du LLM (Core LLM)
    llm_client = init_llm()

    # 4. Rendu de l'interface
    render_chat_history()
    handle_user_interaction(llm_client)

if __name__ == "__main__":
    main()
