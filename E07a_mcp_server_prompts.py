import asyncio
import os
import re
import urllib.parse
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.sse import SseServerTransport
import mcp.types as types
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
import uvicorn
import random

# ==============================================================================
# Demo LLM - Phase E : Étape 7a : Serveur de Prompts MCP
# ==============================================================================
# ASPECT CLÉ : Ce serveur définit des "Prompts" prêts à l'emploi qui guident
# le LLM dans son comportement, en lui fournissant du contexte ou en lui 
# ordonnant d'utiliser des outils spécifiques.
# ==============================================================================

server = Server("marvel-prompts-server")

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "data")
SOURCE_DIR = os.path.join(DATA_DIR, "source_files")

def normalize_id(text: str) -> str:
    """Normalise un identifiant (ex: 'captain%20america' -> 'captain_america')."""
    if not text: return ""
    text = urllib.parse.unquote(text).lower().strip()
    text = re.sub(r'[\s\(\)-]+', '_', text)
    text = re.sub(r'_+', '_', text).strip('_')
    if text == "spider_man": return "spider-man"
    return text


# --- TOOLS ---
# Le serveur expose "simulate_combat" pour que le prompt 1 puisse l'utiliser.
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    print("  [MCP SERVER] Discovery: Le client demande la liste des outils.")
    return [
        types.Tool(
            name="simulate_combat",
            description="Simule un combat entre deux super-héros et renvoie le vainqueur avec le score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hero1": {"type": "string"},
                    "hero2": {"type": "string"}
                },
                "required": ["hero1", "hero2"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    print("\n" + "="*50)
    print(f"  [MCP SERVER] 🛠️  EXÉCUTION D'OUTIL DEMANDÉE")
    print("="*50)
    print(f"  [MCP SERVER] 🎯 Outil : '{name}'")
    print(f"  [MCP SERVER] 🔧 Args  : {arguments}")
    if name == "simulate_combat":
        hero1 = arguments.get("hero1", "Inconnu 1")
        hero2 = arguments.get("hero2", "Inconnu 2")
        score1 = random.randint(50, 100)
        score2 = random.randint(50, 100)
        winner = hero1 if score1 >= score2 else hero2
        return [types.TextContent(type="text", text=f"Résultat du simulateur: {hero1} (Puissance: {score1}) vs {hero2} (Puissance: {score2}). Vainqueur déclaré: {winner}.")]
    raise ValueError(f"Outil inconnu: {name}")


# --- PROMPTS ---
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    print("  [MCP SERVER] Discovery: Le client demande la liste des Prompts.")
    return [
        types.Prompt(
            name="analyze_combat",
            description="Demande au LLM de simuler puis de commenter de façon épique un combat entre deux super-héros.",
            arguments=[
                types.PromptArgument(name="hero1", description="Nom du premier combattant (ex: Thor)", required=True),
                types.PromptArgument(name="hero2", description="Nom du deuxième combattant (ex: Hulk)", required=True)
            ]
        ),
        types.Prompt(
            name="create_hero_card",
            description="Fournit les données brutes d'un héros au LLM pour générer une fiche d'identité JSON stricte.",
            arguments=[
                types.PromptArgument(name="hero_name", description="Identifiant du héros (ex: spider-man, iron_man)", required=True)
            ]
        )
    ]


@server.get_prompt()
async def handle_get_prompt(name: str, arguments: dict | None) -> types.GetPromptResult:
    args = arguments or {}
    print("\n" + "="*50)
    print(f"  [MCP SERVER] 📝 DEMANDE DE PROMPT REÇUE")
    print("="*50)
    print(f"  [MCP SERVER] 🎯 Nom du prompt : '{name}'")
    print(f"  [MCP SERVER] 🔧 Arguments   : {args}")
    
    if name == "analyze_combat":
        hero1 = args.get("hero1", "Combattant A")
        hero2 = args.get("hero2", "Combattant B")
        
        print(f"  [MCP SERVER] ⚙️  Génération des instructions de combat pour {hero1} vs {hero2}...")
        # Ce prompt est une simple instruction texte (TextContent)
        instruction = (
            f"Je souhaite que tu joues le rôle d'un commentateur sportif expert en combats de super-héros Marvel.\n"
            f"Un duel épique va avoir lieu entre {hero1} et {hero2}.\n\n"
            f"Ta mission :\n"
            f"1. Présente brièvement les deux combattants et leurs forces respectives.\n"
            f"2. Utilise IMPÉRATIVEMENT ton outil de simulation de combat ('simulate_combat') pour obtenir le résultat chiffré et le vainqueur de l'affrontement.\n"
            f"3. Rédige un compte-rendu narratif et épique du combat en te basant stricement sur le résultat de l'outil.\n"
            f"4. Conclus par une phrase d'accroche pour le vainqueur."
        )
        
        return types.GetPromptResult(
            description=f"Prompt commentateur de combat pour {hero1} vs {hero2}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=instruction
                    )
                )
            ]
        )
        
    elif name == "create_hero_card":
        hero_raw = args.get("hero_name", "Inconnu")
        hero_id = normalize_id(hero_raw)
        path = os.path.join(SOURCE_DIR, f"hero_{hero_id}.txt")
        
        print(f"  [MCP SERVER] ⚙️  Génération de la fiche pour {hero_raw}...")
        
        # Le serveur lit le fichier local pour l'injecter comme EmbeddedResource
        content_text = f"ERREUR: Aucune donnée brute trouvée pour le héros '{hero_raw}'."
        if os.path.exists(path):
            print(f"  [MCP SERVER] 📁 Fichier source trouvé : {path}")
            with open(path, "r", encoding="utf-8") as f:
                content_text = f.read()
            print(f"  [MCP SERVER] 💉 Injection de {len(content_text)} caractères dans le Prompt en tant qu'EmbeddedResource.")
        else:
            print(f"  [MCP SERVER] ❌ ERREUR : Fichier source non trouvé : {path}")

        instruction = (
            f"Voici les données brutes concernant {hero_raw} (incluses en tant que ressource ci-dessus).\n\n"
            f"S'il te plaît, crée une fiche d'identité JSON stricte contenant les champs suivants :\n"
            f"- \"nom_reel\": Nom de naissance\n"
            f"- \"alter_ego\": Pseudo de héros\n"
            f"- \"pouvoirs\": Liste des pouvoirs principaux (tableau de chaînes de caractères)\n"
            f"- \"niveau_menace\": Estimation numérique de 1 à 10 basée sur l'analyse de ses capacités dans le texte\n\n"
            f"Contrainte Forte : Ne réponds qu'avec le code JSON pur (pas de bloc markdown, pas d'explication de ta démarche)."
        )

        return types.GetPromptResult(
            description=f"Prompt Extraction JSON pour {hero_raw}",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.EmbeddedResource(
                        type="resource",
                        resource=types.TextResourceContents(
                            uri=f"mcp://marvel/heroes/{hero_id}",
                            mimeType="text/plain",
                            text=content_text
                        )
                    )
                ),
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=instruction
                    )
                )
            ]
        )
        
    raise ValueError(f"Prompt inconnu: {name}")


# --- INFRASTRUCTURE RÉSEAU ---
sse = SseServerTransport("/messages/")

async def handle_sse(request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await server.run(read, write, InitializationOptions(
            server_name="marvel-prompts", server_version="1.0.0",
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
    print("🚀 Serveur MCP Prompts démarré sur http://127.0.0.1:8006")
    uvicorn.run(starlette_app, host="127.0.0.1", port=8006)
