import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# ==============================================================================
# Demo LLM - Étape 2 : Mode Chat avec Continuité de Conversation
# ==============================================================================
# Ce programme permet d'avoir une conversation interactive avec le LLM.
# ASPECT CLÉ : Contrairement à l'étape 1, nous conservons la liste des messages
# échangés pour que le LLM ait le "contexte" de la discussion en cours.
# ==============================================================================

def main():
    # Chargement des variables d'environnement
    load_dotenv()
    
    model_name = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    
    if not api_key or not model_name:
        print("Erreur : Configuration manquante dans le fichier .env.")
        return

    # Initialisation du modèle (Interface Standard)
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7
    )

    # ASPECT CLÉ : Initialisation de la mémoire de session (liste de messages)
    # On commence par un message système pour définir le comportement de l'IA.
    messages = [
        SystemMessage(content="Tu es un assistant expert de l'univers Marvel. Tu réponds de manière précise et enthousiaste. Tu fais des réponses courtes et concises.")
    ]

    print("--- Demo LLM - Étape 2 : Mode Chat Interactif ---")
    print("(Tapez 'exit' ou 'quitter' pour arrêter la conversation)")
    
    while True:
        # 1. Saisie utilisateur
        user_input = input("\nVous : ")
        
        if user_input.lower() in ["exit", "quitter", "quit"]:
            print("Fin de la conversation. À bientôt !")
            break
            
        if not user_input.strip():
            continue

        # 2. Ajout du message utilisateur à l'historique de la session
        # ASPECT CLÉ : On accumule les messages dans la liste 'messages'
        messages.append(HumanMessage(content=user_input))
        
        print(f"\n[Attente de la réponse du modèle '{model_name}'...]")
        
        try:
            # 3. Appel du modèle avec toute la continuité des messages
            # ASPECT CLÉ : On passe LA LISTE COMPLÈTE au LLM
            response = llm.invoke(messages)
            
            # 4. Affichage et mémorisation de la réponse de l'IA
            print("\nAI : " + response.content)
            
            # ASPECT CLÉ : Il faut aussi mémoriser la réponse de l'AI pour le prochain tour
            messages.append(AIMessage(content=response.content))
            
        except Exception as e:
            print(f"\nUne erreur est survenue : {e}")
            break

if __name__ == "__main__":
    main()
