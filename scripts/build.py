#!/usr/bin/env python3
"""Academic website generator for Dr Haithem Afli.
Dependency-free (Python 3 stdlib only). Content (data/*.json) is separated from
templates (this file's render_* functions). All dynamic text is HTML-escaped;
URLs are validated; malformed records fail safely (skipped with a logged warning,
never emitting broken HTML). Build is reproducible. Output goes to site/ and must
never be hand-edited.

Usage:  python3 scripts/build.py        # build into site/
        python3 scripts/build.py --check # validate data only, no write
"""
import json, html, pathlib, sys, re, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "site"
BASE_URL = "https://hafli.github.io/haithem-afli-academic-website"  # GitHub user HAfli; Pages serves lowercase. Update to custom domain when configured
BUILD_DATE = datetime.date.today().isoformat()
warnings = []

def esc(s):
    return html.escape(str(s), quote=True) if s is not None else ""

def valid_url(u):
    if not isinstance(u, str):
        return False
    if u.startswith("mailto:") and "@" in u:
        return True
    return re.match(r"^https?://[\w.\-]+(/[\w\-./?%&=:#@+,~();]*)?$", u) is not None

def valid_url_or_local(u):
    return bool(u) and (valid_url(u) or u.startswith("assets/"))

def load(name):
    try:
        return json.load(open(DATA / name, encoding="utf-8"))
    except Exception as e:
        warnings.append(f"FATAL: cannot load {name}: {e}")
        return None

def link(url, text, cls=""):
    if not valid_url(url):
        if url: warnings.append(f"invalid URL skipped: {url}")
        return esc(text)
    c = f' class="{cls}"' if cls else ""
    return f'<a href="{esc(url)}"{c} rel="noopener">{esc(text)}</a>'

# ---------- layout ----------
NAV = [("index","Home"),("about","About"),("research-vision","Vision"),("journey","Research Journey"),("research","Research"),("rinn-ai","Rinn AI"),("publications","Publications"),
       ("projects","Projects & Funding"),("group","HAI Group"),("supervision","Supervision"),
       ("teaching","Teaching"),("innovation","Innovation"),("talks","Talks & Outreach"),
       ("service","Leadership & Service"),("news","News"),("showcase","Showcase"),
       ("assistant","Ask Me"),("research-intelligence","Research Intelligence"),
       ("gallery","Media"),("cv","CV"),("contact","Contact")]

PROFILE_LINK_LABELS = {
    "orcid.org":"ORCID","aclanthology.org":"ACL Anthology","adaptcentre.ie":"ADAPT Centre",
    "dblp.org":"DBLP","scholar.google.com":"Google Scholar","dl.acm.org":"ACM Digital Library",
    "openreview.net":"OpenReview","researchgate.net":"ResearchGate","linkedin.com":"LinkedIn","x.com":"X",
    "github.com":"GitHub"}
def profile_links_html(profile):
    out = []
    for u in profile["sameAs"]:
        if not valid_url(u): continue
        host = u.split("//")[1].split("/")[0].replace("www.","")
        label = next((v for k,v in PROFILE_LINK_LABELS.items() if k in host), host)
        out.append(f'<li>{link(u, label)}</li>')
    return "".join(out)

def email_component(profile, inline=False):
    """Bot-resistant email: address parts held in data attributes (no full address in the HTML
    source), reconstructed in JavaScript for the mailto link and the Copy button. Displays
    'user [at] domain'."""
    u, d = profile["email"].split("@")
    cls = "email inline" if inline else "email"
    return (f'<span class="{cls}" data-u="{esc(u)}" data-d="{esc(d)}">'
            f'<a class="email-addr" href="#" data-mailto>{esc(u)} [at] {esc(d)}</a>'
            f'<button type="button" class="email-copy" aria-label="Copy email address to clipboard">Copy</button>'
            f'<span class="email-status" role="status" aria-live="polite"></span></span>')

NAV_LABELS = {s: t for s, t in [("index","Home"),("about","About"),("research-vision","Research Vision"),("journey","Research Journey"),("research","Research"),("rinn-ai","Rinn AI"),
    ("publications","Publications"),("projects","Projects & Funding"),("group","HAI Group"),("supervision","Supervision"),
    ("teaching","Teaching"),("innovation","Innovation"),("talks","Talks & Outreach"),("service","Leadership & Service"),
    ("news","News"),("showcase","Research Showcase"),("collections","Research Collections"),("timeline","Research Timeline"),
    ("assistant","Ask Me"),("research-intelligence","Research Intelligence"),("gallery","Media"),("cv","CV"),("contact","Contact"),
    ("conference-deadlines","Conference Deadlines"),("funding-calls","Funding Calls"),("research-calendar","Research Calendar"),
    ("newsletter","HAI Research Brief"),("subscribe","Subscribe"),("analytics-map","Global Research Reach"),
    ("languages","Languages"),("privacy","Privacy")]}
RI_CHILDREN = {"conference-deadlines","funding-calls","research-calendar","newsletter","subscribe","analytics-map"}

# Simplified, grouped primary navigation — priorities over completeness (Release 2.1).
NAV_GROUPS = [
    ("About", [("about","Biography"),("research-vision","Research Vision"),("journey","Research Journey"),
               ("service","Leadership & Service"),("cv","CV")]),
    ("Research", [("research","Research Themes"),("group","HAI Research Group"),("rinn-ai","RINN AI"),
                  ("event-adapt-leadership","ADAPT"),("assistant","Explore My Research")]),
    ("Publications", [("publications","Publications")]),
    ("Projects & Impact", [("projects","Projects"),("innovation","Innovation"),("talks","Talks"),
                           ("research-intelligence","Research Intelligence")]),
    ("People", [("prospective-phd","Prospective PhD Students"),("collaborate","Collaborate"),("industry","Industry")]),
    ("Media", [("news","News"),("showcase","Showcase"),("gallery","Gallery"),("for-media","For Media")]),
    ("Contact", [("contact","Contact")]),
]
def _href(s): return "index.html" if s == "index" else s + ".html"
def nav_html(slug):
    out = []
    for gname, items in NAV_GROUPS:
        if len(items) == 1:
            s, t = items[0]
            cur = ' aria-current="page"' if s == slug else ""
            out.append(f'<a class="navtop" href="{_href(s)}"{cur}>{esc(t)}</a>')
        else:
            active = any(s == slug for s, _ in items)
            CUR = ' aria-current="page"'
            lis = "".join(
                '<li><a href="' + _href(s) + '"' + (CUR if s == slug else "") + '>' + esc(t) + '</a></li>'
                for s, t in items)
            openattr = " open" if active else ""
            summ = '<summary class="cur">' if active else '<summary>'
            out.append(f'<details class="navgroup"{openattr}>{summ}{esc(gname)}</summary><ul class="navmenu">{lis}</ul></details>')
    return "".join(out)

def page(slug, title, body, description, jsonld=None, head_extra=""):
    nav = nav_html(slug)
    lds = []
    if jsonld: lds.append(jsonld)
    # breadcrumb (Home > [Research Intelligence >] Page) for non-home pages
    crumb_html = ""
    if slug != "index":
        trail = [("index","Home")]
        if slug in RI_CHILDREN: trail.append(("research-intelligence","Research Intelligence"))
        trail.append((slug, NAV_LABELS.get(slug, title)))
        crumb_html = '<nav class="crumbs" aria-label="Breadcrumb"><ol>' + "".join(
            (f'<li><a href="{("index.html" if s=="index" else s+".html")}">{esc(t)}</a></li>'
             if s != slug else f'<li aria-current="page">{esc(t)}</li>') for s, t in trail) + '</ol></nav>'
        lds.append({"@context":"https://schema.org","@type":"BreadcrumbList",
            "itemListElement":[{"@type":"ListItem","position":i+1,"name":t,
                "item":f"{BASE_URL}/{'index.html' if s=='index' else s+'.html'}"} for i,(s,t) in enumerate(trail)]})
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in lds)
    canonical = f"{BASE_URL}/{'index.html' if slug=='index' else slug+'.html'}"
    doc_title = "Dr Haithem Afli — Human-Centred AI, MTU" if slug == "index" else f"{title} — Dr Haithem Afli"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(doc_title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(doc_title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{esc(canonical)}">
<meta property="og:site_name" content="Dr Haithem Afli">
<meta name="twitter:card" content="summary">
<meta name="twitter:title" content="{esc(doc_title)}">
<meta name="twitter:description" content="{esc(description)}">
<link rel="alternate" type="application/atom+xml" title="News" href="feed.xml">
<link rel="alternate" hreflang="en" href="{esc(canonical)}">
<link rel="alternate" hreflang="x-default" href="{esc(canonical)}">
<link rel="stylesheet" href="style.css">
{head_extra}
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="brand"><a href="index.html">Dr Haithem Afli</a><span>AI &amp; Human-Centred Computing · MTU</span></div>
  <nav aria-label="Primary">{nav}</nav>
  <details class="langsel"><summary aria-label="Choose language">Language: English</summary>
    <ul aria-label="Languages"><li><a href="index.html" aria-current="true" lang="en">English</a></li>
    <li><a href="languages.html" lang="ga">Gaeilge</a></li><li><a href="languages.html" lang="ar">العربية</a></li>
    <li><a href="languages.html" lang="es">Español</a></li><li><a href="languages.html" lang="ru">Русский</a></li>
    <li><a href="languages.html" lang="fa">فارسی</a></li><li><a href="languages.html" lang="he">עברית</a></li>
    <li><a href="languages.html" lang="de">Deutsch</a></li><li><a href="languages.html" lang="it">Italiano</a></li>
    <li><a href="languages.html" lang="fr">Français</a></li><li><a href="languages.html" lang="tr">Türkçe</a></li></ul></details>
</header>
<main id="main">
{crumb_html}
<h1>{esc(title)}</h1>
{body}
</main>
<footer class="site">
  <nav class="footer-links" aria-label="Institutional and scholarly links">
    <div><span class="footer-h">Institutions</span>
      <a href="https://www.mtu.ie/" rel="noopener">MTU</a>
      <a href="group.html">Human-Centred AI Group</a>
      <a href="rinn-ai.html">Rinn AI</a>
      <a href="https://www.adaptcentre.ie/" rel="noopener">ADAPT Centre</a></div>
    <div><span class="footer-h">Scholarly profiles</span>
      <a href="https://orcid.org/0000-0002-7449-4707" rel="noopener">ORCID</a>
      <a href="https://scholar.google.com/citations?user=qR-on1wAAAAJ" rel="noopener">Google Scholar</a>
      <a href="https://aclanthology.org/people/haithem-afli/" rel="noopener">ACL Anthology</a>
      <a href="https://dblp.org/pid/120/2260.html" rel="noopener">DBLP</a>
      <a href="https://github.com/HAfli" rel="noopener">GitHub</a></div>
  </nav>
  <p class="footer-meta">© {datetime.date.today().year} Haithem Afli · Munster Technological University, Cork.
  <span class="muted">Last updated automatically: {BUILD_DATE}.</span></p>
</footer>
<script src="email.js" defer></script>
</body>
</html>"""

# ---------- pages ----------
def render(profile, pubs, sup, projects, news, service, teaching, talks, patent, gallery, rinn):
    pages = {}
    themes = {t["id"]: t["name"] for t in profile["themes"]}
    IMGS = {i["id"]: i for i in gallery.get("images", []) if valid_url_or_local(i.get("src",""))}
    MILESTONES = (load("milestones.json") or {}).get("milestones", [])
    top_highlights = sorted(MILESTONES, key=lambda m: -m.get("cis", 0))[:8]
    EVENTS = (load("events.json") or {}).get("events", [])
    ms2event = {e["milestone"]: e["id"] for e in EVENTS if e.get("milestone") and e.get("state") == "approved-public"}

    def fig(image_id, hero=False, cls="fig", attrs=""):
        i = IMGS.get(image_id)
        if not i: return ""
        loading = ' fetchpriority="high"' if hero else ' loading="lazy" decoding="async"'
        srcset = f' srcset="{esc(i["srcset"])}"' if i.get("srcset") else ""
        cap = f'<figcaption>{esc(i["caption"])}</figcaption>' if i.get("caption") else ""
        return (f'<figure class="{cls}"{attrs}><img src="{esc(i["src"])}" alt="{esc(i.get("alt",""))}"'
                f'{srcset} sizes="(max-width:640px) 100vw, 640px" width="{i.get("w",800)}" '
                f'height="{i.get("h",600)}"{loading}>{cap}</figure>')

    def figs_for(placement, limit=None):
        sel = [i["id"] for i in gallery.get("images", []) if placement in i.get("placements",[]) and i["id"] in IMGS]
        if limit: sel = sel[:limit]
        return "".join(fig(x) for x in sel)

    # next verified upcoming deadline (for homepage + hub), excluding the conference date itself
    _conf = load("conference_deadlines.json") or {}
    next_deadline = None
    for e in _conf.get("editions", []):
        for d in e.get("deadlines", []):
            if (d.get("verification_status")=="verified" and d.get("date") and d["date"] >= BUILD_DATE
                    and d.get("type") != "conference"):
                cand = (d["date"], f'{e["edition"]} — {d["label"]}', e.get("official_url",""))
                if next_deadline is None or cand[0] < next_deadline[0]:
                    next_deadline = cand
    next_deadline_html = (f'<li><span class="muted">{esc(next_deadline[0])}</span> — '
                          f'{link(next_deadline[2], next_deadline[1]) if next_deadline[2] else esc(next_deadline[1])}</li>'
                          if next_deadline else "")

    # JSON-LD Person — structured roles (not one jobTitle string), affiliations, occupations
    org_ld = {a["id"]: {"@type":"Organization","name":a["name"],"url":a.get("url")} for a in profile.get("affiliations",[])}
    person_ld = {
        "@context":"https://schema.org","@type":"Person","name":profile["name"],
        "honorificPrefix":profile["honorific"],"jobTitle":profile["title"],
        "identifier":f'https://orcid.org/{profile["orcid"]}',
        "affiliation":[org_ld[k] for k in ("mtu","rinn","adapt") if k in org_ld],
        "memberOf":[org_ld[k] for k in ("rinn","adapt") if k in org_ld],
        "hasOccupation":[
            {"@type":"Role","roleName":r["role"],"startDate":(r.get("period","").split("–")[0] or None)}
            for r in profile["roles"]
        ],
        "alumniOf":[e["institution"] for e in profile["education"]],
        "sameAs":[u for u in profile["sameAs"] if valid_url(u)],
        "knowsAbout":[t["name"] for t in profile["themes"]]
    }

    # HOME — a curated landing page (Release 2.1 editorial reduction)
    hero_img = fig("haithem-afli-portrait", hero=True, cls="portrait") or \
        '<div class="placeholder-photo" role="img" aria-label="Portrait">Portrait</div>'
    newest_pub = pubs["publications"][0] if pubs["publications"] else None
    newest_pub_html = (f'{link(newest_pub.get("url"), newest_pub["title"]) if newest_pub.get("url") else esc(newest_pub["title"])} '
                       f'<span class="muted">— {esc(newest_pub["venue"])}, {newest_pub["year"]}</span>') if newest_pub else ""
    recent3 = "".join(
        f'<li>{link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"])} '
        f'<span class="muted">— {esc(p["venue"])}, {p["year"]}</span></li>'
        for p in pubs["publications"][1:4])
    featured_projects = "".join(
        f'<div class="role-card"><h3>{link(p.get("url"), p["short_name"]) if p.get("url") else esc(p.get("short_name") or p["name"])}</h3>'
        f'<p class="muted">{esc(p.get("funder",""))} · {esc(p.get("role",""))}</p></div>'
        for p in projects["national_projects"][:2] if "WITHHELD" not in p.get("note",""))
    # three flagship research programmes (primary + two cross-cutting)
    flagship_themes = [("multilingual","Multilingual & Culturally Aware AI","Language technologies for high- and low-resource languages and cultures — the primary programme."),
                       ("trustworthy","Trustworthy & Human-Centred AI","Privacy-preserving, explainable and accountable machine learning."),
                       ("evaluation","Evaluation Science","Rigorous methods for evaluating language models and translation.")]
    programme_cards = "".join(
        f'<div class="role-card"><h3><a href="theme-{tid}.html">{esc(name)}</a></h3><p class="muted">{esc(desc)}</p></div>'
        for tid, name, desc in flagship_themes)
    # five selected achievements (curated, strongest verified milestones)
    _cat_label = {"keynote":"Keynote","publication":"Publication","grant":"Grant","patent":"Patent",
        "leadership":"Leadership","award":"Award","media":"Media","education":"Education","industry":"Industry"}
    _ms_index = {m["id"]: m for m in MILESTONES}
    hl_ids = ["m-2026-rinn","m-adapt","m-2024-patent","m-2024-keynote-brazil","m-2025-emnlp"]
    highlights_cards = "".join(
        f'<div class="role-card"><h3>{esc(_ms_index[i]["title"])}</h3>'
        f'<p class="muted"><span class="tag">{esc(_cat_label.get(_ms_index[i].get("category"), _ms_index[i].get("category","")))}</span> '
        f'{_ms_index[i]["year"]} — {esc(_ms_index[i].get("impact",""))}</p></div>'
        for i in hl_ids if i in _ms_index)
    body = f"""
<div class="hero">{hero_img}
<div>
<p class="lede">{esc(profile["title"])}, {link("https://www.mtu.ie/","Munster Technological University")}, Cork.</p>
<p class="roles-hero">Institutional Co-Lead, Rinn Artificial Intelligence at MTU · Principal Investigator, ADAPT Centre ·
Founder and Lead, Human-Centred AI Research Group.</p>
<p><a href="research-vision.html">Research vision →</a> · <a href="journey.html">Research journey →</a> · <a href="cv.html">CV (PDF) →</a></p>
</div></div>

<section><h2>Research vision</h2>
<p class="lede">AI should not simply become more capable. It should become more trustworthy, multilingual, culturally
aware and human-centred.</p>
<p><a href="research-vision.html">Read the research vision →</a></p></section>

<section><h2>Research programmes</h2>
<div class="cards">{programme_cards}</div>
<p><a href="research.html">All research themes →</a></p></section>

<section class="feature"><h2>Selected achievements</h2>
<div class="cards">{highlights_cards}</div>
<p><a href="journey.html">The full research journey →</a></p></section>

<section><h2>Leadership &amp; current projects</h2>
<p>Institutional Co-Lead of <a href="rinn-ai.html">Rinn Artificial Intelligence</a> at MTU and Principal
Investigator in the <a href="event-adapt-leadership.html">ADAPT Centre</a>.</p>
<div class="cards">{featured_projects}</div>
<p><a href="projects.html">All projects and funding →</a></p></section>

<section><h2>Latest publications</h2>
{f'<p><strong>Latest:</strong> {newest_pub_html}</p>' if newest_pub_html else ''}
<p class="muted">Recent:</p><ul class="pubs">{recent3}</ul>
<p><a href="publications.html">All publications →</a></p></section>

<section><h2>Find your path</h2>
<p class="muted">Tailored starting points depending on who you are.</p>
<div class="audience-cta">
<a href="prospective-phd.html">Prospective PhD students</a>
<a href="collaborate.html">Researchers &amp; collaborators</a>
<a href="industry.html">Industry &amp; public sector</a>
<a href="for-media.html">Media &amp; event organisers</a></div></section>

<section><h2>Contact</h2><p>For research collaboration, supervision enquiries, invited talks and media requests,
see the <a href="contact.html">contact page and scholarly profiles →</a></p></section>
"""
    pages["index"] = page("index","Dr Haithem Afli", body,
        profile["short_description"], person_ld)

    # ABOUT (biography — verified, EU English, no hype)
    edu = "".join(f'<li><strong>{esc(e["degree"])}</strong>, {esc(e["institution"])}, {e["year"]}'
                  f'{" — <em>"+esc(e["thesis"])+"</em>" if e.get("thesis") else ""}.</li>' for e in profile["education"])
    def role_card(c):
        rl = "; ".join(esc(r) for r in c["roles"])
        links = []
        if valid_url(c.get("url","")): links.append(link(c["url"], "Official page"))
        elif c.get("url"): links.append(f'<a href="{esc(c["url"])}">Details</a>')
        if c.get("internal"): links.append(f'<a href="{esc(c["internal"])}">On this site</a>')
        if c.get("profile"): links.append(link(c["profile"], "Profile"))
        linkbar = " · ".join(links)
        return (f'<div class="role-card"><h3>{esc(c["org"])}</h3>'
                f'<p class="role-titles">{rl}</p><p class="muted">{esc(c["desc"])}</p>'
                f'<p class="role-links">{linkbar}</p></div>')
    cards = "".join(role_card(c) for c in profile["role_cards"])
    mem = " · ".join(link(m["url"], m["name"]) for m in profile.get("memberships",[]))
    body = f"""
<div class="hero">{fig("haithem-afli-portrait", cls="portrait")}
<div>
<p>Dr Haithem Afli is a Lecturer in Artificial Intelligence at {link("https://www.mtu.ie/","Munster Technological University")}
and a researcher in multilingual, culturally aware and human-centred AI. He serves as Institutional Co-Lead
for {link("https://www.researchireland.ie/news/rinn-network/","Rinn Artificial Intelligence")} at MTU, Deputy
Theme Lead for Inclusive Language Model &amp; Translation Methods, and Principal Investigator in the centre.</p>
<p>He is also a Principal Investigator and MTU Lead within the {link("https://www.adaptcentre.ie/","Research Ireland ADAPT Centre")}
and founder of the Human-Centred AI Research Group. His research focuses on inclusive language models, machine
translation, multilingual and Arabic NLP, culturally grounded reasoning, reliable evaluation of large language
models, trustworthy AI, healthcare AI and computational biology.</p>
</div></div>
<p>His work connects foundational AI research with education, public engagement, interdisciplinary
collaboration and practical applications across language, health, science and industry. Governance and
service roles are detailed on the <a href="service.html">Leadership &amp; Service</a> page.</p>
{fig("bibm-2025")}
<h2>Current roles and affiliations</h2>
<div class="cards">{cards}</div>
<p class="muted">Professional memberships: {mem}.</p>
<h2>Research focus</h2>
<p>Inclusive and multilingual language models · machine translation and translation methods · evaluation
science and the reliability of LLM-as-a-judge · human-centred and trustworthy AI · AI for healthcare,
biology and scientific discovery. See <a href="research.html">Research</a> and <a href="rinn-ai.html">Rinn AI</a>.</p>
<h2>Education</h2><ul>{edu}</ul>
<h2>Verified profiles</h2>
<ul class="ids">{profile_links_html(profile)}</ul>
"""
    pages["about"] = page("about","About", body,
        "Biography, current roles and affiliations of Dr Haithem Afli — Rinn AI Institutional Co-Lead at MTU, "
        "ADAPT Centre PI, and founder of the Human-Centred AI Research Group.", person_ld)

    # RESEARCH
    theme_desc = {
     "hcai":"Studying AI as a socio-technical and cultural system: algorithmic accountability, interpretability, and the human and societal dimensions of intelligent systems.",
     "multilingual":"Cross-lingual and cultural reasoning, low-resource and dialectal NLP (with emphasis on Arabic), tokenisation, and multilingual evaluation.",
     "trustworthy":"Robustness, uncertainty, fairness, explainability, privacy-preserving and federated learning, and AI governance.",
     "evaluation":"Evaluation as measurement science: distribution-based evaluation, dynamic and robustness-aware benchmarks, and the reliability of LLM-as-a-judge.",
     "bio":"Machine learning for genomics, microbiome analysis, and biomedical and clinical data, including foundation models for biological data.",
     "innovation":"Translating research into responsible, human-centred products and services through spin-outs, industry partnerships and commercialisation."
    }
    theme_why = {
     "hcai":"Because AI systems increasingly mediate knowledge, culture and decisions, they must be understood — and designed — with people at the centre, not only optimised for benchmark scores.",
     "multilingual":"Most language technology works best in English; billions of speakers of Arabic and under-resourced languages are underserved. This work aims to close that gap.",
     "trustworthy":"AI that informs healthcare, governance and public life must be robust, fair and explainable before it can be relied upon.",
     "evaluation":"If we cannot measure a model's capability reliably, we cannot trust claims about it. This work treats evaluation itself as a scientific instrument.",
     "bio":"Genomic and clinical data are among the highest-impact places for trustworthy AI — where reliability and interpretability directly affect people.",
     "innovation":"Research creates value when it reaches classrooms, clinics, public services and industry; commercialisation is how impact becomes durable."
    }
    _t2c = {}
    for _c in (load("collections.json") or {}).get("collections", []):
        for _th in _c.get("themes", []): _t2c[_th] = _c["id"]
    _pub_counts = {}
    for _p in pubs["publications"]:
        for _th in _p.get("themes", []): _pub_counts[_th] = _pub_counts.get(_th, 0) + 1
    def theme_section(t):
        why = f'<p class="muted"><strong>Why it matters:</strong> {esc(theme_why[t["id"]])}</p>' if t["id"] in theme_why else ""
        browse = f'<p class="theme-browse"><a href="theme-{esc(t["id"])}.html"><strong>Open the {esc(t["name"])} theme page →</strong></a></p>'
        if t["id"] in _t2c:
            n = _pub_counts.get(t["id"], 0)
            browse += (f'<p class="theme-browse"><a href="collections.html#{esc(_t2c[t["id"]])}">'
                       f'Browse {n} publication{"s" if n!=1 else ""} in this theme →</a></p>')
        return (f'<section id="{esc(t["id"])}"><h3>{esc(t["name"])}</h3>'
                f'<p>{esc(theme_desc.get(t["id"],""))}</p>{why}{browse}</section>')
    _tbid = {t["id"]: t for t in profile["themes"]}
    theme_groups = [("Primary research programme", ["multilingual"]),
                    ("Cross-cutting themes", ["evaluation", "trustworthy", "hcai"]),
                    ("Application themes", ["bio", "innovation"])]
    sects = ""
    for gname, ids in theme_groups:
        inner = "".join(theme_section(_tbid[i]) for i in ids if i in _tbid)
        if inner:
            sects += f'<h2 class="theme-group">{esc(gname)}</h2>{inner}'
    agenda = [
     ("Inclusive multilingual language models","Developing and evaluating models that work reliably across high-resource and under-resourced languages."),
     ("Cultural reasoning in generative AI","Investigating how language models interpret culturally specific knowledge, values and reasoning patterns."),
     ("Reliable multilingual evaluation","Studying the limitations of automated judges, benchmarks and evaluation protocols across languages and cultures."),
     ("Inclusive translation technologies","Designing translation methods that preserve meaning, cultural context, sentiment and specialist terminology."),
     ("Human-centred AI evaluation","Combining expert, community and user evaluation with technical metrics."),
     ("AI for health and scientific domains","Applying language models, genomic foundation models and trustworthy machine learning to healthcare and biological research."),
     ("Research translation and innovation","Connecting foundational research with public-sector, education, industry and societal applications."),
    ]
    agenda_html = "".join(f'<li><strong>{esc(h)}</strong> — {esc(d)}</li>' for h,d in agenda)
    body = (f'<p class="lede">Research organised into coherent programmes rather than isolated topics. '
            f'Dr Afli\'s current focus centres on inclusive and multilingual language models — the theme he '
            f'deputy-leads in <a href="rinn-ai.html">Rinn Artificial Intelligence</a> — which connects with, '
            f'but does not replace, his wider programmes in evaluation science, trustworthy AI and AI for '
            f'biology.</p>{sects}'
            f'<section id="agenda"><h2>Current research agenda</h2><ol class="agenda">{agenda_html}</ol></section>'
            f'<div class="grid-img">{figs_for("research", limit=4)}</div>')
    pages["research"] = page("research","Research", body,
        "Research programmes of Dr Haithem Afli: inclusive multilingual language models, evaluation science, trustworthy AI, AI for biology.", person_ld)

    # RESEARCH JOURNEY — a narrative from verified career milestones (nothing fabricated)
    ms_data = load("milestones.json") or {"chapters": [], "milestones": []}
    _ms_by_ch = {}
    for m in ms_data.get("milestones", []):
        _ms_by_ch.setdefault(m.get("chapter"), []).append(m)
    def _ms_links(m):
        r = m.get("refs", {}); out = []
        if m["id"] in ms2event: out.append(f'<a href="event-{ms2event[m["id"]]}.html"><strong>Event page</strong></a>')
        if r.get("pub"): out.append(link("publications.html", "Publication"))
        if r.get("project"): out.append(link("projects.html", "Project"))
        if r.get("news"): out.append(link("news.html", "In the news"))
        if r.get("theme"): out.append(link(f"research.html#{r['theme']}", themes.get(r["theme"], r["theme"])))
        return (' <span class="muted">· ' + " · ".join(out) + '</span>') if out else ""
    journey_body = ['<p class="lede">From statistical machine translation to national leadership in human-centred, '
                    'multilingual AI — the evolution of Dr Afli\'s research, told through verified milestones, each '
                    'linked to its publications, projects and impact.</p>']
    for ch in ms_data.get("chapters", []):
        mis = sorted(_ms_by_ch.get(ch["id"], []), key=lambda x: x["year"])
        journey_body.append(f'<section id="{esc(ch["id"])}"><h2>{esc(ch["title"])} '
                            f'<span class="muted">{esc(ch.get("years",""))}</span></h2>'
                            f'<p>{esc(ch.get("narrative",""))}</p>')
        if mis:
            journey_body.append('<ul class="pubs">')
            _jcat = {"keynote":"Keynote","publication":"Publication","grant":"Grant","patent":"Patent",
                     "leadership":"Leadership","award":"Award","media":"Media","education":"Education","industry":"Industry"}
            for m in mis:
                journey_body.append(f'<li class="tl-item"><span class="tag">{esc(_jcat.get(m.get("category"), m.get("category","")))}</span> '
                    f'<span class="tl-year">{m["year"]}</span> <strong>{esc(m["title"])}</strong><br>'
                    f'{esc(m.get("description",""))} <em class="muted">{esc(m.get("impact",""))}</em>'
                    f'{_ms_links(m)}</li>')
            journey_body.append('</ul>')
        journey_body.append('</section>')
    journey_body.append('<p class="note">This journey is assembled from the site\'s verified records — '
                        '<a href="publications.html">publications</a>, <a href="projects.html">projects</a>, '
                        '<a href="talks.html">talks</a> and <a href="news.html">news</a>. '
                        'See the full <a href="timeline.html">timeline</a>.</p>')
    journey_ld = {"@context": "https://schema.org", "@type": "ProfilePage",
        "mainEntity": {"@type": "Person", "name": profile["name"], "jobTitle": profile["title"]}}
    pages["journey"] = page("journey", "Research Journey", "".join(journey_body),
        "The research journey of Dr Haithem Afli — from multimodal machine translation to national leadership in human-centred, multilingual AI, told through verified milestones.",
        journey_ld)

    # EVENT PAGES — one canonical, verified record per major event (sections hidden when unsupported)
    events_data = EVENTS
    _pubmap = {p.get("id"): p for p in pubs["publications"]}
    _newsmap = {n.get("id"): n for n in news.get("items", [])}
    _ms_by_id = {m["id"]: m for m in MILESTONES}
    event_slug = {e["id"]: "event-"+e["id"] for e in events_data if e.get("state") == "approved-public"}
    def event_page(e):
        th = e.get("theme")
        rows = []
        meta = " · ".join(x for x in [e.get("type"), str(e.get("year","")),
               ("Host: "+e["host"]) if e.get("host") and e["host"]!="—" else "",
               e.get("location") if e.get("location") and e["location"]!="—" else ""] if x)
        parts = [f'<p class="lede">{esc(e["summary"])}</p>', f'<p class="muted">{esc(meta)}</p>']
        if e.get("why"): parts.append(f'<h2>Why it mattered</h2><p>{esc(e["why"])}</p>')
        if e.get("contribution"): parts.append(f'<h2>Scientific / professional contribution</h2><p>{esc(e["contribution"])}</p>')
        # connected records (only real ones)
        conn = []
        if th in themes: conn.append(f'<li><span class="tag">Research theme</span> <a href="research.html#{esc(th)}">{esc(themes[th])}</a></li>')
        if e.get("pub") in _pubmap:
            p = _pubmap[e["pub"]]; u = ("https://doi.org/"+p["doi"]) if p.get("doi") else p.get("url","publications.html")
            conn.append(f'<li><span class="tag">Related publication</span> {link(u, p["title"])} <span class="muted">— {esc(p["venue"])}, {p["year"]}</span></li>')
        if e.get("project"): conn.append(f'<li><span class="tag">Related project</span> <a href="projects.html">{esc(e["project"])}</a></li>')
        if e.get("news") in _newsmap:
            n = _newsmap[e["news"]]; conn.append(f'<li><span class="tag">Media coverage</span> {link(n.get("link","news.html"), n["headline"])}</li>')
        if e.get("milestone") in _ms_by_id:
            m = _ms_by_id[e["milestone"]]; conn.append(f'<li><span class="tag">Milestone</span> <a href="journey.html#{esc(m.get("chapter",""))}">{esc(m["title"])}</a></li>')
        if e.get("related_event") in event_slug:
            conn.append(f'<li><span class="tag">Related event</span> <a href="{event_slug[e["related_event"]]}.html">{esc(next((x["title"] for x in events_data if x["id"]==e["related_event"]),"Related event"))}</a></li>')
        # collaborators from the linked publication (verified authorship)
        if e.get("pub") in _pubmap:
            au = [a for a in _pubmap[e["pub"]]["authors"] if a.strip().lower() not in ("haithem afli",)][:6]
            if au: conn.append(f'<li><span class="tag">Collaborators</span> {esc(", ".join(au))}</li>')
        if conn: parts.append('<h2>Connected records</h2><ul class="pubs">'+"".join(conn)+'</ul>')
        # external/official link
        if e.get("link") and e["link"].startswith("http"):
            parts.append(f'<p>{link(e["link"], "Official source / more information")}</p>')
        elif e.get("link"): parts.append(f'<p><a href="{esc(e["link"])}">More on this →</a></p>')
        # materials note (private assets are NOT published; truthful availability signal only)
        if e.get("materials") == "on-request":
            parts.append('<p class="note">Slides and any recording from this event are held in the research '
                         'group\'s archive and are available on request; they are prepared for release with '
                         'transcripts and permissions before publication.</p>')
        if e.get("review_note"):
            parts.append(f'<p class="muted"><em>Note: {esc(e["review_note"])}</em></p>')
        # recommendation strip — related records by shared theme (graph adjacency), with labels
        recs = []
        for ev in events_data:
            if ev["id"] != e["id"] and ev.get("state")=="approved-public" and ev.get("theme")==th:
                recs.append(f'<li><a href="{event_slug[ev["id"]]}.html">{esc(ev["title"])}</a> <span class="muted">— {esc(ev.get("type",""))}</span></li>')
        for m in MILESTONES:
            if m.get("refs",{}).get("theme")==th and m["id"]!=e.get("milestone"):
                recs.append(f'<li><a href="journey.html#{esc(m.get("chapter",""))}">{esc(m["title"])}</a> <span class="muted">— milestone</span></li>')
        recs = recs[:6]
        if recs: parts.append('<h2>Related research</h2><ul class="pubs">'+"".join(recs)+'</ul>')
        parts.append(f'<p class="muted">Compiled from verified records (publications, projects, news and profile) on {esc(BUILD_DATE)}. '
                     f'Part of the <a href="journey.html">research journey</a> · <a href="timeline.html">timeline</a>.</p>')
        ev_ld = {"@context":"https://schema.org",
                 "@type":("Event" if e.get("type","").lower().find("keynote")>=0 or "talk" in e.get("type","").lower() else "CreativeWork"),
                 "name":e["title"], **({"startDate":str(e["year"])} if e.get("year") else {}),
                 **({"location":{"@type":"Place","name":e["location"]}} if e.get("location") and e["location"]!="—" else {}),
                 "about":themes.get(th, th) if th else None}
        return page(event_slug[e["id"]], e["title"], "".join(parts),
                    e["summary"][:155], {k:v for k,v in ev_ld.items() if v is not None})
    for e in events_data:
        if e.get("state") == "approved-public":
            pages[event_slug[e["id"]]] = event_page(e)

    # THEME LANDING PAGES — aggregate verified evidence per research theme
    THEME_OVERVIEW = {
      "hcai": ("Human-Centred AI", "Designing AI that amplifies human judgement, dignity and inclusion rather than displacing them.",
               "Because the value of AI depends on how well it serves people, communities and public institutions."),
      "multilingual": ("Multilingual & Culturally Aware AI", "Language technologies — translation, speech and language models — that work across high- and low-resource languages and cultures.",
               "Because most of the world's languages are under-served by current AI, widening rather than closing gaps."),
      "trustworthy": ("Trustworthy AI, Safety & Governance", "Privacy-preserving, explainable and accountable machine learning, and NLP for political and societal analysis.",
               "Because AI used in health, migration and public discourse must be safe, private and open to scrutiny."),
      "evaluation": ("Evaluation Science & LLM-as-a-Judge", "Rigorous methods for evaluating language models, embeddings and translation — including the limits of automated judges.",
               "Because progress claims are only as sound as the evaluation behind them."),
      "bio": ("AI for Healthcare, Biology & Genomics", "Language models, genomic foundation models and trustworthy ML applied to health and biological data.",
               "Because precision medicine and biological discovery increasingly depend on reading data at scale."),
      "innovation": ("Responsible Innovation & Commercialisation", "Translating research into open-source tools, patents and industry collaboration.",
               "Because durable impact comes from research reaching classrooms, clinics, public services and industry."),
    }
    ev_proj_theme = {e["project"]: e["theme"] for e in EVENTS if e.get("project") and e.get("theme")}
    def theme_page(tid):
        name, overview, why = THEME_OVERVIEW[tid]
        tp = [p for p in pubs["publications"] if tid in p.get("themes", [])]
        tm = [m for m in MILESTONES if m.get("refs", {}).get("theme") == tid]
        te = [e for e in EVENTS if e.get("theme") == tid and e.get("state") == "approved-public"]
        tn = [n for n in news.get("items", []) if tid in (n.get("related_entities") or [])]
        tpr = [pr for pr, th in ev_proj_theme.items() if th == tid]
        parts = [f'<div class="theme-hero"><p class="lede">{esc(overview)}</p>'
                 f'<p class="muted"><strong>Why it matters:</strong> {esc(why)}</p></div>']
        if te:
            parts.append('<h2>Featured events</h2><ul class="pubs">' + "".join(
                f'<li><a href="{event_slug[e["id"]]}.html">{esc(e["title"])}</a> <span class="muted">— {esc(e.get("type",""))}, {e.get("year","")}</span></li>' for e in te) + '</ul>')
        if tpr:
            parts.append('<h2>Related projects</h2><ul class="pubs">' + "".join(f'<li><a href="projects.html">{esc(pr)}</a></li>' for pr in tpr) + '</ul>')
        if tp:
            parts.append(f'<h2>Publications <span class="muted">({len(tp)})</span></h2><ul class="pubs">' + "".join(
                f'<li>{(link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"]))} <span class="muted">— {esc(p["venue"])}, {p["year"]}</span></li>'
                for p in sorted(tp, key=lambda x:-x["year"])[:12]) + '</ul>')
            if len(tp) > 12: parts.append(f'<p><a href="publications.html">All {len(tp)} publications in this theme →</a></p>')
        if tm:
            parts.append('<h2>Milestones</h2><ul class="pubs">' + "".join(
                f'<li>{m["year"]} — <a href="journey.html#{esc(m.get("chapter",""))}">{esc(m["title"])}</a></li>' for m in sorted(tm, key=lambda x:x["year"])) + '</ul>')
        if tn:
            parts.append('<h2>In the news</h2><ul class="pubs">' + "".join(f'<li>{link(n.get("link","news.html"), n["headline"])}</li>' for n in tn) + '</ul>')
        parts.append('<p class="muted">See the <a href="research.html">full research agenda</a> · '
                     '<a href="collections.html">collections</a> · <a href="journey.html">research journey</a>.</p>')
        ld = {"@context":"https://schema.org","@type":"CollectionPage","name":name+" — research theme","about":name}
        return page("theme-"+tid, name, "".join(parts),
                    f"{name}: {overview}", ld)
    for tid in THEME_OVERVIEW:
        pages["theme-"+tid] = theme_page(tid)

    # RESEARCH VISION — philosophy, restrained tone, from verified themes/agenda
    doctoral_n = len(sup.get("doctoral_completed", []))
    pages["research-vision"] = page("research-vision", "Research Vision",
        '<p class="lede">AI should not simply become more capable. It should become more trustworthy, multilingual, '
        'culturally aware and human-centred.</p>'
        '<p>Dr Afli\'s research pursues language technologies that work for people and communities who are '
        'under-served by current AI — across languages, cultures, health and public life. The programme joins four '
        'commitments:</p>'
        '<h2>Multilingual and low-resource languages</h2><p>Most of the world\'s languages lack the data and tools '
        'that high-resource languages enjoy. Work on <a href="theme-multilingual.html">multilingual and culturally '
        'aware AI</a> — including Irish, Arabic and other low-resource languages, and open-source tooling such as '
        'adaptNMT and adaptMLLM — aims to narrow that gap.</p>'
        '<h2>Cultural reasoning</h2><p>Language models interpret culturally specific knowledge and values unevenly. '
        'Research on culturally grounded question answering (for example the Arabic PalmX and QIAS systems) studies '
        'how models handle cultural context.</p>'
        '<h2>Trustworthy evaluation</h2><p>Claims of progress are only as sound as the evaluation behind them. Work on '
        '<a href="theme-evaluation.html">evaluation science</a> — robust text-embedding evaluation (PTEB) and the '
        'limits of automated judges — treats evaluation as a first-class research problem.</p>'
        '<h2>Human-centred and trustworthy AI</h2><p>Privacy-preserving and explainable methods — including the '
        'European patent on split federated learning — keep people and their data at the centre. See '
        '<a href="theme-hcai.html">Human-Centred AI</a> and <a href="theme-trustworthy.html">Trustworthy AI</a>.</p>'
        '<h2>How the centres contribute</h2><p>The <a href="group.html">Human-Centred AI Research Group</a> is the '
        'group home; the <a href="rinn-ai.html">Rinn Artificial Intelligence</a> national centre and the '
        '<a href="https://www.adaptcentre.ie/" rel="noopener">ADAPT Centre</a> provide national research platforms; '
        'and Horizon Europe projects such as GenDAI extend the work in AI for health.</p>'
        '<h2>Future directions</h2><p>The current agenda centres on inclusive multilingual language models, cultural '
        'reasoning in generative AI, and reliable multilingual evaluation — advancing AI that is dependable, '
        'culturally aware and human-centred across language, health and society.</p>'
        '<h2>The next five years</h2>'
        '<p>Building on the current programme and existing collaborations, the work over the coming years is expected '
        'to develop along several connected lines:</p>'
        '<ul class="pubs">'
        '<li><strong>Inclusive multilingual models.</strong> Extending language models and translation to more '
        'low-resource languages, continuing the direction of adaptNMT and adaptMLLM.</li>'
        '<li><strong>Trustworthy evaluation.</strong> Strengthening evaluation methods for language models and '
        'embeddings, building on PTEB and work on the limits of automated judges.</li>'
        '<li><strong>Trustworthy and safe AI.</strong> Advancing privacy-preserving and explainable methods, '
        'continuing the split-federated-learning line protected by the 2024 patent.</li>'
        '<li><strong>AI for health.</strong> Deepening the genomics-and-language work through Horizon Europe (GenDAI) '
        'and related collaborations.</li>'
        '<li><strong>Public-sector and societal AI.</strong> Continuing the PoliticalNLP direction on NLP for '
        'governance and public discourse.</li>'
        '<li><strong>European collaboration and doctoral research.</strong> Growing the Human-Centred AI Research '
        'Group and its role within Rinn AI and ADAPT, and supervising doctoral researchers across these themes.</li>'
        '</ul>'
        '<p class="muted">These directions build on existing projects, publications and partnerships rather than new '
        'commitments; specific projects and funding are confirmed as they are announced.</p>'
        '<p class="muted">Explore the <a href="journey.html">research journey</a>, the '
        '<a href="research.html">research themes</a>, and the <a href="publications.html">publications</a> behind this vision.</p>',
        "The research vision of Dr Haithem Afli: trustworthy, multilingual, culturally aware and human-centred AI, grounded in verified research.",
        {"@context":"https://schema.org","@type":"AboutPage","name":"Research Vision"})

    # AUDIENCE PAGES — tailored entry points from verified evidence
    def audience_page(slug, title, desc, body_html):
        return page(slug, title, body_html, desc, person_ld)
    pages["prospective-phd"] = audience_page("prospective-phd", "For Prospective PhD Students",
        "Information for prospective PhD students interested in human-centred, multilingual and trustworthy AI with Dr Haithem Afli at MTU.",
        '<p class="lede">If you are interested in human-centred, multilingual or trustworthy AI, you may be a good fit '
        'for doctoral research in the Human-Centred AI Research Group.</p>'
        '<h2>Research areas</h2><div class="audience-cta">'
        + "".join(f'<a href="theme-{t["id"]}.html">{esc(t["name"])}</a>' for t in profile["themes"]) + '</div>'
        '<h2>Supervision</h2><p>Dr Afli supervises doctoral and master\'s researchers and has supervised '
        f'{doctoral_n} completed doctoral researchers to date (see <a href="supervision.html">supervision</a>). '
        'Supervision spans multilingual NLP, evaluation, trustworthy AI and AI for health.</p>'
        '<h2>Research environment</h2><p>Doctoral researchers work within the '
        '<a href="group.html">Human-Centred AI Research Group</a> at MTU, with links to the national '
        '<a href="rinn-ai.html">Rinn Artificial Intelligence</a> centre and the ADAPT Centre.</p>'
        '<h2>How to get in touch</h2><p>Send a short description of your interests and background via the '
        '<a href="contact.html">contact page</a>. Please note that funding availability varies and is not guaranteed; '
        'any funded openings are advertised through official channels.</p>')
    pages["collaborate"] = audience_page("collaborate", "For Researchers & Collaborators",
        "Collaboration with Dr Haithem Afli: publications, projects, open-source software, datasets and European research.",
        '<p class="lede">Opportunities to collaborate on multilingual, human-centred and trustworthy AI.</p>'
        '<h2>Research outputs</h2><p>See the <a href="publications.html">publications</a> (peer-reviewed and preprint), '
        'the <a href="showcase.html">research showcase</a> and <a href="collections.html">collections</a> by theme.</p>'
        '<h2>Software &amp; resources</h2><p>Open-source tooling includes adaptNMT and adaptMLLM for low-resource '
        'neural machine translation; language resources include the gaHealth English–Irish health corpus and the '
        'TransCasm bilingual corpus (see the relevant <a href="publications.html">publications</a>).</p>'
        '<h2>European &amp; national projects</h2><p>Current and recent projects include Horizon Europe (GenDAI) and '
        'Horizon 2020 (ITFLOWS, WARIFA, STOP, SliceNet); see <a href="projects.html">projects &amp; funding</a>.</p>'
        '<h2>Get in touch</h2><p>Proposals for joint work and consortia are welcome via the '
        '<a href="contact.html">contact page</a>.</p>')
    pages["industry"] = audience_page("industry", "For Industry & Public Sector",
        "Applied AI expertise for industry and the public sector: multilingual NLP, trustworthy AI, AI for health, and technology transfer.",
        '<p class="lede">Applied research and technology transfer in multilingual, trustworthy and human-centred AI.</p>'
        '<h2>Expertise</h2><p>Multilingual NLP and translation, trustworthy and privacy-preserving machine learning, '
        'evaluation of language models, and AI for health and biological data.</p>'
        '<h2>Innovation &amp; intellectual property</h2><p>Outcomes include the European patent on split federated '
        'learning (WO/2024/227944), Enterprise Ireland Innovation Voucher collaborations with Irish SMEs, and '
        'LinguaAnalysis (multilingual financial text analytics, acquired in 2024). See '
        '<a href="innovation.html">innovation &amp; industry</a>.</p>'
        '<h2>Collaboration pathways</h2><p>Engagement is possible through the ADAPT Centre, Rinn AI, funded projects '
        'and direct research agreements. Start a conversation via the <a href="contact.html">contact page</a>.</p>')
    pages["for-media"] = audience_page("for-media", "For Media & Event Organisers",
        "Media and speaking information for Dr Haithem Afli: biography, speaking topics, keynote experience and media coverage.",
        '<p class="lede">Information for journalists and event organisers.</p>'
        '<h2>Short biography</h2><p>Dr Haithem Afli is a Lecturer in Artificial Intelligence at Munster '
        'Technological University, Institutional Co-Lead for Rinn Artificial Intelligence at MTU, and a Principal '
        'Investigator in the ADAPT Centre. He founded and leads the Human-Centred AI Research Group.</p>'
        '<h2>Extended biography</h2><p>His research advances multilingual, culturally aware and trustworthy '
        'human-centred AI, spanning language models, translation, evaluation and AI for health. He holds a European '
        'patent, has led and contributed to Horizon Europe and Horizon 2020 projects, and serves as an evaluator for '
        'the European Commission (REA). See the <a href="about.html">full biography</a> and '
        '<a href="journey.html">research journey</a>.</p>'
        '<h2>Speaking topics</h2><p>Human-centred and inclusive AI; multilingual and low-resource language '
        'technologies; trustworthy AI and evaluation; AI for health and precision medicine.</p>'
        '<h2>Keynote &amp; talk experience</h2><p>Recent international talks include the keynote '
        '<a href="event-language-of-life-brazil.html">“The Language of Life”</a> (Brazil) and an '
        '<a href="event-language-of-life-wuhan.html">invited talk at Wuhan University</a>.</p>'
        '<h2>Media coverage</h2><p><a href="event-cork-independent-2025.html">Cork Independent — “Ireland at AI '
        '‘crossroads’”</a> (2025).</p>'
        '<h2>Downloads &amp; contact</h2><p>An up-to-date <a href="cv.html">CV</a> is available. Photographs are '
        'provided on request following rights and consent review. Contact via the '
        '<a href="contact.html">contact page</a>.</p>')

    # ---- publication taxonomy: professional labels, BibTeX entry types, output categories ----
    TYPE_LABEL = {"journal":"Journal articles","conference":"Conference papers","workshop":"Workshop papers",
        "shared-task":"Shared-task papers","proceedings":"Edited proceedings","preprint":"Preprints",
        "book-chapter":"Book chapters","report":"Reports and deliverables"}
    TYPE_LABEL_SG = {"journal":"Journal article","conference":"Conference paper","workshop":"Workshop paper",
        "shared-task":"Shared-task paper","proceedings":"Edited proceedings","preprint":"Preprint",
        "book-chapter":"Book chapter","report":"Report / deliverable"}
    BIB_ENTRY = {"journal":"article","conference":"inproceedings","workshop":"inproceedings",
        "shared-task":"inproceedings","book-chapter":"incollection","proceedings":"proceedings",
        "report":"techreport","preprint":"misc"}
    TYPE_CAT = {"journal":"peer","conference":"peer","workshop":"peer","shared-task":"peer","book-chapter":"peer",
        "preprint":"preprint","proceedings":"proceedings","report":"report"}
    CAT_ORDER = [("peer","Peer-reviewed publications"),("preprint","Preprints"),
        ("proceedings","Edited proceedings"),("report","Technical reports & project deliverables")]
    PUBS = sorted(pubs["publications"], key=lambda x:(-x["year"], x["title"]))

    # deterministic, unique BibTeX keys for EVERY record: firstauthor + year + short-title token
    _STOP = {"a","an","the","on","of","for","and","to","in","using","towards","from","with","an","is","at"}
    def _incomplete_authors(p):
        return (not p.get("authors")) or any(a.strip().lower() in ("et al.","et al","others") for a in p["authors"])
    bibkeys, _used = {}, set()
    for p in PUBS:
        last = re.sub(r'[^a-z]','', (p["authors"][0].split()[-1].lower() if p.get("authors") else "afli")) or "afli"
        tok = ""
        for w in re.sub(r'[^a-z0-9 ]',' ', p["title"].lower()).split():
            if w not in _STOP and len(w) > 2: tok = w; break
        base = f"{last}{p['year']}{tok}"; key = base; i = 0
        while key in _used: i += 1; key = f"{base}{chr(ord('a')+i-1)}"
        _used.add(key); bibkeys[p["id"]] = key

    def best_url(p):  # source-link priority: DOI > publisher/landing > ACL Anthology
        if p.get("doi"): return "https://doi.org/"+p["doi"]
        if p.get("url"): return p["url"]
        if p.get("anthology_id"): return "https://aclanthology.org/"+p["anthology_id"]+"/"
        return None

    def bibtex_for(p):
        """Deterministic BibTeX from VERIFIED fields only. Suppressed when the author list is
        incomplete (never emits 'et al.'). ACL Anthology entries link the canonical .bib instead."""
        if p.get("anthology_id") or _incomplete_authors(p): return None
        entry = BIB_ENTRY.get(p.get("type"), "misc")
        venue_field = "journal" if entry == "article" else ("booktitle" if entry in ("inproceedings","incollection") else
                      ("title" if entry == "proceedings" else ("institution" if entry == "techreport" else "howpublished")))
        lines = [f'@{entry}{{{bibkeys[p["id"]]},',
                 f'  title = {{{p["title"]}}},',
                 f'  author = {{{" and ".join(p["authors"])}}},',
                 f'  {venue_field} = {{{p["venue"]}}},',
                 f'  year = {{{p["year"]}}},']
        if p.get("pages"): lines.append(f'  pages = {{{p["pages"]}}},')
        if p.get("volume"): lines.append(f'  volume = {{{p["volume"]}}},')
        if p.get("publisher"): lines.append(f'  publisher = {{{p["publisher"]}}},')
        if p.get("doi"): lines.append(f'  doi = {{{p["doi"]}}},')
        if p.get("arxiv"): lines.append(f'  eprint = {{{p["arxiv"]}}}, archivePrefix = {{arXiv}},')
        if best_url(p): lines.append(f'  url = {{{best_url(p)}}},')
        lines.append("}")
        return "\n".join(lines)

    # PUBLICATIONS — compact cards, grouped by output category, with search/year/type filters
    def pub_item(p):
        authors_full = [esc(a) for a in p["authors"]]
        authors = ", ".join(authors_full) if len(authors_full) <= 8 else \
                  ", ".join(authors_full[:8]) + f' <span class="muted">… +{len(authors_full)-8} more</span>'
        url = best_url(p)
        title = link(url, p["title"]) if url else esc(p["title"])
        badge = f'<span class="ptype">{esc(TYPE_LABEL_SG.get(p.get("type"), p.get("type","")))}</span>'
        status = ""  # output category + type badge already convey status; avoid raw labels
        yr = f'{p["year"]}'
        if p.get("arxiv_deposit"): yr += f' <span class="muted">(arXiv deposit {esc(p["arxiv_deposit"])})</span>'
        links = []
        if p.get("doi"): links.append(link("https://doi.org/"+p["doi"], "DOI"))
        if p.get("pdf_url"): links.append(link(p["pdf_url"], "PDF"))
        if p.get("arxiv_url") or p.get("arxiv"): links.append(link(p.get("arxiv_url") or ("https://arxiv.org/abs/"+p["arxiv"]), "arXiv"))
        if p.get("anthology_id"): links.append(link("https://aclanthology.org/"+p["anthology_id"]+"/", "ACL Anthology"))
        if p.get("anthology_id"): links.append(link("https://aclanthology.org/"+p["anthology_id"]+".bib", "BibTeX"))
        linkrow = (' · ' + " · ".join(links)) if links else ""
        th = "".join(f'<a class="tag" href="research.html#{esc(t)}">{esc(themes.get(t,t))}</a>' for t in p.get("themes",[]))
        extra = ""
        # graphical abstract — shown only when a real image asset exists (no placeholders)
        if p.get("graphical_abstract") and p["graphical_abstract"] in IMGS:
            extra += f'<div class="pub-ga">{fig(p["graphical_abstract"], cls="fig")}</div>'
        if p.get("abstract"):
            extra += f'<details class="pub-abs"><summary>Abstract</summary><p>{esc(p["abstract"])}</p></details>'
        bib = bibtex_for(p)
        if bib:
            extra += f'<details class="pub-abs"><summary>BibTeX</summary><pre class="bibtex">{esc(bib)}</pre></details>'
        search = esc(" ".join([p["title"]] + p["authors"] + [p.get("venue",""), str(p["year"])]).lower())
        return (f'<li class="pub" data-year="{p["year"]}" data-type="{esc(p["type"])}" '
                f'data-themes="{esc(" ".join(p.get("themes",[])))}" data-search="{search}" data-bibkey="{esc(bibkeys[p["id"]])}">'
                f'<div class="pub-t">{title} {badge}{status}</div>'
                f'<div class="pub-m">{authors}. <em>{esc(p["venue"])}</em>, {yr}.{linkrow}</div>'
                f'<div class="pub-tags">{th}</div>{extra}</li>')

    years = sorted({p["year"] for p in PUBS}, reverse=True)
    present_types = [t for t in TYPE_LABEL if any(p["type"]==t for p in PUBS)]
    peer_n = sum(1 for p in PUBS if TYPE_CAT.get(p["type"])=="peer")
    total_n = len(PUBS)
    filt = ('<div class="filters" role="group" aria-label="Search and filter publications">'
            '<label for="p-q">Search <input type="search" id="p-q" placeholder="title, author, venue…" autocomplete="off"></label>'
            '<label for="p-year">Year <select id="p-year"><option value="">All years</option>'
            + "".join(f'<option value="{y}">{y}</option>' for y in years) + '</select></label>'
            '<label for="p-type">Type <select id="p-type"><option value="">All types</option>'
            + "".join(f'<option value="{esc(t)}">{esc(TYPE_LABEL[t])}</option>' for t in present_types)
            + '</select></label>'
            '<span id="p-count" class="result-count" role="status" aria-live="polite"></span></div>')
    # category sections with progressive disclosure
    cats_html = ""
    for cid, clabel in CAT_ORDER:
        cps = [p for p in PUBS if TYPE_CAT.get(p["type"]) == cid]
        if not cps: continue
        cards = "".join(pub_item(p) for p in cps)
        cats_html += (f'<section class="pubcat" data-cat="{cid}"><h2>{esc(clabel)} '
                      f'<span class="cat-count muted">({len(cps)})</span></h2>'
                      f'<ul class="pubs list">{cards}</ul>'
                      f'<button type="button" class="show-more btn-secondary" hidden>Show more</button></section>')
    body = ('<p class="lede">A complete record of Dr Haithem Afli\'s research outputs — peer-reviewed publications, '
            'preprints, edited proceedings and technical reports — maintained on an ongoing basis, with metadata drawn '
            'from authoritative scholarly sources (ACL Anthology, Crossref and the original publishers). The '
            f'continuously updated record is also on {link("https://aclanthology.org/people/haithem-afli/","ACL Anthology")}, '
            f'{link("https://orcid.org/0000-0002-7449-4707","ORCID")} and '
            f'{link("https://dblp.org/pid/120/2260.html","DBLP")}.</p>'
            f'<p class="pub-summary"><strong>{peer_n}</strong> peer-reviewed publications · '
            f'<strong>{total_n}</strong> total research outputs.</p>'
            f'{filt}{cats_html}'
            '<script src="pubs.js" defer></script>')
    pub_graph = {"@context":"https://schema.org","@graph":[
        {"@type":("Book" if p.get("type")=="book-chapter" else "ScholarlyArticle"),
         "headline":p["title"],"name":p["title"],
         "author":[{"@type":"Person","name":a} for a in p["authors"]],
         "datePublished":str(p["year"]),"isPartOf":p["venue"],
         **({"abstract":p["abstract"]} if p.get("abstract") else {}),
         **({"publisher":{"@type":"Organization","name":p["publisher"]}} if p.get("publisher") else {}),
         **({"url":best_url(p)} if best_url(p) else {}),
         **({"sameAs":"https://doi.org/"+p["doi"], "identifier":"https://doi.org/"+p["doi"]} if p.get("doi") else {})}
        for p in PUBS]}
    pages["publications"] = page("publications","Publications", body,
        "Complete research-output record of Dr Haithem Afli: peer-reviewed publications, preprints, edited proceedings and reports in NLP, multilingual and human-centred AI.", pub_graph)

    # RINN AI (dedicated page)
    f = rinn["facts"]
    priorities = ""
    for p in rinn["theme"]["priorities"]:
        priorities += f'<h3>{esc(p["h"])}</h3><ul class="pubs">' + "".join(f'<li>{esc(i)}</li>' for i in p["items"]) + '</ul>'
    eco = "".join(f'<section><h3>{esc(e["name"])}</h3><p>{esc(e["desc"])}</p></section>' for e in rinn["ecosystem"])
    rinn_ld = {"@context":"https://schema.org","@type":"ResearchProject","name":rinn["programme_name"],
               "funder":{"@type":"Organization","name":rinn["funder"]},"url":rinn["verification"]["sources"][0],
               "member":{"@type":"Person","name":profile["name"],"roleName":rinn["afli_roles"]["short"]}}
    body = f"""
<p class="lede">{esc(rinn["paraphrase"])}</p>
<p><strong>{esc(rinn["programme_name"])}</strong> is a {esc(rinn["programme_type"]).lower()} supported by
{esc(rinn["funder"])}. It brings together researchers across foundational and applied AI, Data Science,
health, governance, society and culture.</p>
<table><tbody>
<tr><th>Funder</th><td>{esc(rinn["funder"])}</td></tr>
<tr><th>National investment</th><td>{esc(f["national_investment"])} <span class="muted">({esc(f["national_investment_note"])})</span></td></tr>
<tr><th>Participating organisations</th><td>{f["organisations"]}</td></tr>
<tr><th>Research themes</th><td>{f["research_themes"]}</td></tr>
<tr><th>Clusters</th><td>{f["clusters"]} — {esc(", ".join(rinn["clusters"]))}</td></tr>
</tbody></table>
<p class="note">Programme facts verified via {link(rinn["verification"]["sources"][0],"Research Ireland")}
(retrieved {esc(rinn["verification"]["verification_date"])}). Rinn AI is directed nationally by
Prof. Noel O'Connor (DCU); Dr Afli's role is institutional (MTU), not national.</p>

<h2>Dr Haithem Afli's involvement</h2>
<p>Dr Haithem Afli serves as {esc(rinn["afli_roles"]["institutional"])}, {esc(rinn["afli_roles"]["theme"])},
and {esc(rinn["afli_roles"]["pi"])}.</p>

<h2>Inclusive Language Model &amp; Translation Methods</h2>
<p>{esc(rinn["theme"]["intro"])}</p>
{priorities}

<h2>Research contribution at MTU</h2>
<p>{esc(rinn["theme"]["mtu_contribution"])}</p>

<h2 id="ecosystem">Rinn AI, ADAPT and the HAI Research Group</h2>
<p>{esc(rinn["ecosystem_note"])}</p>
{eco}
"""
    pages["rinn-ai"] = page("rinn-ai","Rinn Artificial Intelligence at MTU", body,
        "Dr Haithem Afli's involvement in Rinn Artificial Intelligence: Institutional Co-Lead at MTU, Deputy Theme Lead for Inclusive Language Model & Translation Methods, and Principal Investigator.",
        rinn_ld)

    # PROJECTS & FUNDING
    def proj_rows(lst):
        out = ""
        for p in lst:
            if "WITHHELD" in (p.get("note","")): continue  # unresolved claims not publicly displayed
            amt = []
            if p.get("total"): amt.append(f'Total: {esc(p["total"])}')
            if p.get("mtu"): amt.append(f'MTU: {esc(p["mtu"])}')
            note = f' <span class="muted">({esc(p["note"])})</span>' if p.get("note") else ""
            vp = ""
            name = link(p.get("url"), p["name"]) if p.get("url") else esc(p["name"])
            out += (f'<tr><td>{name}{vp}</td><td>{esc(p.get("programme") or p.get("funder",""))}</td>'
                    f'<td>{esc(p.get("role",""))}</td><td>{" · ".join(amt)}{note}</td><td>{esc(p.get("period",""))}</td></tr>')
        return out
    withheld = [p["name"] for p in projects["national_projects"] if "WITHHELD" in p.get("note","")]
    body = f"""
<p class="lede">Funded research projects and institutional roles. Funding figures show the total programme or
consortium award and, where relevant, the MTU allocation.</p>
<div class="grid-img">{figs_for("projects", limit=3)}</div>
<h2>National programmes</h2>
<table><thead><tr><th>Project</th><th>Funder</th><th>Role</th><th>Funding</th><th>Period</th></tr></thead>
<tbody>{proj_rows(projects["national_projects"])}</tbody></table>
<h2>European projects</h2>
<table><thead><tr><th>Project</th><th>Programme</th><th>Role</th><th>Funding</th><th>Period</th></tr></thead>
<tbody>{proj_rows(projects["eu_projects"])}</tbody></table>
"""
    pages["projects"] = page("projects","Projects & Funding", body,
        "Funded research projects of Dr Haithem Afli across Horizon Europe, H2020 and national programmes.", person_ld)

    # HAI GROUP
    pages["group"] = page("group","Human-Centred AI Research Group",
        """<p class="lede">The Human-Centred AI (HAI) Research Group at MTU studies how humans and AI interact
across languages, cultures and application domains, with the aim of building AI systems that are reliable,
trustworthy, interpretable, culturally aware and human-centred.</p>
<h2>Themes</h2><ul><li>Human-centred evaluation and evaluation science</li><li>Multilingual and culturally aware AI</li>
<li>Trustworthy AI, safety and governance</li><li>Reasoning and reasoning stability</li>
<li>AI for healthcare, biology and genomics</li></ul>
<h2>Collaboration and supervision</h2>
<p>The group welcomes prospective PhD students, postdoctoral researchers and collaborators whose interests
align with these themes. Enquiries via the <a href="contact.html">contact page</a>.</p>"""
        + figs_for("group"),
        "The Human-Centred AI (HAI) Research Group led by Dr Haithem Afli at MTU.", person_ld)

    # SUPERVISION
    def card(p, fields):
        outputs = ""
        if p.get("outputs"):
            outputs = '<div class="pub-tags">'+"".join(f'<span class="tag">{esc(o)}</span>' for o in p["outputs"])+'</div>'
        meta = " · ".join(esc(p[f]) for f in fields if p.get(f))
        return f'<li><strong>{esc(p["name"])}</strong> <span class="muted">— {meta}</span>{outputs}</li>'
    doc = "".join(card(p,["institution","period","role","area"]) for p in sup["doctoral_completed"])
    post = "".join(card(p,["institution","period","area"]) for p in sup["postdoctoral_completed"])
    fell = "".join(card(p,["institution","period","area"]) for p in sup["fellows_completed"])
    intern = "".join(card(p,["home","host","year","project"]) for p in sup["interns_visitors"])
    # masters grouped by year with topic filter
    myears = sorted({m["period"] for m in sup["masters"]}, reverse=True)
    alltopics = sorted({t for m in sup["masters"] for t in m["topics"]})
    mfilt = ('<div class="filters"><label>Topic <select id="f-topic"><option value="">All</option>'
             + "".join(f'<option value="{esc(t)}">{esc(t.replace("-"," ").title())}</option>' for t in alltopics)
             + '</select></label></div>')
    mitems = ""
    for yr in myears:
        rows = [m for m in sup["masters"] if m["period"]==yr]
        insts = sorted({m["institution"] for m in rows})
        mitems += f'<h3>{esc(yr)} — {esc(", ".join(insts))}</h3><ul class="pubs">'
        for m in rows:
            flagged = ""
            prog = ' <span class="muted">(research project)</span>' if "Research Project" in (m.get("notes") or "") else ""
            outputs = ""
            if m.get("notes") and ("publication" in m["notes"] or "PhD" in m["notes"] or "published" in m["notes"]) and "VERIFY" not in m["notes"]:
                outputs = f' <span class="tag">linked output</span>'
            mitems += (f'<li data-topics="{esc(" ".join(m["topics"]))}"><strong>{esc(m["name"])}</strong>{prog} '
                       f'<span class="muted">— <em>{esc(m["project"])}</em></span>{flagged}{outputs}</li>')
        mitems += "</ul>"
    body = f"""
<p class="lede">Doctoral, postdoctoral and Master's research supervision and mentoring. Records are based on
available academic records and may not be exhaustive. Where the specific role is not documented, entries are
described neutrally as research supervised or advised by Dr Haithem Afli.</p>
{figs_for("supervision")}
<h2>Doctoral supervision (completed)</h2><ul class="pubs">{doc}</ul>
<h2>Postdoctoral mentoring (completed)</h2><ul class="pubs">{post}</ul>
<h2>Research fellows (completed)</h2><ul class="pubs">{fell}</ul>
<h2>Research interns and visiting scholars</h2><ul class="pubs">{intern}</ul>
<h2>Master's research supervision</h2>
<p class="note">{esc(sup["note"])}</p>{mfilt}<div id="masters">{mitems}</div>
<script src="sup.js" defer></script>
"""
    pages["supervision"] = page("supervision","Supervision & Mentoring", body,
        "Doctoral, postdoctoral and Master's research supervision by Dr Haithem Afli.", person_ld)

    # TEACHING
    tp = "".join(f'<li><strong>{esc(p["name"])}</strong> <span class="muted">— {esc(p["detail"])} ({esc(p["period"])})</span></li>' for p in teaching["programmes"])
    pages["teaching"] = page("teaching","Teaching",
        f'<p class="lede">{esc(teaching["philosophy"])}</p>'
        f'<h2>Programmes and modules</h2><ul class="pubs">{tp}</ul>'
        f'<h2>Teaching and outreach</h2><div class="grid-img">{figs_for("teaching", limit=6)}</div>',
        "Teaching by Dr Haithem Afli: MSc in AI, Computational Biology, Data Analytics, and executive education.", person_ld)

    # INNOVATION
    inn = "".join(f'<li><strong>{esc(i["name"])}</strong> <span class="muted">— {esc(i["detail"])}</span></li>' for i in projects["innovation"])
    pat = (f'<h2>Patent</h2><ul class="pubs"><li>{link(patent["patent"]["url"], patent["patent"]["title"])} '
           f'<span class="muted">— {esc(patent["patent"]["number"])}, filed {esc(patent["patent"]["filing_date"])}; '
           f'inventors: {esc(", ".join(patent["patent"]["inventors"]))}.</span></li></ul>')
    pages["innovation"] = page("innovation","Innovation & Industry",
        f'<p class="lede">Translating research into responsible, human-centred products and services.</p><ul class="pubs">{inn}</ul>{pat}',
        "Innovation, commercialisation and industry engagement by Dr Haithem Afli, including patent WO/2024/227944.", person_ld)

    # TALKS
    tk = "".join(f'<li><strong>{esc(t["title"])}</strong> <span class="muted">— {esc(t["event"])}{", "+str(t["year"]) if t.get("year") else ""} ({esc(t["role"])})</span></li>' for t in talks["selected"])
    pages["talks"] = page("talks","Talks & Outreach",
        f'<p class="lede">Selected invited talks, keynotes and public engagement.</p>'
        f'<div class="grid-img">{figs_for("talks", limit=8)}</div>'
        f'<h2>Selected talks</h2><ul class="pubs">{tk}</ul>',
        "Invited talks, keynotes and public engagement by Dr Haithem Afli.", person_ld)

    # SERVICE
    def ul(items): return "<ul class='pubs'>"+"".join(f"<li>{esc(x)}</li>" for x in items)+"</ul>"
    pages["service"] = page("service","Leadership & Service",
        f'<h2>University governance</h2>{ul(service["governance"])}'
        f'<h2>External examining</h2>{ul(service["external_examiner"])}'
        f'<h2>Conferences, journals and committees</h2>{ul(service["committees"])}'
        f'<h2>External expert roles</h2>{ul(service["external_expert"])}',
        "University leadership, governance, reviewing and professional service of Dr Haithem Afli.", person_ld)

    # NEWS (category + theme filters, date sort, links to source + original post)
    cats = sorted({n.get("category","other") for n in news["items"]})
    def news_item(n):
        srcs = []
        if n.get("link"): srcs.append(link(n["link"],"Authoritative source"))
        if n.get("original_post"): srcs.append(link(n["original_post"],"Original post"))
        img = ""
        if n.get("image") and isinstance(n["image"],dict) and valid_url(n["image"].get("src","")):
            img = (f'<img src="{esc(n["image"]["src"])}" alt="{esc(n["image"].get("alt",""))}" '
                   f'width="{esc(n["image"].get("w",560))}" height="{esc(n["image"].get("h",315))}" loading="lazy">')
        nt = "".join(f'<span class="tag">{esc(themes.get(t,t))}</span>' for t in n.get("related_entities",[]) if t.startswith("theme:") for t in [t.split(":")[1]])
        return (f'<li data-cat="{esc(n.get("category",""))}" '
                f'data-themes="{esc(" ".join(t.split(":")[1] for t in n.get("related_entities",[]) if t.startswith("theme:")))}">'
                f'<span class="muted">{esc(n["date"])}</span> · <span class="tag">{esc(n.get("category","")) }</span><br>'
                f'<strong>{esc(n["headline"])}</strong><br>{img}{esc(n["summary"])} '
                f'{" · ".join(srcs)}</li>')
    nfilt = ('<div class="filters" role="group" aria-label="Filter news">'
             '<label>Category <select id="n-cat"><option value="">All</option>'
             + "".join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in cats)
             + '</select></label> <label>Theme <select id="n-theme"><option value="">All</option>'
             + "".join(f'<option value="{esc(t["id"])}">{esc(t["name"])}</option>' for t in profile["themes"])
             + '</select></label></div>')
    ni = "".join(news_item(n) for n in sorted(news["items"], key=lambda x:x["date"], reverse=True))
    pages["news"] = page("news","News",
        f'<p class="lede">Academic news: publications, talks, projects and research-group activity. '
        f'Each item is sourced and dated; where a professional LinkedIn or X post announced the activity, '
        f'the original post is linked alongside the authoritative source.</p>{nfilt}'
        f'<ul class="news">{ni}</ul><p><a href="feed.xml">Atom feed</a></p>'
        '<script src="news.js" defer></script>',
        "Academic news from Dr Haithem Afli and the HAI Research Group.", person_ld)

    # MEDIA — accessible, filterable photograph gallery + multimedia (recordings, audio, slides)
    cat_labels = {"research-conferences":"Research conferences","teaching":"Teaching",
        "public-engagement":"Public engagement","research-collaborations":"Research collaborations",
        "supervision":"Supervision and academic milestones","hai-group":"HAI Research Group","portrait":"Portrait"}
    gallery_cats = [c for c in gallery["categories"] if c != "portrait"
                    and any(i.get("category")==c and i["id"] in IMGS for i in gallery["images"])]
    gimgs = ""
    for i in gallery["images"]:
        if i.get("category") in gallery_cats and i["id"] in IMGS:
            gimgs += fig(i["id"], attrs=f' data-cat="{esc(i["category"])}"')
    gallery_filter = ('<div class="filters" role="group" aria-label="Filter photographs by category">'
        '<label for="g-cat">Category <select id="g-cat"><option value="">All categories</option>'
        + "".join(f'<option value="{esc(c)}">{esc(cat_labels.get(c, c.replace("-"," ").title()))}</option>' for c in gallery_cats)
        + '</select></label><span id="g-count" class="result-count" role="status" aria-live="polite"></span></div>')

    # Multimedia items (recordings, audio, slides, posters) — approved + accessible only
    media = load("media.json") or {"items": []}
    def _media_ok(m):
        if m.get("status") != "approved" or str(m.get("id","")).startswith("example-"): return False
        if m.get("kind") in ("video","audio") and not m.get("transcript"): return False
        target = m.get("file") or m.get("link")
        if not target: return False
        if m.get("file") and not (ROOT/m["file"]).exists(): return False  # never reference a missing asset
        return True
    mitems = [m for m in media.get("items", []) if _media_ok(m)]
    def media_card(m):
        thumb = fig(m["thumbnail"]) if m.get("thumbnail") in IMGS else ""
        trans = f' · {link(m["transcript"], "Transcript")}' if m.get("transcript") else ""
        desc = f'<p class="muted">{esc(m.get("description",""))}</p>' if m.get("description") else ""
        head = f'<h3>{esc(m["title"])} <span class="muted">{esc(m.get("date",""))}</span></h3>'
        if m["kind"] == "video" and m.get("file"):
            cap = f'<track kind="captions" src="{esc(m["captions"])}" label="Captions" default>' if m.get("captions") else ""
            body_m = (f'<video controls preload="none"{f" poster="+chr(34)+esc(IMGS[m["thumbnail"]]["src"])+chr(34) if m.get("thumbnail") in IMGS else ""}>'
                      f'<source src="{esc(m["file"])}">{cap}Your browser does not support the video element.</video>')
        elif m["kind"] == "audio" and m.get("file"):
            body_m = f'<audio controls preload="none"><source src="{esc(m["file"])}">Your browser does not support the audio element.</audio>'
        elif m["kind"] in ("slides","poster"):
            body_m = thumb + f'<p>{link(m.get("file") or m.get("link"), "Download "+("slides" if m["kind"]=="slides" else "poster")+" (PDF)")}</p>'
        else:  # external recording — privacy-preserving link, never an auto-loading tracking embed
            body_m = thumb + f'<p>{link(m.get("link"), "Watch/listen on the official page (opens in a new tab)")}</p>'
        return f'<div class="media-card">{head}{body_m}<p class="muted">{link(m.get("license","") ,"Licence") if m.get("license","").startswith("http") else ""}{trans}</p>{desc}</div>'
    media_sections = ""
    for kind, label in [("video","Talk recordings"),("audio","Audio & podcasts"),
                        ("slides","Slides & posters"),("poster","Posters")]:
        ms = [m for m in mitems if m.get("kind")==kind]
        if kind=="slides": ms = [m for m in mitems if m.get("kind") in ("slides","poster")]
        if kind=="poster": continue
        if not ms: continue
        media_sections += f'<section><h2>{esc(label)}</h2><div class="cards">'+"".join(media_card(m) for m in ms)+'</div></section>'
    media_note = ("" if mitems else
        '<p class="note">Talk recordings, audio, slides and graphical abstracts are published here as they become '
        'available; each recording is accompanied by a transcript for accessibility.</p>')

    body = ('<p class="lede">Photographs, recordings and slides from Dr Afli\'s research, teaching and public '
            'engagement. Every recording is published with a transcript, and no third-party tracking is used.</p>'
            + media_sections + media_note
            + '<h2>Photographs</h2>' + gallery_filter
            + f'<div class="grid-img" id="gallery-grid">{gimgs}</div>'
            + '<script src="gallery.js" defer></script>')
    pages["gallery"] = page("gallery","Media", body,
        "Media gallery of Dr Haithem Afli: photographs, talk recordings, audio and slides from research, teaching, and public engagement.", person_ld)

    # RESEARCH INTELLIGENCE portal
    conf = load("conference_deadlines.json"); fund = load("funding_calls.json")
    conf_editions = (conf or {}).get("editions", []); fund_calls = (fund or {}).get("calls", [])
    empty_note = ('<p class="note">Entries here are added only from official sources by the automated sync '
                  'pipeline (<code>scripts/admin_sync.py</code>); no speculative dates are shown. '
                  'No verified upcoming entries at the time of the last sync — the watchlist below shows the '
                  'series and programmes monitored.</p>')
    def watch_ul(d):
        return "".join(f'<h3>{esc(k)}</h3><p>{esc(", ".join(v))}</p>' for k,v in d.items())

    pages["research-intelligence"] = page("research-intelligence","Research Intelligence",
        '<p class="lede">A maintained view of upcoming conference deadlines, European and Irish funding calls, '
        'a research calendar, and the fortnightly HAI Research Brief. Everything here is drawn from official '
        'sources; nothing is invented.</p>'
        '<div class="cards">'
        '<div class="role-card"><h3><a href="conference-deadlines.html">Conference deadlines</a></h3><p class="muted">ACL-family, Arabic NLP, and AI/ML venues relevant to HAI.</p></div>'
        '<div class="role-card"><h3><a href="funding-calls.html">Funding calls</a></h3><p class="muted">Horizon Europe, MSCA, ERC, Research Ireland, Enterprise Ireland.</p></div>'
        '<div class="role-card"><h3><a href="research-calendar.html">Research calendar</a></h3><p class="muted">Verified deadlines and events, with calendar (ICS) feeds.</p></div>'
        '<div class="role-card"><h3><a href="newsletter.html">HAI Research Brief</a></h3><p class="muted">Fortnightly newsletter — news, publications, opportunities.</p></div>'
        '<div class="role-card"><h3><a href="subscribe.html">Subscribe</a></h3><p class="muted">Choose newsletter, deadline and funding alerts.</p></div>'
        '</div>'
        '<h2>Feeds and calendars</h2>'
        '<p class="muted">Subscribe in your feed reader (RSS) or calendar app (ICS) to receive updates automatically. '
        'Each feed is described below so you can choose the ones that fit your needs.</p>'
        '<div class="cards">'
        '<div class="role-card"><h3><a href="feeds/deadlines.xml">Conference Deadlines (RSS)</a></h3>'
        '<p class="muted"><strong>Purpose:</strong> submission, notification and camera-ready dates for relevant venues. '
        '<strong>For:</strong> researchers and students planning submissions. '
        '<strong>Use:</strong> follow in a feed reader so no deadline is missed.</p></div>'
        '<div class="role-card"><h3><a href="feeds/funding-calls.xml">Funding Opportunities (RSS)</a></h3>'
        '<p class="muted"><strong>Purpose:</strong> European and Irish calls relevant to the group. '
        '<strong>For:</strong> principal investigators and prospective partners. '
        '<strong>Use:</strong> track open calls and deadlines as they are published.</p></div>'
        '<div class="role-card"><h3><a href="feeds/hai-newsletter.xml">Research Updates (RSS)</a></h3>'
        '<p class="muted"><strong>Purpose:</strong> news, publications and highlights from the HAI Research Brief. '
        '<strong>For:</strong> collaborators and anyone following the group. '
        '<strong>Use:</strong> a lightweight way to keep up without email.</p></div>'
        '<div class="role-card"><h3><a href="calendars/all-research-deadlines.ics">Research Calendar (ICS)</a></h3>'
        '<p class="muted"><strong>Purpose:</strong> verified deadlines and events as calendar entries. '
        '<strong>For:</strong> anyone who prefers their calendar to a feed reader. '
        '<strong>Use:</strong> subscribe once and dates appear alongside your own events.</p></div>'
        '</div>'
        '<p class="muted">See also the <a href="analytics-map.html">aggregated global research reach</a>.</p>',
        "Research intelligence for HAI: conference deadlines, funding calls, calendar and the HAI Research Brief.", person_ld)

    def edition_html(e):
        rows = ""
        for d in e.get("deadlines", []):
            when = esc(d["date"])
            if d.get("timezone"): when += f' <span class="muted">23:59 {esc(d["timezone"])}</span>'
            utc = f'<span class="muted">{esc(d["utc_datetime"][:16].replace("T"," "))} UTC</span>' if d.get("utc_datetime") else ""
            rows += (f'<tr><td>{esc(d["label"])}</td><td>{when}</td><td>{utc}</td>'
                     f'<td>{link(d.get("source_url"),"source") if d.get("source_url") else ""}</td></tr>')
        loc = f'{esc(e.get("location",""))}' + (f' · {esc(e["conference_start"])}–{esc(e["conference_end"])}' if e.get("conference_start") else "")
        return (f'<section><h3>{link(e.get("official_url"), e["edition"]) if e.get("official_url") else esc(e["edition"])} '
                f'<span class="tag">{esc(e.get("status",""))}</span></h3>'
                f'<p class="muted">{loc}. All deadlines Anywhere on Earth (UTC−12); UTC equivalents shown.</p>'
                f'<table><thead><tr><th>Deadline</th><th>Date</th><th>UTC</th><th>Source</th></tr></thead>'
                f'<tbody>{rows}</tbody></table></section>')
    editions_html = "".join(edition_html(e) for e in conf_editions)
    pages["conference-deadlines"] = page("conference-deadlines","Conference Deadlines",
        '<p class="lede">Submission and camera-ready deadlines for conferences relevant to HAI, from official '
        'conference pages, calls, and ACL Rolling Review. ARR submission, conference commitment, direct submission, '
        'workshop and shared-task deadlines are tracked as distinct types.</p>'
        + (('<h2>Upcoming</h2>' + editions_html) if conf_editions else empty_note)
        + '<h2>Series monitored</h2>' + watch_ul((conf or {}).get("watchlist", {}))
        + '<p><a href="calendars/nlp-deadlines.ics">NLP deadlines (ICS)</a> · '
          '<a href="calendars/ai-deadlines.ics">AI/ML deadlines (ICS)</a> · '
          '<a href="calendars/arabic-nlp-deadlines.ics">Arabic NLP (ICS)</a></p>',
        "Conference deadlines relevant to the Human-Centred AI Research Group.", person_ld)

    pages["funding-calls"] = page("funding-calls","Funding Calls",
        '<p class="lede">European and Irish funding calls relevant to Dr Afli and HAI, from the EC Funding &amp; '
        'Tenders Portal, ERC, MSCA, Research Ireland and Enterprise Ireland. Programmes without a fixed deadline '
        'are shown as “Rolling applications”; official titles and identifiers are preserved.</p>'
        + (empty_note if not fund_calls else "")
        + '<h2>Programme families monitored</h2>' + watch_ul((fund or {}).get("programmes", {}))
        + '<p><a href="calendars/eu-funding-calls.ics">EU funding (ICS)</a> · '
          '<a href="calendars/irish-funding-calls.ics">Irish funding (ICS)</a> · '
          '<a href="feeds/funding-calls.xml">RSS</a></p>'
          '<p class="note">Refer to each official call document for the definitive conditions.</p>',
        "European and Irish funding calls relevant to HAI.", person_ld)

    # collect verified upcoming deadlines across sources, nearest first
    cal_items = []
    for e in conf_editions:
        for d in e.get("deadlines", []):
            if d.get("verification_status")=="verified" and d.get("date") >= BUILD_DATE:
                cal_items.append((d["date"], f'{e["edition"]} — {d["label"]}', e.get("official_url","")))
    for c in fund_calls:
        if c.get("deadline") and c.get("verification_status")=="verified" and c["deadline"] >= BUILD_DATE:
            cal_items.append((c["deadline"], f'{c.get("programme","")} — {c.get("title","")}', c.get("official_url","")))
    cal_items.sort()
    cal_list = ("".join(f'<li><span class="muted">{esc(dt)}</span> — {link(u,t) if u else esc(t)}</li>' for dt,t,u in cal_items)
                if cal_items else '<li class="muted">No verified upcoming dates at the last sync.</li>')
    pages["research-calendar"] = page("research-calendar","Research Calendar",
        '<p class="lede">A calendar of verified conference deadlines, conference dates, funding deadlines and HAI '
        'events. Only verified dates are included; speculative dates are never shown.</p>'
        f'<h2>Upcoming (nearest first)</h2><ul class="pubs">{cal_list}</ul>'
        '<h2>Calendar subscriptions</h2><ul class="pubs">'
        '<li><a href="calendars/all-research-deadlines.ics">All research deadlines</a></li>'
        '<li><a href="calendars/nlp-deadlines.ics">NLP deadlines</a></li>'
        '<li><a href="calendars/ai-deadlines.ics">AI/ML deadlines</a></li>'
        '<li><a href="calendars/arabic-nlp-deadlines.ics">Arabic NLP deadlines</a></li>'
        '<li><a href="calendars/eu-funding-calls.ics">EU funding calls</a></li>'
        '<li><a href="calendars/irish-funding-calls.ics">Irish funding calls</a></li>'
        '<li><a href="calendars/hai-events.ics">HAI events</a></li></ul>',
        "Research calendar and subscribable ICS feeds for HAI deadlines and events.", person_ld)

    pages["newsletter"] = page("newsletter","HAI Research Brief",
        '<p class="lede">The <strong>HAI Research Brief</strong> — news, publications, opportunities and research '
        'advances from the Human-Centred AI Research Group at MTU, published fortnightly.</p>'
        + (('<h2>Issues</h2><ul class="pubs">' + "".join(
            f'<li><a href="{esc(i.get("url","#"))}">Issue {esc(i.get("number"))}</a> — {esc(i.get("date"))}</li>'
            for i in (load("newsletter_issues.json") or {}).get("issues", [])) + '</ul>')
           if (load("newsletter_issues.json") or {}).get("issues") else
           '<p class="note">The first issue is in preparation. Issues are generated in review mode from verified '
           'sources and published after approval; no issue is auto-sent. <a href="subscribe.html">Subscribe</a> to '
           'be notified.</p>')
        + '<p><a href="feeds/hai-newsletter.xml">Newsletter RSS</a> · <a href="subscribe.html">Subscribe</a></p>',
        "The HAI Research Brief — fortnightly newsletter of the Human-Centred AI Research Group.", person_ld)

    pages["subscribe"] = page("subscribe","Subscribe",
        '<p class="lede">Choose what to receive. Newsletter subscription uses double opt-in and every email '
        'includes an unsubscribe and preference link. You are never subscribed to categories you did not choose.</p>'
        '<p class="note">Subscriptions are handled by a privacy-compliant mailing service and use double opt-in. '
        'To be added in the meantime, please get in touch: '+email_component(profile, inline=True)+'.</p>'
        '<h2>Categories</h2><ul class="pubs">'
        '<li>HAI Research Brief (fortnightly newsletter)</li><li>Conference deadlines</li>'
        '<li>European funding calls</li><li>Research Ireland calls</li><li>Enterprise Ireland calls</li>'
        '<li>HAI opportunities</li><li>HAI events and seminars</li></ul>'
        '<h2>Newsletter language</h2><p class="muted">English is sent by default; translated summary editions are '
        'sent for a chosen language only where an approved translation exists.</p>'
        '<p>See the <a href="privacy.html">privacy notice</a>.</p>',
        "Subscribe to the HAI Research Brief and research-intelligence alerts.", person_ld)

    pages["analytics-map"] = page("analytics-map","Global Research Reach",
        '<p class="lede">Aggregated, country-level view of where the website is read. No individual visitors, IP '
        'addresses, exact locations or movement are shown or stored.</p>'
        '<p class="note">A privacy-conscious analytics provider (e.g. Plausible or Cloudflare Web Analytics) has not '
        'yet been connected, so no visitor data is available. When connected, this page shows a country-level map '
        'with an accessible data table; countries with fewer than five visitors are combined into a regional total. '
        'See the <a href="privacy.html">privacy notice</a>.</p>'
        '<h2>Reach (accessible table)</h2><table><thead><tr><th>Country</th><th>Visitors</th><th>Share</th></tr></thead>'
        '<tbody><tr><td colspan="3" class="muted">No aggregated data yet.</td></tr></tbody></table>',
        "Aggregated, privacy-preserving country-level view of website readership.", person_ld)

    pages["languages"] = page("languages","Languages",
        '<p class="lede">This website is published in English. Translations into additional languages are being '
        'introduced through a review-based workflow; unreviewed machine translations are not published.</p>'
        '<p class="note">Translated pages, when available, are provided to improve accessibility. Where any '
        'difference arises, the English page and the linked official sources are the canonical references.</p>'
        '<h2>Planned languages</h2><ul class="pubs">'
        + "".join(f'<li lang="{esc(l["code"])}">{esc(l["native"])} <span class="muted">— {esc(l["status"])}</span></li>'
                  for l in (load("languages.json") or {}).get("languages", []))
        + '</ul>',
        "Language availability and translation policy for the website.", person_ld)

    pages["privacy"] = page("privacy","Privacy",
        '<p class="lede">This website uses privacy-conscious analytics to understand aggregate usage and improve its '
        'academic and research content.</p>'
        '<h2>Analytics</h2><p>When enabled, analytics are aggregated and country-level only: no persistent tracking '
        'cookies, no cross-site tracking, no advertising identifiers, no behavioural profiling, and no storage of raw '
        'IP addresses or precise location. Only meaningful academic interactions (for example, CV downloads or '
        'publication-link clicks) may be counted, in aggregate. Retention is short and justified.</p>'
        '<h2>Newsletter</h2><p>Newsletter subscription uses explicit double opt-in; every email carries an '
        'unsubscribe and preference link. Subscriber data is held with a privacy-compliant mailing provider, never in '
        'this website’s repository, and email addresses never appear in generated files.</p>'
        '<p class="muted">The aggregated, country-level <a href="analytics-map.html">research-reach view</a> '
        'contains no individual or location-precise data.</p>'
        '<h2>Contact</h2><p>Privacy questions: '+email_component(profile, inline=True)+'.</p>',
        "Privacy notice: privacy-conscious analytics and newsletter data handling.", person_ld)

    # RESEARCH COMMUNICATION LAYER (single source of truth; nothing fabricated; drafts stay private)
    comm = load("communication.json") or {"assets":{}}
    collections_data = load("collections.json") or {"collections":[]}
    def publ(p):  # one publication list item
        t = link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"])
        return f'<li>{t} <span class="muted">— {esc(p["venue"])}, {p["year"]}</span></li>'

    # RESEARCH SHOWCASE — selected outputs, all from existing verified data
    flagship_pubs = [p for p in pubs["publications"] if p.get("instrument_claim") or p.get("anthology_id")][:6]
    keynotes = [t for t in talks.get("selected",[]) if "keynote" in t.get("role","").lower() or "invited" in t.get("role","").lower()]
    showcase_body = (
        '<p class="lede">A concise overview of the strongest research outputs — for visitors new to the work. '
        'Every item links to its authoritative record; nothing here replaces the peer-reviewed source.</p>'
        f'<h2>Selected publications</h2><ul class="pubs">{"".join(publ(p) for p in flagship_pubs)}</ul>'
        '<h2>Research programmes</h2><ul class="pubs">'
        f'<li>{link("https://www.researchireland.ie/news/rinn-network/","Rinn Artificial Intelligence")} — Institutional Co-Lead at MTU, Deputy Theme Lead, PI. <a href="rinn-ai.html">Details →</a></li>'
        f'<li>{link("https://www.adaptcentre.ie/","ADAPT Centre")} — PI and MTU Lead.</li>'
        f'<li><a href="group.html">Human-Centred AI Research Group</a> — Founder and Lead.</li></ul>'
        + (f'<h2>Keynotes and invited talks</h2><ul class="pubs">' + "".join(
            f'<li><strong>{esc(t["title"])}</strong> <span class="muted">— {esc(t["event"])}{", "+str(t["year"]) if t.get("year") else ""} ({esc(t["role"])})</span></li>'
            for t in keynotes) + '</ul>' if keynotes else '')
        + '<h2>Patent</h2><ul class="pubs"><li>'
        + link(patent["patent"]["url"], patent["patent"]["title"]) + f' <span class="muted">— {esc(patent["patent"]["number"])}</span></li></ul>'
        + '<h2>Explore</h2><p><a href="collections.html">Research collections</a> · '
          '<a href="timeline.html">Research timeline</a> · <a href="publications.html">All publications</a> · '
          '<a href="projects.html">Projects &amp; funding</a>.</p>')
    pages["showcase"] = page("showcase","Research Showcase", showcase_body,
        "A curated overview of Dr Haithem Afli's selected publications, programmes, keynotes and patent.", person_ld)

    # RESEARCH COLLECTIONS — auto-aggregated by existing theme tags
    coll_html = ""
    for c in collections_data["collections"]:
        cp = [p for p in pubs["publications"] if set(c["themes"]) & set(p.get("themes",[]))]
        if not cp: continue
        coll_html += (f'<section id="{esc(c["id"])}"><h2>{esc(c["name"])} '
                      f'<span class="muted">({len(cp)})</span></h2><ul class="pubs">'
                      + "".join(publ(p) for p in sorted(cp, key=lambda x:-x["year"])) + '</ul></section>')
    pages["collections"] = page("collections","Research Collections",
        '<p class="lede">Publications grouped by research theme. Collections aggregate existing records '
        'automatically; each paper links to its authoritative source.</p>' + coll_html,
        "Curated collections of Dr Haithem Afli's research by theme: human-centred AI, multilingual NLP, evaluation, trustworthy AI, AI for biology.", person_ld)

    # RESEARCH TIMELINE — chronological view from existing data (publications by year + milestones)
    events = []
    for p in pubs["publications"]:
        events.append((p["year"], "publication", (link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"])) + f' <span class="muted">— {esc(p["venue"])}</span>'))
    events.append((2026, "role", "Institutional Co-Lead, Rinn Artificial Intelligence at MTU (Deputy Theme Lead; PI)"))
    events.append((2024, "patent", link(patent["patent"]["url"], "Patent WO/2024/227944 — On-Air Split Federated Learning")))
    events.append((2018, "role", "Lecturer & PI, MTU; founded the Human-Centred AI Research Group"))
    events.append((2014, "milestone", "PhD, Le Mans Université — Statistical Machine Translation in a Multimodal Context"))
    # verified career milestones (keynotes, grants, awards, media, leadership) → the timeline backbone
    for m in MILESTONES:
        if m.get("category") in ("keynote","grant","award","media","leadership","patent"):
            events.append((m["year"], m.get("category"),
                f'{esc(m["title"])} <a class="muted" href="journey.html#{esc(m.get("chapter",""))}">(journey)</a>'))
    _fgroup = {"publication":"publications","keynote":"talks","talk":"talks","grant":"projects",
               "leadership":"leadership","role":"leadership","award":"recognition","patent":"recognition",
               "media":"media","milestone":"milestones"}
    tl = ""
    for yr in sorted({e[0] for e in events}, reverse=True):
        items = [e for e in events if e[0]==yr]
        tl += f'<h3 class="tl-year">{yr}</h3><ul class="pubs">' + "".join(
            f'<li data-f="{_fgroup.get(k,"other")}"><span class="tag">{esc(k)}</span> {v}</li>' for _,k,v in items) + '</ul>'
    tl_filter = ('<div class="filter-chips" role="group" aria-label="Filter the timeline">'
        '<button type="button" data-f="" aria-pressed="true">All</button>'
        + "".join(f'<button type="button" data-f="{f}" aria-pressed="false">{lab}</button>'
                  for f,lab in [("publications","Publications"),("talks","Talks"),("projects","Projects &amp; grants"),
                                ("leadership","Leadership"),("recognition","Recognition"),("media","Media")])
        + '<span id="tl-count" class="result-count" role="status" aria-live="polite"></span></div>')
    pages["timeline"] = page("timeline","Research Timeline",
        '<p class="lede">The evolution of the research programme over time — publications and major milestones, '
        'drawn from the site\'s verified records. Filter by kind, or read the narrative in the '
        '<a href="journey.html">research journey</a>.</p>' + tl_filter
        + f'<div id="tl-list">{tl}</div><script src="timeline.js" defer></script>',
        "A chronological timeline of Dr Haithem Afli's publications, roles and milestones.", person_ld)

    # RESEARCH ASSISTANT — grounded, client-side, citation-first (no server, no LLM, cannot hallucinate)
    assistant_body = (
        '<p class="lede">Ask about Dr Afli\'s research, publications, projects, supervision or talks. '
        'Every answer comes only from this website\'s verified records, always shows its sources, and says '
        'clearly when the answer is not known — it never invents information.</p>'
        '<noscript><p class="note">Ask Me needs JavaScript. You can still use the '
        '<a href="showcase.html">showcase</a>, <a href="publications.html">publications</a>, '
        '<a href="collections.html">collections</a> and <a href="timeline.html">timeline</a> to explore the same records.</p></noscript>'
        '<section id="asst" class="asst" aria-label="Ask Me">'
        '<div class="asst-intents"><span class="muted">I am a…</span> '
        '<button type="button" class="chip" data-intent="phd">Prospective PhD student</button>'
        '<button type="button" class="chip" data-intent="industry">Industry partner</button>'
        '<button type="button" class="chip" data-intent="journalist">Journalist</button>'
        '<button type="button" class="chip" data-intent="msc">Prospective MSc student</button>'
        '<button type="button" class="chip" data-intent="collab">Academic collaborator</button></div>'
        '<div class="asst-controls">'
        '<label class="asst-lang">Query language '
        '<select id="asst-lang"><option value="auto">Auto-detect</option>'
        '<option value="en">English</option><option value="ar">العربية</option><option value="fr">Français</option>'
        '<option value="es">Español</option><option value="de">Deutsch</option><option value="it">Italiano</option>'
        '<option value="tr">Türkçe</option><option value="ru">Русский</option><option value="ga">Gaeilge</option>'
        '<option value="fa">فارسی</option><option value="he">עברית</option></select></label>'
        '<label class="asst-bench"><input type="checkbox" id="asst-bench"> Transparency mode '
        '<span class="muted">(show retrieval scores)</span></label></div>'
        '<form id="asst-form" class="asst-form" role="search" autocomplete="off">'
        '<label for="asst-q" class="sr-only">Ask a question</label>'
        '<input type="text" id="asst-q" name="q" placeholder="e.g. What is the research on multilingual evaluation?" '
        'aria-describedby="asst-hint">'
        '<button type="submit" class="btn">Ask</button></form>'
        '<p id="asst-hint" class="muted">Answers are retrieved from indexed records only. '
        'Nothing you type is stored or sent to any server. <a href="#asst-about">How this works</a>.</p>'
        '<div class="asst-examples"><span class="muted">Try:</span> '
        '<button type="button" class="chip asst-example" data-q="What are Haithem Afli\'s main research areas?">What are the main research areas?</button>'
        '<button type="button" class="chip asst-example" data-q="Which projects relate to multilingual AI?">Which projects relate to multilingual AI?</button>'
        '<button type="button" class="chip asst-example" data-q="What PhD topics are currently available?">What PhD topics are available?</button>'
        '<button type="button" class="chip asst-example" data-q="Which publications should I read first?">Which publications should I read first?</button></div>'
        '<div id="asst-out" class="asst-out" role="region" aria-live="polite" aria-atomic="false"></div>'
        '<div id="asst-graph" class="asst-graph" hidden><h2>Related records</h2>'
        '<ul id="asst-graph-list" class="pubs"></ul></div>'
        '</section>'
        '<section id="asst-about" class="asst-about"><h2>How Ask Me works</h2>'
        '<p>Ask Me is a <strong>Human-Centred AI</strong> feature designed for trust rather than fluency. '
        'It runs entirely in your browser using a retrieval index built from this site\'s verified data '
        '(publications, projects, talks, supervision and pages). It does not use a generative language model, '
        'so it cannot fabricate, paraphrase incorrectly, or hallucinate. Every answer is a set of real records, '
        'each with a link to its authoritative source and a retrieval confidence score you can inspect.</p>'
        '<h3>What it does</h3><ul class="pubs">'
        '<li><strong>Grounded retrieval.</strong> It ranks indexed records against your question and returns the closest matches, with citations.</li>'
        '<li><strong>Cross-language.</strong> A curated glossary maps key terms in several languages to the same research themes, so a question in Arabic, French or Irish reaches the same records as English.</li>'
        '<li><strong>Explainable.</strong> Each result shows <em>why</em> it was returned (matched terms), its confidence, and when the record was last built.</li>'
        '<li><strong>Honest.</strong> If nothing is confidently relevant, it says so and points you to the right section, rather than guessing.</li>'
        '<li><strong>Private.</strong> No tracking, no cookies, no server calls. Your question stays in your browser for the session only.</li></ul>'
        '<p class="muted">For the design rationale and limitations, see the '
        '<a href="https://github.com/HAfli/haithem-afli-academic-website/blob/main/docs/research-assistant.md">research-assistant documentation</a>. '
        'For anything beyond these records, please <a href="contact.html">get in touch</a>.</p></section>'
        '<script src="assistant.js" defer></script>')
    pages["assistant"] = page("assistant","Ask Me About My Research", assistant_body,
        "Ask Me — a grounded, citation-first way to explore Dr Haithem Afli's research. It answers only from verified records, shows its sources and confidence, and never fabricates.",
        person_ld)

    # PUBLICATION SPOTLIGHTS — only for human-APPROVED communication assets (none published until approved)
    for pid, a in comm.get("assets", {}).items():
        sp = a.get("spotlight") or {}
        pl = a.get("plain_language") or {}
        if sp.get("status") != "approved" and pl.get("status") != "approved":
            continue  # never auto-publish drafts
        pub = next((p for p in pubs["publications"] if p.get("id")==pid), None)
        if not pub: continue
        slug = "spotlight-" + re.sub(r'[^a-z0-9]+','-', pid.lower()).strip('-')
        parts = [f'<p class="lede">{esc(pub["title"])}</p>',
                 f'<p class="muted">{esc(", ".join(pub["authors"]))} — {esc(pub["venue"])}, {pub["year"]}. '
                 f'{link(pub.get("url"),"Read the paper") if pub.get("url") else ""}</p>']
        if pl.get("status")=="approved":
            parts.append(f'<h2>Plain-language summary</h2><p>{esc(pl["text"])}</p>'
                         '<p class="muted">A plain-language summary for non-specialists; the paper is the authoritative source.</p>')
        if sp.get("status")=="approved":
            if sp.get("key_contributions"):
                parts.append('<h2>Key contributions</h2><ul class="pubs">'+"".join(f'<li>{esc(x)}</li>' for x in sp["key_contributions"])+'</ul>')
            if sp.get("impact"): parts.append(f'<h2>Impact</h2><p>{esc(sp["impact"])}</p>')
        pages[slug] = page(slug, "Spotlight — "+pub["title"][:60], "".join(parts),
            f'Research spotlight: {pub["title"]}.', person_ld)

    # CV
    pages["cv"] = page("cv","Curriculum Vitae",
        '<p class="lede">A full curriculum vitae is summarised across this site.</p>'
        '<h2>Current appointments and research leadership</h2><ul class="pubs">'
        '<li>Lecturer in Artificial Intelligence, Munster Technological University</li>'
        '<li>Institutional Co-Lead, Rinn Artificial Intelligence at MTU</li>'
        '<li>Deputy Theme Lead, Inclusive Language Model &amp; Translation Methods (Rinn AI)</li>'
        '<li>Principal Investigator, Rinn Artificial Intelligence</li>'
        '<li>Principal Investigator and MTU Lead, ADAPT Centre</li>'
        '<li>Founder and Lead, Human-Centred AI Research Group</li>'
        '<li>Chair, Computer Science Postgraduate Research Board</li>'
        '<li>Elected Member, MTU Academic Council</li></ul>'
        '<h2>Research centres</h2><ul class="pubs">'
        '<li>Rinn Artificial Intelligence (Research Ireland) — Institutional Co-Lead at MTU, Deputy Theme Lead, PI</li>'
        '<li>ADAPT Centre (Research Ireland) — PI and MTU Lead</li>'
        '<li>Human-Centred AI Research Group (MTU) — Founder and Lead</li></ul>'
        + (f'<p><a class="btn" href="downloads/Haithem_Afli_CV.pdf">Download CV — PDF</a></p>'
           f'<p class="muted">Generated from the current website record on {esc(BUILD_DATE)}.</p>'
           if (ROOT/"downloads/Haithem_Afli_CV.pdf").exists() else
           '<p>A complete academic CV is available upon request.</p>') +
        '<p>Key sections: <a href="about.html">biography</a>, <a href="rinn-ai.html">Rinn AI</a>, '
        '<a href="publications.html">publications</a>, <a href="projects.html">projects and funding</a>, '
        '<a href="supervision.html">supervision</a>, <a href="service.html">leadership and service</a>.</p>',
        "Curriculum vitae of Dr Haithem Afli, including current Rinn AI and ADAPT research leadership.", person_ld)

    # CONTACT
    pages["contact"] = page("contact","Contact",
        f"""<p class="lede">For research collaboration, supervision enquiries, invited talks and media requests.</p>
<p><strong>Email:</strong> {email_component(profile)}</p>
<p><strong>Affiliation:</strong> {esc(profile["affiliation"])}</p>
<h2>Profiles and links</h2><ul class="ids">{profile_links_html(profile)}<li>{link("https://github.com/HAfli","GitHub")}</li></ul>
<p class="note">Only professional contact information is published here.</p>""",
        "Contact details for Dr Haithem Afli, MTU.", person_ld)

    return pages

# ---------- feed + sitemap + robots ----------
def feed_link(url):
    return f'<link href="{esc(url)}"/>' if valid_url(url) else ""

def feed(news):
    entries = ""
    for n in news["items"]:
        d = n["date"] if len(n["date"])==10 else n["date"]+"-01"
        entries += (f'<entry><title>{esc(n["headline"])}</title>'
                    f'<id>{esc(BASE_URL)}/news.html#{esc(d)}</id>'
                    f'<updated>{esc(d)}T00:00:00Z</updated>'
                    f'<summary>{esc(n["summary"])}</summary>'
                    f'{feed_link(n.get("link",""))}</entry>')
    return (f'<?xml version="1.0" encoding="utf-8"?>\n<feed xmlns="http://www.w3.org/2005/Atom">'
            f'<title>Dr Haithem Afli — News</title><id>{esc(BASE_URL)}/feed.xml</id>'
            f'<updated>{BUILD_DATE}T00:00:00Z</updated><link href="{esc(BASE_URL)}/feed.xml" rel="self"/>{entries}</feed>')

def sitemap(slugs):
    urls = "".join(f'<url><loc>{esc(BASE_URL)}/{"index.html" if s=="index" else s+".html"}</loc>'
                   f'<lastmod>{BUILD_DATE}</lastmod></url>' for s in slugs)
    return f'<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>'

CSS = """:root{--ink:#1a1a1a;--muted:#5a5f66;--line:#e2e5ea;--accent:#0b5c8a;--bg:#fff;--tag:#eef2f6;--surface:#fff;--accent-soft:#dfe7ef;color-scheme:light dark}
@media(prefers-color-scheme:dark){:root{--ink:#e8eaed;--muted:#9aa2ab;--line:#2b3138;--accent:#6cb6e6;--bg:#14171a;--tag:#1e242b;--surface:#1b2027;--accent-soft:#233240}}
*{box-sizing:border-box}html{font-size:17px}
body{margin:0;font-family:-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.6}
.skip{position:absolute;left:-999px}.skip:focus{left:8px;top:8px;background:#fff;padding:8px;z-index:10;border:2px solid var(--accent)}
header.site,footer.site{padding:1rem 1.25rem;border-bottom:1px solid var(--line)}
footer.site{border-top:1px solid var(--line);border-bottom:0;color:var(--muted);font-size:.9rem;margin-top:3rem}
.brand a{font-weight:700;color:var(--ink);text-decoration:none;font-size:1.15rem}
.brand span{display:block;color:var(--muted);font-size:.85rem}
header.site nav{margin-top:.6rem;display:flex;flex-wrap:wrap;gap:.15rem 1rem}
header.site nav a{color:var(--accent);text-decoration:none;font-size:.92rem}
header.site nav a[aria-current]{color:var(--ink);font-weight:600;text-decoration:underline}
main{max-width:52rem;margin:0 auto;padding:1.5rem 1.25rem}
h1{font-size:1.9rem;line-height:1.2;margin:.2rem 0 1rem}h2{font-size:1.3rem;margin:2rem 0 .6rem;border-bottom:1px solid var(--line);padding-bottom:.3rem}
h3{font-size:1.05rem;margin:1.4rem 0 .4rem;color:var(--muted)}
a{color:var(--accent)}.lede{font-size:1.12rem}.muted{color:var(--muted)}
.note{background:var(--tag);padding:.6rem .8rem;border-radius:6px;font-size:.9rem;color:var(--muted)}
ul.themes{columns:2;list-style:none;padding:0}ul.themes li{margin:.3rem 0}
ul.pubs,ul.news,ul.ids{list-style:none;padding:0}ul.pubs>li,ul.news>li{padding:.5rem 0;border-bottom:1px solid var(--line)}
.pub-t{font-weight:600}.pub-m{color:var(--muted);font-size:.93rem}
.tag{display:inline-block;background:var(--tag);color:var(--muted);font-size:.72rem;padding:.1rem .5rem;border-radius:10px;margin:.2rem .2rem 0 0}
.filters{display:flex;gap:1rem;flex-wrap:wrap;margin:1rem 0;padding:.6rem;background:var(--tag);border-radius:6px}
.filters select{font-size:.95rem;padding:.2rem}
table{width:100%;border-collapse:collapse;font-size:.92rem;margin:.5rem 0}
th,td{text-align:left;padding:.5rem .4rem;border-bottom:1px solid var(--line);vertical-align:top}
th{color:var(--muted);font-weight:600}
.placeholder-photo{width:140px;height:140px;border:2px dashed var(--line);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:.8rem;text-align:center;float:right;margin:0 0 1rem 1rem}
@media(max-width:520px){ul.themes{columns:1}.placeholder-photo{float:none;margin:0 auto 1rem}}
:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.grid-img{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin:.5rem 0}
.grid-img figure{margin:0}.grid-img img{width:100%;height:auto;border-radius:8px;border:1px solid var(--line)}
.grid-img figcaption{font-size:.82rem;color:var(--muted);margin-top:.3rem}
.news img{max-width:100%;height:auto;border-radius:8px;margin:.5rem 0}
.roles-hero{color:var(--muted);font-size:.98rem}
section.feature{background:var(--tag);border-radius:10px;padding:.8rem 1rem;margin:1.2rem 0}
section.feature h2{border:0;margin:.2rem 0 .4rem}
ol.agenda{padding-left:1.2rem}ol.agenda li{margin:.4rem 0}
.hero{display:flex;gap:1.5rem;align-items:flex-start;flex-wrap:wrap;margin:.5rem 0 1rem}
.hero>div{flex:1;min-width:260px}
figure.portrait{margin:0;flex:0 0 200px}figure.portrait img{width:200px;height:auto;border-radius:12px;border:1px solid var(--line)}
figure.fig{margin:1rem 0}figure.fig img{width:100%;height:auto;border-radius:10px;border:1px solid var(--line)}
figure.fig figcaption,.grid-img figcaption{font-size:.85rem;color:var(--muted);margin-top:.35rem}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:1rem;margin:.5rem 0}
.role-card{border:1px solid var(--line);border-radius:12px;padding:.8rem 1rem;background:var(--surface,#fff)}
.role-card h3{margin:.1rem 0 .3rem;color:var(--ink);font-size:1.02rem}
.role-titles{font-weight:600;margin:.2rem 0}.role-links{font-size:.85rem;margin:.4rem 0 0}
.grid-img figure{margin:0}
@media(max-width:520px){figure.portrait,figure.portrait img{flex-basis:auto;width:100%}}
.btn{display:inline-block;background:var(--accent);color:#fff;padding:.5rem .9rem;border-radius:8px;text-decoration:none;font-weight:600}
.btn:hover{filter:brightness(1.08)}
details.langsel{margin-top:.5rem;font-size:.9rem}details.langsel summary{cursor:pointer;color:var(--accent)}
details.langsel ul{list-style:none;display:flex;flex-wrap:wrap;gap:.2rem .9rem;padding:.4rem 0 0;margin:0}
nav.crumbs{font-size:.85rem;margin:0 0 .6rem}nav.crumbs ol{list-style:none;display:flex;flex-wrap:wrap;gap:.35rem;padding:0;margin:0}
nav.crumbs li:not(:last-child)::after{content:"›";margin-left:.35rem;color:var(--muted)}
nav.crumbs li[aria-current]{color:var(--muted)}
.chips{display:flex;flex-wrap:wrap;gap:.5rem;margin:.5rem 0}
.theme-chip{display:inline-block;background:var(--tag);color:var(--accent);padding:.35rem .75rem;border-radius:20px;text-decoration:none;font-size:.9rem}
.theme-chip:hover{background:#dfe7ef}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);border:0}
.asst{border:1px solid var(--line);border-radius:12px;padding:1rem;margin:1rem 0;background:var(--surface,#fff)}
.asst-intents{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin-bottom:.7rem}
.chip{background:var(--tag);color:var(--accent);border:1px solid var(--line);padding:.3rem .7rem;border-radius:20px;font-size:.88rem;cursor:pointer}
.chip:hover,.chip[aria-pressed="true"]{background:var(--accent);color:#fff}
.asst-controls{display:flex;flex-wrap:wrap;gap:1rem;align-items:center;margin:.4rem 0;font-size:.9rem}
.asst-controls select{padding:.2rem;font-size:.9rem}
.asst-form{display:flex;gap:.5rem;margin:.5rem 0}
.asst-form input[type=text]{flex:1;padding:.55rem .7rem;border:1px solid var(--line);border-radius:8px;font-size:1rem}
.asst-out{margin-top:.8rem}
.asst-answer{border-left:3px solid var(--accent);padding:.2rem 0 .2rem .8rem;margin:.6rem 0}
.asst-answer.none{border-left-color:var(--muted)}
.asst-conf{font-size:.8rem;color:var(--muted)}
.asst-why{font-size:.85rem;color:var(--muted);margin:.2rem 0}
.asst-why .mt{background:var(--tag);border-radius:4px;padding:0 .3rem;margin-right:.2rem}
.asst-score{font-variant-numeric:tabular-nums}
.asst-meta{font-size:.78rem;color:var(--muted);margin-top:.5rem}
details.asst-detail>summary{cursor:pointer;color:var(--accent);font-size:.85rem}
[dir=rtl] .asst-answer{border-left:0;border-right:3px solid var(--accent);padding:.2rem .8rem .2rem 0}
[dir=rtl] .asst-why .mt{margin-right:0;margin-left:.2rem}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
a.tag{text-decoration:none}a.tag:hover{background:#dfe7ef}
.pub-abs{margin:.35rem 0}.pub-abs summary{cursor:pointer;color:var(--accent);font-size:.88rem}
.pub-abs p{font-size:.92rem;color:var(--ink);margin:.4rem 0}
pre.bibtex{background:var(--tag);padding:.6rem;border-radius:6px;overflow-x:auto;font-size:.8rem;white-space:pre-wrap}
.pub-rel{font-size:.82rem;margin-top:.25rem}
.theme-browse{font-size:.9rem;margin:.3rem 0 0}
.email{display:inline-flex;align-items:center;gap:.5rem;flex-wrap:wrap}
.email .email-addr{text-decoration:none;font-weight:600}
.email .email-copy{font-size:.8rem;padding:.15rem .55rem;border:1px solid var(--line);border-radius:6px;background:var(--tag);color:var(--accent);cursor:pointer}
.email .email-copy:hover{background:#dfe7ef}
.email .email-status{font-size:.8rem;color:var(--muted)}
footer.site .footer-links{display:flex;flex-wrap:wrap;gap:1.5rem;margin:0 0 .8rem}
footer.site .footer-links div{display:flex;flex-direction:column;gap:.15rem}
footer.site .footer-h{font-size:.75rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}
footer.site .footer-links a{font-size:.9rem}
footer.site .footer-meta{font-size:.85rem;margin:0}
.pub-summary{font-size:1rem;margin:.3rem 0 .8rem}
.filters label{display:inline-flex;flex-direction:column;font-size:.8rem;color:var(--muted);gap:.15rem}
.filters input[type=search]{font-size:.95rem;padding:.3rem .5rem;border:1px solid var(--line);border-radius:6px;min-width:14rem}
.result-count{align-self:flex-end;font-size:.9rem;color:var(--muted);font-weight:600}
.pubcat{margin:1.5rem 0}
.ptype{display:inline-block;font-size:.68rem;text-transform:uppercase;letter-spacing:.03em;color:var(--muted);border:1px solid var(--line);border-radius:4px;padding:0 .35rem;vertical-align:middle;margin-left:.3rem}
.show-more{margin:.6rem 0 0;background:var(--tag);color:var(--accent);border:1px solid var(--line);border-radius:8px;padding:.4rem .9rem;font-weight:600;cursor:pointer}
.show-more:hover{background:#dfe7ef}
.media-card{border:1px solid var(--line);border-radius:12px;padding:.9rem 1rem;background:var(--surface,#fff)}
.media-card h3{margin:.1rem 0 .5rem;color:var(--ink);font-size:1.02rem}
.media-card video,.media-card audio{width:100%;border-radius:8px}
.media-card figure{margin:0 0 .5rem}
.pub-ga{margin:.4rem 0}.pub-ga img{max-width:220px;height:auto;border:1px solid var(--line);border-radius:8px}
/* Release 2.0 design-system polish (dark-mode aware; reduced-motion respected) */
.skip:focus{background:var(--surface)}
section.feature{background:var(--tag)}
.role-card,.media-card{transition:box-shadow .18s ease,transform .18s ease,border-color .18s ease}
@media(prefers-reduced-motion:no-preference){.role-card:hover,.media-card:hover{box-shadow:0 6px 20px rgba(0,0,0,.08);transform:translateY(-2px);border-color:var(--accent-soft)}}
.theme-chip:hover,a.tag:hover,.chip:hover{background:var(--accent-soft)}
.hero{align-items:center}
main{max-width:54rem}
h2{letter-spacing:-.01em}
.lede{color:var(--ink)}
.cards{gap:1rem}
.audience-cta{display:flex;flex-wrap:wrap;gap:.6rem;margin:1rem 0}
.audience-cta a{display:inline-block;background:var(--tag);border:1px solid var(--line);border-radius:10px;padding:.55rem .9rem;text-decoration:none;color:var(--accent);font-weight:600}
.audience-cta a:hover{background:var(--accent-soft)}
.summary-card{border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:10px;padding:.9rem 1.1rem;margin:1rem 0;background:var(--surface)}
.summary-card h3{margin:.1rem 0 .5rem}
.summary-grid{display:grid;grid-template-columns:120px 1fr;gap:.3rem .8rem;font-size:.94rem}
.summary-grid dt{font-weight:600;color:var(--muted)}
.summary-grid dd{margin:0}
.theme-hero{background:var(--tag);border-radius:12px;padding:1rem 1.2rem;margin:.4rem 0 1rem}
@media(max-width:640px){header.site nav{gap:.1rem .7rem;font-size:.9rem}main{padding:1.1rem 1rem}.summary-grid{grid-template-columns:1fr}}
.filter-chips{display:flex;flex-wrap:wrap;gap:.4rem;margin:.6rem 0}
.filter-chips button{background:var(--tag);border:1px solid var(--line);border-radius:16px;padding:.25rem .7rem;font-size:.85rem;color:var(--accent);cursor:pointer}
.filter-chips button[aria-pressed="true"]{background:var(--accent);color:#fff}
/* Release 2.1 grouped navigation */
header.site nav[aria-label="Primary"]{display:flex;flex-wrap:wrap;gap:.2rem 1.1rem;align-items:flex-start}
a.navtop{color:var(--accent);text-decoration:none;font-size:.94rem;padding:.1rem 0}
a.navtop[aria-current]{color:var(--ink);font-weight:600;text-decoration:underline}
.navgroup{position:relative}
.navgroup>summary{cursor:pointer;list-style:none;color:var(--accent);font-size:.94rem;padding:.1rem 0}
.navgroup>summary::-webkit-details-marker{display:none}
.navgroup>summary::after{content:"\\25be";font-size:.7rem;margin-left:.2rem;color:var(--muted)}
.navgroup>summary.cur{color:var(--ink);font-weight:600}
.navmenu{position:absolute;z-index:30;top:1.7rem;left:0;background:var(--surface);border:1px solid var(--line);border-radius:10px;padding:.4rem;margin:0;min-width:13rem;list-style:none;box-shadow:0 8px 24px rgba(0,0,0,.12)}
.navmenu li{margin:0;border:0;padding:0}
.navmenu a{display:block;padding:.4rem .55rem;border-radius:7px;text-decoration:none;color:var(--accent);font-size:.9rem}
.navmenu a:hover,.navmenu a[aria-current]{background:var(--tag);color:var(--ink)}
@media(max-width:640px){.navgroup{width:100%}.navmenu{position:static;box-shadow:none;border:0;padding:.1rem 0 .3rem .9rem;min-width:0}}
.theme-group{border:0;padding:0;margin:1.8rem 0 .4rem;font-size:1.05rem;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.asst-examples{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:.5rem 0}
.tl-item .tag{margin-right:.15rem}.tl-item .tl-year{color:var(--muted);font-variant-numeric:tabular-nums;margin-right:.2rem}
li.tl-item{padding:.6rem 0}"""

PUBS_JS = r"""(function(){
var q=document.getElementById('p-q'),y=document.getElementById('p-year'),
t=document.getElementById('p-type'),count=document.getElementById('p-count');
var PAGE=12,STEP=20;
var secs=[].slice.call(document.querySelectorAll('.pubcat'));
secs.forEach(function(s){s._page=PAGE;var b=s.querySelector('.show-more');
 if(b)b.addEventListener('click',function(){s._page+=STEP;apply();});});
function apply(){
 var qs=(q&&q.value||'').trim().toLowerCase(),yv=y&&y.value||'',tv=t&&t.value||'';
 var filtering=!!(qs||yv||tv),total=0;
 secs.forEach(function(s){
  var lis=[].slice.call(s.querySelectorAll('.pub')),m=0,shown=0;
  lis.forEach(function(li){
   var ok=(!yv||li.dataset.year===yv)&&(!tv||li.dataset.type===tv)&&(!qs||(li.dataset.search||'').indexOf(qs)>=0);
   if(ok){m++;
    if(filtering){li.style.display='';}
    else{shown++;li.style.display=(shown<=s._page)?'':'none';}
   } else {li.style.display='none';}
  });
  total+=m;
  s.style.display=m?'':'none';
  var badge=s.querySelector('.cat-count');if(badge)badge.textContent='('+m+')';
  var b=s.querySelector('.show-more');
  if(b){var more=(!filtering&&m>s._page);b.hidden=!more;
   if(more)b.textContent='Show '+Math.min(STEP,m-s._page)+' more';}
 });
 if(count)count.textContent=total+' result'+(total!==1?'s':'');
}
[q,y,t].forEach(function(el){if(el)el.addEventListener(el.tagName==='SELECT'?'change':'input',apply);});
apply();
})();"""

NEWS_JS = """(function(){var c=document.getElementById('n-cat'),h=document.getElementById('n-theme');
function f(){var cv=c?c.value:'',hv=h?h.value:'';document.querySelectorAll('.news>li').forEach(function(li){
var ok=(!cv||li.dataset.cat===cv)&&(!hv||(' '+li.dataset.themes+' ').indexOf(' '+hv+' ')>=0);
li.style.display=ok?'':'none';});}
if(c)c.addEventListener('change',f);if(h)h.addEventListener('change',f);})();"""

SUP_JS = """(function(){var s=document.getElementById('f-topic');if(!s)return;
s.addEventListener('change',function(){var v=s.value;
document.querySelectorAll('#masters li').forEach(function(li){
var ok=!v||(' '+li.dataset.topics+' ').indexOf(' '+v+' ')>=0;li.style.display=ok?'':'none';});
document.querySelectorAll('#masters h3').forEach(function(h){var n=h.nextElementSibling;
var any=n&&Array.from(n.children).some(function(li){return li.style.display!=='none';});h.style.display=any?'':'none';});});})();"""

# Accessible photo-gallery category filter (keyboard-operable native select; live count).
GALLERY_JS = r"""(function(){
var sel=document.getElementById('g-cat'),count=document.getElementById('g-count'),
grid=document.getElementById('gallery-grid');
if(!grid)return;
var figs=[].slice.call(grid.querySelectorAll('figure'));
function apply(){var v=sel&&sel.value||'',n=0;
 figs.forEach(function(f){var ok=!v||f.getAttribute('data-cat')===v;f.style.display=ok?'':'none';if(ok)n++;});
 if(count)count.textContent=n+' photograph'+(n!==1?'s':'');}
if(sel)sel.addEventListener('change',apply);apply();
})();"""

# Timeline filter chips (accessible; hides empty year groups; live count).
TIMELINE_JS = r"""(function(){
var chips=document.querySelectorAll('.filter-chips button'),count=document.getElementById('tl-count'),
list=document.getElementById('tl-list');
if(!list)return;
function apply(f){var n=0;
 list.querySelectorAll('li[data-f]').forEach(function(li){var ok=!f||li.getAttribute('data-f')===f;li.style.display=ok?'':'none';if(ok)n++;});
 list.querySelectorAll('.tl-year').forEach(function(h){var ul=h.nextElementSibling;
  var any=ul&&Array.prototype.some.call(ul.children,function(li){return li.style.display!=='none';});
  h.style.display=any?'':'none';if(ul)ul.style.display=any?'':'none';});
 if(count)count.textContent=n+' item'+(n!==1?'s':'');}
chips.forEach(function(b){b.addEventListener('click',function(){
 chips.forEach(function(x){x.setAttribute('aria-pressed','false');});
 b.setAttribute('aria-pressed','true');apply(b.getAttribute('data-f'));});});
apply('');
})();"""

# Bot-resistant email: parts live in data attributes; JS assembles the address only on user action.
EMAIL_JS = r"""(function(){
function addr(el){return el.getAttribute('data-u')+String.fromCharCode(64)+el.getAttribute('data-d');}
document.querySelectorAll('.email').forEach(function(el){
 var a=el.querySelector('[data-mailto]');
 if(a)a.addEventListener('click',function(e){e.preventDefault();window.location.href='mailto:'+addr(el);});
 var b=el.querySelector('.email-copy'),s=el.querySelector('.email-status');
 if(b)b.addEventListener('click',function(){var v=addr(el);
  function done(msg){if(s){s.textContent=' '+msg;}setTimeout(function(){if(s)s.textContent='';},4000);}
  if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(v).then(function(){done('Copied');},function(){done(v);});}
  else{done(v);}});
});
})();"""

# Client-side grounded Research Assistant. Retrieves from site/data/assistant-index.json only.
# No LLM, no network, no storage: it ranks real records and cites them. If nothing is confidently
# relevant it says so. Cross-language via the index glossary. Explainable (matched terms + score).
ASSISTANT_JS = r"""(function(){
var out=document.getElementById('asst-out'),form=document.getElementById('asst-form'),
q=document.getElementById('asst-q'),langSel=document.getElementById('asst-lang'),
bench=document.getElementById('asst-bench'),graphBox=document.getElementById('asst-graph'),
graphList=document.getElementById('asst-graph-list');
if(!form)return;
var IDX=null,curIntent=null;
var STOP={'the':1,'a':1,'an':1,'of':1,'in':1,'on':1,'and':1,'or':1,'to':1,'is':1,'are':1,'what':1,'who':1,
'how':1,'for':1,'with':1,'about':1,'do':1,'does':1,'your':1,'you':1,'i':1,'am':1,'me':1,'my':1,'que':1,'la':1,
'le':1,'les':1,'des':1,'el':1,'los':1,'der':1,'die':1,'das':1};
var INTENTS={
 phd:{q:'PhD supervision multilingual trustworthy human-centred research topics',
   note:'Prospective PhD students: supervision record, themes and how to apply.',
   links:[['supervision.html','Supervision & mentoring'],['research.html','Research themes'],['contact.html','Contact']]},
 industry:{q:'projects funding translation evaluation health industry collaboration patent',
   note:'Industry partners: applied projects, the patent, and collaboration routes.',
   links:[['projects.html','Projects & funding'],['innovation.html','Innovation & industry'],['contact.html','Contact']]},
 journalist:{q:'Rinn Artificial Intelligence leadership keynotes news impact',
   note:'Journalists: verified roles, a factual media overview and news.',
   links:[['showcase.html','Research showcase'],['news.html','News'],['rinn-ai.html','Rinn AI'],['contact.html','Contact']]},
 msc:{q:'teaching modules MSc masters supervision artificial intelligence',
   note:'Prospective MSc students: teaching, modules and MSc supervision.',
   links:[['teaching.html','Teaching'],['supervision.html','Supervision'],['contact.html','Contact']]},
 collab:{q:'publications research themes multilingual evaluation trustworthy collaboration',
   note:'Academic collaborators: research agenda, publications and themes.',
   links:[['research.html','Research'],['publications.html','Publications'],['collections.html','Collections'],['contact.html','Contact']]}};
function esc(s){return String(s).replace(/[&<>"]/g,function(c){return{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function tokens(s){return String(s||'').toLowerCase().replace(/[^\p{L}\p{N}\s]/gu,' ').split(/\s+/).filter(function(t){return t&&!STOP[t];});}
function detectLang(s){ // very small heuristic; only to pick a glossary, never to translate
 if(/[؀-ۿ]/.test(s))return /[پچگیک]/.test(s)?'fa':'ar';
 if(/[֐-׿]/.test(s))return 'he';
 if(/[Ѐ-ӿ]/.test(s))return 'ru';
 return 'en';}
function expand(toks,lang){ // map query terms via glossary to canonical theme keys (cross-language)
 var g=IDX.glossary||{},hits=[],extra=[];
 var maps=[g[lang]||{},g.en||{}];
 var raw=toks.join(' ');
 maps.forEach(function(m){for(var k in m){if(raw.indexOf(k)>=0){extra.push(m[k]);var nm=(IDX.theme_names||{})[m[k]];if(nm)extra=extra.concat(tokens(nm));}}});
 return {toks:toks.concat(extra),themeHits:extra};}
function score(docToks,queryToks){var set={},n=0;docToks.forEach(function(t){set[t]=(set[t]||0)+1;});
 var matched=[];queryToks.forEach(function(t){if(set[t]){n+=1;if(matched.indexOf(t)<0)matched.push(t);}
  else{for(var d in set){if(d.length>3&&(d.indexOf(t)===0||t.indexOf(d)===0)){n+=0.5;if(matched.indexOf(t)<0)matched.push(t);break;}}}});
 return {n:n,matched:matched};}
function typeLabel(t){return{publication:'Publication',project:'Project',talk:'Talk',supervision:'Supervision',page:'Section'}[t]||t;}
function render(query,lang){
 out.innerHTML='';graphBox.hidden=true;graphList.innerHTML='';
 if(!IDX){out.innerHTML='<p class="note">The knowledge index is still loading. Please try again in a moment.</p>';return;}
 var base=tokens(query),ex=expand(base,lang),qt=ex.toks;
 if(!qt.length){out.innerHTML='<p class="note">Please enter a question or pick one of the buttons above.</p>';return;}
 var ranked=IDX.docs.map(function(d){var s=score(tokens(d.text),qt);return{d:d,s:s.n,matched:s.matched};})
   .filter(function(r){return r.s>0;}).sort(function(a,b){return b.s-a.s;});
 var max=ranked.length?ranked[0].s:0;
 var showBench=bench&&bench.checked;
 if(!ranked.length||max<1){
  out.innerHTML='<div class="asst-answer none"><p><strong>I don’t have a confident answer to that from the verified records on this site.</strong> '
   +'I only answer from indexed publications, projects, talks, supervision and pages, and I won’t guess.</p>'
   +'<p class="asst-why">You may find it here: <a href="publications.html">publications</a>, '
   +'<a href="research.html">research themes</a>, <a href="projects.html">projects</a>, or please '
   +'<a href="contact.html">contact Dr Afli</a> directly.</p></div>';
  return;}
 var top=ranked.slice(0,6);
 var head='<p class="asst-meta">Retrieved '+top.length+' record'+(top.length>1?'s':'')+' from the verified index'
   +(ex.themeHits.length?' · matched theme'+(ex.themeHits.length>1?'s':'')+': '+esc(ex.themeHits.filter(function(v,i,a){return a.indexOf(v)===i;}).map(function(k){return (IDX.theme_names||{})[k]||k;}).join(', ')):'')
   +' · index built '+esc(IDX.generated)+'</p>';
 var html=top.map(function(r){var d=r.d,conf=Math.round(r.s/max*100);
  var confWord=conf>=75?'high':conf>=45?'moderate':'low';
  var terms=r.matched.slice(0,6).map(function(t){return '<span class="mt">'+esc(t)+'</span>';}).join('');
  var yr=d.year?(' · '+d.year):'';
  return '<div class="asst-answer"><div><a href="'+esc(d.url)+'"><strong>'+esc(d.title)+'</strong></a> '
   +'<span class="asst-conf">— '+esc(typeLabel(d.type))+yr+'</span></div>'
   +'<div class="asst-why">Why this: matched '+terms+' · confidence '+confWord
   +(showBench?' <span class="asst-score">(score '+r.s.toFixed(1)+' / '+conf+'%)</span>':'')+'</div></div>';
 }).join('');
 out.innerHTML=head+html
  +'<details class="asst-detail"><summary>Why these answers?</summary>'
  +'<p class="asst-why">Each record was ranked by how many of your query terms (after cross-language '
  +'glossary expansion) appear in its indexed text. Records are real entries from this site; each links to its '
  +'authoritative source. Confidence is relative to the best match for this query. Nothing was generated or paraphrased.</p></details>';
 // knowledge-graph style related records (same themes as the top hit)
 var themes=(top[0].d.themes)||[];
 if(themes.length){var rel=IDX.docs.filter(function(d){return d!==top[0].d&&(d.themes||[]).some(function(t){return themes.indexOf(t)>=0;});}).slice(0,6);
  if(rel.length){graphList.innerHTML=rel.map(function(d){return '<li><a href="'+esc(d.url)+'">'+esc(d.title)+'</a> <span class="muted">— '+esc(typeLabel(d.type))+'</span></li>';}).join('');graphBox.hidden=false;}}
}
function run(query){var lang=langSel&&langSel.value!=='auto'?langSel.value:detectLang(query);render(query,lang);}
form.addEventListener('submit',function(e){e.preventDefault();run(q.value);});
document.querySelectorAll('.chip').forEach(function(b){b.addEventListener('click',function(){
 var it=INTENTS[b.dataset.intent];if(!it)return;curIntent=b.dataset.intent;
 document.querySelectorAll('.chip').forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false');});
 q.value=q.value||'';var lang=langSel&&langSel.value!=='auto'?langSel.value:'en';render(it.q,lang);
 out.insertAdjacentHTML('afterbegin','<p class="note">'+esc(it.note)+' Quick links: '
  +it.links.map(function(l){return '<a href="'+l[0]+'">'+esc(l[1])+'</a>';}).join(' · ')+'</p>');
}); });
document.querySelectorAll('.asst-example').forEach(function(b){b.addEventListener('click',function(){
 q.value=b.getAttribute('data-q');run(q.value);
});});
fetch('data/assistant-index.json').then(function(r){return r.json();}).then(function(j){IDX=j;})
 .catch(function(){out.innerHTML='<p class="note">The assistant index could not be loaded. You can browse '
  +'<a href="publications.html">publications</a> and <a href="research.html">research</a> directly.</p>';});
})();"""

import shutil, time, datetime as _dt

# static asset source dirs to publish into site/ (originals in assets/source are deliberately excluded)
ASSET_DIRS = ["assets/img", "assets/downloads", "downloads"]

def publish_assets(verbose=False):
    """Mirror every static asset dir into site/: create dirs, overwrite files,
    and prune stale files no longer in source. Best-effort prune so the build still
    runs on filesystems that disallow deletion (it warns instead of failing)."""
    copied = []
    for rel in ASSET_DIRS:
        src = ROOT / rel
        if not src.exists():
            continue
        dst = OUT / rel
        dst.mkdir(parents=True, exist_ok=True)
        src_rel = set()
        for f in src.rglob("*"):
            if not f.is_file():
                continue
            r = f.relative_to(src)
            if r.as_posix().startswith("media-kits/"):
                continue  # media kits are review-gated (reports/media-kits), never auto-published
            src_rel.add(r.as_posix())
            out = dst / r
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(f, out)          # overwrite in place
            copied.append((dst/r).relative_to(OUT).as_posix())
            if verbose:
                print(f"  copy {(dst/r).relative_to(OUT).as_posix()}")
        # prune stale
        for f in list(dst.rglob("*")):
            if f.is_file() and f.relative_to(dst).as_posix() not in src_rel:
                try:
                    f.unlink()
                    if verbose: print(f"  prune {f.relative_to(OUT).as_posix()}")
                except OSError:
                    warnings.append(f"could not prune stale asset {f.relative_to(OUT).as_posix()} (filesystem read-only)")
    return copied

LOCAL_REF_RE = re.compile(r'(?:src|href)="([^"]+)"')
SRCSET_RE = re.compile(r'srcset="([^"]+)"')

def is_local(ref):
    return not (ref.startswith(("http://","https://","//","mailto:","#","data:")) or ref == "")

def collect_refs(html):
    """Return (local_refs, rootrel_refs) from one HTML string."""
    refs, rootrel = set(), set()
    for m in LOCAL_REF_RE.findall(html):
        r = m.split("#")[0]
        if not is_local(r):
            continue
        if r.startswith("/"):
            rootrel.add(r)          # would break under the /repo/ Pages prefix
        else:
            refs.add(r)
    for ss in SRCSET_RE.findall(html):
        for part in ss.split(","):
            url = part.strip().split(" ")[0]
            if is_local(url):
                (rootrel if url.startswith("/") else refs).add(url.split("#")[0])
    return refs, rootrel

def validate_site(pages, verbose=False):
    """Check every referenced local asset exists in site/, no root-relative paths,
    no broken internal page links. Returns (errors, refmap)."""
    errors = []
    present = {p.relative_to(OUT).as_posix() for p in OUT.rglob("*") if p.is_file()}
    refmap = {}
    for slug in pages:
        fn = ("index" if slug=="index" else slug) + ".html"
        html = (OUT/fn).read_text(encoding="utf-8")
        refs, rootrel = collect_refs(html)
        refmap[fn] = refs
        for r in sorted(rootrel):
            errors.append(f"{fn}: root-relative path '{r}' will break under the GitHub Pages repo prefix")
        for r in sorted(refs):
            target = r
            if target not in present:
                errors.append(f"{fn}: missing asset -> {r}")
            elif verbose:
                print(f"  ok   {fn} -> {r}")
    return errors, refmap

def derivative_report(gallery):
    """Confirm every referenced image derivative exists; return inventory rows."""
    inv, missing = [], []
    for im in gallery.get("images", []):
        base = im["id"]
        variants = []
        for name in ("thumb","medium","large"):
            for ext in ("webp","jpg"):
                rel = f"assets/img/{base}-{name}.{ext}"
                exists = (OUT/rel).exists()
                variants.append((rel, exists))
                if not exists:
                    missing.append(rel)
        size = 0
        srcp = OUT/(im.get("src","").replace("assets/","assets/")) if im.get("src") else None
        if srcp and srcp.exists(): size = srcp.stat().st_size
        inv.append({"id":base,"src":im.get("src"),"w":im.get("w"),"h":im.get("h"),
                    "bytes":size,"derivatives":[v[0] for v in variants],
                    "referenced":True,"in_srcset":bool(im.get("srcset"))})
    return inv, missing

def write_reports(pages, copied, inv, errors, refmap, duration):
    imgs = [f for f in copied if re.search(r'\.(jpg|jpeg|png|webp|gif|svg)$', f, re.I)]
    counts = {ext: len([f for f in copied if f.lower().endswith("."+ext)]) for ext in ("jpg","webp","png","svg","pdf","css","js")}
    total_size = sum((p.stat().st_size for p in OUT.rglob("*") if p.is_file()))
    ext_links = sorted({m for slug in pages for m in re.findall(r'href="(https?://[^"]+)"', (OUT/(("index" if slug=="index" else slug)+".html")).read_text(encoding="utf-8"))})
    report = {
        "build_date": BUILD_DATE, "base_url": BASE_URL, "duration_sec": round(duration,3),
        "pages": sorted(("index" if s=="index" else s)+".html" for s in pages),
        "assets": {"images": len(imgs), "jpg": counts["jpg"], "webp": counts["webp"], "png": counts["png"],
                   "svg": counts["svg"], "pdf": counts["pdf"], "total_files": len(copied)},
        "css_files": len(list(OUT.glob("*.css"))), "js_files": len(list(OUT.glob("*.js"))),
        "image_inventory": inv, "external_links": ext_links,
        "broken_references": errors, "total_site_bytes": total_size,
    }
    (OUT/"build-report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False), encoding="utf-8")
    rows = "".join(f'<tr><td>{esc(i["id"])}</td><td>{esc(i["src"])}</td><td>{i["w"]}×{i["h"]}</td>'
                   f'<td>{i["bytes"]//1024} KB</td><td>{len(i["derivatives"])}</td>'
                   f'<td>{"yes" if i["in_srcset"] else "no"}</td></tr>' for i in inv)
    brk = ("<p><strong>No broken references detected.</strong></p>" if not errors
           else "<ul>"+"".join(f"<li>{esc(e)}</li>" for e in errors)+"</ul>")
    ext = "".join(f'<li>{esc(u)}</li>' for u in ext_links)
    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1"><title>Build report</title>
<style>body{{font-family:system-ui,Arial,sans-serif;max-width:60rem;margin:1.5rem auto;padding:0 1rem;color:#1a1a1a}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}td,th{{border-bottom:1px solid #e2e5ea;padding:.35rem .5rem;text-align:left}}
code{{background:#eef2f6;padding:.1rem .3rem;border-radius:4px}}</style></head><body>
<h1>Build report</h1>
<p>Generated {esc(BUILD_DATE)} · base URL <code>{esc(BASE_URL)}</code> · duration {round(duration,2)}s ·
total site size {total_size//1024} KB.</p>
<h2>Build statistics</h2>
<ul><li>Pages: {len(report["pages"])}</li><li>Static asset files: {len(copied)}</li>
<li>Images: {len(imgs)} (JPEG {counts["jpg"]}, WebP {counts["webp"]}, PNG {counts["png"]}, SVG {counts["svg"]})</li>
<li>CSS files: {report["css_files"]} · JavaScript files: {report["js_files"]} · PDFs: {counts["pdf"]}</li>
<li>Broken references: {len(errors)}</li></ul>
<h2>Generated pages</h2><ul>{"".join(f"<li><code>{esc(p)}</code></li>" for p in report["pages"])}</ul>
<h2>Image inventory</h2><table><tr><th>ID</th><th>src</th><th>dims</th><th>size</th><th>derivatives</th><th>srcset</th></tr>{rows}</table>
<h2>Broken references</h2>{brk}
<h2>External links ({len(ext_links)})</h2><ul>{ext}</ul>
</body></html>"""
    (OUT/"build-report.html").write_text(html, encoding="utf-8")

def _ics(events):
    out = ["BEGIN:VCALENDAR","VERSION:2.0","PRODID:-//HAI MTU//Research Intelligence//EN","CALSCALE:GREGORIAN"]
    for e in events:
        d = e["date"].replace("-","")
        out += ["BEGIN:VEVENT", f"UID:{e['uid']}@hafli.github.io",
                f"DTSTAMP:{BUILD_DATE.replace('-','')}T000000Z", f"DTSTART;VALUE=DATE:{d}",
                f"SUMMARY:{e['summary']}"]
        if e.get("url"): out.append(f"URL:{e['url']}")
        out.append("END:VEVENT")
    out.append("END:VCALENDAR")
    return "\r\n".join(out)+"\r\n"

def build_knowledge_index():
    """Generate a language-neutral knowledge graph + retrieval index into site/data/ from the
    existing verified data. The client-side Research Assistant retrieves from this index only —
    it surfaces real records with citations and cannot invent content. Cross-language querying is
    supported via a theme/keyword glossary (query terms in any language map to language-neutral IDs)."""
    outdir = OUT/"data"; outdir.mkdir(parents=True, exist_ok=True)
    prof = load("profile.json") or {}; pubs = (load("publications.json") or {}).get("publications",[])
    projd = load("projects.json") or {}; talks = (load("talks.json") or {}).get("selected",[])
    sup = load("supervision.json") or {}; rinn = load("rinn.json") or {}
    themes = {t["id"]: t["name"] for t in prof.get("themes",[])}
    nodes, edges, docs = [], [], []
    def node(nid, ntype, label, url=None, extra=None):
        nodes.append({"id":nid,"type":ntype,"label":label,**({"url":url} if url else {}),**(extra or {})})
    # theme nodes
    for tid, tname in themes.items(): node(f"theme:{tid}","theme",tname,url=f"research.html#{tid}")
    # publications
    for p in pubs:
        pid = p.get("id") or ("pub:"+re.sub(r'[^a-z0-9]+','-',p["title"].lower())[:40])
        node(pid,"publication",p["title"],url=p.get("url") or "publications.html",
             extra={"year":p["year"],"venue":p["venue"],"type":p.get("type")})
        for th in p.get("themes",[]):
            if th in themes: edges.append([pid,"in-theme",f"theme:{th}"])
        for a in p["authors"]:
            aid="person:"+re.sub(r'[^a-z0-9]+','-',a.lower())
            if not any(n["id"]==aid for n in nodes): node(aid,"person",a)
            edges.append([pid,"authored-by",aid])
        docs.append({"id":pid,"type":"publication","title":p["title"],
                     "url":p.get("url") or "publications.html","year":p["year"],
                     "themes":[themes.get(t,t) for t in p.get("themes",[])],
                     "text":" ".join([p["title"],p["venue"]," ".join(p["authors"])," ".join(themes.get(t,t) for t in p.get("themes",[]))]).lower()})
    # projects
    for p in projd.get("national_projects",[])+projd.get("eu_projects",[]):
        if "WITHHELD" in p.get("note",""): continue
        prid="project:"+re.sub(r'[^a-z0-9]+','-',(p.get("short_name") or p["name"]).lower())[:40]
        node(prid,"project",p.get("short_name") or p["name"],url=p.get("url") or "projects.html",
             extra={"funder":p.get("funder") or p.get("programme")})
        docs.append({"id":prid,"type":"project","title":p.get("short_name") or p["name"],
                     "url":p.get("url") or "projects.html",
                     "text":" ".join([p.get("name",""),p.get("funder","") or p.get("programme",""),p.get("role","")]).lower()})
    # talks
    for t in talks:
        tid="talk:"+re.sub(r'[^a-z0-9]+','-',t["title"].lower())[:40]
        node(tid,"talk",t["title"],url="talks.html",extra={"event":t.get("event"),"year":t.get("year")})
        docs.append({"id":tid,"type":"talk","title":t["title"],"url":"talks.html",
                     "text":" ".join([t["title"],t.get("event",""),str(t.get("year",""))]).lower()})
    # supervision (public completed doctoral)
    for s in sup.get("doctoral_completed",[]):
        sid="student:"+re.sub(r'[^a-z0-9]+','-',s["name"].lower())
        node(sid,"student",s["name"],url="supervision.html",extra={"area":s.get("area")})
        docs.append({"id":sid,"type":"supervision","title":s["name"],"url":"supervision.html",
                     "text":" ".join([s["name"],s.get("area",""),s.get("institution","")]).lower()})
    # career milestones (the narrative backbone) → nodes + retrievable docs
    for m in (load("milestones.json") or {}).get("milestones", []):
        node(m["id"],"milestone",m["title"],url="journey.html#"+str(m.get("chapter","")),
             extra={"year":m.get("year"),"category":m.get("category"),"cis":m.get("cis")})
        r=m.get("refs",{})
        if r.get("theme") in themes: edges.append([m["id"],"in-theme","theme:"+r["theme"]])
        docs.append({"id":m["id"],"type":"milestone","title":m["title"],"url":"journey.html",
                     "themes":[themes.get(r["theme"],r["theme"])] if r.get("theme") else [],
                     "text":" ".join([m["title"],m.get("description",""),m.get("impact",""),str(m.get("year",""))]).lower()})
    # news & media coverage
    for n in (load("news.json") or {}).get("items", []):
        nid="news:"+re.sub(r'[^a-z0-9]+','-',n.get("id",n.get("headline","")).lower())[:40]
        node(nid,"news",n.get("headline",""),url=n.get("link") or "news.html",extra={"date":n.get("date")})
        docs.append({"id":nid,"type":"news","title":n.get("headline",""),"url":n.get("link") or "news.html",
                     "text":" ".join([n.get("headline",""),n.get("summary","")]).lower()})
    # pages
    for slug,label in [("research","Research themes and current agenda"),("rinn-ai","Rinn Artificial Intelligence"),
        ("group","Human-Centred AI Research Group"),("teaching","Teaching and modules"),
        ("supervision","Supervision and mentoring"),("projects","Projects and funding"),
        ("publications","Publications"),("showcase","Research showcase"),("collections","Research collections"),
        ("timeline","Research timeline"),("research-intelligence","Research intelligence"),("cv","Curriculum vitae")]:
        docs.append({"id":"page:"+slug,"type":"page","title":label,"url":slug+".html","text":label.lower()})
    # cross-language theme/keyword glossary → language-neutral theme ids and canonical english terms
    glossary = {
     "en":{"multilingual":"multilingual","arabic":"multilingual","translation":"multilingual","evaluation":"evaluation",
           "benchmark":"evaluation","judge":"evaluation","health":"bio","biology":"bio","genomic":"bio","genomics":"bio",
           "trustworthy":"trustworthy","safety":"trustworthy","fairness":"trustworthy","human":"hcai","cultural":"multilingual"},
     "ar":{"متعدد اللغات":"multilingual","العربية":"multilingual","ترجمة":"multilingual","تقييم":"evaluation","معيار":"evaluation",
           "صحة":"bio","أحياء":"bio","جينوم":"bio","موثوق":"trustworthy","سلامة":"trustworthy","إنسان":"hcai","ثقافي":"multilingual"},
     "fr":{"multilingue":"multilingual","arabe":"multilingual","traduction":"multilingual","évaluation":"evaluation",
           "santé":"bio","biologie":"bio","fiable":"trustworthy","humain":"hcai","culturel":"multilingual"},
     "es":{"multilingüe":"multilingual","árabe":"multilingual","traducción":"multilingual","evaluación":"evaluation",
           "salud":"bio","biología":"bio","confiable":"trustworthy","humano":"hcai","cultural":"multilingual"},
     "de":{"mehrsprachig":"multilingual","arabisch":"multilingual","übersetzung":"multilingual","bewertung":"evaluation",
           "gesundheit":"bio","biologie":"bio","vertrauenswürdig":"trustworthy","mensch":"hcai"},
     "it":{"multilingue":"multilingual","arabo":"multilingual","traduzione":"multilingual","valutazione":"evaluation",
           "salute":"bio","biologia":"bio","affidabile":"trustworthy","umano":"hcai"},
     "tr":{"çok dilli":"multilingual","arapça":"multilingual","çeviri":"multilingual","değerlendirme":"evaluation",
           "sağlık":"bio","biyoloji":"bio","güvenilir":"trustworthy","insan":"hcai"},
     "ru":{"многоязычный":"multilingual","арабский":"multilingual","перевод":"multilingual","оценка":"evaluation",
           "здоровье":"bio","биология":"bio","надёжный":"trustworthy","человек":"hcai"},
     "ga":{"ilteangach":"multilingual","araibis":"multilingual","aistriúchán":"multilingual","meastóireacht":"evaluation",
           "sláinte":"bio","bitheolaíocht":"bio","iontaofa":"trustworthy","daonna":"hcai"},
     "fa":{"چندزبانه":"multilingual","عربی":"multilingual","ترجمه":"multilingual","ارزیابی":"evaluation",
           "سلامت":"bio","زیست":"bio","قابل‌اعتماد":"trustworthy","انسان":"hcai"},
     "he":{"רב-לשוני":"multilingual","ערבית":"multilingual","תרגום":"multilingual","הערכה":"evaluation",
           "בריאות":"bio","ביולוגיה":"bio","אמין":"trustworthy","אנושי":"hcai"},
    }
    index = {"generated":BUILD_DATE,"theme_names":themes,"glossary":glossary,"docs":docs,
             "counts":{"publications":len(pubs),"docs":len(docs)}}
    (outdir/"knowledge-graph.json").write_text(json.dumps({"generated":BUILD_DATE,"nodes":nodes,"edges":edges}, ensure_ascii=False), encoding="utf-8")
    (outdir/"assistant-index.json").write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    # PRIVATE knowledge-gap report: what the assistant CANNOT answer well yet (never published).
    # Grounded, factual coverage diagnostics only — no fabricated content.
    gaps = []
    no_url = [p["title"] for p in pubs if not p.get("url")]
    no_theme = [p["title"] for p in pubs if not p.get("themes")]
    theme_counts = {tid:0 for tid in themes}
    for p in pubs:
        for th in p.get("themes",[]):
            if th in theme_counts: theme_counts[th]+=1
    thin = [themes[t] for t,c in theme_counts.items() if c<2]
    if no_url: gaps.append(f"- {len(no_url)} publication(s) have no link to an authoritative source, so the assistant can cite them only by title: "+"; ".join(no_url[:8])+(" …" if len(no_url)>8 else ""))
    if no_theme: gaps.append(f"- {len(no_theme)} publication(s) carry no theme tag, so cross-language theme retrieval will miss them: "+"; ".join(no_theme[:8])+(" …" if len(no_theme)>8 else ""))
    if thin: gaps.append(f"- Thinly-covered themes (<2 indexed publications), where answers will be sparse: "+", ".join(thin))
    if not talks: gaps.append("- No talks are indexed; journalist/outreach queries will retrieve little.")
    report = ("# Knowledge-gap report (PRIVATE — do not publish)\n\n"
        f"Generated {BUILD_DATE} from the retrieval index. This lists where the grounded assistant has thin or "
        "missing coverage, so records can be improved. It contains no invented content — only coverage diagnostics.\n\n"
        f"Index: {len(docs)} retrievable records ({len(pubs)} publications, {len([d for d in docs if d['type']=='project'])} projects, "
        f"{len([d for d in docs if d['type']=='talk'])} talks).\n\n"
        + ("## Coverage gaps\n"+"\n".join(gaps) if gaps else "## Coverage gaps\nNo structural gaps detected.")
        + "\n\n## How to close a gap\nAdd the missing `url` or `themes` to the record in `data/*.json`, verify it against the "
          "authoritative source, and rebuild. The assistant improves automatically — no assistant code changes are needed.\n")
    try:
        rep_dir = ROOT/"reports"; rep_dir.mkdir(exist_ok=True)
        (rep_dir/"knowledge-gaps.md").write_text(report, encoding="utf-8")
    except Exception as e:
        warnings.append(f"knowledge-gap report not written: {e}")
    return len(nodes), len(edges), len(docs)

def ensure_feed_scaffolds():
    """Generate real ICS calendars + RSS feeds in site/ from the verified registries, so the
    deployed site always carries correct feeds even from a plain build. Only verified dates are
    included; speculative dates are never emitted."""
    cal = OUT/"calendars"; cal.mkdir(parents=True, exist_ok=True)
    feeds = OUT/"feeds"; feeds.mkdir(parents=True, exist_ok=True)
    conf = load("conference_deadlines.json") or {}; fund = load("funding_calls.json") or {}
    conf_ev, arabic_ev = [], []
    for e in conf.get("editions", []):
        for d in e.get("deadlines", []):
            if d.get("verification_status")=="verified" and d.get("date"):
                ev = {"uid": f'{e["id"]}-{d["type"]}', "date": d["date"],
                      "summary": f'{e["edition"]} — {d["label"]}', "url": e.get("official_url","")}
                conf_ev.append(ev)
                if "arabic" in (e.get("series","")+" "+" ".join(e.get("topics",[]))).lower(): arabic_ev.append(ev)
    fund_ev = [{"uid": c["id"], "date": c["deadline"], "summary": f'{c.get("programme","")} — {c.get("title","")}',
                "url": c.get("official_url","")} for c in fund.get("calls", [])
               if c.get("deadline") and c.get("verification_status")=="verified"]
    for fn, ev in [("nlp-deadlines",conf_ev),("ai-deadlines",conf_ev),("arabic-nlp-deadlines",arabic_ev),
                   ("eu-funding-calls",fund_ev),("irish-funding-calls",fund_ev),("hai-events",[]),
                   ("all-research-deadlines",conf_ev+fund_ev)]:
        (cal/f"{fn}.ics").write_text(_ics(ev), encoding="utf-8")
    def rss(title, items):
        it = "".join(f"<item><title>{i['t']}</title><link>{i['u']}</link>"
                     f"<guid isPermaLink=\"false\">{i['uid']}</guid></item>" for i in items)
        return ('<?xml version="1.0" encoding="utf-8"?><rss version="2.0"><channel>'
                f'<title>HAI — {title}</title>'
                '<link>https://hafli.github.io/haithem-afli-academic-website/</link>'
                f'<description>HAI — {title}</description>{it}</channel></rss>')
    (feeds/"deadlines.xml").write_text(rss("Conference deadlines",
        [{"t":e["summary"],"u":e["url"],"uid":e["uid"]} for e in conf_ev]), encoding="utf-8")
    (feeds/"funding-calls.xml").write_text(rss("Funding calls",
        [{"t":e["summary"],"u":e["url"],"uid":e["uid"]} for e in fund_ev]), encoding="utf-8")
    (feeds/"hai-news.xml").write_text(rss("HAI News", []), encoding="utf-8")
    (feeds/"hai-newsletter.xml").write_text(rss("HAI Research Brief", []), encoding="utf-8")

def main():
    t0 = time.time()
    verbose = "--verbose" in sys.argv
    check = "--check" in sys.argv
    data = {n: load(n+".json") for n in ["profile","publications","supervision","projects","news","service","teaching","talks","patent","gallery","rinn"]}
    if any(v is None for v in data.values()):
        print("\n".join(warnings)); sys.exit(2)
    for p in data["publications"]["publications"]:
        for k in ("title","authors","venue","year","type"):
            if k not in p: warnings.append(f"pub missing {k}: {p.get('title','?')}")
        if p.get("url") and not valid_url(p["url"]): warnings.append(f"bad pub url: {p['title']}")
    if check:
        print("CHECK:", "clean" if not warnings else f"{len(warnings)} warning(s)")
        print("\n".join(" - "+w for w in warnings)); sys.exit(1 if warnings else 0)

    OUT.mkdir(exist_ok=True)
    # Generate PDF CV from canonical data (best-effort; button is conditional on the file existing)
    try:
        import importlib.util as _il
        spec = _il.spec_from_file_location("gen_cv", ROOT/"scripts/generate_cv.py")
        _m = _il.module_from_spec(spec); spec.loader.exec_module(_m); _m.main()
    except Exception as e:
        warnings.append(f"CV PDF not generated: {e}")
    # Ensure feed/calendar scaffolds exist so the portal pages validate (admin_sync enriches them)
    ensure_feed_scaffolds()
    pages = render(data["profile"],data["publications"],data["supervision"],data["projects"],
                   data["news"],data["service"],data["teaching"],data["talks"],data["patent"],data["gallery"],data["rinn"])
    for slug, html_doc in pages.items():
        (OUT/f"{'index' if slug=='index' else slug}.html").write_text(html_doc, encoding="utf-8")
    (OUT/"style.css").write_text(CSS, encoding="utf-8")
    (OUT/"pubs.js").write_text(PUBS_JS, encoding="utf-8")
    (OUT/"sup.js").write_text(SUP_JS, encoding="utf-8")
    (OUT/"news.js").write_text(NEWS_JS, encoding="utf-8")
    (OUT/"assistant.js").write_text(ASSISTANT_JS, encoding="utf-8")
    (OUT/"email.js").write_text(EMAIL_JS, encoding="utf-8")
    (OUT/"gallery.js").write_text(GALLERY_JS, encoding="utf-8")
    (OUT/"timeline.js").write_text(TIMELINE_JS, encoding="utf-8")
    kn, ke, kd = build_knowledge_index()
    if verbose: print(f"Knowledge index: {kn} nodes, {ke} edges, {kd} retrievable docs")
    # Read-only public API layer (aggregate, non-personal). Generated from verified data every build.
    try:
        import importlib.util as _il2
        _s2 = _il2.spec_from_file_location("research_os", ROOT/"scripts/research_os.py")
        _ros = _il2.module_from_spec(_s2); _s2.loader.exec_module(_ros)
        _eps = _ros.gen_api()
        if verbose: print(f"Public API: {len(_eps)} endpoints under site/api/")
    except Exception as e:
        warnings.append(f"Public API not generated: {e}")
    (OUT/"feed.xml").write_text(feed(data["news"]), encoding="utf-8")
    (OUT/"sitemap.xml").write_text(sitemap(list(pages)), encoding="utf-8")
    (OUT/"robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {BASE_URL}/sitemap.xml\n", encoding="utf-8")
    (OUT/".nojekyll").write_text("", encoding="utf-8")

    if verbose: print("Publishing static assets:")
    copied = publish_assets(verbose)
    inv, missing_deriv = derivative_report(data["gallery"])
    errors, refmap = validate_site(pages, verbose)
    for md in missing_deriv:
        errors.append(f"missing image derivative -> {md}")
    duration = time.time() - t0
    write_reports(pages, copied, inv, errors, refmap, duration)

    imgs = [f for f in copied if re.search(r'\.(jpg|jpeg|png|webp|gif|svg)$', f, re.I)]
    print("Pages generated:", len(pages))
    print("Images copied:  ", len(imgs))
    print("  JPEG:", len([f for f in copied if f.lower().endswith('.jpg')]))
    print("  WebP:", len([f for f in copied if f.lower().endswith('.webp')]))
    print("  PNG :", len([f for f in copied if f.lower().endswith('.png')]))
    print("CSS files:      ", len(list(OUT.glob('*.css'))))
    print("JavaScript files:", len(list(OUT.glob('*.js'))))
    print("PDFs copied:    ", len([f for f in copied if f.lower().endswith('.pdf')]))
    broken_links = [e for e in errors if "missing asset" in e or "root-relative" in e]
    missing_imgs = [e for e in errors if "derivative" in e or re.search(r'\.(jpg|jpeg|png|webp)', e)]
    print("Broken internal links:", len(broken_links))
    print("Missing images:", len(missing_imgs))
    print("Missing assets:", len(errors))
    if errors:
        print("\nBUILD FAILED — unresolved references:")
        print("\n".join(" - "+e for e in errors))
        print(f"\nSee {OUT/'build-report.html'} for details.")
        sys.exit(1)
    print("Build completed successfully.")
    if warnings and verbose:
        print("Warnings:\n"+"\n".join(" - "+w for w in warnings))

if __name__ == "__main__":
    main()
