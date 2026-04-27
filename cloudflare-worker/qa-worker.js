/*
 * SPO Incentives — Q&A Worker
 *
 * Backs the inline "Ask the authors" feature on the static site.
 *
 * Endpoints
 * ---------
 *   POST /qa
 *     Form fields: finding, page, q, email (optional)
 *     Stores the question in KV under qa:queue:<finding>:<ulid> and
 *     emails the team via MailChannels.
 *
 *   GET /qa/<finding>
 *     Returns approved answers for that finding as JSON:
 *     { answers: [{author, date, html, text}] }
 *     Approved answers live under qa:answer:<finding>:<id>.
 *
 *   POST /qa/answer  (admin only — guarded by ADMIN_TOKEN)
 *     Form fields: finding, author, html, text, date
 *     Adds an answer that the GET endpoint will surface inline.
 *
 * KV layout
 * ---------
 *   qa:queue:<finding>:<ulid>   -> { question, email, page, ts }
 *   qa:answer:<finding>:<id>    -> { author, date, html, text }
 *
 * Bindings expected (set in wrangler.toml)
 * ----------------------------------------
 *   QA           — KV namespace for storage
 *   FROM_EMAIL   — sender (e.g. "qa@yourdomain.tld")
 *   TO_EMAIL     — recipient list, comma-separated
 *   ADMIN_TOKEN  — shared secret guarding /qa/answer
 *   ALLOWED_ORIGIN — site origin (e.g. "https://input-output-hk.github.io")
 */

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const allowedOrigin = env.ALLOWED_ORIGIN || "*";
    const cors = {
      "Access-Control-Allow-Origin": allowedOrigin,
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Accept",
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: cors });
    }

    // POST /qa  — submit a question
    if (url.pathname === "/qa" && request.method === "POST") {
      return await handleSubmit(request, env, cors);
    }

    // POST /qa/answer  — admin posts an answer
    if (url.pathname === "/qa/answer" && request.method === "POST") {
      return await handleAnswer(request, env, cors);
    }

    // GET /qa/<finding>  — fetch approved answers
    const m = url.pathname.match(/^\/qa\/([A-Z0-9.\-_]+)$/i);
    if (m && request.method === "GET") {
      return await handleList(m[1], env, cors);
    }

    return new Response("Not found", { status: 404, headers: cors });
  },
};

async function handleSubmit(request, env, cors) {
  const form = await request.formData();
  const finding = (form.get("finding") || "").toString().trim();
  const page = (form.get("page") || "").toString().trim();
  const q = (form.get("q") || "").toString().trim();
  const email = (form.get("email") || "").toString().trim();

  if (!finding || !q) {
    return json({ ok: false, error: "missing_fields" }, 400, cors);
  }
  if (q.length > 4000) {
    return json({ ok: false, error: "too_long" }, 413, cors);
  }
  if (!/^[A-Z]{3}\.O\d+(\.F\d+)?$/i.test(finding)) {
    return json({ ok: false, error: "bad_finding_id" }, 400, cors);
  }

  const id = ulid();
  const key = `qa:queue:${finding}:${id}`;
  const record = {
    finding,
    page,
    question: q,
    email,
    ts: Date.now(),
  };
  await env.QA.put(key, JSON.stringify(record), {
    expirationTtl: 60 * 60 * 24 * 365,
  });

  // Notify the team via MailChannels (free for Cloudflare Workers).
  if (env.FROM_EMAIL && env.TO_EMAIL) {
    try {
      await sendEmail(env, finding, page, q, email);
    } catch (e) {
      // Mail failure is non-blocking; the question is in KV.
    }
  }

  return json({ ok: true, id }, 200, cors);
}

async function handleAnswer(request, env, cors) {
  const auth = request.headers.get("Authorization") || "";
  const token = auth.replace(/^Bearer\s+/, "");
  if (!env.ADMIN_TOKEN || token !== env.ADMIN_TOKEN) {
    return json({ ok: false, error: "unauthorized" }, 401, cors);
  }
  const form = await request.formData();
  const finding = (form.get("finding") || "").toString().trim();
  const author = (form.get("author") || "IO Research").toString().trim();
  const html = (form.get("html") || "").toString();
  const text = (form.get("text") || "").toString();
  const date = (form.get("date") || new Date().toISOString().slice(0, 10))
    .toString();
  if (!finding || (!html && !text)) {
    return json({ ok: false, error: "missing_fields" }, 400, cors);
  }
  const id = ulid();
  const key = `qa:answer:${finding}:${id}`;
  await env.QA.put(
    key,
    JSON.stringify({ author, date, html, text }),
    { expirationTtl: 60 * 60 * 24 * 365 * 5 }
  );
  return json({ ok: true, id }, 200, cors);
}

async function handleList(finding, env, cors) {
  const list = await env.QA.list({ prefix: `qa:answer:${finding}:` });
  const answers = [];
  for (const k of list.keys) {
    const v = await env.QA.get(k.name, "json");
    if (v) answers.push(v);
  }
  // Most recent first.
  answers.sort((a, b) => (b.date || "").localeCompare(a.date || ""));
  return json({ answers }, 200, cors);
}

function json(payload, status, cors) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}

function ulid() {
  // Compact, sortable, URL-safe id. Not cryptographically strong; fine for
  // public-write rate-limited records.
  const rnd = crypto.getRandomValues(new Uint8Array(10));
  const t = Date.now().toString(36);
  const r = Array.from(rnd, (b) => b.toString(36).padStart(2, "0")).join("");
  return `${t}-${r.slice(0, 12)}`;
}

async function sendEmail(env, finding, page, question, replyEmail) {
  const subject = `[SPO Q&A] ${finding} — new reader question`;
  const body = [
    `Finding: ${finding}`,
    `Page: ${page}`,
    `Reply-to: ${replyEmail || "(not provided)"}`,
    "",
    question,
  ].join("\n");

  const recipients = (env.TO_EMAIL || "")
    .split(",")
    .map((e) => e.trim())
    .filter(Boolean)
    .map((e) => ({ email: e }));

  await fetch("https://api.mailchannels.net/tx/v1/send", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      personalizations: [{ to: recipients }],
      from: { email: env.FROM_EMAIL, name: "SPO Incentives Q&A" },
      reply_to: replyEmail ? { email: replyEmail } : undefined,
      subject,
      content: [{ type: "text/plain", value: body }],
    }),
  });
}
