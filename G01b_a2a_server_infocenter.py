import asyncio
import os
from google.adk import Agent, Runner

# ==============================================================================
# Demo LLM - Phase G : Étape 1 : Découverte A2A (Server Info Center)
# ==============================================================================
# Ce script crée un Agent A2A représentant le centre d'information du SHIELD.
# ==============================================================================

async def main():
    print("🧠 Initialisation de l'Agent A2A : SHIELD Info Center...")
    
    # 1. Création de l'Agent
    agent = Agent(
        name="SHIELD_InfoCenter",
        description="Base de données centrale des super-humains, entités cosmiques, et menaces mondiales.",
    )

    # 2. Démarrage du serveur A2A
    port = int(os.environ.get("PORT", 8082))
    print(f"✅ L'Agent Info Center est prêt et écoute sur le port {port}.")
    print("📡 Protocole Discovery actif. En attente de requêtes...")
    
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
