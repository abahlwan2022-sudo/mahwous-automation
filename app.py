"""
Mahwous (مهووس) - Perfume Product Automation System
Full-Stack Flask Application for Salla Platform CSV Generation
"""

import os
import json
import re
import csv
import io
import unicodedata
from flask import Flask, request, jsonify, send_file, render_template_string
import pandas as pd
import anthropic
import requests
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
import tempfile

app = Flask(__name__)

# ─── CONFIG ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY    = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID     = os.environ.get("GOOGLE_CSE_ID", "")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BRANDS_FILE     = os.path.join(DATA_DIR, "brands.csv")
CATEGORIES_FILE = os.path.join(DATA_DIR, "categories.csv")

# ─── DATA LOADING ──────────────────────────────────────────────────────────────
def load_brands():
    try:
        df = pd.read_csv(BRANDS_FILE, encoding="utf-8-sig")
        brands = []
        for _, row in df.iterrows():
            brands.append({
                "name":        str(row.get("اسم الماركة", "") or ""),
                "description": str(row.get("وصف مختصر عن الماركة", "") or ""),
                "logo":        str(row.get("صورة شعار الماركة", "") or ""),
                "page_url":    str(row.get("(SEO Page URL) رابط صفحة العلامة التجارية", "") or ""),
                "page_title":  str(row.get("(Page Title) عنوان صفحة العلامة التجارية", "") or ""),
            })
        return brands
    except Exception as e:
        print(f"Error loading brands: {e}")
        return []

def load_categories():
    try:
        df = pd.read_csv(CATEGORIES_FILE, encoding="utf-8-sig")
        cats = []
        for _, row in df.iterrows():
            cats.append({
                "name":       str(row.get("التصنيفات", "") or ""),
                "is_sub":     str(row.get("هل التصنيف فرعي ام لا", "") or ""),
                "parent":     str(row.get("التصنيف الاساسي", "") or ""),
                "page_link":  str(row.get("رابط مخصص للتصنيف (Page Link)", "") or ""),
            })
        return cats
    except Exception as e:
        print(f"Error loading categories: {e}")
        return []

BRANDS     = load_brands()
CATEGORIES = load_categories()

# ─── MATCHING LOGIC ────────────────────────────────────────────────────────────
def match_brand(perfume_name: str) -> dict:
    """Find matching brand from perfume name using fuzzy keyword matching."""
    name_lower = perfume_name.lower()
    # Arabic + English brand keywords
    for brand in BRANDS:
        brand_name = brand["name"]
        parts = re.split(r"\s*\|\s*", brand_name)
        for part in parts:
            part_clean = part.strip().lower()
            if part_clean and part_clean in name_lower:
                return brand
    return {"name": "", "description": "", "logo": "", "page_url": "", "page_title": ""}

def match_category(perfume_name: str, gender: str = "unisex") -> str:
    """Return Salla category path like 'العطور > عطور رجالية'."""
    name_lower = perfume_name.lower()
    gender_lower = gender.lower()

    # Gender keywords
    male_words   = ["رجال", "للرجال", "رجالي", "men", "homme", "man"]
    female_words = ["نساء", "للنساء", "نسائي", "women", "femme", "woman", "ladies"]

    is_male   = any(w in name_lower or w in gender_lower for w in male_words)
    is_female = any(w in name_lower or w in gender_lower for w in female_words)

    if is_male:
        return "العطور > عطور رجالية"
    elif is_female:
        return "العطور > عطور نسائية"
    else:
        return "العطور > عطور للجنسين"

# ─── SYSTEM PROMPT ─────────────────────────────────────────────────────────────
def build_system_prompt():
    return """أنت كاتب محتوى خبير عالمي في صناعة العطور الفاخرة، متخصص في كتابة أوصاف منتجات احترافية محسّنة لمحركات البحث التقليدية (Google SEO) ومحركات بحث الذكاء الاصطناعي (GEO/AIO). تعمل حصرياً لمتجر "مهووس" (Mahwous) - الوجهة الأولى للعطور الفاخرة في السعودية.

## هويتك ومهمتك
**من أنت:**
- خبير عطور محترف مع 15+ سنة خبرة في صناعة العطور الفاخرة
- متخصص في SEO و Generative Engine Optimization (GEO)
- كاتب محتوى عربي بارع بأسلوب راقٍ، ودود، عاطفي، وتسويقي مقنع
- تمثل صوت متجر "مهووس" بكل احترافية وثقة

**مهمتك:**
كتابة أوصاف منتجات عطور شاملة، احترافية، ومحسّنة بشكل علمي صارم لتحقيق:
1. تصدر نتائج البحث في Google (الصفحة الأولى)
2. الظهور في إجابات محركات بحث الذكاء الاصطناعي (ChatGPT, Gemini, Perplexity)
3. زيادة معدل التحويل (Conversion Rate) بنسبة 40-60%
4. تعزيز ثقة العملاء (E-E-A-T: Experience, Expertise, Authoritativeness, Trustworthiness)

## القواعد العلمية الصارمة للكلمات المفتاحية

### 1. هرمية الكلمات المفتاحية (إلزامية)
**المستوى 1: الكلمة الرئيسية (Primary Keyword)**
- الصيغة: "عطر [الماركة] [اسم العطر] [التركيز] [الحجم] [للجنس]"
- مثال: "عطر أكوا دي بارما كولونيا إنتنسا أو دو كولون 180 مل للرجال"
- التكرار: 5-7 مرات في وصف 1200 كلمة
- الكثافة: 1.5-2%

**المستوى 2: الكلمات الثانوية (3 كلمات)**
- التكرار: 3-5 مرات لكل كلمة
- الكثافة: 0.5-1% لكل كلمة

**المستوى 3: الكلمات الدلالية (LSI) (10-15 كلمة)**
- الفئات: صفات، مكونات، أحاسيس، مناسبات
- التكرار: 2-3 مرات لكل كلمة

**المستوى 4: الكلمات الحوارية (5-8 عبارات)**
- أنماط: "أبحث عن عطر...", "ما هو أفضل...", "هل يناسب..."

### 2. خريطة المواقع الاستراتيجية (إلزامية)
**الأولوية القصوى:**
- H1 (العنوان الرئيسي): يجب أن يطابق الكلمة الرئيسية 100%
- أول 100 كلمة (الفقرة الذهبية): الكلمة الرئيسية في أول 50 كلمة
- آخر 100 كلمة: تكرار الكلمة الرئيسية

## قواعد الأسلوب الصارمة
- ممنوع منعاً باتاً استخدام الرموز التعبيرية (Emojis) نهائياً
- استخدم الخط العريض (Bold) للكلمات المفتاحية فقط بصيغة HTML: <strong>
- دائماً اكتب تركيز العطر بالعربية: "أو دو بارفيوم"
- أسلوبك: راقٍ 40%، ودود 25%، رومانسي 20%، تسويقي مقنع 15%
- الطول المطلوب: 1200 - 1500 كلمة بالضبط

## تنسيق الإخراج (HTML)
يجب أن يكون الإخراج بتنسيق HTML كامل ومتوافق مع محرر Salla، يستخدم:
- <h2> للعنوان الرئيسي
- <h3> للعناوين الفرعية
- <p> للفقرات
- <ul><li> للقوائم النقطية
- <strong> للكلمات المفتاحية والبولد
- <a href="..."> للروابط الداخلية

## هيكل الوصف الإلزامي (10 أقسام)

### القسم 1: العنوان الرئيسي H2
**للعطر العادي:**
<h2>عطر [الماركة] [اسم العطر] [التركيز] [الحجم] [للجنس]</h2>

**للتستر:**
<h2>تستر [الماركة] [اسم العطر] أو دو بارفيوم [الحجم] [للجنس]</h2>

### القسم 2: الفقرة الذهبية (100-150 كلمة)
- عاطفية ورومانسية تشد القارئ
- الكلمة الرئيسية في أول 50 كلمة
- ذكر الماركة والإصدار بوضوح
- دعوة للشراء طبيعية وغير مباشرة

### القسم 3: تفاصيل المنتج
<h3>تفاصيل المنتج</h3>
<ul>
  <li><strong>الماركة:</strong> [اسم الماركة عربي | إنجليزي] مع رابط داخلي إن وجد</li>
  <li><strong>اسم العطر:</strong> [الاسم]</li>
  <li><strong>الجنس:</strong> [للرجال/للنساء/للجنسين]</li>
  <li><strong>العائلة العطرية:</strong> [شرقي/زهري/خشبي/...]</li>
  <li><strong>الحجم:</strong> [XX مل]</li>
  <li><strong>التركيز:</strong> أو دو بارفيوم / أو دو كولون / إلخ</li>
  <li><strong>الإصدار:</strong> [سنة الإصدار أو "كلاسيكي"]</li>
  <li><strong>نوع المنتج:</strong> [تستر / عادي]</li>
</ul>

### القسم 4: رحلة العطر (الهرم العطري)
<h3>رحلة العطر - الهرم العطري</h3>
وصف حسي للنوتات الثلاث:
- المقدمة (Top Notes): أول 15-30 دقيقة
- القلب (Heart/Middle Notes): 30 دقيقة - 4 ساعات
- القاعدة (Base Notes): 4+ ساعات مع التركيز على الثبات

### القسم 5: لماذا تختار هذا العطر؟
<h3>لماذا تختار [اسم العطر]؟</h3>
4-5 نقاط تبدأ بكلمة مفتاحية Bold:
- الثبات والفوحان
- التميز والأصالة
- الجاذبية والقوة
- القيمة الاقتصادية (خاصة للتستر)

### القسم 6: متى وأين ترتدي هذا العطر؟
<h3>متى وأين ترتدي [اسم العطر]؟</h3>
- الفصول المناسبة
- الأوقات (صباح/مساء/ليل)
- المناسبات (يومي/رسمي/رومانسي)
- الفئة العمرية المناسبة

### القسم 7: لمسة خبير من مهووس
<h3>لمسة خبير من مهووس</h3>
استخدم "نحن" (E-E-A-T):
- تحليل حسي عميق وتخصصي
- قوة الثبات والفوحان
- نصيحة رش (Layering Tips)

### القسم 8: الأسئلة الشائعة
<h3>الأسئلة الشائعة (FAQ)</h3>
6 أسئلة وأجوبة تخدم بحث الذكاء الاصطناعي تشمل:
- كم يدوم العطر؟
- هل يناسب الاستخدام اليومي؟
- ما الفرق بين التستر والعطر العادي؟
- ما العائلة العطرية؟
- هل يناسب الطقس الحار في السعودية؟
- ما مناسبات ارتداء هذا العطر؟

### القسم 9: اكتشف المزيد
<h3>اكتشف المزيد من عطور مهووس</h3>
3 روابط داخلية لأقسام المتجر:
- رابط لقسم الماركة
- رابط لقسم التصنيف (رجالي/نسائي)
- رابط لصفحة العروض أو الأكثر مبيعاً

### القسم 10: الخاتمة
فقرة ختامية تتضمن:
- رسالة طمأنة: أصلي 100%، شحن سريع داخل السعودية
- ختام بشعار المتجر: "عالمك العطري يبدأ من مهووس"

---

## معايير الجودة الإلزامية (Checklist)
قبل تسليم الوصف، تحقق من:
✓ الطول: 1200-1500 كلمة
✓ الكلمة الرئيسية في H2 ✓
✓ الكلمة الرئيسية في أول 50 كلمة ✓
✓ لا توجد Emojis ✓
✓ Bold على الكلمات المفتاحية فقط ✓
✓ "أو دو بارفيوم" بالعربية ✓
✓ 6 أسئلة FAQ ✓
✓ 3 روابط داخلية ✓
✓ HTML صحيح ومتوافق ✓"""

# ─── AI DESCRIPTION GENERATOR ─────────────────────────────────────────────────
def generate_description(perfume_name: str, is_tester: bool, brand: dict,
                          category: str, size: str = "", gender: str = "للجنسين",
                          concentration: str = "أو دو بارفيوم") -> str:
    """Call Claude API to generate the full HTML product description."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    brand_link = ""
    if brand.get("page_url"):
        brand_link = f'<a href="https://mahwous.com/{brand["page_url"]}" target="_blank">{brand["name"]}</a>'
    else:
        brand_link = brand.get("name", "")

    product_type = "تستر" if is_tester else "عطر"
    tester_note  = " (تستر)" if is_tester else ""

    user_prompt = f"""اكتب وصفاً احترافياً كاملاً بالـ HTML لمنتج العطر التالي:

**اسم العطر:** {perfume_name}
**الماركة:** {brand.get('name', 'غير محدد')} — رابط الماركة: {brand_link}
**التصنيف:** {category}
**الحجم:** {size if size else '100 مل'}
**التركيز:** {concentration}
**الجنس:** {gender}
**نوع المنتج:** {product_type}{tester_note}
**هل هو تستر:** {'نعم' if is_tester else 'لا'}

روابط داخلية مهووس للاستخدام في "اكتشف المزيد":
1. عطور {brand.get('name', '')} الكاملة: https://mahwous.com/{brand.get('page_url', 'brands')}
2. قسم العطور الرجالية: https://mahwous.com/عطور-رجالية
3. قسم العطور النسائية: https://mahwous.com/عطور-نسائية
4. الأكثر مبيعاً: https://mahwous.com/الأكثر-مبيعاً

التزم بالهيكل الـ 10 أقسام المحدد في تعليماتك. الإخراج يجب أن يكون HTML خالصاً متوافقاً مع Salla.
الطول المطلوب: 1200-1500 كلمة."""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=build_system_prompt(),
        messages=[{"role": "user", "content": user_prompt}]
    )
    return message.content[0].text

# ─── SEO GENERATOR ─────────────────────────────────────────────────────────────
def generate_seo_data(perfume_name: str, brand: dict, size: str,
                      is_tester: bool, gender: str) -> dict:
    """Generate all SEO fields for Salla."""
    product_type = "تستر" if is_tester else "عطر"

    # Page title
    brand_en = ""
    if brand.get("name"):
        parts = re.split(r"\s*\|\s*", brand["name"])
        brand_en = parts[-1].strip() if len(parts) > 1 else parts[0].strip()
    page_title = f"{perfume_name} {size} | {brand_en}"

    # Page description (160 chars max)
    base_desc = f"تسوق {perfume_name} الأصلي {size} من {brand.get('name', '')}. عطر {gender} فاخر بثبات استثنائي. أصلي 100% من مهووس."
    if len(base_desc) > 160:
        base_desc = base_desc[:157] + "..."

    # URL slug
    en_name = transliterate_arabic(perfume_name)
    size_slug = size.lower().replace(" ", "").replace("مل", "ml").replace("مل", "ml")
    url = f"{en_name}-{size_slug}".replace("--", "-").strip("-")

    # Alt text
    alt_text = f"زجاجة {product_type} {perfume_name} {size} الأصلية"

    # Tags
    tags = generate_tags(perfume_name, brand, is_tester, gender)

    return {
        "page_title":   page_title,
        "page_desc":    base_desc,
        "url":          url,
        "alt_text":     alt_text,
        "tags":         tags,
    }

def transliterate_arabic(text: str) -> str:
    """Simple Arabic to Latin transliteration for URL slugs."""
    ar_to_en = {
        'ا': 'a', 'أ': 'a', 'إ': 'e', 'آ': 'a',
        'ب': 'b', 'ت': 't', 'ث': 'th', 'ج': 'j',
        'ح': 'h', 'خ': 'kh', 'د': 'd', 'ذ': 'z',
        'ر': 'r', 'ز': 'z', 'س': 's', 'ش': 'sh',
        'ص': 's', 'ض': 'd', 'ط': 't', 'ظ': 'z',
        'ع': 'a', 'غ': 'gh', 'ف': 'f', 'ق': 'q',
        'ك': 'k', 'ل': 'l', 'م': 'm', 'ن': 'n',
        'ه': 'h', 'و': 'w', 'ي': 'y', 'ى': 'a',
        'ة': 'a', 'ء': '', 'ئ': 'y', 'ؤ': 'w',
        'لا': 'la',
    }
    result = ""
    for ch in text.lower():
        if ch in ar_to_en:
            result += ar_to_en[ch]
        elif ch.isascii() and (ch.isalnum() or ch in " -"):
            result += ch
        elif ch == " ":
            result += "-"
    result = re.sub(r'-+', '-', result).strip('-')
    return result or "perfume"

def generate_tags(perfume_name: str, brand: dict, is_tester: bool, gender: str) -> list:
    tags = [
        perfume_name,
        brand.get("name", ""),
        "عطور مهووس",
        "عطور اصلية",
        "mahwous",
        "عطور فاخرة",
        "عطور السعودية",
    ]
    if is_tester:
        tags += ["تستر عطر", "tester perfume", "عطر تستر أصلي"]
    if "رجال" in gender or "men" in gender.lower():
        tags += ["عطور رجالية", "men perfume", "عطر رجالي فاخر"]
    elif "نساء" in gender or "women" in gender.lower():
        tags += ["عطور نسائية", "women perfume", "عطر نسائي فاخر"]
    else:
        tags += ["عطور للجنسين", "unisex perfume"]

    brand_en = ""
    if brand.get("name"):
        parts = re.split(r"\s*\|\s*", brand["name"])
        brand_en = parts[-1].strip() if len(parts) > 1 else ""
    if brand_en:
        tags.append(brand_en.lower())

    return [t for t in tags if t.strip()]

# ─── IMAGE FETCHER ─────────────────────────────────────────────────────────────
def fetch_perfume_image(perfume_name: str, is_tester: bool) -> str:
    """Search Google Images for perfume bottle image."""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        return ""
    try:
        suffix = " tester bottle" if is_tester else " perfume bottle"
        query  = perfume_name + suffix
        url    = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key":        GOOGLE_API_KEY,
            "cx":         GOOGLE_CSE_ID,
            "q":          query,
            "searchType": "image",
            "num":        1,
            "imgSize":    "large",
            "imgType":    "photo",
        }
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if "items" in data and data["items"]:
            return data["items"][0]["link"]
    except Exception as e:
        print(f"Image fetch error: {e}")
    return ""

# ─── CSV / XLSX EXPORT ─────────────────────────────────────────────────────────
SALLA_COLUMNS = [
    "النوع", "أسم المنتج", "تصنيف المنتج", "صورة المنتج", "وصف صورة المنتج",
    "نوع المنتج", "سعر المنتج", "الوصف", "هل يتطلب شحن؟", "رمز المنتج sku",
    "سعر التكلفة", "السعر المخفض", "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض",
    "اقصي كمية لكل عميل", "إخفاء خيار تحديد الكمية", "اضافة صورة عند الطلب",
    "الوزن", "وحدة الوزن", "الماركة", "العنوان الترويجي", "تثبيت المنتج",
    "الباركود", "السعرات الحرارية", "MPN", "GTIN", "خاضع للضريبة ؟",
    "سبب عدم الخضوع للضريبة", "[1] الاسم", "[1] النوع", "[1] القيمة", "[1] الصورة / اللون"
]

def build_salla_row(product_name, category, image_url, alt_text, description,
                    brand_name, price, sku) -> dict:
    row = {col: "" for col in SALLA_COLUMNS}
    row["النوع"]                  = "منتج"
    row["أسم المنتج"]             = product_name
    row["تصنيف المنتج"]          = category
    row["صورة المنتج"]           = image_url
    row["وصف صورة المنتج"]       = alt_text
    row["نوع المنتج"]            = "منتج جاهز"
    row["سعر المنتج"]            = price
    row["الوصف"]                 = description
    row["هل يتطلب شحن؟"]        = "نعم"
    row["رمز المنتج sku"]        = sku
    row["الوزن"]                 = "0.2"
    row["وحدة الوزن"]            = "kg"
    row["الماركة"]               = brand_name
    row["خاضع للضريبة ؟"]       = "نعم"
    row["اقصي كمية لكل عميل"]   = "0"
    row["إخفاء خيار تحديد الكمية"] = "0"
    row["اضافة صورة عند الطلب"] = "0"
    return row

def export_salla_csv(rows: list) -> bytes:
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=SALLA_COLUMNS)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8-sig")

def export_salla_xlsx(rows: list) -> bytes:
    """Export as Excel matching Salla's exact 2-row-header format."""
    from openpyxl import Workbook
    wb = Workbook()
    ws = wb.active
    ws.title = "Salla Products Template Sheet"

    # Row 1: section headers (matching Salla template)
    ws.cell(1, 1, "بيانات المنتج")
    for col in range(2, len(SALLA_COLUMNS) + 1):
        ws.cell(1, col, "")

    # Style row 1
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="1a1a2e")
        cell.alignment = Alignment(horizontal="center", vertical="center")

    # Row 2: column names
    for i, col_name in enumerate(SALLA_COLUMNS, 1):
        cell = ws.cell(2, i, col_name)
        cell.font = Font(bold=True)
        cell.fill = PatternFill("solid", fgColor="E8D5B7")
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)

    # Data rows starting from row 3
    for row_idx, row_data in enumerate(rows, 3):
        for col_idx, col_name in enumerate(SALLA_COLUMNS, 1):
            ws.cell(row_idx, col_idx, row_data.get(col_name, ""))

    # Adjust column widths
    for col in ws.columns:
        max_len = max((len(str(cell.value or "")) for cell in col), default=10)
        ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()

# ─── ROUTES ────────────────────────────────────────────────────────────────────
@app.route("/health")
def health():
    return "OK", 200

@app.route("/")
def index():
    return render_template_string(open(
        os.path.join(os.path.dirname(__file__), "templates", "index.html")
    ).read())

@app.route("/api/brands", methods=["GET"])
def api_brands():
    return jsonify([{"name": b["name"], "page_url": b["page_url"]} for b in BRANDS])

@app.route("/api/categories", methods=["GET"])
def api_categories():
    return jsonify(CATEGORIES)

@app.route("/api/match", methods=["POST"])
def api_match():
    """Auto-match brand and category from perfume name."""
    data = request.json or {}
    perfume_name = data.get("name", "")
    gender       = data.get("gender", "unisex")
    brand    = match_brand(perfume_name)
    category = match_category(perfume_name, gender)
    return jsonify({"brand": brand, "category": category})

@app.route("/api/generate", methods=["POST"])
def api_generate():
    """Generate full product data: description + SEO."""
    data = request.json or {}
    perfume_name  = data.get("name", "").strip()
    is_tester     = data.get("is_tester", False)
    gender        = data.get("gender", "للجنسين")
    size          = data.get("size", "100 مل")
    concentration = data.get("concentration", "أو دو بارفيوم")
    price         = data.get("price", "")
    image_url     = data.get("image_url", "")
    sku           = data.get("sku", "")

    if not perfume_name:
        return jsonify({"error": "اسم العطر مطلوب"}), 400
    if not ANTHROPIC_API_KEY:
        return jsonify({"error": "مفتاح API غير مضبوط"}), 500

    brand    = match_brand(perfume_name)
    category = match_category(perfume_name, gender)

    # Fetch image if not provided
    if not image_url:
        image_url = fetch_perfume_image(perfume_name, is_tester)

    # Generate AI description
    try:
        description = generate_description(
            perfume_name, is_tester, brand, category, size, gender, concentration
        )
    except Exception as e:
        return jsonify({"error": f"خطأ في توليد الوصف: {str(e)}"}), 500

    # Generate SEO data
    seo = generate_seo_data(perfume_name, brand, size, is_tester, gender)

    # Build product name
    type_prefix = "تستر" if is_tester else "عطر"
    brand_prefix = f" {brand['name']}" if brand.get("name") else ""
    product_name = f"{type_prefix}{brand_prefix} {perfume_name} {concentration} {size} {gender}".strip()

    # Build Salla row
    salla_row = build_salla_row(
        product_name=product_name,
        category=category,
        image_url=image_url,
        alt_text=seo["alt_text"],
        description=description,
        brand_name=brand.get("name", ""),
        price=price,
        sku=sku,
    )

    return jsonify({
        "product_name": product_name,
        "brand":        brand,
        "category":     category,
        "image_url":    image_url,
        "description":  description,
        "seo":          seo,
        "salla_row":    salla_row,
    })

@app.route("/api/export/csv", methods=["POST"])
def api_export_csv():
    data = request.json or {}
    rows = data.get("rows", [])
    if not rows:
        return jsonify({"error": "لا توجد بيانات للتصدير"}), 400
    csv_bytes = export_salla_csv(rows)
    return send_file(
        io.BytesIO(csv_bytes),
        mimetype="text/csv",
        as_attachment=True,
        download_name="mahwous_products.csv"
    )

@app.route("/api/export/xlsx", methods=["POST"])
def api_export_xlsx():
    data = request.json or {}
    rows = data.get("rows", [])
    if not rows:
        return jsonify({"error": "لا توجد بيانات للتصدير"}), 400
    xlsx_bytes = export_salla_xlsx(rows)
    return send_file(
        io.BytesIO(xlsx_bytes),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="mahwous_products.xlsx"
    )

@app.route("/api/batch", methods=["POST"])
def api_batch():
    """Process multiple perfume names at once."""
    data = request.json or {}
    names = data.get("names", [])
    is_tester = data.get("is_tester", False)
    gender    = data.get("gender", "للجنسين")
    results   = []

    for name in names[:20]:  # Limit to 20 per batch
        try:
            brand    = match_brand(name)
            category = match_category(name, gender)
            seo      = generate_seo_data(name, brand, "100 مل", is_tester, gender)
            image_url = fetch_perfume_image(name, is_tester)

            desc = generate_description(
                name, is_tester, brand, category, "100 مل", gender
            )

            type_prefix = "تستر" if is_tester else "عطر"
            product_name = f"{type_prefix} {brand.get('name','')} {name} أو دو بارفيوم 100 مل {gender}".strip()

            row = build_salla_row(
                product_name=product_name,
                category=category,
                image_url=image_url,
                alt_text=seo["alt_text"],
                description=desc,
                brand_name=brand.get("name", ""),
                price="",
                sku="",
            )
            results.append({"name": name, "success": True, "row": row, "seo": seo})
        except Exception as e:
            results.append({"name": name, "success": False, "error": str(e)})

    return jsonify({"results": results})

if __name__ == "__main__":
    # Port is fixed to 8080 for stability on Railway
    app.run(host="0.0.0.0", port=8080, debug=False)
