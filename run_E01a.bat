@echo off
title Demo LLM - E01a MCP Server (Discovery)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur MCP Marvel Combat (Port 8000)...
python E01a_mcp_server.py
echo.
echo === Serveur MCP arrete ===
pause
