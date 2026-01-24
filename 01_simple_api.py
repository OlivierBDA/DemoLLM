import os
from google import genai
from dotenv import load_dotenv

# ==============================================================================
# Demo LLM - Étape 1 : Appel simple d'une API LLM
# ==============================================================================
# Cet exemple montre comment configurer le client GenAI et effectuer un appel 
# simple pour générer du texte en utilisant le modèle gemini-3-flash-preview.
# ==============================================================================

def main():
    # ASPECT CLÉ : Chargement des variables d'environnement depuis le fichier .env
    load_dotenv()
    
    # Configuration de l'API
    # ASPET CLÉ : On utilise la bibliothèque 'google-genai' (SDK moderne)
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        print("Erreur : La variable d'environnement GOOGLE_API_KEY n'est pas définie.")
        print("Veuillez configurer votre clé API avec : set GOOGLE_API_KEY=votre_cle")
        return

    # Initialisation du client GenAI
    # ASPECT CLÉ : Le client centralise les interactions avec les modèles de Google
    client = genai.Client(api_key=api_key)

    print("--- Demo LLM - Étape 1 : Appel Simple API ---")
    
    # Définition du prompt par l'utilisateur
    # ASPECT CLÉ : On permet à l'utilisateur de saisir son propre prompt
    prompt = input("\nPosez votre question au LLM (ex: Qui est Iron Man ?) : ")
    
    if not prompt.strip():
        print("Erreur : Le prompt ne peut pas être vide.")
        return
    
    print("\n[Attente de la réponse du modèle 'gemini-3-flash-preview'...]")
    
    try:
        # ASPECT CLÉ : Appel simple à generate_content
        # On spécifie explicitement le modèle gemini-3-flash-preview
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        
        # Affichage du résultat
        print("\n" + "="*50)
        print("RÉPONSE DU LLM :")
        print("="*50)
        
        if response.text:
            print(response.text)
        else:
            # ASPECT CLÉ : Debug si la réponse textuelle est vide
            print("ATTENTION : 'response.text' est None ou vide.")
            print("\n--- Diagnostic de la réponse ---")
            print(f"Prompt envoyé (longueur: {len(prompt)}): '{prompt}'")
            
            if response.candidates:
                candidate = response.candidates[0]
                print(f"Raison de fin : {candidate.finish_reason}")
                
                if candidate.safety_ratings:
                    print("Sécurité :")
                    for rating in candidate.safety_ratings:
                        print(f" - {rating.category}: {rating.probability}")
                
                if candidate.content and candidate.content.parts:
                    print("Contenu brut trouvé dans candidate.content.parts :")
                    for part in candidate.content.parts:
                        print(f" - {part}")
                else:
                    print("Aucun contenu trouvé dans le candidat.")
            else:
                print("Aucun candidat retourné par le modèle.")
                print(f"Réponse complète pour debug : {response}")
                
        print("="*50)
        
    except Exception as e:
        print(f"\nUne erreur est survenue lors de l'appel à l'API : {e}")
        print("Vérifiez votre clé API et la disponibilité du modèle 'gemini-3-flash-preview'.")

if __name__ == "__main__":
    main()
