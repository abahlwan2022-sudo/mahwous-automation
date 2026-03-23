# مهووس — أتمتة إدراج العطور على سلة
# Mahwous — Perfume Product Automation for Salla

تطبيق ويب متكامل لأتمتة إدراج منتجات العطور على منصة سلة، مع توليد أوصاف احترافية محسّنة SEO باستخدام الذكاء الاصطناعي.

---

## 🚀 خطوات الرفع على Railway

### 1. تجهيز المشروع
```bash
git init
git add .
git commit -m "initial: mahwous automation app"
```

### 2. رفع على GitHub
```bash
gh repo create mahwous-automation --private
git remote add origin https://github.com/YOUR_USERNAME/mahwous-automation.git
git push -u origin main
```

### 3. النشر على Railway
1. اذهب إلى [railway.app](https://railway.app) وسجّل الدخول
2. انقر **New Project → Deploy from GitHub repo**
3. اختر مستودع `mahwous-automation`
4. في تبويب **Variables**، أضف:
   - `ANTHROPIC_API_KEY` = مفتاح Claude API الخاص بك
   - `GOOGLE_API_KEY` = مفتاح Google (اختياري، لجلب الصور)
   - `GOOGLE_CSE_ID` = معرف محرك البحث المخصص (اختياري)
5. Railway سيبني ويشغّل التطبيق تلقائياً.
6. ستحصل على رابط مثل: `https://mahwous-automation.railway.app`

---

## 🏗 هيكل المشروع
```
mahwous-app/
├── app.py                  # الخادم الرئيسي Flask
├── requirements.txt        # مكتبات Python
├── Dockerfile              # إعداد الحاوية
├── railway.toml            # إعداد Railway
├── .env.example            # نموذج متغيرات البيئة
├── templates/
│   └── index.html          # واجهة المستخدم الكاملة
└── data/
    ├── brands.csv          # قاعدة بيانات الماركات
    ├── categories.csv      # قاعدة بيانات التصنيفات
    └── new_product_template.csv
```

---

## 🛠 الميزات

| الميزة | الوصف |
|--------|-------|
| 🤖 AI Description | وصف احترافي 1200-1500 كلمة بـ HTML جاهز لسلة |
| 🏷 Brand Matching | مطابقة تلقائية للماركة من اسم العطر |
| 📂 Category Matching | تعيين تلقائي للتصنيف (رجالي/نسائي/للجنسين) |
| 🔍 SEO Generation | عنوان، وصف، URL، Alt Text، Tags |
| 🖼 Image Fetching | جلب صورة تلقائي عبر Google Image Search |
| 📊 CSV/XLSX Export | تصدير متوافق 100% مع قالب سلة |
| 📦 Batch Mode | معالجة حتى 20 عطر دفعة واحدة |

---

## 🔑 الحصول على API Keys

### Anthropic Claude API
1. اذهب إلى [console.anthropic.com](https://console.anthropic.com)
2. أنشئ حساباً جديداً
3. من **API Keys** → **Create Key**
4. انسخ المفتاح وضعه في `ANTHROPIC_API_KEY`

### Google Custom Search API (اختياري)
1. اذهب إلى [console.cloud.google.com](https://console.cloud.google.com)
2. أنشئ مشروعاً جديداً
3. فعّل **Custom Search API**
4. أنشئ **API Key** من Credentials
5. اذهب إلى [programmablesearchengine.google.com](https://programmablesearchengine.google.com)
6. أنشئ محرك بحث جديد، فعّل **Image Search**
7. انسخ **Search Engine ID**

---

## 💻 التشغيل المحلي

```bash
# إنشاء بيئة افتراضية
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# تثبيت المكتبات
pip install -r requirements.txt

# إعداد متغيرات البيئة
cp .env.example .env
# عدّل ملف .env وأضف مفاتيحك

# تشغيل التطبيق
python app.py
# افتح: http://localhost:8080
```

---

## 📋 تحديث قواعد البيانات

لتحديث الماركات أو التصنيفات، استبدل الملفات في مجلد `data/`:
- `data/brands.csv` → ماركات مهووس
- `data/categories.csv` → تصنيفات مهووس

التنسيق المطلوب محفوظ من الملفات الأصلية المرفوعة.

---

*مشروع مهووس — عالمك العطري يبدأ من مهووس*
