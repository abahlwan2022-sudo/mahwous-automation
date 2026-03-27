# مهووس — مركز التحكم (Streamlit)

تطبيق لمعالجة ملفات سلة: المسار الآلي، SEO، المقارنة، التدقيق، منتج سريع.

## المتطلبات

- Python **3.11** (أو 3.10+)
- ملفات عيّنة في `data/` (ماركات، تصنيفات) — مرفقة مع المشروع

## البداية السريعة (محلي)

```powershell
cd mahwous-automation-master
python -m venv .venv
.\.venv\Scripts\activate
pip install -U pip
pip install -r requirements.txt
copy .env.example .env
# عدّل .env وأضف ANTHROPIC_API_KEY وغيرها إن رغبت
python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501
```

أو انقر نقراً مزدوجاً **`run_app.bat`** (ويندوز).

ثم افتح المتصفح: `http://127.0.0.1:8501`

## متغيرات البيئة (اختياري)

| المتغير | الوصف |
|---------|--------|
| `ANTHROPIC_API_KEY` | Claude — أوصاف، SEO، فلترة مشبوه |
| `GOOGLE_API_KEY` / `GOOGLE_CSE_ID` | جلب صور من Google |
| `MAHWOUS_SITE_BASE` | روابط HTML في الوصف (افتراضي: `https://mahwous.com`) |
| `PUBLIC_APP_URL` | رابط لوحة التطبيق المعروض في الواجهة |

يمكن أيضاً ضبط المفاتيح من **صفحة الإعدادات** داخل التطبيق.

## Docker

```bash
docker build -t mahwous .
docker run -p 8501:8501 -e ANTHROPIC_API_KEY=... mahwous
```

## الاختبارات

```bash
pip install -r requirements.txt
pytest tests/ -q
```

## النشر (Railway)

يُستخدم `Dockerfile` و`railway.toml`. عيّن المتغيرات على المنصة؛ لا ترفع `.env` إلى Git.
