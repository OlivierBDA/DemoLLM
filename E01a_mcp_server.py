import asyncio
import random
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn

# ==============================================================================
# Demo LLM - Phase E : Étape 1a : Le Serveur MCP (Version RÉSEAU / SSE)
# ==============================================================================
# ASPECT CLÉ : Le serveur est désormais un service HTTP indépendant.
# Il écoute sur un port et attend des connexions SSE.
# ==============================================================================

server = Server("marvel-combat-server")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    print("  [MCP SERVER] Discovery: Le client demande la liste des outils.")
    return [
        types.Tool(
            name="resolve_combat",
            description="Détermine le vainqueur d'un combat entre deux héros Marvel.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hero1": {"type": "string", "description": "Nom du premier combattant"},
                    "hero2": {"type": "string", "description": "Nom du deuxième combattant"}
                },
                "required": ["hero1", "hero2"],
            },
            outputSchema={
                "type": "object",
                "properties": {
                    "winner": {"type": "string", "description": "Nom du vainqueur"},
                    "reason": {"type": "string", "description": "Explication de la victoire"},
                    "points": {"type": "integer", "description": "Points de domination (0-100)"}
                },
                "required": ["winner", "reason", "points"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> types.CallToolResult:
    print(f"  [MCP SERVER] Execution: Appel de l'outil '{name}' avec les paramètres : {arguments}")
    if name == "resolve_combat":
        h1 = arguments.get("hero1", "Inconnu 1")
        h2 = arguments.get("hero2", "Inconnu 2")
        winner = random.choice([h1, h2])
        reason = random.choice([
            "grâce à une force brute supérieure.",
            "en utilisant une stratégie plus fine.",
            "grâce à son équipement technologique."
        ])
        points = random.randint(50, 100)
        
        result_text = f"Le vainqueur est **{winner}** {reason} (Score: {points})"
        structured_data = {"winner": winner, "reason": reason, "points": points}
        
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=result_text)],
            structuredContent=structured_data
        )
    raise ValueError(f"Outil inconnu : {name}")

# --- CONFIGURATION DU TRANSPORT SSE ---
sse = SseServerTransport("/messages/")

async def handle_sse(request):
    """Gère la connexion SSE initiale."""
    async with sse.connect_sse(
        request.scope, request.receive, request._send
    ) as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marvel-combat",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )
    return Response()

# --- APPLICATION STARLETTE ---
starlette_app = Starlette(
    routes=[
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ]
)

if __name__ == "__main__":
    print("🚀 Serveur MCP Marvel Combat démarré sur http://127.0.0.1:8000")
    uvicorn.run(starlette_app, host="127.0.0.1", port=8000)
