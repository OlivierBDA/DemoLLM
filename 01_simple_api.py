import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

# ==============================================================================
# Demo LLM - Étape 1 : Appel simple d'une API LLM (via Interface Standard)
# ==============================================================================
# Cet exemple montre l'utilisation d'une interface standard (OpenAI-compatible)
# via LangChain. Cela permet de changer de fournisseur (Gemini, Mistral, OpenAI)
# simplement en modifiant les variables dans le fichier .env, sans toucher au code.
# ==============================================================================

def main():
    # ASPECT CLÉ : Chargement des variables techniques depuis le fichier .env
    load_dotenv()
    
    # Configuration récupérée du .env
    model_name = os.getenv("LLM_MODEL")
    api_key = os.getenv("LLM_API_KEY")
    base_url = os.getenv("LLM_BASE_URL")
    
    if not api_key or not model_name:
        print("Erreur : Les variables LLM_MODEL ou LLM_API_KEY ne sont pas définies dans le .env.")
        return

    # Initialisation du modèle via l'interface standard ChatOpenAI
    # ASPECT CLÉ : On utilise ChatOpenAI() comme un wrapper agnostique.
    # Le base_url permet de rediriger les appels vers n'importe quel fournisseur compatible.
    llm = ChatOpenAI(
        model=model_name,
        api_key=api_key,
        base_url=base_url,
        temperature=0.7
    )

    print(f"--- Demo LLM - Étape 1 : Appel Simple (Interface Standard) ---")
    print(f"Configuration : Modèle = {model_name} | Endpoint = {base_url}")
    
    # Saisie du prompt
    prompt_text = input("\nPosez votre question (ex: Qui est Iron Man ?) : ")
    
    if not prompt_text.strip():
        print("Erreur : La question ne peut pas être vide.")
        return
    
    print(f"\n[Attente de la réponse du modèle '{model_name}'...]")
    
    try:
        # ASPECT CLÉ : Structure de message standard LangChain
        message = HumanMessage(content=prompt_text)
        
        # Appel du modèle
        response = llm.invoke([message])
        
        # Affichage du résultat
        print("\n" + "="*50)
        print("RÉPONSE DU LLM :")
        print("="*50)
        print(response.content)
        print("="*50)
        
    except Exception as e:
        print(f"\nUne erreur est survenue lors de l'appel : {e}")
        print("Vérifiez votre configuration dans le fichier .env.")

if __name__ == "__main__":
    main()
