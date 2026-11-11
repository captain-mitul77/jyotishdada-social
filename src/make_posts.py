"""Generate today's assets into out/<date>/ : feed.jpg, story.jpg, reel.mp4, caption_<platform>.txt, meta.json

    python src/make_posts.py                 # today (IST), city from CITY_SLUG (default delhi)
    POST_DATE=2026-11-09 python src/make_posts.py
"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import captions  # noqa: E402
import data  # noqa: E402
import render  # noqa: E402
import video  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "out"


def main() -> Path:
    date = data.today_ist()
    panchang, items = data.fetch_day(date)
    c = render.Ctx(panchang, items, date, data.CITY_SLUG)
    d = OUT / date.isoformat()
    d.mkdir(parents=True, exist_ok=True)

    render.feed_card(c).save(d / "feed.jpg", quality=92, optimize=True)  # Instagram API accepts JPEG only
    scenes = []
    for i, fn in enumerate(render.SCENES, 1):
        p = d / f"scene{i}.jpg"
        fn(c).save(p, quality=92, optimize=True)
        scenes.append(p)
    shutil.copyfile(scenes[0], d / "story.jpg")  # the hook scene doubles as the Story image
    video.build_reel(scenes, d / "reel.mp4")
    for p in scenes:  # keep the published folder small; only feed/story/reel are needed later
        p.unlink()

    for plat in ("instagram", "facebook", "telegram", "youtube"):
        (d / f"caption_{plat}.txt").write_text(captions.build(c, plat), encoding="utf-8")
    meta = {"date": date.isoformat(), "city": data.CITY_SLUG, "youtube_title": captions.youtube_title(c),
            "festival_today": c.today_events[0]["name"] if c.today_events else None}
    (d / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"generated {d}")
    return d


if __name__ == "__main__":
    main()
