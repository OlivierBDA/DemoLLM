@echo off
title Demo LLM - D01a Combat API
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement du service API de combat...
python D01a_combat_service.py
echo.
echo === Service API arrete ===
pause
