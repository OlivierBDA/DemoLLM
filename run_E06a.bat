@echo off
title Demo LLM - E06a MCP Server (Notifications)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Serveur Web MCP Notification (Port 8004)...
python E06a_mcp_server_notifications.py
echo.
echo === Serveur MCP arrete ===
pause
