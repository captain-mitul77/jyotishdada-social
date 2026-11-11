/**
 * Bug fix (pre-launch cleanup, Aug 2026): the production domain was
 * hardcoded as the literal string "https://example.com" in three
 * separate places (`app/layout.tsx`'s `metadataBase`, `app/sitemap.ts`,
 * `app/robots.ts`) plus now a fourth (festival Event JSON-LD's
 * `organizer.url`) — easy to update 3 of 4 and ship a broken sitemap or
 * OG image URL. One place to change once the real domain is bought.
 *
 * Sprint 50 fix (found live on daily-panchang-iota.vercel.app —
 * `canonical`/`og:image`/`twitter:image` were all literally pointing at
 * `https://example.com`, since `NEXT_PUBLIC_SITE_URL` had never been set
 * in that Vercel project's environment variables): fell back to
 * Vercel's auto-injected `VERCEL_URL`.
 *
 * Sprint 52 fix (found live on the actual redeployed site, immediately
 * after Sprint 50's fix went out): `VERCEL_URL` is the *unique,
 * per-build* deployment hostname (e.g.
 * `daily-panchang-65wpvike4-mjt-eam-space.vercel.app`, a fresh random
 * hash every deploy) — NOT the stable project domain
 * (`daily-panchang-iota.vercel.app`). Sprint 50's fix worked exactly as
 * designed (no more literal "example.com"), but designed around the
 * wrong assumption about what `VERCEL_URL` actually contains, so
 * `canonical`/OG links pointed at a URL that changes on every single
 * future deploy — arguably a subtler bug than the one it replaced,
 * since a real-looking-but-wrong URL is easier to miss than an
 * obviously-fake one. Vercel provides `VERCEL_PROJECT_PRODUCTION_URL`
 * specifically for this — the stable domain assigned to the project's
 * Production environment, unaffected by which specific deployment
 * served the request. Preferred first; `VERCEL_URL` kept as a secondary
 * fallback (correct for preview-deployment URLs specifically, where a
 * per-build hostname is actually the right thing to link to);
 * `example.com` last, for local dev with no Vercel env at all.
 *
 * Setting `NEXT_PUBLIC_SITE_URL` in the Vercel project settings once a
 * real custom domain is bought still takes priority over all fallbacks
 * below and remains the correct final step before launch.
 *
 * Sprint 55 (rebrand, 2026-09-04): site renamed DailyPanchang -> JyotishDada,
 * domain jyotishdada.com purchased. Set NEXT_PUBLIC_SITE_URL=https://jyotishdada.com
 * and NEXT_PUBLIC_SITE_NAME=JyotishDada in the production environment
 * (works on Vercel or a plain VPS .env — this file doesn't care which).
 * The VERCEL_URL fallbacks below are now dead weight if you're moving off
 * Vercel entirely; harmless to leave (they just won't fire), not removed
 * here since a final hosting decision was still open as of this sprint.
 *
 * Sprint 70 update (2026-09-17): the hosting decision referenced above is
 * now resolved — production is confirmed live on Cloudflare (Workers, via
 * the OpenNext adapter) + Render (backend) + Upstash (Redis). There is no
 * Vercel anywhere in the current stack. `NEXT_PUBLIC_SITE_URL` is expected
 * to be set to `https://jyotishdada.com` directly in the Cloudflare
 * project's environment variables (same as it would be set in any other
 * host's env panel — this file still doesn't care which), which takes
 * priority over both fallbacks below, so nothing is broken by leaving
 * them in place. The `VERCEL_PROJECT_PRODUCTION_URL`/`VERCEL_URL`
 * fallbacks are now confirmed genuinely dead code (those env vars will
 * never be set on Cloudflare) — kept rather than removed in this pass
 * since they're harmless no-ops and this session's scope was the ads.txt
 * investigation that surfaced the stale docs, not a code cleanup; safe to
 * delete in a future pass if you want one less thing to read here.
 */
export const SITE_URL =
  process.env.NEXT_PUBLIC_SITE_URL ?? "https://jyotishdada.com";

/**
 * Added Sprint 31 (Privacy/About/Contact content pass) — same one-place-
 * to-change pattern as SITE_URL above. Used by the Privacy Policy, About,
 * and Contact pages so there's a single spot to fill in the real site
 * name and a real inbox before launch, instead of hunting through 3
 * separate page files.
 */
export const SITE_NAME = process.env.NEXT_PUBLIC_SITE_NAME ?? "JyotishDada";

/**
 * Sprint 105 (brand-query SEO): people type the name as one word
 * ("JyotishDada"), two words ("Jyotish Dada") and, in India, in Devanagari.
 * Until this sprint only the one-word form existed anywhere in the HTML or
 * the structured data, so Google had no on-site signal that the spaced
 * query refers to this site. Used as `alternateName` in the sitewide
 * Organization + WebSite JSON-LD (app/layout.tsx) and once in plain visible
 * text on /about. The Devanagari spelling is a straight transliteration
 * chosen by the assistant, NOT confirmed by the owner (logged as 105d).
 */
export const SITE_ALT_NAMES = ["Jyotish Dada", "ज्योतिष दादा"];

/**
 * Sprint 105: a 512x512 static PNG (public/logo-512.png) for the
 * Organization `logo`. The old value, `/icon`, is a 32x32 favicon, below
 * Google's documented logo minimum (112x112), so it could never be used as
 * the site's logo in results. Static file on purpose: Sprint 58 had a 500 /
 * CPU-limit problem with the ImageResponse favicon route on Cloudflare.
 */
export const SITE_LOGO_URL = `${SITE_URL}/logo-512.png`;
export const CONTACT_EMAIL =
  process.env.NEXT_PUBLIC_CONTACT_EMAIL ?? "hellodada@jyotishdada.com";

/**
 * Sprint 55 (launch prep, 2026-09-04): `app/privacy/page.tsx` (Sprint 31)
 * has described Google Analytics + AdSense usage in prose since it was
 * written, but neither was ever actually wired into any component —
 * confirmed by grepping the whole tree for gtag/adsbygoogle/analytics
 * script tags this session and finding zero matches outside that one
 * page's text. That's a real privacy-policy/actual-behavior mismatch,
 * not just a missing feature — flagging it here rather than leaving it
 * implicit. `app/layout.tsx` now loads these scripts, but ONLY when the
 * corresponding env var is set, so nothing changes until real IDs exist:
 * - GA_MEASUREMENT_ID: from Google Analytics (GA4) — "G-XXXXXXXXXX".
 * - ADSENSE_CLIENT_ID: from Google AdSense, after the site is approved —
 *   "ca-pub-XXXXXXXXXXXXXXXX". AdSense approval is a review process (can
 *   take from under a day to a few weeks) — it is NOT something that can
 *   be verified or turned on in this session; do not treat "set the env
 *   var" as equivalent to "ads are approved and live."
 */
export const GA_MEASUREMENT_ID =
  process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID ?? "";
export const ADSENSE_CLIENT_ID =
  process.env.NEXT_PUBLIC_ADSENSE_CLIENT_ID ?? "ca-pub-3293671666670299";

/**
 * Sprint 73: true while CONTACT_EMAIL is still the example.com placeholder.
 * A fake mailbox on the Contact page is itself an AdSense trust problem, so
 * the page hides the mailto link (and says so in dev) until a real inbox is
 * configured via NEXT_PUBLIC_CONTACT_EMAIL.
 *
 * Sprint 91 bug fix: this tested `endsWith("@jyotishdada.com")` — but that
 * is the domain of the REAL, owner-confirmed default above
 * (hellodada@jyotishdada.com), so the flag was permanently `true` and (by
 * the code's logic — not checked against the live site) the Contact page
 * hid the address and told visitors "our public contact inbox is being set
 * up". The placeholder this guards against is the old `hello@example.com`
 * default, so that is what is tested now.
 */
export const CONTACT_EMAIL_IS_PLACEHOLDER =
  CONTACT_EMAIL.endsWith("@example.com");

/**
 * Sprint 73: official social profiles. Every entry is env-driven and only
 * rendered (footer icons + Organization `sameAs` JSON-LD) when a real URL is
 * set — no invented handles. Set once the Facebook/Instagram pages exist:
 *   NEXT_PUBLIC_FACEBOOK_URL=https://www.facebook.com/<page>
 *   NEXT_PUBLIC_INSTAGRAM_URL=https://www.instagram.com/<handle>
 * (Optional: NEXT_PUBLIC_YOUTUBE_URL, NEXT_PUBLIC_TELEGRAM_URL (Sprint 123), NEXT_PUBLIC_X_URL, NEXT_PUBLIC_WHATSAPP_CHANNEL_URL.)
 * NEXT_PUBLIC_* values are inlined at build time on Cloudflare — see the
 * build-vs-runtime env note in DEPLOYMENT.md before assuming a runtime set works.
 */
export const SOCIAL_LINKS: { label: string; href: string }[] = [
  { label: "Facebook", href: process.env.NEXT_PUBLIC_FACEBOOK_URL ?? "" },
  { label: "Instagram", href: process.env.NEXT_PUBLIC_INSTAGRAM_URL ?? "" },
  { label: "YouTube", href: process.env.NEXT_PUBLIC_YOUTUBE_URL ?? "" },
  { label: "Telegram", href: process.env.NEXT_PUBLIC_TELEGRAM_URL ?? "" },
  { label: "X", href: process.env.NEXT_PUBLIC_X_URL ?? "" },
  {
    label: "WhatsApp Channel",
    href: process.env.NEXT_PUBLIC_WHATSAPP_CHANNEL_URL ?? "",
  },
].filter((s) => /^https:\/\//.test(s.href));

/**
 * Sprint 73: Sentry (browser-only) DSN. Empty => Sentry is never loaded.
 * NEXT_PUBLIC_* is inlined at build time, so it must be set on the
 * `npm run cf:deploy` command line (see DEPLOYMENT.md), not in the Cloudflare
 * dashboard runtime variables.
 */
export const SENTRY_DSN =
  process.env.NEXT_PUBLIC_SENTRY_DSN ??
  "https://638e8f80b7041aec2ff6f16adeb0bbcd@o4512119459217408.ingest.de.sentry.io/4512119502995536";
