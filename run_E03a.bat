@echo off
title Demo LLM - E03a MCP Server (Resources)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur MCP Marvel Resources (Port 8001)...
python E03a_mcp_server_resources.py
echo.
echo === Serveur MCP arrete ===
pause
