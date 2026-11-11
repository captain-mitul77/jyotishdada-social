# jyotishdada-social

Free daily social automation for JyotishDada: builds a Hindi/English Panchang card, Story and 18.8 s Reel from the live
API, hosts them on GitHub Pages, and posts to Telegram, Facebook and Instagram from GitHub Actions. Setup: **SOCIAL_PLAYBOOK.md**.

```bash
pip install -r requirements.txt        # also needs ffmpeg and libraqm (Devanagari shaping)
API_BASE=http://localhost:8000 POST_DATE=2026-11-09 python src/make_posts.py   # -> out/2026-11-09/
python src/publish.py out/2026-11-09 --dry-run
DAYS=7 python src/make_week.py                                                  # weekly Shorts batch
python brand/make_brand_assets.py                                               # avatars, covers, highlights
```
Layout: `src/data.py` (API), `render.py` (images), `video.py` (ffmpeg), `captions.py`, `hindi.py`, `publish.py`, `.github/workflows/`.
No new API shapes: only the site's `Panchang` fields and the `/api/festivals` feed items are read.
