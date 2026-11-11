"""Draws the daily feed card (1080x1350) and the four 1080x1920 reel scenes with Pillow.

Colours are the site's design tokens (tailwind.config.js). Fonts: Eczar (display, has Devanagari),
Noto Sans Devanagari and Inter, all open-licence (OFL), loaded from ./fonts.
"""
import datetime as dt
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import hindi as H
from data import window

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"
LOGO = ROOT / "brand" / "logo-512.png"

CREAM, MAROON, MARIGOLD, GOLD, INDIGO, INK, WHITE = (
    "#FBF3E7", "#6B1E23", "#E8A33D", "#C9A227", "#2C3454", "#2B1B12", "#FFFFFF")
SOFT_MARIGOLD = "#F6D58E"

_cache = {}


def font(name: str, size: int, wght: int | None = None) -> ImageFont.FreeTypeFont:
    key = (name, size, wght)
    if key in _cache:
        return _cache[key]
    f = ImageFont.truetype(str(FONTS / name), size)
    if wght is not None:
        vals = []
        for ax in f.get_variation_axes():
            nm = ax["name"].decode() if isinstance(ax["name"], bytes) else ax["name"]
            vals.append(wght if "eight" in nm else ax["default"])
        f.set_variation_by_axes(vals)
    _cache[key] = f
    return f


def display(size, w=700):  # Eczar: Latin + Devanagari headings
    return font("Eczar.ttf", size, w)


def deva(size, w=500):
    return font("NotoSansDevanagari.ttf", size, w)


def latin(size, w=500):
    return font("Inter.ttf", size, w)


def tw(d, text, f):
    return d.textlength(text, font=f)


def fit(d, text, make, max_w, start, minimum=28):
    size = start
    while size > minimum and tw(d, text, make(size)) > max_w:
        size -= 2
    return make(size)


def text(d, xy, s, f, fill, anchor="la"):
    d.text(xy, s, font=f, fill=fill, anchor=anchor)


def rrect(d, box, r, fill=None, outline=None, width=2):
    d.rounded_rectangle(box, radius=r, fill=fill, outline=outline, width=width)


def logo_tile(size: int) -> Image.Image:
    im = Image.open(LOGO).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS)


def hi_date(date: dt.date) -> str:
    return f"{date.day} {H.MONTH[date.month - 1]} {date.year}"


def short_hi(date: dt.date) -> str:
    return f"{date.day} {H.MONTH[date.month - 1]}"


def _t12(iso_dt: str) -> str:
    return dt.datetime.fromisoformat(iso_dt).strftime("%I:%M %p")


def tithi_upto(p: dict):
    """(end-time text, next tithi name) when the sunrise tithi ends before the next sunrise, else (None, None).
    Reads the `tracks` field the backend already returns; nothing is recomputed here."""
    for tr in p.get("tracks", []) or []:
        if tr.get("type") != "Tithi" or len(tr.get("events", [])) < 2:
            continue
        first, nxt = tr["events"][0], tr["events"][1]
        try:
            end = dt.datetime.fromisoformat(first["endTime"])
            day = dt.date.fromisoformat(p["date"])
            sunrise_next = dt.datetime.combine(day + dt.timedelta(days=1),
                                               dt.time.fromisoformat(p["nextSunrise"]))
        except (KeyError, ValueError):
            return None, None
        if end >= sunrise_next:
            return None, None
        label = _t12(first["endTime"])
        if end.date() != day:
            label += f" ({end.strftime('%b')} {end.day})"
        return label, nxt["label"].split(",")[0].strip()
    return None, None


class Ctx:
    """Everything the templates need, derived once from the Panchang dict and festival items."""

    def __init__(self, p: dict, items: list, date: dt.date, city_slug: str):
        self.p, self.date, self.city_slug = p, date, city_slug
        self.wd_en = H.weekday_en(p["weekday"])
        self.wd_hi = H.hi(H.WEEKDAY, self.wd_en)
        self.tithi_en, self.tithi_hi = p["tithi"], H.hi(H.TITHI, p["tithi"])
        self.paksha_en, self.paksha_hi = p["tithiPaksha"], H.hi(H.PAKSHA, p["tithiPaksha"])
        self.nak_en, self.nak_hi = p["nakshatra"], H.hi(H.NAKSHATRA, p["nakshatra"])
        self.yoga_en, self.yoga_hi = p["yoga"], H.hi(H.YOGA, p["yoga"])
        self.kar_en, self.kar_hi = p["karana"], H.hi(H.KARANA, p["karana"])
        self.city_en = p["city"].split(",")[0]
        self.city_hi = H.CITY.get(city_slug, self.city_en)
        self.tithi_upto, self.tithi_next_en = tithi_upto(p)
        self.tithi_next_hi = H.hi(H.TITHI, (self.tithi_next_en or "").replace(",", "").split(" ")[0])
        iso = date.isoformat()
        # "Other" is things like plain Amavasya / Purnima; real festivals and vrats are the named categories.
        self.today_events = [i for i in items if i["date"] == iso and i.get("category") != "Other"]
        self.upcoming = [i for i in items if i["date"] > iso and i.get("category") != "Other"][:4]


def _header(img, d, band_h, subtitle):
    d.rectangle((0, 0, img.width, band_h), fill=MAROON)
    d.rectangle((0, band_h, img.width, band_h + 6), fill=GOLD)
    tile = logo_tile(band_h - 60)
    img.paste(tile, (50, 30), tile)
    x = 50 + tile.width + 28
    text(d, (x, band_h / 2 - 6), "JyotishDada", display(64, 700), CREAM, "ls")
    text(d, (x, band_h / 2 + 44), subtitle, deva(32, 500), SOFT_MARIGOLD, "ls")


def _footer(img, d, y0, line1, line2):
    d.rectangle((0, y0, img.width, img.height), fill=MAROON)
    d.rectangle((0, y0 - 6, img.width, y0), fill=GOLD)
    mid = y0 + (img.height - y0) / 2
    text(d, (img.width / 2, mid - 16), line1, deva(42, 700), CREAM, "mm")
    text(d, (img.width / 2, mid + 30), line2, deva(34, 600), MARIGOLD, "mm")


def _elem_card(d, box, label_hi, label_en, val_hi, val_en, sub=None):
    x0, y0, x1, y1 = box
    rrect(d, box, 28, fill=WHITE, outline=GOLD, width=3)
    pad = 28
    text(d, (x0 + pad, y0 + 26), f"{label_hi}  ·  {label_en}", deva(28, 600), MAROON)
    f = fit(d, val_hi, lambda s: display(s, 700), x1 - x0 - 2 * pad, 60, 34)
    text(d, (x0 + pad, y0 + 142), val_hi, f, INK, "ls")
    en = val_en if sub is None else f"{val_en}  ·  {sub}"
    text(d, (x0 + pad, y1 - 24), en, fit(d, en, lambda s: latin(s, 500), x1 - x0 - 2 * pad, 30, 20), "#6A5A4E", "ls")


def _time_card(d, box, label_hi, label_en, value, kind):
    x0, y0, x1, y1 = box
    good = kind == "good"
    fill, fg, sub = (MARIGOLD, INK, "#5A3A0C") if good else (MAROON, CREAM, SOFT_MARIGOLD)
    rrect(d, box, 28, fill=fill)
    text(d, (x0 + 32, y0 + 22), f"{label_hi}  ·  {label_en}", deva(30, 700), sub)
    v = window(value) or "—"
    f = fit(d, v, lambda s: display(s, 700), x1 - x0 - 64, 62, 30)
    text(d, (x0 + 32, y1 - 24), v, f, fg, "ls")


# ───────────────────────────── feed card 1080x1350 ─────────────────────────────
def feed_card(c: Ctx) -> Image.Image:
    W, H_ = 1080, 1350
    img = Image.new("RGB", (W, H_), CREAM)
    d = ImageDraw.Draw(img)
    _header(img, d, 150, "आज का पंचांग  ·  Daily Panchang")

    text(d, (W / 2, 238), hi_date(c.date), display(80, 700), MAROON, "mm")
    text(d, (W / 2, 306), f"{c.wd_hi}  ·  {c.wd_en}", deva(38, 600), INK, "mm")
    info = f"{c.city_hi}  ·  सूर्योदय {c.p['sunrise']}  ·  सूर्यास्त {c.p['sunset']}"
    text(d, (W / 2, 352), info, fit(d, info, lambda s: deva(s, 500), W - 100, 30, 22), "#6A5A4E", "mm")

    y = 388
    if c.today_events:
        name = f"आज  ·  {c.today_events[0]['name']}"
        rrect(d, (60, y, W - 60, y + 58), 29, fill=MARIGOLD)
        text(d, (W / 2, y + 29), name, fit(d, name, lambda s: deva(s, 700), W - 160, 34, 22), INK, "mm")
        y += 78
    row_h, gap = 208, 20
    cw = (W - 120 - gap) // 2
    tsub = f"{c.tithi_en} · {c.paksha_en}" + (f" · till {c.tithi_upto}" if c.tithi_upto else "")
    cells = [
        ("तिथि", "Tithi", c.tithi_hi, tsub),
        ("नक्षत्र", "Nakshatra", c.nak_hi, c.nak_en),
        ("योग", "Yoga", c.yoga_hi, c.yoga_en),
        ("करण", "Karana", c.kar_hi, c.kar_en),
    ]
    for i, (lh, le, vh, ve) in enumerate(cells):
        cx = 60 + (i % 2) * (cw + gap)
        cy = y + (i // 2) * (row_h + gap)
        _elem_card(d, (cx, cy, cx + cw, cy + row_h), lh, le, vh, ve)
    y += 2 * row_h + gap + 18
    tH = 130
    _time_card(d, (60, y, W - 60, y + tH), "अभिजीत मुहूर्त", "Abhijit (auspicious)", c.p.get("abhijit", ""), "good")
    y += tH + 16
    _time_card(d, (60, y, W - 60, y + tH), "राहु काल", "Rahu Kaal (avoid)", c.p.get("rahuKalam", ""), "bad")
    _footer(img, d, H_ - 118, "पूरा पंचांग  ·  jyotishdada.com", "अपने शहर का पंचांग देखें  ·  Free")
    return img


# ───────────────────────────── reel scenes 1080x1920 ─────────────────────────────
def _scene_base(subtitle):
    W, H_ = 1080, 1920
    img = Image.new("RGB", (W, H_), CREAM)
    d = ImageDraw.Draw(img)
    _header(img, d, 200, subtitle)
    _footer(img, d, H_ - 240, "पूरा पंचांग  ·  jyotishdada.com", "Link in bio · बायो में लिंक")
    return img, d


def scene_hook(c: Ctx) -> Image.Image:
    img, d = _scene_base("आज का पंचांग  ·  Daily Panchang")
    W = img.width
    text(d, (W / 2, 350), hi_date(c.date), display(120, 700), MAROON, "mm")
    text(d, (W / 2, 462), f"{c.wd_hi}  ·  {c.wd_en}", deva(52, 600), INK, "mm")
    text(d, (W / 2, 530), f"{c.city_hi}  ·  {c.city_en}", deva(38, 500), "#6A5A4E", "mm")
    rrect(d, (90, 620, W - 90, 1400), 48, fill=WHITE, outline=GOLD, width=4)
    text(d, (W / 2, 705), "आज की तिथि  ·  Tithi", deva(44, 700), MAROON, "mm")
    f = fit(d, c.tithi_hi, lambda s: display(s, 800), W - 260, 230, 100)
    text(d, (W / 2, 925), c.tithi_hi, f, INK, "mm")
    text(d, (W / 2, 1085), c.paksha_hi, deva(64, 600), MAROON, "mm")
    text(d, (W / 2, 1165), f"{c.tithi_en}  ·  {c.paksha_en} Paksha", latin(42, 500), "#6A5A4E", "mm")
    if c.tithi_upto:
        nxt = f"{c.tithi_next_hi} ({c.tithi_next_en})"
        text(d, (W / 2, 1255), f"{c.tithi_upto} तक, फिर {nxt}", fit(d, f"{c.tithi_upto} तक, फिर {nxt}", lambda s: deva(s, 600), W - 220, 40, 26), INDIGO, "mm")
    text(d, (W / 2, 1340), f"सूर्योदय {c.p['sunrise']}   ·   सूर्यास्त {c.p['sunset']}", deva(38, 600), INDIGO, "mm")
    if c.today_events:
        nm = f"आज  ·  {c.today_events[0]['name']}"
        rrect(d, (90, 1470, W - 90, 1570), 50, fill=MARIGOLD)
        text(d, (W / 2, 1520), nm, fit(d, nm, lambda s: deva(s, 700), W - 240, 50, 26), INK, "mm")
    else:
        text(d, (W / 2, 1520), "आज का शुभ-अशुभ समय देखें  ›", deva(46, 700), MAROON, "mm")
    return img


def scene_elements(c: Ctx) -> Image.Image:
    img, d = _scene_base("पंचांग के पाँच अंग  ·  The Five Limbs")
    W = img.width
    text(d, (W / 2, 330), "आज का नक्षत्र, योग और करण", deva(56, 700), MAROON, "mm")
    y = 410
    for lh, le, vh, ve in [("नक्षत्र", "Nakshatra", c.nak_hi, c.nak_en),
                           ("योग", "Yoga", c.yoga_hi, c.yoga_en),
                           ("करण", "Karana", c.kar_hi, c.kar_en)]:
        rrect(d, (90, y, W - 90, y + 370), 40, fill=WHITE, outline=GOLD, width=4)
        text(d, (130, y + 54), f"{lh}  ·  {le}", deva(42, 700), MAROON, "lm")
        f = fit(d, vh, lambda s: display(s, 800), W - 300, 140, 70)
        text(d, (130, y + 220), vh, f, INK, "lm")
        text(d, (130, y + 320), ve, latin(40, 500), "#6A5A4E", "lm")
        y += 400
    return img


def scene_timings(c: Ctx) -> Image.Image:
    img, d = _scene_base("शुभ  ·  अशुभ समय  ·  Timings")
    W = img.width
    p = c.p
    text(d, (W / 2, 320), "आज के शुभ और अशुभ समय", deva(54, 700), MAROON, "mm")
    y, h, g = 380, 196, 22
    rows = [("अभिजीत मुहूर्त", "Abhijit", p.get("abhijit", ""), "good"),
            ("ब्रह्म मुहूर्त", "Brahma Muhurta", p.get("brahmaMuhurta", ""), "good"),
            ("राहु काल", "Rahu Kaal", p.get("rahuKalam", ""), "bad"),
            ("यमगण्ड", "Yamaganda", p.get("yamaganda", ""), "bad"),
            ("गुलिक काल", "Gulika Kaal", p.get("gulikKalam", ""), "bad")]
    for lh, le, v, k in rows:
        _time_card(d, (80, y, W - 80, y + h), lh, le, v, k)
        y += h + g
    return img


def scene_cta(c: Ctx) -> Image.Image:
    img, d = _scene_base("आने वाले पर्व  ·  Upcoming")
    W = img.width
    text(d, (W / 2, 330), "आने वाले पर्व और व्रत", deva(58, 700), MAROON, "mm")
    y = 400
    if not c.upcoming:
        text(d, (W / 2, 800), "अपने शहर का सटीक पंचांग", display(80, 700), INK, "mm")
        text(d, (W / 2, 910), "तिथि · मुहूर्त · कुंडली · व्रत", deva(48, 600), MAROON, "mm")
    for it in c.upcoming:
        day = dt.date.fromisoformat(it["date"])
        rrect(d, (80, y, W - 80, y + 210), 36, fill=WHITE, outline=GOLD, width=4)
        text(d, (120, y + 62), f"{short_hi(day)}  ·  {H.hi(H.WEEKDAY, it['weekday'])}", deva(44, 700), MAROON, "lm")
        nm = it["name"]
        text(d, (120, y + 142), nm, fit(d, nm, lambda s: display(s, 700), W - 280, 70, 36), INK, "lm")
        y += 235
    top = max(y + 10, 1250)
    rrect(d, (80, top, W - 80, top + 190), 36, fill=MARIGOLD)
    text(d, (W / 2, top + 66), "रोज़ सुबह का पंचांग पाने के लिए", deva(44, 700), INK, "mm")
    text(d, (W / 2, top + 128), "फ़ॉलो करें  ·  Follow JyotishDada", deva(44, 700), MAROON, "mm")
    return img


SCENES = [scene_hook, scene_elements, scene_timings, scene_cta]
