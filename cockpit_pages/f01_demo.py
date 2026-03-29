import streamlit as st
import subprocess
import os
import sys
import time

st.title("Étape F01 : Injection de Compétences (Skills)")

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
**Objectif : Démontrer comment transformer l'expertise d'un Agent IA sans modifier son code, juste en injectant un fichier de définition de compétence ("Skill").**

Cette étape illustre la puissance des **Skills** (Compétences). Au lieu d'avoir un Agent générique ("Je suis un assistant utile"), on lui donne un cadre complet de raisonnement.
Ici, nous passons d'un simple "Fan de Marvel" à un "Expert Tacticien du SHIELD" utilisant le **Framework S.T.A.R.K.**

**Fonctionnement :**
1. L'application charge un fichier externe `tactical_analysis.md` (La *Skill*).
2. Ce fichier définit un framework précis (Scan, Terrain, Assets, Risk, Kill-Switch) et donne des exemples concrets (Few-Shot Prompting).
3. Le contenu de ce fichier est injecté dans le **System Message** de l'orchestrateur (LangChain).
4. Le modèle de fondation (LLM) obéit désormais à ce nouveau cadre de réflexion.
''')

    st.info("💡 L'intérêt majeur est la séparation des préoccupations : Les développeurs gèrent le code Python (le moteur), les experts métiers gèrent les fichiers Markdown de Skills (la connaissance).")

    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            User [label="Utilisateur"];
            UI [label="Streamlit Chat", style=filled, color=lightblue];
            Skill [label="tactical_analysis.md\\n(Skill Framework)", style=filled, color=lightgreen, shape=note];
            LLM [label="LLM (OpenAI/Gemini)\\navec Système Prompt", style=filled, color=orange];
            
            User -> UI [label="Question"];
            Skill -> UI [label="Activation (Toggle)"];
            UI -> LLM [label="Historique + Skill injectée"];
            LLM -> UI [label="Réponse (Stream)"];
        }
    ''')


with tab_demo:
    st.header("Démonstration Technique")
    st.success('''
**Note d'architecture :** La démo ci-dessous est l'application d'origine exécutée en tâche de fond et incrustée ici. 
Elle tourne de manière totalement isolée sur le port `8508`.

💡 **Idée de test :** Essayez de poser la question `Comment on gère une attaque de Sentinelles anti mutants au milieu de Paris ?` avant et après avoir activé la Skill pour comparer.
''')

    # Gestion du processus en tâche de fond via session_state
    if "f01_process" not in st.session_state:
        st.session_state.f01_process = None

    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("▶️ Démarrer l'App F01", type="primary", use_container_width=True):
            if st.session_state.f01_process is None:
                with st.spinner("Démarrage de l'application Streamlit sur le port 8508..."):
                    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    print(f"\\n[Demo_Cockpit] Lancement de l'App F01 en tâche de fond sur le port 8508...")
                    
                    # Lancement asynchrone (Popen)
                    process = subprocess.Popen(
                        [sys.executable, "-m", "streamlit", "run", "F01_streamlit_skills.py", "--server.port", "8508", "--server.headless", "true"],
                        cwd=root_dir,
                    )
                    st.session_state.f01_process = process
                    time.sleep(3) # Attente que le serveur soit prêt
                    st.rerun()
            else:
                st.info("L'application est déjà en cours d'exécution.")

    with col2:
        if st.button("⏹️ Arrêter l'App F01", use_container_width=True):
            if st.session_state.f01_process is not None:
                st.session_state.f01_process.terminate()
                st.session_state.f01_process = None
                print(f"[Demo_Cockpit] Arret de l'App F01\\n")
                st.success("Application arrêtée.")
                time.sleep(1)
                st.rerun()

    # Affichage de l'Iframe si le processus tourne
    st.markdown("---")
    if st.session_state.f01_process is not None:
        st.write("🔴 **Application en direct :**")
        st.components.v1.iframe("http://localhost:8508", height=700, scrolling=True)
    else:
        st.info("Cliquez sur 'Démarrer l'App F01' pour afficher l'interface de chat et tester la Skill.")

with tab_code:
    st.header("Aperçu du Code Source et de la Skill")
    
    st.subheader("1. Fichier de Skill (.md)")
    st.write("Voici le contenu du fichier `skills/tactical_analysis.md` qui dicte le comportement de l'IA :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "skills", "tactical_analysis.md")
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            st.code(content, language="markdown")

    except FileNotFoundError:
        st.error("Fichier tactical_analysis.md introuvable.")

    st.markdown("---")
    st.subheader("2. Code d'Injection du Prompt Système")
    st.write("Voici comment le script Python charge ce fichier et l'injecte dans LangChain :")
    try:
        file_path_py = os.path.join(root_dir, "F01_streamlit_skills.py")
        with open(file_path_py, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Lignes 41 à 57 du F01_streamlit_skills.py (index 40 à 57)
        snippet = "".join(lines[40:57])
        st.code(snippet, language="python")

    except FileNotFoundError:
        st.error("Fichier F01_streamlit_skills.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Dans un SI d'entreprise, cette approche permet de créer une usine à Agents (Agent Factory) :
*   **Moteur Unique** : Le service informatique maintient une seule application (le moteur IA, la gestion de l'historique, la sécurité, l'UI).
*   **Comportements Multiples** : Chaque département crée ses propres "Skills" en écrivant de simples fichiers texte (Markdown, YAML).
*   **Exemples d'usage :**
    *   *Skill RH* : Recadrage sur la politique de congés avec obligation de citer le règlement intérieur.
    *   *Skill Finance* : Formatage strict des tableaux de bord financiers et interdiction de donner des conseils d'investissement non vérifiés.
    *   *Skill Dev* : Validation de code avec des règles de nommage très spécifiques à l'entreprise.

On décentralise l'expertise métier vers les métiers eux-mêmes.

</div>
""", unsafe_allow_html=True)
