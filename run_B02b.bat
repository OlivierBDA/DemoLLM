@echo off
title Demo LLM - B02b Query RAG
cd /d "%~dp0"
echo Activation de l'environnement virtuel...
call .venv\Scripts\activate.bat
echo Lancement de B02b_query_rag.py...
python B02b_query_rag.py
echo.
echo === Fin de l'execution ===
pause
