@echo off
title Demo LLM - E05a MCP Server (Progress)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur MCP Progress (Port 8003)...
python E05a_mcp_server_progress.py
echo.
echo === Serveur MCP arrete ===
pause
