import asyncio
import os
import re
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn
import urllib.parse

# ==============================================================================
# Demo LLM - Phase E : Étape 4a : Serveur de Ressource Templates (Version RÉSEAU)
# ==============================================================================
# ASPECT CLÉ : Ce serveur utilise des 'Templates' pour exposer dynamiquement 
# une multitude de fichiers sans avoir à les lister individuellement.
# ==============================================================================

server = Server("marvel-template-server")

# Chemins de données
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
SOURCE_DIR = os.path.join(DATA_DIR, "source_files")

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Liste les ressources statiques."""
    print("  [MCP SERVER] Discovery: Le client demande les ressources statiques.")
    return [
        types.Resource(uri="mcp://marvel/timeline", name="Timeline du MCU", mimeType="text/markdown"),
        types.Resource(uri="mcp://marvel/heroes", name="Catalogue des Héros", mimeType="text/markdown")
    ]

@server.list_resource_templates()
async def handle_list_resource_templates() -> list[types.ResourceTemplate]:
    """Liste les modèles de ressources dynamiques."""
    print("  [MCP SERVER] Discovery: Le client demande les modèles (Templates).")
    return [
        types.ResourceTemplate(
            uriTemplate="mcp://marvel/heroes/{name}",
            name="Fiche Hero",
            description="Récupère les détails d'un héros par son identifiant (ex: iron_man, hulk)",
            mimeType="text/plain"
        ),
        types.ResourceTemplate(
            uriTemplate="mcp://marvel/movies/{title}",
            name="Fiche Film",
            description="Récupère les détails d'un film par son titre court (ex: thor_2011, avengers_2012)",
            mimeType="text/plain"
        )
    ]

def normalize_id(text: str) -> str:
    """Normalise un identifiant (ex: 'captain%20america' -> 'captain_america')."""
    if not text:
        return ""
    
    # 1. Décodage des caractères URL (ex: %20 -> espace)
    text = urllib.parse.unquote(text)
    
    # 2. Passage en minuscules et nettoyage des espaces extrêmes
    text = text.lower().strip()
    # Remplacement des parenthèses, espaces et tirets par des underscores
    # On garde les caractères alphanumériques et les underscores
    text = re.sub(r'[\s\(\)-]+', '_', text)
    # Nettoyage des underscores doubles ou en fin de chaîne
    text = re.sub(r'_+', '_', text).strip('_')
    return text

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lit une ressource statique ou résout un template."""
    uri_str = str(uri)
    print(f"  [MCP SERVER] Reading: Demande pour {uri_str}")

    # 1. Gestion des ressources statiques
    if uri_str == "mcp://marvel/timeline":
        path = os.path.join(DATA_DIR, "mcu_timeline.md")
    elif uri_str == "mcp://marvel/heroes":
        path = os.path.join(DATA_DIR, "marvel_heroes.md")
    
    # 2. Résolution des templates (Pattern matching avec normalisation)
    elif uri_str.startswith("mcp://marvel/heroes/"):
        raw_id = uri_str.replace("mcp://marvel/heroes/", "")
        hero_id = normalize_id(raw_id)
        # Cas particulier pour spider-man qui utilise un tiret dans le nom de fichier
        if hero_id == "spider_man":
            hero_id = "spider-man"
            
        path = os.path.join(SOURCE_DIR, f"hero_{hero_id}.txt")
        print(f"               Matching Template Héros -> '{raw_id}' normalisé en '{hero_id}'")
        
    elif uri_str.startswith("mcp://marvel/movies/"):
        raw_id = uri_str.replace("mcp://marvel/movies/", "")
        movie_id = normalize_id(raw_id)
        path = os.path.join(SOURCE_DIR, f"movie_{movie_id}.txt")
        print(f"               Matching Template Film -> '{raw_id}' normalisé en '{movie_id}'")
    
    else:
        print(f"  [MCP SERVER] Error: URI non reconnue : {uri_str}")
        raise ValueError(f"Ressource inconnue : {uri_str}")

    # Lecture du fichier
    if os.path.exists(path):
        print(f"               Lecture du fichier : {path}")
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print(f"  [MCP SERVER] Error: Fichier introuvable : {path}")
        raise ValueError(f"Fichier non trouvé pour l'URI : {uri_str}")

# --- INFRASTRUCTURE RÉSEAU ---
sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await server.run(read, write, InitializationOptions(
            server_name="marvel-templates", server_version="1.0.0",
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
    print("🚀 Serveur MCP Templates démarré sur http://127.0.0.1:8002")
    uvicorn.run(starlette_app, host="127.0.0.1", port=8002)
