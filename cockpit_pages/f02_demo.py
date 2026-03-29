import streamlit as st
import subprocess
import os
import sys
import time
import json

st.title("Étape F02 : Skills Discovery & Contexte Éphémère (Routing)")

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
**Objectif : Démontrer comment un Agent peut découvrir de lui-même des compétences (Skills) à la volée, et les utiliser sans corrompre son historique de conversation.**

Dans la phase précédente (F01), l'utilisateur activait manuellement une Skill. 
Ici, nous passons à une architecture d'entreprise automatisée à **2 Niveaux** ("2-Tier Architecture") recommandée par Anthropic.

**L'Architecture à 2 Niveaux :**
1.  **Niveau 1 (Le Manifeste / Registry) :** L'Agent reçoit au démarrage un résumé très léger de toutes les compétences disponibles (ex: "ID: legal-001, Description: Juridique").
2.  **Niveau 2 (L'Injection Dynamique) :** Si l'Agent juge que la question nécessite une expertise (`Routing`), il utilise un outil (Tool Calling) pour télécharger le lourd fichier Markdown de la Skill.
3.  **Isolation (Contexte Éphémère) :** Le contenu de la Skill n'est utilisé **que pour générer la réponse en cours**, puis il est "oublié". Cela garantit que la Skill "Tacticien" ne viendra pas interférer si la question suivante concerne le droit.
''')

    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            UI [label="Streamlit Chat", style=filled, color=lightblue];
            Manifest [label="manifest.json\\n(Descriptions)", style=filled, color=lightyellow, shape=cylinder];
            LLM [label="Agent LangGraph\\n(Routeur)", style=filled, color=orange];
            SkillA [label="tactical_analysis.md\\n(Guerre)", style=filled, color=lightgreen, shape=note];
            SkillB [label="sokovia_accords.md\\n(Droit)", style=filled, color=lightgreen, shape=note];
            
            Manifest -> LLM [label="Prompt Système Global (Niv 1)"];
            User -> UI [label="Question"];
            UI -> LLM [label="Historique"];
            LLM -> SkillA [label="Tool Call : fetch_skill() si Guerre"];
            LLM -> SkillB [label="Tool Call : fetch_skill() si Droit"];
            SkillA -> LLM [label="Injection Ephémère (Niv 2)"];
            LLM -> UI [label="Réponse finale (Skill oubliée)"];
        }
    ''')


with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Note d'architecture :** La démo ci-dessous est l'application F02 exécutée en tâche de fond (port `8509`).

💡 **Scénario de Test :**
Posez ces questions à la suite pour vérifier l'isolement du contexte :
1. *"Je dois stopper une émeute de mutants à New York"* -> L'agent doit charger la skill Tactique (S.T.A.R.K).
2. *"Est-ce que spider man respecte bien la légalité ?"* -> L'agent doit charger la skill Légale (Accords Sokovie) SANS être impacté par la logique militaire de la question 1.
''')

    if "f02_process" not in st.session_state:
        st.session_state.f02_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer l'App F02", type="primary", use_container_width=True):
            if st.session_state.f02_process is None:
                with st.spinner("Démarrage de l'application Streamlit sur le port 8509..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App F02 sur le port 8509...")
                    
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "F02_dynamic_skills.py", "--server.port", "8509", "--server.headless", "true"],
                        cwd=root_dir,
                    )
                    st.session_state.f02_process = process
                    time.sleep(3)
                    st.rerun()
            else:
                st.info("L'application est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter l'App F02", use_container_width=True):
            if st.session_state.f02_process is not None:
                st.session_state.f02_process.terminate()
                st.session_state.f02_process = None
                print(f"[Demo_Cockpit] Arret de l'App F02\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    st.markdown("---")
    if st.session_state.f02_process is not None:
        st.write("🔴 **Application en direct :**")
        st.components.v1.iframe("http://localhost:8509", height=700, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer l'App F02' pour afficher l'interface.")

with tab_code:
    st.header("Aperçu du Code Source (Niveaux 1 & 2)")

    st.subheader("1. Le Manifeste (Niveau 1)")
    st.write("Le fichier `skills/manifest.json` que l'Agent lit en permanence :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "skills", "manifest.json")
        with open(file_path, "r", encoding="utf-8") as f:
            st.code(f.read(), language="json")
    except FileNotFoundError:
        st.error("Fichier manifest.json introuvable.")

    st.markdown("---")
    st.subheader("2. L'Outil de Chargement Dynamique (Tool Calling)")
    st.write("Le code LangChain permettant à l'Agent de demander le contenu d'une Skill précise :")
    try:
        file_path_py = os.path.join(root_dir, "F02_dynamic_skills.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Penser à extraire la portion de l'outil `fetch_skill`
        snippet = "".join(lines[46:61])
        st.code(snippet, language="python")
    except FileNotFoundError:
         st.error("Fichier F02_dynamic_skills.py introuvable.")
         
    st.markdown("---")
    st.subheader("3. Isolation (Contexte Éphémère)")
    st.write("La sauvegarde en session : on stocke uniquement la réponse de l'IA, on 'oublie' intentionnellement l'outil et le prompt système de la Skill.")
    try:
        snippet_state = "".join(lines[155:160])
        st.code(snippet_state, language="python")
    except Exception:
        pass

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise : Architecture Hub & Spoke**

Dans un SI mature, vous ne voulez pas créer un chatbot séparé pour le support IT, un autre pour la Finance, un autre pour les RH.

Cette architecture `F02` vous permet de créer un **Assistant Unique (Hub)** :
* L'employé lui pose une question.
* L'Assistant consulte le catalogue d'entreprise (Manifeste).
* L'Assistant télécharge la "Connaissance/Procédure" (Spoke) *idéale* de manière invisible.
* Une fois le problème réglé, l'Assistant redevient "Vierge" et prêt pour un problème d'un tout autre domaine.

C'est ainsi qu'on gère le "problème de la fenêtre de contexte" : on ne charge pas toutes les règles de l'entreprise dans la mémoire du LLM, on les charge à la demande.

</div>
""", unsafe_allow_html=True)
