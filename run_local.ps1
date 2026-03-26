# تشغيل محلي موصى به عند ظهور Connection error / invalid wire type مع Streamlit
# 1) نفّذ: pip install -r requirements.txt
# 2) شغّل: powershell -ExecutionPolicy Bypass -File .\run_local.ps1
# 3) افتح المتصفح يدوياً على العنوان المطبوع (يفضّل Chrome/Edge وليس معاينة IDE)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

$env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
# ربط الخادم على loopback فقط — يقلل التداخل مع منافذ/جلسات أخرى
python -m streamlit run app.py `
  --server.address 127.0.0.1 `
  --server.port 8501 `
  --browser.gatherUsageStats false `
  --server.headless false
