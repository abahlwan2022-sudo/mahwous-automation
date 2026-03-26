"""
منطق مهووس الخالص (بدون Streamlit) — فلاتر صارمة، تحقق مدخلات/مخرجات، أسعار.
يُستورد من app.py ويُختبر بـ pytest.
"""
from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass
from typing import Optional

import pandas as pd

LOG = logging.getLogger("mahwous.core")

SALLA_SEO_COLS = [
    "No. (غير قابل للتعديل)",
    "اسم المنتج (غير قابل للتعديل)",
    "رابط مخصص للمنتج (SEO Page URL)",
    "عنوان صفحة المنتج (SEO Page Title)",
    "وصف صفحة المنتج (SEO Page Description)",
]

REQUIRED_EXPORT_PRODUCT_FIELDS = ("أسم المنتج", "سعر المنتج", "الماركة")


def normalize_price_digits(val) -> str:
    s = str(val or "").strip()
    if not s or s.lower() in ("nan", "none"):
        return ""
    for i, ch in enumerate("٠١٢٣٤٥٦٧٨٩"):
        s = s.replace(ch, str(i))
    s = s.replace("\u066b", ".").replace("٫", ".").replace("\u066c", "")
    m = re.search(r"(\d+(?:[.,]\d+)?)", s.replace(",", ""))
    if m:
        return m.group(1).replace(",", ".")
    digits = re.sub(r"[^\d.]", "", s)
    return digits or ""


def parse_price_numeric(val) -> tuple:
    s = normalize_price_digits(val)
    if not s:
        return False, 0.0
    try:
        return True, float(s)
    except ValueError:
        return False, 0.0


def _normalize_key(text: str) -> str:
    if not text or not isinstance(text, str):
        return ""
    text = text.strip().lower()
    text = unicodedata.normalize("NFKC", text)
    for i, n in enumerate("٠١٢٣٤٥٦٧٨٩"):
        text = text.replace(n, str(i))
    text = re.sub(r"[^\w\s\d]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_size_ml(text: str) -> float:
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


ACCESSORY_KEYWORD_PATTERNS = [
    r"حقيبة", r"\bbag\b", r"\bpouch\b", r"مِرشة", r"أداة\s*تطبيق", r"\bapplicator\b",
    r"\bfunnel\b", r"roller\s*ball", r"رول\s*أون", r"غطاء\s*فقط", r"cap\s*only",
    r"refill\s*case", r"علبة\s*فارغة", r"زجاجة\s*فارغة", r"empty\s*bottle",
    r"atomizer\s*head", r"مضخة\s*فقط", r"pump\s*only", r"travel\s*case",
    r"صندوق\s*فقط", r"حامل\s*عطر", r"\bstand\b", r"مِرشة\s*عطر", r"كيس\s*حماية",
    r"protection\s*pouch", r"مبخرة",
]


@dataclass
class StrictFilterOptions:
    """خيارات الفلترة قبل المقارنة (في المسار الآلي تُطبَّق على ملف المنافسين فقط)."""
    exclude_samples_testers: bool = False  # عينات = حجم صغير أو سمبل/فايال؛ عطور التستر لا تُستبعد
    exclude_accessories: bool = False
    exclude_non_global_brands: bool = False
    exclude_without_volume: bool = False


def strict_row_is_sample_small_volume(name: str, desc: str = "") -> bool:
    """
    استبعاد «العينات»: حجم صغير (مثل 2–8 مل) أو كلمات سمبل/فايال/ميني.
    عطور التستر (تستر / tester) لا تُعامل كعينة ولا تُستبعد بهذا الخيار.
    """
    raw = str(name or "").strip()
    if not raw:
        return False
    combined_lower = f"{name} {desc}".lower()
    if re.search(r"\btester\b|\bتستر\b|\bتيستر\b", combined_lower, re.IGNORECASE):
        return False
    comb = f"{name} {desc}"
    vol = _extract_size_ml(comb)
    if 0 < vol <= 8.0:
        return True
    tl = combined_lower
    if re.search(
        r"\bعينة\b|\bسمبل\b|\bsample\b|\bvial\b|\bminiature\b|\bميني\b|\bmini\b",
        tl,
        re.IGNORECASE,
    ):
        return True
    return False


def strict_row_is_accessory(name: str) -> bool:
    t = str(name or "").lower()
    for pat in ACCESSORY_KEYWORD_PATTERNS:
        if re.search(pat, t, re.IGNORECASE):
            return True
    return False


def product_name_matches_approved_brand_list(name: str, brands_list: list) -> bool:
    if not brands_list:
        return True
    nl = str(name or "").lower()
    for b in brands_list:
        bs = str(b).strip()
        if bs and bs.lower() in nl:
            return True
    return False


def strict_row_has_volume_in_text(name: str, desc: str = "") -> bool:
    combined = f"{name or ''} {desc or ''}"
    return _extract_size_ml(combined) > 0


def apply_strict_pipeline_filters(
    df: pd.DataFrame,
    name_col: str,
    desc_col: Optional[str],
    brands_list: list,
    opts: StrictFilterOptions,
    label: str = "dataset",
) -> tuple[pd.DataFrame, dict]:
    empty_stats = {
        "label": label, "input_rows": 0, "output_rows": 0,
        "dropped_empty_name": 0, "dropped_samples": 0, "dropped_accessories": 0,
        "dropped_non_brand": 0, "dropped_no_volume": 0,
    }
    if df is None or df.empty:
        return df, empty_stats
    if name_col not in df.columns:
        LOG.error("apply_strict_pipeline_filters: missing name col %s (%s)", name_col, label)
        return df, {**empty_stats, "input_rows": len(df), "output_rows": len(df), "error": "no_name_col"}

    stats = {
        "label": label, "input_rows": len(df), "output_rows": 0,
        "dropped_empty_name": 0, "dropped_samples": 0, "dropped_accessories": 0,
        "dropped_non_brand": 0, "dropped_no_volume": 0,
    }
    brand_filter_active = bool(opts.exclude_non_global_brands and brands_list)
    if opts.exclude_non_global_brands and not brands_list:
        LOG.warning(
            "non-global brand filter on but brands list empty — skipping brand filter (%s)",
            label,
        )

    keep_idx = []
    for i, row in df.iterrows():
        name = str(row.get(name_col, "") or "").strip()
        if not name or name.lower() in ("nan", "none"):
            stats["dropped_empty_name"] += 1
            continue
        desc = ""
        if desc_col and desc_col in df.columns:
            desc = str(row.get(desc_col, "") or "")

        if opts.exclude_samples_testers and strict_row_is_sample_small_volume(name, desc):
            stats["dropped_samples"] += 1
            continue
        if opts.exclude_accessories and strict_row_is_accessory(name):
            stats["dropped_accessories"] += 1
            continue
        if brand_filter_active and not product_name_matches_approved_brand_list(name, brands_list):
            stats["dropped_non_brand"] += 1
            continue
        if opts.exclude_without_volume and not strict_row_has_volume_in_text(name, desc):
            stats["dropped_no_volume"] += 1
            continue
        keep_idx.append(i)

    out = df.loc[keep_idx].reset_index(drop=True) if keep_idx else pd.DataFrame(columns=df.columns)
    stats["output_rows"] = len(out)
    LOG.info(
        "strict_filters %s: in=%s out=%s dropped=%s",
        label, stats["input_rows"], stats["output_rows"],
        {k: stats[k] for k in stats if k.startswith("dropped")},
    )
    return out, stats


def validate_input_dataframe(df: Optional[pd.DataFrame], label: str, min_rows: int = 1) -> tuple[bool, list]:
    issues = []
    if df is None:
        issues.append(f"{label}: لا توجد بيانات (None).")
        return False, issues
    if not isinstance(df, pd.DataFrame):
        issues.append(f"{label}: نوع البيانات غير صالح.")
        return False, issues
    if df.empty:
        issues.append(f"{label}: الملف فارغ أو لا يحتوي صفوفاً بعد القراءة.")
        return False, issues
    if len(df.columns) < 1:
        issues.append(f"{label}: لا توجد أعمدة.")
        return False, issues
    if len(df) < min_rows:
        issues.append(f"{label}: عدد الصفوف ({len(df)}) أقل من الحد الأدنى ({min_rows}).")
        return False, issues
    return True, []


def validate_export_product_dataframe(df: Optional[pd.DataFrame], max_issues: int = 80) -> tuple[bool, list]:
    issues: list = []
    if df is None or df.empty:
        issues.append("جدول التصدير فارغ.")
        return False, issues
    for req in REQUIRED_EXPORT_PRODUCT_FIELDS:
        if req not in df.columns:
            issues.append(f"حقل إلزامي مفقود في الجدول: {req}")
    sku_col = "رمز المنتج sku"
    name_col = "أسم المنتج"
    keys_seen = set()
    dup_n = 0
    for ix, row in df.iterrows():
        sku = str(row.get(sku_col, "") or "").strip().lower()
        nm = _normalize_key(str(row.get(name_col, "") or ""))
        key = f"sku:{sku}" if sku and sku not in ("nan", "none", "") else nm
        if key and key != "sku:":
            if key in keys_seen:
                dup_n += 1
            keys_seen.add(key)
        name_v = str(row.get(name_col, "") or "").strip()
        if not name_v or name_v.lower() in ("nan", "none"):
            issues.append(f"صف {ix}: اسم المنتج فارغ.")
        price_raw = row.get("سعر المنتج", "")
        ps = str(price_raw).strip()
        if ps and ps.lower() not in ("nan", "none"):
            ok_p, _ = parse_price_numeric(price_raw)
            if not ok_p:
                issues.append(f"صف {ix}: سعر المنتج غير رقمي: {price_raw!r}")
        brand_v = str(row.get("الماركة", "") or "").strip()
        if not brand_v or brand_v.lower() in ("nan", "none"):
            issues.append(f"صف {ix}: الماركة فارغة.")
        if len(issues) >= max_issues:
            break
    if dup_n:
        issues.append(f"تكرار محتمل لـ {dup_n} صف (SKU أو اسم موحّد).")
    ok = len(issues) == 0
    return ok, issues


def validate_export_seo_dataframe(df: Optional[pd.DataFrame]) -> tuple[bool, list]:
    issues = []
    if df is None or df.empty:
        return True, []
    for c in SALLA_SEO_COLS:
        if c not in df.columns:
            issues.append(f"SEO: عمود مفقود {c}")
    name_col = "اسم المنتج (غير قابل للتعديل)"
    seen = set()
    for ix, row in df.iterrows():
        nm = _normalize_key(str(row.get(name_col, "") or ""))
        if nm:
            if nm in seen:
                issues.append(f"SEO صف {ix}: تكرار اسم المنتج.")
            seen.add(nm)
        if not str(row.get("رابط مخصص للمنتج (SEO Page URL)", "") or "").strip():
            issues.append(f"SEO صف {ix}: رابط فارغ.")
    return len(issues) == 0, issues


def validate_export_brands_list(brands: list) -> tuple[bool, list]:
    issues = []
    if not brands:
        return True, []
    seen = set()
    for i, b in enumerate(brands):
        nm = _normalize_key(str(b.get("اسم العلامة التجارية", b.get("اسم الماركة", "")) or ""))
        if nm in seen:
            issues.append(f"ماركة مكررة: {nm}")
        seen.add(nm)
    return len(issues) == 0, issues
