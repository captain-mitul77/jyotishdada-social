# JyotishDada social launch playbook (all free)

Everything here costs ₹0. Items marked **[UNVERIFIED]** could not be checked from the build environment (no real
accounts, no way to call Meta/YouTube/Telegram for real). They are also listed as follow-ups 123a–123h in the website
repo's `SPRINT_LOG.md`. Platform rules change often; re-check the linked rule before relying on it.

## 0. What is automatic and what is not

| Network | Fully automatic and free? | How |
|---|---|---|
| **Telegram channel** | Yes | Bot API, photo + reel video, every morning |
| **Facebook Page** | Yes **[UNVERIFIED]** | Graph API: photo + Reel, Page token |
| **Instagram** (feed, Story, Reel) | Yes **[UNVERIFIED]** | Graph API. Needs a Professional account linked to a Facebook Page; images must be **JPEG**; media must be on a public URL (we use GitHub Pages) |
| **YouTube Shorts** | **No, not publicly.** | API uploads from a Google project that has not passed YouTube's API audit are forced to **private**. Use the weekly batch + YouTube Studio's free scheduler (section 6), or apply for the audit later |
| **X (Twitter)** | **No (not free)** | The free API tier was closed to new developers in Feb 2026; posting is pay-per-use (about $0.015 per post, $0.20 if it has a link). Post by hand from the Telegram copy, or skip X |
| **WhatsApp Channel** | No | There is no posting API. Forward the Telegram post by hand (10 seconds) |

Instagram's API limit (100 API posts per 24 h) is far above our 3 a day.

## 1. Names, handles and branding

* **Display name:** `JyotishDada | Daily Panchang` (Instagram name field: `JyotishDada – आज का पंचांग`).
* **Handle:** try `@jyotishdada` on every network. If taken: `@jyotish.dada`, `@jyotishdada.official`, `@jyotishdada_in`. Use the **same** handle everywhere. Availability **[UNVERIFIED]**.
* **One email for all accounts:** the Contact page already publishes `hellodada@jyotishdada.com`; use it as the login/recovery email (create it in Cloudflare Email Routing → forward to your Gmail, free). Turn on 2-step verification on every account and save recovery codes.
* **Profile picture:** `brand/generated/profile_1080.png` (maroon tile + diya flame, safe for circle crops). Same image on every network.
* **Covers:** Facebook `facebook_cover_1640x624.jpg`, YouTube `youtube_banner_2560x1440.jpg`, Instagram Highlights `highlight_*.png`, first pinned post `first_post_1080x1350.jpg`. Regenerate with `python brand/make_brand_assets.py`.
* **Colours / fonts** (same as the site): maroon `#6B1E23`, marigold `#E8A33D`, gold `#C9A227`, cream `#FBF3E7`; Eczar + Noto Sans Devanagari.

## 2. Bios (copy-paste; lengths checked)

| Where | Text |
|---|---|
| **Instagram bio** (≤150, now 109) | `🪔 रोज़ का पंचांग · राहु काल · मुहूर्त · व्रत-त्योहार` ⏎ `Free Hindu Panchang & Jyotish tools` ⏎ `👇 अपने शहर का पंचांग` — website field: `https://jyotishdada.com/panchang/delhi/dainik?utm_source=instagram&utm_medium=bio` |
| **Facebook intro** (≤101, now 88) | `रोज़ का पंचांग, मुहूर्त, व्रत-त्योहार और कुंडली — मुफ़्त। Free Hindu Panchang & Jyotish.` Category: **Education** or **Website** (avoid "Astrologer & Psychic": stricter ad and monetisation policies) |
| **Telegram description** (≤255, now 148) | `🪔 हर सुबह ~6 बजे आज का पंचांग: तिथि, नक्षत्र, योग, राहु काल, अभिजीत मुहूर्त। व्रत-त्योहार की तारीखें। Free daily Hindu Panchang from jyotishdada.com` |
| **YouTube description** | `JyotishDada पर रोज़ सुबह आज का पंचांग: तिथि, नक्षत्र, योग, राहु काल और अभिजीत मुहूर्त, हिंदी में। पूरा पंचांग, मुहूर्त, कुंडली और व्रत-त्योहार: https://jyotishdada.com` |
| **X bio** (optional) | `रोज़ का पंचांग, राहु काल, मुहूर्त और व्रत-त्योहार। Free daily Hindu Panchang & Jyotish tools. jyotishdada.com` |

**Pinned first post** (use `first_post_1080x1350.jpg`): `नमस्ते 🙏 JyotishDada पर हर सुबह आपके शहर का पंचांग, राहु काल, मुहूर्त और व्रत-त्योहार, मुफ़्त। फ़ॉलो करें और अपना शहर बताएँ! 👇 jyotishdada.com`

## 3. Create the accounts (do in this order)

### 3.1 Facebook Page (needed first: Instagram automation depends on it)
1. Log in to a personal Facebook profile (the Page needs a human admin; it stays private).
2. Menu → **Pages → Create new Page**. Name, category (above), bio. Upload profile picture and cover.
3. Add the website, email and "Open" hours not needed. Create a button: **Learn more → https://jyotishdada.com**.
4. Post the first-post image so the Page is not empty.

### 3.2 Instagram
1. Create the account with the shared email. Handle and name from section 1.
2. Profile → **Edit profile → Switch to professional account** (Business; creators may not be supported by the publishing API, so choose Business). Category: *Education* or *Website*.
3. **Edit profile → Page → connect the Facebook Page** from 3.1.
4. Upload picture, bio, website link. Post `first_post_1080x1350.jpg`; add the 5 highlight covers (create empty Highlights, set covers).

### 3.3 Telegram channel
1. Telegram → New Channel → name `JyotishDada | आज का पंचांग`, **Public**, link `t.me/jyotishdada`.
2. Open **@BotFather** → `/newbot` → name `JyotishDada Bot`, username must end in `bot` (e.g. `jyotishdada_bot`). Copy the **bot token** → secret `TELEGRAM_BOT_TOKEN`.
3. Channel → Administrators → add the bot, allow **Post messages**.
4. Secret `TELEGRAM_CHANNEL` = `@jyotishdada`.
5. Optional private copy (to hand-post to X, WhatsApp, Shorts): message your bot once, open `https://api.telegram.org/bot<TOKEN>/getUpdates`, copy `message.chat.id` → secret `TELEGRAM_ADMIN_CHAT_ID`.

### 3.4 YouTube
1. Sign in with the shared Google account → profile → **Create a channel** → name, handle `@jyotishdada`.
2. **Customize channel**: picture, banner, description. **Verify your phone** at youtube.com/verify (needed for uploads over 15 min and custom thumbnails; harmless to do now).
3. Uploading is done through the weekly batch (section 6).

### 3.5 WhatsApp Channel (manual)
WhatsApp → Updates → **+** → New channel → same name/picture. Paste the channel link into the website env var (section 8). Forward each Telegram post.

### 3.6 X (optional, manual)
Create `@jyotishdada`, add bio and picture. No automation (not free).

## 4. One-time automation setup (about 45 minutes)

### 4.1 GitHub repo and Pages (free; hosting for media and the scheduler)
1. Create a **public** GitHub repo `jyotishdada-social` and push this folder. (Public repos get unlimited free Actions minutes; the repo holds no secrets.)
2. After the first workflow run creates the `gh-pages` branch: **Settings → Pages → Deploy from a branch → `gh-pages` / root**.
3. Repo → Settings → **Secrets and variables → Actions**. Add secrets as you finish each section. Optional **Variables**: `CITY_SLUG` (default `delhi`), `API_BASE`, `YT_PRIVACY`, `GRAPH_VERSION`, `PLATFORMS`.
4. Run **Actions → Daily social post → Run workflow** with `dry_run = true` first. Check the generated images in the run's artifact, then run it once for real.

### 4.2 Meta (Facebook + Instagram) secrets **[UNVERIFIED end to end]**
1. developers.facebook.com → log in with the Facebook profile that admins the Page → **Create app** (use case: *Other* / type *Business*). Keep it in **Development mode**; as the app's admin you can post to your own Page and Instagram without App Review (**[UNVERIFIED]**; if Meta asks for review, see follow-up 123c).
2. Add products: **Facebook Login** (for Business) and the **Instagram** product that uses Facebook Login (not "Instagram Login").
3. Open **Tools → Graph API Explorer**, choose your app, add permissions: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`. **Generate Access Token** and approve your Page and Instagram account.
4. Make it long-lived: `GET /oauth/access_token?grant_type=fb_exchange_token&client_id=<APP_ID>&client_secret=<APP_SECRET>&fb_exchange_token=<SHORT_TOKEN>`.
5. Get the **Page token** (does not expire when made from a long-lived user token): `GET /me/accounts?access_token=<LONG_TOKEN>` → copy `id` → secret `META_PAGE_ID`, `access_token` → secret `META_PAGE_TOKEN`.
6. Instagram id: `GET /<PAGE_ID>?fields=instagram_business_account&access_token=<PAGE_TOKEN>` → `instagram_business_account.id` → secret `IG_USER_ID`.
7. Check the cap any time: `GET /<IG_USER_ID>/content_publishing_limit`.
8. If a post fails with an auth error months later, repeat steps 3 to 5 (token revoked, password changed, or permissions changed).

### 4.3 YouTube API (optional, only if you want API uploads; they stay private until audited)
Google Cloud Console → new project → enable **YouTube Data API v3** → OAuth consent screen (External) → **publish the app to "In production"** (in "Testing" the refresh token dies after 7 days) → OAuth client (Desktop) → run a one-time consent with scope `https://www.googleapis.com/auth/youtube.upload` to get a refresh token → secrets `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`. Uploads arrive as **private**; to publish them automatically you must pass Google's API Services audit (form linked from the API docs). Most people should skip this and use section 6.

## 5. What gets posted every day (about 05:53 IST)

| Output | Where | Content |
|---|---|---|
| `feed.jpg` 1080×1350 | Instagram feed, Facebook, Telegram | Hindi date, tithi (with "till HH:MM"), nakshatra, yoga, karana, Abhijit, Rahu Kaal, festival banner when today has one |
| `story.jpg` 1080×1920 | Instagram Story | Tithi hook |
| `reel.mp4` 1080×1920, 18.8 s | Instagram Reel, Facebook Reel, Telegram, Shorts (manual) | 4 scenes: tithi → nakshatra/yoga/karana → shubh/ashubh timings → upcoming festivals + follow |
| Captions | all | Hindi + short English line, UTM-tagged link to `/panchang/<city>/dainik` |

Every number comes from the live `GET /api/panchang` (`Panchang` type) and `GET /api/festivals` feed: nothing is calculated or invented by the bot. Hindi names come from fixed tables (`src/hindi.py`); a name with no entry is shown in the API's English spelling.

**Do not** auto-post the Rashifal: the `/api/jyotish/rashifal` text is general template content, not a computed prediction, and auto-posting it daily as if it were would hurt trust.

## 6. Shorts and manual-network routine (5 minutes a week)
1. Every Sunday the **Weekly batch** workflow builds the next 7 days. Download the `week-batch` artifact.
2. **YouTube Studio → Create → Upload videos**: select the 7 `reel.mp4` files, set the title from each `meta.json` (`youtube_title`), description from `caption_youtube.txt`, **Visibility → Schedule** at 06:00 IST each day. Shorts are detected automatically (vertical, under 3 minutes).
3. The same files can be scheduled in the Instagram app (Reels → Advanced settings → Schedule) or Meta Business Suite if you want a second safety net.
4. Daily, from the private Telegram copy: forward to the WhatsApp Channel; post to X if you want it.

## 7. Growth: getting people to the site
* **Be consistent at one time** (06:00 IST): people check the panchang at dawn.
* **Link every post to a deep page** (`/panchang/<city>/dainik`); Instagram captions are not clickable, so the bio link carries the traffic, and captions say "लिंक बायो में".
* **Measure it:** the links carry `utm_source=<network>`. In GA4 look at *Reports → Acquisition → Traffic acquisition* filtered on medium `social`. (GA4 is only live if `NEXT_PUBLIC_GA_MEASUREMENT_ID` is set in production; the PRD records that as unconfirmed.)
* **Other cities:** the default is Delhi. For Mumbai/Ahmedabad etc. either change `CITY_SLUG`, or later duplicate the job per city (follow-up 123d).
* **Hook ideas that fit the data we already have:** "राहु काल कब है?", "आज का शुभ मुहूर्त", "इस हफ्ते के व्रत-त्योहार", festival countdown 3 days ahead, Ekadashi/Purnima/Amavasya alerts.
* **Engage:** answer comments in Hindi within a day; ask "आपके शहर का पंचांग चाहिए?" and use the answers to choose cities.
* **Do not**: buy followers, join engagement pods, ask anyone to click ads, or post health/finance/marriage promises. Social traffic is welcome for the AdSense re-application, but invalid-traffic tricks are the fastest way to fail it.
* Reach is not guaranteed. Expect slow growth for the first 2 to 3 months; judge by saves/shares and site visits, not just followers.

## 8. Wire the accounts into the website
The footer, Contact page and Organization `sameAs` JSON-LD already render from `SOCIAL_LINKS`. Set these as **build-time** env vars (they are inlined at build, see `DEPLOYMENT.md` on the Cloudflare gotcha), then redeploy:
```
NEXT_PUBLIC_FACEBOOK_URL=https://www.facebook.com/<page>
NEXT_PUBLIC_INSTAGRAM_URL=https://www.instagram.com/jyotishdada
NEXT_PUBLIC_YOUTUBE_URL=https://www.youtube.com/@jyotishdada
NEXT_PUBLIC_TELEGRAM_URL=https://t.me/jyotishdada      # needs the one-line change in frontend-patch/
NEXT_PUBLIC_WHATSAPP_CHANNEL_URL=https://whatsapp.com/channel/<id>
NEXT_PUBLIC_X_URL=https://x.com/jyotishdada
```
Only add a URL once the account exists and has content: Google reads these as `sameAs` identity signals.

## 9. Daily health check and troubleshooting
* GitHub emails you when a run fails. Failed platforms are listed in `out/<date>/posted.json` (also on the `gh-pages` branch).
* Backend asleep (Render free plan): the job retries for several minutes. Your keep-alive Worker should prevent this.
* Instagram `ERROR` container: usually the image is not JPEG, the video is not H.264/AAC, or the media URL was not yet live. Re-run the workflow with `platforms=instagram`; the ledger prevents double posts to the others.
* `workflow_dispatch` with `post_date` back-fills a missed day.
* Scheduled workflows in public repos pause after 60 days without repo activity; the job commits an empty keep-alive when needed **[UNVERIFIED]**.

## 10. Skills / connectors that would help
None are required. Useful if you add them: a **GitHub** connector (I could push this repo and read workflow failures), **Google Drive** (store brand files), and Claude Code or Cowork if you want me to run `git`/`gh` for you directly. Everything above works without them.
