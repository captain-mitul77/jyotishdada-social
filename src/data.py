"""Fetch today's Panchang + upcoming festivals from the live JyotishDada API.

Response shapes are the ones the website already uses (lib/types.ts `Panchang`, and the
`/api/festivals` feed `items`). Nothing here adds or reshapes a field.
"""
import os
import time
import datetime as dt
from zoneinfo import ZoneInfo

import requests

API_BASE = os.environ.get("API_BASE", "https://api.jyotishdada.com").rstrip("/")
SITE_URL = os.environ.get("SITE_URL", "https://jyotishdada.com").rstrip("/")
CITY_SLUG = os.environ.get("CITY_SLUG", "delhi")
IST = ZoneInfo("Asia/Kolkata")


def today_ist() -> dt.date:
    override = os.environ.get("POST_DATE")  # YYYY-MM-DD, for testing / back-fill
    if override:
        return dt.date.fromisoformat(override)
    return dt.datetime.now(IST).date()


def get_json(path: str, params: dict, tries: int = 6, timeout: int = 90):
    """The backend is on Render's free plan and sleeps; the first call can take a minute.
    Retry with a growing pause instead of failing the whole day's post."""
    last = None
    for i in range(tries):
        try:
            r = requests.get(f"{API_BASE}{path}", params=params, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            last = f"HTTP {r.status_code}: {r.text[:200]}"
        except requests.RequestException as e:  # noqa: PERF203
            last = repr(e)
        time.sleep(min(10 * (i + 1), 45))
    raise RuntimeError(f"API call failed after {tries} tries: {path} {params} -> {last}")


def fetch_day(date: dt.date, city: str = CITY_SLUG):
    panchang = get_json("/api/panchang", {"city": city, "date": date.isoformat()})
    feed = get_json("/api/festivals", {"city": city, "days": 21, "from": date.isoformat()})
    return panchang, feed.get("items", [])


def dainik_url(city: str = CITY_SLUG, source: str = "social", campaign: str = "daily_panchang") -> str:
    """Page that has the full daily detail; UTM tags so GA4 can show which network sent the visit."""
    return (f"{SITE_URL}/panchang/{city}/dainik"
            f"?utm_source={source}&utm_medium=social&utm_campaign={campaign}")


def window(s: str) -> str:
    """'08:00 AM to 09:21 AM' -> '08:00 AM – 09:21 AM' (other strings pass through)."""
    return (s or "").replace(" to ", " – ")
