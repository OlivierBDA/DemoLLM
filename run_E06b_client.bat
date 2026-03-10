@echo off
title Demo LLM - E06b MCP Client (HTML Viewer)
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du Client MCP (Générateur HTML)...
python E06b_mcp_client_html.py
echo.
echo === Client MCP arrete ===
pause
