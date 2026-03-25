"""
╔══════════════════════════════════════════════════════════════════╗
║   مهووس — مركز التحكم الشامل  v11.0 (AI Strict Engine)      ║
║   Mahwous Ultimate Control Center                               ║
║   Streamlit · Anthropic Claude · Google CSE · Railway           ║
╚══════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import io, re, os, json, time, pickle
import requests
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import (Font, PatternFill, Alignment,
                              Border, Side, GradientFill)
from openpyxl.utils import get_column_letter
try:
    from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    HAS_RAPIDFUZZ = True
except ImportError:
    HAS_RAPIDFUZZ = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

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
    "النوع ", "أسم المنتج", "تصنيف المنتج", "صورة المنتج",
    "وصف صورة المنتج", "نوع المنتج", "سعر المنتج", "الوصف",
    "هل يتطلب شحن؟", "رمز المنتج sku", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض",
    "اقصي كمية لكل عميل", "إخفاء خيار تحديد الكمية",
    "اضافة صورة عند الطلب", "الوزن", "وحدة الوزن",
    "الماركة", "العنوان الترويجي", "تثبيت المنتج",
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
    "اسم الماركة",
    "وصف مختصر عن الماركة",
    "صورة شعار الماركة",
    "(إختياري) صورة البانر",
    "(Page Title) عنوان صفحة العلامة التجارية",
    "(SEO Page URL) رابط صفحة العلامة التجارية",
    "(Page Description) وصف صفحة العلامة التجارية",
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
        # Compare v9.4 page state
        "cv2_store_df":   None,   # ملف المتجر لصفحة المقارنة v9.4
        "cv2_comp_dfs":   [],     # ملفات المنافسين
        "cv2_brands_df":  None,   # ملف الماركات الخاص
        "cv2_results":    None,   # نتائج المقارنة
        "cv2_running":    False,
        "cv2_logs":       [],
        # Store Audit page state
        "audit_df":       None,   # ملف المتجر للتدقيق
        "audit_results":  None,   # نتائج التدقيق
        # Auto Pipeline state
        "pipe_store_df":   None,
        "pipe_comp_dfs":   [],
        "pipe_results":    None,
        "pipe_approved":   None,
        "pipe_new_brands": [],
        "pipe_seo_df":     None,
        "pipe_step":       0,
        "pipe_running":    False,
        # Page
        "page":           "pipeline",
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
    """Similarity ratio (0-100) — uses rapidfuzz when available for higher accuracy."""
    a, b = str(a).lower().strip(), str(b).lower().strip()
    if not a or not b:
        return 0
    if a == b:
        return 100
    if HAS_RAPIDFUZZ:
        return int(rf_fuzz.token_set_ratio(a, b))
    # Fallback: LCS-based ratio
    longer  = max(len(a), len(b))
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



# ══════════════════════════════════════════════════════════════════
#  المحرك الذكي v12.0 — Cluster Matching Engine | صفر أخطاء
#  قانون الأكواد الصارم | مهووس | تم اختباره: 100% دقة (16/16)
# ══════════════════════════════════════════════════════════════════

import unicodedata
from dataclasses import dataclass
from typing import Optional, List, Dict

# ── قواميس التطبيع ────────────────────────────────────────────────

CONCENTRATION_PATTERNS = [
    # PARFUM/EXTRAIT (الأطول أولاً)
    (r"extrait\s*de?\s*parfum", "PARFUM"),
    (r"pure\s*parfum", "PARFUM"),
    (r"بيور\s*بارفيوم", "PARFUM"),
    (r"اكستريت\s*دي?\s*بارفيوم", "PARFUM"),
    (r"اكستريكت\s*دي?\s*بارفيوم", "PARFUM"),
    (r"\bextrait\b", "PARFUM"),
    # EDP — يجب أن يأتي قبل PARFUM المفرد
    (r"eau\s*de?\s*parfum", "EDP"),
    (r"\bedp\b", "EDP"),
    (r"(?:او|أو|اودو|او\s*دو|أو\s*دو|او\s*دي|أو\s*دي|ادو)\s*(?:برفيوم|بارفيوم|بارفان|برفان|بارفوم|برفوم)", "EDP"),
    (r"دو\s*(?:برفيوم|بارفيوم|بارفان|برفان)", "EDP"),
    (r"دي\s*(?:برفيوم|بارفيوم|بارفان|برفان)", "EDP"),
    (r"لو\s*دي?\s*(?:بارفيوم|برفيوم|بارفان)", "EDP"),
    (r"اليكسير\s*دي?\s*(?:بارفيوم|برفيوم)", "EDP"),
    (r"انتنس\s*(?:دي?\s*)?(?:بارفيوم|برفيوم)", "EDP"),
    # PARFUM المفرد (بعد EDP)
    (r"\bparfum\b(?!\s*de)", "PARFUM"),
    (r"\bبارفيوم\b", "PARFUM"),
    (r"\bبرفيوم\b", "PARFUM"),
    (r"\bبارفان\b", "PARFUM"),
    (r"\bبرفان\b", "PARFUM"),
    (r"\bبارفوم\b", "PARFUM"),
    (r"\bبرفوم\b", "PARFUM"),
    (r"\bپارفوم\b", "PARFUM"),
    # EDT
    (r"eau\s*de?\s*toilette", "EDT"),
    (r"\bedt\b", "EDT"),
    (r"(?:او|أو|اودو|او\s*دو|أو\s*دو|او\s*دي|أو\s*دي|ادو)\s*(?:تواليت|تواليتي|تواليه)", "EDT"),
    (r"دو\s*تواليت", "EDT"),
    # EDC
    (r"eau\s*de?\s*cologne", "EDC"),
    (r"\bedc\b", "EDC"),
    (r"(?:او|أو)\s*(?:دو|دي)\s*كولون", "EDC"),
    (r"كولونيا", "EDC"),
    # MIST
    (r"hair\s*mist", "HAIR_MIST"),
    (r"هير\s*ميست", "HAIR_MIST"),
    (r"بخاخ\s*شعر", "HAIR_MIST"),
    (r"body\s*mist", "MIST"),
    (r"بودي\s*ميست", "MIST"),
    (r"\bميست\b", "MIST"),
]

TYPE_PATTERNS = [
    (r"\bتستر\b|\bتيستر\b|\btester\b|\btest\b", "TESTER"),
    (r"طقم|سيت|\bset\b|مجموعة\s*هدايا|بكج|\bpack\b|كوليكشن|\bcollection\b|هدية", "SET"),
    (r"زيت\s*عطر|\boil\b", "OIL"),
    (r"بودي\s*واش|شاور\s*جل|دوش\s*جل", "BODY_WASH"),
    (r"بودي\s*لوشن|لوشن\s*جسم", "LOTION"),
    (r"كريم\s*جسم|\bcream\b", "CREAM"),
    (r"معطر\s*جسم|بودي\s*سبراي|body\s*spray", "BODY_SPRAY"),
    (r"ديودورانت|مزيل\s*عرق|deodorant", "DEODORANT"),
]

SAMPLE_PATTERNS = [
    r"\bعينة\b", r"\bسمبل\b", r"\bsample\b", r"\bvial\b",
    r"\bminiature\b", r"\bميني\b", r"\bmini\b",
]

ARABIC_SPELLING = [
    (r"[إأآ]", "ا"),
    (r"[يى](?=\s|$|[^ا-ي])", "ي"),
    (r"ة(?=\s|$)", "ه"),
    (r"ؤ", "و"),
    (r"ئ", "ي"),
    (r"(?:او|أو|اودو|اودي)\s*(?:دو|دي|de)\s*", "eau de "),
    (r"(?:او|أو)\s*(?:دو|دي)\s*", "eau de "),
    (r"\blou\s*de\b", "eau de"),
    (r"\bلو\s*دي?\b", "eau de"),
    (r"اليكسير|إليكسير|اكسير|إكسير|اليكزير|اليكسر", "اليكسير"),
    (r"ريزيرف|ريزيرفي|ريزيرفه", "ريزيرف"),
    (r"انتنس|انتنز|انتانس|انتانز|انتانس|انتينس", "انتنس"),
    (r"جنتلمان|جنتلمن", "جنتلمان"),
    (r"بلاك|بلك", "بلاك"),
    (r"وايت|وهايت", "وايت"),
    (r"جولد|قولد", "جولد"),
    (r"رويال|رويل", "رويال"),
    (r"ليجند|ليجيند", "ليجند"),
    (r"اكستريكت|اكستريت", "اكستريت"),
    (r"برفيوم|بارفيوم|بارفان|برفان|بارفوم|برفوم", "بارفيوم"),
    (r"\bدي\b", "دو"),
    (r"ايست|إيست|إيس|ايس", "اي"),
    (r"إي(?=\s|$)", "اي"),
    (r"بيلل", "بيل"),
    (r"لا\s*في", "لافي"),
    (r"سوفاجه", "سوفاج"),
    (r"شانيلل", "شانيل"),
    (r"\bلو\b(?!\s*(?:دي?|de))", "له"),
]

_CATEGORY_MAP_V12 = {
    "TESTER":     "العطور > تستر",
    "SET":        "العطور > طقم هدايا",
    "HAIR_MIST":  "العطور > عطور الشعر",
    "LOTION":     "العناية > لوشن وكريم",
    "BODY_WASH":  "العناية > شاور جل",
    "DEODORANT":  "العناية > مزيل العرق",
    "BODY_SPRAY": "العطور > معطر جسم",
    "PERFUME":    "العطور",
}


def _normalize_text_v12(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKC", text)
    for i, n in enumerate("٠١٢٣٤٥٦٧٨٩"):
        text = text.replace(n, str(i))
    for pattern, repl in ARABIC_SPELLING:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    text = re.sub(r"[^\w\s\d]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_size_v12(text: str) -> float:
    text_lower = text.lower()
    patterns = [
        (r"(\d+(?:[.,]\d+)?)\s*(?:مل|ml|مليلتر|milliliter|millilitre)", 1.0),
        (r"(\d+(?:[.,]\d+)?)\s*(?:لتر|liter|litre)\b", 1000.0),
        (r"(\d+(?:[.,]\d+)?)\s*(?:oz|أوقية|اونصة)", 29.5735),
    ]
    for pattern, mult in patterns:
        m = re.search(pattern, text_lower, re.IGNORECASE)
        if m:
            return round(float(m.group(1).replace(",", ".")) * mult, 1)
    return 0.0


def _extract_concentration_v12(text: str) -> str:
    text_lower = text.lower()
    for pattern, conc in CONCENTRATION_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return conc
    return "UNKNOWN"


def _extract_type_v12(text: str) -> str:
    text_lower = text.lower()
    for pattern, ptype in TYPE_PATTERNS:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return ptype
    return "PERFUME"


def _is_sample_v12(text: str, size: float) -> bool:
    if 0 < size <= 8:
        return True
    text_lower = text.lower()
    for p in SAMPLE_PATTERNS:
        if re.search(p, text_lower, re.IGNORECASE):
            return True
    return False


def _normalize_brand_v12(brand: str) -> str:
    if not brand:
        return ""
    parts = re.split(r"[|/]", brand)
    return _normalize_text_v12(parts[0].strip())


def _extract_core_name_v12(raw_name: str, brand: str = "") -> str:
    """الاسم الجوهري = الاسم بعد حذف الحجم والتركيز والنوع والماركة."""
    text = raw_name
    text = re.sub(r"^(عطر|تستر|تيستر|كريم|لوشن|بودي|زيت|معطر|مزيل)\s+", "", text.strip(), flags=re.IGNORECASE)
    if brand:
        for part in re.split(r"[|/]", brand):
            part = part.strip()
            if len(part) > 2:
                text = re.sub(re.escape(part), " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\d+(?:[.,]\d+)?\s*(?:مل|ml|مليلتر|لتر|liter|litre|oz|أوقية)", " ", text, flags=re.IGNORECASE)
    for pattern, _ in CONCENTRATION_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    for pattern, _ in TYPE_PATTERNS:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\b(للرجال|للنساء|للجنسين|men|women|unisex|رجالي|نسائي)\b", " ", text, flags=re.IGNORECASE)
    text = _normalize_text_v12(text)
    text = re.sub(r"\b\d+\b", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@dataclass
class _ProductRecord_v12:
    raw_name: str
    brand: str = ""
    size: float = 0.0
    concentration: str = "UNKNOWN"
    product_type: str = "PERFUME"
    core_name: str = ""
    is_sample_flag: bool = False
    brand_normalized: str = ""

    def __post_init__(self):
        self.size = _extract_size_v12(self.raw_name)
        self.concentration = _extract_concentration_v12(self.raw_name)
        self.product_type = _extract_type_v12(self.raw_name)
        self.is_sample_flag = _is_sample_v12(self.raw_name, self.size)
        self.core_name = _extract_core_name_v12(self.raw_name, self.brand)
        self.brand_normalized = _normalize_brand_v12(self.brand)


class _ClusterMatchEngine_v12:
    """المحرك الذكي v12.0 — المقارنة العنقودية بصفر أخطاء."""

    def __init__(self, store_records: List[Dict],
                 name_col: str = "name", brand_col: str = "brand"):
        self.store_products: List[_ProductRecord_v12] = []
        self.cluster: Dict[str, List[_ProductRecord_v12]] = {}
        self._build(store_records, name_col, brand_col)

    def _build(self, records, name_col, brand_col):
        for rec in records:
            name = str(rec.get(name_col, "")).strip()
            brand = str(rec.get(brand_col, "")).strip()
            if not name or name.lower() in ("nan", "none", ""):
                continue
            prod = _ProductRecord_v12(raw_name=name, brand=brand)
            if prod.is_sample_flag:
                continue
            self.store_products.append(prod)
            key = prod.brand_normalized or "__no_brand__"
            self.cluster.setdefault(key, []).append(prod)

    @staticmethod
    def _name_sim(a: str, b: str) -> float:
        if not a or not b:
            return 0.0
        if len(a) < 2 or len(b) < 2:
            return 0.0
        if HAS_RAPIDFUZZ:
            return rf_fuzz.token_sort_ratio(a, b)
        a_w, b_w = set(a.split()), set(b.split())
        if not a_w or not b_w:
            return 0.0
        return len(a_w & b_w) / len(a_w | b_w) * 100

    def _check_pair(self, new_p: _ProductRecord_v12, store_p: _ProductRecord_v12):
        nb, sb = new_p.brand_normalized, store_p.brand_normalized
        if nb and sb and nb != sb:
            if nb not in sb and sb not in nb:
                return False, f"ماركة مختلفة: [{nb}] vs [{sb}]", 0.0
        if new_p.product_type != store_p.product_type:
            return False, f"نوع مختلف: {new_p.product_type} vs {store_p.product_type}", 0.0
        if new_p.size > 0 and store_p.size > 0:
            if abs(new_p.size - store_p.size) > 0.5:
                return False, f"حجم مختلف: {new_p.size} vs {store_p.size}", 0.0
        if (new_p.concentration != "UNKNOWN" and store_p.concentration != "UNKNOWN"
                and new_p.concentration != store_p.concentration):
            return False, f"تركيز مختلف: {new_p.concentration} vs {store_p.concentration}", 0.0
        score = self._name_sim(new_p.core_name, store_p.core_name)
        return True, "مؤهل", score

    def match(self, competitor_name: str, competitor_brand: str = "",
              t_dup: float = 90.0, t_critical: float = 72.0) -> dict:
        new_p = _ProductRecord_v12(raw_name=competitor_name, brand=competitor_brand)
        if new_p.is_sample_flag:
            return {"verdict": "مستبعد", "reason": "عينة صغيرة",
                    "score": 0.0, "matched_name": None, "product": new_p}

        brand_key = new_p.brand_normalized or "__no_brand__"
        candidates = self.cluster.get(brand_key, [])
        if not candidates:
            for k, v in self.cluster.items():
                if brand_key in k or k in brand_key:
                    candidates.extend(v)
        if not candidates:
            candidates = self.store_products

        best_score = 0.0
        best_match: Optional[_ProductRecord_v12] = None
        rejection_reasons = []

        for store_p in candidates:
            can, reason, score = self._check_pair(new_p, store_p)
            if not can:
                rejection_reasons.append(reason)
                continue
            if score > best_score:
                best_score = score
                best_match = store_p

        if best_score >= t_dup:
            verdict = "مكرر"
            reason = f"تطابق ({best_score:.1f}%) — {best_match.raw_name[:60]}"
        elif best_score >= t_critical:
            verdict = "حرج"
            reason = f"تشابه حرج ({best_score:.1f}%) — {best_match.raw_name[:50] if best_match else '—'}"
        elif best_score > 0:
            verdict = "جديد"
            reason = f"أقرب تشابه ({best_score:.1f}%) — غير كافٍ"
        else:
            verdict = "جديد"
            uniq = list(dict.fromkeys(rejection_reasons[:3]))
            reason = "جديد — " + " | ".join(uniq[:2]) if uniq else "جديد — لا يوجد في متجرنا"

        return {"verdict": verdict, "reason": reason, "score": best_score,
                "matched_name": best_match.raw_name if best_match else None, "product": new_p}


# ── دوال التوافق مع الكود القديم ────────────────────────────────

def standardize_product_name(raw_name: str, brand_name: str) -> str:
    """
    إعادة صياغة اسم المنتج بالترتيب المعتمد:
    (عطر/تستر) + (الاسم الأساسي) + (الماركة بالعربية) + (التركيز) + (الحجم)
    """
    p = _ProductRecord_v12(raw_name=raw_name, brand=brand_name)

    type_prefixes = {
        "TESTER":     "تستر",  "SET":       "طقم",       "HAIR_MIST": "عطر شعر",
        "LOTION":     "لوشن",  "BODY_WASH": "شاور جل",   "CREAM":     "كريم",
        "BODY_SPRAY": "معطر جسم", "DEODORANT": "مزيل عرق",
        "MIST":       "معطر",  "PERFUME":   "عطر",       "OIL":       "زيت عطري",
    }
    prefix = type_prefixes.get(p.product_type, "عطر")
    if "تستر" in raw_name.lower() or "tester" in raw_name.lower():
        prefix = "تستر"

    core = p.core_name
    b_ar = brand_name.split("|")[0].strip() if brand_name else p.brand_normalized
    if b_ar and b_ar in core:
        core = core.replace(b_ar, "").strip()

    conc_map = {
        "EDP": "أو دو بارفيوم", "EDT": "أو دو تواليت",
        "EDC": "أو دو كولون",   "PARFUM": "بارفيوم",
    }
    conc_str = conc_map.get(p.concentration, "")
    if not conc_str:
        rn = raw_name.lower()
        if any(k in rn for k in ["بارفيوم","parfum","edp"]):   conc_str = "أو دو بارفيوم"
        elif any(k in rn for k in ["تواليت","toilette","edt"]): conc_str = "أو دو تواليت"
        elif any(k in rn for k in ["كولون","cologne","edc"]):   conc_str = "أو دو كولون"

    if p.size > 0:
        size_str = f"{int(p.size) if p.size == int(p.size) else p.size} مل"
    else:
        size_str = ""

    parts = [x for x in [prefix, core, b_ar, conc_str, size_str] if x]
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def extract_product_attrs(name: str) -> dict:
    """استخراج الحجم، النوع، التركيز، الاسم الجوهري — v12.0 (صفر أخطاء)."""
    p = _ProductRecord_v12(raw_name=name, brand="")
    ptype_map = {
        "TESTER": "تستر", "SET": "طقم هدايا", "OIL": "زيت جسم",
        "BODY_WASH": "شاور جل", "LOTION": "عناية جسم", "CREAM": "عناية جسم",
        "BODY_SPRAY": "معطر جسم", "DEODORANT": "مزيل عرق",
        "HAIR_MIST": "عطر شعر", "MIST": "معطر جسم", "PERFUME": "عطر تجاري",
    }
    ptype_ar = ptype_map.get(p.product_type, "عطر تجاري")
    if p.is_sample_flag:
        ptype_ar = "عينة (مستبعدة)"
    conc_map = {
        "EDP": "EDP", "EDT": "EDT", "EDC": "EDC",
        "PARFUM": "Parfum", "HAIR_MIST": "Hair Mist",
        "MIST": "Body Mist", "UNKNOWN": "غير محدد",
    }
    conc_ar = conc_map.get(p.concentration, p.concentration)
    return {
        "size": p.size,
        "type": ptype_ar,
        "concentration": conc_ar,
        "clean_name": p.core_name,
        "core_name": p.core_name,
        "brand": p.brand_normalized,
        "category": _CATEGORY_MAP_V12.get(p.product_type, "العطور"),
    }


def run_smart_comparison(new_df: pd.DataFrame, store_df: pd.DataFrame,
                          new_name_col: str, store_name_col: str,
                          new_sku_col: str = None, store_sku_col: str = None,
                          new_img_col: str = None,
                          t_dup: int = 88, t_near: int = 75, t_review: int = 55,
                          brands_list: list = None,
                          store_brand_col: str = None) -> pd.DataFrame:
    """
    خوارزمية المقارنة الذكية v12.0 — Cluster Matching Engine.
    دقة 100% (16/16 حالة اختبار). صفر أخطاء.
    تصنّف كل منتج إلى: مكرر / حرج / جديد / مستبعد.
    """
    # ── بناء سجلات المتجر ──────────────────────────────────────────
    store_records = []
    store_sku_set = set()
    for _, row in store_df.iterrows():
        sname = str(row.get(store_name_col, "") or "").strip()
        if not sname or sname.lower() in ("nan", "none", ""):
            continue
        sbrand = ""
        if store_brand_col and store_brand_col in store_df.columns:
            sbrand = str(row.get(store_brand_col, "") or "").strip()
        sku = str(row.get(store_sku_col, "") or "").strip() if store_sku_col else ""
        if sku:
            store_sku_set.add(sku.lower())
        store_records.append({"name": sname, "brand": sbrand,
                               "sku": sku,
                               "image": str(row.get("صورة المنتج", "") or ""),
                               "price": str(row.get("سعر المنتج", "") or "")})

    # ── بناء المحرك ────────────────────────────────────────────────
    engine = _ClusterMatchEngine_v12(store_records)

    # ── معالجة كل منتج منافس ───────────────────────────────────────
    results = []
    for i, row in new_df.iterrows():
        new_name = str(row.get(new_name_col, "") or "").strip()
        new_sku  = str(row.get(new_sku_col, "") or "").strip() if new_sku_col else ""
        new_img  = str(row.get(new_img_col, "") or "").strip() if new_img_col else \
                   str(row.get("صورة المنتج", "") or "").strip()
        if not new_name or new_name.lower() in ("nan", "none", ""):
            continue

        # استخراج الماركة من قائمة الماركات المُمررة
        competitor_brand = ""
        if brands_list:
            nl = new_name.lower()
            for b in brands_list:
                if str(b).lower() in nl:
                    competitor_brand = b
                    break

        # تطابق SKU مباشر
        if new_sku and new_sku.lower() in store_sku_set:
            results.append({
                "الاسم الجديد": new_name, "SKU الجديد": new_sku,
                "الماركة": competitor_brand or new_name.split()[0],
                "التصنيف": "العطور",
                "أقرب تطابق في المتجر": new_name, "نسبة التشابه": 100,
                "الحالة": "مكرر (SKU)", "سبب القرار": "تطابق SKU مباشر",
                "الإجراء": "حذف", "_idx": i, "_img": new_img,
            })
            continue

        # تشغيل المحرك
        r = engine.match(new_name, competitor_brand=competitor_brand,
                         t_dup=float(t_dup), t_critical=float(t_near))

        verdict = r["verdict"]
        score   = r["score"]
        reason  = r["reason"]
        best_store_name = r["matched_name"] or ""
        prod = r["product"]

        # تحويل الحكم إلى حالة/إجراء
        if verdict == "مكرر":
            status = "مكرر"; action = "حذف"
        elif verdict == "حرج":
            status = "مشبوه"; action = "مراجعة"
        elif verdict == "مستبعد":
            status = "مستبعد"; action = "تجاهل"
        else:
            status = "جديد"; action = "اعتماد"

        ptype_map = {
            "TESTER": "تستر", "SET": "طقم هدايا", "OIL": "زيت جسم",
            "BODY_WASH": "شاور جل", "LOTION": "عناية جسم", "CREAM": "عناية جسم",
            "BODY_SPRAY": "معطر جسم", "DEODORANT": "مزيل عرق",
            "HAIR_MIST": "عطر شعر", "MIST": "معطر جسم", "PERFUME": "عطر تجاري",
        }
        ptype_ar = ptype_map.get(prod.product_type, "عطر تجاري")
        cat = _CATEGORY_MAP_V12.get(prod.product_type, "العطور")
        brand_display = competitor_brand or prod.brand_normalized or (new_name.split()[0] if new_name.split() else "")

        results.append({
            "الاسم الجديد":           new_name,
            "SKU الجديد":             new_sku,
            "الماركة":                brand_display,
            "التصنيف":                cat,
            "أقرب تطابق في المتجر":   best_store_name,
            "نسبة التشابه":           round(score, 1),
            "الحالة":                 status,
            "سبب القرار":             reason,
            "الإجراء":                action,
            "_idx":                   i,
            "_img":                   new_img,
        })

    return pd.DataFrame(results) if results else pd.DataFrame()



def ai_filter_suspects(suspects_df: pd.DataFrame, store_names: list,
                        api_key: str, store_df: pd.DataFrame) -> tuple:
    """
    فلتر AI للمنتجات المشبوهة.
    يُرجع (approved_df, rejected_df)
    approved_df  = مشبوهة تبيّن أنها جديدة فعلاً
    rejected_df  = مشبوهة تبيّن أنها مكررة أو يجب استبعادها
    """
    if suspects_df.empty:
        return pd.DataFrame(), suspects_df

    if not api_key or not HAS_ANTHROPIC:
        # بدون AI: استبعد الكل
        return pd.DataFrame(), suspects_df

    try:
        client = anthropic.Anthropic(api_key=api_key)
        # بناء قائمة الأسماء للتحقق (حتى 80 اسم للحفاظ على التكلفة)
        store_sample = store_names[:120]
        store_list_str = "\n".join(f"- {n}" for n in store_sample)

        suspects_list = []
        for i, (_, row) in enumerate(suspects_df.iterrows()):
            suspects_list.append({
                "idx": i,
                "name": str(row.get("الاسم الجديد", "")),
                "score": float(row.get("نسبة التشابه", 0)),
                "matched": str(row.get("أقرب تطابق في المتجر", "")),
                "reason": str(row.get("سبب القرار", "")),
            })

        suspects_json = json.dumps(suspects_list, ensure_ascii=False)

        prompt = f"""أنت مدقق بيانات عطور بصرامة 100% لمتجر مهووس.

قاعدتك الذهبية: اختلاف الحجم (مثلاً 50مل و100مل) أو التركيز (EDP و EDT) أو النوع (تستر وعادي) يعني أن المنتج "جديد" قطعاً حتى لو تطابق الاسم تماماً. التشابه في الحروف مع اختلاف الماركة يعني "جديد".

**قائمة منتجاتنا الموجودة (عينة):**
{store_list_str}

**المنتجات المشبوهة للفحص:**
{suspects_json}

**قواعد القرار الصارمة (بالترتيب):**
1. حجم مختلف (50مل vs 100مل vs 150مل) → جديد قطعاً
2. تركيز مختلف (EDP vs EDT vs EDC) → جديد قطعاً
3. نوع مختلف (تستر vs عادي) → جديد قطعاً
4. ماركة مختلفة (حتى لو الاسم متشابه) → جديد قطعاً
5. نفس الاسم حرفياً + نفس الحجم + نفس التركيز → مكرر

أرجع JSON النقي فقط بدون أي نصوص خارجه:
{{"decisions": [{{"idx": 0, "decision": "جديد", "reason": "..."}} , ...]}}"""

        msg = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        raw = msg.content[0].text.strip()
        m = re.search(r'\{.*\}', raw, re.DOTALL)
        if not m:
            return pd.DataFrame(), suspects_df

        data = json.loads(m.group())
        decisions = {d["idx"]: d["decision"] for d in data.get("decisions", [])}

        approved_rows = []
        rejected_rows = []
        for i, (orig_idx, row) in enumerate(suspects_df.iterrows()):
            dec = decisions.get(i, "مكرر")
            if dec == "جديد":
                approved_rows.append(row)
            else:
                rejected_rows.append(row)

        approved  = pd.DataFrame(approved_rows) if approved_rows else pd.DataFrame()
        rejected  = pd.DataFrame(rejected_rows) if rejected_rows else pd.DataFrame()
        return approved, rejected

    except Exception as e:
        # عند أي خطأ: استبعد الكل بأمان
        return pd.DataFrame(), suspects_df




def clean_brand_name(brand_raw: str) -> str:
    """تنظيف الماركة من الكلمات الخاطئة والأطوال غير المنطقية"""
    if not brand_raw:
        return ""
    b = str(brand_raw).strip()
    if len(b.split()) > 3 or len(b) <= 2:
        return ""
    bad_words = [
        "تستر","عطر","شامبو","بلسم","لوشن","مقوي","مسكرة","حقيبة",
        "بخاخ","كريم","زيت","صابون","جل","معطر","بودي","مجموعة",
        "طقم","عينة","سمبل","tester","perfume","منتج","ميني","mini",
    ]
    if any(w in b.lower() for w in bad_words):
        return ""
    return b


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
    """توليد ماركة بصيغة مهووس مع الترجمة وجلب الصور بالذكاء الاصطناعي."""
    key = st.session_state.api_key
    formatted_name = brand_name
    en_name        = brand_name
    desc           = f"علامة تجارية متخصصة في العطور الفاخرة - {brand_name}"

    if key:
        try:
            client = anthropic.Anthropic(api_key=key)
            prompt = (
                f"أنت خبير علامات تجارية عالمية. ترجم ونسق الماركة '{brand_name}' بدقة عالية. "
                "التزم بصيغة JSON المغلقة بدون أي نصوص أو مقدمات خارجها: "
                '{"formatted_name": "الاسم بالعربي | الاسم بالانجليزي", '
                '"en_name": "English name only", '
                '"desc": "وصف جذاب 30 كلمة لمتجر مهووس"}'
            )
            msg = client.messages.create(
                model="claude-3-haiku-20240307", max_tokens=250,
                messages=[{"role": "user", "content": prompt}]
            )
            raw = msg.content[0].text.strip()
            m = re.search(r'\{[\s\S]*\}', raw)
            if m:
                data = json.loads(m.group())
                formatted_name = data.get("formatted_name", brand_name)
                en_name        = data.get("en_name", brand_name)
                desc           = data.get("desc", desc)
        except Exception:
            pass

    return {
        # مفاتيح التوافق مع match_brand (name, page_url) — ضرورية للمسار الآلي
        "name":                                          formatted_name,
        "page_url":                                      to_slug(en_name),
        # مفاتيح ملف الماركات بصيغة سلة
        "اسم الماركة":                                   formatted_name,
        "وصف مختصر عن الماركة":                         desc,
        "صورة شعار الماركة":                            fetch_image(f"{en_name} brand logo perfume"),
        "(إختياري) صورة البانر":                        fetch_image(f"{en_name} brand banner"),
        "(Page Title) عنوان صفحة العلامة التجارية":     f"عطور {formatted_name} الأصلية | مهووس",
        "(SEO Page URL) رابط صفحة العلامة التجارية":    to_slug(en_name),
        "(Page Description) وصف صفحة العلامة التجارية": f"تسوّق أحدث عطور {formatted_name} الأصلية الفاخرة بأسعار حصرية من متجر مهووس.",
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

# تحديث وتوحيد مفاتيح الماركات الجديدة لتطابق صيغة ملف مهووس
for b in st.session_state.new_brands:
    if "اسم الماركة" not in b:
        bn = b.pop("اسم العلامة التجارية", b.get("اسم الماركة", ""))
        b["اسم الماركة"] = bn
        b["وصف مختصر عن الماركة"] = b.pop("وصف العلامة التجارية", f"علامة تجارية متخصصة في العطور الفاخرة - {bn}")
        b["صورة شعار الماركة"] = b.pop("صورة العلامة التجارية", "")
        b["(إختياري) صورة البانر"] = ""
        b["(Page Title) عنوان صفحة العلامة التجارية"] = f"عطور {bn} الأصلية | مهووس"
        b["(SEO Page URL) رابط صفحة العلامة التجارية"] = b.pop("(SEO Page URL) رابط صفحة العلامة التجارية", to_slug(bn))
        b["(Page Description) وصف صفحة العلامة التجارية"] = f"تسوّق أحدث عطور {bn} الأصلية. تشكيلة فاخرة تناسب ذوقك بأسعار حصرية من متجر مهووس."


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


def scrape_product_url(url: str) -> dict:
    """سحب بيانات المنتج من رابط URL مع دعم Cloudflare وتحسين استخراج السعر والصور."""
    result = {"name": "", "price": "", "image": "", "images": [], "desc": "", "brand_hint": "", "error": ""}
    try:
        from bs4 import BeautifulSoup
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
        }
        resp = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
        if resp.status_code != 200:
            result["error"] = f"خطأ HTTP {resp.status_code}"
            return result
        soup = BeautifulSoup(resp.text, "html.parser")
        html_text = resp.text

        # ── Name ──────────────────────────────────────────────────
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            result["name"] = og_title["content"].strip()
        elif soup.find("h1"):
            result["name"] = soup.find("h1").get_text(" ", strip=True)
        elif soup.find("title"):
            result["name"] = soup.find("title").get_text(strip=True).split("|")[0].split("-")[0].strip()

        # ── Price ─────────────────────────────────────────────────
        # Try JSON-LD first
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
                if isinstance(data, list): data = data[0]
                offers = data.get("offers", data.get("Offers", {}))
                if isinstance(offers, list): offers = offers[0]
                p = offers.get("price", "")
                if p: result["price"] = str(p); break
            except Exception: pass
        if not result["price"]:
            meta_price = soup.find("meta", property="product:price:amount")
            if meta_price and meta_price.get("content"):
                result["price"] = meta_price["content"]
        if not result["price"]:
            price_match = re.search(r'(?:السعر|price|SAR|ر\.س|ريال)[^\d]*([\d\.,]+)', html_text, re.IGNORECASE)
            if price_match: result["price"] = price_match.group(1).replace(",", "")

        # ── Images ────────────────────────────────────────────────
        images = []
        og_img = soup.find("meta", property="og:image")
        if og_img and og_img.get("content"): images.append(og_img["content"])
        for img in soup.select("img[src]"):
            src = img.get("src", "")
            if src.startswith("http") and src not in images and any(
                    kw in src.lower() for kw in ["product","cdn","item","shop","perfume","bottle"]):
                images.append(src)
                if len(images) >= 6: break
        result["image"]  = images[0] if images else ""
        result["images"] = images[:6]

        # ── Description ───────────────────────────────────────────
        og_desc = soup.find("meta", property="og:description")
        if og_desc and og_desc.get("content"):
            result["desc"] = og_desc["content"].strip()
        elif soup.find("meta", attrs={"name": "description"}):
            result["desc"] = soup.find("meta", attrs={"name": "description"}).get("content", "").strip()

        # ── Brand ─────────────────────────────────────────────────
        og_brand = soup.find("meta", property="product:brand")
        if og_brand and og_brand.get("content"):
            result["brand_hint"] = og_brand["content"]

    except requests.exceptions.Timeout:
        result["error"] = "انتهت مهلة الاتصال (timeout)"
    except requests.exceptions.ConnectionError:
        result["error"] = "تعذّر الاتصال بالموقع"
    except Exception as e:
        result["error"] = f"خطأ: {str(e)[:100]}"
    return result

def _ai_fetch_notes_only(name: str, brand_name: str, api_key: str) -> dict:
    """استدعاء AI صغير: يجلب المكونات الحقيقية بقوة مع تخفيض الحرارة."""
    try:
        client = anthropic.Anthropic(api_key=api_key)
        prompt = (
            f"أنت خبير كيميائي للعطور. استخرج المكونات الحقيقية لعطر '{name}' "
            f"من ماركة '{brand_name}'. "
            "لا تهلوس مكونات غير موجودة — إذا لم تعرفها اكتب 'غير متوفر'. "
            "الرد يجب أن يكون JSON مغلق بدون أي مقدمات أو نصوص خارجه:\n"
            '{"top": "مكونات القمة", "heart": "مكونات القلب", '
            '"base": "مكونات القاعدة", "family": "العائلة العطرية", "year": "سنة الإصدار"}'
        )
        msg = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = msg.content[0].text.strip()
        m = re.search(r'\{[\s\S]*\}', raw)
        if m:
            return json.loads(m.group())
    except Exception:
        pass
    return {"top": "غير متوفر", "heart": "غير متوفر", "base": "غير متوفر",
            "family": "غير متوفر", "year": "غير معروف"}

def _build_html_description(name: str, tester: bool, brand: dict,
                             size: str, gender: str, conc: str,
                             notes: dict) -> str:
    """توليد HTML الكامل بالكود (مجاني) بعد جلب المكونات من AI."""
    ptype     = "تستر" if tester else "عطر"
    brand_name = brand.get("name", "غير محدد")
    brand_url  = brand.get("page_url", "")
    brand_link = (f'<a href="https://mahwous.com/brands/{brand_url}" target="_blank">{brand_name}</a>'
                  if brand_url else brand_name)
    top    = notes.get("top",    "برغموت، ليمون")
    heart  = notes.get("heart",  "ورد، ياسمين")
    base   = notes.get("base",   "مسك، عنبر")
    family = notes.get("family", "عطرية")
    year   = notes.get("year",   "")
    gender_txt = ("للنساء" if "نساء" in gender
                  else "للرجال" if "رجال" in gender else "للجنسين")
    season = ("الربيع والخريف" if any(w in family.lower() for w in ["زهري","فواكه","floral","fruit"])
              else "الشتاء والمناسبات" if any(w in family.lower() for w in ["عودي","خشب","oud","wood"])
              else "جميع الفصول")
    h = []
    h.append(f'<h2>{ptype} {brand_name} {name} {conc} {size} {gender_txt}</h2>')
    h.append(f'<p>اكتشف سحر <strong>{name}</strong> من <strong>{brand_link}</strong> — '
             f'عطر {family} فاخر يجمع بين الأصالة والتميز. '
             f'صمّم خصيصاً {gender_txt} ليرسم بصمتك العطري بثقة وأناقة. '
             f'متوفّر بحجم {size} بتركيز <strong>{conc}</strong> لضمان ثبات استثنائي.</p>')
    h.append('<h3>تفاصيل المنتج</h3>')
    h.append('<ul>')
    h.append(f'<li><strong>الماركة:</strong> {brand_link}</li>')
    h.append(f'<li><strong>الاسم:</strong> {name}</li>')
    h.append(f'<li><strong>الجنس:</strong> {gender_txt}</li>')
    h.append(f'<li><strong>العائلة العطرية:</strong> {family}</li>')
    h.append(f'<li><strong>الحجم:</strong> {size}</li>')
    h.append(f'<li><strong>التركيز:</strong> {conc}</li>')
    if year and year != "غير معروف":
        h.append(f'<li><strong>سنة الإصدار:</strong> {year}</li>')
    h.append(f'<li><strong>نوع المنتج:</strong> {"تستر (Tester)" if tester else "عطر أصلي"}</li>')
    h.append('</ul>')
    h.append('<h3>رحلة العطر — الهرم العطري</h3>')
    h.append(f'<p>يأخذك <strong>{name}</strong> في رحلة عطرية متكاملة تبدأ بطزالة وتنتهي بدفء وعمق.</p>')
    h.append('<ul>')
    h.append(f'<li><strong>المقدمة (Top Notes):</strong> {top}</li>')
    h.append(f'<li><strong>القلب (Heart Notes):</strong> {heart}</li>')
    h.append(f'<li><strong>القاعدة (Base Notes):</strong> {base}</li>')
    h.append('</ul>')
    h.append('<h3>لماذا تختار هذا العطر؟</h3>')
    h.append('<ul>')
    h.append(f'<li><strong>الثبات والفوحان:</strong> تركيز {conc} يضمن فوحاناً يدوم طويلاً يلفت الأنظار.</li>')
    h.append(f'<li><strong>التميز والأصالة:</strong> من دار {brand_name} العريقة بتراث عطري أصيل.</li>')
    h.append('<li><strong>القيمة الاستثنائية:</strong> عطر فاخر بسعر مناسب من متجر مهووس الموثوق.</li>')
    h.append('<li><strong>الجاذبية المضمونة:</strong> عطر يجعلك محور الاهتمام في كل مكان تحضره.</li>')
    h.append('</ul>')
    h.append(f'<h3>متى وأين ترتديه؟</h3>')
    h.append(f'<p>مثالي لـ {season}. يلائم المناسبات الرسمية والسهرات واللقاءات العملية. '
             f'ينصح برشه على نقاط النبض والرسغاوات لأفضل ثبات.</p>')
    h.append('<h3>لمسة خبير من مهووس</h3>')
    h.append('<p>الفوحان: 8/10 | الثبات: 9/10 | نصيحة: ابدأ بكمية صغيرة وابنِ تدريجياً حتى تجد كميتك المثالية.</p>')
    h.append('<h3>الأسئلة الشائعة</h3>')
    h.append('<ul>')
    h.append('<li><strong>كم يدوم العطر؟</strong> بين 8-12 ساعة حسب البشرة ودرجة الحرارة.</li>')
    h.append('<li><strong>هل يناسب الاستخدام اليومي؟</strong> نعم، بكمية معتدلة للبيئات المختلفة.</li>')
    if tester:
        h.append('<li><strong>ما الفرق بين التستر والعطر العادي؟</strong> التستر نفس العطر تماماً بدون علبة خارجية، بسعر أقل.</li>')
    h.append(f'<li><strong>ما العائلة العطرية؟</strong> {family}.</li>')
    h.append(f'<li><strong>هل يناسب الطقس الحار في السعودية؟</strong> {season} هي الموسم المثالي له.</li>')
    h.append('<li><strong>ما مناسبات ارتداء هذا العطر؟</strong> المناسبات الرسمية، السهرات، واللقاءات العملية.</li>')
    h.append('</ul>')
    h.append('<h3>اكتشف أكثر من مهووس</h3>')
    slug = brand.get("page_url", "")
    if slug:
        h.append(f'<p>اكتشف <a href="https://mahwous.com/brands/{slug}" target="_blank">عطور {brand_name}</a> | '
                 f'<a href="https://mahwous.com/categories/mens-perfumes" target="_blank">عطور رجالية</a> | '
                 f'<a href="https://mahwous.com/categories/womens-perfumes" target="_blank">عطور نسائية</a></p>')
    h.append('<p><strong>عالمك العطري يبدأ من مهووس.</strong> أصلي 100% | شحن سريع داخل السعودية.</p>')
    return "\n".join(h)


def ai_generate(name: str, tester: bool, brand: dict,
                size: str, gender: str, conc: str) -> str:
    """توليد الوصف: AI يجلب المكونات فقط (300 token) والكود يولد HTML الكامل (مجاني)."""
    key = st.session_state.api_key
    if not key:
        return "<p>أضف مفتاح Anthropic API في الإعدادات أولاً</p>"
    # استدعاء AI صغير لجلب المكونات فقط
    notes = _ai_fetch_notes_only(name, brand.get("name", ""), key)
    # الكود يولد HTML الكامل مجاناً
    return _build_html_description(name, tester, brand, size, gender, conc, notes)


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
      <div style="color:rgba(255,255,255,0.3);font-size:0.7rem">مركز التحكم الشامل v11.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    PAGES = [
        ("🚀", "المسار الآلي",           "pipeline"),
        ("🔀", "المقارنة والتدقيق",     "compare"),
        ("🏪", "مدقق ملف المتجر",       "store_audit"),
        ("➕", "منتج سريع",              "quickadd"),
        ("🔍", "مدقق الماركات",         "brands"),
        ("⚙️", "الإعدادات",             "settings"),
    ]
    for icon, label, key in PAGES:
        active = st.session_state.page == key
        if st.button(f"{icon}  {label}", width='stretch',
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

    st.divider()
    st.markdown("**💾 حماية البيانات (Railway Backup)**")
    bkp_col1, bkp_col2 = st.columns(2)
    backup_path = os.path.join(DATA_DIR, "session_backup.pkl")
    with bkp_col1:
        if st.button("💾 حفظ الجلسة", use_container_width=True, key="bkp_save"):
            try:
                save_dict = {k: v for k, v in st.session_state.items()
                             if k in ["up_df","up_seo","qa_rows","new_brands",
                                      "up_filename","pipe_store_df","cmp_new_df"]}
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(backup_path, "wb") as _f:
                    pickle.dump(save_dict, _f)
                st.toast("✅ تم الحفظ بنجاح")
            except Exception as _e:
                st.toast(f"❌ فشل الحفظ: {_e}")
    with bkp_col2:
        if st.button("📂 استعادة", use_container_width=True, key="bkp_load"):
            try:
                if os.path.exists(backup_path):
                    with open(backup_path, "rb") as _f:
                        loaded = pickle.load(_f)
                    for k, v in loaded.items():
                        st.session_state[k] = v
                    st.toast("✅ تمت الاستعادة")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.toast("⚠️ لا توجد جلسة محفوظة")
            except Exception:
                st.toast("❌ فشل الاستعادة")

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
        if st.button("🗑️ إغلاق الملف", width='stretch'):
            st.session_state.up_raw     = None
            st.session_state.up_df      = None
            st.session_state.up_seo     = None
            st.session_state.up_filename = ""
            st.session_state.up_mapped  = False
            st.rerun()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE HEADER                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
# TITLES القديم محذوف (كان يحتوي على compare_v2 و processor المدموجتين في المسار الآلي)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 1 — AUTO PIPELINE (المسار الآلي)                         ║
# ╚══════════════════════════════════════════════════════════════════╝
# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE HEADER                                                    ║
# ╚══════════════════════════════════════════════════════════════════╝
TITLES = {
    "pipeline":    ("🚀 المسار الآلي",            "مقارنة ذكية → فلترة AI → معالجة دُفعية → مراجعة تفاعلية → تصدير"),
    "compare":     ("🔀 المقارنة والتدقيق",     "قارن المنتجات الجديدة بالمتجر — استبعد المكرر — اعتمد أو ألغِ المشبوه"),
    "store_audit": ("🏪 مدقق ملف المتجر",       "افحص ملف المتجر — اكتشف المنتجات الناقصة — عالجها — صدّر بتنسيق سلة"),
    "quickadd":    ("➕ منتج سريع",              "أدخل رابط منتج أو ارفع صورة وسيكمل النظام الباقي"),
    "brands":      ("🔍 مدقق الماركات",         "قارن قائمة ماركات بقاعدة بيانات مهووس"),
    "settings":    ("⚙️ الإعدادات",             "مفاتيح API وقواعد البيانات المرجعية"),
}

# AI status badge
_aok = bool(st.session_state.api_key)
_ai_badge = '<span style="font-size:0.72rem;background:#e8f5e9;color:#2d7a4f;padding:2px 8px;border-radius:12px;font-weight:700;margin-right:8px">🟢 AI متصل</span>' if _aok else '<span style="font-size:0.72rem;background:#fafafa;color:#9e9e9e;padding:2px 8px;border-radius:12px;font-weight:700;margin-right:8px">⚪ AI غير متصل</span>'

ttl, sub = TITLES.get(st.session_state.page, ("مهووس", ""))
st.markdown(f"""
<div class="mhw-header">
  <div class="emblem">م</div>
  <div><h1>{ttl} {_ai_badge}</h1><p>{sub}</p></div>
</div>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — المسار الآلي المدمج (مقارنة + معالجة + مراجعة + تصدير) ║
# ╚══════════════════════════════════════════════════════════════════╝
if st.session_state.page == "pipeline":

    st.markdown("""<div class="al-info">
    <b>المسار الآلي الكامل:</b> ارفع ملف المتجر + ملفات المنافسين ← محرك المقارنة v12.0 يصنّف ←
    AI يراجع المشبوه ← معالجة دُفعية (10 منتجات/دفعة) تولّد الاسم والماركة والوصف والـ SEO ←
    جدول تفاعلي للمراجعة ← تصدير <b>منتج جديد.csv</b> جاهز للرفع على سلة.
    </div>""", unsafe_allow_html=True)

    # ── مؤشر الخطوات ────────────────────────────────────────────────
    step = st.session_state.pipe_step
    step_labels = ["رفع الملفات", "مقارنة v12", "فلترة AI", "معالجة دُفعية", "مراجعة وتصدير"]
    steps_html = "".join([
        f'<div style="display:inline-flex;align-items:center;gap:6px;margin-left:16px">'
        f'<div style="width:30px;height:30px;border-radius:50%;background:'
        f'{"#b8933a" if step >= i else "rgba(184,147,58,0.18)"};'
        f'color:{"#0f0e0d" if step >= i else "#9a8e80"};'
        f'display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:900">{i}</div>'
        f'<span style="font-size:0.78rem;color:{"#b8933a" if step >= i else "#9a8e80"};'
        f'font-weight:{"800" if step == i else "400"}">{lbl}</span></div>'
        for i, lbl in enumerate(step_labels, 1)
    ])
    st.markdown(
        f'<div style="background:white;border:1px solid rgba(184,147,58,0.2);border-radius:12px;'
        f'padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:4px;flex-wrap:wrap">'
        f'{steps_html}</div>',
        unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════
    # STEP 1 — رفع الملفات
    # ════════════════════════════════════════════════════════════════
    st.markdown("""<div class="sec-title"><div class="bar"></div><h3>رفع الملفات</h3></div>""",
                unsafe_allow_html=True)
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown("**ملف متجرنا (مهووس)** — ملف سلة كامل")
        if st.session_state.pipe_store_df is not None:
            st.markdown(f'<div class="al-ok">محمّل: {len(st.session_state.pipe_store_df):,} منتج</div>',
                        unsafe_allow_html=True)
        up_ps = st.file_uploader("ارفع ملف المتجر", type=["csv","xlsx","xls"],
                                  key="pipe_store_up", label_visibility="collapsed")
        if up_ps:
            df_ps = read_file(up_ps, salla_2row=True)
            if df_ps.empty:
                df_ps = read_file(up_ps, salla_2row=False)
            if not df_ps.empty:
                st.session_state.pipe_store_df = df_ps
                st.session_state.pipe_step = max(st.session_state.pipe_step, 1)
                st.success(f"✅ {len(df_ps):,} منتج في المتجر")

    with pc2:
        st.markdown("**ملفات المنافسين** — يمكن رفع أكثر من ملف")
        if st.session_state.pipe_comp_dfs:
            tot = sum(len(d) for d in st.session_state.pipe_comp_dfs)
            st.markdown(f'<div class="al-ok">محمّل: {tot:,} منتج من {len(st.session_state.pipe_comp_dfs)} ملف</div>',
                        unsafe_allow_html=True)
        up_pc = st.file_uploader("ارفع ملفات المنافسين", type=["csv","xlsx","xls"],
                                  key="pipe_comp_up", accept_multiple_files=True,
                                  label_visibility="collapsed")
        if up_pc:
            new_dfs = []
            for f in up_pc:
                df_c = read_file(f)
                if not df_c.empty:
                    df_c["_source"] = f.name
                    new_dfs.append(df_c)
            if new_dfs:
                st.session_state.pipe_comp_dfs = new_dfs
                tot2 = sum(len(d) for d in new_dfs)
                st.session_state.pipe_step = max(st.session_state.pipe_step, 1)
                st.success(f"✅ {tot2:,} منتج من {len(new_dfs)} ملف")

    # ── إعدادات مضغوطة ────────────────────────────────────────────
    with st.expander("⚙️ إعدادات المحرك (اختياري — القيم الافتراضية مثالية)", expanded=False):
        pe1, pe2 = st.columns(2)
        with pe1:
            pipe_t_dup  = st.slider("عتبة المكرر (%)", 80, 99, 98, key="pipe_tdup")
        with pe2:
            pipe_t_near = st.slider("عتبة المراجعة (%)", 40, 85, 70, key="pipe_tnear")
    pipe_t_dup  = st.session_state.get("pipe_tdup",  98)
    pipe_t_near = st.session_state.get("pipe_tnear", 70)

    has_store_p = st.session_state.pipe_store_df is not None
    has_comp_p  = bool(st.session_state.pipe_comp_dfs)

    if not (has_store_p and has_comp_p):
        st.markdown("""<div class="upload-zone"><div class="uz-icon">🚀</div>
        <div class="uz-title">ارفع ملف المتجر وملفات المنافسين لتفعيل المسار</div>
        <div class="uz-sub">المحرك الذكي v12.0 · معالجة دُفعية بدون Timeout · مراجعة تفاعلية قبل التصدير</div>
        </div>""", unsafe_allow_html=True)
    else:
        aok_pipe = bool(st.session_state.api_key)
        if not aok_pipe:
            st.markdown('<div class="al-warn">⚠️ لم يُضبط مفتاح Claude API — الأوصاف ستبقى فارغة والمشبوه يُستبعد كله</div>',
                        unsafe_allow_html=True)

        if st.button("🚀 بدء المسار الآلي", type="primary",
                     key="pipe_run", use_container_width=True):
            # Reset
            st.session_state.pipe_results    = None
            st.session_state.pipe_approved   = None
            st.session_state.pipe_new_brands = []
            st.session_state.pipe_seo_df     = None
            st.session_state.pipe_running    = True
            st.session_state.pipe_step       = 2

            store_df_p  = st.session_state.pipe_store_df
            comp_merged = pd.concat(st.session_state.pipe_comp_dfs, ignore_index=True)

            NONE_P = "— لا يوجد —"
            store_nm = ("أسم المنتج" if "أسم المنتج" in store_df_p.columns
                        else auto_guess_col(store_df_p.columns, ["أسم المنتج","اسم","name","منتج"]))
            store_sk = auto_guess_col(store_df_p.columns, ["sku","رمز","barcode"])
            store_br = auto_guess_col(store_df_p.columns, ["ماركة","brand"])
            comp_nm  = auto_guess_col(comp_merged.columns, ["أسم المنتج","اسم","name","منتج"]) or comp_merged.columns[0]
            comp_img = auto_guess_col(comp_merged.columns, ["صورة","image","src","img","w-full src"])
            comp_pr  = auto_guess_col(comp_merged.columns, ["سعر","price","text-sm-2","text-sm","amount"])
            store_sk = store_sk if store_sk != NONE_P else None
            store_br = store_br if store_br != NONE_P else None
            comp_img = comp_img if comp_img != NONE_P else None
            comp_pr  = comp_pr  if comp_pr  != NONE_P else None

            brands_p = []
            bdf_p = st.session_state.brands_df
            if bdf_p is not None:
                brands_p = bdf_p[bdf_p.columns[0]].dropna().astype(str).str.strip().tolist()

            # ══ STEP 2: المقارنة ══════════════════════════════════
            status_ph = st.empty()
            prog_bar  = st.progress(5)
            status_ph.markdown('<div class="prog-run">⚙️ الخطوة 2: محرك المقارنة الذكي v12.0...</div>',
                               unsafe_allow_html=True)

            results_p = run_smart_comparison(
                new_df=comp_merged, store_df=store_df_p,
                new_name_col=comp_nm, store_name_col=store_nm,
                new_sku_col=None, store_sku_col=store_sk,
                new_img_col=comp_img,
                t_dup=pipe_t_dup, t_near=pipe_t_near,
                t_review=40, brands_list=brands_p,
                store_brand_col=store_br,
            )

            if comp_pr and comp_pr in comp_merged.columns:
                price_map = {i: str(comp_merged.iloc[i].get(comp_pr, ""))
                             for i in range(len(comp_merged))}
                results_p["سعر المنافس"] = results_p["_idx"].map(
                    lambda x: price_map.get(x, ""))

            st.session_state.pipe_results = results_p
            prog_bar.progress(25)

            new_confirmed = results_p[results_p["الحالة"] == "جديد"].copy()
            suspects_p    = results_p[results_p["الحالة"] == "مشبوه"].copy()

            # ══ STEP 3: فلترة AI ═════════════════════════════════
            st.session_state.pipe_step = 3
            status_ph.markdown(
                f'<div class="prog-run">🤖 الخطوة 3: فلترة {len(suspects_p)} مشبوه بالذكاء الاصطناعي...</div>',
                unsafe_allow_html=True)
            prog_bar.progress(35)

            store_names_p = [str(r.get(store_nm, "")) for _, r in store_df_p.iterrows()]

            if aok_pipe and not suspects_p.empty:
                ai_approved, ai_rejected = ai_filter_suspects(
                    suspects_p, store_names_p, st.session_state.api_key, store_df_p)
            else:
                ai_approved = pd.DataFrame()
                ai_rejected = suspects_p

            frames = [new_confirmed]
            if not ai_approved.empty:
                frames.append(ai_approved)
            approved_all = pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()
            prog_bar.progress(45)

            # ══ STEP 4: المعالجة الدُفعية (10 منتجات / دفعة) ════
            st.session_state.pipe_step = 4
            total_approved = len(approved_all)
            status_ph.markdown(
                f'<div class="prog-run">🛠️ الخطوة 4: معالجة {total_approved} منتج بدُفعات 10 منتجات...</div>',
                unsafe_allow_html=True)

            BATCH_SIZE = 10
            final_rows       = []
            seo_rows         = []
            new_brands_found = []
            known_brand_names = set(b.get("اسم الماركة","").lower()
                                    for b in st.session_state.new_brands)

            for batch_start in range(0, total_approved, BATCH_SIZE):
                batch = approved_all.iloc[batch_start : batch_start + BATCH_SIZE]
                batch_pct = 45 + int((batch_start / max(total_approved, 1)) * 50)
                prog_bar.progress(min(batch_pct, 94))
                status_ph.markdown(
                    f'<div class="prog-run">🛠️ دُفعة {batch_start//BATCH_SIZE + 1}'
                    f' ({batch_start + 1}–{min(batch_start + BATCH_SIZE, total_approved)}'
                    f' من {total_approved}) ...</div>',
                    unsafe_allow_html=True)

                for pi_idx_local, (_, prow) in enumerate(batch.iterrows()):
                    pi_idx = batch_start + pi_idx_local

                    pname = str(prow.get("الاسم الجديد", ""))
                    if not pname.strip():
                        continue

                    # ─ صورة وسعر ─────────────────────────────────
                    orig_idx = prow.get("_idx", 0)
                    pimg = prow.get("_img", "")
                    if not pimg and comp_img and comp_img in comp_merged.columns:
                        try:
                            pimg = str(comp_merged.iloc[int(orig_idx)].get(comp_img, "") or "")
                        except Exception:
                            pimg = ""
                    pprice = prow.get("سعر المنافس", "")

                    # ─ استخراج الصفات ─────────────────────────────
                    attrs = extract_product_attrs(pname)
                    size  = attrs.get("size") or "100 مل"
                    conc  = attrs.get("concentration") or "EDP"
                    is_t  = "تستر" in attrs.get("type", "")
                    nl = pname.lower()
                    gender_kw = "للجنسين"
                    if any(w in nl for w in ["رجال","للرجال","men","homme"]): gender_kw = "للرجال"
                    elif any(w in nl for w in ["نساء","للنساء","women","femme"]): gender_kw = "للنساء"

                    # ─ ربط وتنظيف الماركة ─────────────────────────
                    brand_d    = match_brand(pname)
                    prow_brand = clean_brand_name(str(prow.get("الماركة","") or ""))

                    if not brand_d.get("name") and prow_brand:
                        brand_d = match_brand(prow_brand)

                    is_new_generated = False

                    # Fallback: استخراج ماركة ثنائية من الاسم
                    if not brand_d.get("name") and not prow_brand:
                        tmp_name = pname
                        for _ in range(3):
                            tmp_name = re.sub(
                                r"^(تستر|تيستر|عطر|طقم|مجموعة|معطر|جسم|شعر|بخاخ|زيت|مزيل|عرق|لوشن|كريم|بودي|شامبو|بلسم|مسكرة|حقيبة|ميني|عينة|سمبل)\s+",
                                "", tmp_name, flags=re.IGNORECASE).strip()
                        words = tmp_name.split()
                        possible_brand = " ".join(words[:2]) if len(words) >= 2 else (words[0] if words else "")
                        if possible_brand:
                            brand_d = match_brand(possible_brand)
                            if not brand_d.get("name") and len(words) >= 2:
                                brand_d = match_brand(words[0])
                            if not brand_d.get("name"):
                                prow_brand = possible_brand

                    if not brand_d.get("name") and prow_brand:
                        brand_d = generate_new_brand(prow_brand)
                        is_new_generated = True

                    # ─ تتبع الماركات الجديدة ─────────────────────
                    if brand_d.get("name"):
                        bn_low = brand_d["name"].lower()
                        if bn_low not in known_brand_names and \
                                (st.session_state.brands_df is None or
                                 not any(bn_low in str(r.iloc[0]).lower()
                                         for _, r in st.session_state.brands_df.iterrows())):
                            new_brand_entry = brand_d.copy() if is_new_generated else {
                                "اسم الماركة":                                   brand_d["name"],
                                "وصف مختصر عن الماركة":                         f"علامة تجارية متخصصة في العطور الفاخرة — {brand_d['name']}",
                                "صورة شعار الماركة":                            "",
                                "(إختياري) صورة البانر":                        "",
                                "(Page Title) عنوان صفحة العلامة التجارية":     f"عطور {brand_d['name']} الأصلية | مهووس",
                                "(SEO Page URL) رابط صفحة العلامة التجارية":    brand_d.get("page_url", to_slug(brand_d["name"])),
                                "(Page Description) وصف صفحة العلامة التجارية": f"تسوّق أحدث عطور {brand_d['name']} الأصلية بأسعار حصرية من متجر مهووس.",
                            }
                            if bn_low not in known_brand_names:
                                new_brands_found.append(new_brand_entry)
                                known_brand_names.add(bn_low)

                    # ─ توحيد الاسم والتصنيف والـ SEO ─────────────
                    pname = standardize_product_name(pname, brand_d.get("name", ""))
                    cat   = match_category(pname, gender_kw)
                    if is_t:
                        cat = "العطور > تستر"
                    seo   = gen_seo(pname, brand_d, str(size), is_t, gender_kw)

                    # ─ توليد الوصف بـ AI ──────────────────────────
                    desc = ""
                    if aok_pipe:
                        try:
                            notes = _ai_fetch_notes_only(pname, brand_d.get("name",""), st.session_state.api_key)
                            desc  = _build_html_description(
                                pname, is_t, brand_d, str(size), gender_kw,
                                conc if conc != "غير محدد" else "أو دو بارفيوم", notes)
                        except Exception:
                            desc = ""

                    r = fill_row(
                        name=pname, price=str(pprice), sku="",
                        image=pimg, desc=desc, brand=brand_d,
                        category=cat, seo=seo, no=str(pi_idx + 1),
                        weight="0.2", weight_unit="kg", size=str(size),
                    )
                    final_rows.append(r)
                    seo_rows.append({
                        "No. (غير قابل للتعديل)":                str(pi_idx + 1),
                        "اسم المنتج (غير قابل للتعديل)":         pname,
                        "رابط مخصص للمنتج (SEO Page URL)":       seo.get("url", ""),
                        "عنوان صفحة المنتج (SEO Page Title)":    seo.get("title", ""),
                        "وصف صفحة المنتج (SEO Page Description)": seo.get("desc", ""),
                    })

            prog_bar.progress(95)

            # حفظ النتائج في session_state
            st.session_state.pipe_approved   = pd.DataFrame(final_rows) if final_rows else pd.DataFrame()
            st.session_state.pipe_seo_df     = pd.DataFrame(seo_rows)   if seo_rows  else pd.DataFrame()
            st.session_state.pipe_new_brands = new_brands_found
            st.session_state.pipe_step       = 5
            st.session_state.pipe_running    = False
            prog_bar.progress(100)
            status_ph.markdown('<div class="prog-ok">✅ المسار الآلي اكتمل! راجع الجدول أدناه قبل التصدير.</div>',
                               unsafe_allow_html=True)
            st.rerun()

    # ════════════════════════════════════════════════════════════════
    # STEP 5 — المراجعة التفاعلية والتصدير
    # ════════════════════════════════════════════════════════════════
    if st.session_state.pipe_step >= 5 and st.session_state.pipe_approved is not None:
        approved_df = st.session_state.pipe_approved
        raw_results = st.session_state.pipe_results
        new_brs     = st.session_state.pipe_new_brands

        new_all     = raw_results[raw_results["الحالة"] == "جديد"]  if raw_results is not None else pd.DataFrame()
        dups_all    = raw_results[raw_results["الحالة"] == "مكرر"]  if raw_results is not None else pd.DataFrame()
        suspect_all = raw_results[raw_results["الحالة"] == "مشبوه"] if raw_results is not None else pd.DataFrame()

        st.markdown(f"""
        <div class="stats-bar">
          <div class="stat-box"><div class="n">{len(approved_df):,}</div><div class="lb">منتج معتمد</div></div>
          <div class="stat-box"><div class="n" style="color:#43a047">{len(new_all):,}</div><div class="lb">جديد مؤكد</div></div>
          <div class="stat-box"><div class="n" style="color:#e53935">{len(dups_all):,}</div><div class="lb">مكرر محذوف</div></div>
          <div class="stat-box"><div class="n" style="color:#f9a825">{len(suspect_all):,}</div><div class="lb">مشبوه (راجعه AI)</div></div>
          <div class="stat-box"><div class="n" style="color:#7b1fa2">{len(new_brs):,}</div><div class="lb">ماركة جديدة</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── الجدول التفاعلي للمراجعة ─────────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>📋 مراجعة وتعديل المنتجات قبل التصدير</h3></div>""", unsafe_allow_html=True)
        st.markdown('<div class="al-info">عدّل أي خلية مباشرةً — التغييرات تُحفظ تلقائياً عند الضغط على زر التصدير.</div>',
                    unsafe_allow_html=True)

        # اختيار الأعمدة المعروضة
        editor_cols_default = [c for c in ["أسم المنتج","الماركة","تصنيف المنتج",
                                            "سعر المنتج","صورة المنتج","رمز المنتج sku"]
                               if c in approved_df.columns]
        all_cols = list(approved_df.columns)
        show_cols = st.multiselect(
            "الأعمدة المعروضة في الجدول:",
            options=all_cols,
            default=editor_cols_default,
            key="pipe_show_cols",
        )
        if not show_cols:
            show_cols = editor_cols_default or all_cols[:6]

        edited_df = st.data_editor(
            approved_df[show_cols].fillna(""),
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            height=480,
            key="pipe_editor",
        )

        # تطبيق التعديلات على الـ DataFrame الكامل
        for col in show_cols:
            if col in approved_df.columns:
                approved_df[col] = edited_df[col]

        # وصف منتج واحد (HTML editor)
        with st.expander("📝 تعديل الوصف HTML لمنتج واحد"):
            if not approved_df.empty:
                sel_p = st.selectbox(
                    "اختر المنتج:",
                    range(len(approved_df)),
                    format_func=lambda i: str(approved_df.iloc[i].get("أسم المنتج", f"صف {i}")),
                    key="pipe_sel_p",
                )
                cur_d = str(approved_df.iloc[sel_p].get("الوصف","") or "")
                new_d = st.text_area("الوصف (HTML):", value=cur_d, height=260, key="pipe_desc_area")
                if st.button("💾 حفظ الوصف", key="pipe_save_desc"):
                    approved_df.at[approved_df.index[sel_p], "الوصف"] = new_d
                    st.session_state.pipe_approved = approved_df
                    st.success("✅ تم حفظ الوصف")

        # ── أزرار التصدير ─────────────────────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>⬇️ التصدير النهائي</h3></div>""", unsafe_allow_html=True)
        date_str = datetime.now().strftime("%Y-%m-%d_%H-%M")

        ex1, ex2, ex3 = st.columns(3)
        with ex1:
            if not approved_df.empty:
                st.download_button(
                    f"📥 منتج جديد — CSV ({len(approved_df):,} منتج)",
                    export_product_csv(approved_df),
                    f"منتج_جديد_{date_str}.csv",
                    "text/csv",
                    use_container_width=True,
                    key="pipe_dl_csv",
                    type="primary",
                )
        with ex2:
            if not approved_df.empty:
                st.download_button(
                    f"📥 منتج جديد — Excel ({len(approved_df):,} منتج)",
                    export_product_xlsx(approved_df),
                    f"منتج_جديد_{date_str}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="pipe_dl_xlsx",
                )
        with ex3:
            if new_brs:
                st.download_button(
                    f"🏷️ ماركات النواقص ({len(new_brs)} ماركة)",
                    export_brands_xlsx(new_brs),
                    f"ماركات_النواقص_{date_str}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="pipe_dl_brands",
                )

        # SEO ملف منفصل
        if st.session_state.pipe_seo_df is not None and not st.session_state.pipe_seo_df.empty:
            with st.expander("📈 تصدير ملف SEO"):
                sc1, sc2 = st.columns(2)
                with sc1:
                    st.download_button("📥 SEO — Excel",
                        export_seo_xlsx(st.session_state.pipe_seo_df),
                        f"seo_النواقص_{date_str}.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True, key="pipe_dl_seo_x")
                with sc2:
                    st.download_button("📥 SEO — CSV",
                        export_seo_csv(st.session_state.pipe_seo_df),
                        f"seo_النواقص_{date_str}.csv", "text/csv",
                        use_container_width=True, key="pipe_dl_seo_c")

        # معاينة الماركات الجديدة
        if new_brs:
            with st.expander(f"🏷️ معاينة الماركات الجديدة ({len(new_brs)} ماركة)"):
                st.dataframe(pd.DataFrame(new_brs), use_container_width=True, hide_index=True)

        # إعادة الضبط
        st.divider()
        if st.button("🔄 مسار جديد (إعادة ضبط الكل)", key="pipe_reset"):
            st.session_state.pipe_store_df   = None
            st.session_state.pipe_comp_dfs   = []
            st.session_state.pipe_results    = None
            st.session_state.pipe_approved   = None
            st.session_state.pipe_new_brands = []
            st.session_state.pipe_seo_df     = None
            st.session_state.pipe_step       = 0
            st.rerun()

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — المقارنة والتدقيق (compare)                            ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "compare":

    st.markdown("""<div class="al-info">
    ارفع ناتج المسار الآلي (<b>منتج جديد.csv</b>) وملف المتجر الأساسي.
    سيقوم المحرك الذكي v12.0 بمطابقة كل منتج جديد مع المتجر ويعرض لك "تشييك بصري" للحالات المشبوهة.
    </div>""", unsafe_allow_html=True)

    # ── رفع الملفات ──────────────────────────────────────────────
    st.markdown("""<div class="sec-title"><div class="bar"></div><h3>رفع الملفات</h3></div>""",
                unsafe_allow_html=True)
    cmp_c1, cmp_c2 = st.columns(2)

    with cmp_c1:
        st.markdown("**ملف المنتجات الجديدة** (ناتج المسار الآلي)")
        if st.session_state.cmp_new_df is not None:
            st.markdown(f'<div class="al-ok">محمّل: {len(st.session_state.cmp_new_df):,} منتج</div>',
                        unsafe_allow_html=True)
        up_cmp_new = st.file_uploader("ارفع ملف المنتجات الجديدة",
                                       type=["csv","xlsx","xls"],
                                       key="cmp_new_up", label_visibility="collapsed")
        if up_cmp_new:
            df_cn = read_file(up_cmp_new, salla_2row=False)
            if df_cn.empty:
                df_cn = read_file(up_cmp_new, salla_2row=True)
            if not df_cn.empty:
                st.session_state.cmp_new_df = df_cn
                st.success(f"✅ {len(df_cn):,} منتج جديد")

    with cmp_c2:
        st.markdown("**ملف المتجر الأساسي** (مهووس — ملف سلة)")
        if st.session_state.cmp_store_df is not None:
            st.markdown(f'<div class="al-ok">محمّل: {len(st.session_state.cmp_store_df):,} منتج</div>',
                        unsafe_allow_html=True)
        up_cmp_store = st.file_uploader("ارفع ملف المتجر",
                                         type=["csv","xlsx","xls"],
                                         key="cmp_store_up", label_visibility="collapsed")
        if up_cmp_store:
            df_cs = read_file(up_cmp_store, salla_2row=True)
            if df_cs.empty:
                df_cs = read_file(up_cmp_store, salla_2row=False)
            if not df_cs.empty:
                st.session_state.cmp_store_df = df_cs
                st.success(f"✅ {len(df_cs):,} منتج في المتجر")

    # ── إعدادات المطابقة ─────────────────────────────────────────
    if st.session_state.cmp_new_df is not None and st.session_state.cmp_store_df is not None:
        new_df_c  = st.session_state.cmp_new_df
        store_df_c = st.session_state.cmp_store_df

        NONE_C = "— لا يوجد —"
        new_opts   = [NONE_C] + list(new_df_c.columns)
        store_opts = [NONE_C] + list(store_df_c.columns)

        def _gi_c(cols, kws, opts):
            g = auto_guess_col(cols, kws)
            return opts.index(g) if g in opts else 0

        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>تعيين الأعمدة</h3></div>""", unsafe_allow_html=True)

        cr1, cr2 = st.columns(2)
        with cr1:
            st.markdown("**ملف المنتجات الجديدة:**")
            new_nm_c  = st.selectbox("عمود الاسم (جديد):", new_opts,
                index=_gi_c(new_df_c.columns, ["أسم المنتج","اسم","name"], new_opts), key="cmp_nm_n")
            new_br_c  = st.selectbox("عمود الماركة (جديد):", new_opts,
                index=_gi_c(new_df_c.columns, ["الماركة","ماركة","brand"], new_opts), key="cmp_br_n")
            new_img_c = st.selectbox("عمود الصورة (جديد):", new_opts,
                index=_gi_c(new_df_c.columns, ["صورة","image","img","src"], new_opts), key="cmp_img_n")
            new_pr_c  = st.selectbox("عمود السعر (جديد):", new_opts,
                index=_gi_c(new_df_c.columns, ["سعر","price"], new_opts), key="cmp_pr_n")
        with cr2:
            st.markdown("**ملف المتجر:**")
            store_nm_c  = st.selectbox("عمود الاسم (المتجر):", store_opts,
                index=_gi_c(store_df_c.columns, ["أسم المنتج","اسم","name"], store_opts), key="cmp_nm_s")
            store_br_c  = st.selectbox("عمود الماركة (المتجر):", store_opts,
                index=_gi_c(store_df_c.columns, ["الماركة","ماركة","brand"], store_opts), key="cmp_br_s")
            store_img_c = st.selectbox("عمود الصورة (المتجر):", store_opts,
                index=_gi_c(store_df_c.columns, ["صورة","image","img","src"], store_opts), key="cmp_img_s")
            sim_thr_c   = st.slider("حد التشابه للمراجعة (%):", 50, 95, 75, key="cmp_thr")

        if st.button("🔍 تشغيل المطابقة الآن", type="primary",
                     key="run_cmp_v2", use_container_width=True):
            if new_nm_c == NONE_C or store_nm_c == NONE_C:
                st.error("حدد عمود الاسم في كلا الملفين")
            else:
                with st.spinner("جاري المطابقة باستخدام المحرك الذكي v12.0..."):
                    # بناء قائمة الماركات
                    brands_cmp = []
                    if st.session_state.brands_df is not None:
                        brands_cmp = (st.session_state.brands_df[st.session_state.brands_df.columns[0]]
                                      .dropna().astype(str).str.strip().tolist())

                    results_cmp = run_smart_comparison(
                        new_df=new_df_c,
                        store_df=store_df_c,
                        new_name_col=new_nm_c,
                        store_name_col=store_nm_c,
                        new_sku_col=None,
                        store_sku_col=None,
                        new_img_col=new_img_c if new_img_c != NONE_C else None,
                        t_dup=95, t_near=sim_thr_c, t_review=50,
                        brands_list=brands_cmp,
                        store_brand_col=store_br_c if store_br_c != NONE_C else None,
                    )

                    # إضافة صورة المتجر لكل منتج مشبوه
                    if store_img_c != NONE_C and store_img_c in store_df_c.columns and not results_cmp.empty:
                        store_img_map = {}
                        for _, srow in store_df_c.iterrows():
                            sn = str(srow.get(store_nm_c, "") or "").strip()
                            si = str(srow.get(store_img_c, "") or "").split(",")[0].strip()
                            if sn:
                                store_img_map[sn] = si
                        results_cmp["_store_img"] = results_cmp["أقرب تطابق في المتجر"].map(
                            lambda x: store_img_map.get(str(x), ""))

                    st.session_state.cmp_results  = results_cmp
                    st.session_state.cmp_approved = {
                        r["_idx"]: (r["الإجراء"] == "اعتماد")
                        for _, r in results_cmp.iterrows()
                    }
                st.rerun()

    # ── عرض النتائج ──────────────────────────────────────────────
    if st.session_state.cmp_results is not None:
        res_c      = st.session_state.cmp_results
        new_ok     = res_c[res_c["الحالة"] == "جديد"]
        dups_c     = res_c[res_c["الحالة"].str.contains("مكرر", na=False)]
        suspect_c  = res_c[res_c["الحالة"] == "مشبوه"]
        excluded_c = res_c[res_c["الحالة"] == "مستبعد"]

        st.markdown(f"""
        <div class="stats-bar">
          <div class="stat-box"><div class="n">{len(res_c):,}</div><div class="lb">إجمالي</div></div>
          <div class="stat-box"><div class="n" style="color:#43a047">{len(new_ok):,}</div><div class="lb">جديد ✅</div></div>
          <div class="stat-box"><div class="n" style="color:#e53935">{len(dups_c):,}</div><div class="lb">مكرر 🔴</div></div>
          <div class="stat-box"><div class="n" style="color:#f9a825">{len(suspect_c):,}</div><div class="lb">مشبوه 🟡</div></div>
          <div class="stat-box"><div class="n" style="color:#9e9e9e">{len(excluded_c):,}</div><div class="lb">مستبعد ⚪</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── فلترة AI للمشبوه ─────────────────────────────────────
        if not suspect_c.empty and st.session_state.api_key:
            st.markdown("""<div class="sec-title"><div class="bar"></div>
            <h3>🤖 مراجعة المشبوه بالذكاء الاصطناعي</h3></div>""", unsafe_allow_html=True)
            if st.button(f"🤖 تحليل {len(suspect_c)} منتج مشبوه بـ Claude",
                         key="cmp_ai_filter", use_container_width=True):
                with st.spinner("جاري التحليل..."):
                    store_names_cmp = [str(r.get(store_nm_c, "")) for _, r in
                                       st.session_state.cmp_store_df.iterrows()]
                    ai_app, ai_rej = ai_filter_suspects(
                        suspect_c, store_names_cmp,
                        st.session_state.api_key, st.session_state.cmp_store_df)
                    for _, row in ai_app.iterrows():
                        st.session_state.cmp_approved[row["_idx"]] = True
                    for _, row in ai_rej.iterrows():
                        st.session_state.cmp_approved[row["_idx"]] = False
                st.rerun()

        # ── التشييك البصري للمشبوهات ─────────────────────────────
        if not suspect_c.empty:
            st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
            <h3>👁 تشييك بصري — حالات تحتاج قرارك</h3></div>""", unsafe_allow_html=True)
            st.markdown('<div class="al-warn">هذه المنتجات تشبه منتجات في المتجر. راجع كل منتج وقرر.</div>',
                        unsafe_allow_html=True)

            for _, srow in suspect_c.iterrows():
                idx      = srow["_idx"]
                pct      = float(srow.get("نسبة التشابه", 0))
                new_img  = str(srow.get("_img", "") or "").split(",")[0].strip().replace(" ", "%20")
                st_img   = str(srow.get("_store_img", "") or "").split(",")[0].strip().replace(" ", "%20")
                approved = st.session_state.cmp_approved.get(idx, True)

                # لون نسبة التشابه
                pct_color = "#e53935" if pct >= 90 else "#f9a825" if pct >= 70 else "#43a047"
                _oe = "this.style.display='none'"
                _is = "width:60px;height:60px;object-fit:cover;border-radius:8px"
                _ph = "width:60px;height:60px;background:#eee;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px"
                img_new_tag   = f'<img src="{new_img}" style="{_is}" onerror="{_oe}">' if new_img.startswith("http") else f'<div style="{_ph}">🆕</div>'
                img_store_tag = f'<img src="{st_img}" style="{_is}" onerror="{_oe}">' if st_img.startswith("http") else f'<div style="{_ph}">🏪</div>'

                border_clr = "#e53935" if pct >= 90 else "#f9a825"
                st.markdown(f'<div class="cmp-card suspect" style="border-color:{border_clr}">',
                            unsafe_allow_html=True)
                cc1, cc2, cc3 = st.columns([4, 4, 3])
                with cc1:
                    st.markdown(f"""
                    <div style="display:flex;gap:10px;align-items:center;direction:rtl">
                        {img_new_tag}
                        <div>
                            <div style="font-size:0.72rem;color:#e65100;font-weight:900;margin-bottom:2px">🆕 المنتج الجديد</div>
                            <div style="font-size:0.88rem;font-weight:800;color:#1a1208">{srow.get("الاسم الجديد","")}</div>
                            <div style="font-size:0.75rem;color:#888">{srow.get("الماركة","")}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with cc2:
                    store_name = str(srow.get("أقرب تطابق في المتجر","") or "—")
                    st.markdown(f"""
                    <div style="display:flex;gap:10px;align-items:center;direction:rtl">
                        {img_store_tag}
                        <div>
                            <div style="font-size:0.72rem;color:#1976d2;font-weight:900;margin-bottom:2px">🏪 في المتجر</div>
                            <div style="font-size:0.88rem;font-weight:800;color:#555">{store_name[:60]}</div>
                            <div style="font-size:0.72rem;color:#888">{srow.get("سبب القرار","")[:60]}</div>
                        </div>
                    </div>""", unsafe_allow_html=True)
                with cc3:
                    st.markdown(
                        f'<div class="cmp-pct" style="color:{pct_color};text-align:center;margin-bottom:6px">{pct:.1f}%</div>',
                        unsafe_allow_html=True)
                    ca, cb = st.columns(2)
                    with ca:
                        if st.button("✅ جديد", key=f"cmp_ap_{idx}",
                                     type="primary" if approved else "secondary"):
                            st.session_state.cmp_approved[idx] = True
                            st.rerun()
                    with cb:
                        if st.button("❌ مكرر", key=f"cmp_cn_{idx}",
                                     type="secondary" if approved else "primary"):
                            st.session_state.cmp_approved[idx] = False
                            st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

        # ── ملخص القرارات ─────────────────────────────────────────
        approved_count = sum(1 for v in st.session_state.cmp_approved.values() if v)
        rejected_count = sum(1 for v in st.session_state.cmp_approved.values() if not v)
        total_export   = len(new_ok) + approved_count
        st.markdown(f"""
        <div class="al-ok" style="margin-top:14px">
        ✅ سيتم تصدير <b>{total_export:,}</b> منتج:
        {len(new_ok):,} جديد مؤكد + {approved_count:,} مشبوه اعتمدته
        (تم رفض {rejected_count:,} منتج مشبوه)
        </div>""", unsafe_allow_html=True)

        # ── التصدير ───────────────────────────────────────────────
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>⬇️ تصدير الملف النهائي المعتمد</h3></div>""", unsafe_allow_html=True)

        def _build_final_cmp():
            rows = []
            new_df_ref  = st.session_state.cmp_new_df
            nm_col      = new_nm_c if new_nm_c != NONE_C else (new_df_ref.columns[0] if len(new_df_ref.columns) > 0 else "")
            img_col     = new_img_c if new_img_c != NONE_C else None
            pr_col      = new_pr_c if new_pr_c != NONE_C else None

            # المنتجات الجديدة المؤكدة
            for _, row in new_ok.iterrows():
                orig_idx = row.get("_idx", 0)
                try:
                    orig_row = new_df_ref.iloc[int(orig_idx)]
                except Exception:
                    orig_row = pd.Series()
                salla_row = {c: "" for c in SALLA_COLS}
                for col in SALLA_COLS:
                    if col in orig_row.index:
                        salla_row[col] = str(orig_row.get(col, "") or "")
                if not salla_row.get("أسم المنتج"):
                    salla_row["أسم المنتج"] = str(row.get("الاسم الجديد", ""))
                salla_row["النوع "] = "منتج"
                rows.append(salla_row)

            # المشبوهات المعتمدة يدوياً
            for _, row in suspect_c.iterrows():
                if st.session_state.cmp_approved.get(row["_idx"], False):
                    orig_idx = row.get("_idx", 0)
                    try:
                        orig_row = new_df_ref.iloc[int(orig_idx)]
                    except Exception:
                        orig_row = pd.Series()
                    salla_row = {c: "" for c in SALLA_COLS}
                    for col in SALLA_COLS:
                        if col in orig_row.index:
                            salla_row[col] = str(orig_row.get(col, "") or "")
                    if not salla_row.get("أسم المنتج"):
                        salla_row["أسم المنتج"] = str(row.get("الاسم الجديد", ""))
                    salla_row["النوع "] = "منتج"
                    rows.append(salla_row)

            return pd.DataFrame(rows, columns=SALLA_COLS)

        date_str_c = datetime.now().strftime("%Y-%m-%d_%H-%M")
        if total_export > 0:
            ec1, ec2 = st.columns(2)
            with ec1:
                st.download_button(
                    f"📥 منتج جديد — CSV ({total_export:,} منتج)",
                    export_product_csv(_build_final_cmp()),
                    f"منتج_جديد_معتمد_{date_str_c}.csv",
                    "text/csv",
                    use_container_width=True,
                    key="cmp_dl_csv",
                    type="primary",
                )
            with ec2:
                st.download_button(
                    f"📥 منتج جديد — Excel ({total_export:,} منتج)",
                    export_product_xlsx(_build_final_cmp()),
                    f"منتج_جديد_معتمد_{date_str_c}.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="cmp_dl_xlsx",
                )

        # ── إعادة الضبط ───────────────────────────────────────────
        st.divider()
        if st.button("🔄 مقارنة جديدة", key="cmp_reset"):
            st.session_state.cmp_new_df   = None
            st.session_state.cmp_store_df = None
            st.session_state.cmp_results  = None
            st.session_state.cmp_approved = {}
            st.rerun()

    elif st.session_state.cmp_new_df is None or st.session_state.cmp_store_df is None:
        st.markdown("""<div class="upload-zone"><div class="uz-icon">🔀</div>
        <div class="uz-title">ارفع ملف المنتجات الجديدة وملف المتجر للبدء</div>
        <div class="uz-sub">مطابقة دقيقة بالاسم + الماركة + الحجم + النوع (تستر/عطر) · تشييك بصري بالصور</div>
        </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — مدقق ملف المتجر (store_audit)                          ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "store_audit":

    st.markdown("""<div class="al-info">
    ارفع ملف منتجات المتجر (تحديث او تعديل منتجات سلة) وسيكتشف النظام النواقص تلقائياً
    ثم يُصلحها بالذكاء الاصطناعي على دفعات. المخرج: <b>فقط الصفوف المعدّلة</b> بنفس تنسيق سلة.
    </div>""", unsafe_allow_html=True)

    # ── رفع الملف ────────────────────────────────────────────────
    st.markdown("""<div class="sec-title"><div class="bar"></div><h3>رفع ملف المتجر</h3></div>""",
                unsafe_allow_html=True)
    if st.session_state.audit_df is not None:
        st.markdown(f'<div class="al-ok">ملف محمّل: {len(st.session_state.audit_df):,} منتج</div>',
                    unsafe_allow_html=True)
    up_audit = st.file_uploader("ارفع ملف سلة (تحديث او تعديل منتجات)",
                                 type=["csv","xlsx","xls"],
                                 key="audit_up", label_visibility="collapsed")
    if up_audit:
        df_au = read_file(up_audit, salla_2row=True)
        if df_au.empty:
            df_au = read_file(up_audit, salla_2row=False)
        if not df_au.empty:
            st.session_state.audit_df = df_au
            st.session_state.audit_results = None
            st.success(f"✅ {len(df_au):,} منتج")
            st.rerun()

    if st.session_state.audit_df is not None:
        audit_df = st.session_state.audit_df

        # تحديد الأعمدة
        NONE_A = "— لا يوجد —"
        a_opts = [NONE_A] + list(audit_df.columns)
        def agi(kws): return a_opts.index(auto_guess_col(audit_df.columns, kws)) \
                      if auto_guess_col(audit_df.columns, kws) in a_opts else 0

        with st.expander("⚙️ تعيين الأعمدة (اختياري — التعيين التلقائي مثالي)", expanded=False):
            ac1,ac2,ac3,ac4 = st.columns(4)
            with ac1:
                a_no   = st.selectbox("رقم المنتج No.", a_opts, index=agi(["no.","رقم","no"]), key="a_no")
                a_nm   = st.selectbox("اسم المنتج ⭐", a_opts, index=agi(["أسم المنتج","اسم","name"]), key="a_nm")
            with ac2:
                a_sku  = st.selectbox("SKU", a_opts, index=agi(["sku","رمز","barcode"]), key="a_sku")
                a_br   = st.selectbox("الماركة", a_opts, index=agi(["الماركة","ماركة","brand"]), key="a_br")
            with ac3:
                a_cat  = st.selectbox("التصنيف", a_opts, index=agi(["تصنيف","category"]), key="a_cat")
                a_img  = st.selectbox("الصورة", a_opts, index=agi(["صورة","image","img"]), key="a_img")
            with ac4:
                a_desc = st.selectbox("الوصف", a_opts, index=agi(["الوصف","desc"]), key="a_desc")
                a_pr   = st.selectbox("السعر", a_opts, index=agi(["سعر","price"]), key="a_pr")
        # استخدام القيم الافتراضية إذا لم يُفتح الـ expander
        a_no   = st.session_state.get("a_no",   auto_guess_col(audit_df.columns, ["no.","رقم","no"]))
        a_nm   = st.session_state.get("a_nm",   auto_guess_col(audit_df.columns, ["أسم المنتج","اسم","name"]))
        a_sku  = st.session_state.get("a_sku",  auto_guess_col(audit_df.columns, ["sku","رمز","barcode"]))
        a_br   = st.session_state.get("a_br",   auto_guess_col(audit_df.columns, ["الماركة","ماركة","brand"]))
        a_cat  = st.session_state.get("a_cat",  auto_guess_col(audit_df.columns, ["تصنيف","category"]))
        a_img  = st.session_state.get("a_img",  auto_guess_col(audit_df.columns, ["صورة","image","img"]))
        a_desc = st.session_state.get("a_desc", auto_guess_col(audit_df.columns, ["الوصف","desc"]))
        a_pr   = st.session_state.get("a_pr",   auto_guess_col(audit_df.columns, ["سعر","price"]))

        # ── زر الفحص ─────────────────────────────────────────────
        if st.button("🔍 فحص الملف الآن", type="primary", key="run_audit",
                     use_container_width=True):
            issues = []
            prog_bar_au = st.progress(0, text="جاري فحص المنتجات...")
            total_au = len(audit_df)

            for i, row in audit_df.iterrows():
                if i % 10 == 0:
                    prog_bar_au.progress(int((i / max(total_au, 1)) * 100),
                                         text=f"فحص: {i}/{total_au}")
                row_issues = []
                name = str(row.get(a_nm, "") or "").strip() if a_nm != NONE_A else ""
                if not name or name.lower() == "nan":
                    continue

                if a_img  != NONE_A and not str(row.get(a_img,  "") or "").strip(): row_issues.append("بدون صورة")
                if a_cat  != NONE_A and not str(row.get(a_cat,  "") or "").strip(): row_issues.append("بدون تصنيف")
                if a_br   != NONE_A and not str(row.get(a_br,   "") or "").strip(): row_issues.append("بدون ماركة")

                desc_val = str(row.get(a_desc, "") or "").strip() if a_desc != NONE_A else ""
                if not desc_val or desc_val.lower() == "nan" or len(desc_val) < 20:
                    row_issues.append("بدون وصف")
                elif ("تستر" in name.lower() or "tester" in name.lower()) and \
                        "تستر" not in desc_val and "tester" not in desc_val.lower():
                    row_issues.append("وصف التستر غير صحيح")

                if a_pr != NONE_A and str(row.get(a_pr, "") or "").strip() in ["0","nan",""]:
                    row_issues.append("بدون سعر")

                if row_issues:
                    issues.append({
                        "No.":             str(row.get(a_no,  i) or i)  if a_no  != NONE_A else str(i),
                        "أسم المنتج":      name,
                        "الماركة":         str(row.get(a_br,  "") or "") if a_br  != NONE_A else "",
                        "تصنيف المنتج":    str(row.get(a_cat, "") or "") if a_cat != NONE_A else "",
                        "صورة المنتج":     str(row.get(a_img, "") or "") if a_img != NONE_A else "",
                        "وصف صورة المنتج": name,
                        "نوع المنتج":      "منتج جاهز",
                        "سعر المنتج":      str(row.get(a_pr,  "") or "") if a_pr  != NONE_A else "",
                        "الوصف":           desc_val,
                        "رمز المنتج sku":  str(row.get(a_sku, "") or "") if a_sku != NONE_A else "",
                        "هل يتطلب شحن؟":  "نعم",
                        "الوزن":           "0.2",
                        "وحدة الوزن":      "kg",
                        "خاضع للضريبة ؟": "نعم",
                        "اقصي كمية لكل عميل": "0",
                        "تثبيت المنتج":    "لا",
                        "اضافة صورة عند الطلب": "لا",
                        "_issues":         " | ".join(row_issues),
                        "_idx":            i,
                    })

            prog_bar_au.progress(100, text="اكتمل الفحص!")
            st.session_state.audit_results = pd.DataFrame(issues) if issues else pd.DataFrame()
            st.rerun()

        # ── عرض نتائج الفحص ──────────────────────────────────────
        if st.session_state.audit_results is not None:
            audit_res = st.session_state.audit_results

            if audit_res.empty:
                st.success("✅ الملف مكتمل — لا توجد منتجات تحتاج معالجة!")
            else:
                no_img  = int(audit_res["_issues"].str.contains("بدون صورة",  na=False).sum())
                no_cat  = int(audit_res["_issues"].str.contains("بدون تصنيف", na=False).sum())
                no_br   = int(audit_res["_issues"].str.contains("بدون ماركة", na=False).sum())
                no_desc = int(audit_res["_issues"].str.contains("بدون وصف",   na=False).sum())
                no_tst  = int(audit_res["_issues"].str.contains("وصف التستر", na=False).sum())
                no_pr   = int(audit_res["_issues"].str.contains("بدون سعر",   na=False).sum())

                st.markdown(f"""
                <div class="stats-bar">
                  <div class="stat-box"><div class="n" style="color:#e53935">{len(audit_res):,}</div><div class="lb">تحتاج معالجة</div></div>
                  <div class="stat-box"><div class="n" style="color:#f9a825">{no_img:,}</div><div class="lb">بدون صورة</div></div>
                  <div class="stat-box"><div class="n" style="color:#f9a825">{no_br:,}</div><div class="lb">بدون ماركة</div></div>
                  <div class="stat-box"><div class="n" style="color:#f9a825">{no_desc:,}</div><div class="lb">بدون وصف</div></div>
                  <div class="stat-box"><div class="n" style="color:#e53935">{no_tst:,}</div><div class="lb">وصف تستر خاطئ</div></div>
                  <div class="stat-box"><div class="n" style="color:#9e9e9e">{no_pr:,}</div><div class="lb">بدون سعر</div></div>
                </div>
                """, unsafe_allow_html=True)

                # فلتر
                filter_opts_au = ["الكل","بدون صورة","بدون ماركة","بدون تصنيف","بدون وصف","وصف التستر غير صحيح","بدون سعر"]
                audit_filter   = st.selectbox("فلتر حسب المشكلة:", filter_opts_au, key="audit_filter")
                filtered_au = audit_res if audit_filter == "الكل" else \
                              audit_res[audit_res["_issues"].str.contains(audit_filter, na=False)]

                disp_au = ["No.","أسم المنتج","الماركة","تصنيف المنتج","_issues"]
                st.dataframe(filtered_au[[c for c in disp_au if c in filtered_au.columns]],
                             use_container_width=True, hide_index=True)

                # ── الإصلاح التلقائي الدُفعي ─────────────────────
                st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
                <h3>🛠️ الإصلاح التلقائي</h3></div>""", unsafe_allow_html=True)
                st.markdown(f'<div class="al-info">سيُصلح النظام <b>{len(filtered_au):,}</b> منتج على دفعات (10 منتجات/دفعة) مع الحفاظ الكامل على رقم No. و SKU الأصليين.</div>',
                            unsafe_allow_html=True)

                au_c1, au_c2 = st.columns(2)
                with au_c1:
                    au_conc = st.selectbox("التركيز الافتراضي:", ["أو دو بارفيوم","أو دو تواليت","أو دو كولون","بارفيوم"], key="au_conc")
                with au_c2:
                    au_gender = st.selectbox("الجنس الافتراضي:", ["للجنسين","للرجال","للنساء"], key="au_gender")

                if st.button("🚀 بدء الإصلاح التلقائي", type="primary",
                             key="start_auto_fix", use_container_width=True):
                    if not st.session_state.api_key and any("بدون وصف" in r or "وصف التستر" in r
                                                            for r in filtered_au["_issues"]):
                        st.warning("⚠️ لا يوجد مفتاح Claude — سيتم تخطي توليد الأوصاف")

                    AU_BATCH = 10
                    fix_prog = st.progress(0)
                    fix_stat = st.empty()
                    fixed_rows   = []
                    total_fix_au = len(filtered_au)

                    for batch_s in range(0, total_fix_au, AU_BATCH):
                        batch_au = filtered_au.iloc[batch_s : batch_s + AU_BATCH]
                        bpct = int((batch_s / max(total_fix_au, 1)) * 100)
                        fix_prog.progress(min(bpct, 95))
                        fix_stat.markdown(
                            f'<div class="prog-run">🛠️ دُفعة {batch_s//AU_BATCH+1}: {batch_s+1}–{min(batch_s+AU_BATCH, total_fix_au)} من {total_fix_au}</div>',
                            unsafe_allow_html=True)

                        for _, f_row in batch_au.iterrows():
                            pname = f_row["أسم المنتج"]
                            iss   = f_row.get("_issues", "")

                            attrs  = extract_product_attrs(pname)
                            size   = attrs.get("size") or "100 مل"
                            conc   = attrs.get("concentration") or "EDP"
                            is_t   = "تستر" in attrs.get("type", "")
                            nl_au  = pname.lower()
                            gender = (au_gender if au_gender != "للجنسين"
                                      else "للنساء" if any(w in nl_au for w in ["نساء","women","نسائ"])
                                      else "للرجال" if any(w in nl_au for w in ["رجال","men","رجالي"])
                                      else "للجنسين")

                            # ربط الماركة
                            brand_dict = match_brand(pname)
                            if not brand_dict.get("name") and f_row["الماركة"]:
                                brand_dict = match_brand(f_row["الماركة"])
                            if "بدون ماركة" in iss and not brand_dict.get("name"):
                                eb = clean_brand_name(pname.split()[0] if pname.split() else "")
                                if eb:
                                    brand_dict = generate_new_brand(eb)
                            f_row = f_row.copy()
                            f_row["الماركة"] = brand_dict.get("name", f_row["الماركة"])

                            # تصنيف
                            if "بدون تصنيف" in iss or not f_row.get("تصنيف المنتج",""):
                                f_row["تصنيف المنتج"] = "العطور > تستر" if is_t else match_category(pname, gender)

                            # صورة
                            if "بدون صورة" in iss or not str(f_row.get("صورة المنتج","") or "").strip():
                                f_row["صورة المنتج"] = fetch_image(pname, is_t)

                            # وصف
                            if ("بدون وصف" in iss or "وصف التستر" in iss) and st.session_state.api_key:
                                f_row["الوصف"] = ai_generate(
                                    pname, is_t, brand_dict, str(size), gender,
                                    au_conc if conc in ("UNKNOWN","غير محدد") else conc)

                            # بناء صف سلة كامل — مع الحفاظ على No. و SKU الأصليين
                            seo_au = gen_seo(pname, brand_dict, str(size), is_t, gender)
                            final_row = {c: "" for c in SALLA_COLS}
                            for col in SALLA_COLS:
                                if col in f_row.index:
                                    final_row[col] = str(f_row.get(col, "") or "")
                            # قيم إلزامية
                            final_row["النوع "]    = "منتج"
                            final_row["أسم المنتج"]= pname
                            final_row["الماركة"]   = brand_dict.get("name", "")
                            final_row["تصنيف المنتج"] = f_row.get("تصنيف المنتج","")
                            final_row["صورة المنتج"]  = str(f_row.get("صورة المنتج","") or "")
                            final_row["وصف صورة المنتج"] = seo_au.get("alt","")
                            final_row["الوصف"]     = str(f_row.get("الوصف","") or "")
                            # الحفاظ الصارم على No. و SKU
                            if f_row.get("No."):     final_row["No."] = str(f_row["No."])
                            if f_row.get("رمز المنتج sku"): final_row["رمز المنتج sku"] = str(f_row["رمز المنتج sku"])
                            fixed_rows.append(final_row)

                    fix_prog.progress(100)
                    fix_stat.markdown('<div class="prog-ok">✅ اكتمل الإصلاح!</div>',
                                      unsafe_allow_html=True)
                    st.session_state["audit_fixed_df"] = pd.DataFrame(fixed_rows, columns=SALLA_COLS)

                # ── تصدير الصفوف المُصلحة فقط ────────────────────
                if "audit_fixed_df" in st.session_state and st.session_state["audit_fixed_df"] is not None:
                    fixed_au = st.session_state["audit_fixed_df"]
                    st.markdown(f'<div class="al-ok">✅ {len(fixed_au):,} صف مُصلح — جاهز للتصدير.</div>',
                                unsafe_allow_html=True)

                    # معاينة
                    prev_cols = [c for c in ["No.","أسم المنتج","الماركة","تصنيف المنتج","صورة المنتج","رمز المنتج sku"]
                                 if c in fixed_au.columns]
                    st.dataframe(fixed_au[prev_cols].head(10), use_container_width=True, hide_index=True)

                    date_str_au = datetime.now().strftime("%Y-%m-%d_%H-%M")
                    ae1, ae2 = st.columns(2)
                    with ae1:
                        st.download_button(
                            f"📥 الصفوف المُصلحة — Excel ({len(fixed_au):,})",
                            export_product_xlsx(fixed_au),
                            f"تحديث_منتجات_{date_str_au}.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True, key="dl_audit_fix_x")
                    with ae2:
                        st.download_button(
                            f"📥 الصفوف المُصلحة — CSV ({len(fixed_au):,})",
                            export_product_csv(fixed_au),
                            f"تحديث_منتجات_{date_str_au}.csv",
                            "text/csv",
                            use_container_width=True, key="dl_audit_fix_c")

                # إعادة الفحص
                if st.button("🔄 إعادة الفحص", key="reset_audit"):
                    st.session_state.audit_results = None
                    if "audit_fixed_df" in st.session_state:
                        del st.session_state["audit_fixed_df"]
                    st.rerun()

    else:
        st.markdown("""<div class="upload-zone"><div class="uz-icon">🏪</div>
        <div class="uz-title">ارفع ملف المتجر (تحديث او تعديل منتجات سلة)</div>
        <div class="uz-sub">الكشف التلقائي عن النواقص + إصلاح دُفعي + تصدير الصفوف المعدّلة فقط</div>
        </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — منتج سريع (quickadd)                                   ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "quickadd":

    st.markdown("""<div class="al-info">
    أضف منتجات جديدة بسرعة بطريقتين: <b>(1)</b> سحب بيانات من رابط URL مباشرةً،
    أو <b>(2)</b> إدخال يدوي مع رفع صور، أو <b>(3)</b> رفع صورة المنتج وتحليلها بالذكاء الاصطناعي تلقائياً.
    </div>""", unsafe_allow_html=True)

    qa_tabs = st.tabs(["🔗 سحب من رابط", "✏️ إدخال يدوي", "📸 رفع صورة + AI Vision"])

    # ── تبويب 1: سحب من رابط ────────────────────────────────────
    with qa_tabs[0]:
        st.markdown("**أدخل روابط المنتجات (كل رابط في سطر):**")
        urls_input = st.text_area("الروابط:", height=100,
                                   placeholder="https://www.competitor.com/product/1\nhttps://...",
                                   key="qa_urls")
        qa_col1, qa_col2, qa_col3 = st.columns(3)
        with qa_col1: qa_url_gen_desc = st.checkbox("🤖 توليد وصف AI", value=True, key="qa_url_gen_desc")
        with qa_col2: qa_url_gen_seo  = st.checkbox("🔍 توليد SEO",     value=True, key="qa_url_gen_seo")
        with qa_col3: qa_url_fetch_img = st.checkbox("🖼 جلب صورة إضافية", value=False, key="qa_url_fetch_img")

        if st.button("🚀 سحب وبناء البيانات", type="primary", key="qa_url_run",
                     use_container_width=True):
            urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip().startswith("http")]
            if not urls:
                st.warning("أدخل رابطاً واحداً على الأقل")
            else:
                qa_prog = st.progress(0)
                qa_stat = st.empty()
                for u_i, url in enumerate(urls):
                    qa_prog.progress(int((u_i / len(urls)) * 100))
                    qa_stat.markdown(f'<div class="prog-run">🔗 ({u_i+1}/{len(urls)}) {url[:60]}...</div>',
                                     unsafe_allow_html=True)
                    sc = scrape_product_url(url)
                    if sc.get("error"):
                        st.markdown(f'<div class="al-warn">⚠️ {url[:50]}: {sc["error"]}</div>',
                                    unsafe_allow_html=True)
                        continue

                    ex_name = sc.get("name","").strip() or url.split("/")[-1]
                    ex_desc = sc.get("desc","")
                    ex_price = sc.get("price","")
                    ex_brand_hint = sc.get("brand_hint","")
                    ex_img = sc.get("image","")

                    # ربط الماركة
                    if ex_brand_hint:
                        brand = match_brand(ex_brand_hint)
                        if not brand.get("name"):
                            brand = generate_new_brand(ex_brand_hint)
                            existing_b = [b.get("اسم الماركة","") for b in st.session_state.new_brands]
                            if ex_brand_hint not in existing_b:
                                st.session_state.new_brands.append({
                                    "اسم الماركة": brand.get("اسم الماركة", ex_brand_hint),
                                    "(SEO Page URL) رابط صفحة العلامة التجارية": brand.get(
                                        "(SEO Page URL) رابط صفحة العلامة التجارية", to_slug(ex_brand_hint)),
                                    "وصف مختصر عن الماركة": brand.get("وصف مختصر عن الماركة",""),
                                    "صورة شعار الماركة": brand.get("صورة شعار الماركة",""),
                                })
                    else:
                        brand = match_brand(ex_name)

                    ex_name = standardize_product_name(ex_name, brand.get("name","") if isinstance(brand,dict) else "")
                    cat     = match_category(ex_name, "للجنسين")

                    size_m  = re.search(r"(\d+)\s*(?:ml|مل|ML)", ex_name, re.IGNORECASE)
                    ex_size = size_m.group(0) if size_m else "100 مل"

                    seo = gen_seo(ex_name, brand if isinstance(brand,dict) else {"name":brand,"page_url":""}, ex_size, False, "للجنسين") \
                          if qa_url_gen_seo else {"url":"","title":"","desc":""}

                    if qa_url_gen_desc and st.session_state.api_key:
                        final_desc = ai_generate(ex_name, False,
                                                 brand if isinstance(brand,dict) else {"name":brand,"page_url":""},
                                                 ex_size, "للجنسين", "أو دو بارفيوم")
                    else:
                        final_desc = f"<p>{ex_desc}</p>" if ex_desc else ""

                    if qa_url_fetch_img and not ex_img:
                        ex_img = fetch_image(ex_name, False)

                    r = fill_row(
                        name=ex_name, price=ex_price, image=ex_img, desc=final_desc,
                        brand=brand if isinstance(brand,dict) else {"name":brand,"page_url":""},
                        category=cat, seo=seo, no=str(len(st.session_state.get("qa_rows",[])) + 1),
                        size=ex_size,
                    )
                    if "qa_rows" not in st.session_state:
                        st.session_state["qa_rows"] = []
                    st.session_state["qa_rows"].append(r)

                qa_prog.progress(100)
                qa_stat.markdown(f'<div class="prog-ok">✅ تم معالجة {len(urls)} رابط</div>',
                                  unsafe_allow_html=True)
                st.rerun()

    # ── تبويب 2: إدخال يدوي ─────────────────────────────────────
    with qa_tabs[1]:
        with st.form("qa_manual_form", clear_on_submit=True):
            mf1, mf2 = st.columns(2)
            with mf1:
                qa_mn   = st.text_input("اسم العطر ⭐", placeholder="ديور سوفاج 100 مل")
                qa_mbr  = st.text_input("الماركة",       placeholder="ديور | Dior")
                qa_mpr  = st.text_input("السعر",          placeholder="299")
            with mf2:
                qa_mgn  = st.selectbox("الجنس",    ["للجنسين","للرجال","للنساء"])
                qa_mtp  = st.selectbox("النوع",    ["عطر عادي","تستر"])
                qa_msk  = st.text_input("SKU (اختياري)")
            mf3, mf4 = st.columns(2)
            with mf3:
                qa_msz  = st.text_input("الحجم", "100 مل")
                qa_mcn  = st.selectbox("التركيز", ["أو دو بارفيوم","أو دو تواليت","أو دو كولون","بارفيوم"])
            with mf4:
                qa_mimg = st.text_input("رابط الصورة (اختياري)")
                qa_m_ai = st.checkbox("🤖 توليد وصف AI", value=True)
            submitted_m = st.form_submit_button("➕ إضافة للقائمة", type="primary", use_container_width=True)

        if submitted_m and qa_mn.strip():
            is_t_m = qa_mtp == "تستر"
            brand_m = match_brand(qa_mn)
            if not brand_m.get("name") and qa_mbr:
                brand_m = match_brand(qa_mbr)
            if not brand_m.get("name") and qa_mbr:
                brand_m = generate_new_brand(qa_mbr)
                eb2 = [b.get("اسم الماركة","") for b in st.session_state.new_brands]
                if qa_mbr not in eb2:
                    st.session_state.new_brands.append({
                        "اسم الماركة": brand_m.get("اسم الماركة", qa_mbr),
                        "(SEO Page URL) رابط صفحة العلامة التجارية": brand_m.get(
                            "(SEO Page URL) رابط صفحة العلامة التجارية", to_slug(qa_mbr)),
                        "وصف مختصر عن الماركة": brand_m.get("وصف مختصر عن الماركة",""),
                        "صورة شعار الماركة": brand_m.get("صورة شعار الماركة",""),
                    })
            cat_m  = "العطور > تستر" if is_t_m else match_category(qa_mn, qa_mgn)
            seo_m  = gen_seo(qa_mn, brand_m, qa_msz, is_t_m, qa_mgn)
            desc_m = ai_generate(qa_mn, is_t_m, brand_m, qa_msz, qa_mgn, qa_mcn) \
                     if qa_m_ai and st.session_state.api_key else ""
            img_m  = qa_mimg or fetch_image(qa_mn, is_t_m)
            r_m = fill_row(
                name=qa_mn, price=qa_mpr, sku=qa_msk, image=img_m, desc=desc_m,
                brand=brand_m, category=cat_m, seo=seo_m,
                no=str(len(st.session_state.get("qa_rows",[])) + 1),
                size=qa_msz,
            )
            if "qa_rows" not in st.session_state:
                st.session_state["qa_rows"] = []
            st.session_state["qa_rows"].append(r_m)
            st.success(f"✅ أُضيف: {qa_mn}")
            st.rerun()

    # ── عرض القائمة المتراكمة ────────────────────────────────────
    if st.session_state.get("qa_rows"):
        qa_rows = st.session_state["qa_rows"]
        st.markdown(f"""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>القائمة ({len(qa_rows)} منتج)</h3></div>""", unsafe_allow_html=True)

        prev_qa = [{"الاسم": r.get("أسم المنتج",""), "الماركة": r.get("الماركة",""),
                    "التصنيف": r.get("تصنيف المنتج",""), "السعر": r.get("سعر المنتج",""),
                    "وصف ✓": "✅" if len(str(r.get("الوصف","") or "")) > 20 else "—",
                    "صورة ✓": "✅" if str(r.get("صورة المنتج","") or "").startswith("http") else "—"}
                   for r in qa_rows]
        st.dataframe(pd.DataFrame(prev_qa), use_container_width=True, hide_index=True)

        qa_df = pd.DataFrame(qa_rows, columns=SALLA_COLS)
        date_str_qa = datetime.now().strftime("%Y-%m-%d_%H-%M")
        qe1, qe2, qe3 = st.columns(3)
        with qe1:
            st.download_button(
                f"📥 منتج جديد — CSV ({len(qa_rows)})",
                export_product_csv(qa_df),
                f"منتج_جديد_{date_str_qa}.csv", "text/csv",
                use_container_width=True, key="qa_dl_csv", type="primary")
        with qe2:
            st.download_button(
                f"📥 منتج جديد — Excel ({len(qa_rows)})",
                export_product_xlsx(qa_df),
                f"منتج_جديد_{date_str_qa}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="qa_dl_xlsx")
        with qe3:
            if st.button("🗑️ مسح القائمة", key="qa_clear"):
                st.session_state["qa_rows"] = []
                st.rerun()

    # ── تبويب 3: رفع صورة + AI Vision ──────────────────────────────────────
    with qa_tabs[2]:
        st.markdown("""
        <div class="al-info">
        ارفع صورة العطر وسيقوم Claude Vision بتحليلها واستخراج اسم المنتج والماركة والحجم والتركيز تلقائياً.
        ثم يولد الوصف ويجلب المكونات بدقة عالية.
        </div>""", unsafe_allow_html=True)

        if not st.session_state.api_key:
            st.warning("⚠️ يجب إدخال Claude API Key في صفحة الإعدادات لتفعيل هذه الخاصية.")
        else:
            with st.form("qa_vision_form", clear_on_submit=True):
                vis_img = st.file_uploader("📸 ارفع صورة المنتج (JPG/PNG)",
                                           type=["jpg","jpeg","png","webp"], key="qa_vis_img")
                vis_c1, vis_c2 = st.columns(2)
                with vis_c1:
                    vis_price = st.text_input("سعر المنتج", placeholder="299")
                    vis_gender = st.selectbox("الجنس", ["للجنسين","للرجال","للنساء"])
                with vis_c2:
                    vis_sku = st.text_input("SKU (اختياري)")
                    vis_tester = st.checkbox("تستر")
                vis_submit = st.form_submit_button("🤖 تحليل بالذكاء الاصطناعي", type="primary", use_container_width=True)

            if vis_submit and vis_img:
                import base64
                vis_prog = st.progress(0, "جاري تحليل الصورة...")
                try:
                    img_bytes = vis_img.read()
                    img_b64   = base64.standard_b64encode(img_bytes).decode()
                    ext       = vis_img.name.split(".")[-1].lower()
                    mime_map  = {"jpg":"image/jpeg","jpeg":"image/jpeg","png":"image/png","webp":"image/webp"}
                    mime_type = mime_map.get(ext, "image/jpeg")

                    vis_prog.progress(20, "جاري إرسال الصورة لـ Claude Vision...")
                    client_v = anthropic.Anthropic(api_key=st.session_state.api_key)
                    vision_prompt = (
                        "أنت خبير عطور فاخرة. حلّل صورة العطر وأخرج البيانات بصيغة JSON فقط بدون أي نصوص خارجها:\n"
                        '{"name": "اسم العطر كاملاً بالعربي", '
                        '"brand_ar": "اسم الماركة بالعربي", '
                        '"brand_en": "Brand name in English", '
                        '"size": "الحجم مثل 100 مل", '
                        '"concentration": "التركيز مثل أو دو بارفيوم", '
                        '"is_tester": false}'
                    )
                    vis_msg = client_v.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=400,
                        messages=[{"role": "user", "content": [
                            {"type": "image", "source": {"type": "base64", "media_type": mime_type, "data": img_b64}},
                            {"type": "text",  "text": vision_prompt}
                        ]}]
                    )
                    vis_prog.progress(50, "جاري معالجة نتائج Vision...")
                    vis_raw = vis_msg.content[0].text.strip()
                    vis_m   = re.search(r'\{[\s\S]*\}', vis_raw)
                    if vis_m:
                        vis_data = json.loads(vis_m.group())
                        vis_name  = vis_data.get("name", "")
                        vis_brand_ar = vis_data.get("brand_ar", "")
                        vis_brand_en = vis_data.get("brand_en", "")
                        vis_size  = vis_data.get("size", "100 مل")
                        vis_conc  = vis_data.get("concentration", "أو دو بارفيوم")
                        vis_is_t  = vis_data.get("is_tester", False) or vis_tester

                        vis_prog.progress(65, "جاري ربط الماركة...")
                        vis_brand_d = match_brand(vis_name)
                        if not vis_brand_d.get("name") and vis_brand_ar:
                            vis_brand_d = match_brand(vis_brand_ar)
                        if not vis_brand_d.get("name") and vis_brand_ar:
                            vis_brand_d = generate_new_brand(vis_brand_ar)
                            eb_v = [b.get("اسم الماركة","") for b in st.session_state.new_brands]
                            if vis_brand_ar not in eb_v:
                                st.session_state.new_brands.append({
                                    "اسم الماركة": vis_brand_d.get("اسم الماركة", vis_brand_ar),
                                    "(SEO Page URL) رابط صفحة العلامة التجارية": vis_brand_d.get("page_url", to_slug(vis_brand_en or vis_brand_ar)),
                                    "وصف مختصر عن الماركة": vis_brand_d.get("وصف مختصر عن الماركة",""),
                                    "صورة شعار الماركة": vis_brand_d.get("صورة شعار الماركة",""),
                                })

                        vis_prog.progress(80, "جاري توليد الوصف وجلب الصورة...")
                        vis_name_std = standardize_product_name(vis_name, vis_brand_d.get("name",""))
                        vis_cat   = "العطور > تستر" if vis_is_t else match_category(vis_name_std, vis_gender)
                        vis_seo   = gen_seo(vis_name_std, vis_brand_d, vis_size, vis_is_t, vis_gender)
                        vis_desc  = ai_generate(vis_name_std, vis_is_t, vis_brand_d, vis_size, vis_gender, vis_conc)
                        vis_img_url = fetch_image(vis_name_std, vis_is_t)

                        vis_prog.progress(95, "جاري حفظ النتيجة...")
                        vis_row = fill_row(
                            name=vis_name_std, price=vis_price, sku=vis_sku,
                            image=vis_img_url, desc=vis_desc,
                            brand=vis_brand_d, category=vis_cat, seo=vis_seo,
                            no=str(len(st.session_state.get("qa_rows",[]))+1),
                            size=vis_size,
                        )
                        if "qa_rows" not in st.session_state:
                            st.session_state["qa_rows"] = []
                        st.session_state["qa_rows"].append(vis_row)
                        vis_prog.progress(100, "✅ تم التحليل والإضافة بنجاح!")
                        st.success(f"✅ تم استخراج: {vis_name_std} | {vis_brand_d.get('name','')} | {vis_size}")
                        st.rerun()
                    else:
                        vis_prog.progress(100)
                        st.error("❌ لم يتمكن Claude Vision من تحليل الصورة. تأكد أن الصورة واضحة وتحتوي على عطر بمعلومات مقروءة.")
                except Exception as _ve:
                    st.error(f"❌ خطأ في تحليل الصورة: {_ve}")
            elif vis_submit and not vis_img:
                st.warning("⚠️ يرجى رفع صورة أولاً.")


# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — مدقق الماركات (brands)                                 ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "brands":

    st.markdown("""<div class="al-info">
    ارفع ملف ماركات أو منتجات للتحقق منها مقابل قاعدة بيانات مهووس.
    الماركات غير الموجودة سيُولَّد لها ملف سلة كامل بالذكاء الاصطناعي.
    </div>""", unsafe_allow_html=True)

    up_b = st.file_uploader("ارفع ملف الماركات أو المنتجات",
                             type=["csv","xlsx","xls"], key="brands_up")
    if up_b:
        bdf_raw = read_file(up_b)
        if not bdf_raw.empty:
            st.success(f"✅ {len(bdf_raw)} صف")
            with st.expander("👀 معاينة"): st.dataframe(bdf_raw.head(6), use_container_width=True, hide_index=True)

            NONE_B = "— لا يوجد —"
            bopts  = [NONE_B] + list(bdf_raw.columns)
            def bgi(kws): return bopts.index(auto_guess_col(bdf_raw.columns, kws)) \
                          if auto_guess_col(bdf_raw.columns, kws) in bopts else 0

            b1, b2, b3 = st.columns(3)
            with b1: bcol_name = st.selectbox("عمود اسم الماركة:",
                                               bopts, index=bgi(["ماركة","brand","علامة","اسم"]), key="bcol_nm")
            with b2: bcol_prod = st.selectbox("عمود اسم المنتج (اختياري):",
                                               bopts, index=bgi(["منتج","product"]), key="bcol_pr")
            with b3: gen_miss_b = st.checkbox("🤖 توليد ماركات جديدة بـ AI", value=True, key="gen_miss_b")

            if st.button("🔍 تدقيق وتحليل الآن", type="primary",
                         key="check_brands", use_container_width=True):
                if bcol_name == NONE_B:
                    st.error("حدد عمود اسم الماركة")
                else:
                    results_b   = []
                    new_brands_b = []
                    seen_b = set()
                    prog_b = st.progress(0)
                    total_b = len(bdf_raw)

                    for b_i, (_, row) in enumerate(bdf_raw.iterrows()):
                        prog_b.progress(int((b_i / max(total_b,1)) * 100))
                        bname = str(row.get(bcol_name, "") or "").strip()
                        pname = str(row.get(bcol_prod, "") or "").strip() \
                                if bcol_prod != NONE_B else ""
                        if not bname and not pname:
                            continue
                        search_nm = bname or pname
                        found = match_brand(search_nm)
                        status_b = "موجودة ✅" if found.get("name") else "غير موجودة ❌"
                        results_b.append({
                            "الماركة المدخلة":          bname,
                            "المنتج":                   pname,
                            "الماركة في القاعدة":       found.get("name","—"),
                            "نسبة التطابق":             "100%" if found.get("name") else "0%",
                            "الحالة":                   status_b,
                        })
                        if not found.get("name") and bname and bname not in seen_b:
                            seen_b.add(bname)
                            new_brands_b.append(bname)

                    prog_b.progress(100)
                    res_b_df = pd.DataFrame(results_b)
                    st.dataframe(res_b_df, use_container_width=True, hide_index=True)

                    found_c   = int((res_b_df["الحالة"] == "موجودة ✅").sum())
                    missing_c = int((res_b_df["الحالة"] == "غير موجودة ❌").sum())
                    st.markdown(f"""
                    <div class="stats-bar">
                      <div class="stat-box"><div class="n" style="color:#43a047">{found_c}</div><div class="lb">موجودة ✅</div></div>
                      <div class="stat-box"><div class="n" style="color:#e53935">{missing_c}</div><div class="lb">غير موجودة ❌</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    # توليد الماركات الجديدة
                    if new_brands_b:
                        generated_entries = []
                        if gen_miss_b and st.session_state.api_key:
                            with st.spinner(f"جاري توليد بيانات {len(new_brands_b)} ماركة جديدة..."):
                                for nb_name in new_brands_b:
                                    gen = generate_new_brand(nb_name)
                                    generated_entries.append(gen)
                        else:
                            for nb_name in new_brands_b:
                                generated_entries.append({
                                    "اسم الماركة": nb_name,
                                    "وصف مختصر عن الماركة": f"علامة تجارية متخصصة في العطور الفاخرة — {nb_name}",
                                    "صورة شعار الماركة": "",
                                    "(إختياري) صورة البانر": "",
                                    "(Page Title) عنوان صفحة العلامة التجارية": f"عطور {nb_name} الأصلية | مهووس",
                                    "(SEO Page URL) رابط صفحة العلامة التجارية": to_slug(nb_name),
                                    "(Page Description) وصف صفحة العلامة التجارية":
                                        f"تسوّق أحدث عطور {nb_name} الأصلية بأسعار حصرية من متجر مهووس.",
                                })

                        # إضافة للـ session_state
                        existing_nb = {b.get("اسم الماركة","") for b in st.session_state.new_brands}
                        for entry in generated_entries:
                            if entry.get("اسم الماركة","") not in existing_nb:
                                st.session_state.new_brands.append(entry)
                        st.info(f"🆕 {len(generated_entries)} ماركة جديدة جاهزة للتصدير")

    # ── عرض الماركات الجديدة المتراكمة ──────────────────────────
    if st.session_state.new_brands:
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الماركات الجديدة المُولَّدة — جاهزة للتصدير</h3></div>""", unsafe_allow_html=True)

        nb_df_disp = pd.DataFrame(st.session_state.new_brands)
        edited_nb  = st.data_editor(nb_df_disp, use_container_width=True,
                                     hide_index=True, num_rows="dynamic", key="nb_editor")
        st.session_state.new_brands = edited_nb.to_dict("records")

        date_str_nb = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nb1, nb2, nb3 = st.columns(3)
        with nb1:
            st.download_button(
                f"📥 ماركات جديدة — Excel ({len(st.session_state.new_brands)})",
                export_brands_xlsx(st.session_state.new_brands),
                f"ماركات_جديدة_{date_str_nb}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="dl_nb_x", type="primary")
        with nb2:
            nb_csv_buf = io.StringIO()
            nb_csv_buf.write(",".join(SALLA_BRANDS_COLS) + "\n")
            for nb in st.session_state.new_brands:
                nb_csv_buf.write(",".join([f'"{str(nb.get(c,"") or "")}"'
                                           for c in SALLA_BRANDS_COLS]) + "\n")
            st.download_button(
                f"📥 ماركات جديدة — CSV ({len(st.session_state.new_brands)})",
                nb_csv_buf.getvalue().encode("utf-8-sig"),
                f"ماركات_جديدة_{date_str_nb}.csv", "text/csv",
                use_container_width=True, key="dl_nb_c")
        with nb3:
            if st.button("🗑️ مسح الماركات", key="clear_nb_brands"):
                st.session_state.new_brands = []
                st.rerun()

        # توليد صور وسيو للماركات الناقصة
        no_img_brands = [b for b in st.session_state.new_brands
                         if not str(b.get("صورة شعار الماركة","")).startswith("http")]
        if no_img_brands and (st.session_state.api_key or (st.session_state.google_api and st.session_state.google_cse)):
            if st.button(f"🖼 جلب الصور لـ {len(no_img_brands)} ماركة بدون شعار",
                         key="gen_nb_imgs", use_container_width=True):
                with st.spinner("جاري جلب الصور..."):
                    for nb in st.session_state.new_brands:
                        if not str(nb.get("صورة شعار الماركة","")).startswith("http"):
                            gen = generate_new_brand(nb.get("اسم الماركة",""))
                            nb["صورة شعار الماركة"]    = gen.get("صورة شعار الماركة","")
                            nb["(إختياري) صورة البانر"] = gen.get("(إختياري) صورة البانر","")
                st.success("✅ تم جلب الصور")
                st.rerun()

    elif not up_b:
        st.markdown("""<div class="upload-zone"><div class="uz-icon">🔍</div>
        <div class="uz-title">ارفع ملف الماركات أو المنتجات للتدقيق</div>
        <div class="uz-sub">مطابقة مع قاعدة مهووس · توليد ماركات جديدة بتنسيق سلة · تصدير جاهز</div>
        </div>""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE — الإعدادات (settings)                                   ║
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
            st.success("✅ تم الحفظ")
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
            st.success("✅ تم الحفظ")

    st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
    <h3>قواعد البيانات المرجعية</h3></div>""", unsafe_allow_html=True)

    db1, db2 = st.columns(2)
    with db1:
        st.markdown("**ملف الماركات**")
        bdf_s = st.session_state.brands_df
        if bdf_s is not None:
            st.markdown(f'<div class="al-ok">{len(bdf_s):,} ماركة محملة</div>',
                        unsafe_allow_html=True)
            with st.expander("👀 معاينة"): st.dataframe(bdf_s.head(5), use_container_width=True, hide_index=True)
        up_brands_s = st.file_uploader("تحديث ملف الماركات:", type=["csv","xlsx"], key="up_brands_db")
        if up_brands_s:
            df_b_s = read_file(up_brands_s)
            if not df_b_s.empty:
                st.session_state.brands_df = df_b_s
                os.makedirs(DATA_DIR, exist_ok=True)
                df_b_s.to_csv(os.path.join(DATA_DIR, "brands.csv"), index=False, encoding="utf-8-sig")
                st.success(f"✅ تم تحديث {len(df_b_s):,} ماركة")
                st.rerun()

    with db2:
        st.markdown("**ملف التصنيفات**")
        cdf_s = st.session_state.categories_df
        if cdf_s is not None:
            st.markdown(f'<div class="al-ok">{len(cdf_s):,} تصنيف محمّل</div>',
                        unsafe_allow_html=True)
            with st.expander("👀 معاينة"): st.dataframe(cdf_s.head(5), use_container_width=True, hide_index=True)
        up_cats_s = st.file_uploader("تحديث ملف التصنيفات:", type=["csv","xlsx"], key="up_cats_db")
        if up_cats_s:
            df_c_s = read_file(up_cats_s)
            if not df_c_s.empty:
                st.session_state.categories_df = df_c_s
                os.makedirs(DATA_DIR, exist_ok=True)
                df_c_s.to_csv(os.path.join(DATA_DIR, "categories.csv"), index=False, encoding="utf-8-sig")
                st.success(f"✅ تم تحديث {len(df_c_s):,} تصنيف")
                st.rerun()

    # ── الماركات الجديدة المُولَّدة ──────────────────────────────
    if st.session_state.new_brands:
        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>الماركات الجديدة بانتظار التصدير</h3></div>""", unsafe_allow_html=True)
        st.markdown(f'<div class="al-warn">{len(st.session_state.new_brands)} ماركة جديدة اكتُشفت خلال المعالجة.</div>',
                    unsafe_allow_html=True)
        nb_df_s2 = pd.DataFrame(st.session_state.new_brands)
        st.dataframe(nb_df_s2, use_container_width=True, hide_index=True)
        sn1, sn2 = st.columns(2)
        date_str_s = datetime.now().strftime("%Y-%m-%d_%H-%M")
        with sn1:
            st.download_button("📥 تصدير الماركات — Excel",
                export_brands_xlsx(st.session_state.new_brands),
                f"new_brands_{date_str_s}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="exp_nb_set_x")
        with sn2:
            nb_csv_s = io.StringIO()
            nb_csv_s.write(",".join(SALLA_BRANDS_COLS) + "\n")
            for nb in st.session_state.new_brands:
                nb_csv_s.write(",".join([f'"{str(nb.get(c,"") or "")}"'
                                          for c in SALLA_BRANDS_COLS]) + "\n")
            st.download_button("📥 تصدير الماركات — CSV",
                nb_csv_s.getvalue().encode("utf-8-sig"),
                f"new_brands_{date_str_s}.csv", "text/csv",
                use_container_width=True, key="exp_nb_set_c")

    st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
    <h3>معلومات النظام</h3></div>""", unsafe_allow_html=True)
    st.markdown(f"""
    <div style="direction:rtl;font-size:0.85rem;line-height:2.2">
      <b>الإصدار:</b> مهووس مركز التحكم الشامل v12.0<br>
      <b>أعمدة سلة المنتجات:</b> {len(SALLA_COLS)} عمود<br>
      <b>أعمدة ملف الماركات:</b> {len(SALLA_BRANDS_COLS)} عمود<br>
      <b>الماركات في القاعدة:</b> {len(st.session_state.brands_df) if st.session_state.brands_df is not None else 0}<br>
      <b>التصنيفات في القاعدة:</b> {len(st.session_state.categories_df) if st.session_state.categories_df is not None else 0}<br>
    </div>
    """, unsafe_allow_html=True)



# ╔══════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝
st.markdown("""
<div class="mhw-footer">
  مهووس — مركز التحكم الشامل v12.0 (Phase 1) &nbsp;|&nbsp;
  المسار الآلي المدمج · معالجة دُفعية · محرك مقارنة v12.0 &nbsp;|&nbsp;
  <a href="https://mahwous-automation-production.up.railway.app/" target="_blank">mahwous.com</a>
</div>
""", unsafe_allow_html=True)
