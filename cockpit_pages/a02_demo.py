import streamlit as st
import os
import subprocess

st.title("Étape A02 : Chat Terminal")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Concept et Explication")
    st.markdown('''
**Objectif : Introduire la notion de "Mémoire" (Contexte) dans une conversation.**

Dans l'étape précédente, le modèle oubliait la question précédente. Ici, nous conservons la liste de tous les messages échangés (Utilisateur et IA) pour que le LLM ait le "contexte" complet de la discussion en cours.
    ''')
    st.info("💡 Sans certitude du contexte, une IA ne peut pas répondre à la question 'Et lui ?' après avoir parlé de Tony Stark.")
    
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            History [label="Historique (Liste de messages)", style=dashed, color=grey];
            LLM [label="LLM (OpenAI/Gemini)", style=filled, color=orange];
            
            User -> History [label="Nouveau Message"];
            History -> LLM [label="Historique Complet"];
            LLM -> User [label="RéponseContextualisée"];
            LLM -> History [label="Sauvegarde Réponse"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.info("*Ce programme est une application terminal interactive (boucle infinie). Pour ne pas bloquer cette interface, il s'ouvrira dans un terminal dédié externe.*")
    
    if st.button("🚀 Ouvrir A02_chat_terminal.py dans un Terminal", type="primary"):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bat_file = os.path.join(root_dir, "run_A02.bat")
        
        try:
            subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
            st.success("Terminal interactif externe lancé !")
        except Exception as e:
            st.error(f"Impossible de lancer le terminal : {e}")
    

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Voici les extraits clés qui gèrent l'accumulation de l'historique (lignes 35, 56 et 69) :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "A02_chat_terminal.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        st.markdown("**1. Initialisation de la mémoire avec le contexte système :**")
        snippet1 = "".join(lines[33:39])
        st.code(snippet1, language="python")

        st.markdown("**2. Ajout des messages Utilisateur et IA dans la boucle :**")
        snippet2 = "".join(lines[53:70])
        st.code(snippet2, language="python")

    except FileNotFoundError:
        st.error("Fichier A02_chat_terminal.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Cette logique d'accumulation d'historique (passer l'entièreté de la conversation au modèle à chaque fois) est le cœur brut de tous les Copilotes et Chatbots.

**Prudence SI :**
* **Limites de Tokens :** La fenêtre de contexte d'un LLM n'est pas infinie. En entreprise, un historique trop long va générer des erreurs, augmenter drastiquement la latence et coûter très cher (facturation au token).
* **Solution :** Il faut mettre en place des stratégies de "fenêtrage" (garder uniquement les *N* derniers messages) ou de "résumé dynamique" (le LLM résume régulièrement la conversation pour compresser la mémoire).
    
</div>
""", unsafe_allow_html=True)
