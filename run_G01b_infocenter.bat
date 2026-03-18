@echo off
set PORT=8082
call .venv\Scripts\activate.bat
echo Lancement du Serveur A2A Info Center sur le port %PORT%...
adk api_server --port %PORT% --a2a a2a_agents_infocenter
pause
