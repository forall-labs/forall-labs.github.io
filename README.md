# Forall Labs website

The site for [Forall Labs](https://forall-labs.github.io), an open research community in AI.

**Live:** https://forall-labs.github.io, on GitHub Pages (free, static files only). The
forms work through [FormSubmit](https://formsubmit.co), which emails each submission, so
no server of our own is needed.

## How it is built

A small Python generator drops each page into one shared template, so the header, nav and
footer are defined once instead of being copy-pasted into a dozen files.

```
site/base.html          the shared chrome: head, header, nav, footer
site/pages/*.html       one file per page; first line is a JSON header
site/static/*           copied to the site root as-is (CSS, forms.js, favicon, og image)
tools/build.py          site/ -> public/
tools/logo.py           draws the ∀L mark: favicon.svg, logo.svg, the symbol in base.html
tools/og.html           source for og.png (screenshot at 1200x630)
public/                 generated output, git-ignored, rebuilt by CI on every deploy
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
<!-- {"url": "/fellowships/", "title": "Fellowships | Forall Labs", "description": "One sentence for search results and link previews."} -->

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

Plain, confident and short, in the spirit of anthropic.com.

- The name is **Forall Labs**, never `ForAll`.
- The tagline is **"Open research in AI, for all of humanity"**. Never "open AI research",
  which reads as OpenAI.
- **No em or en dashes anywhere** (`—`, `–`, `&mdash;`, `&ndash;`). Use a full stop, a colon
  or a comma. Page titles are `Page | Forall Labs`. Check with
  `grep -rn "—\|–\|&mdash;\|&ndash;" site/`.
- Do not lead with how new the lab is. The founding year (2026, no month) appears on the
  About page only. Toronto is mentioned on About, not in the intro.

## Forms

Every form posts to `FORM_ACTION` in `tools/build.py`, a [FormSubmit](https://formsubmit.co)
address. Pages write `action="{{form_action}}"` and the build fills it in.

- `site/static/forms.js` sends the form in the background and swaps it for the
  confirmation panel named by the form's `data-success` attribute. Without JavaScript the
  form posts normally and FormSubmit redirects to `/thanks/`.
- Hidden fields: `_subject` (email subject), `_template`, `_next` (no-JS redirect),
  `_autoresponse` (the copy sent to the person who submitted), `_honey` (spam trap).
- `/contact/?topic=support` preselects the option with `data-topic="support"`.
- **First use:** FormSubmit emails an activation link to the address the first time a form
  is sent. Until it is clicked, submissions are rejected and the form shows its error
  message. After activating, FormSubmit offers a random alias; put it in `FORM_ACTION` to
  keep the address out of the page source.

## Licence

Site text is [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). Code is open source.
