// Cloudflare Pages Function: POST /api/submit
// One endpoint for every form on the site (join, project proposals, applications, event sign-ups).
// Each HTML form sends a hidden field `form` that says which form it is.
//
// Bindings (set in Cloudflare Pages > Settings > Bindings / Variables):
//   DB                    D1 database (required)
//   TURNSTILE_SECRET_KEY  Turnstile secret (recommended; spam protection is skipped if missing)
//   DISCORD_WEBHOOK_URL   Discord channel webhook for "new submission" pings (optional)

const FORMS = {
  // form id: required fields (everything else is stored as extra data)
  join: ["name", "email"],
  proposal: ["name", "email", "title", "summary"],
  application: ["name", "email", "role", "motivation"],
  event: ["name", "email", "event"],
};

const MAX_FIELD = 5000; // characters per field
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export async function onRequestPost({ request, env }) {
  const wantsJson = (request.headers.get("accept") || "").includes("application/json");
  const fail = (status, message) =>
    wantsJson
      ? Response.json({ ok: false, error: message }, { status })
      : new Response(page("Something went wrong", message), { status, headers: { "content-type": "text/html; charset=utf-8" } });

  let fd;
  try {
    fd = await request.formData();
  } catch {
    return fail(400, "The form could not be read. Please try again.");
  }

  // Honeypot: real people never fill the hidden "website" field.
  if ((fd.get("website") || "").toString().trim() !== "") {
    return redirectOrJson(wantsJson, "/thanks.html");
  }

  const formId = (fd.get("form") || "").toString();
  const required = FORMS[formId];
  if (!required) return fail(400, "Unknown form.");

  // Spam check with Cloudflare Turnstile (free).
  if (env.TURNSTILE_SECRET_KEY) {
    const token = (fd.get("cf-turnstile-response") || "").toString();
    const ok = await verifyTurnstile(token, env.TURNSTILE_SECRET_KEY, request.headers.get("cf-connecting-ip"));
    if (!ok) return fail(400, "The spam check failed. Please reload the page and try again.");
  }

  // Collect fields (multi-select checkboxes become arrays).
  const data = {};
  for (const key of new Set(fd.keys())) {
    if (key === "form" || key === "website" || key === "cf-turnstile-response") continue;
    const values = fd.getAll(key).map((v) => v.toString().trim().slice(0, MAX_FIELD)).filter(Boolean);
    if (values.length) data[key] = values.length === 1 ? values[0] : values;
  }

  for (const field of required) {
    if (!data[field]) return fail(400, `Please fill in "${field}".`);
  }
  const email = String(data.email).toLowerCase();
  if (!EMAIL_RE.test(email)) return fail(400, "Please enter a valid email address.");

  const name = String(data.name);
  delete data.name;
  delete data.email;

  if (!env.DB) return fail(500, "The database is not connected yet (missing DB binding).");

  await env.DB.prepare(
    "INSERT INTO submissions (form, name, email, data, country, user_agent) VALUES (?1, ?2, ?3, ?4, ?5, ?6)"
  )
    .bind(
      formId,
      name,
      email,
      JSON.stringify(data),
      request.headers.get("cf-ipcountry") || null,
      (request.headers.get("user-agent") || "").slice(0, 300)
    )
    .run();

  if (env.DISCORD_WEBHOOK_URL) {
    // Fire and forget; a failed ping must never lose the submission.
    try {
      await fetch(env.DISCORD_WEBHOOK_URL, {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ content: `New **${formId}** submission from ${name}` }),
      });
    } catch {}
  }

  return redirectOrJson(wantsJson, "/thanks.html");
}

export function onRequestGet() {
  return new Response("Use POST.", { status: 405, headers: { allow: "POST" } });
}

async function verifyTurnstile(token, secret, ip) {
  if (!token) return false;
  const body = new FormData();
  body.append("secret", secret);
  body.append("response", token);
  if (ip) body.append("remoteip", ip);
  try {
    const res = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", { method: "POST", body });
    const out = await res.json();
    return out.success === true;
  } catch {
    return false;
  }
}

function redirectOrJson(wantsJson, location) {
  return wantsJson ? Response.json({ ok: true }) : Response.redirect(new URL(location, "https://forall-labs.ai").toString().replace("https://forall-labs.ai", ""), 303);
}

function page(title, message) {
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  return `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>${esc(title)} | Forall Labs</title><link rel="stylesheet" href="/styles.css"></head><body><main class="hero wrap"><p class="eyebrow">Forall Labs</p><h1>${esc(title)}</h1><p class="lead">${esc(message)}</p><div class="actions"><a class="btn primary" href="javascript:history.back()">Go back</a></div></main></body></html>`;
}
