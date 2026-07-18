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
NAV = [("index","Home"),("about","About"),("research","Research"),("rinn-ai","Rinn AI"),("publications","Publications"),
       ("projects","Projects & Funding"),("group","HAI Group"),("supervision","Supervision"),
       ("teaching","Teaching"),("innovation","Innovation"),("talks","Talks & Outreach"),
       ("service","Leadership & Service"),("news","News"),("research-intelligence","Research Intelligence"),
       ("gallery","Media"),("cv","CV"),("contact","Contact")]

PROFILE_LINK_LABELS = {
    "orcid.org":"ORCID","aclanthology.org":"ACL Anthology","adaptcentre.ie":"ADAPT Centre",
    "dblp.org":"DBLP","scholar.google.com":"Google Scholar","dl.acm.org":"ACM Digital Library",
    "openreview.net":"OpenReview","researchgate.net":"ResearchGate","linkedin.com":"LinkedIn","x.com":"X"}
def profile_links_html(profile):
    out = []
    for u in profile["sameAs"]:
        if not valid_url(u): continue
        host = u.split("//")[1].split("/")[0].replace("www.","")
        label = next((v for k,v in PROFILE_LINK_LABELS.items() if k in host), host)
        out.append(f'<li>{link(u, label)}</li>')
    return "".join(out)

def page(slug, title, body, description, jsonld=None):
    def navlink(s, t):
        href = "index.html" if s == "index" else s + ".html"
        cur = ' aria-current="page"' if s == slug else ""
        return f'<a href="{href}"{cur}>{esc(t)}</a>'
    nav = " ".join(navlink(s, t) for s, t in NAV)
    ld = f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>' if jsonld else ""
    canonical = f"{BASE_URL}/{'index.html' if slug=='index' else slug+'.html'}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} — Dr Haithem Afli</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canonical)}">
<meta property="og:title" content="{esc(title)} — Dr Haithem Afli">
<meta property="og:description" content="{esc(description)}">
<meta property="og:type" content="profile">
<meta property="og:url" content="{esc(canonical)}">
<meta name="twitter:card" content="summary">
<link rel="alternate" type="application/atom+xml" title="News" href="feed.xml">
<link rel="alternate" hreflang="en" href="{esc(canonical)}">
<link rel="alternate" hreflang="x-default" href="{esc(canonical)}">
<link rel="stylesheet" href="style.css">
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
    <li><a href="languages.html" lang="fr">Français</a></li></ul></details>
</header>
<main id="main">
<h1>{esc(title)}</h1>
{body}
</main>
<footer class="site">
  <p>© {datetime.date.today().year} Haithem Afli. Last updated July 2026.</p>
</footer>
</body>
</html>"""

# ---------- pages ----------
def render(profile, pubs, sup, projects, news, service, teaching, talks, patent, gallery, rinn):
    pages = {}
    themes = {t["id"]: t["name"] for t in profile["themes"]}
    IMGS = {i["id"]: i for i in gallery.get("images", []) if valid_url_or_local(i.get("src",""))}

    def fig(image_id, hero=False, cls="fig"):
        i = IMGS.get(image_id)
        if not i: return ""
        loading = "" if hero else ' loading="lazy"'
        srcset = f' srcset="{esc(i["srcset"])}"' if i.get("srcset") else ""
        cap = f'<figcaption>{esc(i["caption"])}</figcaption>' if i.get("caption") else ""
        return (f'<figure class="{cls}"><img src="{esc(i["src"])}" alt="{esc(i.get("alt",""))}"'
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
        "email":f'mailto:{profile["email"]}',"identifier":f'https://orcid.org/{profile["orcid"]}',
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

    # HOME
    recent = "".join(
        f'<li>{link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"])} '
        f'<span class="muted">— {esc(p["venue"])}, {p["year"]}</span></li>'
        for p in pubs["publications"][:5])
    themes_html = "".join(f'<li><a href="research.html#{esc(t["id"])}">{esc(t["name"])}</a></li>' for t in profile["themes"])
    hero_img = fig("haithem-afli-portrait", hero=True, cls="portrait") or \
        '<div class="placeholder-photo" role="img" aria-label="Portrait">Portrait</div>'
    body = f"""
<div class="hero">{hero_img}
<div>
<p class="lede">{esc(profile["title"])}, {link("https://www.mtu.ie/","Munster Technological University")}, Cork.</p>
<p class="roles-hero">Institutional Co-Lead, Rinn Artificial Intelligence at MTU · Principal Investigator, ADAPT Centre ·
Founder and Lead, Human-Centred AI Research Group.</p>
<p>{esc(profile["positioning"])}</p>
</div></div>
<section class="feature"><h2>New national research leadership</h2>
<p>Dr Haithem Afli has joined <a href="rinn-ai.html">Rinn Artificial Intelligence</a> as Institutional
Co-Lead at MTU, Deputy Theme Lead for Inclusive Language Model &amp; Translation Methods, and Principal
Investigator — focusing on multilingual and inclusive language technologies, culturally aware AI,
translation methods and reliable evaluation of language models. <a href="rinn-ai.html">Read more →</a></p></section>
<section><h2>Research themes</h2><ul class="themes">{themes_html}</ul>
<p><a href="research.html">Research and current agenda →</a> · <a href="about.html">About and full roles →</a></p></section>
<section><h2>Selected recent publications</h2><ul class="pubs">{recent}</ul>
<p><a href="publications.html">All publications →</a></p></section>
<section><h2>Latest news</h2><ul>{"".join(f'<li><span class="muted">{esc(n["date"])}</span> — {esc(n["headline"])}</li>' for n in news["items"][:3])}</ul>
<p><a href="news.html">More news →</a></p></section>
<section><h2>Research Intelligence</h2>
<p class="muted">Maintained conference deadlines, European and Irish funding calls, a research calendar, and the
fortnightly HAI Research Brief — all from official sources.</p>
{("<ul>"+next_deadline_html+"</ul>") if next_deadline_html else ""}
<p><a href="research-intelligence.html">Open Research Intelligence →</a> · <a href="subscribe.html">Subscribe</a></p></section>
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
    sects = "".join(
        f'<section id="{esc(t["id"])}"><h2>{esc(t["name"])}</h2><p>{esc(theme_desc.get(t["id"],""))}</p></section>'
        for t in profile["themes"])
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

    # PUBLICATIONS (filter by year/type/theme with progressive-enhancement JS)
    def pub_item(p):
        authors = ", ".join(esc(a) for a in p["authors"])
        title = link(p.get("url"), p["title"]) if p.get("url") else esc(p["title"])
        bib = f' · {link("https://aclanthology.org/"+p["anthology_id"]+".bib","BibTeX")}' if p.get("anthology_id") else ""
        doi = f' · DOI {esc(p["doi"])}' if p.get("doi") else ""
        status = "" if p.get("status")=="published" else f' <span class="tag">{esc(p.get("status"))}</span>'
        th = "".join(f'<span class="tag">{esc(themes.get(t,t))}</span>' for t in p.get("themes",[]))
        return (f'<li class="pub" data-year="{p["year"]}" data-type="{esc(p["type"])}" '
                f'data-themes="{esc(" ".join(p.get("themes",[])))}">'
                f'<div class="pub-t">{title}{status}</div>'
                f'<div class="pub-m">{authors}. <em>{esc(p["venue"])}</em>, {p["year"]}.{doi}{bib}</div>'
                f'<div class="pub-tags">{th}</div></li>')
    years = sorted({p["year"] for p in pubs["publications"]}, reverse=True)
    ptypes = sorted({p["type"] for p in pubs["publications"]})
    filt = ('<div class="filters" role="group" aria-label="Filter publications">'
            '<label>Theme <select id="f-theme"><option value="">All</option>'
            + "".join(f'<option value="{esc(t["id"])}">{esc(t["name"])}</option>' for t in profile["themes"])
            + '</select></label> '
            '<label>Type <select id="f-type"><option value="">All</option>'
            + "".join(f'<option value="{esc(t)}">{esc(t)}</option>' for t in ptypes)
            + '</select></label></div>')
    items = "".join(pub_item(p) for p in sorted(pubs["publications"], key=lambda x:(-x["year"], x["title"])))
    body = (f'<p class="lede">Selected and recent publications. The complete, continuously updated list is on '
            f'{link("https://aclanthology.org/people/haithem-afli/","ACL Anthology")}, '
            f'{link("https://orcid.org/0000-0002-7449-4707","ORCID")} and '
            f'{link("https://dblp.org/pid/120/2260.html","DBLP")}.</p>'
            f'<p class="note">{esc(pubs["note"])}</p>{filt}<ul class="pubs list">{items}</ul>'
            '<script src="pubs.js" defer></script>')
    pages["publications"] = page("publications","Publications", body,
        "Publications by Dr Haithem Afli in NLP, evaluation science, multilingual AI and AI for biology.", person_ld)

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

<h2>Rinn AI, ADAPT and the HAI Research Group</h2>
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

    # MEDIA GALLERY (curated categories)
    cat_labels = {"research-conferences":"Research conferences","teaching":"Teaching",
        "public-engagement":"Public engagement","research-collaborations":"Research collaborations",
        "supervision":"Supervision and academic milestones","hai-group":"HAI Research Group","portrait":"Portrait"}
    g = ""
    for cat in gallery["categories"]:
        if cat == "portrait": continue
        ids = [i["id"] for i in gallery["images"] if i.get("category")==cat and i["id"] in IMGS]
        if not ids: continue
        g += f'<h2>{esc(cat_labels.get(cat, cat.replace("-"," ").title()))}</h2><div class="grid-img">' + "".join(fig(x) for x in ids) + '</div>'
    body = f'<p class="lede">Selected photographs from professional academic activities, supplied by Dr Afli.</p>{g}'
    pages["gallery"] = page("gallery","Media", body,
        "Professional media gallery of Dr Haithem Afli: conferences, talks, teaching, research collaborations and supervision.", person_ld)

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
        '<h2>Feeds</h2><p>RSS: <a href="feeds/deadlines.xml">deadlines</a>, <a href="feeds/funding-calls.xml">funding</a>, '
        '<a href="feeds/hai-newsletter.xml">newsletter</a>. '
        'Calendar: <a href="calendars/all-research-deadlines.ics">all research deadlines (ICS)</a>.</p>'
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
        '<p class="note">A privacy-compliant mailing provider must be connected before the form goes live (subscriber '
        'data is never stored in this repository, and no email addresses appear in any generated file). Until then, '
        'contact <a href="mailto:'+esc(profile["email"])+'">'+esc(profile["email"])+'</a> to be added manually.</p>'
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
        '<h2>Contact</h2><p>Privacy questions: <a href="mailto:'+esc(profile["email"])+'">'+esc(profile["email"])+'</a>.</p>',
        "Privacy notice: privacy-conscious analytics and newsletter data handling.", person_ld)

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
<p><strong>Email:</strong> {link("mailto:"+profile["email"], profile["email"])}</p>
<p><strong>Affiliation:</strong> {esc(profile["affiliation"])}</p>
<h2>Profiles and links</h2><ul class="ids">{profile_links_html(profile)}</ul>
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

CSS = """:root{--ink:#1a1a1a;--muted:#5a5f66;--line:#e2e5ea;--accent:#0b5c8a;--bg:#fff;--tag:#eef2f6}
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
details.langsel ul{list-style:none;display:flex;flex-wrap:wrap;gap:.2rem .9rem;padding:.4rem 0 0;margin:0}"""

PUBS_JS = """(function(){var t=document.getElementById('f-theme'),y=document.getElementById('f-type');
function f(){var th=t.value,ty=y.value;document.querySelectorAll('.pub').forEach(function(p){
var ok=(!th||(' '+p.dataset.themes+' ').indexOf(' '+th+' ')>=0)&&(!ty||p.dataset.type===ty);
p.style.display=ok?'':'none';});}
if(t)t.addEventListener('change',f);if(y)y.addEventListener('change',f);})();"""

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
