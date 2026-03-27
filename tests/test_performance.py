"""اختبار أداء تقريبي على دفعات كبيرة (بدون شبكة)."""
import time

import pandas as pd
import pytest

from mahwous_core import StrictFilterOptions, apply_strict_pipeline_filters


@pytest.mark.slow
def test_filter_10k_rows_reasonable_time():
    n = 10_000
    df = pd.DataFrame({
        "أسم المنتج": [f"عطر ماركة {i} 100 مل" for i in range(n)],
        "وصف": [""] * n,
    })
    opts = StrictFilterOptions(
        exclude_samples_testers=True,
        exclude_accessories=True,
        exclude_non_global_brands=False,
        exclude_without_volume=False,
    )
    t0 = time.perf_counter()
    out, stats = apply_strict_pipeline_filters(
        df, "أسم المنتج", "وصف", [], opts, label="perf",
    )
    elapsed = time.perf_counter() - t0
    assert len(out) == n
    assert stats["output_rows"] == n
    assert elapsed < 90.0, f"تجاوز الحد الزمني: {elapsed:.2f}s"
