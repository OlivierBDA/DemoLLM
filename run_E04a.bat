@echo off
title Demo LLM - E04a MCP Server (Templates)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur MCP Templates (Port 8002)...
python E04a_mcp_server_templates.py
echo.
echo === Serveur MCP arrete ===
pause
