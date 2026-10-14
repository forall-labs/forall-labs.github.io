# Forall Labs website

The site for [Forall Labs](https://forall-labs.github.io) — an independent, non-profit,
open research community in AI.

**Live now:** https://forall-labs.github.io (GitHub Pages, free, static only).
**Later:** Cloudflare Pages at `forall-labs.ai` once the domain is bought, which is what
turns the forms on. The build output layout is already the Cloudflare one, so that move
is a settings change rather than a rewrite.

## How it is built

A small Python generator drops each page into one shared template, so the header, nav and
footer are defined once instead of being copy-pasted into a dozen files.

```
site/base.html          the shared chrome: head, header, nav, notice bar, footer
site/pages/*.html       one file per page; first line is a JSON header
site/static/*           copied to the site root as-is (CSS, favicon, og image, robots.txt)
tools/build.py          site/ -> public/
public/                 generated output, git-ignored, rebuilt by CI on every deploy
functions/api/submit.js Cloudflare Pages Function for the forms (unused on GitHub Pages)
schema.sql              creates the submissions table in the D1 database
```

Build it:

```bash
python3 tools/build.py          # writes public/
cd public && python3 -m http.server 8000
```

No dependencies beyond Python 3.

## Adding a page

Create `site/pages/<name>.html` with a JSON header on the first line, then write the body.
`build.py` picks it up automatically and adds it to the sitemap.

```html
<!-- {"url": "/fellowships/", "title": "Fellowships — Forall Labs", "description": "One sentence for search results and link previews."} -->

<section class="page-head">
  <div class="wrap">
    <p class="eyebrow">Fellowships</p>
    <h1>…</h1>
  </div>
</section>
```

| Header key | Meaning |
|---|---|
| `url` | Where it is served. `/x/` becomes `public/x/index.html`; `/404.html` stays a file. |
| `title` | `<title>` tag. |
| `description` | Meta description and link-preview text. |
| `og_title` | Optional. Link-preview title, when it should differ from `title`. |
| `nav` | Optional. Which nav item to highlight, for pages not in the nav themselves. |
| `sitemap` | Optional. `false` keeps the page out of `sitemap.xml`. |

The nav itself lives in the `NAV` list at the top of `tools/build.py`.

## Adding a news post

A post is just a page: `site/pages/news-<slug>.html` with `"url": "/news/<slug>/"` and
`"nav": "/news/"`. Add it to the list in `site/pages/news.html` by hand.

## Writing style

- The name is **Forall Labs** — never `ForAll`.
- The tagline is **"Open research in AI, for all of humanity"** — never "open AI research",
  which reads as OpenAI.

## What does not work on GitHub Pages

`functions/api/submit.js` is a Cloudflare Pages Function. GitHub Pages serves static files
only, so `POST /api/submit` does not exist there. The two form pages ship with their submit
buttons disabled, and a `.notice-bar` banner on every page says so to visitors.

To accept submissions before the domain is ready, point both forms at a free third-party
endpoint (Formspree, Tally, a Google Form) by changing one `action=` attribute per page, and
remove the `disabled` attribute and the `.form-disabled` block.

## Before launch, replace these placeholders

Search the project for `TODO`:

- the Discord invite — five links currently point at the GitHub organisation instead
- the Hugging Face organisation link in the footer, commented out until the org is claimed
- `YOUR-TURNSTILE-SITE-KEY` in `apply.html` and `propose.html`, commented out with the widget

## Moving to Cloudflare once forall-labs.ai is bought

1. **Database:** Cloudflare dashboard → Storage & Databases → D1 → Create, name it
   `forall-labs-db`. Open its Console tab, paste `schema.sql`, and run it.
2. **Spam protection:** Cloudflare dashboard → Turnstile → Add widget for `forall-labs.ai`
   (add your `*.pages.dev` hostname too while testing). The **site key** goes in the two form
   pages; keep the **secret key** for step 4.
3. **Pages project:** Workers & Pages → Create → Pages → Connect to Git → pick this repo.
   - Framework preset: **None**
   - Build command: `python3 tools/build.py`
   - Build output directory: `public`
4. **Settings:** Bindings → add **D1 database**, variable name `DB`, database `forall-labs-db`.
   Variables and Secrets → add `TURNSTILE_SECRET_KEY`, and optionally `DISCORD_WEBHOOK_URL`.
   Redeploy so the settings take effect.
5. **Domain:** Custom domains → add `forall-labs.ai` and `www.forall-labs.ai`.
6. **Turn the forms on:** remove the `disabled` attribute and the `.form-disabled` block from
   `site/pages/apply.html` and `site/pages/propose.html`, uncomment the Turnstile widget and
   script, and remove the `.notice-bar` block from `site/base.html`.
7. **Swap the base URL:** `BASE_URL` in `tools/build.py`, and the `Sitemap:` line in
   `site/static/robots.txt`.
8. **Test:** send yourself an application, then in the D1 Console run
   `SELECT * FROM submissions ORDER BY id DESC LIMIT 5;`

## Reviewing submissions

- Quick look: D1 Console in the Cloudflare dashboard (queries are at the bottom of `schema.sql`).
- Export: `npx wrangler d1 export forall-labs-db --remote --output=submissions.sql`.
- Later: a private `/admin` page behind Cloudflare Access (free for small teams).

## Licence

Site text is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code is open source.
