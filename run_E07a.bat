@echo off
title Demo LLM - E07a MCP Server (Prompts)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur Prompts MCP (Port 8006)...
python E07a_mcp_server_prompts.py
echo.
echo === Serveur MCP arrete ===
pause
