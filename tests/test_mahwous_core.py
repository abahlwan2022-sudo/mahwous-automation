"""اختبارات وحدة لـ mahwous_core (بدون Streamlit)."""
import pandas as pd
import pytest

from mahwous_core import (
    StrictFilterOptions,
    apply_strict_pipeline_filters,
    normalize_price_digits,
    parse_price_numeric,
    product_name_matches_approved_brand_list,
    strict_row_is_accessory,
    strict_row_is_sample_small_volume,
    validate_export_brands_list,
    validate_export_product_dataframe,
    validate_export_seo_dataframe,
    validate_input_dataframe,
)


def test_parse_price_numeric_arabic_digits():
    ok, v = parse_price_numeric("١٢٣ ريال")
    assert ok
    assert abs(v - 123.0) < 0.01


def test_normalize_price_digits():
    assert normalize_price_digits("299 SR") in ("299", "299.0")


def test_validate_input_empty():
    ok, issues = validate_input_dataframe(pd.DataFrame(), "ملف")
    assert not ok
    assert any("فارغ" in x for x in issues)


def test_validate_input_ok():
    df = pd.DataFrame({"أسم المنتج": ["عطر تجريبي 100 مل"]})
    ok, issues = validate_input_dataframe(df, "ملف")
    assert ok and not issues


def test_strict_sample_small_volume():
    assert not strict_row_is_sample_small_volume("تستر ديور 100 مل")
    assert not strict_row_is_sample_small_volume("Dior Tester 100ml")
    assert strict_row_is_sample_small_volume("عينة 2 مل")
    assert strict_row_is_sample_small_volume("Chanel sample vial 5ml")
    assert not strict_row_is_sample_small_volume("عطر ديور سووفاج 100 مل")


def test_strict_accessory():
    assert strict_row_is_accessory("حقيبة عطر فارغة")
    assert strict_row_is_accessory("Travel case for perfume")
    assert not strict_row_is_accessory("عطر كريد أفينتوس 100 مل")


def test_brand_list_match():
    assert product_name_matches_approved_brand_list("عطر شانيل بلو 100 مل", ["شانيل", "ديور"])
    assert not product_name_matches_approved_brand_list("عطر غير معروف", ["شانيل"])


def test_apply_filters_volume():
    df = pd.DataFrame({
        "أسم المنتج": [
            "عطر كامل 100 مل",
            "قطعة بدون حجم",
        ],
    })
    opts = StrictFilterOptions(exclude_without_volume=True)
    out, stats = apply_strict_pipeline_filters(
        df, "أسم المنتج", None, [], opts, label="t",
    )
    assert len(out) == 1
    assert stats["dropped_no_volume"] == 1


def test_validate_export_product_ok():
    df = pd.DataFrame({
        "أسم المنتج": ["عطر أ 100 مل"],
        "سعر المنتج": ["199"],
        "الماركة": ["ماركة"],
        "رمز المنتج sku": ["SKU1"],
    })
    ok, issues = validate_export_product_dataframe(df)
    assert ok and not issues


def test_validate_export_duplicate():
    df = pd.DataFrame({
        "أسم المنتج": ["نفس", "نفس"],
        "سعر المنتج": ["1", "1"],
        "الماركة": ["م", "م"],
        "رمز المنتج sku": ["", ""],
    })
    ok, issues = validate_export_product_dataframe(df)
    assert not ok
    assert any("تكرار" in x for x in issues)


def test_validate_seo():
    df = pd.DataFrame({
        "No. (غير قابل للتعديل)": ["1"],
        "اسم المنتج (غير قابل للتعديل)": ["عطر"],
        "رابط مخصص للمنتج (SEO Page URL)": ["/p1"],
        "عنوان صفحة المنتج (SEO Page Title)": ["t"],
        "وصف صفحة المنتج (SEO Page Description)": ["d"],
    })
    ok, issues = validate_export_seo_dataframe(df)
    assert ok


def test_validate_brands_dup():
    brands = [
        {"اسم الماركة": "أ"},
        {"اسم الماركة": "أ"},
    ]
    ok, issues = validate_export_brands_list(brands)
    assert not ok
