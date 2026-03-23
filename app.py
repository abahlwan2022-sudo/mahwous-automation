"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          مهووس — نظام إدارة منتجات العطور الذكي                            ║
║          Mahwous — AI-Powered Perfume Product Management System             ║
║          Version 2.0 | Streamlit + Anthropic + Google CSE                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, io, re, json, time, unicodedata
from datetime import datetime
import requests

# ── Export libs ──────────────────────────────────────────────────────────────
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (
    Font, PatternFill, Alignment, Border, Side, GradientFill
)
from openpyxl.utils import get_column_letter

# ── AI ────────────────────────────────────────────────────────────────────────
import anthropic

# ═══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="مهووس — إدارة المنتجات",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Cairo', sans-serif; direction: rtl; }

/* Header */
.main-header {
    background: linear-gradient(135deg, #0f0e0d 0%, #1a1510 100%);
    color: #b8933a;
    padding: 1.2rem 2rem;
    border-radius: 14px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
    border: 1px solid rgba(184,147,58,0.3);
}
.main-header h1 { color: #b8933a; font-size: 1.8rem; margin: 0; }
.main-header p  { color: rgba(255,255,255,0.5); font-size: 0.85rem; margin: 0; }

/* Mode card */
.mode-card {
    background: rgba(184,147,58,0.07);
    border: 1px solid rgba(184,147,58,0.25);
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.75rem;
    cursor: pointer;
    transition: all 0.2s;
}
.mode-card:hover { border-color: #b8933a; background: rgba(184,147,58,0.12); }

/* Status badges */
.badge-ok  { background: #e8f5e9; color: #2d7a4f; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; }
.badge-err { background: #fdecea; color: #c62828; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; }
.badge-pend{ background: #fff8e1; color: #f57f17; padding: 3px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 700; }

/* Progress rows */
.proc-row {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: 8px;
    background: rgba(0,0,0,0.02);
    margin-bottom: 4px; font-size: 0.875rem;
}

/* Metric card */
.metric-card {
    background: #fff;
    border: 1px solid #e8e2d9;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.metric-card .num  { font-size: 2rem; font-weight: 700; color: #b8933a; }
.metric-card .lbl  { font-size: 0.8rem; color: #7a6e68; }

/* Divider */
.gold-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #b8933a, transparent);
    margin: 1.5rem 0;
    border: none;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# CONSTANTS — SALLA EXACT COLUMN SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

# Full Salla product update template columns (exact order)
SALLA_PRODUCT_COLS = [
    "No.", "النوع ", "أسم المنتج", "تصنيف المنتج", "صورة المنتج",
    "وصف صورة المنتج", "نوع المنتج", "سعر المنتج", "الوصف",
    "هل يتطلب شحن؟", "رمز المنتج sku", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض", "اقصي كمية لكل عميل",
    "إخفاء خيار تحديد الكمية", "اضافة صورة عند الطلب", "الوزن", "وحدة الوزن",
    "حالة المنتج", "الماركة", "العنوان الترويجي", "تثبيت المنتج", "الباركود",
    "السعرات الحرارية", "MPN", "GTIN", "خاضع للضريبة ؟",
    "سبب عدم الخضوع للضريبة",
    "[1] الاسم", "[1] النوع", "[1] القيمة", "[1] الصورة / اللون",
    "[2] الاسم", "[2] النوع", "[2] القيمة", "[2] الصورة / اللون",
    "[3] الاسم", "[3] النوع", "[3] القيمة", "[3] الصورة / اللون",
]

# Salla SEO template columns
SALLA_SEO_COLS = [
    "No. (غير قابل للتعديل)",
    "اسم المنتج (غير قابل للتعديل)",
    "رابط مخصص للمنتج (SEO Page URL)",
    "عنوان صفحة المنتج (SEO Page Title)",
    "وصف صفحة المنتج (SEO Page Description)",
]

# Price update template
SALLA_PRICE_COLS = [
    "No.", "النوع ", "أسم المنتج", "رمز المنتج sku",
    "سعر المنتج", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ═══════════════════════════════════════════════════════════════════════════════
# SESSION STATE INIT
# ═══════════════════════════════════════════════════════════════════════════════
def init_state():
    defaults = {
        "brands_df":      None,
        "categories_df":  None,
        "working_df":     None,        # The main editable DataFrame
        "results_df":     None,        # After AI processing
        "source_file_name": "",
        "col_map":        {},
        "mode":           "new",       # new | edit | seo_merge | price
        "processing_log": [],
        "api_key":        os.environ.get("ANTHROPIC_API_KEY", ""),
        "google_api_key": os.environ.get("GOOGLE_API_KEY", ""),
        "google_cse_id":  os.environ.get("GOOGLE_CSE_ID", ""),
        "step":           1,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v
    # Auto-load bundled reference data
    if st.session_state.brands_df is None:
        try:
            st.session_state.brands_df = pd.read_csv(
                os.path.join(DATA_DIR, "brands.csv"), encoding="utf-8-sig"
            )
        except: pass
    if st.session_state.categories_df is None:
        try:
            st.session_state.categories_df = pd.read_csv(
                os.path.join(DATA_DIR, "categories.csv"), encoding="utf-8-sig"
            )
        except: pass

init_state()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: READ ANY FILE → DataFrame
# ═══════════════════════════════════════════════════════════════════════════════
def read_any_file(uploaded_file, header_row: int = 0) -> pd.DataFrame:
    """Read CSV or XLSX into DataFrame."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith((".xlsx", ".xlsm", ".xls")):
            df = pd.read_excel(uploaded_file, header=header_row, dtype=str)
        else:
            for enc in ("utf-8-sig", "utf-8", "cp1256", "latin-1"):
                try:
                    uploaded_file.seek(0)
                    df = pd.read_csv(uploaded_file, header=header_row,
                                     encoding=enc, dtype=str)
                    break
                except UnicodeDecodeError:
                    continue
        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return pd.DataFrame()

def read_salla_product_file(uploaded_file) -> pd.DataFrame:
    """Read Salla 2-header-row product file correctly."""
    name = uploaded_file.name.lower()
    try:
        if name.endswith((".xlsx", ".xlsm")):
            df = pd.read_excel(uploaded_file, header=1, dtype=str)
        else:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, header=1, encoding="utf-8-sig", dtype=str)
        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة ملف سلة: {e}")
        return pd.DataFrame()

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: BRAND & CATEGORY MATCHING
# ═══════════════════════════════════════════════════════════════════════════════
def match_brand(perfume_name: str) -> dict:
    brands_df = st.session_state.brands_df
    if brands_df is None or perfume_name.strip() == "":
        return {}
    name_lower = str(perfume_name).lower()
    col_name = "اسم الماركة"
    if col_name not in brands_df.columns:
        col_name = brands_df.columns[0]
    for _, row in brands_df.iterrows():
        brand_raw = str(row.get(col_name, ""))
        parts = re.split(r"\s*\|\s*", brand_raw)
        for p in parts:
            p_clean = p.strip().lower()
            if p_clean and p_clean in name_lower:
                return {
                    "name":     brand_raw,
                    "page_url": str(row.get("(SEO Page URL) رابط صفحة العلامة التجارية", "") or ""),
                }
    return {"name": "", "page_url": ""}

def match_category(perfume_name: str, gender: str = "") -> str:
    n = (str(perfume_name) + " " + str(gender)).lower()
    if any(w in n for w in ["رجال", "للرجال", "men", "homme"]):
        return "العطور > عطور رجالية"
    elif any(w in n for w in ["نساء", "للنساء", "women", "femme"]):
        return "العطور > عطور نسائية"
    return "العطور > عطور للجنسين"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: TRANSLITERATE ARABIC → URL SLUG
# ═══════════════════════════════════════════════════════════════════════════════
def to_slug(text: str) -> str:
    ar = {'ا':'a','أ':'a','إ':'e','آ':'a','ب':'b','ت':'t','ث':'th','ج':'j',
          'ح':'h','خ':'kh','د':'d','ذ':'z','ر':'r','ز':'z','س':'s','ش':'sh',
          'ص':'s','ض':'d','ط':'t','ظ':'z','ع':'a','غ':'gh','ف':'f','ق':'q',
          'ك':'k','ل':'l','م':'m','ن':'n','ه':'h','و':'w','ي':'y','ى':'a',
          'ة':'a','ء':'','ئ':'y','ؤ':'w'}
    out = ""
    for ch in str(text).lower():
        if ch in ar:       out += ar[ch]
        elif ch.isascii() and ch.isalnum(): out += ch
        elif ch in " -_": out += "-"
    return re.sub(r"-+", "-", out).strip("-") or "perfume"

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: GOOGLE IMAGE SEARCH
# ═══════════════════════════════════════════════════════════════════════════════
def fetch_image(perfume_name: str, is_tester: bool = False) -> str:
    gkey = st.session_state.google_api_key
    gcse = st.session_state.google_cse_id
    if not gkey or not gcse:
        return ""
    try:
        q = perfume_name + (" tester box bottle" if is_tester else " perfume bottle")
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": gkey, "cx": gcse, "q": q,
                    "searchType": "image", "num": 1, "imgSize": "large"},
            timeout=10
        )
        items = r.json().get("items", [])
        return items[0]["link"] if items else ""
    except:
        return ""

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER: SEO GENERATION (no AI call needed)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_seo(name: str, brand: dict, size: str,
                 is_tester: bool, gender: str) -> dict:
    brand_en = ""
    if brand.get("name"):
        parts = re.split(r"\s*\|\s*", brand["name"])
        brand_en = parts[-1].strip() if len(parts) > 1 else parts[0]
    prefix = "تستر" if is_tester else "عطر"
    page_title = f"{prefix} {name} {size} | {brand_en}".strip()
    page_desc  = f"تسوق {prefix} {name} {size} الأصلي من {brand.get('name','')}. عطر {gender} فاخر ثابت. أصلي 100% من مهووس."
    if len(page_desc) > 160:
        page_desc = page_desc[:157] + "..."
    url = to_slug(f"{brand_en}-{name}-{size}".replace("مل", "ml"))
    alt = f"زجاجة {prefix} {name} {size} الأصلية"
    return {"url": url, "page_title": page_title, "page_desc": page_desc, "alt": alt}

# ═══════════════════════════════════════════════════════════════════════════════
# AI: SYSTEM PROMPT (injected once)
# ═══════════════════════════════════════════════════════════════════════════════
SYSTEM_PROMPT = """أنت خبير عالمي في كتابة أوصاف منتجات العطور الفاخرة، متخصص في SEO وGEO، تعمل حصرياً لمتجر "مهووس" (Mahwous) في السعودية.

## قواعد الأسلوب الصارمة
- ممنوع منعاً باتاً استخدام الرموز التعبيرية (Emojis)
- اكتب تركيز العطر دائماً: "أو دو بارفيوم"
- أسلوبك: راقٍ 40%، ودود 25%، رومانسي 20%، تسويقي 15%
- الطول: 1200-1500 كلمة
- **الإخراج يجب أن يكون HTML خالصاً فقط** — بدون أي نص خارج الـ HTML

## هيكل الوصف الإلزامي (HTML)
```
<h2>[عطر/تستر] [الماركة] [الاسم] [التركيز] [الحجم] [للجنس]</h2>
<p>فقرة افتتاحية عاطفية (100-150 كلمة). الكلمة المفتاحية في أول 50 كلمة. دعوة للشراء.</p>
<h3>تفاصيل المنتج</h3>
<ul>
  <li><strong>الماركة:</strong> [اسم الماركة مع رابط داخلي إن أُعطي]</li>
  <li><strong>اسم العطر:</strong> ...</li>
  <li><strong>الجنس:</strong> ...</li>
  <li><strong>العائلة العطرية:</strong> ...</li>
  <li><strong>الحجم:</strong> ...</li>
  <li><strong>التركيز:</strong> أو دو بارفيوم</li>
  <li><strong>نوع المنتج:</strong> [تستر/عادي]</li>
</ul>
<h3>رحلة العطر - الهرم العطري</h3>
<ul>
  <li><strong>المقدمة (Top Notes):</strong> ...</li>
  <li><strong>القلب (Heart Notes):</strong> ...</li>
  <li><strong>القاعدة (Base Notes):</strong> ...</li>
</ul>
<h3>لماذا تختار [اسم العطر]؟</h3>
<ul>
  <li><strong>الثبات والفوحان:</strong> ...</li>
  <li><strong>التميز والأصالة:</strong> ...</li>
  <li><strong>القيمة الاستثنائية:</strong> ...</li>
  <li><strong>الجاذبية المضمونة:</strong> ...</li>
</ul>
<h3>متى وأين ترتدي [اسم العطر]؟</h3>
<p>...</p>
<h3>لمسة خبير من مهووس</h3>
<p>...</p>
<h3>الأسئلة الشائعة (FAQ)</h3>
<ul>
  <li><strong>كم يدوم العطر؟</strong> ...</li>
  <li><strong>هل يناسب الاستخدام اليومي؟</strong> ...</li>
  <li><strong>ما الفرق بين التستر والعادي؟</strong> ...</li>
  <li><strong>ما العائلة العطرية؟</strong> ...</li>
  <li><strong>هل يناسب الطقس الحار؟</strong> ...</li>
  <li><strong>ما مناسبات ارتدائه؟</strong> ...</li>
</ul>
<p><strong>اكتشف المزيد:</strong> <a href="https://mahwous.com/brands">تسوق حسب الماركة</a> | <a href="https://mahwous.com/men">عطور رجالية</a> | <a href="https://mahwous.com/women">عطور نسائية</a></p>
<p><strong>عالمك العطري يبدأ من مهووس.</strong> أصلي 100% | شحن سريع داخل السعودية.</p>
```"""

def generate_description(name: str, is_tester: bool, brand: dict,
                          size: str, gender: str, concentration: str) -> str:
    api_key = st.session_state.api_key
    if not api_key:
        return "<p>⚠️ لم يتم ضبط مفتاح Anthropic API</p>"
    client = anthropic.Anthropic(api_key=api_key)
    brand_link = ""
    if brand.get("page_url"):
        brand_link = f'رابط صفحة الماركة: <a href="https://mahwous.com/{brand["page_url"]}">{brand["name"]}</a>'
    ptype = "تستر" if is_tester else "عطر"
    prompt = f"""اكتب وصفاً HTML احترافياً كاملاً للمنتج التالي:
- نوع: {ptype}
- الاسم: {name}
- الماركة: {brand.get("name", "غير محدد")} {brand_link}
- الحجم: {size}
- التركيز: {concentration}
- الجنس: {gender}
- هل هو تستر: {"نعم" if is_tester else "لا"}

أعد HTML خالصاً فقط بدون أي نص خارجي."""
    try:
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text
    except Exception as e:
        return f"<p>خطأ: {e}</p>"

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT: SALLA PRODUCT XLSX  (exact 2-row-header format)
# ═══════════════════════════════════════════════════════════════════════════════
def build_salla_product_xlsx(df: pd.DataFrame) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Salla Products Template Sheet"

    GOLD = "B8933A"; DARK = "0F0E0D"; LIGHT_GOLD = "E8D5B7"; WHITE = "FFFFFF"

    # Row 1 — section header
    ws.cell(1, 1, "بيانات المنتج")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(SALLA_PRODUCT_COLS))
    c = ws.cell(1, 1)
    c.font      = Font(bold=True, color=WHITE, name="Cairo", size=12)
    c.fill      = PatternFill("solid", fgColor=DARK)
    c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    ws.row_dimensions[1].height = 28

    # Row 2 — column headers
    for i, col in enumerate(SALLA_PRODUCT_COLS, 1):
        c = ws.cell(2, i, col)
        c.font      = Font(bold=True, color=DARK, name="Cairo", size=9)
        c.fill      = PatternFill("solid", fgColor=LIGHT_GOLD)
        c.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True, reading_order=2)
        c.border    = Border(
            bottom=Side(style="thin", color=GOLD),
            right=Side(style="hair", color="D5C9B0")
        )
    ws.row_dimensions[2].height = 32

    # Data rows from row 3
    for row_idx, (_, row) in enumerate(df.iterrows(), 3):
        for col_idx, col_name in enumerate(SALLA_PRODUCT_COLS, 1):
            val = row.get(col_name, "") if col_name in df.columns else ""
            c   = ws.cell(row_idx, col_idx, str(val) if pd.notna(val) else "")
            c.alignment = Alignment(
                horizontal="right", vertical="top",
                wrap_text=(col_name == "الوصف"), reading_order=2
            )
            if row_idx % 2 == 0:
                c.fill = PatternFill("solid", fgColor="FAFAF8")
        ws.row_dimensions[row_idx].height = 18

    # Column widths
    widths = {"أسم المنتج": 45, "الوصف": 60, "تصنيف المنتج": 40,
              "صورة المنتج": 50, "الماركة": 25, "No.": 14}
    for i, col in enumerate(SALLA_PRODUCT_COLS, 1):
        w = widths.get(col, 16)
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "A3"

    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.read()

def build_salla_product_csv(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    # Row 1: section header
    out.write("بيانات المنتج" + "," * (len(SALLA_PRODUCT_COLS)-1) + "\n")
    # Row 2: column names
    out.write(",".join(SALLA_PRODUCT_COLS) + "\n")
    # Data
    for _, row in df.iterrows():
        vals = [str(row.get(c,"") if pd.notna(row.get(c,"")) else "") for c in SALLA_PRODUCT_COLS]
        vals = [f'"{v}"' if "," in v or "\n" in v else v for v in vals]
        out.write(",".join(vals) + "\n")
    return out.getvalue().encode("utf-8-sig")

# ═══════════════════════════════════════════════════════════════════════════════
# EXPORT: SALLA SEO XLSX
# ═══════════════════════════════════════════════════════════════════════════════
def build_salla_seo_xlsx(df: pd.DataFrame) -> bytes:
    wb = Workbook(); ws = wb.active
    ws.title = "Salla Product Seo Sheet"
    GOLD = "B8933A"; DARK = "1A1510"; LIGHT = "FFF8E1"

    for i, col in enumerate(SALLA_SEO_COLS, 1):
        c = ws.cell(1, i, col)
        c.font      = Font(bold=True, color="FFFFFF", name="Cairo", size=9)
        c.fill      = PatternFill("solid", fgColor=DARK)
        c.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True, reading_order=2)
        c.border    = Border(bottom=Side(style="medium", color=GOLD))
    ws.row_dimensions[1].height = 30

    for row_idx, (_, row) in enumerate(df.iterrows(), 2):
        for col_idx, col in enumerate(SALLA_SEO_COLS, 1):
            val = row.get(col, "") if col in df.columns else ""
            c   = ws.cell(row_idx, col_idx, str(val) if pd.notna(val) else "")
            c.alignment = Alignment(horizontal="right", vertical="top",
                                    wrap_text=True, reading_order=2)
            if row_idx % 2 == 0:
                c.fill = PatternFill("solid", fgColor=LIGHT)
        ws.row_dimensions[row_idx].height = 18

    for i, col in enumerate(SALLA_SEO_COLS, 1):
        w = {"اسم المنتج (غير قابل للتعديل)": 50,
             "وصف صفحة المنتج (SEO Page Description)": 70,
             "عنوان صفحة المنتج (SEO Page Title)": 55}.get(col, 22)
        ws.column_dimensions[get_column_letter(i)].width = w

    ws.freeze_panes = "A2"
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.read()

def build_salla_seo_csv(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    out.write(",".join(SALLA_SEO_COLS) + "\n")
    for _, row in df.iterrows():
        vals = [str(row.get(c,"") if pd.notna(row.get(c,"")) else "") for c in SALLA_SEO_COLS]
        vals = [f'"{v}"' if "," in v or "\n" in v else v for v in vals]
        out.write(",".join(vals) + "\n")
    return out.getvalue().encode("utf-8-sig")

# ═══════════════════════════════════════════════════════════════════════════════
# BUILD PRODUCT ROW (single row for the working DataFrame)
# ═══════════════════════════════════════════════════════════════════════════════
def build_product_row(
    product_no, name, is_tester, gender, size, concentration,
    price, sku, image_url, description, brand, category, seo
) -> dict:
    row = {col: "" for col in SALLA_PRODUCT_COLS}
    row["No."]                    = str(product_no) if product_no else ""
    row["النوع "]                 = "منتج"
    row["أسم المنتج"]             = str(name)
    row["تصنيف المنتج"]           = category
    row["صورة المنتج"]            = image_url
    row["وصف صورة المنتج"]        = seo.get("alt", "")
    row["نوع المنتج"]             = "منتج جاهز"
    row["سعر المنتج"]             = str(price) if price else ""
    row["الوصف"]                  = description
    row["هل يتطلب شحن؟"]         = "نعم"
    row["رمز المنتج sku"]         = str(sku) if sku else ""
    row["الوزن"]                  = "0.2"
    row["وحدة الوزن"]             = "kg"
    row["حالة المنتج"]            = "مرئي"
    row["الماركة"]                = brand.get("name", "")
    row["خاضع للضريبة ؟"]        = "نعم"
    row["اقصي كمية لكل عميل"]    = "0"
    row["إخفاء خيار تحديد الكمية"] = "0"
    row["اضافة صورة عند الطلب"]  = "0"
    return row

# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## ⚙️ الإعدادات")

    # API Keys
    with st.expander("🔑 مفاتيح API", expanded=False):
        k = st.text_input("Anthropic API Key", value=st.session_state.api_key,
                          type="password", key="inp_ant")
        if k: st.session_state.api_key = k

        gk = st.text_input("Google API Key", value=st.session_state.google_api_key,
                           type="password", key="inp_gk")
        if gk: st.session_state.google_api_key = gk

        gc = st.text_input("Google CSE ID", value=st.session_state.google_cse_id,
                           key="inp_gc")
        if gc: st.session_state.google_cse_id = gc

    st.divider()

    # Reference data status
    st.markdown("### 📚 قواعد البيانات المرجعية")

    brands_ok = st.session_state.brands_df is not None
    cats_ok   = st.session_state.categories_df is not None
    st.markdown(
        f"{'✅' if brands_ok else '❌'} الماركات: "
        f"{'**%d ماركة**' % len(st.session_state.brands_df) if brands_ok else 'غير محملة'}"
    )
    st.markdown(
        f"{'✅' if cats_ok else '❌'} التصنيفات: "
        f"{'**%d تصنيف**' % len(st.session_state.categories_df) if cats_ok else 'غير محملة'}"
    )

    with st.expander("🔄 تحديث الملفات المرجعية"):
        bf = st.file_uploader("ماركات مهووس (CSV/Excel)", type=["csv","xlsx"], key="up_brands")
        if bf:
            st.session_state.brands_df = read_any_file(bf)
            st.success(f"✅ تم رفع {len(st.session_state.brands_df)} ماركة")

        cf = st.file_uploader("تصنيفات مهووس (CSV/Excel)", type=["csv","xlsx"], key="up_cats")
        if cf:
            st.session_state.categories_df = read_any_file(cf)
            st.success(f"✅ تم رفع {len(st.session_state.categories_df)} تصنيف")

    st.divider()
    if st.button("🗑️ مسح كل البيانات", use_container_width=True):
        for k in ["working_df", "results_df", "col_map", "processing_log"]:
            st.session_state[k] = [] if k == "processing_log" else None
        st.session_state.step = 1
        st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="main-header">
  <div style="font-size:2.5rem">🌸</div>
  <div>
    <h1>مهووس — نظام إدارة المنتجات الذكي</h1>
    <p>Mahwous AI-Powered Product Automation for Salla Platform</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# MODE SELECTOR
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown("### 🎯 اختر وضع العمل")
col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("➕ منتجات جديدة\nمن قائمة أسماء", use_container_width=True,
                 type="primary" if st.session_state.mode == "new" else "secondary"):
        st.session_state.mode = "new"; st.session_state.step = 1; st.rerun()

with col2:
    if st.button("✏️ تعديل ملف\nمنتجات سلة", use_container_width=True,
                 type="primary" if st.session_state.mode == "edit" else "secondary"):
        st.session_state.mode = "edit"; st.session_state.step = 1; st.rerun()

with col3:
    if st.button("🔍 دمج بيانات\nالـ SEO", use_container_width=True,
                 type="primary" if st.session_state.mode == "seo_merge" else "secondary"):
        st.session_state.mode = "seo_merge"; st.session_state.step = 1; st.rerun()

with col4:
    if st.button("💰 تحديث\nالأسعار", use_container_width=True,
                 type="primary" if st.session_state.mode == "price" else "secondary"):
        st.session_state.mode = "price"; st.session_state.step = 1; st.rerun()

st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ██████████  MODE: NEW PRODUCTS  ██████████████████████████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
if st.session_state.mode == "new":
    st.markdown("## ➕ إضافة منتجات جديدة")
    st.caption("ارفع ملفاً يحتوي أسماء العطور (أو أي عمود آخر) وسيكمل النظام باقي البيانات تلقائياً.")

    # ── STEP 1: Upload & Map ──────────────────────────────────────────────────
    st.markdown("### الخطوة 1: رفع الملف وتعيين الأعمدة")

    uploaded = st.file_uploader(
        "ارفع ملف CSV أو Excel (أعمدة حرة — من أي مورد)",
        type=["csv", "xlsx", "xls"],
        key="up_new"
    )

    if uploaded:
        raw_df = read_any_file(uploaded)
        if not raw_df.empty:
            cols_list = ["— اختر —"] + list(raw_df.columns)
            st.success(f"✅ تم قراءة الملف: **{len(raw_df)} صف** و **{len(raw_df.columns)} عمود**")
            with st.expander("👀 معاينة الملف الأصلي", expanded=False):
                st.dataframe(raw_df.head(10), use_container_width=True)

            st.markdown("**تعيين الأعمدة:**")
            c1, c2, c3 = st.columns(3)
            with c1:
                name_col = st.selectbox("عمود اسم المنتج / العطر *", cols_list, key="nc")
            with c2:
                price_col = st.selectbox("عمود السعر (اختياري)", cols_list, key="pc")
            with c3:
                sku_col = st.selectbox("عمود SKU (اختياري)", cols_list, key="sc")

            c4, c5, c6 = st.columns(3)
            with c4:
                size_col = st.selectbox("عمود الحجم (اختياري)", cols_list, key="szc")
            with c5:
                gender_col = st.selectbox("عمود الجنس (اختياري)", cols_list, key="gc_")
            with c6:
                tester_col = st.selectbox("عمود تستر/عادي (اختياري)", cols_list, key="tc")

            st.divider()
            st.markdown("**الإعدادات الافتراضية** (تُطبق عند غياب العمود المقابل):")
            d1, d2, d3, d4 = st.columns(4)
            with d1:
                default_gender = st.selectbox("الجنس الافتراضي",
                    ["للجنسين","للرجال","للنساء"], key="dg")
            with d2:
                default_size = st.text_input("الحجم الافتراضي", "100 مل", key="ds")
            with d3:
                default_conc = st.selectbox("التركيز الافتراضي",
                    ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="dc")
            with d4:
                default_tester = st.selectbox("النوع الافتراضي",
                    ["عطر عادي","تستر"], key="dt")

            gen_images  = st.checkbox("🖼 جلب الصور تلقائياً (Google CSE)", value=False, key="gi")
            gen_desc    = st.checkbox("🤖 توليد الوصف بالذكاء الاصطناعي", value=True, key="gd")

            if name_col == "— اختر —":
                st.warning("⚠️ يرجى تحديد عمود اسم المنتج")
            else:
                if st.button("🚀 ابدأ المعالجة", type="primary", key="proc_new"):
                    rows_out   = []
                    seo_out    = []
                    log        = []
                    progress   = st.progress(0)
                    status_box = st.empty()
                    total      = len(raw_df)

                    for idx, src_row in raw_df.iterrows():
                        pct = int((idx+1) / total * 100)
                        progress.progress(pct)

                        name = str(src_row.get(name_col, "")).strip()
                        if not name or name.lower() in ("nan","none",""):
                            log.append({"#": idx+1, "اسم": "فارغ", "حالة": "تجاهل"})
                            continue

                        status_box.info(f"⏳ معالجة ({idx+1}/{total}): **{name}**")

                        # Resolve fields
                        price    = src_row.get(price_col, "") if price_col != "— اختر —" else ""
                        sku      = src_row.get(sku_col, "")   if sku_col   != "— اختر —" else ""
                        size     = src_row.get(size_col, "")  if size_col  != "— اختر —" else ""
                        gender   = src_row.get(gender_col,"") if gender_col!= "— اختر —" else ""
                        tester_v = src_row.get(tester_col,"") if tester_col!= "— اختر —" else ""

                        size    = str(size).strip()   if str(size).strip() not in ("","nan")   else default_size
                        gender  = str(gender).strip() if str(gender).strip() not in ("","nan") else default_gender
                        is_test = any(w in str(tester_v).lower() for w in ["تستر","tester","yes","نعم"]) if tester_col != "— اختر —" else (default_tester == "تستر")
                        conc    = default_conc

                        brand    = match_brand(name)
                        category = match_category(name, gender)
                        seo      = generate_seo(name, brand, size, is_test, gender)
                        image_url = fetch_image(name, is_test) if gen_images else ""

                        desc = ""
                        if gen_desc:
                            desc = generate_description(name, is_test, brand, size, gender, conc)

                        prow = build_product_row(
                            product_no="", name=name, is_tester=is_test,
                            gender=gender, size=size, concentration=conc,
                            price=price, sku=sku, image_url=image_url,
                            description=desc, brand=brand,
                            category=category, seo=seo
                        )
                        rows_out.append(prow)
                        seo_out.append({
                            "No. (غير قابل للتعديل)":       "",
                            "اسم المنتج (غير قابل للتعديل)": prow["أسم المنتج"],
                            "رابط مخصص للمنتج (SEO Page URL)":      seo["url"],
                            "عنوان صفحة المنتج (SEO Page Title)":    seo["page_title"],
                            "وصف صفحة المنتج (SEO Page Description)": seo["page_desc"],
                        })
                        log.append({"#": idx+1, "اسم": name,
                                    "ماركة": brand.get("name","—"),
                                    "تصنيف": category,
                                    "صورة": "✅" if image_url else "—",
                                    "وصف": "✅" if desc else "—",
                                    "حالة": "✅ نجح"})

                    progress.progress(100)
                    status_box.success(f"✅ تمت معالجة {len(rows_out)} منتج بنجاح!")
                    st.session_state.working_df = pd.DataFrame(rows_out)
                    st.session_state.results_df  = pd.DataFrame(seo_out)
                    st.session_state.processing_log = log
                    st.session_state.step = 2
                    st.rerun()

    # ── STEP 2: Review & Export ──────────────────────────────────────────────
    if st.session_state.step >= 2 and st.session_state.working_df is not None:
        st.markdown("---")
        st.markdown("### الخطوة 2: مراجعة وتعديل النتائج")

        # Metrics
        df_w = st.session_state.working_df
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("إجمالي المنتجات", len(df_w))
        with m2: st.metric("مع وصف AI", int((df_w["الوصف"] != "").sum()))
        with m3: st.metric("مع صورة", int((df_w["صورة المنتج"] != "").sum()))
        with m4: st.metric("مع ماركة", int((df_w["الماركة"] != "").sum()))

        # Processing log
        if st.session_state.processing_log:
            with st.expander("📋 سجل المعالجة"):
                st.dataframe(pd.DataFrame(st.session_state.processing_log), use_container_width=True)

        # Editable grid — show key columns only for usability
        edit_cols = ["أسم المنتج","الماركة","تصنيف المنتج","سعر المنتج",
                     "رمز المنتج sku","صورة المنتج","وصف صورة المنتج","حالة المنتج"]
        edit_cols = [c for c in edit_cols if c in df_w.columns]

        st.markdown("**جدول التعديل التفاعلي** (عدّل أي خلية مباشرةً):")
        edited_main = st.data_editor(
            df_w[edit_cols],
            use_container_width=True,
            num_rows="dynamic",
            key="editor_new_main"
        )
        # Apply edits back
        for c in edit_cols:
            df_w[c] = edited_main[c]
        st.session_state.working_df = df_w

        # Description editor
        with st.expander("📝 تعديل الأوصاف"):
            desc_df = df_w[["أسم المنتج","الوصف"]].copy()
            edited_desc = st.data_editor(desc_df, use_container_width=True,
                                         num_rows="fixed", key="editor_desc")
            df_w["الوصف"] = edited_desc["الوصف"]
            st.session_state.working_df = df_w

        # SEO editor
        st.markdown("**جدول SEO:**")
        seo_df_edit = st.data_editor(
            st.session_state.results_df,
            use_container_width=True,
            num_rows="dynamic",
            key="editor_seo"
        )
        st.session_state.results_df = seo_df_edit

        # ── EXPORT BUTTONS ────────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("### الخطوة 3: التصدير")
        st.caption("اختر صيغة التصدير المناسبة لكل ملف")

        ca, cb, cc, cd = st.columns(4)
        with ca:
            xlsx_prod = build_salla_product_xlsx(st.session_state.working_df)
            st.download_button("📥 منتجات — Excel", xlsx_prod,
                               "mahwous_products.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
        with cb:
            csv_prod = build_salla_product_csv(st.session_state.working_df)
            st.download_button("📥 منتجات — CSV", csv_prod,
                               "mahwous_products.csv", "text/csv",
                               use_container_width=True)
        with cc:
            xlsx_seo = build_salla_seo_xlsx(st.session_state.results_df)
            st.download_button("📥 SEO — Excel", xlsx_seo,
                               "mahwous_seo.xlsx",
                               "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               use_container_width=True)
        with cd:
            csv_seo = build_salla_seo_csv(st.session_state.results_df)
            st.download_button("📥 SEO — CSV", csv_seo,
                               "mahwous_seo.csv", "text/csv",
                               use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ██████████  MODE: EDIT EXISTING SALLA FILE  ██████████████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "edit":
    st.markdown("## ✏️ تعديل ملف منتجات سلة الموجود")
    st.caption("ارفع ملف تحديث/تعديل المنتجات المصدَّر من سلة، عدّله، وصدّره مرة أخرى.")

    uploaded_salla = st.file_uploader(
        "ارفع ملف منتجات سلة (Excel أو CSV)",
        type=["csv","xlsx","xls"], key="up_edit"
    )

    if uploaded_salla:
        salla_df = read_salla_product_file(uploaded_salla)
        if not salla_df.empty:
            st.success(f"✅ تم قراءة **{len(salla_df)} منتج** من ملف سلة")

            # Show all columns present vs. expected
            present = set(salla_df.columns)
            expected = set(SALLA_PRODUCT_COLS)
            missing = expected - present
            if missing:
                st.warning(f"أعمدة غير موجودة في الملف (ستُضاف فارغة): {', '.join(list(missing)[:8])}...")

            # Build full df with all Salla columns
            full_df = pd.DataFrame(columns=SALLA_PRODUCT_COLS)
            for col in SALLA_PRODUCT_COLS:
                if col in salla_df.columns:
                    full_df[col] = salla_df[col]
                else:
                    full_df[col] = ""

            st.markdown("### خيارات المعالجة الإضافية")
            op1, op2, op3 = st.columns(3)
            with op1:
                regen_desc = st.checkbox("🤖 توليد وصف AI للصفوف الفارغة")
            with op2:
                regen_seo  = st.checkbox("🔍 توليد SEO للصفوف الفارغة")
            with op3:
                fetch_imgs = st.checkbox("🖼 جلب صور للصفوف الفارغة")

            if st.button("⚡ تطبيق المعالجة", key="proc_edit") and any([regen_desc, regen_seo, fetch_imgs]):
                progress = st.progress(0)
                seo_rows = []
                for i, (idx, row) in enumerate(full_df.iterrows()):
                    progress.progress(int((i+1)/len(full_df)*100))
                    name = str(row.get("أسم المنتج","")).strip()
                    if not name: continue
                    brand    = match_brand(name)
                    is_test  = any(w in name.lower() for w in ["تستر","tester"])
                    gender   = "للنساء" if any(w in name for w in ["نسائ","women"]) else \
                               "للرجال" if any(w in name for w in ["رجال","men"]) else "للجنسين"
                    size_m   = re.search(r"\d+\s*مل|\d+\s*ml", name, re.I)
                    size     = size_m.group() if size_m else "100 مل"

                    if fetch_imgs and not str(row.get("صورة المنتج","")).startswith("http"):
                        full_df.at[idx, "صورة المنتج"] = fetch_image(name, is_test)

                    if regen_desc and not str(row.get("الوصف","")).strip():
                        full_df.at[idx, "الوصف"] = generate_description(
                            name, is_test, brand, size, gender, "أو دو بارفيوم"
                        )
                    if not full_df.at[idx,"الماركة"]:
                        full_df.at[idx,"الماركة"] = brand.get("name","")
                    if not full_df.at[idx,"تصنيف المنتج"]:
                        full_df.at[idx,"تصنيف المنتج"] = match_category(name, gender)

                    seo = generate_seo(name, brand, size, is_test, gender)
                    seo_rows.append({
                        "No. (غير قابل للتعديل)":          str(row.get("No.","") or ""),
                        "اسم المنتج (غير قابل للتعديل)":   name,
                        "رابط مخصص للمنتج (SEO Page URL)": seo["url"],
                        "عنوان صفحة المنتج (SEO Page Title)": seo["page_title"],
                        "وصف صفحة المنتج (SEO Page Description)": seo["page_desc"],
                    })

                progress.progress(100)
                st.success("✅ تمت المعالجة!")
                st.session_state.working_df = full_df
                if seo_rows:
                    st.session_state.results_df = pd.DataFrame(seo_rows)
            else:
                st.session_state.working_df = full_df

            # ── Editable grid ──────────────────────────────────────────────
            st.markdown("### الجدول التفاعلي — عدّل وأضف وامسح")
            edit_cols_e = ["No.", "أسم المنتج", "الماركة", "تصنيف المنتج",
                           "سعر المنتج", "رمز المنتج sku", "صورة المنتج",
                           "وصف صورة المنتج", "حالة المنتج", "السعر المخفض"]
            edit_cols_e = [c for c in edit_cols_e if c in st.session_state.working_df.columns]
            edited_e = st.data_editor(
                st.session_state.working_df[edit_cols_e],
                use_container_width=True, num_rows="dynamic", key="editor_edit"
            )
            for c in edit_cols_e:
                st.session_state.working_df[c] = edited_e[c]

            with st.expander("📝 تعديل الأوصاف (HTML)"):
                desc_e = st.data_editor(
                    st.session_state.working_df[["أسم المنتج","الوصف"]],
                    use_container_width=True, key="editor_edit_desc"
                )
                st.session_state.working_df["الوصف"] = desc_e["الوصف"]

            # Export
            st.markdown("### التصدير")
            c1,c2,c3,c4 = st.columns(4)
            with c1:
                st.download_button("📥 منتجات — Excel",
                    build_salla_product_xlsx(st.session_state.working_df),
                    "salla_products_updated.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True)
            with c2:
                st.download_button("📥 منتجات — CSV",
                    build_salla_product_csv(st.session_state.working_df),
                    "salla_products_updated.csv","text/csv",use_container_width=True)
            with c3:
                if st.session_state.results_df is not None:
                    st.download_button("📥 SEO — Excel",
                        build_salla_seo_xlsx(st.session_state.results_df),
                        "salla_seo_updated.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
            with c4:
                if st.session_state.results_df is not None:
                    st.download_button("📥 SEO — CSV",
                        build_salla_seo_csv(st.session_state.results_df),
                        "salla_seo_updated.csv","text/csv",use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ██████████  MODE: SEO MERGE  ████████████████████████████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "seo_merge":
    st.markdown("## 🔍 دمج بيانات SEO في ملف المنتجات")
    st.caption("ارفع ملف منتجات سلة وملف بيانات SEO، وسيتم دمجهما تلقائياً.")

    c1, c2 = st.columns(2)
    with c1:
        prod_file = st.file_uploader("📂 ملف منتجات سلة (Excel/CSV)",
                                     type=["csv","xlsx"], key="seo_prod")
    with c2:
        seo_file  = st.file_uploader("📂 ملف بيانات SEO (Excel/CSV)",
                                     type=["csv","xlsx"], key="seo_seo")

    if prod_file and seo_file:
        prod_df = read_salla_product_file(prod_file)
        seo_df  = read_any_file(seo_file)

        if not prod_df.empty and not seo_df.empty:
            st.success(f"✅ منتجات: {len(prod_df)} صف | SEO: {len(seo_df)} صف")

            with st.expander("👀 معاينة ملف SEO"):
                st.dataframe(seo_df.head(5), use_container_width=True)

            # Auto-detect SEO columns
            no_col  = next((c for c in seo_df.columns if "no" in c.lower() or "رقم" in c), seo_df.columns[0])
            url_col = next((c for c in seo_df.columns if "url" in c.lower() or "رابط" in c), None)
            title_col = next((c for c in seo_df.columns if "title" in c.lower() or "عنوان" in c), None)
            desc_col  = next((c for c in seo_df.columns if "desc" in c.lower() or "وصف" in c), None)

            st.markdown("**تأكيد تعيين أعمدة SEO:**")
            sc1,sc2,sc3,sc4 = st.columns(4)
            seo_cols_list = list(seo_df.columns)
            with sc1: no_col_s   = st.selectbox("عمود رقم المنتج", seo_cols_list,
                                                 index=seo_cols_list.index(no_col) if no_col in seo_cols_list else 0)
            with sc2: url_col_s  = st.selectbox("عمود الرابط URL",  seo_cols_list,
                                                 index=seo_cols_list.index(url_col) if url_col in seo_cols_list else 0)
            with sc3: ttl_col_s  = st.selectbox("عمود العنوان",     seo_cols_list,
                                                 index=seo_cols_list.index(title_col) if title_col in seo_cols_list else 0)
            with sc4: dsc_col_s  = st.selectbox("عمود الوصف",       seo_cols_list,
                                                 index=seo_cols_list.index(desc_col) if desc_col in seo_cols_list else 0)

            what_to_merge = st.multiselect(
                "ماذا تريد دمجه في ملف المنتجات؟",
                ["الوصف (HTML)","الماركة","التصنيف","وصف صورة المنتج","حالة المنتج"],
                default=["الوصف (HTML)"]
            )

            if st.button("⚡ دمج البيانات", type="primary", key="merge_btn"):
                # Convert No. to string for matching
                seo_df[no_col_s] = seo_df[no_col_s].astype(str).str.strip()
                if "No." in prod_df.columns:
                    prod_df["No."] = prod_df["No."].astype(str).str.strip()

                # Build SEO output df
                seo_out_rows = []
                for _, prow in prod_df.iterrows():
                    no_val = str(prow.get("No.","")).strip()
                    match  = seo_df[seo_df[no_col_s] == no_val]
                    srow   = match.iloc[0] if not match.empty else None

                    seo_out_rows.append({
                        "No. (غير قابل للتعديل)":            no_val,
                        "اسم المنتج (غير قابل للتعديل)":     str(prow.get("أسم المنتج","")),
                        "رابط مخصص للمنتج (SEO Page URL)":   str(srow[url_col_s]) if srow is not None else "",
                        "عنوان صفحة المنتج (SEO Page Title)": str(srow[ttl_col_s]) if srow is not None else "",
                        "وصف صفحة المنتج (SEO Page Description)": str(srow[dsc_col_s]) if srow is not None else "",
                    })

                merged_count = sum(1 for r in seo_out_rows if r["رابط مخصص للمنتج (SEO Page URL)"])
                st.success(f"✅ تم الدمج: {merged_count}/{len(prod_df)} صف لديه بيانات SEO")

                st.session_state.working_df = prod_df
                st.session_state.results_df = pd.DataFrame(seo_out_rows)

                # Show preview
                st.dataframe(pd.DataFrame(seo_out_rows).head(10), use_container_width=True)

                c1,c2,c3,c4 = st.columns(4)
                with c1:
                    st.download_button("📥 منتجات — Excel",
                        build_salla_product_xlsx(prod_df),
                        "salla_products_merged.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c2:
                    st.download_button("📥 منتجات — CSV",
                        build_salla_product_csv(prod_df),
                        "salla_products_merged.csv","text/csv",use_container_width=True)
                with c3:
                    st.download_button("📥 SEO — Excel",
                        build_salla_seo_xlsx(pd.DataFrame(seo_out_rows)),
                        "salla_seo_merged.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c4:
                    st.download_button("📥 SEO — CSV",
                        build_salla_seo_csv(pd.DataFrame(seo_out_rows)),
                        "salla_seo_merged.csv","text/csv",use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# ██████████  MODE: PRICE UPDATE  █████████████████████████████████████████████
# ═══════════════════════════════════════════════════════════════════════════════
elif st.session_state.mode == "price":
    st.markdown("## 💰 تحديث الأسعار")
    st.caption("ارفع ملف CSV/Excel بالأسعار الجديدة، عيّن الأعمدة، وصدّر ملف تحديث سلة.")

    uploaded_price = st.file_uploader(
        "ارفع ملف الأسعار (CSV/Excel — من أي مصدر)",
        type=["csv","xlsx","xls"], key="up_price"
    )

    if uploaded_price:
        raw_p = read_any_file(uploaded_price)
        if not raw_p.empty:
            st.success(f"✅ تم قراءة **{len(raw_p)} صف**")
            with st.expander("👀 معاينة"): st.dataframe(raw_p.head(8), use_container_width=True)

            pcols = ["— اختر —"] + list(raw_p.columns)
            p1,p2,p3,p4,p5 = st.columns(5)
            with p1: no_c   = st.selectbox("رقم المنتج No.", pcols, key="pno")
            with p2: nm_c   = st.selectbox("اسم المنتج",    pcols, key="pnm")
            with p3: pr_c   = st.selectbox("السعر *",       pcols, key="ppr")
            with p4: sk_c   = st.selectbox("SKU",           pcols, key="psk")
            with p5: dc_c   = st.selectbox("السعر المخفض",  pcols, key="pdc")

            if st.button("⚡ بناء ملف تحديث الأسعار", type="primary", key="price_build"):
                price_rows = []
                for _, row in raw_p.iterrows():
                    price_rows.append({
                        "No.":                   str(row.get(no_c,"")) if no_c != "— اختر —" else "",
                        "النوع ":                "منتج",
                        "أسم المنتج":            str(row.get(nm_c,"")) if nm_c != "— اختر —" else "",
                        "رمز المنتج sku":        str(row.get(sk_c,"")) if sk_c != "— اختر —" else "",
                        "سعر المنتج":            str(row.get(pr_c,"")) if pr_c != "— اختر —" else "",
                        "سعر التكلفة":           "",
                        "السعر المخفض":          str(row.get(dc_c,"")) if dc_c != "— اختر —" else "",
                        "تاريخ بداية التخفيض":   "",
                        "تاريخ نهاية التخفيض":   "",
                    })

                price_df = pd.DataFrame(price_rows)
                st.markdown("### مراجعة وتعديل")
                edited_pr = st.data_editor(price_df, use_container_width=True,
                                           num_rows="dynamic", key="editor_price")

                # Build XLSX
                def price_xlsx(df):
                    wb = Workbook(); ws = wb.active; ws.title = "Price Update"
                    ws.cell(1,1,"بيانات المنتج")
                    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(SALLA_PRICE_COLS))
                    ws.cell(1,1).font = Font(bold=True,color="FFFFFF")
                    ws.cell(1,1).fill = PatternFill("solid",fgColor="0F0E0D")
                    ws.cell(1,1).alignment = Alignment(horizontal="center")
                    for i,c in enumerate(SALLA_PRICE_COLS,1):
                        cell = ws.cell(2,i,c)
                        cell.font = Font(bold=True)
                        cell.fill = PatternFill("solid",fgColor="E8D5B7")
                        cell.alignment = Alignment(horizontal="center",wrap_text=True)
                    for ri,(_, row) in enumerate(df.iterrows(),3):
                        for ci,col in enumerate(SALLA_PRICE_COLS,1):
                            ws.cell(ri,ci,str(row.get(col,"") or ""))
                    buf=io.BytesIO(); wb.save(buf); buf.seek(0); return buf.read()

                c1,c2 = st.columns(2)
                with c1:
                    st.download_button("📥 تحديث الأسعار — Excel",
                        price_xlsx(edited_pr), "price_update.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c2:
                    csv_p = io.StringIO()
                    csv_p.write("بيانات المنتج"+"," * (len(SALLA_PRICE_COLS)-1)+"\n")
                    csv_p.write(",".join(SALLA_PRICE_COLS)+"\n")
                    for _,row in edited_pr.iterrows():
                        csv_p.write(",".join([f'"{str(row.get(c,""))}"' for c in SALLA_PRICE_COLS])+"\n")
                    st.download_button("📥 تحديث الأسعار — CSV",
                        csv_p.getvalue().encode("utf-8-sig"),
                        "price_update.csv","text/csv",use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════════════
st.markdown('<hr class="gold-divider">', unsafe_allow_html=True)
st.markdown(
    "<div style='text-align:center;color:#9a8e86;font-size:0.8rem'>"
    "🌸 مهووس — عالمك العطري يبدأ من مهووس | Mahwous Automation System v2.0"
    "</div>",
    unsafe_allow_html=True
)
