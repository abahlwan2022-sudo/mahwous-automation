"""
╔══════════════════════════════════════════════════════════════════════════════╗
║   مهووس — مدير الملفات الذكي الشامل  v3.0                                 ║
║   Mahwous Smart File Manager — Full Edition                                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import numpy as np
import os, io, re, json, time
import requests
from datetime import datetime
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import anthropic

# ══════════════════════════════════════════════════════════════
# PAGE CONFIG
# ══════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="مهووس | مدير الملفات",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ══════════════════════════════════════════════════════════════
# GLOBAL CSS
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700;900&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], .stApp {
    font-family: 'Cairo', sans-serif !important;
    direction: rtl;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0e0d 0%, #1c1710 100%);
    border-left: 2px solid rgba(184,147,58,0.3);
}
section[data-testid="stSidebar"] * { color: #e8d5b7 !important; }
section[data-testid="stSidebar"] .stButton button {
    background: rgba(184,147,58,0.12) !important;
    border: 1px solid rgba(184,147,58,0.35) !important;
    color: #b8933a !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(184,147,58,0.25) !important;
}

/* ── Top Bar ── */
.top-bar {
    background: linear-gradient(135deg,#0f0e0d 0%,#1c1710 60%,#2a1f0e 100%);
    padding: 14px 24px; border-radius: 14px; margin-bottom: 18px;
    display: flex; align-items: center; gap: 16px;
    border: 1px solid rgba(184,147,58,0.35);
    box-shadow: 0 8px 32px rgba(0,0,0,0.25);
}
.top-bar .logo-circle {
    width:48px; height:48px; border-radius:50%;
    background: linear-gradient(135deg,#b8933a,#d4a843);
    display:flex; align-items:center; justify-content:center;
    font-size:22px; font-weight:900; color:#0f0e0d;
    box-shadow: 0 0 24px rgba(184,147,58,0.5);
    flex-shrink:0;
}
.top-bar h1 { color:#b8933a; font-size:1.6rem; margin:0; line-height:1.2; }
.top-bar p  { color:rgba(255,255,255,0.4); font-size:0.78rem; margin:0; }

/* ── Nav Pills ── */
.nav-container {
    display:flex; gap:8px; flex-wrap:wrap; margin-bottom:20px;
}
.nav-pill {
    padding:9px 20px; border-radius:30px; cursor:pointer;
    font-size:0.85rem; font-weight:700; border:none;
    transition:all 0.2s; white-space:nowrap;
}
.nav-pill.active {
    background:linear-gradient(135deg,#b8933a,#d4a843);
    color:#0f0e0d; box-shadow:0 4px 16px rgba(184,147,58,0.4);
}
.nav-pill.inactive {
    background:rgba(184,147,58,0.08);
    color:#7a6e68; border:1px solid rgba(184,147,58,0.2);
}
.nav-pill.inactive:hover {
    background:rgba(184,147,58,0.15); color:#0f0e0d;
}

/* ── Upload Zone ── */
.upload-zone {
    border:2px dashed rgba(184,147,58,0.4); border-radius:16px;
    padding:2.5rem; text-align:center;
    background:rgba(184,147,58,0.04);
    transition:all 0.2s;
}
.upload-zone:hover { border-color:#b8933a; background:rgba(184,147,58,0.08); }
.upload-icon { font-size:3rem; margin-bottom:0.5rem; }
.upload-title { font-size:1.1rem; font-weight:700; color:#0f0e0d; margin-bottom:0.25rem; }
.upload-sub   { font-size:0.82rem; color:#9a8e86; }

/* ── Section Header ── */
.sec-header {
    display:flex; align-items:center; gap:10px;
    margin:20px 0 12px;
}
.sec-header .bar {
    width:4px; height:22px; border-radius:2px;
    background:linear-gradient(180deg,#b8933a,#d4a843);
}
.sec-header h3 { margin:0; font-size:1rem; font-weight:700; color:#0f0e0d; }

/* ── Stat Card ── */
.stat-row { display:flex; gap:12px; flex-wrap:wrap; margin:12px 0; }
.stat-card {
    flex:1; min-width:120px;
    background:#fff; border:1px solid rgba(184,147,58,0.2);
    border-radius:12px; padding:14px 18px; text-align:center;
    box-shadow:0 2px 12px rgba(0,0,0,0.05);
}
.stat-card .n  { font-size:2rem; font-weight:900; color:#b8933a; line-height:1; }
.stat-card .lbl{ font-size:0.75rem; color:#7a6e68; margin-top:4px; }

/* ── Tool Button ── */
.tool-btn {
    display:inline-flex; align-items:center; gap:6px;
    padding:8px 16px; border-radius:8px; cursor:pointer;
    font-size:0.82rem; font-weight:700; border:none;
    transition:all 0.18s; white-space:nowrap;
}
.tool-btn.primary {
    background:linear-gradient(135deg,#0f0e0d,#2a1f0e);
    color:#b8933a; box-shadow:0 4px 14px rgba(15,14,13,0.2);
}
.tool-btn.gold {
    background:linear-gradient(135deg,#b8933a,#d4a843);
    color:#0f0e0d;
}
.tool-btn.outline {
    background:transparent; color:#b8933a;
    border:1.5px solid rgba(184,147,58,0.4);
}

/* ── Progress ── */
.proc-item {
    display:flex; align-items:center; gap:10px;
    padding:7px 12px; border-radius:8px; margin-bottom:4px;
    font-size:0.82rem;
}
.proc-item.ok  { background:#f0faf4; color:#2d7a4f; }
.proc-item.err { background:#fef2f2; color:#c62828; }
.proc-item.run { background:#fff8e1; color:#e65100; }

/* ── Tags ── */
.tag-ai    { background:#e8f5e9; color:#2d7a4f; padding:3px 10px; border-radius:20px; font-size:0.74rem; font-weight:700; }
.tag-img   { background:#e3f2fd; color:#1565c0; padding:3px 10px; border-radius:20px; font-size:0.74rem; font-weight:700; }
.tag-brand { background:#fce4ec; color:#880e4f; padding:3px 10px; border-radius:20px; font-size:0.74rem; font-weight:700; }
.tag-miss  { background:#fafafa; color:#9e9e9e; padding:3px 10px; border-radius:20px; font-size:0.74rem; }

/* ── Gold Divider ── */
.gdiv {
    height:1px; margin:20px 0;
    background:linear-gradient(90deg,transparent,rgba(184,147,58,0.4),transparent);
    border:none;
}

/* ── Alerts ── */
.alert-info    { background:#e3f2fd; border-right:4px solid #1976d2; border-radius:8px; padding:10px 14px; font-size:0.85rem; color:#0d47a1; }
.alert-success { background:#e8f5e9; border-right:4px solid #388e3c; border-radius:8px; padding:10px 14px; font-size:0.85rem; color:#1b5e20; }
.alert-warn    { background:#fff8e1; border-right:4px solid #f57f17; border-radius:8px; padding:10px 14px; font-size:0.85rem; color:#e65100; }

/* ── Data Editor override ── */
.stDataFrame, [data-testid="stDataFrame"] { direction: rtl; }

/* Streamlit button overrides */
.stButton > button {
    font-family:'Cairo',sans-serif !important;
    font-weight:600 !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# SALLA EXACT SCHEMAS
# ══════════════════════════════════════════════════════════════
SALLA_PRODUCT_COLS = [
    "No.", "النوع ", "أسم المنتج", "تصنيف المنتج", "صورة المنتج",
    "وصف صورة المنتج", "نوع المنتج", "سعر المنتج", "الوصف",
    "هل يتطلب شحن؟", "رمز المنتج sku", "سعر التكلفة", "السعر المخفض",
    "تاريخ بداية التخفيض", "تاريخ نهاية التخفيض", "اقصي كمية لكل عميل",
    "إخفاء خيار تحديد الكمية", "اضافة صورة عند الطلب", "الوزن", "وحدة الوزن",
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

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ── Key columns shown by default in the editor ──
EDITOR_DEFAULT_COLS = [
    "No.", "النوع ", "أسم المنتج", "الماركة", "تصنيف المنتج",
    "سعر المنتج", "رمز المنتج sku", "صورة المنتج",
    "وصف صورة المنتج", "حالة المنتج", "السعر المخفض",
]

# ══════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════
def _init():
    defs = {
        "page":           "manager",   # manager | new | seo | price | settings
        "brands_df":      None,
        "categories_df":  None,
        "api_key":        os.environ.get("ANTHROPIC_API_KEY",""),
        "google_api":     os.environ.get("GOOGLE_API_KEY",""),
        "google_cse":     os.environ.get("GOOGLE_CSE_ID",""),
        # File Manager state
        "fm_df":          None,        # active working DataFrame (all columns)
        "fm_seo_df":      None,        # SEO companion DataFrame
        "fm_filename":    "",
        "fm_col_map":     {},          # source col → salla col mapping
        "fm_log":         [],
        # New Product wizard
        "nw_rows":        [],          # pending new product rows
    }
    for k,v in defs.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Auto-load bundled reference data
    if st.session_state.brands_df is None:
        p = os.path.join(DATA_DIR,"brands.csv")
        if os.path.exists(p):
            try: st.session_state.brands_df = pd.read_csv(p,encoding="utf-8-sig")
            except: pass
    if st.session_state.categories_df is None:
        p = os.path.join(DATA_DIR,"categories.csv")
        if os.path.exists(p):
            try: st.session_state.categories_df = pd.read_csv(p,encoding="utf-8-sig")
            except: pass

_init()

# ══════════════════════════════════════════════════════════════
# UTILITIES
# ══════════════════════════════════════════════════════════════
def read_file(f, salla_format=False) -> pd.DataFrame:
    """Read CSV or Excel → clean DataFrame."""
    name = f.name.lower()
    hdr  = 1 if salla_format else 0
    try:
        if name.endswith((".xlsx",".xlsm",".xls")):
            df = pd.read_excel(f, header=hdr, dtype=str)
        else:
            for enc in ("utf-8-sig","utf-8","cp1256","latin-1"):
                try:
                    f.seek(0)
                    df = pd.read_csv(f,header=hdr,encoding=enc,dtype=str)
                    break
                except UnicodeDecodeError: continue
        df = df.dropna(how="all").reset_index(drop=True)
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"خطأ في قراءة الملف: {e}")
        return pd.DataFrame()

def ensure_salla_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure DataFrame has all Salla product columns."""
    for col in SALLA_PRODUCT_COLS:
        if col not in df.columns:
            df[col] = ""
    return df[SALLA_PRODUCT_COLS]

def match_brand(name: str) -> dict:
    bdf = st.session_state.brands_df
    if bdf is None or not name.strip(): return {"name":"","page_url":""}
    nl = name.lower()
    for _,row in bdf.iterrows():
        raw = str(row.iloc[0])
        for p in re.split(r"\s*\|\s*",raw):
            if p.strip().lower() and p.strip().lower() in nl:
                return {"name":raw,"page_url":str(row.get("(SEO Page URL) رابط صفحة العلامة التجارية","") or "")}
    return {"name":"","page_url":""}

def match_category(name:str, gender:str="") -> str:
    t = (name+" "+gender).lower()
    if any(w in t for w in ["رجال","للرجال","men","homme"]): return "العطور > عطور رجالية"
    if any(w in t for w in ["نساء","للنساء","women","femme"]): return "العطور > عطور نسائية"
    return "العطور > عطور للجنسين"

def to_slug(text:str)->str:
    ar={"ا":"a","أ":"a","إ":"e","آ":"a","ب":"b","ت":"t","ث":"th","ج":"j","ح":"h","خ":"kh","د":"d","ذ":"z","ر":"r","ز":"z","س":"s","ش":"sh","ص":"s","ض":"d","ط":"t","ظ":"z","ع":"a","غ":"gh","ف":"f","ق":"q","ك":"k","ل":"l","م":"m","ن":"n","ه":"h","و":"w","ي":"y","ى":"a","ة":"a","ء":"","ئ":"y","ؤ":"w"}
    o=""
    for c in str(text).lower():
        if c in ar: o+=ar[c]
        elif c.isascii() and c.isalnum(): o+=c
        elif c in " -_": o+="-"
    return re.sub(r"-+","-",o).strip("-") or "perfume"

def fetch_image(name:str,tester:bool=False)->str:
    k=st.session_state.google_api; cx=st.session_state.google_cse
    if not k or not cx: return ""
    try:
        q=name+(" tester box" if tester else " perfume bottle")
        r=requests.get("https://www.googleapis.com/customsearch/v1",
            params={"key":k,"cx":cx,"q":q,"searchType":"image","num":1,"imgSize":"large"},timeout=10)
        items=r.json().get("items",[])
        return items[0]["link"] if items else ""
    except: return ""

def gen_seo(name:str,brand:dict,size:str,tester:bool,gender:str)->dict:
    bname=brand.get("name","")
    parts=re.split(r"\s*\|\s*",bname); ben=parts[-1].strip() if len(parts)>1 else bname
    pref="تستر" if tester else "عطر"
    title=f"{pref} {name} {size} | {ben}".strip()
    desc=f"تسوق {pref} {name} {size} الأصلي من {bname}. عطر {gender} فاخر ثابت. أصلي 100% من مهووس."
    if len(desc)>160: desc=desc[:157]+"..."
    return {"url":to_slug(f"{ben}-{name}-{size}".replace("مل","ml")),
            "title":title,"desc":desc,
            "alt":f"زجاجة {pref} {name} {size} الأصلية"}

SYSTEM_PROMPT = """أنت خبير كتابة أوصاف عطور فاخرة تعمل لمتجر "مهووس" السعودي.

قواعد صارمة:
- ممنوع الرموز التعبيرية (Emojis) نهائياً
- التركيز دائماً: "أو دو بارفيوم"
- أسلوبك: راقٍ 40%، ودود 25%، رومانسي 20%، تسويقي 15%
- الطول: 1200-1500 كلمة
- **الإخراج HTML خالص فقط** — لا نص خارج HTML

هيكل الوصف الإلزامي:
<h2>[عطر/تستر] [الماركة] [الاسم] [التركيز] [الحجم] [للجنس]</h2>
<p>فقرة افتتاحية عاطفية، الكلمة المفتاحية في أول 50 كلمة، دعوة للشراء.</p>
<h3>تفاصيل المنتج</h3>
<ul><li><strong>الماركة:</strong></li><li><strong>الجنس:</strong></li><li><strong>العائلة العطرية:</strong></li><li><strong>الحجم:</strong></li><li><strong>التركيز:</strong> أو دو بارفيوم</li></ul>
<h3>رحلة العطر - الهرم العطري</h3>
<ul><li><strong>المقدمة:</strong></li><li><strong>القلب:</strong></li><li><strong>القاعدة:</strong></li></ul>
<h3>لماذا تختار هذا العطر؟</h3>
<ul><li><strong>الثبات:</strong></li><li><strong>التميز:</strong></li><li><strong>القيمة:</strong></li><li><strong>الجاذبية:</strong></li></ul>
<h3>متى وأين ترتديه؟</h3><p>...</p>
<h3>لمسة خبير من مهووس</h3><p>...</p>
<h3>الأسئلة الشائعة</h3>
<ul><li><strong>كم يدوم؟</strong></li><li><strong>هل يناسب اليومي؟</strong></li><li><strong>الفرق بين التستر والعادي؟</strong></li><li><strong>العائلة العطرية؟</strong></li><li><strong>يناسب الطقس الحار؟</strong></li><li><strong>مناسبات الارتداء؟</strong></li></ul>
<p><strong>عالمك العطري يبدأ من مهووس.</strong> أصلي 100% | شحن سريع داخل السعودية.</p>"""

def gen_desc(name:str,tester:bool,brand:dict,size:str,gender:str,conc:str)->str:
    key=st.session_state.api_key
    if not key: return "<p>⚠️ لم يتم ضبط مفتاح Anthropic API في الإعدادات</p>"
    try:
        client=anthropic.Anthropic(api_key=key)
        ptype="تستر" if tester else "عطر"
        blink=""
        if brand.get("page_url"):
            blink=f'— رابط: <a href="https://mahwous.com/{brand["page_url"]}">{brand["name"]}</a>'
        msg=client.messages.create(
            model="claude-opus-4-5", max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role":"user","content":
                f"اكتب وصفاً HTML كاملاً:\n"
                f"- النوع: {ptype}\n- الاسم: {name}\n"
                f"- الماركة: {brand.get('name','غير محدد')} {blink}\n"
                f"- الحجم: {size}\n- التركيز: {conc}\n- الجنس: {gender}\n"
                f"أعد HTML خالصاً فقط."}])
        return msg.content[0].text
    except Exception as e:
        return f"<p>خطأ في توليد الوصف: {e}</p>"

# ══════════════════════════════════════════════════════════════
# EXPORT FUNCTIONS
# ══════════════════════════════════════════════════════════════
def export_product_xlsx(df:pd.DataFrame)->bytes:
    wb=Workbook(); ws=wb.active; ws.title="Salla Products Template Sheet"
    GOLD="B8933A"; DARK="0F0E0D"; LGOLD="E8D5B7"
    ws.cell(1,1,"بيانات المنتج")
    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(SALLA_PRODUCT_COLS))
    c=ws.cell(1,1)
    c.font=Font(bold=True,color="FFFFFF",name="Cairo",size=11)
    c.fill=PatternFill("solid",fgColor=DARK)
    c.alignment=Alignment(horizontal="center",vertical="center")
    ws.row_dimensions[1].height=26
    for i,col in enumerate(SALLA_PRODUCT_COLS,1):
        c=ws.cell(2,i,col)
        c.font=Font(bold=True,color=DARK,name="Cairo",size=8)
        c.fill=PatternFill("solid",fgColor=LGOLD)
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True,reading_order=2)
        c.border=Border(bottom=Side(style="thin",color=GOLD))
    ws.row_dimensions[2].height=30
    for ri,(_, row) in enumerate(df.iterrows(),3):
        for ci,col in enumerate(SALLA_PRODUCT_COLS,1):
            v=str(row.get(col,"") if pd.notna(row.get(col,"")) else "")
            c=ws.cell(ri,ci,v)
            c.alignment=Alignment(horizontal="right",vertical="top",
                                   wrap_text=(col=="الوصف"),reading_order=2)
            if ri%2==0: c.fill=PatternFill("solid",fgColor="FAFAF8")
        ws.row_dimensions[ri].height=18
    WIDTHS={"أسم المنتج":45,"الوصف":55,"تصنيف المنتج":38,
            "صورة المنتج":48,"الماركة":24,"No.":13}
    for i,col in enumerate(SALLA_PRODUCT_COLS,1):
        ws.column_dimensions[get_column_letter(i)].width=WIDTHS.get(col,14)
    ws.freeze_panes="A3"
    b=io.BytesIO(); wb.save(b); b.seek(0); return b.read()

def export_product_csv(df:pd.DataFrame)->bytes:
    out=io.StringIO()
    out.write("بيانات المنتج"+","*(len(SALLA_PRODUCT_COLS)-1)+"\n")
    out.write(",".join(SALLA_PRODUCT_COLS)+"\n")
    for _,row in df.iterrows():
        vals=[]
        for c in SALLA_PRODUCT_COLS:
            v=str(row.get(c,"") if pd.notna(row.get(c,"")) else "")
            vals.append(f'"{v}"' if any(x in v for x in [",","\n",'"']) else v)
        out.write(",".join(vals)+"\n")
    return out.getvalue().encode("utf-8-sig")

def export_seo_xlsx(df:pd.DataFrame)->bytes:
    wb=Workbook(); ws=wb.active; ws.title="Salla Product Seo Sheet"
    for i,col in enumerate(SALLA_SEO_COLS,1):
        c=ws.cell(1,i,col)
        c.font=Font(bold=True,color="FFFFFF",name="Cairo",size=9)
        c.fill=PatternFill("solid",fgColor="1A1510")
        c.alignment=Alignment(horizontal="center",vertical="center",wrap_text=True,reading_order=2)
    ws.row_dimensions[1].height=28
    for ri,(_, row) in enumerate(df.iterrows(),2):
        for ci,col in enumerate(SALLA_SEO_COLS,1):
            v=str(row.get(col,"") if pd.notna(row.get(col,"")) else "")
            c=ws.cell(ri,ci,v)
            c.alignment=Alignment(horizontal="right",vertical="top",wrap_text=True,reading_order=2)
            if ri%2==0: c.fill=PatternFill("solid",fgColor="FFF8E1")
        ws.row_dimensions[ri].height=18
    WIDTHS={"اسم المنتج (غير قابل للتعديل)":50,
            "وصف صفحة المنتج (SEO Page Description)":65,
            "عنوان صفحة المنتج (SEO Page Title)":52}
    for i,col in enumerate(SALLA_SEO_COLS,1):
        ws.column_dimensions[get_column_letter(i)].width=WIDTHS.get(col,22)
    ws.freeze_panes="A2"
    b=io.BytesIO(); wb.save(b); b.seek(0); return b.read()

def export_seo_csv(df:pd.DataFrame)->bytes:
    out=io.StringIO()
    out.write(",".join(SALLA_SEO_COLS)+"\n")
    for _,row in df.iterrows():
        vals=[]
        for c in SALLA_SEO_COLS:
            v=str(row.get(c,"") if pd.notna(row.get(c,"")) else "")
            vals.append(f'"{v}"' if any(x in v for x in [",","\n"]) else v)
        out.write(",".join(vals)+"\n")
    return out.getvalue().encode("utf-8-sig")

# ══════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:16px 0 8px">
      <div style="font-size:2.2rem">🌸</div>
      <div style="color:#b8933a;font-size:1.2rem;font-weight:900">مهووس</div>
      <div style="color:rgba(255,255,255,0.35);font-size:0.72rem">Mahwous v3.0</div>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    # Navigation
    pages = [
        ("📁","مدير الملفات","manager"),
        ("➕","منتج جديد سريع","new"),
        ("🔍","دمج SEO","seo"),
        ("💰","تحديث الأسعار","price"),
        ("⚙️","الإعدادات","settings"),
    ]
    for icon,label,key in pages:
        is_active = st.session_state.page == key
        if st.button(f"{icon}  {label}", use_container_width=True,
                     type="primary" if is_active else "secondary",
                     key=f"nav_{key}"):
            st.session_state.page = key
            st.rerun()

    st.divider()
    # Status indicators
    bok = st.session_state.brands_df is not None
    cok = st.session_state.categories_df is not None
    aok = bool(st.session_state.api_key)
    st.markdown(f"""
    <div style="font-size:0.78rem;padding:4px 0">
      {'✅' if bok else '❌'} الماركات: {len(st.session_state.brands_df) if bok else 'غير محملة'}
    </div>
    <div style="font-size:0.78rem;padding:4px 0">
      {'✅' if cok else '❌'} التصنيفات: {len(st.session_state.categories_df) if cok else 'غير محملة'}
    </div>
    <div style="font-size:0.78rem;padding:4px 0">
      {'✅' if aok else '❌'} Claude API: {'متصل' if aok else 'غير مضبوط'}
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.fm_df is not None:
        st.divider()
        st.markdown(f"""
        <div style="background:rgba(184,147,58,0.12);border-radius:8px;padding:10px;font-size:0.8rem">
          <div style="font-weight:700;margin-bottom:4px">📄 الملف المفتوح</div>
          <div style="color:#b8933a;font-size:0.85rem">{st.session_state.fm_filename}</div>
          <div style="color:rgba(255,255,255,0.5)">
            {len(st.session_state.fm_df)} صف | {len(st.session_state.fm_df.columns)} عمود
          </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ إغلاق الملف", use_container_width=True):
            st.session_state.fm_df = None
            st.session_state.fm_seo_df = None
            st.session_state.fm_filename = ""
            st.rerun()

# ══════════════════════════════════════════════════════════════
# TOP BAR
# ══════════════════════════════════════════════════════════════
page_titles = {
    "manager":  ("📁 مدير الملفات الشامل", "ارفع أي ملف، عدّل، أكمل بالذكاء الاصطناعي، وصدّر لسلة"),
    "new":      ("➕ منتج جديد سريع", "أعطِ الاسم والذكاء الاصطناعي يكمل الباقي"),
    "seo":      ("🔍 دمج بيانات SEO", "اربط ملف منتجات سلة بملف SEO"),
    "price":    ("💰 تحديث الأسعار", "تحديث الأسعار من أي ملف"),
    "settings": ("⚙️ الإعدادات", "مفاتيح API وقواعد البيانات المرجعية"),
}
t,s = page_titles.get(st.session_state.page,("مهووس",""))
st.markdown(f"""
<div class="top-bar">
  <div class="logo-circle">م</div>
  <div><h1>{t}</h1><p>{s}</p></div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ████  PAGE: FILE MANAGER  ████████████████████████████████████
# ══════════════════════════════════════════════════════════════
if st.session_state.page == "manager":

    # ── UPLOAD SECTION (always visible at top) ────────────────
    st.markdown("""
    <div class="sec-header"><div class="bar"></div><h3>رفع الملف</h3></div>
    """, unsafe_allow_html=True)

    up_col1, up_col2 = st.columns([3,1])
    with up_col1:
        uploaded = st.file_uploader(
            "ارفع أي ملف Excel أو CSV (من أي مصدر — ملفات سلة، ملفات موردين، قوائم أسماء...)",
            type=["csv","xlsx","xls","xlsm"],
            label_visibility="collapsed",
            key="fm_uploader"
        )
    with up_col2:
        salla_fmt = st.checkbox("ملف سلة (صفان في الرأس)", value=False, key="fm_salla_fmt")

    if uploaded:
        df_raw = read_file(uploaded, salla_format=salla_fmt)
        if not df_raw.empty:
            st.session_state.fm_filename = uploaded.name
            # If columns match Salla format already, use as-is; else keep as raw
            st.session_state.fm_df = df_raw
            st.session_state.fm_col_map = {}
            st.rerun()

    # ── COLUMN MAPPING (if file loaded but not yet mapped) ────
    if st.session_state.fm_df is not None:
        df = st.session_state.fm_df

        # Check if it's already a salla-format file
        has_salla_cols = sum(1 for c in SALLA_PRODUCT_COLS if c in df.columns)
        is_salla = has_salla_cols >= 5

        if not is_salla and not st.session_state.fm_col_map:
            st.markdown("""<hr class="gdiv">
            <div class="sec-header"><div class="bar"></div><h3>تعيين الأعمدة — خبرني أين هو كل عمود</h3></div>
            """, unsafe_allow_html=True)
            st.markdown(f"""
            <div class="alert-info">
              وجدت <b>{len(df.columns)}</b> عمود و <b>{len(df)}</b> صف.
              حدد أي عمود يمثل كل حقل:
            </div>
            """, unsafe_allow_html=True)

            with st.expander("👀 معاينة الملف الأصلي", expanded=True):
                st.dataframe(df.head(8), use_container_width=True)

            cols_opts = ["— لا يوجد —"] + list(df.columns)

            def best_guess(keywords):
                for kw in keywords:
                    for c in df.columns:
                        if kw.lower() in c.lower(): return c
                return "— لا يوجد —"

            c1,c2,c3 = st.columns(3)
            with c1:
                col_name  = st.selectbox("اسم المنتج / العطر *", cols_opts,
                    index=cols_opts.index(best_guess(["اسم","name","منتج","عطر"])),key="cm_name")
                col_price = st.selectbox("السعر",cols_opts,
                    index=cols_opts.index(best_guess(["سعر","price"])),key="cm_price")
            with c2:
                col_sku   = st.selectbox("رمز SKU",cols_opts,
                    index=cols_opts.index(best_guess(["sku","رمز","barcode"])),key="cm_sku")
                col_size  = st.selectbox("الحجم",cols_opts,
                    index=cols_opts.index(best_guess(["حجم","size","مل","ml"])),key="cm_size")
            with c3:
                col_img   = st.selectbox("رابط الصورة",cols_opts,
                    index=cols_opts.index(best_guess(["صورة","image","img","photo","url"])),key="cm_img")
                col_desc  = st.selectbox("الوصف",cols_opts,
                    index=cols_opts.index(best_guess(["وصف","desc"])),key="cm_desc")

            c4,c5,c6 = st.columns(3)
            with c4:
                col_gender= st.selectbox("الجنس",cols_opts,
                    index=cols_opts.index(best_guess(["جنس","gender","sex"])),key="cm_gender")
            with c5:
                col_brand = st.selectbox("الماركة",cols_opts,
                    index=cols_opts.index(best_guess(["ماركة","brand","علامة"])),key="cm_brand")
            with c6:
                col_tester= st.selectbox("تستر؟",cols_opts,
                    index=cols_opts.index(best_guess(["تستر","tester"])),key="cm_tester")

            st.markdown("**الإعدادات الافتراضية:**")
            d1,d2,d3,d4 = st.columns(4)
            with d1: dft_gender = st.selectbox("الجنس الافتراضي",["للجنسين","للرجال","للنساء"],key="dg2")
            with d2: dft_size   = st.text_input("الحجم الافتراضي","100 مل",key="ds2")
            with d3: dft_conc   = st.selectbox("التركيز الافتراضي",["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"],key="dc2")
            with d4: dft_type   = st.selectbox("النوع الافتراضي",["عطر عادي","تستر"],key="dt2")

            if col_name != "— لا يوجد —":
                if st.button("✅ تأكيد تعيين الأعمدة وتحويل الملف", type="primary", key="confirm_map"):
                    # Build Salla-format DataFrame
                    rows = []
                    for _,row in df.iterrows():
                        def gv(c): return str(row.get(c,"") if c!="— لا يوجد —" and c in df.columns else "")
                        name = gv(col_name).strip()
                        if not name or name.lower() in ("nan","none",""): continue

                        price  = gv(col_price)
                        sku    = gv(col_sku)
                        size   = gv(col_size).strip() or dft_size
                        img    = gv(col_img)
                        desc   = gv(col_desc)
                        gender = gv(col_gender).strip() or dft_gender
                        brand_name = gv(col_brand)
                        tester_v   = gv(col_tester)
                        is_test = any(w in tester_v.lower() for w in ["تستر","tester","yes","نعم"]) if col_tester!="— لا يوجد —" else (dft_type=="تستر")

                        brand = match_brand(name) if not brand_name else {"name":brand_name,"page_url":""}
                        cat   = match_category(name,gender)
                        seo   = gen_seo(name,brand,size,is_test,gender)

                        nr = {c:"" for c in SALLA_PRODUCT_COLS}
                        nr["النوع "]                  = "منتج"
                        nr["أسم المنتج"]              = name
                        nr["تصنيف المنتج"]            = cat
                        nr["صورة المنتج"]             = img
                        nr["وصف صورة المنتج"]         = seo["alt"]
                        nr["نوع المنتج"]              = "منتج جاهز"
                        nr["سعر المنتج"]              = price
                        nr["الوصف"]                   = desc
                        nr["هل يتطلب شحن؟"]          = "نعم"
                        nr["رمز المنتج sku"]          = sku
                        nr["الوزن"]                   = "0.2"
                        nr["وحدة الوزن"]              = "kg"
                        nr["حالة المنتج"]             = "مرئي"
                        nr["الماركة"]                 = brand.get("name","")
                        nr["خاضع للضريبة ؟"]         = "نعم"
                        nr["اقصي كمية لكل عميل"]     = "0"
                        nr["إخفاء خيار تحديد الكمية"]= "0"
                        nr["اضافة صورة عند الطلب"]   = "0"
                        rows.append(nr)

                    st.session_state.fm_df = pd.DataFrame(rows)
                    st.session_state.fm_col_map = {"mapped": True}
                    st.success(f"✅ تم تحويل {len(rows)} صف إلى تنسيق سلة!")
                    st.rerun()
        else:
            # Already Salla format or already mapped
            if is_salla:
                st.session_state.fm_df = ensure_salla_cols(df)
                st.session_state.fm_col_map = {"mapped": True}

    # ── MAIN EDITOR (if file is ready in Salla format) ────────
    if st.session_state.fm_df is not None and (
            st.session_state.fm_col_map.get("mapped") or
            sum(1 for c in SALLA_PRODUCT_COLS if c in st.session_state.fm_df.columns) >= 5):

        df = st.session_state.fm_df

        # ── Stats bar ──────────────────────────────────────────
        n_total = len(df)
        n_desc  = int((df.get("الوصف", pd.Series(dtype=str)).fillna("").str.strip() != "").sum())
        n_img   = int((df.get("صورة المنتج", pd.Series(dtype=str)).fillna("").str.startswith("http").sum()))
        n_brand = int((df.get("الماركة", pd.Series(dtype=str)).fillna("").str.strip() != "").sum())
        n_price = int((df.get("سعر المنتج", pd.Series(dtype=str)).fillna("").str.strip() != "").sum())

        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-card"><div class="n">{n_total}</div><div class="lbl">إجمالي المنتجات</div></div>
          <div class="stat-card"><div class="n">{n_desc}</div><div class="lbl">مع وصف AI</div></div>
          <div class="stat-card"><div class="n">{n_img}</div><div class="lbl">مع صورة</div></div>
          <div class="stat-card"><div class="n">{n_brand}</div><div class="lbl">مع ماركة</div></div>
          <div class="stat-card"><div class="n">{n_price}</div><div class="lbl">مع سعر</div></div>
        </div>
        """, unsafe_allow_html=True)

        # ── TOOLBOX ────────────────────────────────────────────
        st.markdown("""<hr class="gdiv">
        <div class="sec-header"><div class="bar"></div><h3>أدوات المعالجة</h3></div>
        """, unsafe_allow_html=True)

        tool_tabs = st.tabs([
            "🤖 توليد الأوصاف",
            "🖼 جلب الصور",
            "🏷 الماركات والتصنيفات",
            "➕ إضافة منتج جديد",
            "🔁 عمليات مجمّعة",
        ])

        # ── Tool: AI Descriptions ──────────────────────────────
        with tool_tabs[0]:
            st.markdown("**توليد الوصف بالذكاء الاصطناعي (Claude)**")
            scope_d = st.radio("نطاق التوليد", [
                "الصفوف التي ليس لها وصف فقط",
                "صف محدد برقمه",
                "كل الصفوف (يستغرق وقتاً)",
            ], horizontal=True, key="scope_d")

            d1,d2,d3 = st.columns(3)
            with d1: dft_c = st.selectbox("التركيز",["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"],key="desc_conc")
            with d2: dft_g = st.selectbox("الجنس الافتراضي",["للجنسين","للرجال","للنساء"],key="desc_gender")
            with d3: dft_s = st.text_input("الحجم الافتراضي","100 مل",key="desc_size")

            if scope_d == "صف محدد برقمه":
                row_idx = st.number_input("رقم الصف (يبدأ من 0)",0,max(0,len(df)-1),0,key="desc_row_idx")

            if st.button("🚀 توليد الأوصاف الآن", type="primary", key="gen_desc_btn"):
                if not st.session_state.api_key:
                    st.error("أضف مفتاح Anthropic API في الإعدادات أولاً")
                else:
                    indices = []
                    if scope_d.startswith("الصفوف التي"):
                        indices = [i for i,r in df.iterrows() if not str(r.get("الوصف","")).strip()]
                    elif scope_d.startswith("صف محدد"):
                        indices = [row_idx]
                    else:
                        indices = list(range(len(df)))

                    if not indices:
                        st.info("لا توجد صفوف تحتاج وصفاً.")
                    else:
                        prog=st.progress(0); stat=st.empty()
                        for n,i in enumerate(indices):
                            row=df.iloc[i]
                            name=str(row.get("أسم المنتج","")).strip()
                            if not name: continue
                            stat.info(f"⏳ ({n+1}/{len(indices)}) {name}")
                            is_t=any(w in name.lower() for w in ["تستر","tester"])
                            size_m=re.search(r"\d+\s*مل|\d+\s*ml",name,re.I)
                            size=size_m.group() if size_m else dft_s
                            brand=match_brand(name)
                            gender=dft_g
                            d=gen_desc(name,is_t,brand,size,gender,dft_c)
                            df.at[i,"الوصف"]=d
                            if not df.at[i,"الماركة"]: df.at[i,"الماركة"]=brand.get("name","")
                            prog.progress(int((n+1)/len(indices)*100))
                        st.session_state.fm_df=df
                        stat.success(f"✅ تم توليد {len(indices)} وصف!")
                        st.rerun()

        # ── Tool: Image Fetching ───────────────────────────────
        with tool_tabs[1]:
            st.markdown("**جلب الصور عبر Google Custom Search API**")
            if not (st.session_state.google_api and st.session_state.google_cse):
                st.warning("أضف Google API Key و CSE ID في الإعدادات")
            scope_i = st.radio("نطاق جلب الصور",[
                "الصفوف التي ليس لها صورة فقط",
                "صف محدد برقمه",
                "كل الصفوف",
            ], horizontal=True, key="scope_i")
            if scope_i=="صف محدد برقمه":
                img_row = st.number_input("رقم الصف",0,max(0,len(df)-1),0,key="img_row")
            add_tester_kw = st.checkbox("إضافة 'tester' للبحث إذا كان المنتج تستراً",value=True)

            if st.button("🖼 جلب الصور الآن",type="primary",key="fetch_img_btn"):
                indices=[]
                if scope_i.startswith("الصفوف التي"):
                    indices=[i for i,r in df.iterrows() if not str(r.get("صورة المنتج","")).startswith("http")]
                elif scope_i.startswith("صف محدد"):
                    indices=[img_row]
                else:
                    indices=list(range(len(df)))

                if not indices: st.info("لا توجد صفوف تحتاج صورة.")
                else:
                    prog=st.progress(0); stat=st.empty()
                    fetched=0
                    for n,i in enumerate(indices):
                        row=df.iloc[i]
                        name=str(row.get("أسم المنتج","")).strip()
                        if not name: continue
                        stat.info(f"🖼 ({n+1}/{len(indices)}) {name}")
                        is_t = add_tester_kw and any(w in name.lower() for w in ["تستر","tester"])
                        url=fetch_image(name,is_t)
                        if url: df.at[i,"صورة المنتج"]=url; fetched+=1
                        # Update alt text
                        seo=gen_seo(name,match_brand(name),"",is_t,"للجنسين")
                        df.at[i,"وصف صورة المنتج"]=seo["alt"]
                        prog.progress(int((n+1)/len(indices)*100))
                    st.session_state.fm_df=df
                    stat.success(f"✅ تم جلب {fetched} صورة من {len(indices)} صف")
                    st.rerun()

            # Manual image URL
            st.divider()
            st.markdown("**إضافة رابط صورة يدوياً لصف محدد:**")
            m1,m2,m3=st.columns([1,3,1])
            with m1: man_row=st.number_input("رقم الصف",0,max(0,len(df)-1),0,key="man_row")
            with m2: man_url=st.text_input("رابط الصورة",placeholder="https://...",key="man_url")
            with m3:
                st.markdown("<br>",unsafe_allow_html=True)
                if st.button("حفظ",key="save_man_img"):
                    if man_url.startswith("http"):
                        df.at[man_row,"صورة المنتج"]=man_url
                        st.session_state.fm_df=df
                        st.success("✅ تم حفظ الصورة")
                        st.rerun()

        # ── Tool: Brands & Categories ──────────────────────────
        with tool_tabs[2]:
            st.markdown("**تعيين الماركات والتصنيفات**")
            scope_b=st.radio("نطاق العملية",[
                "الصفوف التي ليس لها ماركة/تصنيف",
                "كل الصفوف (يُعيد التعيين)",
            ], horizontal=True, key="scope_b")

            if st.button("🏷 تعيين الآن",type="primary",key="assign_brand_btn"):
                indices = [i for i,r in df.iterrows()
                           if not str(r.get("الماركة","")).strip()] if scope_b.startswith("الصفوف") \
                           else list(range(len(df)))
                for i in indices:
                    row=df.iloc[i]
                    name=str(row.get("أسم المنتج","")).strip()
                    if not name: continue
                    brand=match_brand(name)
                    cat=match_category(name,str(row.get("وصف صورة المنتج","")))
                    if brand.get("name"): df.at[i,"الماركة"]=brand["name"]
                    if not str(row.get("تصنيف المنتج","")).strip(): df.at[i,"تصنيف المنتج"]=cat
                st.session_state.fm_df=df
                st.success(f"✅ تم تعيين الماركات والتصنيفات لـ {len(indices)} صف")
                st.rerun()

            st.divider()
            # Manual override for a row
            st.markdown("**تعديل يدوي لصف محدد:**")
            b1,b2,b3=st.columns(3)
            with b1: brow_i=st.number_input("رقم الصف",0,max(0,len(df)-1),0,key="brow_i")
            brands_list = ["— اختر —"] + (
                [str(r.iloc[0]) for _,r in st.session_state.brands_df.iterrows()]
                if st.session_state.brands_df is not None else []
            )
            cats_list = ["— اختر —"] + (
                [str(r.get("التصنيفات","")) for _,r in st.session_state.categories_df.iterrows()]
                if st.session_state.categories_df is not None else []
            )
            with b2: sel_brand=st.selectbox("الماركة",brands_list,key="sel_brand")
            with b3: sel_cat=st.selectbox("التصنيف",cats_list,key="sel_cat")
            if st.button("تطبيق على الصف",key="apply_brand"):
                if sel_brand!="— اختر —": df.at[brow_i,"الماركة"]=sel_brand
                if sel_cat!="— اختر —":
                    # Build full category path
                    cat_df = st.session_state.categories_df
                    row_c  = cat_df[cat_df["التصنيفات"]==sel_cat].iloc[0] if cat_df is not None and len(cat_df[cat_df["التصنيفات"]==sel_cat])>0 else None
                    if row_c is not None:
                        parent = str(row_c.get("التصنيف الاساسي",""))
                        path   = f"{parent} > {sel_cat}" if parent and parent.strip() else sel_cat
                    else:
                        path = sel_cat
                    df.at[brow_i,"تصنيف المنتج"]=path
                st.session_state.fm_df=df
                st.success("✅ تم التطبيق")
                st.rerun()

        # ── Tool: Add New Product Row ──────────────────────────
        with tool_tabs[3]:
            st.markdown("**أضف منتجاً جديداً — أدخل الاسم وسيكمل النظام الباقي**")
            np1,np2,np3,np4 = st.columns(4)
            with np1: new_name   = st.text_input("اسم العطر *",placeholder="مثال: ديور سوفاج 100 مل",key="new_name")
            with np2: new_gender = st.selectbox("الجنس",["للجنسين","للرجال","للنساء"],key="new_gender")
            with np3: new_size   = st.text_input("الحجم","100 مل",key="new_size")
            with np4: new_conc   = st.selectbox("التركيز",["أو دو بارفيوم","أو دو كولون","أو دو تواليت"],key="new_conc")

            np5,np6,np7,np8 = st.columns(4)
            with np5: new_price = st.text_input("السعر",key="new_price")
            with np6: new_sku   = st.text_input("SKU",key="new_sku")
            with np7: new_img   = st.text_input("رابط الصورة (اختياري)",key="new_img")
            with np8: new_type  = st.selectbox("النوع",["عطر عادي","تستر"],key="new_type")

            n_opts = st.columns(3)
            with n_opts[0]: do_desc  = st.checkbox("🤖 توليد وصف AI",value=True,key="do_desc_new")
            with n_opts[1]: do_img   = st.checkbox("🖼 جلب صورة تلقائياً",value=False,key="do_img_new")
            with n_opts[2]: do_seo   = st.checkbox("🔍 توليد SEO",value=True,key="do_seo_new")

            if st.button("➕ إضافة المنتج",type="primary",key="add_product_btn"):
                if not new_name.strip():
                    st.error("أدخل اسم العطر")
                else:
                    with st.spinner("جاري معالجة المنتج..."):
                        is_t    = new_type=="تستر"
                        brand   = match_brand(new_name)
                        cat     = match_category(new_name,new_gender)
                        seo     = gen_seo(new_name,brand,new_size,is_t,new_gender)
                        img_url = new_img or (fetch_image(new_name,is_t) if do_img else "")
                        desc    = gen_desc(new_name,is_t,brand,new_size,new_gender,new_conc) if do_desc else ""

                        nr = {c:"" for c in SALLA_PRODUCT_COLS}
                        nr["النوع "]                   = "منتج"
                        nr["أسم المنتج"]               = new_name
                        nr["تصنيف المنتج"]             = cat
                        nr["صورة المنتج"]              = img_url
                        nr["وصف صورة المنتج"]          = seo["alt"]
                        nr["نوع المنتج"]               = "منتج جاهز"
                        nr["سعر المنتج"]               = new_price
                        nr["الوصف"]                    = desc
                        nr["هل يتطلب شحن؟"]           = "نعم"
                        nr["رمز المنتج sku"]           = new_sku
                        nr["الوزن"]                    = "0.2"
                        nr["وحدة الوزن"]               = "kg"
                        nr["حالة المنتج"]              = "مرئي"
                        nr["الماركة"]                  = brand.get("name","")
                        nr["خاضع للضريبة ؟"]          = "نعم"
                        nr["اقصي كمية لكل عميل"]      = "0"
                        nr["إخفاء خيار تحديد الكمية"] = "0"
                        nr["اضافة صورة عند الطلب"]    = "0"

                        new_row_df = pd.DataFrame([nr])
                        st.session_state.fm_df = pd.concat(
                            [df, new_row_df], ignore_index=True
                        )

                        # Update SEO df
                        seo_row = {
                            "No. (غير قابل للتعديل)": "",
                            "اسم المنتج (غير قابل للتعديل)": new_name,
                            "رابط مخصص للمنتج (SEO Page URL)": seo["url"],
                            "عنوان صفحة المنتج (SEO Page Title)": seo["title"],
                            "وصف صفحة المنتج (SEO Page Description)": seo["desc"],
                        }
                        prev_seo = st.session_state.fm_seo_df or pd.DataFrame(columns=SALLA_SEO_COLS)
                        st.session_state.fm_seo_df = pd.concat(
                            [prev_seo, pd.DataFrame([seo_row])], ignore_index=True
                        )
                        st.success(f"✅ تمت إضافة: **{new_name}**")
                        st.rerun()

        # ── Tool: Bulk Operations ──────────────────────────────
        with tool_tabs[4]:
            st.markdown("**عمليات مجمّعة على كل الصفوف**")
            b_ops = st.multiselect("اختر العمليات المطلوبة:", [
                "🏷 تعيين الماركات الفارغة",
                "📂 تعيين التصنيفات الفارغة",
                "🔍 توليد SEO للكل",
                "🔤 توليد Alt Text",
                "📋 تعيين القيم الثابتة (نوع، شحن، ضريبة)",
            ], key="bulk_ops")

            if st.button("⚡ تنفيذ العمليات المختارة",type="primary",key="bulk_run"):
                prog=st.progress(0); stat=st.empty()
                seo_rows=[]
                for i,(idx,row) in enumerate(df.iterrows()):
                    prog.progress(int((i+1)/len(df)*100))
                    name=str(row.get("أسم المنتج","")).strip()
                    if not name: continue
                    brand=match_brand(name)
                    is_t=any(w in name.lower() for w in ["تستر","tester"])
                    size_m=re.search(r"\d+\s*مل|\d+\s*ml",name,re.I)
                    size=size_m.group() if size_m else "100 مل"
                    gender="للنساء" if any(w in name for w in ["نسائ","women"]) else \
                           "للرجال" if any(w in name for w in ["رجال","men"]) else "للجنسين"
                    seo=gen_seo(name,brand,size,is_t,gender)
                    if "🏷 تعيين الماركات الفارغة" in b_ops and not str(row.get("الماركة","")).strip():
                        df.at[idx,"الماركة"]=brand.get("name","")
                    if "📂 تعيين التصنيفات الفارغة" in b_ops and not str(row.get("تصنيف المنتج","")).strip():
                        df.at[idx,"تصنيف المنتج"]=match_category(name,gender)
                    if "🔤 توليد Alt Text" in b_ops:
                        df.at[idx,"وصف صورة المنتج"]=seo["alt"]
                    if "📋 تعيين القيم الثابتة (نوع، شحن، ضريبة)" in b_ops:
                        df.at[idx,"النوع "]="منتج"
                        df.at[idx,"نوع المنتج"]="منتج جاهز"
                        df.at[idx,"هل يتطلب شحن؟"]="نعم"
                        df.at[idx,"خاضع للضريبة ؟"]="نعم"
                    if "🔍 توليد SEO للكل" in b_ops:
                        seo_rows.append({
                            "No. (غير قابل للتعديل)":           str(row.get("No.","") or ""),
                            "اسم المنتج (غير قابل للتعديل)":    name,
                            "رابط مخصص للمنتج (SEO Page URL)":  seo["url"],
                            "عنوان صفحة المنتج (SEO Page Title)":seo["title"],
                            "وصف صفحة المنتج (SEO Page Description)":seo["desc"],
                        })
                st.session_state.fm_df=df
                if seo_rows:
                    st.session_state.fm_seo_df=pd.DataFrame(seo_rows)
                stat.success("✅ تمت العمليات المجمّعة!")
                st.rerun()

        # ── EDITABLE GRID ──────────────────────────────────────
        st.markdown("""<hr class="gdiv">
        <div class="sec-header"><div class="bar"></div><h3>الجدول التفاعلي — عدّل أي خلية مباشرةً</h3></div>
        """, unsafe_allow_html=True)

        # Column selector
        all_cols = list(df.columns)
        show_cols_default = [c for c in EDITOR_DEFAULT_COLS if c in all_cols]
        show_cols = st.multiselect(
            "الأعمدة المعروضة في الجدول:",
            options=all_cols,
            default=show_cols_default,
            key="show_cols"
        )

        if not show_cols:
            show_cols = show_cols_default or all_cols[:8]

        edited_df = st.data_editor(
            df[show_cols].fillna(""),
            use_container_width=True,
            num_rows="dynamic",
            height=450,
            key="main_editor"
        )
        # Write edits back to full df
        for c in show_cols:
            df[c] = edited_df[c]
        st.session_state.fm_df = df

        # ── Description editor (separate) ──────────────────────
        with st.expander("📝 تعديل الأوصاف (HTML) — عرض منتج واحد"):
            sel_prod = st.selectbox(
                "اختر المنتج:",
                options=range(len(df)),
                format_func=lambda i: str(df.iloc[i].get("أسم المنتج","صف "+str(i))),
                key="sel_prod_desc"
            )
            if sel_prod is not None:
                cur_desc = str(df.iloc[sel_prod].get("الوصف","") or "")
                new_desc = st.text_area("الوصف (HTML):", value=cur_desc, height=300, key="prod_desc_area")
                if st.button("💾 حفظ الوصف",key="save_desc"):
                    df.at[sel_prod,"الوصف"]=new_desc
                    st.session_state.fm_df=df
                    st.success("✅ تم حفظ الوصف")
                    st.rerun()

        # SEO table
        if st.session_state.fm_seo_df is not None:
            with st.expander("🔍 جدول SEO — قابل للتعديل"):
                edited_seo = st.data_editor(
                    st.session_state.fm_seo_df.fillna(""),
                    use_container_width=True, num_rows="dynamic", key="seo_editor_main"
                )
                st.session_state.fm_seo_df = edited_seo

        # ── EXPORT ─────────────────────────────────────────────
        st.markdown("""<hr class="gdiv">
        <div class="sec-header"><div class="bar"></div><h3>التصدير — جاهز للرفع على سلة</h3></div>
        """, unsafe_allow_html=True)

        e1,e2,e3,e4 = st.columns(4)
        with e1:
            st.download_button(
                "📥 ملف المنتجات — Excel",
                export_product_xlsx(df),
                "mahwous_products.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True, key="exp_prod_xl"
            )
        with e2:
            st.download_button(
                "📥 ملف المنتجات — CSV",
                export_product_csv(df),
                "mahwous_products.csv","text/csv",
                use_container_width=True, key="exp_prod_csv"
            )
        with e3:
            if st.session_state.fm_seo_df is not None:
                st.download_button(
                    "📥 ملف SEO — Excel",
                    export_seo_xlsx(st.session_state.fm_seo_df),
                    "mahwous_seo.xlsx",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True, key="exp_seo_xl"
                )
            else:
                st.info("لا يوجد ملف SEO بعد — نفّذ 'توليد SEO للكل' من عمليات مجمّعة")
        with e4:
            if st.session_state.fm_seo_df is not None:
                st.download_button(
                    "📥 ملف SEO — CSV",
                    export_seo_csv(st.session_state.fm_seo_df),
                    "mahwous_seo.csv","text/csv",
                    use_container_width=True, key="exp_seo_csv"
                )

    elif st.session_state.fm_df is None:
        st.markdown("""
        <div class="upload-zone">
          <div class="upload-icon">📂</div>
          <div class="upload-title">ارفع ملفك للبدء</div>
          <div class="upload-sub">يدعم: Excel (.xlsx, .xls) | CSV (UTF-8, Windows-1256)</div>
          <div class="upload-sub" style="margin-top:8px">
            ملفات سلة | ملفات الموردين | قوائم الأسماء | أي تنسيق آخر
          </div>
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
# ████  PAGE: NEW PRODUCT QUICK  ██████████████████████████████
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "new":
    st.markdown("""<div class="sec-header"><div class="bar"></div><h3>أضف منتجاً — أدخل الاسم فقط</h3></div>""",
                unsafe_allow_html=True)

    with st.form("new_product_form", clear_on_submit=True):
        f1,f2,f3 = st.columns(3)
        with f1:
            nm = st.text_input("اسم العطر *", placeholder="مثال: شانيل بلو دو شانيل 100 مل")
            pr = st.text_input("السعر", placeholder="299")
        with f2:
            gn = st.selectbox("الجنس", ["للجنسين","للرجال","للنساء"])
            sk = st.text_input("SKU", placeholder="SKU-001")
        with f3:
            sz = st.text_input("الحجم", "100 مل")
            cn = st.selectbox("التركيز", ["أو دو بارفيوم","أو دو كولون","أو دو تواليت","بارفيوم"])

        f4,f5,f6 = st.columns(3)
        with f4: tp = st.selectbox("النوع", ["عطر عادي","تستر"])
        with f5: im = st.text_input("رابط الصورة (اختياري)")
        with f6: st.markdown("<br>",unsafe_allow_html=True)

        o1,o2,o3 = st.columns(3)
        with o1: do_d = st.checkbox("🤖 وصف AI",value=True)
        with o2: do_i = st.checkbox("🖼 جلب صورة",value=False)
        with o3: do_s = st.checkbox("🔍 بيانات SEO",value=True)

        submitted = st.form_submit_button("➕ إضافة للقائمة", type="primary", use_container_width=True)

    if submitted and nm.strip():
        with st.spinner("جاري المعالجة..."):
            is_t   = tp=="تستر"
            brand  = match_brand(nm)
            cat    = match_category(nm,gn)
            seo    = gen_seo(nm,brand,sz,is_t,gn)
            img_url= im or (fetch_image(nm,is_t) if do_i else "")
            desc   = gen_desc(nm,is_t,brand,sz,gn,cn) if do_d else ""

            nr = {c:"" for c in SALLA_PRODUCT_COLS}
            nr.update({
                "النوع ":"منتج","أسم المنتج":nm,"تصنيف المنتج":cat,
                "صورة المنتج":img_url,"وصف صورة المنتج":seo["alt"],
                "نوع المنتج":"منتج جاهز","سعر المنتج":pr,"الوصف":desc,
                "هل يتطلب شحن؟":"نعم","رمز المنتج sku":sk,
                "الوزن":"0.2","وحدة الوزن":"kg","حالة المنتج":"مرئي",
                "الماركة":brand.get("name",""),"خاضع للضريبة ؟":"نعم",
                "اقصي كمية لكل عميل":"0",
                "إخفاء خيار تحديد الكمية":"0","اضافة صورة عند الطلب":"0",
            })
            st.session_state.nw_rows.append({
                "product": nr,
                "seo": {"url":seo["url"],"title":seo["title"],"desc":seo["desc"]}
            })
        st.success(f"✅ أُضيف: **{nm}**")

    # Show pending list
    if st.session_state.nw_rows:
        st.markdown(f"### قائمة المنتجات المعلّقة ({len(st.session_state.nw_rows)} منتج)")
        preview_data = []
        for r in st.session_state.nw_rows:
            p = r["product"]
            preview_data.append({
                "الاسم": p.get("أسم المنتج",""),
                "الماركة": p.get("الماركة",""),
                "التصنيف": p.get("تصنيف المنتج",""),
                "السعر": p.get("سعر المنتج",""),
                "وصف ✓": "✅" if p.get("الوصف","").strip() else "—",
                "صورة ✓": "✅" if p.get("صورة المنتج","").startswith("http") else "—",
            })
        st.dataframe(pd.DataFrame(preview_data), use_container_width=True)

        c1,c2,c3,c4,c5 = st.columns(5)
        prod_df_new = pd.DataFrame([r["product"] for r in st.session_state.nw_rows])
        seo_df_new  = pd.DataFrame([{
            "No. (غير قابل للتعديل)":"",
            "اسم المنتج (غير قابل للتعديل)": r["product"]["أسم المنتج"],
            "رابط مخصص للمنتج (SEO Page URL)": r["seo"]["url"],
            "عنوان صفحة المنتج (SEO Page Title)": r["seo"]["title"],
            "وصف صفحة المنتج (SEO Page Description)": r["seo"]["desc"],
        } for r in st.session_state.nw_rows])

        with c1:
            st.download_button("📥 منتجات Excel",export_product_xlsx(prod_df_new),
                "new_products.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with c2:
            st.download_button("📥 منتجات CSV",export_product_csv(prod_df_new),
                "new_products.csv","text/csv",use_container_width=True)
        with c3:
            st.download_button("📥 SEO Excel",export_seo_xlsx(seo_df_new),
                "new_seo.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True)
        with c4:
            st.download_button("📥 SEO CSV",export_seo_csv(seo_df_new),
                "new_seo.csv","text/csv",use_container_width=True)
        with c5:
            if st.button("🔀 نقل للمدير",use_container_width=True):
                existing = st.session_state.fm_df
                if existing is not None:
                    st.session_state.fm_df = pd.concat([existing,prod_df_new],ignore_index=True)
                else:
                    st.session_state.fm_df = prod_df_new
                    st.session_state.fm_col_map = {"mapped":True}
                st.session_state.nw_rows = []
                st.session_state.page = "manager"
                st.rerun()

        if st.button("🗑️ مسح القائمة",key="clear_nw"):
            st.session_state.nw_rows=[]; st.rerun()

# ══════════════════════════════════════════════════════════════
# ████  PAGE: SEO MERGE  ██████████████████████████████████████
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "seo":
    st.markdown("""<div class="sec-header"><div class="bar"></div><h3>دمج ملف المنتجات بملف SEO</h3></div>""",
                unsafe_allow_html=True)
    c1,c2 = st.columns(2)
    with c1:
        prod_f = st.file_uploader("ملف منتجات سلة",type=["csv","xlsx"],key="seo_pf")
    with c2:
        seo_f  = st.file_uploader("ملف SEO",type=["csv","xlsx"],key="seo_sf")

    if prod_f and seo_f:
        pf = read_file(prod_f, salla_format=True)
        sf = read_file(seo_f)
        if not pf.empty and not sf.empty:
            st.success(f"منتجات: {len(pf)} | SEO: {len(sf)}")

            sc = list(sf.columns)
            s1,s2,s3,s4 = st.columns(4)
            def gi(kws):
                for kw in kws:
                    for c in sc:
                        if kw.lower() in c.lower(): return sc.index(c)
                return 0
            with s1: no_c  = st.selectbox("رقم المنتج",sc,index=gi(["no","رقم"]),key="seo_no")
            with s2: url_c = st.selectbox("URL",sc,index=gi(["url","رابط"]),key="seo_url")
            with s3: ttl_c = st.selectbox("العنوان",sc,index=gi(["title","عنوان"]),key="seo_ttl")
            with s4: dsc_c = st.selectbox("الوصف",sc,index=gi(["desc","وصف"]),key="seo_dsc")

            if st.button("⚡ دمج الآن",type="primary",key="seo_merge_btn"):
                sf[no_c]=sf[no_c].astype(str).str.strip()
                if "No." in pf.columns: pf["No."]=pf["No."].astype(str).str.strip()
                out=[]
                for _,row in pf.iterrows():
                    no=str(row.get("No.","")).strip()
                    m=sf[sf[no_c]==no]
                    sr=m.iloc[0] if not m.empty else None
                    out.append({
                        "No. (غير قابل للتعديل)":no,
                        "اسم المنتج (غير قابل للتعديل)":str(row.get("أسم المنتج","")),
                        "رابط مخصص للمنتج (SEO Page URL)":str(sr[url_c]) if sr is not None else "",
                        "عنوان صفحة المنتج (SEO Page Title)":str(sr[ttl_c]) if sr is not None else "",
                        "وصف صفحة المنتج (SEO Page Description)":str(sr[dsc_c]) if sr is not None else "",
                    })
                out_df=pd.DataFrame(out)
                matched=int((out_df["رابط مخصص للمنتج (SEO Page URL)"]!="").sum())
                st.success(f"✅ تم الدمج: {matched}/{len(pf)} صف له بيانات SEO")
                st.dataframe(out_df.head(10),use_container_width=True)

                edited_seo_m = st.data_editor(out_df,use_container_width=True,
                                              num_rows="fixed",key="seo_merge_editor")
                c1,c2,c3,c4=st.columns(4)
                with c1:
                    st.download_button("📥 منتجات Excel",
                        export_product_xlsx(ensure_salla_cols(pf)),
                        "merged_products.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c2:
                    st.download_button("📥 منتجات CSV",
                        export_product_csv(ensure_salla_cols(pf)),
                        "merged_products.csv","text/csv",use_container_width=True)
                with c3:
                    st.download_button("📥 SEO Excel",
                        export_seo_xlsx(edited_seo_m),
                        "merged_seo.xlsx","application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c4:
                    st.download_button("📥 SEO CSV",
                        export_seo_csv(edited_seo_m),
                        "merged_seo.csv","text/csv",use_container_width=True)

# ══════════════════════════════════════════════════════════════
# ████  PAGE: PRICE UPDATE  ███████████████████████████████████
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "price":
    st.markdown("""<div class="sec-header"><div class="bar"></div><h3>تحديث الأسعار</h3></div>""",
                unsafe_allow_html=True)

    price_file = st.file_uploader("ارفع ملف الأسعار",type=["csv","xlsx"],key="pr_file")
    if price_file:
        pdf = read_file(price_file)
        if not pdf.empty:
            st.success(f"✅ {len(pdf)} صف")
            with st.expander("معاينة"): st.dataframe(pdf.head(6),use_container_width=True)
            pc = ["— لا يوجد —"]+list(pdf.columns)
            def bi(kws):
                for kw in kws:
                    for c in pdf.columns:
                        if kw.lower() in c.lower(): return pc.index(c)
                return 0
            p1,p2,p3,p4,p5 = st.columns(5)
            with p1: no_c =st.selectbox("No.",pc,index=bi(["no","رقم","id"]),key="pr_no")
            with p2: nm_c =st.selectbox("الاسم",pc,index=bi(["اسم","name"]),key="pr_nm")
            with p3: pr_c =st.selectbox("السعر *",pc,index=bi(["سعر","price"]),key="pr_pr")
            with p4: sk_c =st.selectbox("SKU",pc,index=bi(["sku","رمز"]),key="pr_sk")
            with p5: dc_c =st.selectbox("المخفض",pc,index=bi(["مخفض","discount","sale"]),key="pr_dc")

            if st.button("⚡ بناء ملف التحديث",type="primary",key="price_build"):
                rows=[]
                for _,row in pdf.iterrows():
                    def gv(c): return str(row.get(c,"") if c!="— لا يوجد —" and c in pdf.columns else "")
                    rows.append({
                        "No.":gv(no_c),"النوع ":"منتج","أسم المنتج":gv(nm_c),
                        "رمز المنتج sku":gv(sk_c),"سعر المنتج":gv(pr_c),
                        "سعر التكلفة":"","السعر المخفض":gv(dc_c),
                        "تاريخ بداية التخفيض":"","تاريخ نهاية التخفيض":"",
                    })
                price_df=pd.DataFrame(rows)
                edited_pr=st.data_editor(price_df,use_container_width=True,
                                         num_rows="dynamic",key="pr_editor")
                def price_xlsx(df):
                    wb=Workbook(); ws=wb.active; ws.title="Price Update"
                    ws.cell(1,1,"بيانات المنتج")
                    ws.merge_cells(start_row=1,start_column=1,end_row=1,end_column=len(SALLA_PRICE_COLS))
                    ws.cell(1,1).font=Font(bold=True,color="FFFFFF")
                    ws.cell(1,1).fill=PatternFill("solid",fgColor="0F0E0D")
                    ws.cell(1,1).alignment=Alignment(horizontal="center")
                    for i,c in enumerate(SALLA_PRICE_COLS,1):
                        cell=ws.cell(2,i,c); cell.font=Font(bold=True)
                        cell.fill=PatternFill("solid",fgColor="E8D5B7")
                        cell.alignment=Alignment(horizontal="center",wrap_text=True)
                    for ri,(_,row) in enumerate(df.iterrows(),3):
                        for ci,c in enumerate(SALLA_PRICE_COLS,1):
                            ws.cell(ri,ci,str(row.get(c,"") or ""))
                    b=io.BytesIO(); wb.save(b); b.seek(0); return b.read()

                c1,c2=st.columns(2)
                with c1:
                    st.download_button("📥 تحديث الأسعار Excel",
                        price_xlsx(edited_pr),"price_update.xlsx",
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True)
                with c2:
                    out=io.StringIO()
                    out.write("بيانات المنتج"+","*(len(SALLA_PRICE_COLS)-1)+"\n")
                    out.write(",".join(SALLA_PRICE_COLS)+"\n")
                    for _,row in edited_pr.iterrows():
                        out.write(",".join([f'"{str(row.get(c,""))}"' for c in SALLA_PRICE_COLS])+"\n")
                    st.download_button("📥 تحديث الأسعار CSV",
                        out.getvalue().encode("utf-8-sig"),
                        "price_update.csv","text/csv",use_container_width=True)

# ══════════════════════════════════════════════════════════════
# ████  PAGE: SETTINGS  ███████████████████████████████████████
# ══════════════════════════════════════════════════════════════
elif st.session_state.page == "settings":
    st.markdown("""<div class="sec-header"><div class="bar"></div><h3>الإعدادات</h3></div>""",
                unsafe_allow_html=True)

    tab1,tab2,tab3 = st.tabs(["🔑 مفاتيح API","📚 قواعد البيانات","ℹ️ معلومات"])

    with tab1:
        st.markdown("#### Anthropic Claude API")
        ak = st.text_input("ANTHROPIC_API_KEY", value=st.session_state.api_key,
                           type="password", key="set_ak",
                           help="احصل عليه من console.anthropic.com")
        if ak != st.session_state.api_key:
            st.session_state.api_key = ak
            st.success("✅ تم حفظ مفتاح Claude")

        st.markdown("#### Google Custom Search API (اختياري — لجلب الصور)")
        gk = st.text_input("GOOGLE_API_KEY", value=st.session_state.google_api,
                           type="password", key="set_gk",
                           help="console.cloud.google.com → APIs → Custom Search API")
        gc = st.text_input("GOOGLE_CSE_ID", value=st.session_state.google_cse,
                           key="set_gc",
                           help="programmablesearchengine.google.com → Search Engine ID")
        if gk != st.session_state.google_api or gc != st.session_state.google_cse:
            st.session_state.google_api = gk
            st.session_state.google_cse = gc
            st.success("✅ تم حفظ مفاتيح Google")

        st.markdown("""
        <div class="alert-info" style="margin-top:12px">
          على Railway: أضف هذه المفاتيح في <b>Variables</b> وليس هنا مباشرة.
          المفاتيح المُدخلة هنا تُحفظ في الجلسة الحالية فقط.
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### الماركات")
        b_status = f"محملة: **{len(st.session_state.brands_df)} ماركة**" if st.session_state.brands_df is not None else "غير محملة"
        st.info(b_status)
        bf=st.file_uploader("تحديث ملف الماركات (CSV/Excel)",type=["csv","xlsx"],key="set_bf")
        if bf:
            st.session_state.brands_df=read_file(bf)
            st.success(f"✅ تم تحميل {len(st.session_state.brands_df)} ماركة")
        if st.session_state.brands_df is not None:
            with st.expander("معاينة الماركات"): st.dataframe(st.session_state.brands_df.head(10),use_container_width=True)

        st.markdown("#### التصنيفات")
        c_status = f"محملة: **{len(st.session_state.categories_df)} تصنيف**" if st.session_state.categories_df is not None else "غير محملة"
        st.info(c_status)
        cf=st.file_uploader("تحديث ملف التصنيفات (CSV/Excel)",type=["csv","xlsx"],key="set_cf")
        if cf:
            st.session_state.categories_df=read_file(cf)
            st.success(f"✅ تم تحميل {len(st.session_state.categories_df)} تصنيف")
        if st.session_state.categories_df is not None:
            with st.expander("معاينة التصنيفات"): st.dataframe(st.session_state.categories_df.head(10),use_container_width=True)

    with tab3:
        st.markdown("""
        ### مهووس — نظام إدارة المنتجات الذكي v3.0

        | الميزة | التفاصيل |
        |--------|---------|
        | 📁 مدير الملفات | ارفع أي ملف (Excel/CSV)، عيّن الأعمدة، عدّل، أكمل بـ AI |
        | 🤖 Claude AI | وصف HTML احترافي 1200-1500 كلمة، SEO محسّن |
        | 🖼 Google CSE | جلب صور تلقائي عبر Custom Search |
        | 🏷 مطابقة ذكية | 521 ماركة + 88 تصنيف تلقائياً |
        | 📊 تصدير مزدوج | Excel + CSV متوافق 100% مع سلة |
        | ✏️ جدول تفاعلي | تعديل أي خلية + إضافة/حذف صفوف |

        **تنسيقات الملفات المدعومة:**
        - `.xlsx`, `.xlsm` (Excel 2007+)
        - `.xls` (Excel 97-2003)
        - `.csv` (UTF-8, UTF-8-BOM, Windows-1256)
        """)

# ══════════════════════════════════════════════════════════════
# FOOTER
# ══════════════════════════════════════════════════════════════
st.markdown("""<hr class="gdiv">
<div style="text-align:center;color:#9a8e86;font-size:0.78rem;padding-bottom:1rem">
  🌸 مهووس — عالمك العطري يبدأ من مهووس | v3.0 | Streamlit on Railway
</div>""", unsafe_allow_html=True)
