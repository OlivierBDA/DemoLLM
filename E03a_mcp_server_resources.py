import asyncio
import os
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn

# ==============================================================================
# Demo LLM - Phase E : Étape 3a : Le Serveur MCP de Ressources (Version RÉSEAU)
# ==============================================================================
# ASPECT CLÉ : Ce serveur expose des données statiques (Resources) via des URIs.
# Contrairement aux Tools, les Resources sont consultatives.
# ==============================================================================

server = Server("marvel-resource-server")

# Chemins vers les fichiers statiques (Resolution relative au script)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
TIMELINE_FILE = os.path.join(DATA_DIR, "mcu_timeline.md")
HEROES_FILE = os.path.join(DATA_DIR, "marvel_heroes.md")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Liste les ressources disponibles pour le client."""
    print("  [MCP SERVER] Discovery: Le client demande la liste des ressources.")
    return [
        types.Resource(
            uri="mcp://marvel/timeline",
            name="Timeline du MCU",
            description="Chronologie synthétique des films Marvel.",
            mimeType="text/markdown"
        ),
        types.Resource(
            uri="mcp://marvel/heroes",
            name="Catalogue des Héros",
            description="Liste des héros disponibles dans la bibliothèque.",
            mimeType="text/markdown"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lit et renvoie le contenu d'une ressource spécifique."""
    # Conversion explicite en string pour éviter les problèmes de type (ex: Pydantic AnyUrl)
    uri_str = str(uri)
    print(f"  [MCP SERVER] Reading: Demande de lecture pour l'URI: {repr(uri_str)}")
    
    if uri_str == "mcp://marvel/timeline":
        print(f"               Recherche fichier: {TIMELINE_FILE}")
        if os.path.exists(TIMELINE_FILE):
            with open(TIMELINE_FILE, "r", encoding="utf-8") as f:
                return f.read()
            
    elif uri_str == "mcp://marvel/heroes":
        print(f"               Recherche fichier: {HEROES_FILE}")
        if os.path.exists(HEROES_FILE):
            with open(HEROES_FILE, "r", encoding="utf-8") as f:
                return f.read()
    
    print(f"  [MCP SERVER] Error: Ressource non trouvée : {repr(uri_str)}")
    raise ValueError(f"Ressource inconnue : {uri_str}")

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
                server_name="marvel-resources",
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
    print("🚀 Serveur MCP Ressources démarré sur http://127.0.0.1:8001")
    print(f"📂 Dossier de données : {DATA_DIR}")
    uvicorn.run(starlette_app, host="127.0.0.1", port=8001)
