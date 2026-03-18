import asyncio
import os
from google.adk import Agent, Runner

# ==============================================================================
# Demo LLM - Phase G : Étape 1 : Découverte A2A (Server Avengers)
# ==============================================================================
# Ce script crée un Agent A2A représentant l'équipe des Avengers.
# ==============================================================================

async def main():
    print("🦸 Initialisation de l'Agent A2A : Avengers...")
    
    # 1. Création de l'Agent
    agent = Agent(
        name="Avengers_Team",
        description="Équipe d'intervention rapide sur le terrain. Spécialisée dans la résolution de conflits physiques et les missions de sauvetage.",
    )

    # 2. Démarrage du serveur A2A
    port = int(os.environ.get("PORT", 8081))
    print(f"✅ L'Agent Avengers est prêt et écoute sur le port {port}.")
    print("📡 Protocole Discovery actif. En attente de détection par le SHIELD...")
    
    # Run the server using the ADK Runner
    runner = Runner(agent=agent, port=port)
    await runner.run()

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())

if __name__ == "__main__":
    # Windows event loop policy workaround if needed
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
