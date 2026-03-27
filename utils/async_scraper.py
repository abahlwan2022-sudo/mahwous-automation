"""
محرك كشط غير متزامن — يكتب data/competitors_latest.csv تحت مجلد العمل الحالي.
يُقرأ رابط الـ Sitemap من متغير البيئة COMPETITOR_SITEMAP_URL عند الحاجة.
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import xml.etree.ElementTree as ET
from urllib.parse import unquote, urlparse, urljoin

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


def _competitors_list_path() -> str:
    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, "competitors_list.json")


def _domain_from_url(u: str) -> str:
    try:
        host = urlparse(str(u or "").strip()).netloc.lower()
        return host.replace("www.", "").strip()
    except Exception:
        return ""


def _normalize_site_to_sitemap(url_or_domain: str) -> str:
    raw = str(url_or_domain or "").strip()
    if not raw:
        return ""
    if not raw.startswith(("http://", "https://")):
        raw = f"https://{raw}"
    p = urlparse(raw)
    base = f"{p.scheme}://{p.netloc}"
    if p.path and p.path.lower().endswith(".xml"):
        return raw
    return urljoin(base + "/", "sitemap.xml")


def _load_competitors_targets() -> list[str]:
    out: list[str] = []
    p = _competitors_list_path()
    if os.path.exists(p):
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, str):
                        out.append(item.strip())
                    elif isinstance(item, dict):
                        v = str(item.get("url", "") or item.get("site", "") or item.get("domain", "")).strip()
                        if v:
                            out.append(v)
        except Exception:
            pass
    if not out:
        sm_url = os.environ.get("COMPETITOR_SITEMAP_URL", "").strip() or DEFAULT_COMPETITOR_SITEMAP_URL
        if sm_url:
            out = [sm_url]
    return [x for x in out if x]


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
    targets = _load_competitors_targets()
    all_rows: list[dict] = []
    for target in targets:
        sm_url = _normalize_site_to_sitemap(target)
        if not sm_url:
            continue
        try:
            rows = await asyncio.to_thread(_sync_fetch_sitemap, sm_url)
        except Exception:
            rows = []
        source_domain = _domain_from_url(target) or _domain_from_url(sm_url)
        for r in rows:
            rr = dict(r)
            rr.setdefault("source_site", source_domain)
            all_rows.append(rr)

    if not all_rows:
        pd.DataFrame(columns=["name", "url", "price", "source_site"]).to_csv(
            out, index=False, encoding="utf-8-sig"
        )
        return

    df = pd.DataFrame(all_rows)
    if "name" in df.columns:
        df["name"] = df["name"].astype(str).str.strip()
        df = df[df["name"] != ""].copy()
    if "url" in df.columns:
        df["url"] = df["url"].astype(str).str.strip()
        df = df[df["url"] != ""].copy()
    df = df.drop_duplicates(subset=[c for c in ["name", "url", "source_site"] if c in df.columns], keep="first")
    df.to_csv(out, index=False, encoding="utf-8-sig")
