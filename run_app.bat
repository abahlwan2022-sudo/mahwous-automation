@echo off
chcp 65001 >nul
cd /d "%~dp0"
title مهووس — Streamlit
echo تشغيل التطبيق على http://127.0.0.1:8501 ...
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
if errorlevel 1 py -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --browser.gatherUsageStats false
pause
