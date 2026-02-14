import asyncio
import os
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types
import sqlite3
import pandas as pd

# Initialisation du serveur MCP
server = Server("marvel-mcp-server")

# --- Phase E : Étape 1 : Le Serveur MCP ---
# Les ressources sont des données statiques ou dynamiques accessibles en lecture seule.
@server.list_resources()
async def handle_list_resources() -> list[types.Resource]:
    """Liste les fiches personnages disponibles."""
    resources = []
    data_path = "data/source_files"
    if os.path.exists(data_path):
        for file in os.listdir(data_path):
            if file.startswith("hero_") and file.endswith(".txt"):
                hero_id = file.replace("hero_", "").replace(".txt", "")
                resources.append(
                    types.Resource(
                        uri=f"marvel://character/{hero_id}",
                        name=f"Fiche de {hero_id.replace('_', ' ').title()}",
                        description=f"Données brutes pour le personnage {hero_id}",
                        mimeType="text/plain",
                    )
                )
    return resources

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Lit le contenu d'une fiche personnage via son URI marvel://."""
    if not uri.startswith("marvel://character/"):
        raise ValueError(f"URI inconnue : {uri}")
    
    hero_id = uri.replace("marvel://character/", "")
    file_path = f"data/source_files/hero_{hero_id}.txt"
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    raise ValueError(f"Personnage non trouvé : {hero_id}")

# --- CONCEPTS MCP 2 : LES OUTILS (TOOLS) ---
# Les outils sont des fonctions que le LLM peut appeler.
@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """Définit les capacités d'action."""
    return [
        types.Tool(
            name="query_marvel_db",
            description="Exécute une requête SQL SELECT sur la base Marvel (tables: heroes, movies, hero_appearances).",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {"type": "string", "description": "La requête SQL SELECT validée."}
                },
                "required": ["sql_query"],
            },
        ),
        types.Tool(
            name="calculate_power_level",
            description="Simule un calcul de puissance basé sur l'ID du héros.",
            inputSchema={
                "type": "object",
                "properties": {
                    "hero_name": {"type": "string", "description": "Nom du héros."}
                },
                "required": ["hero_name"],
            },
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Exécute l'outil demandé."""
    if name == "query_marvel_db":
        sql = arguments.get("sql_query")
        try:
            conn = sqlite3.connect("data/marvel_data.db")
            df = pd.read_sql_query(sql, conn)
            conn.close()
            return [types.TextContent(type="text", text=df.to_markdown())]
        except Exception as e:
            return [types.TextContent(type="text", text=f"Erreur SQL : {str(e)}")]
            
    elif name == "calculate_power_level":
        hero = arguments.get("hero_name", "Inconnu")
        # Logique bidon pour la démo
        power = len(hero) * 10 
        return [types.TextContent(type="text", text=f"Puissance estimée de {hero} : {power}/100")]
        
    raise ValueError(f"Outil inconnu : {name}")

# --- CONCEPTS MCP 3 : LES PROMPTS ---
# Les prompts sont des modèles réutilisables.
@server.list_prompts()
async def handle_list_prompts() -> list[types.Prompt]:
    """Liste les prompts pré-configurés."""
    return [
        types.Prompt(
            name="analyse_combat",
            description="Un prompt pour analyser un combat entre deux héros.",
            arguments=[
                types.PromptArgument(name="hero1", description="Premier héros", required=True),
                types.PromptArgument(name="hero2", description="Second héros", required=True),
            ],
        )
    ]

@server.get_prompt()
async def handle_get_prompt(
    name: str, arguments: dict[str, str] | None
) -> types.GetPromptResult:
    """Retourne le contenu du prompt."""
    if name == "analyse_combat":
        h1 = arguments.get("hero1")
        h2 = arguments.get("hero2")
        return types.GetPromptResult(
            description="Analyse de combat",
            messages=[
                types.PromptMessage(
                    role="user",
                    content=types.TextContent(
                        type="text",
                        text=f"En utilisant tes outils et ressources, compare les forces de {h1} et {h2} et prédis le vainqueur."
                    ),
                )
            ],
        )
    raise ValueError(f"Prompt inconnu : {name}")

async def main():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="marvel-mcp",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
