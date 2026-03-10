@echo off
title Demo LLM - E06c MCP Admin (Trigger)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du panneau d'administration...
python E06c_mcp_server_admin.py
echo.
echo === Admin arrete ===
pause
