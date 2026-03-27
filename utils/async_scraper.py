"""
محرك كشط غير متزامن — يكتب data/competitors_latest.csv تحت مجلد العمل الحالي.
يُقرأ رابط الـ Sitemap من متغير البيئة COMPETITOR_SITEMAP_URL عند الحاجة.
"""
from __future__ import annotations

import asyncio
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse

import pandas as pd
import requests

_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
_REQ_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; MahwousBot/1.0; +https://mahwous.com)"}

# متجر الخبير: sitemap_products.xml يعيد 410 حالياً — نستخدم الفهرس الرئيسي الذي يشير إلى sitemap-1..N
DEFAULT_COMPETITOR_SITEMAP_URL = "https://alkhabeershop.com/sitemap.xml"

_MAX_CHILD_SITEMAPS = 12
_MAX_TOTAL_URLS = 12000


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

    loc_tag = f"{{{_NS}}}loc"
    url_tag = f"{{{_NS}}}url"

    def _name_from_product_url(u: str) -> str:
        p = urlparse(u)
        parts = [x for x in (p.path or "").split("/") if x]
        if not parts:
            return ""
        tail = unquote(parts[-1])
        return tail.replace("-", " ").replace("_", " ").strip()[:240]

    for el in root.iter():
        if el.tag == url_tag:
            for child in el:
                if child.tag == loc_tag and (child.text or "").strip():
                    u = child.text.strip()
                    nm = _name_from_product_url(u)
                    if not nm:
                        continue
                    rows.append({"name": nm, "url": u, "price": ""})

    if not rows:
        for m in re.finditer(r"<loc>\s*([^<]+)\s*</loc>", text, re.I):
            u = m.group(1).strip()
            nm = _name_from_product_url(u)
            if not nm:
                continue
            rows.append({"name": nm, "url": u, "price": ""})
    return rows


def _child_sitemap_urls_from_index(root: ET.Element) -> list[str]:
    if not str(root.tag).endswith("sitemapindex"):
        return []
    urls: list[str] = []
    for sm in root.findall(f"{{{_NS}}}sitemap"):
        loc = sm.find(f"{{{_NS}}}loc")
        if loc is not None and (loc.text or "").strip():
            urls.append(loc.text.strip())
    return urls


def _sync_fetch_sitemap(url: str) -> list[dict]:
    r = requests.get(url, timeout=120, headers=_REQ_HEADERS)
    r.raise_for_status()
    text = r.text
    try:
        root = ET.fromstring(text)
    except ET.ParseError:
        return _rows_from_sitemap_xml(text)

    children = _child_sitemap_urls_from_index(root)
    if not children:
        return _rows_from_sitemap_xml(text)

    all_rows: list[dict] = []
    for child_url in children[:_MAX_CHILD_SITEMAPS]:
        try:
            cr = requests.get(child_url, timeout=120, headers=_REQ_HEADERS)
            cr.raise_for_status()
            all_rows.extend(_rows_from_sitemap_xml(cr.text))
        except Exception:
            continue
        if len(all_rows) >= _MAX_TOTAL_URLS:
            break
    return all_rows[:_MAX_TOTAL_URLS]


async def run_scraper_engine() -> None:
    """تشغيل الكشط وكتابة competitors_latest.csv."""
    out = _data_csv_path()
    sm_url = os.environ.get("COMPETITOR_SITEMAP_URL", "").strip() or DEFAULT_COMPETITOR_SITEMAP_URL
    rows: list[dict] = []
    if sm_url:
        rows = await asyncio.to_thread(_sync_fetch_sitemap, sm_url)
    if not rows:
        pd.DataFrame(columns=["name", "url", "price"]).to_csv(
            out, index=False, encoding="utf-8-sig"
        )
        return
    pd.DataFrame(rows).to_csv(out, index=False, encoding="utf-8-sig")
