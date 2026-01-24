import os
import streamlit as st
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Étape 3 : Interface Graphique (Streamlit)
# ==============================================================================
# Ce programme offre une interface web professionnelle pour la conversation.
# ASPECT CLÉ : Séparation de la logique métier (LLM) et de l'interface (UI).
# Utilisation du streaming pour une expérience utilisateur fluide.
# ==============================================================================

# ------------------------------------------------------------------------------
# LOGIQUE MÉTIER : Interaction avec le LLM
# ------------------------------------------------------------------------------
def get_llm_chain():
    """Initialise et retourne l'objet LLM configuré."""
    load_dotenv()
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7,
        streaming=True
    )

def process_chat(llm, messages):
    """Envoie les messages au LLM et retourne un générateur pour le streaming."""
    return llm.stream(messages)

# ------------------------------------------------------------------------------
# INTERFACE UTILISATEUR : Streamlit
# ------------------------------------------------------------------------------
def main():
    st.set_page_config(page_title="Demo LLM - Marvel Chat", page_icon="🦸", layout="centered")

    # Sidebar pour les informations techniques (aspect pro)
    with st.sidebar:
        st.title("⚙️ Configuration")
        load_dotenv()
        st.info(f"**Modèle :** {os.getenv('LLM_MODEL')}\n\n**Endpoint :** {os.getenv('LLM_BASE_URL')}")
        
        if st.button("🗑️ Nouvelle Conversation", use_container_width=True):
            st.session_state.messages = [
                SystemMessage(content="Tu es un assistant expert de l'univers Marvel. Tu fais des réponses courtes et concises.")
            ]
            st.rerun()

    st.title("🦸 Demo LLM : Assistant Marvel")
    st.markdown("---")

    # Initialisation de l'historique dans la session streamlit
    if "messages" not in st.session_state:
        st.session_state.messages = [
            SystemMessage(content="Tu es un assistant expert de l'univers Marvel. Tu fais des réponses courtes et concises.")
        ]

    # Affichage des messages existants (en ignorant le message système)
    for msg in st.session_state.messages:
        if isinstance(msg, HumanMessage):
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            with st.chat_message("assistant"):
                st.markdown(msg.content)

    # Entrée utilisateur
    if prompt := st.chat_input("Posez votre question sur les super-héros..."):
        # 1. Affichage immédiat du message utilisateur
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 2. Ajout à l'historique session
        st.session_state.messages.append(HumanMessage(content=prompt))

        # 3. Réponse du LLM avec streaming
        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                llm = get_llm_chain()
                # ASPECT CLÉ : On passe la liste de messages pour la continuité
                for chunk in process_chat(llm, st.session_state.messages):
                    full_response += chunk.content
                    response_placeholder.markdown(full_response + "▌")
                
                response_placeholder.markdown(full_response)
                
                # 4. Ajout de la réponse complète à l'historique
                st.session_state.messages.append(AIMessage(content=full_response))
                
            except Exception as e:
                st.error(f"Erreur : {e}")

if __name__ == "__main__":
    main()
