"""سيناريوهات تكامل خفيفة (فلترة + تحقق) بدون تشغيل Streamlit."""
import pandas as pd

from mahwous_core import (
    StrictFilterOptions,
    apply_strict_pipeline_filters,
    validate_export_product_dataframe,
    validate_input_dataframe,
)


def test_competitor_only_sample_filter():
    """فلتر العينات يُطبَّق على المنافسين؛ التستر لا يُستبعد، السمبل/الحجم الصغير يُستبعد."""
    comp = pd.DataFrame({
        "name": ["تستر ديور 100 مل", "عينة شانيل 2 مل", "Competitor B 100ml"],
        "description": ["", "", ""],
    })
    ok_c, _ = validate_input_dataframe(comp, "منافس")
    assert ok_c

    opts = StrictFilterOptions(
        exclude_samples_testers=True,
        exclude_without_volume=False,
    )
    cp_out, cp_stats = apply_strict_pipeline_filters(
        comp, "name", "description", [], opts, "comp",
    )
    assert cp_stats["dropped_samples"] >= 1
    assert "تستر" in cp_out["name"].iloc[0]
    assert len(cp_out) == 2


def test_export_validation_after_merge():
    df = pd.DataFrame({
        "أسم المنتج": ["منتج نهائي 100 مل"],
        "سعر المنتج": ["250.5"],
        "الماركة": ["ماركة"],
        "رمز المنتج sku": ["X1"],
    })
    ok, issues = validate_export_product_dataframe(df)
    assert ok and not issues
