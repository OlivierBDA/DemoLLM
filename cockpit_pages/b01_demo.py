import streamlit as st
import os
import subprocess
import sys

st.title("Étape B01 : Génération de Données (Préparation)")

# Création des onglets
tab_concept, tab_demo, tab_code, tab_conclusion = st.tabs([
    "📖 Concept", 
    "⚡ Démo", 
    "💻 Code", 
    "🏢 Ouverture SI"
])

with tab_concept:
    st.header("Concept et Explication")
    st.warning('''
**⚠️ ÉTAPE FICTIVE (Pour les besoins de la démonstration)**

L'objectif de cette étape est de **fabriquer de la donnée** de toute pièce pour pouvoir ensuite l'utiliser dans notre moteur de recherche RAG. 
Nous allons utiliser l'IA générative pour rédiger de longues fiches "Wikipédia" très détaillées sur les héros Marvel.
    ''')
    
    st.info('''
**Pourquoi cette étape ?**
Pour faire une démonstration de RAG, il faut du texte à interroger. Plutôt que de copier-coller manuellement des articles, nous utilisons un script automatisé (`B01_generate_data.py`) qui demande au LLM de créer ces fichiers texte et les enregistre dans le dossier `data/source_files`.
    ''')
    
    st.graphviz_chart('''
        digraph G {
            rankdir=LR;
            node [shape=box, fontname="Helvetica", fontsize=10];
            Config [label="data_config.json\\n(Liste de Héros)", shape=note];
            LLM [label="Générateur LLM\\n(Prompt Créatif)", style=filled, color=orange];
            Files [label="Fichiers Textes\\n(.txt)", shape=folder, style=filled, color=yellow];
            
            Config -> LLM;
            LLM -> Files [label="Sauvegarde sur Disque"];
        }
    ''')

with tab_demo:
    st.header("Démonstration Technique")
    st.info("*Pour visualiser ce que fait ce script ou reconstruire la base de données brute, vous pouvez lancer l'exécution ci-dessous.*")
    
    if st.button("Lancer la Génération de Données (B01)", type="primary"):
        with st.spinner("Génération en cours...): Ce processus peut prendre plus d'une minute selon le nombre de fiches à générer."):
            root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            try:
                result = subprocess.run(
                    [sys.executable, "B01_generate_data.py"],
                    capture_output=True,
                    text=True,
                    cwd=root_dir,
                    timeout=180
                )
                
                st.write("**Résultat de la console (B01) :**")
                st.code(result.stdout, language="text")
                if result.stderr:
                    st.error("Erreurs (stderr) :")
                    st.code(result.stderr, language="text")
                else:
                    st.success("Génération terminée avec succès !")
                    
            except subprocess.TimeoutExpired:
                st.error("L'opération a pris trop de temps (Timeout).")
            except Exception as e:
                st.error(f"Erreur d'exécution : {e}")

with tab_code:
    st.header("Aperçu du Code Source")
    st.write("Le script itère sur une liste, invoque le LLM avec un template de prompt très restrictif, puis écrit les fichiers `.txt` :")
    try:
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        file_path = os.path.join(root_dir, "B01_generate_data.py")
        
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Extrait de la boucle de génération
        snippet1 = "".join(lines[97:113])
        st.code(snippet1, language="python")

    except FileNotFoundError:
        st.error("Fichier B01_generate_data.py introuvable.")

with tab_conclusion:
    st.header("Ouverture SI d'Entreprise")
    st.markdown("""
<div class="ouverture-si-box">

**Parallèle Entreprise :**

Dans la réalité d'un Système d'Information (SI) du monde réel, **cette étape B01 N'EXISTE PAS**.
L'entreprise n'invente pas sa donnée de base (knowledge base) avec un LLM, elle l'a déjà !

**D'où viennent vraiment les données (Data Sources) ?**
* Dépôts Documentaires (SharePoint, GED, Google Drive)
* Bases de Connaissances (Confluence, Notion, Wiki)
* Systèmes de Ticketing (Jira, ServiceNow)
* CRM & ERP (Salesforce, SAP)
* Bases de données SQL / NoSQL existantes

*Le véritable défi en entreprise n'est pas de générer cette donnée, mais de s'y **connecter**, de la **récupérer** proprement (Ingestion & ETL) et de la **mettre à jour**.*
    
</div>
""", unsafe_allow_html=True)
