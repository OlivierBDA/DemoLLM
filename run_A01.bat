@echo off
title Demo LLM - A01 Simple API
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement de A01_simple_api.py...
python A01_simple_api.py
echo.
echo === Fin de l'execution ===
pause
