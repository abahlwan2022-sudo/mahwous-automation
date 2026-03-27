"""
محرك كشط غير متزامن — يكتب data/competitors_latest.csv تحت مجلد العمل الحالي.
يُقرأ رابط الـ Sitemap من متغير البيئة COMPETITOR_SITEMAP_URL عند الحاجة.
"""
from __future__ import annotations

import asyncio
import os
import re
import xml.etree.ElementTree as ET

import pandas as pd
import requests


def _data_csv_path() -> str:
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "competitors_latest.csv")


def _rows_from_sitemap_xml(text: str) -> list[dict]:
    rows: list[dict] = []
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return rows

    ns = "http://www.sitemaps.org/schemas/sitemap/0.9"
    loc_tag = f"{{{ns}}}loc"
    url_tag = f"{{{ns}}}url"

    for el in root.iter():
        if el.tag == url_tag:
            for child in el:
                if child.tag == loc_tag and (child.text or "").strip():
                    u = child.text.strip()
                    tail = u.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")
                    rows.append({"name": tail[:240], "url": u, "price": ""})

    if not rows:
        for m in re.finditer(r"<loc>\s*([^<]+)\s*</loc>", text, re.I):
            u = m.group(1).strip()
            tail = u.rsplit("/", 1)[-1].replace("-", " ").replace("_", " ")
            rows.append({"name": tail[:240], "url": u, "price": ""})
    return rows


def _sync_fetch_sitemap(url: str) -> list[dict]:
    r = requests.get(
        url,
        timeout=120,
        headers={"User-Agent": "Mozilla/5.0 (compatible; MahwousBot/1.0)"},
    )
    r.raise_for_status()
    return _rows_from_sitemap_xml(r.text)


async def run_scraper_engine() -> None:
    """تشغيل الكشط وكتابة competitors_latest.csv."""
    out = _data_csv_path()
    sm_url = os.environ.get("COMPETITOR_SITEMAP_URL", "").strip()
    rows: list[dict] = []
    if sm_url:
        rows = await asyncio.to_thread(_sync_fetch_sitemap, sm_url)
    if not rows:
        pd.DataFrame(columns=["name", "url", "price"]).to_csv(
            out, index=False, encoding="utf-8-sig"
        )
        return
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
