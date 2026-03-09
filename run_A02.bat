@echo off
title Demo LLM - A02 Chat Terminal
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement de A02_chat_terminal.py...
python A02_chat_terminal.py
echo.
echo === Fin de l'execution ===
pause
