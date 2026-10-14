-- Forall Labs submissions database (Cloudflare D1, which is SQLite).
-- One table holds every form; `form` says which one, `data` holds the form-specific answers as JSON.
-- Run once:  npx wrangler d1 execute forall-labs-db --remote --file=schema.sql

CREATE TABLE IF NOT EXISTS submissions (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  form        TEXT NOT NULL,                      -- join | proposal | application | event
  name        TEXT NOT NULL,
  email       TEXT NOT NULL,
  data        TEXT NOT NULL DEFAULT '{}',         -- JSON of the other answers
  status      TEXT NOT NULL DEFAULT 'new',        -- new | reviewing | accepted | declined
  country     TEXT,                               -- from Cloudflare, two-letter code
  user_agent  TEXT,
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_submissions_form_created ON submissions (form, created_at);
CREATE INDEX IF NOT EXISTS idx_submissions_email ON submissions (email);

-- Handy queries (run in the D1 console in the Cloudflare dashboard):
--   SELECT id, form, name, email, created_at FROM submissions ORDER BY id DESC LIMIT 50;
--   SELECT * FROM submissions WHERE form = 'application' AND status = 'new';
--   UPDATE submissions SET status = 'accepted' WHERE id = 12;
