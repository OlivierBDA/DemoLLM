from fastapi import FastAPI, Query
import random
import time
from datetime import datetime

# ==============================================================================
# Demo LLM - Étape 9A : Service REST de Combat (Outil Externe)
# ==============================================================================
# Ce service simule un combat entre deux héros.
# ASPECT CLÉ : C'est un pur programme Python exposé en API, sans LLM interne.
# Le LLM l'utilisera comme un "outil" (Tool Calling).
# ==============================================================================
# .venv\Scripts\python.exe 09a_combat_service.py
#"Compare la force et l'intelligence des héros dans un graphique."
#"Montre le box-office des films par année sous forme de lignes."
#"Quels sont nos héros les plus rapides ? (Affiche un graphique)"

app = FastAPI(
    title="Marvel Combat Simulator API",
    description="Une API pour simuler des duels entre super-héros du MCU.",
    version="1.0.0"
)

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur le simulateur de combat Marvel. Consultez /docs pour l'API."}

@app.get("/simulate_combat")
def simulate_combat(
    hero1: str = Query(..., description="Nom du premier combattant"),
    hero2: str = Query(..., description="Nom du second combattant")
):
    """
    Simule un duel aléatoire entre deux héros et retourne le vainqueur.
    """
    print(f"\n[API CALL] Requête de combat reçue : {hero1} VS {hero2}")
    
    # Simulation d'un petit délai pour le réalisme de la démo
    time.sleep(1)
    
    # Logique de combat classique (aléatoire)
    participants = [hero1, hero2]
    winner = random.choice(participants)
    loser = hero2 if winner == hero1 else hero1
    
    # Génération d'un commentaire aléatoire
    scenarios = [
        "Un combat épique au cœur de New York.",
        "Une démonstration de force brute incroyable.",
        "Le combat s'est terminé par une ruse inattendue.",
        "La victoire s'est jouée à un cheveu.",
        "Une alliance temporaire semble s'être formée après le duel."
    ]
    detail = random.choice(scenarios)
    
    result = {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "matchup": f"{hero1} vs {hero2}",
        "winner": winner,
        "loser": loser,
        "commentary": detail
    }
    
    print(f"[API RESPONSE] Vainqueur : {winner}")
    return result

if __name__ == "__main__":
    import uvicorn
    print("\n[SERVEUR] Lancement du service de combat sur http://127.0.0.1:8000")
    print("[DOCS] La documentation OpenAPI est disponible sur http://127.0.0.1:8000/docs")
    uvicorn.run(app, host="127.0.0.1", port=8000)
