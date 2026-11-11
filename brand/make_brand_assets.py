"""One-off: builds every profile/cover image for the new accounts from the site's logo and palette.
    python brand/make_brand_assets.py   ->  brand/generated/*
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import render as R  # noqa: E402

OUT = Path(__file__).resolve().parent / "generated"
OUT.mkdir(exist_ok=True)
logo = Image.open(R.LOGO).convert("RGBA")


def tile(size):
    return logo.resize((size, size), Image.LANCZOS)


# 1. Profile picture. Square, full-bleed maroon, flame centred so every platform's circle crop keeps it whole.
bg = Image.new("RGB", (1080, 1080), R.MAROON)
bg.paste(tile(1080), (0, 0), tile(1080))
bg.save(OUT / "profile_1080.png")
bg.resize((400, 400), Image.LANCZOS).save(OUT / "profile_400.png")

# 2. Facebook cover 1640x624 (shown 820x312 on desktop, centre ~640 px wide on phones: keep text central).
def cover(w, h, safe_w, title_size, sub_size, path):
    img = Image.new("RGB", (w, h), R.MAROON)
    d = ImageDraw.Draw(img)
    d.rectangle((0, h - 10, w, h), fill=R.GOLD)
    t = tile(int(h * 0.30)) if w < 2000 else tile(260)
    cx = w / 2
    img.paste(t, (int(cx - t.width / 2), int(h * 0.12 if w < 2000 else h / 2 - 330)), t)
    ty = h * 0.55 if w < 2000 else h / 2 - 10
    d.text((cx, ty), "JyotishDada", font=R.display(title_size, 700), fill=R.CREAM, anchor="mm")
    sub = "आज का पंचांग  ·  मुहूर्त  ·  कुंडली  ·  व्रत-त्योहार"
    d.text((cx, ty + title_size * 0.75), sub, font=R.fit(d, sub, lambda s: R.deva(s, 600), safe_w, sub_size, 20), fill=R.SOFT_MARIGOLD, anchor="mm")
    d.text((cx, ty + title_size * 1.35), "jyotishdada.com", font=R.latin(int(sub_size * 0.9), 600), fill=R.MARIGOLD, anchor="mm")
    img.save(path, quality=92)


cover(1640, 624, 1000, 96, 46, OUT / "facebook_cover_1640x624.jpg")
# 3. YouTube banner 2560x1440: only the central 1546x423 is visible on every device.
cover(2560, 1440, 1400, 120, 56, OUT / "youtube_banner_2560x1440.jpg")

# 4. Instagram story-highlight covers (1080x1920; the icon area is the centre circle)
for slug, hi_t, en_t in [("panchang", "पंचांग", "Panchang"), ("muhurat", "मुहूर्त", "Muhurat"),
                         ("tyohar", "त्योहार", "Festivals"), ("vrat", "व्रत", "Vrat"), ("kundali", "कुंडली", "Kundali")]:
    im = Image.new("RGB", (1080, 1920), R.MAROON)
    d = ImageDraw.Draw(im)
    d.ellipse((140, 700, 940, 1500), outline=R.GOLD, width=10)
    t = tile(300)
    im.paste(t, (390, 800), t)
    d.text((540, 1250), hi_t, font=R.display(130, 700), fill=R.CREAM, anchor="mm")
    d.text((540, 1370), en_t, font=R.latin(52, 600), fill=R.MARIGOLD, anchor="mm")
    im.save(OUT / f"highlight_{slug}.png")

# 5. First post (pinned): who we are. 1080x1350.
im = Image.new("RGB", (1080, 1350), R.CREAM)
d = ImageDraw.Draw(im)
R._header(im, d, 170, "ज्योतिष दादा  ·  Free Panchang")
d.text((540, 330), "नमस्ते 🙏".replace(" 🙏", ""), font=R.display(120, 700), fill=R.MAROON, anchor="mm")
lines = ["हर सुबह, आपके शहर का", "पंचांग  ·  राहु काल  ·  मुहूर्त", "त्योहार  ·  व्रत  ·  कुंडली", "", "बिल्कुल मुफ़्त  ·  हिंदी + English"]
y = 520
for ln in lines:
    d.text((540, y), ln, font=R.deva(52, 700 if ln and not ln.startswith("बिल्कुल") else 600), fill=R.INK if ln else R.INK, anchor="mm")
    y += 90
R.rrect(d, (120, 1060, 960, 1170), 55, fill=R.MARIGOLD)
d.text((540, 1115), "फ़ॉलो करें  ·  Follow", font=R.deva(52, 700), fill=R.INK, anchor="mm")
R._footer(im, d, 1232, "jyotishdada.com", "रोज़ सुबह ~6 बजे नया पंचांग")
im.save(OUT / "first_post_1080x1350.jpg", quality=92)
print("wrote", *sorted(p.name for p in OUT.iterdir()), sep="\n  ")
