"""
╔══════════════════════════════════════════════════════════════════╗
║   مهووس — مركز التحكم الشامل  v4.5  (Production-Ready)         ║
║   Mahwous Ultimate Control Center                               ║
║   Streamlit · Anthropic Claude · Google CSE · Railway           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import io, re, os, json, time
import requests
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (Font, PatternFill, Alignment,
                              Border, Side, GradientFill)
from openpyxl.utils import get_column_letter
import anthropic

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title="مهووس | مركز التحكم",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  GLOBAL CSS — Arabic RTL + Gold Theme                          ║
# ╚══════════════════════════════════════════════════════════════════╝
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

/* ── Global Reset & RTL ─────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp, .main, section, div {
  font-family: 'Cairo', sans-serif !important;
}
.stApp { background-color: #f5f0e8; }

/* ── Sidebar ─────────────────────────────────────── */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #0f0e0d 0%, #1c1610 100%) !important;
  border-left: 1px solid rgba(184,147,58,0.25);
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div { color: #e0d0b0 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #c8b080 !important; }

/* ── Top Header ──────────────────────────────────── */
.mhw-header {
  background: linear-gradient(135deg, #0f0e0d 0%, #1c1610 50%, #2a1e08 100%);
  border: 1px solid rgba(184,147,58,0.3);
  border-radius: 14px;
  padding: 16px 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
  box-shadow: 0 8px 32px rgba(0,0,0,0.2);
}
.mhw-header .emblem {
  width: 52px; height: 52px;
  background: linear-gradient(135deg, #b8933a, #e0b84a);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 26px; font-weight: 900; color: #0f0e0d;
  box-shadow: 0 0 24px rgba(184,147,58,0.6);
  flex-shrink: 0;
}
.mhw-header h1 {
  color: #b8933a; font-size: 1.55rem;
  margin: 0; line-height: 1.2;
}
.mhw-header p { color: rgba(255,255,255,0.38); font-size: 0.78rem; margin: 0; }

/* ── Section Title ───────────────────────────────── */
.sec-title {
  display: flex; align-items: center; gap: 10px;
  margin: 22px 0 14px; direction: rtl;
}
.sec-title .bar {
  width: 5px; height: 24px; border-radius: 3px;
  background: linear-gradient(180deg, #b8933a, #e0b84a);
}
.sec-title h3 { margin: 0; font-size: 1.05rem; font-weight: 800; color: #1a1208; }

/* ── Stats Bar ───────────────────────────────────── */
.stats-bar { display: flex; gap: 12px; flex-wrap: wrap; margin: 14px 0; }
.stat-box {
  flex: 1; min-width: 110px;
  background: white;
  border: 1px solid rgba(184,147,58,0.22);
  border-radius: 12px;
  padding: 14px 16px; text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}
.stat-box .n  { font-size: 1.9rem; font-weight: 900; color: #b8933a; line-height: 1; }
.stat-box .lb { font-size: 0.73rem; color: #7a6e60; margin-top: 3px; }

/* ── Upload Zone ─────────────────────────────────── */
.upload-zone {
  border: 2px dashed rgba(184,147,58,0.38);
  border-radius: 16px; padding: 2.5rem;
  text-align: center;
  background: rgba(184,147,58,0.035);
  transition: all 0.2s;
}
.upload-zone:hover {
  border-color: #b8933a;
  background: rgba(184,147,58,0.07);
}
.uz-icon  { font-size: 3rem; }
.uz-title { font-size: 1.08rem; font-weight: 800; color: #1a1208; margin: 6px 0 3px; }
.uz-sub   { font-size: 0.8rem; color: #9a8e80; }

/* ── Tool Tabs ───────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
  background: rgba(184,147,58,0.06);
  border-radius: 10px; padding: 4px; gap: 4px;
  border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px !important;
  font-family: 'Cairo', sans-serif !important;
  font-weight: 700 !important; font-size: 0.82rem !important;
  padding: 8px 14px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(135deg, #b8933a, #e0b84a) !important;
  color: #0f0e0d !important;
}

/* ── Alerts ──────────────────────────────────────── */
.al-info {
  background: #e8f4fd; border-right: 4px solid #1976d2;
  border-radius: 8px; padding: 10px 14px;
  font-size: 0.84rem; color: #0d3c6e; margin: 8px 0;
  direction: rtl;
}
.al-ok {
  background: #e8f5e9; border-right: 4px solid #388e3c;
  border-radius: 8px; padding: 10px 14px;
  font-size: 0.84rem; color: #1b5020; margin: 8px 0;
  direction: rtl;
}
.al-warn {
  background: #fff8e1; border-right: 4px solid #f9a825;
  border-radius: 8px; padding: 10px 14px;
  font-size: 0.84rem; color: #5d4300; margin: 8px 0;
  direction: rtl;
}

/* ── Buttons ─────────────────────────────────────── */
div.stButton > button {
  font-family: 'Cairo', sans-serif !important;
  font-weight: 700 !important;
}
div.stButton > button[kind="primary"] {
  background: linear-gradient(135deg, #0f0e0d, #2a1e08) !important;
  color: #b8933a !important;
  border: none !important;
}
div.stButton > button:hover { opacity: 0.88 !important; }

/* ── Gold Divider ────────────────────────────────── */
.gdiv {
  height: 1px; border: none; margin: 20px 0;
  background: linear-gradient(90deg, transparent, rgba(184,147,58,0.4), transparent);
}

/* ── Progress Item ───────────────────────────────── */
.prog-ok  { background:#e8f5e9; border-radius:8px; padding:6px 12px; margin:3px 0; font-size:0.82rem; color:#1b5020; }
.prog-err { background:#fdecea; border-radius:8px; padding:6px 12px; margin:3px 0; font-size:0.82rem; color:#b71c1c; }
.prog-run { background:#fff8e1; border-radius:8px; padding:6px 12px; margin:3px 0; font-size:0.82rem; color:#e65100; }

/* ── Badges ──────────────────────────────────────── */
.badge-ok   { display:inline-block; background:#e8f5e9; color:#2d7a4f; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
.badge-miss { display:inline-block; background:#fafafa; color:#9e9e9e; padding:2px 10px; border-radius:20px; font-size:0.72rem; }
.badge-new  { display:inline-block; background:#fff3e0; color:#e65100; padding:2px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }

/* ── Compare Card ────────────────────────────────── */
.cmp-card {
  background: white;
  border: 1px solid rgba(184,147,58,0.25);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  direction: rtl;
}
.cmp-card.suspect { border-color: #f9a825; background: #fffde7; }
.cmp-card.exact   { border-color: #388e3c; background: #f1f8e9; }
.cmp-card img { width: 80px; height: 80px; object-fit: cover; border-radius: 8px; }
.cmp-pct { font-size: 1.2rem; font-weight: 900; color: #f9a825; }

/* ── Footer ──────────────────────────────────────── */
.mhw-footer {
  text-align: center; color: #9a8e80;
  font-size: 0.76rem; padding: 16px 0 8px;
  border-top: 1px solid rgba(184,147,58,0.15);
  margin-top: 32px;
}
</style>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  SALLA EXACT SCHEMAS                                            ║
# ╚══════════════════════════════════════════════════════════════════╝
SALLA_COLS = [
    "No.", "النوع ", "أسم المنتج", "تصنيف المنتج", "صورة المنتج",
    "وصف صورة المنتج", "نوع المنتج", "سعر المنتج", "الوصف",
    "هل يتطلب شحن؟", "رمز المنتج sku", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض",
    "اقصي كمية لكل عميل", "إخفاء خيار تحديد الكمية",
    "اضافة صورة عند الطلب", "الوزن", "وحدة الوزن",
    "حالة المنتج", "الماركة", "العنوان الترويجي", "تثبيت المنتج",
    "الباركود", "السعرات الحرارية", "MPN", "GTIN",
    "خاضع للضريبة ؟", "سبب عدم الخضوع للضريبة",
    "[1] الاسم", "[1] النوع", "[1] القيمة", "[1] الصورة / اللون",
    "[2] الاسم", "[2] النوع", "[2] القيمة", "[2] الصورة / اللون",
    "[3] الاسم", "[3] النوع", "[3] القيمة", "[3] الصورة / اللون",
]

SALLA_SEO_COLS = [
    "No. (غير قابل للتعديل)",
    "اسم المنتج (غير قابل للتعديل)",
    "رابط مخصص للمنتج (SEO Page URL)",
    "عنوان صفحة المنتج (SEO Page Title)",
    "وصف صفحة المنتج (SEO Page Description)",
]

SALLA_PRICE_COLS = [
    "No.", "النوع ", "أسم المنتج", "رمز المنتج sku",
    "سعر المنتج", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض",
]

# Salla brands file exact columns
SALLA_BRANDS_COLS = [
    "اسم العلامة التجارية",
    "(SEO Page URL) رابط صفحة العلامة التجارية",
    "وصف العلامة التجارية",
    "صورة العلامة التجارية",
]

# Editor shows these by default (rest hidden unless user selects)
EDITOR_COLS = [
    "No.", "النوع ", "أسم المنتج", "الماركة", "تصنيف المنتج",
    "سعر المنتج", "رمز المنتج sku", "صورة المنتج",
    "وصف صورة المنتج", "حالة المنتج", "السعر المخفض",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI SYSTEM PROMPT — خبير وصف منتجات مهووس v4.5                ║
# ╚══════════════════════════════════════════════════════════════════╝
AI_SYSTEM = """أنت خبير كتابة أوصاف عطور فاخرة تعمل حصرياً لمتجر "مهووس" السعودي.

قواعد صارمة لا تُكسر:
- ممنوع منعاً باتاً استخدام الرموز التعبيرية (Emojis) نهائياً
- التركيز يُكتب دائماً: "أو دو بارفيوم"
- أسلوبك: راقٍ 40%، ودود 25%، رومانسي 20%، تسويقي مقنع 15%
- الطول: 1200-1500 كلمة بالضبط
- الإخراج HTML خالص فقط — لا نص خارج الوسوم
- استخدم <strong> للكلمات المفتاحية
- الروابط الداخلية: استخدم <a href="https://mahwous.com/brands/[slug]" target="_blank">[اسم الماركة]</a>
- المكونات: اذكر مكونات حقيقية موثوقة إذا عرفتها، وإلا اذكر مكونات تقريبية منطقية للعائلة العطرية

هيكل الوصف الإلزامي:
<h2>[عطر/تستر] [الماركة] [الاسم] [التركيز] [الحجم] [للجنس]</h2>
<p>فقرة افتتاحية عاطفية 100-150 كلمة، الكلمة المفتاحية في أول 50 كلمة، دعوة للشراء.</p>
<h3>تفاصيل المنتج</h3>
<ul>
<li><strong>الماركة:</strong> [مع رابط داخلي]</li>
<li><strong>الاسم:</strong></li>
<li><strong>الجنس:</strong></li>
<li><strong>العائلة العطرية:</strong></li>
<li><strong>الحجم:</strong></li>
<li><strong>التركيز:</strong> أو دو بارفيوم</li>
<li><strong>سنة الإصدار:</strong></li>
<li><strong>نوع المنتج:</strong> [تستر / عادي]</li>
</ul>
<h3>رحلة العطر - الهرم العطري</h3>
<p>وصف حسي شاعري للعطر كاملاً.</p>
<ul>
<li><strong>المقدمة (Top Notes):</strong> [المكونات الحقيقية أو التقريبية]</li>
<li><strong>القلب (Heart Notes):</strong> [المكونات الحقيقية أو التقريبية]</li>
<li><strong>القاعدة (Base Notes):</strong> [المكونات الحقيقية أو التقريبية]</li>
</ul>
<h3>لماذا تختار هذا العطر؟</h3>
<ul>
<li><strong>الثبات والفوحان:</strong> [وصف دقيق]</li>
<li><strong>التميز والأصالة:</strong> [وصف دقيق]</li>
<li><strong>القيمة الاستثنائية:</strong> [وصف دقيق]</li>
<li><strong>الجاذبية المضمونة:</strong> [وصف دقيق]</li>
</ul>
<h3>متى وأين ترتديه؟</h3>
<p>الفصول المناسبة، أوقات الاستخدام، المناسبات الملائمة.</p>
<h3>لمسة خبير من مهووس</h3>
<p>تقييم للفوحان (1-10) والثبات (1-10) ونصيحة رش احترافية.</p>
<h3>الأسئلة الشائعة</h3>
<ul>
<li><strong>كم يدوم العطر؟</strong> [إجابة دقيقة]</li>
<li><strong>هل يناسب الاستخدام اليومي؟</strong> [إجابة]</li>
<li><strong>ما الفرق بين التستر والعطر العادي؟</strong> [إجابة]</li>
<li><strong>ما العائلة العطرية؟</strong> [إجابة]</li>
<li><strong>هل يناسب الطقس الحار في السعودية؟</strong> [إجابة]</li>
<li><strong>ما مناسبات ارتداء هذا العطر؟</strong> [إجابة]</li>
</ul>
<h3>اكتشف أكثر من مهووس</h3>
<p>روابط داخلية لعطور مشابهة: <a href="https://mahwous.com/brands/[slug]" target="_blank">[عطور الماركة]</a> | <a href="https://mahwous.com/categories/mens-perfumes" target="_blank">[عطور رجالية]</a></p>
<p><strong>عالمك العطري يبدأ من مهووس.</strong> أصلي 100% | شحن سريع داخل السعودية.</p>

في نهاية الوصف أضف قسم SEO منفصل بصيغة JSON:
<!--SEO_DATA
{
  "page_title": "...",
  "meta_description": "...",
  "url_slug": "...",
  "alt_text": "...",
  "tags": ["...", "..."]
}
SEO_DATA-->"""

# ╔══════════════════════════════════════════════════════════════════╗
# ║  SESSION STATE INIT                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
def _init_state():
    defaults = {
        # API keys
        "api_key":        os.environ.get("ANTHROPIC_API_KEY", ""),
        "google_api":     os.environ.get("GOOGLE_API_KEY", ""),
        "google_cse":     os.environ.get("GOOGLE_CSE_ID", ""),
        # Reference data
        "brands_df":      None,
        "categories_df":  None,
        # Universal Processor state
        "up_raw":         None,   # raw uploaded df
        "up_df":          None,   # restructured Salla df
        "up_seo":         None,   # SEO companion df
        "up_filename":    "",
        "up_mapped":      False,
        # Quick Add list
        "qa_rows":        [],
        # Comparison page state
        "cmp_new_df":     None,   # new products file
        "cmp_store_df":   None,   # store master file
        "cmp_results":    None,   # comparison results df
        "cmp_approved":   {},     # {idx: True/False} user decisions
        # New brands generated
        "new_brands":     [],     # list of dicts for new brands
        # Page
        "page":           "processor",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Auto-load bundled reference CSVs
    if st.session_state.brands_df is None:
        p = os.path.join(DATA_DIR, "brands.csv")
        if os.path.exists(p):
            try:
                st.session_state.brands_df = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                pass
    if st.session_state.categories_df is None:
        p = os.path.join(DATA_DIR, "categories.csv")
        if os.path.exists(p):
            try:
                st.session_state.categories_df = pd.read_csv(p, encoding="utf-8-sig")
            except Exception:
                pass

_init_state()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  CORE UTILITIES                                                 ║
# ╚══════════════════════════════════════════════════════════════════╝

def read_file(f, salla_2row: bool = False) -> pd.DataFrame:
    """Read CSV or Excel → clean DataFrame. Handles multi-encoding."""
    name = f.name.lower()
    hdr  = 1 if salla_2row else 0
    try:
        if name.endswith((".xlsx", ".xlsm", ".xls")):
            df = pd.read_excel(f, header=hdr, dtype=str)
        else:
            for enc in ("utf-8-sig", "utf-8", "cp1256", "latin-1"):
                try:
                    f.seek(0)
                    df = pd.read_csv(f, header=hdr, encoding=enc, dtype=str)
                    break
                except UnicodeDecodeError:
                    continue
        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return pd.DataFrame()


def auto_guess_col(cols, keywords: list) -> str:
    """Guess which column matches a list of keywords."""
    for kw in keywords:
        for c in cols:
            if kw.lower() in c.lower():
                return c
    return "— لا يوجد —"


def _fuzzy_ratio(a: str, b: str) -> int:
    """Simple character-level similarity ratio (0-100) without external libs."""
    a, b = str(a).lower().strip(), str(b).lower().strip()
    if not a or not b:
        return 0
    if a == b:
        return 100
    # Longest common subsequence length / max length * 100
    longer  = max(len(a), len(b))
    shorter = min(len(a), len(b))
    # Count matching chars in order
    matches = 0
    j = 0
    for ch in a:
        while j < len(b):
            if b[j] == ch:
                matches += 1
                j += 1
                break
            j += 1
    return int(matches / longer * 100)


def match_brand(name: str) -> dict:
    bdf = st.session_state.brands_df
    if bdf is None or not str(name).strip():
        return {"name": "", "page_url": ""}
    nl = str(name).lower()
    col0 = bdf.columns[0]
    for _, row in bdf.iterrows():
        raw = str(row[col0])
        for part in re.split(r"\s*\|\s*", raw):
            p = part.strip().lower()
            if p and p in nl:
                return {
                    "name": raw,
                    "page_url": str(row.get(
                        "(SEO Page URL) رابط صفحة العلامة التجارية", "") or ""),
                }
    return {"name": "", "page_url": ""}


def generate_new_brand(brand_name: str) -> dict:
    """Generate a new brand entry in Salla format using AI."""
    key = st.session_state.api_key
    slug = to_slug(brand_name)
    desc = ""
    if key:
        try:
            client = anthropic.Anthropic(api_key=key)
            msg = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=300,
                messages=[{"role": "user", "content":
                    f"اكتب وصفاً موجزاً (50-80 كلمة) لعلامة العطور التجارية '{brand_name}' "
                    f"بالعربية، بأسلوب فاخر ومهني. بدون رموز تعبيرية. نص فقط."}],
            )
            desc = msg.content[0].text.strip()
        except Exception:
            desc = f"علامة تجارية عالمية متخصصة في صناعة العطور الفاخرة."
    return {
        "اسم العلامة التجارية":                           brand_name,
        "(SEO Page URL) رابط صفحة العلامة التجارية":     slug,
        "وصف العلامة التجارية":                          desc,
        "صورة العلامة التجارية":                         "",
    }


def match_category(name: str, gender: str = "") -> str:
    t = (str(name) + " " + str(gender)).lower()
    if any(w in t for w in ["رجال", "للرجال", "men", "homme", "رجالي"]):
        return "العطور > عطور رجالية"
    if any(w in t for w in ["نساء", "للنساء", "women", "femme", "نسائي"]):
        return "العطور > عطور نسائية"
    return "العطور > عطور للجنسين"


def to_slug(text: str) -> str:
    ar = {
        "ا": "a", "أ": "a", "إ": "e", "آ": "a", "ب": "b", "ت": "t",
        "ث": "th", "ج": "j", "ح": "h", "خ": "kh", "د": "d", "ذ": "z",
        "ر": "r", "ز": "z", "س": "s", "ش": "sh", "ص": "s", "ض": "d",
        "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f", "ق": "q",
        "ك": "k", "ل": "l", "م": "m", "ن": "n", "ه": "h", "و": "w",
        "ي": "y", "ى": "a", "ة": "a", "ء": "", "ئ": "y", "ؤ": "w",
    }
    out = ""
    for c in str(text).lower():
        if c in ar:
            out += ar[c]
        elif c.isascii() and c.isalnum():
            out += c
        elif c in " -_":
            out += "-"
    return re.sub(r"-+", "-", out).strip("-") or "perfume"


def gen_seo(name: str, brand: dict, size: str,
            tester: bool, gender: str) -> dict:
    bname = brand.get("name", "")
    parts = re.split(r"\s*\|\s*", bname)
    ben   = parts[-1].strip() if len(parts) > 1 else bname
    pref  = "تستر" if tester else "عطر"
    title = f"{pref} {name} {size} | {ben}".strip()
    desc  = (f"تسوق {pref} {name} {size} الأصلي من {bname}. "
             f"عطر {gender} فاخر ثابت. أصلي 100% من مهووس.")
    if len(desc) > 160:
        desc = desc[:157] + "..."
    slug = to_slug(f"{ben}-{name}-{size}".replace("مل", "ml"))
    return {
        "url":   slug,
        "title": title,
        "desc":  desc,
        "alt":   f"زجاجة {pref} {name} {size} الأصلية",
    }


def fetch_image(name: str, tester: bool = False) -> str:
    gk = st.session_state.google_api
    cx = st.session_state.google_cse
    if not gk or not cx:
        return ""
    try:
        q = name + (" tester box" if tester else " perfume bottle")
        r = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={"key": gk, "cx": cx, "q": q,
                    "searchType": "image", "num": 1, "imgSize": "large"},
            timeout=10,
        )
        items = r.json().get("items", [])
        return items[0]["link"] if items else ""
    except Exception:
        return ""


def ai_generate(name: str, tester: bool, brand: dict,
                size: str, gender: str, conc: str) -> str:
    key = st.session_state.api_key
    if not key:
        return "<p>أضف مفتاح Anthropic API في الإعدادات أولاً</p>"
    try:
        client = anthropic.Anthropic(api_key=key)
        ptype  = "تستر" if tester else "عطر"
        blink  = ""
        if brand.get("page_url"):
            blink = (f'— <a href="https://mahwous.com/{brand["page_url"]}"'
                     f' target="_blank">{brand["name"]}</a>')
        msg = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=4096,
            system=AI_SYSTEM,
            messages=[{"role": "user", "content":
                f"اكتب وصفاً HTML احترافياً كاملاً:\n"
                f"- النوع: {ptype}\n"
                f"- الاسم: {name}\n"
                f"- الماركة: {brand.get('name', 'غير محدد')} {blink}\n"
                f"- الحجم: {size}\n"
                f"- التركيز: {conc}\n"
                f"- الجنس: {gender}\n"
                f"أعد HTML خالصاً فقط بدون أي نص خارجه."}],
        )
        return msg.content[0].text
    except Exception as e:
        return f"<p>خطأ في الذكاء الاصطناعي: {e}</p>"


def build_empty_salla_row() -> dict:
    r = {c: "" for c in SALLA_COLS}
    r["النوع "]                    = "منتج"
    r["نوع المنتج"]               = "منتج جاهز"
    r["هل يتطلب شحن؟"]           = "نعم"
    r["خاضع للضريبة ؟"]          = "نعم"
    r["الوزن"]                    = "0.2"
    r["وحدة الوزن"]               = "kg"
    r["حالة المنتج"]              = "مرئي"
    r["اقصي كمية لكل عميل"]      = "0"
    r["إخفاء خيار تحديد الكمية"] = "0"
    r["اضافة صورة عند الطلب"]    = "0"
    return r


def fill_row(name, price="", sku="", image="", desc="",
             brand=None, category="", seo=None, no="",
             weight="0.2", weight_unit="kg", size="") -> dict:
    if brand is None:
        brand = {}
    if seo is None:
        seo = {}
    r = build_empty_salla_row()
    r["No."]             = str(no)
    r["أسم المنتج"]      = str(name)
    r["سعر المنتج"]      = str(price)
    r["رمز المنتج sku"]  = str(sku)
    r["صورة المنتج"]     = str(image)
    r["وصف صورة المنتج"] = seo.get("alt", "")
    r["الوصف"]           = str(desc)
    r["الماركة"]         = brand.get("name", "")
    r["تصنيف المنتج"]    = str(category)
    r["الوزن"]           = str(weight) if weight else "0.2"
    r["وحدة الوزن"]      = str(weight_unit) if weight_unit else "kg"
    # If no price → set quantity to 0
    if not str(price).strip() or str(price).strip() in ("0", "nan", "None"):
        r["اقصي كمية لكل عميل"] = "0"
    return r

# ╔══════════════════════════════════════════════════════════════════╗
# ║  EXPORT FUNCTIONS                                               ║
# ╚══════════════════════════════════════════════════════════════════╝

def _style_header_row(ws, row_num: int, cols: list,
                      bg: str = "0F0E0D", fg: str = "B8933A"):
    for i, col in enumerate(cols, 1):
        c = ws.cell(row_num, i, col)
        c.font      = Font(bold=True, color="FFFFFF" if bg != "E8D5B7" else "0F0E0D",
                           name="Cairo", size=9)
        c.fill      = PatternFill("solid", fgColor=bg)
        c.alignment = Alignment(horizontal="center", vertical="center",
                                wrap_text=True, readingOrder=2)
        c.border    = Border(bottom=Side(style="thin", color=fg))
    ws.row_dimensions[row_num].height = 30


def export_product_xlsx(df: pd.DataFrame) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Salla Products Template Sheet"

    # Row 1 — merged section header
    ws.cell(1, 1, "بيانات المنتج")
    ws.merge_cells(start_row=1, start_column=1,
                   end_row=1, end_column=len(SALLA_COLS))
    c = ws.cell(1, 1)
    c.font      = Font(bold=True, color="FFFFFF", name="Cairo", size=12)
    c.fill      = PatternFill("solid", fgColor="0F0E0D")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 28

    # Row 2 — column names
    _style_header_row(ws, 2, SALLA_COLS, bg="E8D5B7", fg="B8933A")

    # Data rows from row 3
    for ri, (_, row) in enumerate(df.iterrows(), 3):
        for ci, col in enumerate(SALLA_COLS, 1):
            v = str(row.get(col, "") if pd.notna(row.get(col, "")) else "")
            c = ws.cell(ri, ci, v)
            c.alignment = Alignment(horizontal="right", vertical="top",
                                    wrap_text=(col == "الوصف"),
                                    readingOrder=2)
            if ri % 2 == 0:
                c.fill = PatternFill("solid", fgColor="FAFAF8")
        ws.row_dimensions[ri].height = 18

    # Column widths
    W = {
        "أسم المنتج": 45, "الوصف": 55, "تصنيف المنتج": 38,
        "صورة المنتج": 46, "الماركة": 24, "No.": 13,
        "وصف صورة المنتج": 36,
    }
    for i, col in enumerate(SALLA_COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = W.get(col, 14)
    ws.freeze_panes = "A3"

    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf.read()


def export_product_csv(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    # Row 1
    out.write("بيانات المنتج" + "," * (len(SALLA_COLS) - 1) + "\n")
    # Row 2
    out.write(",".join(SALLA_COLS) + "\n")
    for _, row in df.iterrows():
        vals = []
        for c in SALLA_COLS:
            v = str(row.get(c, "") if pd.notna(row.get(c, "")) else "")
            if any(x in v for x in [",", "\n", '"']):
                v = f'"{v.replace(chr(34), chr(34)*2)}"'
            vals.append(v)
        out.write(",".join(vals) + "\n")
    return out.getvalue().encode("utf-8-sig")


def export_seo_xlsx(df: pd.DataFrame) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.title = "Salla Product Seo Sheet"
    _style_header_row(ws, 1, SALLA_SEO_COLS, bg="1A1510", fg="B8933A")
    for ri, (_, row) in enumerate(df.iterrows(), 2):
        for ci, col in enumerate(SALLA_SEO_COLS, 1):
            v = str(row.get(col, "") if pd.notna(row.get(col, "")) else "")
            c = ws.cell(ri, ci, v)
            c.alignment = Alignment(horizontal="right", vertical="top",
                                    wrap_text=True, readingOrder=2)
            if ri % 2 == 0:
                c.fill = PatternFill("solid", fgColor="FFF8E1")
        ws.row_dimensions[ri].height = 18
    W2 = {"اسم المنتج (غير قابل للتعديل)": 50,
          "وصف صفحة المنتج (SEO Page Description)": 65,
          "عنوان صفحة المنتج (SEO Page Title)": 52}
    for i, col in enumerate(SALLA_SEO_COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = W2.get(col, 22)
    ws.freeze_panes = "A2"
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.read()


def export_seo_csv(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    out.write(",".join(SALLA_SEO_COLS) + "\n")
    for _, row in df.iterrows():
        vals = []
        for c in SALLA_SEO_COLS:
            v = str(row.get(c, "") if pd.notna(row.get(c, "")) else "")
            if any(x in v for x in [",", "\n"]):
                v = f'"{v}"'
            vals.append(v)
        out.write(",".join(vals) + "\n")
    return out.getvalue().encode("utf-8-sig")


def export_price_xlsx(df: pd.DataFrame) -> bytes:
    wb = Workbook(); ws = wb.active; ws.title = "Price Update"
    ws.cell(1, 1, "بيانات المنتج")
    ws.merge_cells(start_row=1, start_column=1,
                   end_row=1, end_column=len(SALLA_PRICE_COLS))
    c = ws.cell(1, 1)
    c.font      = Font(bold=True, color="FFFFFF", name="Cairo")
    c.fill      = PatternFill("solid", fgColor="0F0E0D")
    c.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[1].height = 26
    _style_header_row(ws, 2, SALLA_PRICE_COLS, bg="E8D5B7", fg="B8933A")
    for ri, (_, row) in enumerate(df.iterrows(), 3):
        for ci, col in enumerate(SALLA_PRICE_COLS, 1):
            ws.cell(ri, ci, str(row.get(col, "") or ""))
        ws.row_dimensions[ri].height = 18
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.read()


def export_price_csv(df: pd.DataFrame) -> bytes:
    out = io.StringIO()
    out.write("بيانات المنتج" + "," * (len(SALLA_PRICE_COLS) - 1) + "\n")
    out.write(",".join(SALLA_PRICE_COLS) + "\n")
    for _, row in df.iterrows():
        out.write(",".join([f'"{str(row.get(c,"") or "")}"'
                            for c in SALLA_PRICE_COLS]) + "\n")
    return out.getvalue().encode("utf-8-sig")


def export_brands_xlsx(brands_list: list) -> bytes:
    """Export new brands in Salla brands file format."""
    wb = Workbook(); ws = wb.active; ws.title = "New Brands"
    _style_header_row(ws, 1, SALLA_BRANDS_COLS, bg="0F0E0D", fg="B8933A")
    for ri, brand in enumerate(brands_list, 2):
        for ci, col in enumerate(SALLA_BRANDS_COLS, 1):
            ws.cell(ri, ci, str(brand.get(col, "") or ""))
        ws.row_dimensions[ri].height = 18
    for i, col in enumerate(SALLA_BRANDS_COLS, 1):
        ws.column_dimensions[get_column_letter(i)].width = 40 if i == 3 else 28
    buf = io.BytesIO(); wb.save(buf); buf.seek(0)
    return buf.read()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR NAVIGATION                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:18px 0 10px">
      <div style="font-size:2.4rem">🌸</div>
      <div style="color:#b8933a;font-size:1.25rem;font-weight:900;margin:4px 0">مهووس</div>
      <div style="color:rgba(255,255,255,0.3);font-size:0.7rem">مركز التحكم الشامل v4.5</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    PAGES = [
        ("🛠️", "المُعالج الشامل",       "processor"),
        ("💰", "مُحدّث الأسعار",        "price"),
        ("➕", "منتج سريع",              "quickadd"),
        ("🔀", "المقارنة والتدقيق",     "compare"),
        ("🔍", "مدقق الماركات",         "brands"),
        ("⚙️", "الإعدادات",             "settings"),
    ]
    for icon, label, key in PAGES:
        active = st.session_state.page == key
        if st.button(f"{icon}  {label}", use_container_width=True,
                     type="primary" if active else "secondary",
                     key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()

    st.divider()
    # Status
    bok = st.session_state.brands_df is not None
    cok = st.session_state.categories_df is not None
    aok = bool(st.session_state.api_key)
    gok = bool(st.session_state.google_api and st.session_state.google_cse)

    status_html = "".join([
        f'<div style="font-size:0.77rem;padding:3px 0">{"✅" if bok else "❌"} '
        f'الماركات: {len(st.session_state.brands_df) if bok else "غير محملة"}</div>',
        f'<div style="font-size:0.77rem;padding:3px 0">{"✅" if cok else "❌"} '
        f'التصنيفات: {len(st.session_state.categories_df) if cok else "غير محملة"}</div>',
        f'<div style="font-size:0.77rem;padding:3px 0">{"✅" if aok else "❌"} '
        f'Claude API: {"متصل" if aok else "غير مضبوط"}</div>',
        f'<div style="font-size:0.77rem;padding:3px 0">{"✅" if gok else "—"} '
        f'Google CSE: {"متصل" if gok else "غير مضبوط"}</div>',
    ])
    st.markdown(status_html, unsafe_allow_html=True)

    # New brands indicator
    if st.session_state.new_brands:
        st.divider()
        nb = len(st.session_state.new_brands)
        st.markdown(f'<div style="font-size:0.77rem;padding:3px 0;color:#f9a825">🆕 {nb} ماركة جديدة بانتظار التصدير</div>',
                    unsafe_allow_html=True)

    # Active file info
    if st.session_state.up_df is not None:
        st.divider()
        fname = st.session_state.up_filename
        nrows = len(st.session_state.up_df)
        st.markdown(f"""
        <div style="background:rgba(184,147,58,0.1);border-radius:8px;padding:10px;
                    font-size:0.78rem;border:1px solid rgba(184,147,58,0.25)">
          <div style="font-weight:800;margin-bottom:4px">📄 الملف النشط</div>
          <div style="color:#b8933a">{fname[:30]}</div>
          <div style="color:rgba(255,255,255,0.4)">{nrows} صف</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ إغلاق الملف", use_container_width=True):
            st.session_state.up_raw     = None
            st.session_state.up_df      = None
            st.session_state.up_seo     = None
            st.session_state.up_filename = ""
            st.session_state.up_mapped  = False
            st.rerun()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE HEADER                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
TITLES = {
    "processor": ("🛠️ المُعالج الشامل",       "ارفع أي ملف — اربط الأعمدة — اكمل بالذكاء الاصطناعي — صدّر لسلة"),
    "price":     ("💰 مُحدّث الأسعار",        "رفع أي ملف أسعار وتصديره بتنسيق سلة الدقيق"),
    "quickadd":  ("➕ منتج سريع",              "أدخل اسم العطر فقط وسيكمل النظام الباقي"),
    "compare":   ("🔀 المقارنة والتدقيق",     "قارن المنتجات الجديدة بالمتجر — استبعد المكرر — اعتمد أو ألغِ المشبوه"),
    "brands":    ("🔍 مدقق الماركات",         "قارن قائمة ماركات بقاعدة بيانات مهووس"),
    "settings":  ("⚙️ الإعدادات",             "مفاتيح API وقواعد البيانات المرجعية"),
}
ttl, sub = TITLES.get(st.session_state.page, ("مهووس", ""))
st.markdown(f"""
<div class="mhw-header">
  <div class="emblem">م</div>
  <div><h1>{ttl}</h1><p>{sub}</p></div>
</div>
""", unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 1 — UNIVERSAL PROCESSOR                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
if st.session_state.page == "processor":

    # ── STEP A: Upload ────────────────────────────────────────────
    st.markdown("""<div class="sec-title"><div class="bar"></div><h3>الخطوة 1 — رفع الملف</h3></div>""",
                unsafe_allow_html=True)

    uc1, uc2 = st.columns([4, 1])
    with uc1:
        up_file = st.file_uploader(
            "ارفع أي ملف Excel أو CSV (من أي مصدر — ملفات سلة، موردين، قوائم أسماء...)",
            type=["csv", "xlsx", "xls", "xlsm"],
            label_visibility="collapsed",
            key="proc_uploader",
        )
    with uc2:
        is_salla_file = st.checkbox("ملف سلة\n(صفّان في الرأس)", value=False, key="is_salla")

    if up_file:
        df_raw = read_file(up_file, salla_2row=is_salla_file)
        if not df_raw.empty:
            st.session_state.up_raw      = df_raw
            st.session_state.up_filename = up_file.name
            st.session_state.up_mapped   = False
            # If it's already a Salla file with enough columns, auto-map
            if sum(1 for c in SALLA_COLS if c in df_raw.columns) >= 8:
                full = pd.DataFrame(columns=SALLA_COLS)
                for col in SALLA_COLS:
                    full[col] = df_raw[col] if col in df_raw.columns else ""
                st.session_state.up_df    = full
                st.session_state.up_mapped = True
            else:
                st.session_state.up_df = None

    # ── STEP B: Column Mapping ────────────────────────────────────
    if st.session_state.up_raw is not None and not st.session_state.up_mapped:
        raw = st.session_state.up_raw
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الخطوة 2 — تعيين الأعمدة</h3></div>""", unsafe_allow_html=True)

        st.markdown(f"""<div class="al-info">
        وجدت <b>{len(raw.columns)}</b> عمود و <b>{len(raw)}</b> صف.
        حدد أي عمود يمثل كل حقل من حقول سلة:
        </div>""", unsafe_allow_html=True)

        with st.expander("👀 معاينة الملف الأصلي", expanded=True):
            st.dataframe(raw.head(8), use_container_width=True)

        NONE_OPT = "— لا يوجد —"
        opts = [NONE_OPT] + list(raw.columns)

        def gi(kws):
            g = auto_guess_col(raw.columns, kws)
            return opts.index(g) if g in opts else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            col_name  = st.selectbox("اسم المنتج / العطر ⭐",  opts, index=gi(["اسم","name","منتج","عطر","product"]),  key="cm_nm")
            col_price = st.selectbox("السعر",                   opts, index=gi(["سعر","price","cost"]),                 key="cm_pr")
        with c2:
            col_sku   = st.selectbox("رمز SKU",                 opts, index=gi(["sku","رمز","barcode","كود"]),          key="cm_sk")
            col_size  = st.selectbox("الحجم",                   opts, index=gi(["حجم","size","مل","ml","volume"]),      key="cm_sz")
        with c3:
            col_img   = st.selectbox("رابط الصورة",             opts, index=gi(["صورة","image","img","photo","url"]),   key="cm_im")
            col_desc  = st.selectbox("الوصف (إن وجد)",          opts, index=gi(["وصف","desc","description"]),           key="cm_de")

        c4, c5, c6, c7 = st.columns(4)
        with c4:
            col_brand  = st.selectbox("الماركة (إن وجدت)",      opts, index=gi(["ماركة","brand","علامة"]),             key="cm_br")
        with c5:
            col_gender = st.selectbox("الجنس (إن وجد)",         opts, index=gi(["جنس","gender","sex"]),                 key="cm_gn")
        with c6:
            col_tester = st.selectbox("تستر/عادي (إن وجد)",    opts, index=gi(["تستر","tester","نوع","type"]),          key="cm_ts")
        with c7:
            col_weight = st.selectbox("الوزن (إن وجد)",         opts, index=gi(["وزن","weight"]),                       key="cm_wt")

        st.markdown("**الإعدادات الافتراضية** (تُطبق عند غياب العمود المقابل):")
        d1, d2, d3, d4, d5 = st.columns(5)
        with d1: dft_gender = st.selectbox("الجنس",     ["للجنسين","للرجال","للنساء"],       key="dft_gn")
        with d2: dft_size   = st.text_input("الحجم",    "100 مل",                             key="dft_sz")
        with d3: dft_conc   = st.selectbox("التركيز",   ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="dft_cn")
        with d4: dft_type   = st.selectbox("النوع",     ["عطر عادي","تستر"],                  key="dft_tp")
        with d5: dft_weight = st.text_input("الوزن (kg)","0.2",                               key="dft_wt")

        if col_name == NONE_OPT:
            st.warning("⚠️ يرجى تحديد عمود اسم المنتج على الأقل")
        else:
            if st.button("✅ تأكيد وتحويل الملف إلى تنسيق سلة", type="primary", key="map_btn"):
                rows_out = []
                seo_out  = []
                new_brands_found = []
                for _, src in raw.iterrows():
                    def gv(col):
                        if col == NONE_OPT or col not in raw.columns:
                            return ""
                        return str(src.get(col, "") or "").strip()

                    name = gv(col_name)
                    if not name or name.lower() in ("nan", "none", ""):
                        continue

                    price     = gv(col_price)
                    sku       = gv(col_sku)
                    img       = gv(col_img)
                    desc      = gv(col_desc)
                    size      = gv(col_size) or dft_size
                    gender    = gv(col_gender) or dft_gender
                    brand_raw = gv(col_brand)
                    tester_v  = gv(col_tester)
                    weight    = gv(col_weight) or dft_weight

                    is_test = any(w in tester_v.lower()
                                  for w in ["تستر","tester","yes","نعم"]) \
                              if col_tester != NONE_OPT else (dft_type == "تستر")

                    brand = match_brand(name) if not brand_raw else \
                               {"name": brand_raw, "page_url": ""}

                    # If brand not found in database → generate new brand
                    if not brand.get("name") and brand_raw:
                        existing_new = [b["اسم العلامة التجارية"] for b in st.session_state.new_brands]
                        if brand_raw not in existing_new and brand_raw not in new_brands_found:
                            new_brands_found.append(brand_raw)
                        brand = {"name": brand_raw, "page_url": to_slug(brand_raw)}

                    cat      = match_category(name, gender)
                    seo      = gen_seo(name, brand, size, is_test, gender)

                    nr = fill_row(name=name, price=price, sku=sku, image=img,
                                  desc=desc, brand=brand, category=cat, seo=seo,
                                  weight=weight)
                    rows_out.append(nr)
                    seo_out.append({
                        "No. (غير قابل للتعديل)":            nr["No."],
                        "اسم المنتج (غير قابل للتعديل)":     name,
                        "رابط مخصص للمنتج (SEO Page URL)":   seo["url"],
                        "عنوان صفحة المنتج (SEO Page Title)": seo["title"],
                        "وصف صفحة المنتج (SEO Page Description)": seo["desc"],
                    })

                st.session_state.up_df     = pd.DataFrame(rows_out)
                st.session_state.up_seo    = pd.DataFrame(seo_out)
                st.session_state.up_mapped = True

                # Add new brands to session
                if new_brands_found:
                    st.info(f"🆕 تم اكتشاف {len(new_brands_found)} ماركة جديدة — يمكن تصديرها من صفحة الإعدادات")
                    for bn in new_brands_found:
                        st.session_state.new_brands.append({
                            "اسم العلامة التجارية": bn,
                            "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(bn),
                            "وصف العلامة التجارية": "",
                            "صورة العلامة التجارية": "",
                        })

                st.success(f"✅ تم تحويل {len(rows_out)} صف إلى تنسيق سلة بنجاح!")
                st.rerun()

    # ── STEP C: Toolbox + Editor ──────────────────────────────────
    if st.session_state.up_df is not None and st.session_state.up_mapped:
        df = st.session_state.up_df

        # Stats
        def _cnt(col):
            return int((df.get(col, pd.Series(dtype=str)).fillna("")
                        .str.strip() != "").sum())

        no_img   = int((df.get("صورة المنتج",   pd.Series(dtype=str)).fillna("").str.strip() == "").sum())
        no_desc  = int((df.get("الوصف",          pd.Series(dtype=str)).fillna("").str.strip() == "").sum())
        no_brand = int((df.get("الماركة",        pd.Series(dtype=str)).fillna("").str.strip() == "").sum())
        no_price = int((df.get("سعر المنتج",     pd.Series(dtype=str)).fillna("").str.strip().isin(["","0","nan"]).sum()))

        st.markdown(f"""
        <div class="stats-bar">
          <div class="stat-box"><div class="n">{len(df)}</div><div class="lb">إجمالي المنتجات</div></div>
          <div class="stat-box"><div class="n" style="color:{'#e53935' if no_img else '#43a047'}">{no_img}</div><div class="lb">بدون صورة</div></div>
          <div class="stat-box"><div class="n" style="color:{'#e53935' if no_desc else '#43a047'}">{no_desc}</div><div class="lb">بدون وصف</div></div>
          <div class="stat-box"><div class="n" style="color:{'#f9a825' if no_brand else '#43a047'}">{no_brand}</div><div class="lb">بدون ماركة</div></div>
          <div class="stat-box"><div class="n" style="color:{'#e53935' if no_price else '#43a047'}">{no_price}</div><div class="lb">بدون سعر</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── TOOLBOX TABS ──────────────────────────────────────────
        st.markdown("""<div class="sec-title"><div class="bar"></div>
        <h3>أدوات المعالجة الذكية</h3></div>""", unsafe_allow_html=True)

        tabs = st.tabs(["🤖 توليد الأوصاف", "🖼 جلب الصور",
                        "🏷 الماركات والتصنيفات", "➕ إضافة منتج", "⚡ عمليات مجمعة"])

        # ── Tab 0: AI Descriptions ─────────────────────────────
        with tabs[0]:
            st.markdown("**توليد الوصف الاحترافي بالذكاء الاصطناعي (Claude)**")
            gen_scope = st.radio("نطاق التوليد:", [
                "الصفوف التي ليس لها وصف فقط",
                "صف واحد بتحديده",
                "كل الصفوف (سيستغرق وقتاً)",
            ], horizontal=True, key="gen_scope")

            dft_conc_ai = st.selectbox("التركيز الافتراضي:", ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="ai_conc")
            dft_gn_ai   = st.selectbox("الجنس الافتراضي:",  ["للجنسين","للرجال","للنساء"], key="ai_gn")
            dft_sz_ai   = st.text_input("الحجم الافتراضي:", "100 مل", key="ai_sz")

            if gen_scope == "صف واحد بتحديده":
                sel_ai = st.number_input("رقم الصف:", 0, max(0, len(df)-1), 0, key="ai_row")

            if st.button("✨ توليد الأوصاف الآن", type="primary", key="gen_desc_btn"):
                if not st.session_state.api_key:
                    st.error("أضف مفتاح Anthropic API في الإعدادات أولاً")
                else:
                    if gen_scope == "الصفوف التي ليس لها وصف فقط":
                        idxs = [i for i in range(len(df))
                                if not str(df.iloc[i].get("الوصف","")).strip()]
                    elif gen_scope == "صف واحد بتحديده":
                        idxs = [sel_ai]
                    else:
                        idxs = list(range(len(df)))

                    prog = st.progress(0); stat = st.empty()
                    for n, i in enumerate(idxs):
                        row  = df.iloc[i]
                        name = str(row.get("أسم المنتج","")).strip()
                        if not name: continue
                        stat.markdown(f'<div class="prog-run">توليد ({n+1}/{len(idxs)}): {name}</div>',
                                      unsafe_allow_html=True)
                        is_t  = any(w in name.lower() for w in ["تستر","tester"])
                        brand = {"name": str(row.get("الماركة","") or ""),
                                 "page_url": to_slug(str(row.get("الماركة","") or ""))}
                        size_m = re.search(r"\d+\s*(?:مل|ml)", name, re.I)
                        size   = size_m.group() if size_m else dft_sz_ai
                        gender = (str(row.get("تصنيف المنتج","")) + " " + name)
                        gender = ("للنساء" if any(w in gender for w in ["نسائ","women"])
                                  else "للرجال" if any(w in gender for w in ["رجال","men"])
                                  else dft_gn_ai)
                        desc = ai_generate(name, is_t, brand, size, gender, dft_conc_ai)
                        df.at[df.index[i], "الوصف"] = desc
                        prog.progress(int((n+1)/len(idxs)*100))

                    st.session_state.up_df = df
                    stat.markdown(f'<div class="prog-ok">✅ تم توليد {len(idxs)} وصف!</div>',
                                  unsafe_allow_html=True)
                    st.rerun()

        # ── Tab 1: Images ──────────────────────────────────────
        with tabs[1]:
            st.markdown("**جلب الصور تلقائياً عبر Google Custom Search**")
            if not (st.session_state.google_api and st.session_state.google_cse):
                st.markdown("""<div class="al-warn">
                أضف GOOGLE_API_KEY و GOOGLE_CSE_ID في الإعدادات لتفعيل جلب الصور.
                </div>""", unsafe_allow_html=True)

            img_scope = st.radio("نطاق الجلب:", [
                "الصفوف بدون صورة فقط",
                "كل الصفوف",
            ], horizontal=True, key="img_scope")
            add_test_kw = st.checkbox("إضافة كلمة 'tester box' للتستر", value=True, key="add_tk")

            if st.button("🖼 جلب الصور الآن", type="primary", key="fetch_img_btn"):
                idxs = ([i for i in range(len(df))
                         if not str(df.iloc[i].get("صورة المنتج","")).strip()]
                        if img_scope.startswith("الصفوف") else list(range(len(df))))
                prog = st.progress(0); stat = st.empty(); fetched = 0
                for n, i in enumerate(idxs):
                    name = str(df.iloc[i].get("أسم المنتج","")).strip()
                    if not name: continue
                    stat.markdown(
                        f'<div class="prog-run">🖼 ({n+1}/{len(idxs)}) {name}</div>',
                        unsafe_allow_html=True)
                    is_t = add_test_kw and any(w in name.lower() for w in ["تستر","tester"])
                    url  = fetch_image(name, is_t)
                    if url:
                        df.at[df.index[i], "صورة المنتج"] = url
                        fetched += 1
                    prog.progress(int((n+1)/len(idxs)*100))

                st.session_state.up_df = df
                stat.markdown(f'<div class="prog-ok">✅ تم جلب {fetched} صورة من {len(idxs)} صف</div>',
                              unsafe_allow_html=True)
                st.rerun()

            st.divider()
            st.markdown("**إضافة رابط صورة يدوياً لصف محدد:**")
            mi1, mi2, mi3 = st.columns([1, 4, 1])
            with mi1: man_row = st.number_input("رقم الصف", 0, max(0, len(df)-1), 0, key="man_r")
            with mi2: man_url = st.text_input("رابط الصورة", placeholder="https://...", key="man_u")
            with mi3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("حفظ", key="save_man"):
                    if man_url.startswith("http"):
                        df.at[df.index[man_row], "صورة المنتج"] = man_url
                        st.session_state.up_df = df
                        st.success("✅ تم حفظ الصورة")
                        st.rerun()

        # ── Tab 2: Brands & Categories ─────────────────────────
        with tabs[2]:
            st.markdown("**تعيين الماركات والتصنيفات التلقائي والمنابي**")
            scope_b = st.radio("نطاق:", [
                "الصفوف التي ليس لها ماركة فقط",
                "كل الصفوف (يُعيد التعيين)",
            ], horizontal=True, key="scope_b")

            if st.button("🏷 تعيين الآن", type="primary", key="assign_b"):
                idxs = ([i for i in range(len(df))
                         if not str(df.iloc[i].get("الماركة","")).strip()]
                        if scope_b.startswith("الصفوف") else list(range(len(df))))
                new_brands_auto = []
                for i in idxs:
                    name  = str(df.iloc[i].get("أسم المنتج","")).strip()
                    if not name: continue
                    brand = match_brand(name)
                    cat   = match_category(name)
                    if brand.get("name"):
                        df.at[df.index[i], "الماركة"] = brand["name"]
                    else:
                        # Try to extract brand from name (first word or two)
                        words = name.split()
                        guessed = words[0] if words else ""
                        if guessed and len(guessed) > 2:
                            df.at[df.index[i], "الماركة"] = guessed
                            existing = [b["اسم العلامة التجارية"] for b in st.session_state.new_brands]
                            if guessed not in existing and guessed not in new_brands_auto:
                                new_brands_auto.append(guessed)
                    if not str(df.iloc[i].get("تصنيف المنتج","")).strip():
                        df.at[df.index[i], "تصنيف المنتج"] = cat
                st.session_state.up_df = df
                if new_brands_auto:
                    for bn in new_brands_auto:
                        st.session_state.new_brands.append({
                            "اسم العلامة التجارية": bn,
                            "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(bn),
                            "وصف العلامة التجارية": "",
                            "صورة العلامة التجارية": "",
                        })
                    st.info(f"🆕 {len(new_brands_auto)} ماركة جديدة أُضيفت — صدّرها من الإعدادات")
                st.success(f"✅ تم التعيين لـ {len(idxs)} صف")
                st.rerun()

            st.divider()
            st.markdown("**تعديل يدوي لصف محدد:**")
            bc1, bc2, bc3 = st.columns(3)
            with bc1:
                b_row = st.number_input("رقم الصف", 0, max(0, len(df)-1), 0, key="b_row")
            bdf = st.session_state.brands_df
            cdf = st.session_state.categories_df
            brands_list = ["— اختر —"] + (
                [str(r.iloc[0]) for _, r in bdf.iterrows()] if bdf is not None else [])
            cats_list = ["— اختر —"] + (
                [str(r.get("التصنيفات","")) for _, r in cdf.iterrows()] if cdf is not None else [])
            with bc2:
                sel_brand = st.selectbox("الماركة", brands_list, key="sel_b")
            with bc3:
                sel_cat   = st.selectbox("التصنيف",  cats_list,   key="sel_c")
            if st.button("✅ تطبيق على الصف", key="apply_b"):
                if sel_brand != "— اختر —":
                    df.at[df.index[b_row], "الماركة"] = sel_brand
                if sel_cat != "— اختر —" and cdf is not None:
                    crow = cdf[cdf["التصنيفات"] == sel_cat]
                    if not crow.empty:
                        par  = str(crow.iloc[0].get("التصنيف الاساسي",""))
                        path = f"{par} > {sel_cat}" if par.strip() else sel_cat
                    else:
                        path = sel_cat
                    df.at[df.index[b_row], "تصنيف المنتج"] = path
                st.session_state.up_df = df
                st.success("✅ تم التطبيق")
                st.rerun()

        # ── Tab 3: Add Product ─────────────────────────────────
        with tabs[3]:
            st.markdown("**إضافة منتج جديد — أدخل الاسم وسيكمل النظام الباقي**")
            np1, np2, np3, np4 = st.columns(4)
            with np1: np_name   = st.text_input("اسم العطر ⭐", placeholder="ديور سوفاج 100 مل", key="np_nm")
            with np2: np_gender = st.selectbox("الجنس", ["للجنسين","للرجال","للنساء"], key="np_gn")
            with np3: np_size   = st.text_input("الحجم", "100 مل", key="np_sz")
            with np4: np_conc   = st.selectbox("التركيز", ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="np_cn")
            np5, np6, np7, np8 = st.columns(4)
            with np5: np_price  = st.text_input("السعر", key="np_pr")
            with np6: np_sku    = st.text_input("SKU", key="np_sk")
            with np7: np_img    = st.text_input("رابط الصورة", key="np_im")
            with np8: np_type   = st.selectbox("النوع", ["عطر عادي","تستر"], key="np_tp")
            np9, np10 = st.columns(2)
            with np9:  np_weight = st.text_input("الوزن (kg)", "0.2", key="np_wt")
            with np10: np_brand_manual = st.text_input("الماركة (يدوي — اتركه فارغاً للكشف التلقائي)", key="np_br")

            ops1, ops2, ops3 = st.columns(3)
            with ops1: do_d = st.checkbox("🤖 توليد وصف AI",   value=True,  key="np_do_d")
            with ops2: do_i = st.checkbox("🖼 جلب صورة",       value=False, key="np_do_i")
            with ops3: do_s = st.checkbox("🔍 توليد SEO",       value=True,  key="np_do_s")

            if st.button("➕ إضافة للجدول", type="primary", key="add_to_table"):
                if not np_name.strip():
                    st.error("أدخل اسم العطر")
                else:
                    with st.spinner("جاري المعالجة..."):
                        is_t   = np_type == "تستر"
                        if np_brand_manual.strip():
                            brand = {"name": np_brand_manual.strip(),
                                     "page_url": to_slug(np_brand_manual.strip())}
                            # Check if new brand
                            existing = [b["اسم العلامة التجارية"] for b in st.session_state.new_brands]
                            if match_brand(np_name).get("name") == "" and np_brand_manual not in existing:
                                st.session_state.new_brands.append({
                                    "اسم العلامة التجارية": np_brand_manual.strip(),
                                    "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(np_brand_manual.strip()),
                                    "وصف العلامة التجارية": "",
                                    "صورة العلامة التجارية": "",
                                })
                        else:
                            brand  = match_brand(np_name)
                        cat    = match_category(np_name, np_gender)
                        seo    = gen_seo(np_name, brand, np_size, is_t, np_gender)
                        img    = np_img or (fetch_image(np_name, is_t) if do_i else "")
                        desc   = ai_generate(np_name, is_t, brand, np_size, np_gender, np_conc) \
                                 if do_d else ""
                        nr     = fill_row(name=np_name, price=np_price, sku=np_sku,
                                          image=img, desc=desc, brand=brand,
                                          category=cat, seo=seo, weight=np_weight)
                        new_df = pd.DataFrame([nr])
                        st.session_state.up_df = pd.concat(
                            [df, new_df], ignore_index=True)
                        if st.session_state.up_seo is not None:
                            st.session_state.up_seo = pd.concat([
                                st.session_state.up_seo,
                                pd.DataFrame([{
                                    "No. (غير قابل للتعديل)": "",
                                    "اسم المنتج (غير قابل للتعديل)": np_name,
                                    "رابط مخصص للمنتج (SEO Page URL)": seo["url"],
                                    "عنوان صفحة المنتج (SEO Page Title)": seo["title"],
                                    "وصف صفحة المنتج (SEO Page Description)": seo["desc"],
                                }])
                            ], ignore_index=True)
                    st.success(f"✅ تمت إضافة: **{np_name}**")
                    st.rerun()

        # ── Tab 4: Bulk Ops ────────────────────────────────────
        with tabs[4]:
            st.markdown("**تنفيذ عمليات متعددة دفعة واحدة على كل الصفوف**")
            bulk_ops = st.multiselect("اختر العمليات:", [
                "🏷 تعيين الماركات الفارغة",
                "📂 تعيين التصنيفات الفارغة",
                "📋 تعيين القيم الثابتة (نوع، شحن، ضريبة، وزن)",
                "🔤 توليد Alt Text للصور",
                "🔍 توليد SEO لكل الصفوف",
                "⚖️ تعيين وزن افتراضي للصفوف الفارغة",
            ], key="bulk_ops")

            dft_bulk_weight = st.text_input("الوزن الافتراضي (kg):", "0.2", key="bulk_wt")

            if st.button("⚡ تنفيذ الآن", type="primary", key="bulk_run"):
                prog = st.progress(0); stat = st.empty()
                seo_rows = []
                for n, (idx, row) in enumerate(df.iterrows()):
                    prog.progress(int((n+1)/len(df)*100))
                    name = str(row.get("أسم المنتج","")).strip()
                    if not name: continue
                    brand  = match_brand(name)
                    is_t   = any(w in name.lower() for w in ["تستر","tester"])
                    size_m = re.search(r"\d+\s*(?:مل|ml)", name, re.I)
                    size   = size_m.group() if size_m else "100 مل"
                    gender = ("للنساء" if any(w in name for w in ["نسائ","women"])
                              else "للرجال" if any(w in name for w in ["رجال","men"])
                              else "للجنسين")
                    seo = gen_seo(name, brand, size, is_t, gender)

                    if "🏷 تعيين الماركات الفارغة" in bulk_ops \
                            and not str(row.get("الماركة","")).strip():
                        df.at[idx, "الماركة"] = brand.get("name","")
                    if "📂 تعيين التصنيفات الفارغة" in bulk_ops \
                            and not str(row.get("تصنيف المنتج","")).strip():
                        df.at[idx, "تصنيف المنتج"] = match_category(name, gender)
                    if "📋 تعيين القيم الثابتة (نوع، شحن، ضريبة، وزن)" in bulk_ops:
                        df.at[idx, "النوع "]                    = "منتج"
                        df.at[idx, "نوع المنتج"]               = "منتج جاهز"
                        df.at[idx, "هل يتطلب شحن؟"]           = "نعم"
                        df.at[idx, "خاضع للضريبة ؟"]          = "نعم"
                        df.at[idx, "الوزن"]                    = df.at[idx, "الوزن"] or dft_bulk_weight
                        df.at[idx, "وحدة الوزن"]               = df.at[idx, "وحدة الوزن"] or "kg"
                        df.at[idx, "حالة المنتج"]              = df.at[idx, "حالة المنتج"] or "مرئي"
                        df.at[idx, "اقصي كمية لكل عميل"]      = df.at[idx, "اقصي كمية لكل عميل"] or "0"
                        df.at[idx, "إخفاء خيار تحديد الكمية"] = "0"
                        df.at[idx, "اضافة صورة عند الطلب"]    = "0"
                    if "⚖️ تعيين وزن افتراضي للصفوف الفارغة" in bulk_ops:
                        if not str(df.at[idx, "الوزن"]).strip() or str(df.at[idx, "الوزن"]).strip() in ("0","nan"):
                            df.at[idx, "الوزن"]      = dft_bulk_weight
                            df.at[idx, "وحدة الوزن"] = "kg"
                    if "🔤 توليد Alt Text للصور" in bulk_ops:
                        df.at[idx, "وصف صورة المنتج"] = seo["alt"]
                    if "🔍 توليد SEO لكل الصفوف" in bulk_ops:
                        seo_rows.append({
                            "No. (غير قابل للتعديل)":            str(row.get("No.","") or ""),
                            "اسم المنتج (غير قابل للتعديل)":     name,
                            "رابط مخصص للمنتج (SEO Page URL)":   seo["url"],
                            "عنوان صفحة المنتج (SEO Page Title)": seo["title"],
                            "وصف صفحة المنتج (SEO Page Description)": seo["desc"],
                        })

                st.session_state.up_df = df
                if seo_rows:
                    st.session_state.up_seo = pd.DataFrame(seo_rows)
                stat.markdown('<div class="prog-ok">✅ تمت جميع العمليات!</div>',
                              unsafe_allow_html=True)
                st.rerun()

        # ── EDITABLE GRID ─────────────────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الجدول التفاعلي — عدّل أي خلية مباشرةً (مثل Excel)</h3></div>""",
                    unsafe_allow_html=True)

        all_c = list(df.columns)
        show_default = [c for c in EDITOR_COLS if c in all_c]
        show_cols = st.multiselect(
            "الأعمدة المعروضة:", options=all_c, default=show_default, key="show_cols")
        if not show_cols:
            show_cols = show_default or all_c[:8]

        edited = st.data_editor(
            df[show_cols].fillna(""),
            use_container_width=True,
            num_rows="dynamic",
            height=440,
            key="main_grid",
        )
        for c in show_cols:
            df[c] = edited[c]
        st.session_state.up_df = df

        # Description editor (single row)
        with st.expander("📝 تعديل الوصف HTML — منتج واحد"):
            sel_p = st.selectbox(
                "اختر المنتج:",
                range(len(df)),
                format_func=lambda i: str(df.iloc[i].get("أسم المنتج", f"صف {i}")),
                key="sel_p",
            )
            cur_d = str(df.iloc[sel_p].get("الوصف","") or "")
            new_d = st.text_area("الوصف (HTML):", value=cur_d, height=280, key="desc_area")
            if st.button("💾 حفظ الوصف", key="save_d"):
                df.at[df.index[sel_p], "الوصف"] = new_d
                st.session_state.up_df = df
                st.success("✅ تم حفظ الوصف")
                st.rerun()

        # SEO table
        if st.session_state.up_seo is not None:
            with st.expander("🔍 جدول SEO — قابل للتعديل"):
                ed_seo = st.data_editor(
                    st.session_state.up_seo.fillna(""),
                    use_container_width=True, num_rows="dynamic", key="seo_grid")
                st.session_state.up_seo = ed_seo

        # ── EXPORT ────────────────────────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>التصدير — جاهز للرفع على سلة</h3></div>""", unsafe_allow_html=True)

        e1, e2, e3, e4, e5 = st.columns(5)
        with e1:
            st.download_button(
                "📥 ملف المنتجات — Excel",
                export_product_xlsx(df),
                "mahwous_products.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="exp_px")
        with e2:
            st.download_button(
                "📥 ملف المنتجات — CSV",
                export_product_csv(df),
                "mahwous_products.csv", "text/csv",
                use_container_width=True, key="exp_pc")
        with e3:
            if st.session_state.up_seo is not None:
                st.download_button(
                    "📥 ملف SEO — Excel",
                    export_seo_xlsx(st.session_state.up_seo),
                    "mahwous_seo.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, key="exp_sx")
            else:
                st.info("نفّذ 'توليد SEO لكل الصفوف' أولاً")
        with e4:
            if st.session_state.up_seo is not None:
                st.download_button(
                    "📥 ملف SEO — CSV",
                    export_seo_csv(st.session_state.up_seo),
                    "mahwous_seo.csv", "text/csv",
                    use_container_width=True, key="exp_sc")
        with e5:
            if st.button("🔀 نقل للمقارنة", use_container_width=True, key="move_to_cmp"):
                st.session_state.cmp_new_df = df.copy()
                st.session_state.page = "compare"
                st.rerun()

    elif st.session_state.up_raw is None:
        st.markdown("""
        <div class="upload-zone">
          <div class="uz-icon">📂</div>
          <div class="uz-title">ارفع ملفك للبدء</div>
          <div class="uz-sub">يدعم: Excel (.xlsx / .xls) | CSV (UTF-8 / Windows-1256 / Latin)</div>
          <div class="uz-sub" style="margin-top:8px">
            ملفات سلة الجاهزة | ملفات الموردين | قوائم أسماء | أي تنسيق
          </div>
        </div>
        """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 2 — PRICE UPDATER                                         ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "price":

    up_p = st.file_uploader("ارفع ملف الأسعار (CSV / Excel)",
                            type=["csv","xlsx","xls"], key="price_up")
    if up_p:
        pdf = read_file(up_p)
        if not pdf.empty:
            st.success(f"✅ {len(pdf)} صف، {len(pdf.columns)} عمود")
            with st.expander("👀 معاينة"): st.dataframe(pdf.head(8), use_container_width=True)

            NONE = "— لا يوجد —"
            pc   = [NONE] + list(pdf.columns)
            def pi(kws): return pc.index(auto_guess_col(pdf.columns, kws)) \
                         if auto_guess_col(pdf.columns, kws) in pc else 0

            p1,p2,p3,p4,p5 = st.columns(5)
            with p1: pno  = st.selectbox("رقم المنتج No.",  pc, index=pi(["no","رقم","id"]),         key="pno")
            with p2: pnm  = st.selectbox("اسم المنتج",       pc, index=pi(["اسم","name","منتج"]),     key="pnm")
            with p3: ppr  = st.selectbox("السعر الجديد ⭐",  pc, index=pi(["سعر","price"]),            key="ppr")
            with p4: psk  = st.selectbox("رمز SKU",          pc, index=pi(["sku","رمز","barcode"]),   key="psk")
            with p5: pdc  = st.selectbox("السعر المخفض",     pc, index=pi(["مخفض","discount","sale"]),key="pdc")

            if st.button("⚡ بناء ملف تحديث الأسعار", type="primary", key="price_build"):
                rows = []
                for _, row in pdf.iterrows():
                    def gv(c):
                        return str(row.get(c,"") if c != NONE and c in pdf.columns else "")
                    rows.append({
                        "No.":               gv(pno),
                        "النوع ":            "منتج",
                        "أسم المنتج":        gv(pnm),
                        "رمز المنتج sku":    gv(psk),
                        "سعر المنتج":        gv(ppr),
                        "سعر التكلفة":       "",
                        "السعر المخفض":      gv(pdc),
                        "تاريخ بداية التخفيض": "",
                        "تاريخ نهاية التخفيض": "",
                    })
                price_df = pd.DataFrame(rows)
                st.markdown("""<div class="sec-title"><div class="bar"></div>
                <h3>مراجعة وتعديل</h3></div>""", unsafe_allow_html=True)
                edited_p = st.data_editor(price_df, use_container_width=True,
                                           num_rows="dynamic", key="price_editor")

                ex1, ex2 = st.columns(2)
                with ex1:
                    st.download_button("📥 تحديث الأسعار — Excel",
                        export_price_xlsx(edited_p), "price_update.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with ex2:
                    st.download_button("📥 تحديث الأسعار — CSV",
                        export_price_csv(edited_p),
                        "price_update.csv", "text/csv", use_container_width=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 3 — QUICK ADD                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "quickadd":

    st.markdown("""<div class="al-info">
    أضف منتجات جديدة واحداً تلو الآخر. كل ما تحتاجه هو اسم العطر
    — النظام يكمل الماركة والتصنيف والوصف والـ SEO تلقائياً.
    </div>""", unsafe_allow_html=True)

    with st.form("qa_form", clear_on_submit=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            qa_nm = st.text_input("اسم العطر ⭐", placeholder="مثال: شانيل بلو دو شانيل 100 مل للرجال")
            qa_pr = st.text_input("السعر", placeholder="299")
        with f2:
            qa_gn = st.selectbox("الجنس", ["للجنسين","للرجال","للنساء"])
            qa_sk = st.text_input("SKU", placeholder="اختياري")
        with f3:
            qa_sz = st.text_input("الحجم", "100 مل")
            qa_cn = st.selectbox("التركيز", ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"])

        f4, f5, f6, f7 = st.columns(4)
        with f4: qa_tp   = st.selectbox("النوع", ["عطر عادي","تستر"])
        with f5: qa_img  = st.text_input("رابط الصورة (اختياري)")
        with f6: qa_wt   = st.text_input("الوزن (kg)", "0.2")
        with f7: qa_br   = st.text_input("الماركة (اختياري)")

        o1, o2, o3 = st.columns(3)
        with o1: qa_do_d = st.checkbox("🤖 وصف AI",   value=True)
        with o2: qa_do_i = st.checkbox("🖼 جلب صورة", value=False)
        with o3: qa_do_s = st.checkbox("🔍 SEO",       value=True)

        sub = st.form_submit_button("➕ إضافة للقائمة", type="primary",
                                    use_container_width=True)

    if sub and qa_nm.strip():
        with st.spinner("جاري المعالجة..."):
            is_t   = qa_tp == "تستر"
            if qa_br.strip():
                brand = {"name": qa_br.strip(), "page_url": to_slug(qa_br.strip())}
                # Check if new brand
                existing_brands = [b["اسم العلامة التجارية"] for b in st.session_state.new_brands]
                if match_brand(qa_nm).get("name") == "" and qa_br not in existing_brands:
                    st.session_state.new_brands.append({
                        "اسم العلامة التجارية": qa_br.strip(),
                        "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(qa_br.strip()),
                        "وصف العلامة التجارية": "",
                        "صورة العلامة التجارية": "",
                    })
            else:
                brand  = match_brand(qa_nm)
            cat    = match_category(qa_nm, qa_gn)
            seo    = gen_seo(qa_nm, brand, qa_sz, is_t, qa_gn)
            img    = qa_img or (fetch_image(qa_nm, is_t) if qa_do_i else "")
            desc   = ai_generate(qa_nm, is_t, brand, qa_sz, qa_gn, qa_cn) if qa_do_d else ""
            nr     = fill_row(name=qa_nm, price=qa_pr, sku=qa_sk, image=img,
                              desc=desc, brand=brand, category=cat, seo=seo,
                              weight=qa_wt)
            st.session_state.qa_rows.append({
                "product": nr,
                "seo": {"url": seo["url"], "title": seo["title"], "desc": seo["desc"]},
            })
        st.success(f"✅ تمت الإضافة: **{qa_nm}**")

    if st.session_state.qa_rows:
        st.markdown(f"### القائمة ({len(st.session_state.qa_rows)} منتج)")
        prev = []
        for r in st.session_state.qa_rows:
            p = r["product"]
            prev.append({
                "الاسم":    p.get("أسم المنتج",""),
                "الماركة":  p.get("الماركة",""),
                "التصنيف":  p.get("تصنيف المنتج",""),
                "السعر":    p.get("سعر المنتج",""),
                "الوزن":    p.get("الوزن",""),
                "وصف ✓":   "✅" if str(p.get("الوصف","")).strip() else "—",
                "صورة ✓":  "✅" if str(p.get("صورة المنتج","")).startswith("http") else "—",
            })
        st.dataframe(pd.DataFrame(prev), use_container_width=True)

        prod_df_qa = pd.DataFrame([r["product"] for r in st.session_state.qa_rows])
        seo_df_qa  = pd.DataFrame([{
            "No. (غير قابل للتعديل)": "",
            "اسم المنتج (غير قابل للتعديل)": r["product"]["أسم المنتج"],
            "رابط مخصص للمنتج (SEO Page URL)": r["seo"]["url"],
            "عنوان صفحة المنتج (SEO Page Title)": r["seo"]["title"],
            "وصف صفحة المنتج (SEO Page Description)": r["seo"]["desc"],
        } for r in st.session_state.qa_rows])

        qe1, qe2, qe3, qe4, qe5 = st.columns(5)
        with qe1:
            st.download_button("📥 منتجات Excel",
                export_product_xlsx(prod_df_qa), "qa_products.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with qe2:
            st.download_button("📥 منتجات CSV",
                export_product_csv(prod_df_qa), "qa_products.csv", "text/csv",
                use_container_width=True)
        with qe3:
            st.download_button("📥 SEO Excel",
                export_seo_xlsx(seo_df_qa), "qa_seo.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with qe4:
            st.download_button("📥 SEO CSV",
                export_seo_csv(seo_df_qa), "qa_seo.csv", "text/csv",
                use_container_width=True)
        with qe5:
            if st.button("🔀 نقل للمُعالج", use_container_width=True, key="move_qa"):
                ex = st.session_state.up_df
                st.session_state.up_df = pd.concat(
                    [ex, prod_df_qa], ignore_index=True) if ex is not None else prod_df_qa
                st.session_state.up_mapped   = True
                st.session_state.up_filename = "منتجات سريعة"
                st.session_state.qa_rows     = []
                st.session_state.page        = "processor"
                st.rerun()

        if st.button("🗑️ مسح القائمة", key="clear_qa"):
            st.session_state.qa_rows = []
            st.rerun()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 4 — COMPARE & DEDUP (NEW)                                 ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "compare":

    st.markdown("""<div class="al-info">
    ارفع ملف المنتجات الجديدة (المُعالج) وملف المتجر الأساسي. سيقارن النظام المنتجات
    ويستبعد المكرر تلقائياً، ويعرض المنتجات المشبوهة (تشابه 60-99%) لتقرر اعتمادها أو إلغاءها.
    </div>""", unsafe_allow_html=True)

    # ── Upload Section ────────────────────────────────────────────
    st.markdown("""<div class="sec-title"><div class="bar"></div><h3>رفع الملفات</h3></div>""",
                unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**ملف المنتجات الجديدة** (المُعالج من المُعالج الشامل)")
        if st.session_state.cmp_new_df is not None:
            st.markdown(f'<div class="al-ok">محمّل من المُعالج: {len(st.session_state.cmp_new_df)} منتج</div>',
                        unsafe_allow_html=True)
        up_new = st.file_uploader("أو ارفع ملف جديد", type=["csv","xlsx","xls"],
                                   key="cmp_new_up", label_visibility="collapsed")
        if up_new:
            df_new = read_file(up_new)
            if not df_new.empty:
                st.session_state.cmp_new_df = df_new
                st.success(f"✅ {len(df_new)} منتج جديد")

    with col_b:
        st.markdown("**ملف المتجر الأساسي** (متجرنا مهووس بكل الأعمدة)")
        if st.session_state.cmp_store_df is not None:
            st.markdown(f'<div class="al-ok">محمّل: {len(st.session_state.cmp_store_df)} منتج في المتجر</div>',
                        unsafe_allow_html=True)
        up_store = st.file_uploader("ارفع ملف المتجر الأساسي", type=["csv","xlsx","xls"],
                                     key="cmp_store_up", label_visibility="collapsed")
        if up_store:
            df_store = read_file(up_store, salla_2row=True)
            if not df_store.empty:
                st.session_state.cmp_store_df = df_store
                st.success(f"✅ {len(df_store)} منتج في المتجر")

    # ── Column Mapping for Comparison ────────────────────────────
    if st.session_state.cmp_new_df is not None and st.session_state.cmp_store_df is not None:
        new_df   = st.session_state.cmp_new_df
        store_df = st.session_state.cmp_store_df

        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>تعيين أعمدة المقارنة</h3></div>""", unsafe_allow_html=True)

        NONE_C = "— لا يوجد —"
        new_opts   = [NONE_C] + list(new_df.columns)
        store_opts = [NONE_C] + list(store_df.columns)

        def gi2(cols, kws):
            g = auto_guess_col(cols, kws)
            opts = [NONE_C] + list(cols)
            return opts.index(g) if g in opts else 0

        cm1, cm2, cm3, cm4 = st.columns(4)
        with cm1:
            new_name_col = st.selectbox("عمود الاسم (الجديد):", new_opts,
                index=gi2(new_df.columns, ["اسم","name","منتج","عطر"]), key="cmp_nm_new")
        with cm2:
            new_sku_col  = st.selectbox("عمود SKU (الجديد):", new_opts,
                index=gi2(new_df.columns, ["sku","رمز","barcode"]), key="cmp_sk_new")
        with cm3:
            store_name_col = st.selectbox("عمود الاسم (المتجر):", store_opts,
                index=gi2(store_df.columns, ["اسم","name","منتج","عطر"]), key="cmp_nm_st")
        with cm4:
            store_sku_col  = st.selectbox("عمود SKU (المتجر):", store_opts,
                index=gi2(store_df.columns, ["sku","رمز","barcode"]), key="cmp_sk_st")

        sim_threshold = st.slider("حد التشابه للمنتجات المشبوهة (%):", 50, 95, 75, key="sim_thr")

        if st.button("🔍 تشغيل المقارنة الآن", type="primary", key="run_cmp"):
            if new_name_col == NONE_C:
                st.error("حدد عمود اسم المنتج في الملف الجديد")
            elif store_name_col == NONE_C:
                st.error("حدد عمود اسم المنتج في ملف المتجر")
            else:
                with st.spinner("جاري المقارنة..."):
                    # Build store name & SKU sets
                    store_names = [str(v).strip().lower() for v in
                                   store_df[store_name_col].fillna("").tolist() if str(v).strip()]
                    store_skus  = set()
                    if store_sku_col != NONE_C:
                        store_skus = {str(v).strip().lower() for v in
                                      store_df[store_sku_col].fillna("").tolist() if str(v).strip()}

                    results = []
                    for i, row in new_df.iterrows():
                        new_name = str(row.get(new_name_col, "") or "").strip()
                        new_sku  = str(row.get(new_sku_col, "") or "").strip() \
                                   if new_sku_col != NONE_C else ""
                        if not new_name:
                            continue

                        # Check exact SKU match
                        if new_sku and new_sku.lower() in store_skus:
                            results.append({
                                "الاسم الجديد":      new_name,
                                "SKU الجديد":        new_sku,
                                "أقرب تطابق في المتجر": new_name,
                                "نسبة التشابه":      100,
                                "الحالة":            "مكرر (SKU)",
                                "الإجراء":           "حذف",
                                "_idx":              i,
                                "_img":              str(row.get("صورة المنتج","") or ""),
                            })
                            continue

                        # Find best fuzzy match
                        best_score = 0
                        best_match = ""
                        new_lower  = new_name.lower()
                        for sn in store_names:
                            score = _fuzzy_ratio(new_lower, sn)
                            if score > best_score:
                                best_score = score
                                best_match = sn

                        if best_score == 100:
                            status = "مكرر (اسم)"
                            action = "حذف"
                        elif best_score >= sim_threshold:
                            status = "مشبوه"
                            action = "مراجعة"
                        else:
                            status = "جديد"
                            action = "اعتماد"

                        results.append({
                            "الاسم الجديد":      new_name,
                            "SKU الجديد":        new_sku,
                            "أقرب تطابق في المتجر": best_match,
                            "نسبة التشابه":      best_score,
                            "الحالة":            status,
                            "الإجراء":           action,
                            "_idx":              i,
                            "_img":              str(row.get("صورة المنتج","") or ""),
                        })

                    st.session_state.cmp_results  = pd.DataFrame(results)
                    st.session_state.cmp_approved = {
                        r["_idx"]: (r["الإجراء"] == "اعتماد")
                        for r in results
                    }
                st.rerun()

    # ── Show Results ──────────────────────────────────────────────
    if st.session_state.cmp_results is not None:
        res = st.session_state.cmp_results

        exact_dup  = res[res["الحالة"].str.contains("مكرر")]
        suspect    = res[res["الحالة"] == "مشبوه"]
        new_clean  = res[res["الحالة"] == "جديد"]

        st.markdown(f"""
        <div class="stats-bar">
          <div class="stat-box"><div class="n">{len(res)}</div><div class="lb">إجمالي المنتجات</div></div>
          <div class="stat-box"><div class="n" style="color:#e53935">{len(exact_dup)}</div><div class="lb">مكرر (محذوف)</div></div>
          <div class="stat-box"><div class="n" style="color:#f9a825">{len(suspect)}</div><div class="lb">مشبوه (يحتاج مراجعة)</div></div>
          <div class="stat-box"><div class="n" style="color:#43a047">{len(new_clean)}</div><div class="lb">جديد (معتمد)</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── Suspect Products Review ────────────────────────────
        if not suspect.empty:
            st.markdown("""<div class="sec-title"><div class="bar"></div>
            <h3>المنتجات المشبوهة — راجع واعتمد أو ألغِ</h3></div>""",
                        unsafe_allow_html=True)
            st.markdown("""<div class="al-warn">
            هذه المنتجات تشبه منتجات موجودة في المتجر بنسبة عالية.
            راجع كل منتج وقرر: <b>اعتماد</b> (منتج مختلف رغم التشابه) أو <b>إلغاء</b> (مكرر).
            </div>""", unsafe_allow_html=True)

            for _, srow in suspect.iterrows():
                idx  = srow["_idx"]
                img  = srow["_img"]
                pct  = srow["نسبة التشابه"]
                approved = st.session_state.cmp_approved.get(idx, True)

                card_cls = "cmp-card suspect"
                st.markdown(f'<div class="{card_cls}">', unsafe_allow_html=True)

                cc1, cc2, cc3 = st.columns([1, 4, 2])
                with cc1:
                    if img and img.startswith("http"):
                        st.image(img, width=80)
                    else:
                        st.markdown("🖼", unsafe_allow_html=False)
                with cc2:
                    st.markdown(f"""
                    <div style="direction:rtl">
                      <div style="font-weight:800;font-size:0.95rem">{srow['الاسم الجديد']}</div>
                      <div style="color:#888;font-size:0.8rem">أقرب تطابق: {srow['أقرب تطابق في المتجر']}</div>
                      <div class="cmp-pct">{pct}% تشابه</div>
                    </div>
                    """, unsafe_allow_html=True)
                with cc3:
                    col_ap, col_cn = st.columns(2)
                    with col_ap:
                        if st.button("✅ اعتماد", key=f"ap_{idx}",
                                     type="primary" if approved else "secondary"):
                            st.session_state.cmp_approved[idx] = True
                            st.rerun()
                    with col_cn:
                        if st.button("❌ إلغاء", key=f"cn_{idx}",
                                     type="secondary" if approved else "primary"):
                            st.session_state.cmp_approved[idx] = False
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── Exact Duplicates Table ─────────────────────────────
        if not exact_dup.empty:
            with st.expander(f"🔴 المنتجات المكررة ({len(exact_dup)}) — ستُحذف تلقائياً"):
                st.dataframe(exact_dup[["الاسم الجديد","SKU الجديد","أقرب تطابق في المتجر","نسبة التشابه"]],
                             use_container_width=True)

        # ── New Products Table ─────────────────────────────────
        if not new_clean.empty:
            with st.expander(f"🟢 المنتجات الجديدة المعتمدة ({len(new_clean)})"):
                st.dataframe(new_clean[["الاسم الجديد","SKU الجديد","نسبة التشابه"]],
                             use_container_width=True)

        # ── Export Final Approved List ─────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>تصدير القائمة النهائية المعتمدة</h3></div>""", unsafe_allow_html=True)

        if st.button("⚡ بناء الملف النهائي المعتمد", type="primary", key="build_final"):
            new_df_src = st.session_state.cmp_new_df
            approved_idxs = {idx for idx, v in st.session_state.cmp_approved.items() if v}
            # Include all "new" (auto-approved) + manually approved suspects
            final_rows = []
            for _, rrow in res.iterrows():
                idx = rrow["_idx"]
                if rrow["الحالة"] == "جديد" or \
                   (rrow["الحالة"] == "مشبوه" and st.session_state.cmp_approved.get(idx, False)):
                    if new_df_src is not None and idx in new_df_src.index:
                        final_rows.append(new_df_src.loc[idx])

            if final_rows:
                final_df = pd.DataFrame(final_rows)
                # Ensure Salla columns
                for col in SALLA_COLS:
                    if col not in final_df.columns:
                        final_df[col] = ""
                final_df = final_df[[c for c in SALLA_COLS if c in final_df.columns]]

                st.success(f"✅ {len(final_df)} منتج معتمد جاهز للرفع على سلة")
                ex1, ex2 = st.columns(2)
                with ex1:
                    st.download_button("📥 الملف النهائي — Excel",
                        export_product_xlsx(final_df),
                        f"mahwous_final_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True, key="dl_final_x")
                with ex2:
                    st.download_button("📥 الملف النهائي — CSV",
                        export_product_csv(final_df),
                        f"mahwous_final_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        "text/csv", use_container_width=True, key="dl_final_c")

                # Also offer to move back to processor for further editing
                if st.button("🛠️ نقل للمُعالج لمزيد من التحرير", key="cmp_to_proc"):
                    st.session_state.up_df      = final_df
                    st.session_state.up_mapped  = True
                    st.session_state.up_filename = "ملف مُعتمد من المقارنة"
                    st.session_state.page       = "processor"
                    st.rerun()
            else:
                st.warning("لا توجد منتجات معتمدة — راجع قرارات الاعتماد/الإلغاء أعلاه")

        if st.button("🔄 إعادة ضبط المقارنة", key="reset_cmp"):
            st.session_state.cmp_results  = None
            st.session_state.cmp_approved = {}
            st.rerun()

    elif st.session_state.cmp_new_df is None and st.session_state.cmp_store_df is None:
        st.markdown("""
        <div class="upload-zone">
          <div class="uz-icon">🔀</div>
          <div class="uz-title">ارفع ملف المنتجات الجديدة وملف المتجر الأساسي</div>
          <div class="uz-sub">أو انقل الملف مباشرةً من المُعالج الشامل باستخدام زر "نقل للمقارنة"</div>
        </div>
        """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 5 — BRANDS CHECKER                                        ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "brands":

    st.markdown("""<div class="al-info">
    ارفع قائمة ماركات للتحقق منها مقابل قاعدة بيانات مهووس.
    المنتجات التي لا تجد لها ماركة ستُولَّد لها ماركة جديدة بتنسيق سلة.
    </div>""", unsafe_allow_html=True)

    up_b = st.file_uploader("ارفع ملف الماركات أو المنتجات",
                             type=["csv","xlsx","xls"], key="brands_up")
    if up_b:
        bdf_raw = read_file(up_b)
        if not bdf_raw.empty:
            st.success(f"✅ {len(bdf_raw)} صف")
            with st.expander("👀 معاينة"): st.dataframe(bdf_raw.head(8), use_container_width=True)

            NONE_B = "— لا يوجد —"
            bopts  = [NONE_B] + list(bdf_raw.columns)
            def bgi(kws): return bopts.index(auto_guess_col(bdf_raw.columns, kws)) \
                          if auto_guess_col(bdf_raw.columns, kws) in bopts else 0

            b1, b2 = st.columns(2)
            with b1: bcol_name = st.selectbox("عمود اسم الماركة:", bopts,
                                               index=bgi(["ماركة","brand","علامة","اسم"]), key="bcol_nm")
            with b2: bcol_prod = st.selectbox("عمود اسم المنتج (اختياري):", bopts,
                                               index=bgi(["منتج","product","اسم"]), key="bcol_pr")

            gen_missing = st.checkbox("🤖 توليد ماركات جديدة بالذكاء الاصطناعي للماركات الغير موجودة",
                                       value=True, key="gen_miss_b")

            if st.button("🔍 تدقيق الآن", type="primary", key="check_brands"):
                if bcol_name == NONE_B:
                    st.error("حدد عمود اسم الماركة")
                else:
                    results_b = []
                    new_brands_b = []
                    for _, row in bdf_raw.iterrows():
                        bname = str(row.get(bcol_name, "") or "").strip()
                        pname = str(row.get(bcol_prod, "") or "").strip() \
                                if bcol_prod != NONE_B else ""
                        if not bname and not pname:
                            continue
                        search_name = bname or pname
                        found = match_brand(search_name)
                        status = "موجودة ✅" if found.get("name") else "غير موجودة ❌"
                        results_b.append({
                            "الماركة المدخلة":  bname,
                            "المنتج":           pname,
                            "الماركة في قاعدة البيانات": found.get("name","—"),
                            "الرابط":           found.get("page_url",""),
                            "الحالة":           status,
                        })
                        if not found.get("name") and bname:
                            existing_new = [b["اسم العلامة التجارية"] for b in st.session_state.new_brands]
                            if bname not in existing_new and bname not in [x["اسم العلامة التجارية"] for x in new_brands_b]:
                                new_brands_b.append({
                                    "اسم العلامة التجارية": bname,
                                    "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(bname),
                                    "وصف العلامة التجارية": "",
                                    "صورة العلامة التجارية": "",
                                })

                    res_b_df = pd.DataFrame(results_b)
                    st.dataframe(res_b_df, use_container_width=True)

                    found_c   = int((res_b_df["الحالة"] == "موجودة ✅").sum())
                    missing_c = int((res_b_df["الحالة"] == "غير موجودة ❌").sum())
                    st.markdown(f"""
                    <div class="stats-bar">
                      <div class="stat-box"><div class="n" style="color:#43a047">{found_c}</div><div class="lb">موجودة</div></div>
                      <div class="stat-box"><div class="n" style="color:#e53935">{missing_c}</div><div class="lb">غير موجودة</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    if new_brands_b:
                        if gen_missing and st.session_state.api_key:
                            with st.spinner(f"توليد أوصاف {len(new_brands_b)} ماركة جديدة..."):
                                for nb in new_brands_b:
                                    gen = generate_new_brand(nb["اسم العلامة التجارية"])
                                    nb["وصف العلامة التجارية"] = gen["وصف العلامة التجارية"]
                        st.session_state.new_brands.extend(new_brands_b)
                        st.info(f"🆕 {len(new_brands_b)} ماركة جديدة أُضيفت — صدّرها من الإعدادات")

    # Show pending new brands
    if st.session_state.new_brands:
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الماركات الجديدة المُولَّدة</h3></div>""", unsafe_allow_html=True)
        nb_df = pd.DataFrame(st.session_state.new_brands)
        edited_nb = st.data_editor(nb_df, use_container_width=True,
                                    num_rows="dynamic", key="nb_editor")
        st.session_state.new_brands = edited_nb.to_dict("records")

        nb1, nb2, nb3 = st.columns(3)
        with nb1:
            st.download_button("📥 ماركات جديدة — Excel",
                export_brands_xlsx(st.session_state.new_brands),
                "new_brands.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_nb_x")
        with nb2:
            nb_csv_buf = io.StringIO()
            nb_csv_buf.write(",".join(SALLA_BRANDS_COLS) + "\n")
            for nb in st.session_state.new_brands:
                nb_csv_buf.write(",".join([f'"{str(nb.get(c,"") or "")}"'
                                           for c in SALLA_BRANDS_COLS]) + "\n")
            st.download_button("📥 ماركات جديدة — CSV",
                nb_csv_buf.getvalue().encode("utf-8-sig"),
                "new_brands.csv", "text/csv",
                use_container_width=True, key="dl_nb_c")
        with nb3:
            if st.button("🗑️ مسح الماركات الجديدة", key="clear_nb"):
                st.session_state.new_brands = []
                st.rerun()

        # Generate AI descriptions for brands without descriptions
        no_desc_brands = [b for b in st.session_state.new_brands
                          if not str(b.get("وصف العلامة التجارية","")).strip()]
        if no_desc_brands and st.session_state.api_key:
            if st.button(f"🤖 توليد أوصاف {len(no_desc_brands)} ماركة بدون وصف", key="gen_nb_desc"):
                with st.spinner("توليد الأوصاف..."):
                    for nb in st.session_state.new_brands:
                        if not str(nb.get("وصف العلامة التجارية","")).strip():
                            gen = generate_new_brand(nb["اسم العلامة التجارية"])
                            nb["وصف العلامة التجارية"] = gen["وصف العلامة التجارية"]
                st.success("✅ تم توليد الأوصاف")
                st.rerun()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 6 — SETTINGS                                              ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "settings":

    st.markdown("""<div class="sec-title"><div class="bar"></div>
    <h3>مفاتيح API</h3></div>""", unsafe_allow_html=True)

    s1, s2 = st.columns(2)
    with s1:
        new_key = st.text_input("🔑 Anthropic API Key (Claude):",
                                value=st.session_state.api_key,
                                type="password", key="set_api")
        if st.button("💾 حفظ مفتاح Claude", key="save_api"):
            st.session_state.api_key = new_key
            st.success("✅ تم حفظ المفتاح")
    with s2:
        new_gk = st.text_input("🔑 Google API Key:",
                               value=st.session_state.google_api,
                               type="password", key="set_gk")
        new_cx = st.text_input("🔍 Google CSE ID:",
                               value=st.session_state.google_cse,
                               type="password", key="set_cx")
        if st.button("💾 حفظ مفاتيح Google", key="save_gk"):
            st.session_state.google_api = new_gk
            st.session_state.google_cse = new_cx
            st.success("✅ تم حفظ المفاتيح")

    st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
    <h3>قواعد البيانات المرجعية</h3></div>""", unsafe_allow_html=True)

    db1, db2 = st.columns(2)
    with db1:
        st.markdown("**ملف الماركات**")
        bdf = st.session_state.brands_df
        if bdf is not None:
            st.markdown(f'<div class="al-ok">{len(bdf)} ماركة محملة</div>',
                        unsafe_allow_html=True)
            with st.expander("👀 معاينة"): st.dataframe(bdf.head(5), use_container_width=True)
        up_brands = st.file_uploader("تحديث ملف الماركات:", type=["csv","xlsx"],
                                      key="up_brands_db")
        if up_brands:
            df_b = read_file(up_brands)
            if not df_b.empty:
                st.session_state.brands_df = df_b
                os.makedirs(DATA_DIR, exist_ok=True)
                df_b.to_csv(os.path.join(DATA_DIR, "brands.csv"),
                            index=False, encoding="utf-8-sig")
                st.success(f"✅ تم تحديث {len(df_b)} ماركة")
                st.rerun()

    with db2:
        st.markdown("**ملف التصنيفات**")
        cdf = st.session_state.categories_df
        if cdf is not None:
            st.markdown(f'<div class="al-ok">{len(cdf)} تصنيف محمّل</div>',
                        unsafe_allow_html=True)
            with st.expander("👀 معاينة"): st.dataframe(cdf.head(5), use_container_width=True)
        up_cats = st.file_uploader("تحديث ملف التصنيفات:", type=["csv","xlsx"],
                                    key="up_cats_db")
        if up_cats:
            df_c = read_file(up_cats)
            if not df_c.empty:
                st.session_state.categories_df = df_c
                os.makedirs(DATA_DIR, exist_ok=True)
                df_c.to_csv(os.path.join(DATA_DIR, "categories.csv"),
                            index=False, encoding="utf-8-sig")
                st.success(f"✅ تم تحديث {len(df_c)} تصنيف")
                st.rerun()

    # New brands export section
    if st.session_state.new_brands:
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الماركات الجديدة المُولَّدة — جاهزة للتصدير</h3></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="al-warn">{len(st.session_state.new_brands)} ماركة جديدة اكتُشفت خلال المعالجة وتحتاج إلى إضافتها لمتجرك على سلة.</div>',
                    unsafe_allow_html=True)
        nb_df_s = pd.DataFrame(st.session_state.new_brands)
        st.dataframe(nb_df_s, use_container_width=True)
        sn1, sn2 = st.columns(2)
        with sn1:
            st.download_button("📥 تصدير الماركات الجديدة — Excel",
                export_brands_xlsx(st.session_state.new_brands),
                "new_brands_salla.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="exp_nb_set_x")
        with sn2:
            nb_csv_s = io.StringIO()
            nb_csv_s.write(",".join(SALLA_BRANDS_COLS) + "\n")
            for nb in st.session_state.new_brands:
                nb_csv_s.write(",".join([f'"{str(nb.get(c,"") or "")}"'
                                          for c in SALLA_BRANDS_COLS]) + "\n")
            st.download_button("📥 تصدير الماركات الجديدة — CSV",
                nb_csv_s.getvalue().encode("utf-8-sig"),
                "new_brands_salla.csv", "text/csv",
                use_container_width=True, key="exp_nb_set_c")

    st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
    <h3>معلومات النظام</h3></div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="direction:rtl;font-size:0.85rem;line-height:2">
      <b>الإصدار:</b> مهووس مركز التحكم الشامل v4.5<br>
      <b>الموقع:</b> <a href="https://mahwous-automation-production.up.railway.app/" target="_blank">mahwous-automation-production.up.railway.app</a><br>
      <b>أعمدة سلة المنتجات:</b> {len(SALLA_COLS)} عمود<br>
      <b>أعمدة سلة SEO:</b> {len(SALLA_SEO_COLS)} عمود<br>
      <b>أعمدة تحديث الأسعار:</b> {len(SALLA_PRICE_COLS)} عمود<br>
      <b>أعمدة ملف الماركات:</b> {len(SALLA_BRANDS_COLS)} عمود<br>
    </div>
    """, unsafe_allow_html=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝
st.markdown("""
<div class="mhw-footer">
  مهووس — مركز التحكم الشامل v4.5 &nbsp;|&nbsp;
  جميع الملفات المُصدَّرة متوافقة 100% مع منصة سلة &nbsp;|&nbsp;
  <a href="https://mahwous-automation-production.up.railway.app/" target="_blank">mahwous.com</a>
</div>
""", unsafe_allow_html=True)
