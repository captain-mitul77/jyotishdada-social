"""Bilingual (Hindi + English) captions built only from the day's Panchang fields."""
import datetime as dt

import hindi as H
from data import dainik_url, window
from render import Ctx, hi_date

BASE_TAGS = ["#आजकापंचांग", "#Panchang", "#AajKaPanchang", "#HinduCalendar", "#Jyotish",
             "#VedicAstrology", "#RahuKaal", "#Tithi", "#Nakshatra", "#Sanatan"]


def _tags(c: Ctx) -> str:
    tags = list(BASE_TAGS)
    for ev in c.today_events[:1]:
        tags.insert(0, "#" + "".join(w.capitalize() for w in ev["name"].replace("-", " ").split()))
    return " ".join(tags[:12])


def _lines(c: Ctx) -> list[str]:
    p = c.p
    out = [
        f"🪔 आज का पंचांग | {hi_date(c.date)}, {c.wd_hi}",
        f"📍 {c.city_hi} ({c.city_en})",
        "",
    ]
    if c.today_events:
        out += [f"✨ आज: {c.today_events[0]['name']}", ""]
    t = f"🌙 तिथि: {c.tithi_hi} ({c.paksha_hi})"
    if c.tithi_upto:
        t += f" — {c.tithi_upto} तक, फिर {c.tithi_next_hi}"
    out += [t,
            f"⭐ नक्षत्र: {c.nak_hi}",
            f"🧘 योग: {c.yoga_hi}  |  करण: {c.kar_hi}",
            f"🌅 सूर्योदय {p['sunrise']}  |  🌇 सूर्यास्त {p['sunset']}",
            "",
            f"✅ अभिजीत मुहूर्त: {window(p.get('abhijit', ''))}",
            f"⚠️ राहु काल: {window(p.get('rahuKalam', ''))}",
            ""]
    return out


def build(c: Ctx, platform: str) -> str:
    """platform: instagram | facebook | telegram | youtube"""
    url = dainik_url(c.city_slug, source=platform)
    body = _lines(c)
    en = (f"Daily Panchang for {c.city_en}, {c.date.strftime('%d %b %Y')}: Tithi {c.tithi_en} "
          f"({c.paksha_en}), Nakshatra {c.nak_en}, Yoga {c.yoga_en}, Karana {c.kar_en}.")
    if platform == "instagram":  # links are not clickable in IG captions
        body += ["👉 अपने शहर का पूरा पंचांग: jyotishdada.com (लिंक बायो में)", "", en, "", _tags(c)]
    elif platform == "facebook":
        body += [f"👉 अपने शहर का पूरा पंचांग: {url}", "", en, "", _tags(c)]
    elif platform == "youtube":
        body += [f"👉 पूरा पंचांग: {url}", "", en, "", "#Shorts " + _tags(c)]
    else:  # telegram: media captions are capped at 1024 characters, so no hashtags and no English line
        body += [f"👉 पूरा पंचांग: {url}"]
    text = "\n".join(body).strip()
    return text[:1020] if platform == "telegram" else text[:2150]


def youtube_title(c: Ctx) -> str:
    t = f"आज का पंचांग {c.date.day} {H.MONTH[c.date.month - 1]} | {c.tithi_hi} | Rahu Kaal"
    return (t[:92] + " #Shorts")[:100]
