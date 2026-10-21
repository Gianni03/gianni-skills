#!/usr/bin/env python3
"""Score job candidates for fit and render a clickable report.

    render.py score  --results FILE [--out FILE]
    render.py build  --results FILE --out-dir DIR [--date YYYY-MM-DD]

`score` applies the role/stack/eligibility rules and tags each job with `fit`
(high|medium|low), `why`, and `group` (ar|latam|known_unknown|out). `build` then
writes a Markdown file and a self-contained HTML file with working links.

The scoring is deliberately conservative and explainable: it reads the posting
title and location, because that is all every portal gives us before a detail
fetch. It is a triage signal, not a verdict — the full evaluation belongs to the
job-application skill once a posting is picked.

Rules live in this file on purpose. They are the user's career preferences, and
changing them should be a visible edit, not a magic value buried in a prompt.
"""

import argparse
import html
import json
import os
import sys
import unicodedata
from urllib.parse import quote_plus, urlparse
from collections import Counter
from datetime import date

# --- Fit rules -------------------------------------------------------------

# A title containing any of these is the wrong discipline. The lists below are
# fallback defaults only -- profile.json always wins when it is present.
STACK_REJECT = [
    "blazor", ".net", "c#", "java", "spring", "laravel", "php", "ruby", "golang",
    "python", "django", "flask", "salesforce", "dynamics 365", "sap ", "cobol",
    "delphi", "genexus", "react native", "flutter", "swift", "kotlin", "android",
    "ios ", "mobile", "moviles", "movil", "data engineer", "data scientist",
    "machine learning", "deep learning", "computer vision", "nlp scientist",
    "mlops", "ml engineer", "data science", "cientifico", "devops", "sre ", "qa ",
    "tester", "ciberseguridad", "seguridad informatica", "soporte", "sysadmin",
    "cnc", "firmware", "embebido", "embedded", "electronica", "vendedor",
    "ventas", "comercial", "administrativ", "operario", "mantenimiento",
    "marketing", "relaciones publicas", "rrhh", "recursos humanos",
    "community", "talent pool", "talent network", "talent community",
]

# Backend-only roles are a stretch even when the posting also says React.
BACKEND_ONLY = ["backend", "back-end", "back end"]

HIGH_ROLE = ["engineer", "developer", "specialist", "lead"]

# AI as a way of BUILDING software — agents, LLM integration, AI-assisted
# delivery. This is deliberately separate from ML/DL research, which the reject
# list above drops first: the order matters, because "Machine Learning Engineer"
# must not be rescued by the word "engineer".
AI_BUILD_ROLE: list[str] = []

# Roughly five years of experience: these titles sit a rung or two above that.
# They are demoted, not hidden -- the scope may still be worth reading, but they
# should not occupy the headline next to a genuine mid-senior match.
SENIORITY_ABOVE = [
    "staff ", "staff,", "principal", "architect", "head of", "director",
    "vp ", "vice president", "distinguished", "fellow", "chief ",
]  # generic enough to keep as a default

# Five-plus years of experience: entry-level and internship roles are a step
# backwards, not a fallback. They are excluded rather than presented as matches.
BELOW_PROFILE = [
    "junior", "jr ", " jr", "trainee", "new grad", "newgrad", "intern",
    "internship", "entry level", "entry-level", "sin experiencia", "primer empleo",
]

MEDIUM_ROLE = [
    "developer", "develop", "desarrollador", "programador", "full stack",
    "fullstack", "software engineer", "engineer", "analista funcional",
]

# --- Eligibility rules -----------------------------------------------------

HOME_PLACES: list[str] = []

REGION_PLACES = ["remote"]

OUT_OF_SCOPE = [
    "united states", "usa", "u.s.", "uk", "united kingdom", "india", "chennai",
    "bangalore", "poland", "portugal", "russia", "germany", "france", "spain",
    "canada", "australia", "singapore", "philippines", "vietnam", "japan",
    "china", "israel", "turkey", "romania", "bulgaria", "hungary", "czech",
]

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILE_FILE = os.path.join(SKILL_DIR, "profile.json")

_PROFILE = None


def _load_profile():
    """Everything personal lives in profile.json, so the skill is shareable.

    Missing profile falls back to the built-in defaults below, which keeps the
    tool usable for a quick test but is not what a real user should rely on.
    """
    global _PROFILE
    try:
        _PROFILE = json.load(open(PROFILE_FILE, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        _PROFILE = None
    return _PROFILE


def _cfg(path, default):
    """Read a dotted key from the profile, falling back to a default."""
    node = _PROFILE
    if not node:
        return default
    for part in path.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node


def _blocked_reason(url):
    """Return the configured reason when a URL points at a paywalled aggregator."""
    domains = _cfg("blocked_domains", {}) or {}
    if not domains:
        return None
    host = (urlparse(url or "").netloc or "").lower()
    for domain, reason in domains.items():
        if host == domain or host.endswith("." + domain):
            return reason
    return None


GROUPS = {
    "home": ("Cerca de casa", "Presencial o híbrido en tu zona"),
    "region": ("Remoto / región", "Confirmar que contraten desde tu país"),
    "known_unknown": ("Ubicación sin dato", "Verificar antes de aplicar"),
    "blocked": ("Bloqueadas — buscar en otro lado", "Sitios que obligan a pagar para postularse"),
    "out": ("Fuera de alcance", ""),
}

SOURCE_LABEL = {
    "computrabajo": "Computrabajo",
    "getonbrd": "GetOnBoard",
    "remoteok": "RemoteOK",
    "linkedin": "LinkedIn",
    "freehire": "freehire",
}


def fold(value):
    """Lowercase and strip accents so 'Córdoba' and 'cordoba' compare equal."""
    if not value:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value))
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch)).lower()


def has_any(text, terms):
    return any(term in text for term in terms)


_LEARNED = {"demote": [], "promote": []}


def _apply_learned(job, fit):
    """Lower a fit when accumulated feedback says this word keeps getting rejected.

    Demotion is capped at high -> medium on purpose. A pattern learned from three
    rejections should stop dominating the headline, not silently delete a posting.
    """
    if fit != "high":
        return fit, ""
    title = fold(job.get("title"))
    for rule in _LEARNED.get("demote", []):
        pattern = rule.get("pattern")
        if pattern and pattern in title:
            return "medium", f"feedback: {pattern}"
    return fit, ""


def classify(job):
    title = fold(job.get("title"))

    reject = _cfg("stack.reject", STACK_REJECT)
    if has_any(title, reject):
        return "low", "stack o rubro ajeno"

    if has_any(title, _cfg("seniority.below", BELOW_PROFILE)):
        return "low", "nivel por debajo del perfil"

    unless = _cfg("stack.reject_unless", {}) or {}
    for family, allowed in unless.items():
        if family in title and not has_any(title, allowed):
            return "low", f"{family} puro"

    high_roles = _cfg("roles.high", HIGH_ROLE)
    specialist = _cfg("roles.specialist", AI_BUILD_ROLE)
    medium_roles = _cfg("roles.medium", MEDIUM_ROLE)

    # A specialist family only counts as a strong match when the title also
    # carries a core signal. "AI-First Frontend Engineer" is a match;
    # "AI Engineer" alone is a different discipline that keeps getting rejected.
    specialist_requires = _cfg("roles.specialist_requires", [])
    specialist_hit = has_any(title, specialist)
    if specialist_hit and specialist_requires and not has_any(title, specialist_requires):
        specialist_hit = False

    if has_any(title, high_roles) or specialist_hit:
        # Angular-only roles are frontend-adjacent, not React work. Worth reading,
        # but they do not belong in the headline list.
        fit = "medium" if ("angular" in title and "react" not in title) else "high"
    elif has_any(title, medium_roles):
        fit = "medium"
    else:
        return "low", "el título no es de desarrollo"

    if fit == "high" and has_any(title, _cfg("seniority.above", SENIORITY_ABOVE)):
        return "medium", "seniority por encima del perfil"

    return _apply_learned(job, fit)


def group_of(job):
    if _blocked_reason(job.get("url")):
        return "blocked"
    location = fold(job.get("location"))
    if has_any(location, _cfg("location.out_of_scope", OUT_OF_SCOPE)):
        return "out"
    if has_any(location, _cfg("location.home", HOME_PLACES)):
        return "home"
    if has_any(location, _cfg("location.region", REGION_PLACES)):
        return "region"
    if not location.strip():
        return "known_unknown"
    return "out"


def _age_days(posted, today):
    """Real age of a posting, used to expose stale recruiter posts honestly."""
    if not posted:
        return None
    try:
        return (date.fromisoformat(today) - date.fromisoformat(str(posted)[:10])).days
    except ValueError:
        return None


def _resolve_links(title, company):
    """Search links that find the original posting behind a paywalled aggregator.

    Nothing here fabricates a URL: these are ordinary searches for the title and
    company, which is how the same vacancy gets found on a board that does not
    charge the candidate.
    """
    query = quote_plus(" ".join(part for part in (title, company) if part)[:180])
    return {
        "google": f"https://www.google.com/search?q={query}",
        "linkedin": f"https://www.linkedin.com/jobs/search/?keywords={query}",
    }


def short_location(value, limit=3):
    """freehire returns eligible-country lists that run to 200+ characters.

    A row is meant to be scannable, so a long list is summarised instead of
    dumped into the table.
    """
    if not value:
        return ""
    text = str(value).strip()
    parts = [part.strip() for part in text.split(",") if part.strip()]
    if len(parts) <= limit:
        return text
    return "Remoto · varios países"


def source_label(portal):
    if portal and portal.startswith("telegram:"):
        return "Telegram"
    return SOURCE_LABEL.get(portal, portal or "—")


# --- Commands --------------------------------------------------------------


def cmd_score(args):
    global _LEARNED
    _load_profile()
    _LEARNED = _load_learned()
    jobs = json.load(open(args.results, encoding="utf-8"))
    if isinstance(jobs, dict):
        jobs = jobs.get("selected") or jobs.get("results") or []

    for job in jobs:
        fit, why = classify(job)
        job["fit"] = fit
        job["why"] = why
        job["group"] = group_of(job)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as handle:
            json.dump(jobs, handle, ensure_ascii=False, indent=2)

    counts = Counter(job["fit"] for job in jobs)
    groups = Counter(job["group"] for job in jobs)
    json.dump({"fit": dict(counts), "group": dict(groups), "total": len(jobs)},
              sys.stdout, indent=2)
    sys.stdout.write("\n")


def _rows_by_group(jobs):
    order = {"high": 0, "medium": 1}
    buckets = {key: [] for key in GROUPS}
    for job in jobs:
        if job["fit"] not in order:
            continue
        buckets[job["group"]].append(job)
    for bucket in buckets.values():
        bucket.sort(key=lambda j: (order[j["fit"]], _neg_date(j.get("date"))))
    return buckets


def _neg_date(value):
    """Sort newest first inside a fit band using a reverse-friendly key."""
    return "".join(chr(0x10FFFF - ord(c)) for c in (value or ""))


def cmd_build(args):
    global _LEARNED
    _load_profile()
    _LEARNED = _load_learned()
    jobs = json.load(open(args.results, encoding="utf-8"))
    if isinstance(jobs, dict):
        jobs = jobs.get("selected") or jobs.get("results") or []
    if not args.skip_score and any("group" not in j for j in jobs):
        for job in jobs:
            fit, why = classify(job)
            job.update(fit=fit, why=why, group=group_of(job))

    buckets = _rows_by_group(jobs)
    visible = buckets["home"] + buckets["region"] + buckets["known_unknown"]
    counts = Counter(job["fit"] for job in visible)
    today = args.date or date.today().isoformat()

    posts = []
    if args.posts:
        raw = json.load(open(args.posts, encoding="utf-8"))
        if isinstance(raw, dict):
            raw = raw.get("results") or raw.get("selected") or []
        for post in raw:
            fit, why = classify(post)
            if fit == "low":
                continue
            post["fit"] = fit
            post["age_days"] = _age_days(post.get("date"), today)
            posts.append(post)
        posts.sort(key=lambda p: ({"high": 0, "medium": 1}[p["fit"]], p["age_days"] or 0))

    os.makedirs(args.out_dir, exist_ok=True)
    md_path = os.path.join(args.out_dir, f"{today}_ofertas.md")
    html_path = os.path.join(args.out_dir, f"{today}_ofertas.html")

    _write_markdown(md_path, today, buckets, counts, posts, buckets["blocked"])
    _write_html(html_path, today, buckets, counts, posts, buckets["blocked"])

    json.dump(
        {"markdown": md_path, "html": html_path, "visible": len(visible),
         "high": counts["high"], "medium": counts["medium"],
         "out_of_scope": len(buckets["out"]), "blocked": len(buckets["blocked"]),
         "posts": len(posts)},
        sys.stdout, indent=2,
    )
    sys.stdout.write("\n")


def _write_markdown(path, today, buckets, counts, posts=None, blocked=None):
    lines = [
        f"# Ofertas frescas — {today}",
        "",
        f"**{counts['high']} high · {counts['medium']} medium** · ventana de 7 días · "
        f"{len(buckets['out'])} descartadas por ubicación fuera de alcance.",
        "",
        "Deduplicado contra corridas anteriores.",
        "",
    ]
    for key in ("home", "region", "known_unknown"):
        rows = buckets[key]
        if not rows:
            continue
        title, sub = GROUPS[key]
        lines.append(f"## {title}")
        if sub:
            lines.extend([f"*{sub}*", ""])
        lines.append("| Fit | Puesto | Empresa | Ubicación | Publicado | Fuente |")
        lines.append("|---|---|---|---|---|---|")
        for job in rows:
            badge = "**HIGH**" if job["fit"] == "high" else "medium"
            lines.append(
                f"| {badge} | [{job['title']}]({job['url']}) | "
                f"{job.get('company') or '—'} | {short_location(job.get('location')) or '—'} | "
                f"{job.get('date') or '—'} | {source_label(job.get('portal'))} |"
            )
        lines.append("")

    if blocked:
        lines.append("## Bloqueadas — buscar en otro lado")
        lines.append(
            "*Estos sitios obligan a pagar para postularse. La oferta existe en algún "
            "lado gratis: los links de la última columna la buscan por puesto y empresa.*"
        )
        lines.append("")
        lines.append("| Puesto | Empresa | Ubicación | Motivo | Buscar en |")
        lines.append("|---|---|---|---|---|")
        for job in blocked:
            links = _resolve_links(job.get("title"), job.get("company"))
            markers = (f"[Google]({links['google']}) · "
                       f"[LinkedIn]({links['linkedin']})")
            reason = _blocked_reason(job.get("url")) or "bloqueado"
            lines.append(
                f"| {job['title']} | {job.get('company') or '—'} | "
                f"{short_location(job.get('location')) or '—'} | {reason} | {markers} |"
            )
        lines.append("")

    if posts:
        lines.append("## Posts de recruiters")
        lines.append(
            "*Publicados en LinkedIn, no en los portales. El índice de búsqueda tiene "
            "meses de atraso: la columna **Edad** es la antigüedad real. Sirven como "
            "mapa de empresas y reclutadores que contratan este perfil, no como oferta fresca.*"
        )
        lines.append("")
        lines.append("| Fit | Puesto | Empresa / Reclutador | Ubicación | Publicado | Edad | Contacto |")
        lines.append("|---|---|---|---|---|---|---|")
        for post in posts:
            badge = "**HIGH**" if post["fit"] == "high" else "medium"
            age = post.get("age_days")
            age_txt = f"{age} días" if age is not None else "—"
            lines.append(
                f"| {badge} | [{post['title']}]({post['url']}) | "
                f"{post.get('company') or '—'} | {short_location(post.get('location')) or '—'} | "
                f"{post.get('date') or '—'} | {age_txt} | {post.get('contact') or '—'} |"
            )
        lines.append("")

    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


CSS = """
  :root { --bg:#0f1115; --panel:#171a21; --line:#262b36; --txt:#e6e9ef; --dim:#9aa4b5;
           --high:#3ddc84; --med:#e8b93b; --link:#7cb8ff; --bad:#e07a5f; --ok:#3ddc84; }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--txt);
         font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
  .wrap { max-width:1320px; margin:0 auto; padding:40px 24px 80px; }
  h1 { font-size:28px; margin:0 0 6px; letter-spacing:-.02em; }
  .meta { color:var(--dim); font-size:13px; margin-bottom:26px; }
  .stats { display:flex; gap:12px; flex-wrap:wrap; margin:22px 0 20px; }
  .stat { background:var(--panel); border:1px solid var(--line); border-radius:10px;
          padding:14px 18px; min-width:110px; }
  .stat b { display:block; font-size:22px; }
  .stat span { color:var(--dim); font-size:12px; text-transform:uppercase; letter-spacing:.06em; }
  .stat.high b { color:var(--high); }
  .stat.med b { color:var(--med); }
  .stat.ok b { color:var(--ok); }
  .stat.bad b { color:var(--bad); }
  .toolbar { display:flex; gap:10px; align-items:center; margin:0 0 30px; flex-wrap:wrap; }
  button { font:inherit; cursor:pointer; border-radius:8px; border:1px solid var(--line);
           background:var(--panel); color:var(--txt); padding:7px 13px; font-size:13px; }
  button:hover { border-color:#3a4150; }
  button.primary { background:#1d4ed8; border-color:#1d4ed8; color:#fff; }
  button.primary:hover { background:#2563eb; }
  button.on { background:rgba(61,220,132,.16); border-color:var(--high); color:var(--high); }
  section { margin-bottom:44px; }
  h2 { font-size:17px; margin:0 0 4px; display:flex; align-items:center; gap:10px; }
  .count { background:var(--panel); border:1px solid var(--line); color:var(--dim);
           font-size:12px; padding:2px 9px; border-radius:20px; font-weight:500; }
  .sub { color:var(--dim); font-size:13px; margin:0 0 14px; }
  .warn { color:var(--med); font-size:13px; margin:0 0 14px; background:rgba(232,185,59,.07);
          border-left:3px solid var(--med); padding:10px 14px; border-radius:0 8px 8px 0; }
  table { width:100%; border-collapse:collapse; background:var(--panel);
          border:1px solid var(--line); border-radius:10px; overflow:hidden; }
  th { text-align:left; font-size:11px; text-transform:uppercase; letter-spacing:.07em;
       color:var(--dim); font-weight:600; padding:11px 14px; border-bottom:1px solid var(--line);
       background:#13161c; }
  td { padding:11px 14px; border-bottom:1px solid var(--line); vertical-align:top; font-size:14px; }
  tr:last-child td { border-bottom:none; }
  tr:hover td { background:#1b1f28; }
  td.t { max-width:380px; font-weight:500; }
  td.t a { color:var(--link); text-decoration:none; }
  td.t a:hover { text-decoration:underline; }
  td.d, td.s { color:var(--dim); font-size:13px; white-space:nowrap; }
  td.act { white-space:nowrap; width:1%; }
  td.act button { padding:5px 10px; font-size:12px; margin-right:5px; }
  .b { font-size:10px; font-weight:700; letter-spacing:.06em; padding:3px 7px;
       border-radius:5px; white-space:nowrap; }
  .b.high { background:rgba(61,220,132,.14); color:var(--high); }
  .b.med { background:rgba(232,185,59,.14); color:var(--med); }
  tr.done td { opacity:.5; }
  tr.done td.act { opacity:1; }
  tr.dropped td { opacity:.32; }
  tr.dropped td.act { opacity:1; }
  .mark { font-size:11px; padding:2px 7px; border-radius:5px; margin-right:6px; white-space:nowrap; }
  .mark.applied { background:rgba(61,220,132,.16); color:var(--high); }
  .mark.dropped { background:rgba(224,122,95,.16); color:var(--bad); }
  a.btn { display:inline-block; padding:4px 10px; margin-right:5px; font-size:12px;
          border:1px solid var(--line); border-radius:6px; background:var(--panel);
          color:var(--link); text-decoration:none; }
  a.btn:hover { border-color:#3a4150; }
  select { font:inherit; font-size:12px; background:var(--panel); color:var(--txt);
           border:1px solid var(--line); border-radius:6px; padding:5px 7px; max-width:170px; }
  footer { color:var(--dim); font-size:12.5px; border-top:1px solid var(--line);
           padding-top:18px; margin-top:20px; }
  footer li { margin-bottom:5px; }
  @media print { td.act, .toolbar { display:none; } }
"""


def _safe(value):
    return html.escape("—" if value is None else str(value))


FEEDBACK_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "state", "feedback.jsonl")
LEARNED_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "state", "learned-rules.json")


def _load_feedback():
    """Prior marks, so reopening the report shows what was already decided."""
    marks = {}
    try:
        with open(FEEDBACK_FILE, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue
                url = entry.get("url")
                if url:
                    marks[url] = {"action": entry.get("action"),
                                  "reason": entry.get("reason"),
                                  "ts": entry.get("ts")}
    except FileNotFoundError:
        pass
    return marks


def _load_learned():
    try:
        return json.load(open(LEARNED_FILE, encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {"demote": [], "promote": []}


JS = """
(function () {
  var STORE = 'jobsearch-feedback-v1';
  var REASONS = [
    ['seniority_high', 'Seniority muy alto'],
    ['stack_missing', 'Stack que no tengo'],
    ['location', 'Ubicación no aplicable'],
    ['english', 'Inglés requerido'],
    ['company', 'No me interesa la empresa'],
    ['closed', 'Ya cerrada / no aplica'],
    ['other', 'Otro']
  ];
  var state = {};
  try { state = JSON.parse(localStorage.getItem(STORE) || '{}'); } catch (e) { state = {}; }
  var served = location.protocol === 'http:' || location.protocol === 'https:';
  var hideDone = false;

  function persist() {
    try { localStorage.setItem(STORE, JSON.stringify(state)); } catch (e) {}
  }

  function send(entry) {
    if (!served) return;
    fetch('/feedback', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(entry)
    }).then(function (r) {
      var el = document.getElementById('status');
      if (el) el.textContent = r.ok ? 'Guardado en el estado' : 'Marcado local (servidor no disponible)';
    }).catch(function () {
      var el = document.getElementById('status');
      if (el) el.textContent = 'Marcado local (servidor no disponible)';
    });
  }

  function setMark(row, action, reason) {
    var url = row.dataset.url;
    if (!url) return;
    if (!action) { delete state[url]; }
    else {
      state[url] = {
        action: action,
        reason: reason || null,
        title: row.dataset.title || '',
        company: row.dataset.company || '',
        portal: row.dataset.portal || '',
        ts: new Date().toISOString()
      };
      send(state[url]);
    }
    persist();
    paintRow(row);
    counters();
  }

  function paintRow(row) {
    var url = row.dataset.url;
    var mark = state[url];
    var slot = row.querySelector('.markslot');
    var applied = row.querySelector('button[data-act="applied"]');
    var dropped = row.querySelector('button[data-act="dropped"]');
    var select = row.querySelector('select.reason');

    row.classList.remove('done', 'dropped');
    if (slot) slot.innerHTML = '';
    if (applied) applied.classList.remove('on');
    if (dropped) dropped.classList.remove('on');
    if (select) select.remove();

    if (!mark) {
      row.style.display = '';
      return;
    }

    if (mark.action === 'applied') {
      row.classList.add('done');
      if (applied) applied.classList.add('on');
      if (slot) slot.innerHTML = '<span class="mark applied">aplicado</span>';
    } else {
      row.classList.add('dropped');
      if (dropped) dropped.classList.add('on');
      var label = 'fuera';
      for (var i = 0; i < REASONS.length; i++) {
        if (REASONS[i][0] === mark.reason) label = REASONS[i][1];
      }
      if (slot) slot.innerHTML = '<span class="mark dropped">' + label + '</span>';

      var picker = document.createElement('select');
      picker.className = 'reason';
      var head = document.createElement('option');
      head.value = '';
      head.textContent = 'razón…';
      picker.appendChild(head);
      for (var j = 0; j < REASONS.length; j++) {
        var option = document.createElement('option');
        option.value = REASONS[j][0];
        option.textContent = REASONS[j][1];
        if (mark.reason === REASONS[j][0]) option.selected = true;
        picker.appendChild(option);
      }
      picker.addEventListener('change', function () {
        setMark(row, 'dropped', picker.value || null);
      });
      if (slot) slot.appendChild(picker);
    }
    row.style.display = (hideDone && mark) ? 'none' : '';
  }

  function counters() {
    var applied = 0, dropped = 0, total = 0;
    document.querySelectorAll('tr[data-url]').forEach(function (row) {
      total++;
      var mark = state[row.dataset.url];
      if (!mark) return;
      if (mark.action === 'applied') applied++;
      if (mark.action === 'dropped') dropped++;
    });
    var a = document.getElementById('c-applied');
    var d = document.getElementById('c-dropped');
    var o = document.getElementById('c-open');
    if (a) a.textContent = applied;
    if (d) d.textContent = dropped;
    if (o) o.textContent = total - applied - dropped;
  }

  document.querySelectorAll('tr[data-url]').forEach(function (row) {
    row.querySelectorAll('button[data-act]').forEach(function (button) {
      button.addEventListener('click', function () {
        var act = button.dataset.act;
        var mark = state[row.dataset.url];
        if (mark && mark.action === act) { setMark(row, null, null); return; }
        setMark(row, act, act === 'dropped' ? (mark && mark.reason) || null : null);
      });
    });
    paintRow(row);
  });

  var toggle = document.getElementById('toggle-done');
  if (toggle) {
    toggle.addEventListener('click', function () {
      hideDone = !hideDone;
      toggle.textContent = hideDone ? 'Mostrar marcadas' : 'Ocultar marcadas';
      document.querySelectorAll('tr[data-url]').forEach(paintRow);
    });
  }

  var exportButton = document.getElementById('export');
  if (exportButton) {
    exportButton.addEventListener('click', function () {
      var entries = Object.keys(state).map(function (url) {
        var entry = state[url];
        return {
          url: url,
          action: entry.action,
          reason: entry.reason,
          title: entry.title,
          company: entry.company,
          portal: entry.portal,
          ts: entry.ts
        };
      });
      var blob = new Blob([JSON.stringify(entries, null, 2)], { type: 'application/json' });
      var link = document.createElement('a');
      link.href = URL.createObjectURL(blob);
      link.download = 'feedback-' + new Date().toISOString().slice(0, 10) + '.json';
      document.body.appendChild(link);
      link.click();
      link.remove();
    });
  }

  counters();
})();
"""


def _write_html(path, today, buckets, counts, posts=None, blocked=None):
    visible = buckets["home"] + buckets["region"] + buckets["known_unknown"]
    sections = []
    for key in ("home", "region", "known_unknown"):
        rows = buckets[key]
        if not rows:
            continue
        title, sub = GROUPS[key]
        high = sum(1 for row in rows if row["fit"] == "high")
        body = []
        for job in rows:
            badge = "high" if job["fit"] == "high" else "med"
            label = "HIGH" if job["fit"] == "high" else "MEDIUM"
            body.append(
                f'      <tr data-url="{_safe(job["url"])}" data-title="{_safe(job["title"])}" '
                f'data-company="{_safe(job.get("company"))}" data-portal="{_safe(job.get("portal"))}">\n'
                f'        <td><span class="b {badge}">{label}</span></td>\n'
                f'        <td class="t"><a href="{_safe(job["url"])}" target="_blank" '
                f'rel="noopener noreferrer">{_safe(job["title"])}</a></td>\n'
                f'        <td>{_safe(job.get("company"))}</td>\n'
                f'        <td>{_safe(short_location(job.get("location")))}</td>\n'
                f'        <td class="d">{_safe(job.get("date"))}</td>\n'
                f'        <td class="s">{_safe(source_label(job.get("portal")))}</td>\n'
                f'        <td class="act"><span class="markslot"></span>'
                f'<button class="applied" data-act="applied">Aplicado</button>'
                f'<button data-act="dropped">Fuera de rango</button></td>\n'
                f'      </tr>'
            )
        note = f" · {high} high" if high else ""
        sections.append(
            f"  <section>\n"
            f"    <h2>{_safe(title)} <span class=\"count\">{len(rows)}</span></h2>\n"
            f"    <p class=\"sub\">{_safe(sub)}{note}</p>\n"
            f"    <table>\n"
            f"      <thead><tr><th>Fit</th><th>Puesto</th><th>Empresa</th>"
            f"<th>Ubicación</th><th>Publicado</th><th>Fuente</th><th>Acción</th></tr></thead>\n"
            f"      <tbody>\n" + "\n".join(body) + "\n      </tbody>\n    </table>\n  </section>"
        )

    blocked_section = ""
    if blocked:
        rows = []
        for job in blocked:
            links = _resolve_links(job.get("title"), job.get("company"))
            reason = _blocked_reason(job.get("url")) or "bloqueado"
            rows.append(
                f'      <tr>\n'
                f'        <td class="t">{_safe(job.get("title"))}</td>\n'
                f'        <td>{_safe(job.get("company"))}</td>\n'
                f'        <td>{_safe(short_location(job.get("location")))}</td>\n'
                f'        <td class="d">{_safe(reason)}</td>\n'
                f'        <td class="act">'
                f'<a class="btn" href="{_safe(links["google"])}" target="_blank" '
                f'rel="noopener noreferrer">Google</a>'
                f'<a class="btn" href="{_safe(links["linkedin"])}" target="_blank" '
                f'rel="noopener noreferrer">LinkedIn</a></td>\n'
                f'      </tr>'
            )
        blocked_section = (
            '  <section>\n'
            '    <h2>Bloqueadas — buscar en otro lado <span class="count">'
            + str(len(blocked)) + '</span></h2>\n'
            '    <p class="warn">Estos sitios obligan a pagar para postularse. La oferta '
            'existe en algún lado gratis: los botones la buscan por puesto y empresa.</p>\n'
            '    <table>\n'
            '      <thead><tr><th>Puesto</th><th>Empresa</th><th>Ubicación</th>'
            '<th>Motivo</th><th>Buscar en</th></tr></thead>\n'
            '      <tbody>\n' + "\n".join(rows) + '\n      </tbody>\n    </table>\n  </section>'
        )

    posts_section = ""
    if posts:
        rows = []
        for post in posts:
            badge = "high" if post["fit"] == "high" else "med"
            label = "HIGH" if post["fit"] == "high" else "MEDIUM"
            age = post.get("age_days")
            age_cls = "old" if age and age > 7 else "fresh"
            age_txt = f"{age} días" if age is not None else "—"
            rows.append(
                f'      <tr data-url="{_safe(post["url"])}" data-title="{_safe(post["title"])}" '
                f'data-company="{_safe(post.get("company"))}" data-portal="linkedin-posts">\n'
                f'        <td><span class="b {badge}">{label}</span></td>\n'
                f'        <td class="t"><a href="{_safe(post["url"])}" target="_blank" '
                f'rel="noopener noreferrer">{_safe(post["title"])}</a></td>\n'
                f'        <td>{_safe(post.get("company"))}</td>\n'
                f'        <td>{_safe(short_location(post.get("location")))}</td>\n'
                f'        <td class="d">{_safe(post.get("date"))}</td>\n'
                f'        <td class="d"><span class="{age_cls}">{age_txt}</span></td>\n'
                f'        <td class="act"><span class="markslot"></span>'
                f'<button class="applied" data-act="applied">Aplicado</button>'
                f'<button data-act="dropped">Fuera de rango</button></td>\n'
                f'      </tr>'
            )
        posts_section = (
            '  <section>\n'
            '    <h2>Posts de recruiters <span class="count">' + str(len(posts)) + '</span></h2>\n'
            '    <p class="warn">Publicados en LinkedIn, no en los portales. El índice de '
            'búsqueda tiene meses de atraso: la columna <b>Edad</b> es la antigüedad real. '
            'Sirven como mapa de empresas y reclutadores que contratan este perfil, no como '
            'oferta fresca.</p>\n'
            '    <table>\n'
            '      <thead><tr><th>Fit</th><th>Puesto</th><th>Empresa / Reclutador</th>'
            '<th>Ubicación</th><th>Publicado</th><th>Edad</th><th>Acción</th></tr></thead>\n'
            '      <tbody>\n' + "\n".join(rows) + '\n      </tbody>\n    </table>\n  </section>'
        )

    head = (
        '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title>Ofertas frescas — {today}</title>\n<style>{CSS}</style>\n</head>\n<body>\n'
        '<div class="wrap">\n'
        f'  <h1>Ofertas frescas — {today}</h1>\n'
        f'  <div class="meta">Ventana de 7 días · deduplicado contra corridas anteriores · '
        f'{len(buckets["out"])} descartadas por ubicación fuera de alcance</div>\n\n'
        '  <div class="stats">\n'
        f'    <div class="stat high"><b>{counts["high"]}</b><span>High fit</span></div>\n'
        f'    <div class="stat med"><b>{counts["medium"]}</b><span>Medium fit</span></div>\n'
        f'    <div class="stat"><b>{len(visible)}</b><span>Aplicables</span></div>\n'
        '    <div class="stat ok"><b id="c-applied">0</b><span>Aplicadas</span></div>\n'
        '    <div class="stat bad"><b id="c-dropped">0</b><span>Fuera de rango</span></div>\n'
        f'    <div class="stat"><b id="c-open">{len(visible)}</b><span>Sin marcar</span></div>\n'
        '  </div>\n\n'
        '  <div class="toolbar">\n'
        '    <button class="primary" id="export">Exportar feedback</button>\n'
        '    <button id="toggle-done">Ocultar marcadas</button>\n'
        '    <span class="sub" id="status" style="margin:0"></span>\n'
        '  </div>\n'
    )

    tail = (
        '\n  <footer>\n'
        '    <strong>Cómo se filtró</strong>\n'
        '    <ul>\n'
        '      <li>Publicado en los últimos 7 días; deadline no vencido.</li>\n'
        '      <li>Rol frontend / UI / product engineer / developer / programador / AI builder.</li>\n'
        '      <li>Descartado si el stack central es Java, .NET, PHP, Python, QA, datos, mobile\n'
        '          nativo, o si el nivel es junior / intern / entry-level.</li>\n'
        '      <li>Descartado si la ubicación no es Argentina, LatAm ni remoto.</li>\n'
        '      <li>Sin repetir ofertas presentadas en corridas anteriores.</li>\n'
        '    </ul>\n'
        '    <p><strong>Marcá cada oferta.</strong> "Aplicado" y "Fuera de rango" alimentan el\n'
        '    aprendizaje: la razón que elijas se acumula y la próxima corrida ordena mejor.\n'
        '    Lo que dejes sin marcar se cuenta como pendiente — no como descartado.</p>\n'
        '  </footer>\n'
        '</div>\n'
        f'<script>{JS}</script>\n'
        '</body>\n</html>'
    )

    document = (head + "\n" + "\n".join(sections) + "\n"
                + blocked_section + "\n" + posts_section + tail)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(document)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    score = sub.add_parser("score", help="tag jobs with fit and eligibility group")
    score.add_argument("--results", required=True)
    score.add_argument("--out", help="write the scored JSON here")
    score.set_defaults(func=cmd_score)

    build = sub.add_parser("build", help="render markdown and HTML reports")
    build.add_argument("--results", required=True)
    build.add_argument("--out-dir", required=True)
    build.add_argument("--date", help="YYYY-MM-DD; defaults to today")
    build.add_argument("--skip-score", action="store_true",
                       help="input already carries fit/group")
    build.add_argument(
        "--posts",
        help="JSON of LinkedIn recruiter posts; rendered as a separate section "
             "with their real age, never mixed into the fresh list",
    )
    build.set_defaults(func=cmd_build)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
