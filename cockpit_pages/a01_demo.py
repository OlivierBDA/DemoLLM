import streamlit as st
import subprocess
import os
import sys

st.title("Étape A01 : Simple API")

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
**Objectif :** Comprendre comment envoyer une requête basique à un LLM et récupérer sa réponse.

Ici, nous n'avons pas de "mémoire". Chaque requête est indépendante. C'est l'équivalent d'un appel API REST classique "Stateless". On pose une question simple, le modèle génère une réponse basée uniquement sur cette question.
''')
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            LLM [label="LLM (OpenAI/Gemini)", style=filled, color=orange];
            
            User -> LLM [label="Prompt (Question)"];
            LLM -> User [label="Réponse"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.info("*Pour préserver la nature bas niveau et pédagogique de cette première étape, le script s'ouvrira dans un VRAI terminal externe interactif.*")
    
    if st.button("🚀 Ouvrir A01_simple_api.py dans un Terminal", type="primary"):
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        bat_file = os.path.join(root_dir, "run_A01.bat")
        
        try:
            # shell=True est nécessaire sous Windows pour la commande 'start'
            subprocess.Popen(f'start cmd /k "{bat_file}"', shell=True, cwd=root_dir)
            st.success("Terminal externe lancé !")
        except Exception as e:
            st.error(f"Impossible de lancer le terminal : {e}")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Voici les extraits clés du script source (lignes 27 à 35 puis 50 à 54) :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "A01_simple_api.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Extraction de lignes spécifiques (Lignes 27 à 35) : Initialisation du LLM
        st.markdown("**1. Initialisation de l'objet LLM de LangChain :**")
        snippet_init = "".join(lines[26:35])
        st.code(snippet_init, language="python")

        # Extraction de lignes spécifiques (Lignes 50 à 54) : Invocation
        st.markdown("**2. Préparation du message et Invocation :**")
        snippet_invoke = "".join(lines[49:54])
        st.code(snippet_invoke, language="python")
        
    except FileNotFoundError:
        st.error("Fichier A01_simple_api.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.info('''
**Parallèle Entreprise :**

Dans un Système d'Information, ce type d'appel simple ("One-shot") est parfait pour :
* **Classification :** Trier un ticket de support entrant.
* **Extraction (NER) :** Isoler le numéro de contrat, le nom du client d'un email.
* **Traduction :** Traduction ou reformulation automatique à la volée.

**Avantage :** Pas besoin de mémoire de session (Stateless), très facile et peu coûteux à déployer et mettre à l'échelle.
''')
