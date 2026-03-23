"""
╔══════════════════════════════════════════════════════════════════╗
║   مهووس — مركز التحكم الشامل  v4.0  (Production-Ready)         ║
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

# Editor shows these by default (rest hidden unless user selects)
EDITOR_COLS = [
    "No.", "النوع ", "أسم المنتج", "الماركة", "تصنيف المنتج",
    "سعر المنتج", "رمز المنتج sku", "صورة المنتج",
    "وصف صورة المنتج", "حالة المنتج", "السعر المخفض",
]

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ╔══════════════════════════════════════════════════════════════════╗
# ║  AI SYSTEM PROMPT                                               ║
# ╚══════════════════════════════════════════════════════════════════╝
AI_SYSTEM = """أنت خبير كتابة أوصاف عطور فاخرة تعمل حصرياً لمتجر "مهووس" السعودي.

قواعد صارمة لا تُكسر:
- ممنوع منعاً باتاً استخدام الرموز التعبيرية (Emojis) نهائياً
- التركيز يُكتب دائماً: "أو دو بارفيوم"
- أسلوبك: راقٍ 40%، ودود 25%، رومانسي 20%، تسويقي مقنع 15%
- الطول: 1200-1500 كلمة بالضبط
- الإخراج HTML خالص فقط — لا نص خارج الوسوم
- استخدم <strong> للكلمات المفتاحية

هيكل الوصف الإلزامي:
<h2>[عطر/تستر] [الماركة] [الاسم] [التركيز] [الحجم] [للجنس]</h2>
<p>فقرة افتتاحية عاطفية 100-150 كلمة، الكلمة المفتاحية في أول 50 كلمة، دعوة للشراء.</p>
<h3>تفاصيل المنتج</h3>
<ul>
<li><strong>الماركة:</strong> [مع رابط داخلي إن وُجد]</li>
<li><strong>الجنس:</strong></li>
<li><strong>العائلة العطرية:</strong></li>
<li><strong>الحجم:</strong></li>
<li><strong>التركيز:</strong> أو دو بارفيوم</li>
<li><strong>نوع المنتج:</strong> [تستر / عادي]</li>
</ul>
<h3>رحلة العطر - الهرم العطري</h3>
<ul>
<li><strong>المقدمة (Top Notes):</strong></li>
<li><strong>القلب (Heart Notes):</strong></li>
<li><strong>القاعدة (Base Notes):</strong></li>
</ul>
<h3>لماذا تختار هذا العطر؟</h3>
<ul>
<li><strong>الثبات والفوحان:</strong></li>
<li><strong>التميز والأصالة:</strong></li>
<li><strong>القيمة الاستثنائية:</strong></li>
<li><strong>الجاذبية المضمونة:</strong></li>
</ul>
<h3>متى وأين ترتديه؟</h3><p>...</p>
<h3>لمسة خبير من مهووس</h3><p>...</p>
<h3>الأسئلة الشائعة</h3>
<ul>
<li><strong>كم يدوم العطر؟</strong></li>
<li><strong>هل يناسب الاستخدام اليومي؟</strong></li>
<li><strong>ما الفرق بين التستر والعطر العادي؟</strong></li>
<li><strong>ما العائلة العطرية؟</strong></li>
<li><strong>هل يناسب الطقس الحار في السعودية؟</strong></li>
<li><strong>ما مناسبات ارتداء هذا العطر؟</strong></li>
</ul>
<p><strong>عالمك العطري يبدأ من مهووس.</strong> أصلي 100% | شحن سريع داخل السعودية.</p>"""

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
        return "<p>⚠️ أضف مفتاح Anthropic API في الإعدادات أولاً</p>"
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
             brand=None, category="", seo=None, no="") -> dict:
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

# ╔══════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR NAVIGATION                                             ║
# ╚══════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:18px 0 10px">
      <div style="font-size:2.4rem">🌸</div>
      <div style="color:#b8933a;font-size:1.25rem;font-weight:900;margin:4px 0">مهووس</div>
      <div style="color:rgba(255,255,255,0.3);font-size:0.7rem">مركز التحكم الشامل v4.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    PAGES = [
        ("🛠️", "المُعالج الشامل",   "processor"),
        ("💰", "مُحدّث الأسعار",    "price"),
        ("➕", "منتج سريع",          "quickadd"),
        ("🔍", "مدقق الماركات",     "brands"),
        ("⚙️", "الإعدادات",         "settings"),
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
    "processor": ("🛠️ المُعالج الشامل",   "ارفع أي ملف — اربط الأعمدة — اكمل بالذكاء الاصطناعي — صدّر لسلة"),
    "price":     ("💰 مُحدّث الأسعار",    "رفع أي ملف أسعار وتصديره بتنسيق سلة الدقيق"),
    "quickadd":  ("➕ منتج سريع",          "أدخل اسم العطر فقط وسيكمل النظام الباقي"),
    "brands":    ("🔍 مدقق الماركات",     "قارن قائمة ماركات بقاعدة بيانات مهووس"),
    "settings":  ("⚙️ الإعدادات",         "مفاتيح API وقواعد البيانات المرجعية"),
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

        c4, c5, c6 = st.columns(3)
        with c4:
            col_brand  = st.selectbox("الماركة (إن وجدت)",      opts, index=gi(["ماركة","brand","علامة"]),             key="cm_br")
        with c5:
            col_gender = st.selectbox("الجنس (إن وجد)",         opts, index=gi(["جنس","gender","sex"]),                 key="cm_gn")
        with c6:
            col_tester = st.selectbox("تستر/عادي (إن وجد)",    opts, index=gi(["تستر","tester","نوع","type"]),          key="cm_ts")

        st.markdown("**الإعدادات الافتراضية** (تُطبق عند غياب العمود المقابل):")
        d1, d2, d3, d4 = st.columns(4)
        with d1: dft_gender = st.selectbox("الجنس",     ["للجنسين","للرجال","للنساء"],       key="dft_gn")
        with d2: dft_size   = st.text_input("الحجم",    "100 مل",                             key="dft_sz")
        with d3: dft_conc   = st.selectbox("التركيز",   ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="dft_cn")
        with d4: dft_type   = st.selectbox("النوع",     ["عطر عادي","تستر"],                  key="dft_tp")

        if col_name == NONE_OPT:
            st.warning("⚠️ يرجى تحديد عمود اسم المنتج على الأقل")
        else:
            if st.button("✅ تأكيد وتحويل الملف إلى تنسيق سلة", type="primary", key="map_btn"):
                rows_out = []
                seo_out  = []
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

                    is_test = any(w in tester_v.lower()
                                  for w in ["تستر","tester","yes","نعم"]) \
                              if col_tester != NONE_OPT else (dft_type == "تستر")

                    brand    = match_brand(name) if not brand_raw else \
                               {"name": brand_raw, "page_url": ""}
                    cat      = match_category(name, gender)
                    seo      = gen_seo(name, brand, size, is_test, gender)

                    nr = fill_row(name=name, price=price, sku=sku, image=img,
                                  desc=desc, brand=brand, category=cat, seo=seo)
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
                st.success(f"✅ تم تحويل {len(rows_out)} صف إلى تنسيق سلة بنجاح!")
                st.rerun()

    # ── STEP C: Toolbox + Editor ──────────────────────────────────
    if st.session_state.up_df is not None and st.session_state.up_mapped:
        df = st.session_state.up_df

        # Stats
        def _cnt(col):
            return int((df.get(col, pd.Series(dtype=str)).fillna("")
                        .str.strip() != "").sum())

        st.markdown(f"""
        <div class="stats-bar">
          <div class="stat-box"><div class="n">{len(df)}</div><div class="lb">إجمالي المنتجات</div></div>
          <div class="stat-box"><div class="n">{_cnt("الوصف")}</div><div class="lb">مع وصف AI</div></div>
          <div class="stat-box"><div class="n">{int(df.get("صورة المنتج",pd.Series(dtype=str)).fillna("").str.startswith("http").sum())}</div><div class="lb">مع صورة</div></div>
          <div class="stat-box"><div class="n">{_cnt("الماركة")}</div><div class="lb">مع ماركة</div></div>
          <div class="stat-box"><div class="n">{_cnt("سعر المنتج")}</div><div class="lb">مع سعر</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""<hr class="gdiv"><div class="sec-title"><div class="bar"></div>
        <h3>أدوات المعالجة الذكية</h3></div>""", unsafe_allow_html=True)

        tabs = st.tabs([
            "🤖 توليد الأوصاف",
            "🖼 جلب الصور",
            "🏷 الماركات والتصنيفات",
            "➕ إضافة منتج",
            "🔁 عمليات مجمّعة",
        ])

        # ── Tab 0: AI Descriptions ─────────────────────────────
        with tabs[0]:
            st.markdown("**توليد الوصف الاحترافي بالذكاء الاصطناعي (Claude)**")
            if not st.session_state.api_key:
                st.markdown('<div class="al-warn">أضف مفتاح Anthropic API في صفحة الإعدادات أولاً</div>',
                            unsafe_allow_html=True)
            scope_d = st.radio("نطاق التوليد:", [
                "الصفوف التي ليس لها وصف فقط",
                "صف واحد برقمه",
                "كل الصفوف (يستغرق وقتاً)",
            ], horizontal=True, key="scope_d")

            dd1, dd2, dd3 = st.columns(3)
            with dd1: d_conc   = st.selectbox("التركيز", ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"], key="d_conc")
            with dd2: d_gender = st.selectbox("الجنس الافتراضي", ["للجنسين","للرجال","للنساء"], key="d_gender")
            with dd3: d_size   = st.text_input("الحجم الافتراضي", "100 مل", key="d_size")

            if scope_d == "صف واحد برقمه":
                d_row = st.number_input("رقم الصف (يبدأ من 0)", 0, max(0, len(df)-1), 0, key="d_row")

            if st.button("🚀 توليد الأوصاف الآن", type="primary", key="gen_desc"):
                if scope_d.startswith("الصفوف التي"):
                    idxs = [i for i in range(len(df))
                            if not str(df.iloc[i].get("الوصف","")).strip()]
                elif scope_d.startswith("صف واحد"):
                    idxs = [d_row]
                else:
                    idxs = list(range(len(df)))

                if not idxs:
                    st.info("لا توجد صفوف تحتاج وصفاً")
                else:
                    prog = st.progress(0); stat = st.empty()
                    for n, i in enumerate(idxs):
                        row  = df.iloc[i]
                        name = str(row.get("أسم المنتج", "")).strip()
                        if not name:
                            continue
                        stat.markdown(
                            f'<div class="prog-run">⏳ ({n+1}/{len(idxs)}) {name}</div>',
                            unsafe_allow_html=True)
                        is_t   = any(w in name.lower() for w in ["تستر","tester"])
                        size_m = re.search(r"\d+\s*(?:مل|ml)", name, re.I)
                        size   = size_m.group() if size_m else d_size
                        brand  = match_brand(name)
                        desc   = ai_generate(name, is_t, brand, size, d_gender, d_conc)
                        df.at[i, "الوصف"]   = desc
                        df.at[i, "الماركة"] = df.at[i, "الماركة"] or brand.get("name", "")
                        prog.progress(int((n+1)/len(idxs)*100))

                    st.session_state.up_df = df
                    stat.markdown(f'<div class="prog-ok">✅ تم توليد {len(idxs)} وصف</div>',
                                  unsafe_allow_html=True)
                    st.rerun()

        # ── Tab 1: Images ──────────────────────────────────────
        with tabs[1]:
            st.markdown("**جلب الصور عبر Google Custom Search**")
            if not (st.session_state.google_api and st.session_state.google_cse):
                st.markdown('<div class="al-warn">أضف Google API Key و CSE ID في الإعدادات</div>',
                            unsafe_allow_html=True)
            scope_i = st.radio("نطاق الجلب:", [
                "الصفوف التي ليس لها صورة فقط",
                "صف واحد برقمه",
                "كل الصفوف",
            ], horizontal=True, key="scope_i")
            if scope_i == "صف واحد برقمه":
                i_row = st.number_input("رقم الصف", 0, max(0, len(df)-1), 0, key="i_row")
            add_test_kw = st.checkbox("إضافة 'tester' للبحث إن كان المنتج تستراً", value=True)

            if st.button("🖼 جلب الصور الآن", type="primary", key="fetch_imgs"):
                if scope_i.startswith("الصفوف"):
                    idxs = [i for i in range(len(df))
                            if not str(df.iloc[i].get("صورة المنتج","")).startswith("http")]
                elif scope_i.startswith("صف واحد"):
                    idxs = [i_row]
                else:
                    idxs = list(range(len(df)))

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
                        df.at[i, "صورة المنتج"] = url
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
                        df.at[man_row, "صورة المنتج"] = man_url
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
                for i in idxs:
                    name  = str(df.iloc[i].get("أسم المنتج","")).strip()
                    if not name: continue
                    brand = match_brand(name)
                    cat   = match_category(name)
                    if brand.get("name"):
                        df.at[i, "الماركة"]      = brand["name"]
                    if not str(df.iloc[i].get("تصنيف المنتج","")).strip():
                        df.at[i, "تصنيف المنتج"] = cat
                st.session_state.up_df = df
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
                    df.at[b_row, "الماركة"] = sel_brand
                if sel_cat != "— اختر —" and cdf is not None:
                    crow = cdf[cdf["التصنيفات"] == sel_cat]
                    if not crow.empty:
                        par  = str(crow.iloc[0].get("التصنيف الاساسي",""))
                        path = f"{par} > {sel_cat}" if par.strip() else sel_cat
                    else:
                        path = sel_cat
                    df.at[b_row, "تصنيف المنتج"] = path
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
            with np5: np_price = st.text_input("السعر", key="np_pr")
            with np6: np_sku   = st.text_input("SKU", key="np_sk")
            with np7: np_img   = st.text_input("رابط الصورة", key="np_im")
            with np8: np_type  = st.selectbox("النوع", ["عطر عادي","تستر"], key="np_tp")

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
                        brand  = match_brand(np_name)
                        cat    = match_category(np_name, np_gender)
                        seo    = gen_seo(np_name, brand, np_size, is_t, np_gender)
                        img    = np_img or (fetch_image(np_name, is_t) if do_i else "")
                        desc   = ai_generate(np_name, is_t, brand, np_size, np_gender, np_conc) \
                                 if do_d else ""
                        nr     = fill_row(name=np_name, price=np_price, sku=np_sku,
                                          image=img, desc=desc, brand=brand,
                                          category=cat, seo=seo)
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
            ], key="bulk_ops")

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
                        df.at[idx, "الوزن"]                    = df.at[idx, "الوزن"] or "0.2"
                        df.at[idx, "وحدة الوزن"]               = df.at[idx, "وحدة الوزن"] or "kg"
                        df.at[idx, "حالة المنتج"]              = df.at[idx, "حالة المنتج"] or "مرئي"
                        df.at[idx, "اقصي كمية لكل عميل"]      = df.at[idx, "اقصي كمية لكل عميل"] or "0"
                        df.at[idx, "إخفاء خيار تحديد الكمية"] = "0"
                        df.at[idx, "اضافة صورة عند الطلب"]    = "0"
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
                df.at[sel_p, "الوصف"] = new_d
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

        e1, e2, e3, e4 = st.columns(4)
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

        f4, f5, f6 = st.columns(3)
        with f4: qa_tp  = st.selectbox("النوع", ["عطر عادي","تستر"])
        with f5: qa_img = st.text_input("رابط الصورة (اختياري)")
        with f6: st.markdown("<br>", unsafe_allow_html=True)

        o1, o2, o3 = st.columns(3)
        with o1: qa_do_d = st.checkbox("🤖 وصف AI",   value=True)
        with o2: qa_do_i = st.checkbox("🖼 جلب صورة", value=False)
        with o3: qa_do_s = st.checkbox("🔍 SEO",       value=True)

        sub = st.form_submit_button("➕ إضافة للقائمة", type="primary",
                                    use_container_width=True)

    if sub and qa_nm.strip():
        with st.spinner("جاري المعالجة..."):
            is_t   = qa_tp == "تستر"
            brand  = match_brand(qa_nm)
            cat    = match_category(qa_nm, qa_gn)
            seo    = gen_seo(qa_nm, brand, qa_sz, is_t, qa_gn)
            img    = qa_img or (fetch_image(qa_nm, is_t) if qa_do_i else "")
            desc   = ai_generate(qa_nm, is_t, brand, qa_sz, qa_gn, qa_cn) if qa_do_d else ""
            nr     = fill_row(name=qa_nm, price=qa_pr, sku=qa_sk, image=img,
                              desc=desc, brand=brand, category=cat, seo=seo)
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
# ║  PAGE 4 — BRANDS CHECKER                                        ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "brands":

    st.markdown("""<div class="al-info">
    ارفع ملفاً يحتوي قائمة أسماء ماركات (من مورد جديد مثلاً) وسيقارنها النظام
    مع قاعدة بيانات مهووس ليحدد المتوفرة والجديدة.
    </div>""", unsafe_allow_html=True)

    up_br = st.file_uploader("ارفع ملف الماركات (CSV / Excel — عمود واحد يكفي)",
                              type=["csv","xlsx","xls"], key="brands_up")
    if up_br:
        br_raw = read_file(up_br)
        if not br_raw.empty:
            cols_br = ["— اختر —"] + list(br_raw.columns)
            bc = st.selectbox("عمود أسماء الماركات:", cols_br,
                              index=1 if len(cols_br) > 1 else 0, key="bc_col")

            if bc != "— اختر —" and st.button("🔍 فحص الآن", type="primary", key="check_brands"):
                if st.session_state.brands_df is None:
                    st.error("قاعدة بيانات الماركات غير محملة. أضفها في الإعدادات.")
                else:
                    incoming = [str(v).strip() for v in br_raw[bc].dropna().tolist()]
                    store_brands = [str(r.iloc[0]).strip()
                                    for _, r in st.session_state.brands_df.iterrows()]

                    found, not_found = [], []
                    for brand in incoming:
                        matched = next(
                            (sb for sb in store_brands
                             if brand.lower() in sb.lower() or sb.lower() in brand.lower()),
                            None)
                        if matched:
                            found.append({"الماركة الواردة": brand,
                                          "مطابقة في مهووس": matched,
                                          "الحالة": "✅ موجودة"})
                        else:
                            not_found.append({"الماركة الواردة": brand,
                                              "مطابقة في مهووس": "—",
                                              "الحالة": "🆕 جديدة"})

                    total = len(incoming)
                    st.markdown(f"""
                    <div class="stats-bar">
                      <div class="stat-box"><div class="n">{total}</div><div class="lb">إجمالي الماركات</div></div>
                      <div class="stat-box"><div class="n">{len(found)}</div><div class="lb">موجودة لدينا</div></div>
                      <div class="stat-box"><div class="n">{len(not_found)}</div><div class="lb">جديدة (غير موجودة)</div></div>
                    </div>
                    """, unsafe_allow_html=True)

                    all_res = pd.DataFrame(found + not_found)
                    st.dataframe(all_res, use_container_width=True, height=400)

                    if not_found:
                        st.markdown("""<div class="sec-title"><div class="bar"></div>
                        <h3>الماركات الجديدة — غير موجودة في مهووس</h3></div>""",
                                    unsafe_allow_html=True)
                        st.dataframe(pd.DataFrame(not_found), use_container_width=True)

                    b1, b2 = st.columns(2)
                    with b1:
                        out = io.StringIO()
                        all_res.to_csv(out, index=False, encoding="utf-8-sig")
                        st.download_button("📥 تحميل نتائج الفحص CSV",
                            out.getvalue().encode("utf-8-sig"),
                            "brands_check.csv", "text/csv", use_container_width=True)
                    with b2:
                        wb_br = Workbook(); ws_br = wb_br.active
                        ws_br.title = "Brands Check"
                        hdrs = list(all_res.columns)
                        for i, h in enumerate(hdrs, 1):
                            c = ws_br.cell(1, i, h)
                            c.font = Font(bold=True); c.fill = PatternFill("solid", fgColor="E8D5B7")
                        for ri, (_, row) in enumerate(all_res.iterrows(), 2):
                            for ci, h in enumerate(hdrs, 1):
                                ws_br.cell(ri, ci, str(row.get(h,"")))
                        buf_br = io.BytesIO(); wb_br.save(buf_br); buf_br.seek(0)
                        st.download_button("📥 تحميل نتائج الفحص Excel",
                            buf_br.read(), "brands_check.xlsx",
                            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  PAGE 5 — SETTINGS                                              ║
# ╚══════════════════════════════════════════════════════════════════╝
elif st.session_state.page == "settings":

    tab1, tab2, tab3 = st.tabs(["🔑 مفاتيح API", "📚 قواعد البيانات", "ℹ️ دليل الاستخدام"])

    with tab1:
        st.markdown("#### Anthropic Claude API")
        ak = st.text_input("ANTHROPIC_API_KEY",
                           value=st.session_state.api_key, type="password",
                           help="console.anthropic.com → API Keys", key="set_ak")
        if ak != st.session_state.api_key:
            st.session_state.api_key = ak
            st.success("✅ تم حفظ مفتاح Claude")

        st.markdown("#### Google Custom Search (اختياري — لجلب الصور)")
        gk = st.text_input("GOOGLE_API_KEY",
                           value=st.session_state.google_api, type="password",
                           help="console.cloud.google.com → Custom Search API", key="set_gk")
        gc = st.text_input("GOOGLE_CSE_ID",
                           value=st.session_state.google_cse,
                           help="programmablesearchengine.google.com → Search Engine ID", key="set_gc")
        if gk != st.session_state.google_api or gc != st.session_state.google_cse:
            st.session_state.google_api = gk
            st.session_state.google_cse = gc
            st.success("✅ تم حفظ مفاتيح Google")

        st.markdown("""<div class="al-warn">
        <b>Railway:</b> أضف هذه المفاتيح كـ Variables في لوحة Railway وليس هنا.
        ما تُدخله هنا يُحفظ في الجلسة الحالية فقط ويُفقد عند إعادة التشغيل.
        </div>""", unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### ماركات مهووس")
            b_st = (f"محملة: **{len(st.session_state.brands_df)} ماركة**"
                    if st.session_state.brands_df is not None else "❌ غير محملة")
            st.info(b_st)
            bf = st.file_uploader("تحديث ملف الماركات", type=["csv","xlsx"], key="set_bf")
            if bf:
                st.session_state.brands_df = read_file(bf)
                st.success(f"✅ {len(st.session_state.brands_df)} ماركة")
            if st.session_state.brands_df is not None:
                with st.expander("معاينة"):
                    st.dataframe(st.session_state.brands_df.head(10), use_container_width=True)

        with c2:
            st.markdown("#### تصنيفات مهووس")
            c_st = (f"محملة: **{len(st.session_state.categories_df)} تصنيف**"
                    if st.session_state.categories_df is not None else "❌ غير محملة")
            st.info(c_st)
            cf = st.file_uploader("تحديث ملف التصنيفات", type=["csv","xlsx"], key="set_cf")
            if cf:
                st.session_state.categories_df = read_file(cf)
                st.success(f"✅ {len(st.session_state.categories_df)} تصنيف")
            if st.session_state.categories_df is not None:
                with st.expander("معاينة"):
                    st.dataframe(st.session_state.categories_df.head(10), use_container_width=True)

    with tab3:
        st.markdown("""
### دليل الاستخدام السريع

| الصفحة | الاستخدام |
|--------|-----------|
| 🛠️ المُعالج الشامل | ارفع أي ملف → عيّن الأعمدة → أكمل بـ AI → صدّر |
| 💰 مُحدّث الأسعار | ملف أسعار من أي مصدر → صدّر بتنسيق سلة |
| ➕ منتج سريع | أدخل اسم العطر فقط → AI يكمل الباقي |
| 🔍 مدقق الماركات | قائمة ماركات جديدة → يكتشف الجديد والموجود |

### أنواع الملفات المدعومة
- **Excel:** `.xlsx`, `.xlsm`, `.xls`
- **CSV:** UTF-8, UTF-8-BOM, Windows-1256, Latin-1

### تنسيق سلة المُصدَّر
- **ملف المنتجات:** 42 عمود، صفان في الرأس (بيانات المنتج + أسماء الأعمدة)
- **ملف SEO:** 5 أعمدة، صف رأس واحد
- **ملف الأسعار:** 9 أعمدة، صفان في الرأس
- جميع ملفات CSV بترميز `UTF-8-BOM` (utf-8-sig)

### مفاتيح API المطلوبة
```
ANTHROPIC_API_KEY  — لتوليد الأوصاف
GOOGLE_API_KEY     — لجلب الصور (اختياري)
GOOGLE_CSE_ID      — معرّف محرك البحث (اختياري)
```
        """)

# ╔══════════════════════════════════════════════════════════════════╗
# ║  FOOTER                                                         ║
# ╚══════════════════════════════════════════════════════════════════╝
st.markdown("""
<div class="mhw-footer">
  🌸 مهووس — مركز التحكم الشامل v4.0 &nbsp;|&nbsp;
  Streamlit · Anthropic Claude · Railway &nbsp;|&nbsp;
  عالمك العطري يبدأ من مهووس
</div>
""", unsafe_allow_html=True)
