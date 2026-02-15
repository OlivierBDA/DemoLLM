import asyncio
import os
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn

# ==============================================================================
# Demo LLM - Phase E : Étape 5a : Serveur avec Progress Tracking (Combat)
# ==============================================================================
# ASPECT CLÉ : Démontrer l'envoi de notifications asynchrones (Progress) pendant
# une exécution longue (Tool Call).
# ==============================================================================

server = Server("marvel-combat-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Déclare l'outil de simulation de combat."""
    return [
        types.Tool(
            name="simulate_combat",
            description="Simule un combat en 3 rounds entre deux héros avec retour en temps réel.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hero1": {"type": "string", "description": "Nom du premier combattant"},
                    "hero2": {"type": "string", "description": "Nom du second combattant"}
                },
                "required": ["hero1", "hero2"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Exécute le combat et envoie des progrès à chaque round."""
    if name != "simulate_combat":
        raise ValueError(f"Outil inconnu : {name}")

    hero1 = arguments.get("hero1", "Héros A")
    hero2 = arguments.get("hero2", "Héros B")
    
    # Récupération du contexte pour les notifications
    ctx = server.request_context
    progress_token = ctx.meta.progressToken if ctx.meta else None
    
    print(f"  [MCP SERVER] Combat démarré : {hero1} vs {hero2}")
    if progress_token:
        print(f"               Progress Tracking activé (Token: {progress_token})")

    # Simulation de 3 rounds
    for r in range(1, 4):
        # 1. Attente simulant un calcul ou une action longue
        await asyncio.sleep(2)
        
        # 2. Envoi de la notification de progrès
        if progress_token:
            msg = f"Round {r} terminé : "
            if r == 1: msg += f"{hero1} prend l'avantage avec une attaque surprise !"
            elif r == 2: msg += f"{hero2} contre-attaque violemment !"
            else: msg += f"L'affrontement atteint son paroxysme !"
            
            await ctx.session.send_progress_notification(
                progress_token=progress_token,
                progress=float(r),
                total=3.0,
                message=msg
            )
            print(f"               Notification envoyée : Round {r}/3")

    return [
        types.TextContent(
            type="text",
            text=f"COMBAT TERMINÉ !\n\nAprès un duel acharné de 3 rounds, {hero1} l'emporte sur {hero2} grâce à une meilleure endurance !"
        )
    ]

# --- INFRASTRUCTURE RÉSEAU (SSE) ---
sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await server.run(read, write, InitializationOptions(
            server_name="marvel-combat", server_version="1.0.0",
            capabilities=server.get_capabilities(
                notification_options=NotificationOptions(),
                experimental_capabilities={}
            )
        ))
    return Response()

starlette_app = Starlette(routes=[
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Mount("/messages/", app=sse.handle_post_message),
])

if __name__ == "__main__":
    print("🚀 Serveur MCP Combat (Progress) démarré sur http://127.0.0.1:8003")
    uvicorn.run(starlette_app, host="127.0.0.1", port=8003)
