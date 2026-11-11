"""Publish today's generated assets. Every platform is optional: it runs only when its secrets are present,
a failure on one never blocks the others, and posted.json stops a re-run from double-posting.

    python src/publish.py out/2026-11-09 [--dry-run]

Environment (all GitHub Actions secrets; see SOCIAL_PLAYBOOK.md):
  PAGES_BASE_URL                 public folder that serves out/ (GitHub Pages), e.g. https://user.github.io/repo/media
  TELEGRAM_BOT_TOKEN  TELEGRAM_CHANNEL (@name)  TELEGRAM_ADMIN_CHAT_ID (optional private copy for manual posting)
  META_PAGE_ID  META_PAGE_TOKEN  IG_USER_ID  [GRAPH_VERSION]
  YT_CLIENT_ID  YT_CLIENT_SECRET  YT_REFRESH_TOKEN  [YT_PRIVACY=private|public|unlisted]
  PLATFORMS=telegram,facebook,instagram,youtube   (default: all that have credentials)
"""
import json
import os
import sys
import time
from pathlib import Path

import requests

GRAPH_VERSION = os.environ.get("GRAPH_VERSION", "v23.0")
GRAPH = os.environ.get("GRAPH_BASE", f"https://graph.facebook.com/{GRAPH_VERSION}")
TG = os.environ.get("TG_BASE", "https://api.telegram.org")
YT_OAUTH = os.environ.get("YT_OAUTH_URL", "https://oauth2.googleapis.com/token")
YT_UPLOAD = os.environ.get("YT_UPLOAD_URL", "https://www.googleapis.com/upload/youtube/v3/videos")
E = os.environ.get


def _check(r: requests.Response, what: str) -> dict:
    if r.status_code >= 400:
        raise RuntimeError(f"{what}: HTTP {r.status_code} {r.text[:400]}")
    try:
        return r.json()
    except ValueError:
        return {}


def wait_for_url(url: str, want: str, timeout=600):
    """GitHub Pages needs a minute or two after the push. Instagram/Facebook fetch the file themselves,
    so don't start until it is really served with the right content-type."""
    end = time.time() + timeout
    while time.time() < end:
        try:
            r = requests.head(url, timeout=20, allow_redirects=True)
            if r.status_code == 200 and r.headers.get("content-type", "").startswith(want):
                return
        except requests.RequestException:
            pass
        time.sleep(10)
    raise RuntimeError(f"media URL never became available as {want}: {url}")


# ───────────────────────── Telegram ─────────────────────────
def telegram(d: Path, base: str, meta: dict):
    tok, chan, admin = E("TELEGRAM_BOT_TOKEN"), E("TELEGRAM_CHANNEL"), E("TELEGRAM_ADMIN_CHAT_ID")
    cap = (d / "caption_telegram.txt").read_text(encoding="utf-8")
    api = f"{TG}/bot{tok}"
    with open(d / "feed.jpg", "rb") as f:
        _check(requests.post(f"{api}/sendPhoto", data={"chat_id": chan, "caption": cap},
                             files={"photo": f}, timeout=120), "telegram sendPhoto")
    with open(d / "reel.mp4", "rb") as f:
        _check(requests.post(f"{api}/sendVideo", data={"chat_id": chan, "supports_streaming": "true",
                                                       "width": 1080, "height": 1920, "caption": cap},
                             files={"video": f}, timeout=300), "telegram sendVideo")
    if admin:  # private copy + full captions so you can post to X / WhatsApp Channel / YouTube Shorts by hand
        with open(d / "reel.mp4", "rb") as f:
            _check(requests.post(f"{api}/sendVideo", data={"chat_id": admin, "caption": "Reel for manual platforms"},
                                 files={"video": f}, timeout=300), "telegram admin video")
        full = (f"YouTube title:\n{meta['youtube_title']}\n\n--- Instagram/Facebook caption ---\n"
                + (d / "caption_instagram.txt").read_text(encoding="utf-8"))
        _check(requests.post(f"{api}/sendMessage", data={"chat_id": admin, "text": full[:4000]}, timeout=60),
               "telegram admin text")


# ───────────────────────── Facebook Page ─────────────────────────
def facebook(d: Path, base: str, meta: dict):
    pid, tok = E("META_PAGE_ID"), E("META_PAGE_TOKEN")
    cap = (d / "caption_facebook.txt").read_text(encoding="utf-8")
    _check(requests.post(f"{GRAPH}/{pid}/photos", data={"url": f"{base}/feed.jpg", "caption": cap,
                                                         "access_token": tok}, timeout=120), "facebook photo")
    # Reel: documented 3-step flow (start -> upload by hosted URL -> finish)
    s = _check(requests.post(f"{GRAPH}/{pid}/video_reels", data={"upload_phase": "start", "access_token": tok},
                             timeout=60), "facebook reel start")
    _check(requests.post(s["upload_url"], headers={"Authorization": f"OAuth {tok}", "file_url": f"{base}/reel.mp4"},
                         timeout=300), "facebook reel upload")
    _check(requests.post(f"{GRAPH}/{pid}/video_reels", data={"upload_phase": "finish", "video_id": s["video_id"],
                                                              "video_state": "PUBLISHED", "description": cap,
                                                              "access_token": tok}, timeout=120), "facebook reel finish")


# ───────────────────────── Instagram ─────────────────────────
def _ig(kind: str, url: str, caption: str | None):
    ig, tok = E("IG_USER_ID"), E("META_PAGE_TOKEN")
    p = {"access_token": tok}
    if kind == "image":
        p.update(image_url=url, caption=caption)
    elif kind == "story":
        p.update(media_type="STORIES", image_url=url)
    else:
        p.update(media_type="REELS", video_url=url, caption=caption, share_to_feed="true")
    cid = _check(requests.post(f"{GRAPH}/{ig}/media", data=p, timeout=120), f"instagram {kind} container")["id"]
    end = time.time() + 600
    while True:  # video containers process asynchronously; publish only once FINISHED
        st = _check(requests.get(f"{GRAPH}/{cid}", params={"fields": "status_code", "access_token": tok},
                                 timeout=60), "instagram status").get("status_code")
        if st in ("FINISHED", "PUBLISHED"):
            break
        if st in ("ERROR", "EXPIRED") or time.time() > end:
            raise RuntimeError(f"instagram {kind} container ended as {st or 'timeout'}")
        time.sleep(8)
    _check(requests.post(f"{GRAPH}/{ig}/media_publish", data={"creation_id": cid, "access_token": tok},
                         timeout=120), f"instagram {kind} publish")


def instagram(d: Path, base: str, meta: dict):
    cap = (d / "caption_instagram.txt").read_text(encoding="utf-8")
    _ig("image", f"{base}/feed.jpg", cap)
    _ig("story", f"{base}/story.jpg", None)
    _ig("reel", f"{base}/reel.mp4", cap)


# ───────────────────────── YouTube ─────────────────────────
def youtube(d: Path, base: str, meta: dict):
    """NOTE: videos uploaded through the API by a Google Cloud project that has not passed YouTube's API
    compliance audit are forced to PRIVATE, whatever privacyStatus says. Default is private for that reason."""
    tok = _check(requests.post(YT_OAUTH, data={"client_id": E("YT_CLIENT_ID"), "client_secret": E("YT_CLIENT_SECRET"),
                                               "refresh_token": E("YT_REFRESH_TOKEN"), "grant_type": "refresh_token"},
                               timeout=60), "youtube token")["access_token"]
    body = {"snippet": {"title": meta["youtube_title"], "description": (d / "caption_youtube.txt").read_text(encoding="utf-8"),
                        "categoryId": "22", "defaultLanguage": "hi"},
            "status": {"privacyStatus": E("YT_PRIVACY", "private"), "selfDeclaredMadeForKids": False}}
    size = (d / "reel.mp4").stat().st_size
    init = requests.post(YT_UPLOAD, params={"uploadType": "resumable", "part": "snippet,status"},
                         headers={"Authorization": f"Bearer {tok}", "X-Upload-Content-Type": "video/mp4",
                                  "X-Upload-Content-Length": str(size)}, json=body, timeout=60)
    _check(init, "youtube init")
    with open(d / "reel.mp4", "rb") as f:
        _check(requests.put(init.headers["Location"], data=f, headers={"Content-Type": "video/mp4"}, timeout=600),
               "youtube upload")


REQUIRED = {
    "telegram": ["TELEGRAM_BOT_TOKEN", "TELEGRAM_CHANNEL"],
    "facebook": ["META_PAGE_ID", "META_PAGE_TOKEN"],
    "instagram": ["IG_USER_ID", "META_PAGE_TOKEN"],
    "youtube": ["YT_CLIENT_ID", "YT_CLIENT_SECRET", "YT_REFRESH_TOKEN"],
}
RUNNERS = {"telegram": telegram, "facebook": facebook, "instagram": instagram, "youtube": youtube}


def main(argv):
    d = Path(argv[1])
    dry = "--dry-run" in argv
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    ledger_path = d / "posted.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    base = f"{E('PAGES_BASE_URL', '').rstrip('/')}/{d.name}"
    wanted = [p.strip() for p in E("PLATFORMS", ",".join(RUNNERS)).split(",") if p.strip()]
    failures = []
    waited = False
    for plat in wanted:
        missing = [k for k in REQUIRED[plat] if not E(k)]
        if missing:
            print(f"[{plat}] skipped (missing {', '.join(missing)})")
            continue
        if ledger.get(plat) == "ok":
            print(f"[{plat}] already posted today, skipping")
            continue
        if dry:
            print(f"[{plat}] would post {d}")
            continue
        try:
            if plat in ("facebook", "instagram") and not waited:  # Meta pulls media from our public URL
                wait_for_url(f"{base}/feed.jpg", "image/jpeg")
                wait_for_url(f"{base}/reel.mp4", "video/")
                waited = True
            RUNNERS[plat](d, base, meta)
            ledger[plat] = "ok"
            print(f"[{plat}] posted")
        except Exception as e:  # noqa: BLE001 - isolate platforms from each other
            ledger[plat] = f"error: {e}"[:500]
            failures.append(plat)
            print(f"[{plat}] FAILED: {e}", file=sys.stderr)
        ledger_path.write_text(json.dumps(ledger, ensure_ascii=False, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
