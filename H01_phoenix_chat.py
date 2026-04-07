import streamlit as st
import os
from dotenv import load_dotenv

# Langchain & OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# Instrumentation Phoenix
import phoenix as px
from openinference.instrumentation.langchain import LangChainInstrumentor

# =====================================================================
# SECTION 1 : Core Logic (Backend / LLM / Instrumenting)
# =====================================================================

load_dotenv()

# Configurer l'instrumentation Phoenix via le collector local
import os
from phoenix.otel import register

os.environ["PHOENIX_PROJECT_NAME"] = "H01_phoenix_chat"
tracer_provider = register(endpoint="http://localhost:6006/v1/traces")
LangChainInstrumentor().instrument(tracer_provider=tracer_provider)

def get_llm():
    return ChatOpenAI(
        model=os.getenv("LLM_MODEL", "gpt-4o-mini"),
        api_key=os.getenv("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),
        temperature=0.7
    )

def generate_response(messages_history):
    llm = get_llm()
    print(f"\n[PHOENIX CHAT] 🤖 Envoi de la requête au LLM (Trace envoyée à Phoenix)...")
    return llm.invoke(messages_history)

# =====================================================================
# SECTION 2 : User Interface (Streamlit)
# =====================================================================

st.set_page_config(page_title="H01 Chat instrumenté", layout="centered")

st.markdown("### 💬 Mode Conversation")
st.info("Posez une question. Les traces seront envoyées à Phoenix (voir l'autre panneau).")

if "h01_messages" not in st.session_state:
    st.session_state.h01_messages = [
        SystemMessage(content="Tu es un assistant utile. Fais des réponses extrêmement synthétiques en 1 seule et unique phrase."),
        AIMessage(content="Bonjour ! Je suis connecté au serveur Phoenix. Posez-moi une question.")
    ]

# Affichage des messages (on ignore le SystemMessage pour l'UI)
for msg in st.session_state.h01_messages:
    if isinstance(msg, SystemMessage):
        continue
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# Input utilisateur
if prompt := st.chat_input("Votre message..."):
    # Ajout du message user
    user_msg = HumanMessage(content=prompt)
    st.session_state.h01_messages.append(user_msg)
    
    with st.chat_message("user"):
        st.markdown(prompt)
        
    with st.chat_message("assistant"):
        with st.spinner("Réflexion et traçage..."):
            response = generate_response(st.session_state.h01_messages)
            st.markdown(response.content)
            
    st.session_state.h01_messages.append(AIMessage(content=response.content))
