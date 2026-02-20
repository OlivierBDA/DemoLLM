import asyncio
import os
import sys
import anyio
import datetime
import traceback
import logging
from mcp import ClientSession
from mcp.client.sse import sse_client
import mcp.types as types

# Force stdout encoding
sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fichier de sortie HTML
OUTPUT_HTML = "E06_viewer.html"
SERVER_URL = "http://127.0.0.1:8004/sse"

def generate_html(resources):
    """Génère une page HTML statique avec rafraîchissement automatique."""
    try:
        html_content = f"""
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>MCP Resources Viewer</title>
            <!-- Rafraîchissement automatique toutes les 1 seconde -->
            <meta http-equiv="refresh" content="1">
            <style>
                body {{ font-family: 'Segoe UI', sans-serif; background-color: #f0f2f6; padding: 20px; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                h1 {{ color: #e23636; border-bottom: 2px solid #e23636; padding-bottom: 10px; }}
                .status {{ font-size: 0.9em; color: #666; margin-bottom: 20px; }}
                .resource-list {{ list-style: none; padding: 0; }}
                .resource-item {{ background: #f8f9fa; border-left: 5px solid #007bff; margin-bottom: 10px; padding: 15px; border-radius: 4px; }}
                .resource-item.new {{ border-left-color: #28a745; background: #e8f5e9; animation: flash 1s; }}
                .uri {{ color: #666; font-family: monospace; font-size: 0.9em; }}
                @keyframes flash {{ 0% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📡 MCP Live Resources</h1>
                <div class="status">
                    Dernière mise à jour : {datetime.datetime.now().strftime("%H:%M:%S")}
                    <br>Connecté à : {SERVER_URL}
                </div>
                
                <ul class="resource-list">
        """
        
        if not resources:
            html_content += "<p>Aucune ressource détectée.</p>"
        else:
            for r in resources:
                # Highlight pour la ressource dynamique
                is_new = "Enemies" in r.name
                css_class = "resource-item new" if is_new else "resource-item"
                icon = "🆕" if is_new else "📄"
                
                html_content += f"""
                    <li class="{css_class}">
                        <strong>{icon} {r.name}</strong><br>
                        <span class="uri">{r.uri}</span>
                    </li>
                """
                
        html_content += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[HTML] Fichier mis à jour : {OUTPUT_HTML} ({len(resources)} ressources)")
    except Exception as e:
        print(f"[HTML GENERATION ERROR] {e}")
        traceback.print_exc()


async def main():
    print(f"Connexion au serveur MCP : {SERVER_URL}...")
    
    # Event pour signaler qu'un rafraîchissement est nécessaire
    refresh_event = asyncio.Event()
    
    try:
        async with sse_client(url=SERVER_URL) as (read, write):
            print("Transport SSE connecté.")
            
            # Callback de notification (DOIT ÊTRE NON-BLOQUANT)
            async def on_notification(notif):
                if isinstance(notif, types.ServerNotification):
                    if isinstance(notif.root, types.ResourceListChangedNotification):
                        print(f"\n[CLIENT] 🔔 Notification reçue (Signal Event) !")
                        # On signale juste à la loop principale de faire le travail
                        refresh_event.set()

            print("Création ClientSession...")
            async with ClientSession(read, write, message_handler=on_notification) as session:
                print("Initialisation de la session...")
                await session.initialize()
                print("Session MCP Initialisée.")
                
                # Chargement initial
                print("Chargement initial...")
                res = await session.list_resources()
                print(f"Ressources initiales : {len(res.resources)}")
                generate_html(res.resources)
                
                print(f"\n[CLIENT] ✅ Client prêt ! Ouvrez '{OUTPUT_HTML}' dans votre navigateur.")
                print("[CLIENT] En attente de notifications (Ctrl+C pour quitter)...")
                
                # Boucle principale : Attend le signal ou dort
                while True:
                    # On attend que l'event soit set
                    await refresh_event.wait()
                    
                    # L'event a été déclenché
                    print("[CLIENT] 🔄 Rafraîchissement déclenché...")
                    refresh_event.clear() # On reset pour la prochaine fois
                    
                    # Petit délai pour laisser le temps au serveur de respirer ou debounce
                    await asyncio.sleep(0.5)
                    
                    try:
                        res = await session.list_resources()
                        print(f"[CLIENT] Catalogue mis à jour : {len(res.resources)} items.")
                        generate_html(res.resources)
                    except Exception as e:
                        print(f"[ERREUR REFRESH] {e}")
                        traceback.print_exc()

    except Exception as e:
        print(f"\n[MAIN EXCEPTION] {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nArrêt du client.")
    except Exception as e:
        print(f"CRITICAL: {e}")
        traceback.print_exc()
