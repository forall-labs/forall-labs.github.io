# Forall Labs website

A fast static site (plain HTML and CSS, no build step) plus one small serverless function that
stores form submissions.

**Live now:** https://forall-labs.github.io (GitHub Pages, free, static only).
**Later:** Cloudflare Pages at https://forall-labs.ai once the domain is bought, which is what turns
the forms on. The `public/` + `functions/` layout is already the Cloudflare one, so that move is a
settings change, not a rewrite.

## What's inside

| Path | What it is |
|---|---|
| `public/index.html` | Homepage |
| `public/apply.html` | "Join Forall Labs" membership application form |
| `public/propose.html` | "Propose a project" form |
| `public/thanks.html` | Page shown after any form is sent |
| `public/styles.css` | All styling, light and dark mode |
| `public/favicon.svg`, `public/og.png` | Browser icon and link-preview image |
| `public/404.html`, `robots.txt`, `sitemap.xml` | Not-found page and search-engine files |
| `functions/api/submit.js` | Receives every form at `POST /api/submit`, checks it, saves it to the database |
| `schema.sql` | Creates the `submissions` table in the database |

## How the forms work

```
Visitor fills a form  ->  POST /api/submit (Cloudflare Pages Function)
                           |-- spam checks: hidden honeypot field + Cloudflare Turnstile
                           |-- required fields and email checked
                           |-- saved to D1 database, table "submissions"
                           |-- optional ping to a Discord channel
                           -> visitor lands on /thanks.html
```

Every form shares one endpoint. A hidden field `form` names it (`application`, `proposal`, `join`, `event`).
To add a new form (event registration, fellowship application...):

1. Copy `public/apply.html`, change the fields and set `<input type="hidden" name="form" value="event">`.
2. If it is a new form id, add it with its required fields to `FORMS` at the top of `functions/api/submit.js`.

Nothing else changes: new answers are stored as JSON in the `data` column.

## Before you launch, replace these placeholders

Search the project for `YOUR-`:

- `https://discord.gg/YOUR-INVITE` -> your Discord invite link
- `YOUR-TURNSTILE-SITE-KEY` -> your Turnstile site key (in `apply.html` and `propose.html`)
- `https://github.com/forall-labs`, `https://huggingface.co/forall-labs` -> your real org links
- The About paragraph in `index.html` -> your own words

## Deploying today: GitHub Pages (free, no domain needed)

The repo is named `forall-labs.github.io`, so the site serves from the root at
https://forall-labs.github.io and every root-absolute link (`/styles.css`, `/apply.html`) works.

`.github/workflows/pages.yml` publishes `public/` on every push to `main`. Settings -> Pages ->
Source must be set to **GitHub Actions**. Nothing else to configure.

**What does not work on GitHub Pages:** `functions/api/submit.js` is a Cloudflare Pages Function.
GitHub Pages serves static files only, so `POST /api/submit` does not exist there. The two form
pages therefore ship with their submit buttons disabled and a short notice. The `.notice-bar`
banner on every page says the same thing to visitors.

To accept submissions before the domain is ready, point both forms at a free third-party endpoint
(Formspree, Tally, a Google Form) by changing one `action=` attribute per page, and drop the
`disabled` attribute and the `.form-disabled` block.

## Moving to Cloudflare once forall-labs.ai is bought

1. **Database:** Cloudflare dashboard -> Storage & Databases -> D1 -> Create, name it `forall-labs-db`.
   Open its Console tab, paste the contents of `schema.sql`, and run it.
2. **Spam protection:** Cloudflare dashboard -> Turnstile -> Add widget for `forall-labs.ai`
   (also add your `*.pages.dev` hostname while testing). Copy the **site key** into the two form pages,
   keep the **secret key** for step 4.
3. **Pages project:** Workers & Pages -> Create -> Pages -> Connect to Git -> pick this repo.
   - Framework preset: **None**
   - Build command: *(leave empty)*
   - Build output directory: `public`
4. **Settings of the Pages project:**
   - Bindings -> add **D1 database**, variable name `DB`, database `forall-labs-db`.
   - Variables and Secrets -> add secret `TURNSTILE_SECRET_KEY` (from step 2).
   - Optional: secret `DISCORD_WEBHOOK_URL` (Discord channel -> Edit -> Integrations -> Webhooks).
   - Redeploy so the settings take effect.
5. **Domain:** Custom domains -> add `forall-labs.ai` and `www.forall-labs.ai`.
6. **Turn the forms back on:** remove the `disabled` attribute and the `.form-disabled` block from
   `apply.html` and `propose.html`, and remove the `.notice-bar` block from all three pages.
7. **Swap the absolute URLs** in `index.html` (`og:url`, `og:image`), `sitemap.xml` and `robots.txt`
   from `forall-labs.github.io` back to `forall-labs.ai`.
8. **Test:** send yourself an application, then in the D1 Console run
   `SELECT * FROM submissions ORDER BY id DESC LIMIT 5;`

## Reviewing submissions

- Quick look: D1 Console in the Cloudflare dashboard (queries are at the bottom of `schema.sql`).
- Spreadsheet: `npx wrangler d1 export forall-labs-db --remote --output=submissions.sql`, or copy query results.
- Later: a private `/admin` page protected by Cloudflare Access (free for small teams).

## Costs and limits

Free tier: 100,000 function requests per day, D1 with 5 GB and 100,000 writes per day, Turnstile unlimited.
If the lab ever outgrows that, Workers Paid is US$5/month and nothing in the code changes.

## Preview locally

```
cd public && python3 -m http.server 8000
```
Open http://localhost:8000 (forms need the Cloudflare deployment to actually submit).
