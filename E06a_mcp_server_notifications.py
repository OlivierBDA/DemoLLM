import asyncio
import os
import anyio
import sys
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, JSONResponse
import uvicorn

# ==============================================================================
# Demo LLM - Phase E : Étape 6a : Serveur avec Notifications de Ressources
# ==============================================================================
# ASPECT CLÉ : Le serveur peut prévenir les clients que son catalogue a changé.
# Très utile pour les systèmes dynamiques (nouveau plugin, nouveau doc).
# ==============================================================================
# 1. Lancer le serveur MCP : python E06a_mcp_server_notifications.py
# 2. Lancer le client MCP : python E06_client_mcp_notifications.py
# 3. Lancer l'admin qui permet d'ajouter une ressource : python E06_admin_mcp.py
# 4. Ouvrir le fichier html E06_viewer.html
# 5. Ajouter la ressource "Ennemis" dans l'admin


# Force logging to stdout for demo visibility
sys.stdout.reconfigure(encoding='utf-8')

server = Server("marvel-notif-server")

# Chemins de données
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
ENEMIES_FILE = os.path.join(DATA_DIR, "marvel_enemies.md")

# Tracking des sessions actives pour le broadcast
active_sessions = set()

@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Liste les ressources, incluant dynamiquement les ennemis si le fichier existe."""
    print(f"  [MCP SERVER] Discovery: Calcul du catalogue en cours...")
    resources = [
        types.Resource(uri="mcp://marvel/timeline", name="Timeline du MCU", mimeType="text/markdown"),
        types.Resource(uri="mcp://marvel/heroes", name="Catalogue des Héros", mimeType="text/markdown")
    ]
    
    # Vérification dynamique du fichier
    if os.path.exists(ENEMIES_FILE):
        print(f"  [MCP SERVER] -> Fichier 'marvel_enemies.md' détecté locally.")
        resources.append(
            types.Resource(uri="mcp://marvel/enemies", name="Liste des Ennemis (DYNAMIQUE)", mimeType="text/markdown")
        )
    else:
        print(f"  [MCP SERVER] -> Fichier 'marvel_enemies.md' NON détecté.")
    
    print(f"  [MCP SERVER] Discovery: Catalogue renvoyé ({len(resources)} ressources).")
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lit les ressources statiques."""
    print(f"  [MCP SERVER] Read: Demande de lecture pour {uri}")
    uri_str = str(uri)
    if uri_str == "mcp://marvel/timeline":
        path = os.path.join(DATA_DIR, "mcu_timeline.md")
    elif uri_str == "mcp://marvel/heroes":
        path = os.path.join(DATA_DIR, "marvel_heroes.md")
    elif uri_str == "mcp://marvel/enemies" and os.path.exists(ENEMIES_FILE):
        path = ENEMIES_FILE
    else:
        raise ValueError(f"Ressource inconnue ou indisponible : {uri_str}")

    if not os.path.exists(path):
         return "Fichier introuvable sur le serveur."

    with open(path, "r", encoding="utf-8") as f:
        return f.read()

# --- INFRASTRUCTURE RÉSEAU (SSE) ET BROADCAST ---
sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        from mcp.server.session import ServerSession
        from contextlib import AsyncExitStack
        from mcp.server.lowlevel.server import InitializationOptions as LowLevelInitOptions

        async with AsyncExitStack() as stack:
            # 1. Config capacités
            init_options = LowLevelInitOptions(
                server_name="marvel-notifications", 
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(resources_changed=True),
                    experimental_capabilities={}
                )
            )
            
            # 2. Ouverture session
            session = await stack.enter_async_context(ServerSession(read, write, init_options))
            lifespan_context = await stack.enter_async_context(server.lifespan(server))
            
            active_sessions.add(session)
            print(f"\n[SERVEUR-MCP] (SSE) Nouvelle connexion client. Sessions actives : {len(active_sessions)}")
            
            try:
                # 3. Boucle Dispatch
                async with anyio.create_task_group() as tg:
                    async for message in session.incoming_messages:
                        tg.start_soon(
                            server._handle_message,
                            message,
                            session,
                            lifespan_context
                        )
            except anyio.get_cancelled_exc_class():
                print("[SERVEUR-MCP] (SSE) Connexion fermée (AnyIO Cancelled).")
            except Exception as e:
                print(f"[SERVEUR-MCP] (SSE) Erreur de connexion : {e}")
            finally:
                active_sessions.discard(session)
                print(f"[SERVEUR-MCP] (SSE) Client déconnecté. Sessions restantes : {len(active_sessions)}")
    
    return Response()

# Endpoint Admin pour forcer la notification resources/list_changed
async def trigger_notification(request):
    """Broadcast notification to all active MCP sessions."""
    print(f"\n[SERVEUR-MCP] >>> RÉCEPTION SIGNAL ADMIN (HTTP POST) <<<")
    print(f"[SERVEUR-MCP] Déclenchement du broadcast MCP vers {len(active_sessions)} client(s)...")
    
    count = 0
    # On itère sur une copie pour éviter les erreurs de modification concurrente
    for session in list(active_sessions):
        try:
            # Appel SDK MCP pour notifier les changements de ressources
            # send_resource_list_changed est une méthode de ServerSession
            await session.send_resource_list_changed()
            count += 1
        except Exception as e:
            print(f"[SERVEUR-MCP] ! Erreur d'envoi à une session : {e}")
            # Si erreur, on considère la session perdue
            active_sessions.discard(session)
            
    print(f"[SERVEUR-MCP] Broadcast terminé. Notifications envoyées avec succès : {count}")
    return JSONResponse({"status": "ok", "broadcast_count": count})

starlette_app = Starlette(routes=[
    Route("/sse", endpoint=handle_sse, methods=["GET"]),
    Route("/admin/notify", endpoint=trigger_notification, methods=["POST"]),
    Mount("/messages/", app=sse.handle_post_message),
])

if __name__ == "__main__":
    print("🚀 Serveur MCP Notifications démarré sur http://127.0.0.1:8004")
    print("👉 Endpoint de trigger : POST http://127.0.0.1:8004/admin/notify")
    # Log level info pour voir les requêtes HTTP
    uvicorn.run(starlette_app, host="127.0.0.1", port=8004, log_level="info")
