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
       ("service","Leadership & Service"),("news","News"),("gallery","Media"),("cv","CV"),("contact","Contact")]

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
<link rel="stylesheet" href="style.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site">
  <div class="brand"><a href="index.html">Dr Haithem Afli</a><span>AI &amp; Human-Centred Computing · MTU</span></div>
  <nav aria-label="Primary">{nav}</nav>
</header>
<main id="main">
<h1>{esc(title)}</h1>
{body}
</main>
<footer class="site">
  <p>© {datetime.date.today().year} Haithem Afli.
     <a href="https://orcid.org/0000-0002-7449-4707" rel="noopener">ORCID 0000-0002-7449-4707</a>.
     Built {esc(BUILD_DATE)} from verified sources. Content may not be exhaustive; corrections welcome.</p>
</footer>
</body>
</html>"""

# ---------- pages ----------
def render(profile, pubs, sup, projects, news, service, teaching, talks, patent, gallery, rinn):
    pages = {}
    themes = {t["id"]: t["name"] for t in profile["themes"]}

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
    body = f"""
<div class="placeholder-photo" role="img" aria-label="Professional photograph to be added">Photograph pending</div>
<p class="lede">{esc(profile["title"])}, {esc(profile["affiliation"])}.</p>
<p class="roles-hero">Institutional Co-Lead, Rinn Artificial Intelligence at MTU · Deputy Theme Lead,
Inclusive Language Model &amp; Translation Methods · Principal Investigator, Rinn AI and ADAPT Centre ·
Founder and Lead, Human-Centred AI Research Group.</p>
<p>{esc(profile["positioning"])}</p>
<section class="feature"><h2>New national research leadership</h2>
<p>Dr Haithem Afli has joined Rinn Artificial Intelligence as Institutional Co-Lead at MTU, Deputy Theme
Lead for Inclusive Language Model &amp; Translation Methods, and Principal Investigator. His work focuses on
multilingual and inclusive language technologies, culturally aware AI, translation methods and reliable
evaluation of language models. <a href="rinn-ai.html">Read about Rinn AI at MTU →</a></p></section>
<section><h2>Current roles</h2><ul class="pubs">{"".join(f'<li>{esc(r["role"])}</li>' for r in profile["roles"])}</ul></section>
<section><h2>Research themes</h2><ul class="themes">{themes_html}</ul></section>
<section><h2>Selected recent publications</h2><ul class="pubs">{recent}</ul>
<p><a href="publications.html">All publications →</a></p></section>
<section><h2>Latest news</h2><ul>{"".join(f'<li><span class="muted">{esc(n["date"])}</span> — {esc(n["headline"])}</li>' for n in news["items"][:3])}</ul>
<p><a href="news.html">More news →</a></p></section>
"""
    pages["index"] = page("index","Dr Haithem Afli", body,
        profile["short_description"], person_ld)

    # ABOUT (biography — verified, EU English, no hype)
    edu = "".join(f'<li><strong>{esc(e["degree"])}</strong>, {esc(e["institution"])}, {e["year"]}'
                  f'{" — <em>"+esc(e["thesis"])+"</em>" if e.get("thesis") else ""}.</li>' for e in profile["education"])
    roles_list = "".join(f'<li>{esc(r["role"])}</li>' for r in profile["roles"]) + \
        '<li>Principal Investigator and MTU Lead, ADAPT Centre</li>' \
        '<li>Founder and Lead, Human-Centred AI Research Group</li>' \
        '<li>Chair, Computer Science Postgraduate Research Board</li>' \
        '<li>Elected Member, MTU Academic Council</li>' \
        '<li>External Expert, European Commission Research Executive Agency</li>' \
        '<li>IEEE Senior Member</li>'
    body = f"""
<p>Dr Haithem Afli is a Lecturer in Artificial Intelligence at Munster Technological University and a
research leader in multilingual, culturally aware and human-centred AI. He is Institutional Co-Lead for
Rinn Artificial Intelligence at MTU, Deputy Theme Lead for Inclusive Language Model &amp; Translation
Methods, and a Principal Investigator in the centre.</p>
<p>He is also a Principal Investigator and MTU research lead within the Research Ireland ADAPT Centre and
founder and lead of the Human-Centred AI Research Group. His research spans multilingual natural language
processing, inclusive language models, machine translation, culturally grounded AI, evaluation science,
trustworthy AI, and applications of machine learning in healthcare and computational biology.</p>
<p>His work investigates how language technologies can better represent linguistic diversity, cultural
context and under-resourced communities. He is particularly interested in Arabic and multilingual language
technologies, the reliability of large-language-model evaluation, cross-cultural reasoning, inclusive
translation methods and human-centred approaches to responsible AI.</p>
<p>Through Rinn AI, ADAPT and major European research programmes, he contributes to foundational research,
interdisciplinary collaboration and the translation of AI research into practical societal, educational,
healthcare and industrial applications.</p>
<p>At MTU, he chairs the Computer Science Postgraduate Research Board, supervises doctoral, postdoctoral and
Master's researchers, and is an elected member of MTU Academic Council. He also serves as an external expert
for the European Commission Research Executive Agency and is a Senior Member of the IEEE.</p>
<h2>Current roles</h2><ul class="pubs">{roles_list}</ul>
<h2>Education</h2><ul>{edu}</ul>
<h2>Identifiers and profiles</h2>
<ul class="ids">{profile_links_html(profile)}</ul>
<p class="note">A canonical MTU staff-profile page has not yet been confirmed; verified scholarly profiles are linked above.</p>
"""
    pages["about"] = page("about","About", body, profile["short_description"], person_ld)

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
            f'<section id="agenda"><h2>Current research agenda</h2><ol class="agenda">{agenda_html}</ol></section>')
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
            vp = ' <span class="tag">confirmation pending</span>' if p.get("verification_pending") and "WITHHELD" not in p.get("verification_pending","") else ""
            name = link(p.get("url"), p["name"]) if p.get("url") else esc(p["name"])
            out += (f'<tr><td>{name}{vp}</td><td>{esc(p.get("programme") or p.get("funder",""))}</td>'
                    f'<td>{esc(p.get("role",""))}</td><td>{" · ".join(amt)}{note}</td><td>{esc(p.get("period",""))}</td></tr>')
        return out
    withheld = [p["name"] for p in projects["national_projects"] if "WITHHELD" in p.get("note","")]
    body = f"""
<p class="lede">Funded research projects and institutional roles. Figures distinguish total consortium
funding from the MTU allocation; consortium totals are not presented as personally secured funding.</p>
<p class="note">{esc(projects["note"])}</p>
<h2>European projects</h2>
<table><thead><tr><th>Project</th><th>Programme</th><th>Role</th><th>Funding</th><th>Period</th></tr></thead>
<tbody>{proj_rows(projects["eu_projects"])}</tbody></table>
<h2>National projects</h2>
<table><thead><tr><th>Project</th><th>Funder</th><th>Role</th><th>Funding</th><th>Period</th></tr></thead>
<tbody>{proj_rows(projects["national_projects"])}</tbody></table>
<p class="note">Some nationally funded activities are undergoing source confirmation and are withheld from
public display until verified against official records.</p>
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
align with these themes. Enquiries via the <a href="contact.html">contact page</a>.</p>""",
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
            flagged = ' <span class="tag">title verification pending</span>' if m.get("notes") and "VERIFICATION QUEUE" in m["notes"] else ""
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
        f'<p class="lede">{esc(teaching["philosophy"])}</p><h2>Programmes and modules</h2><ul class="pubs">{tp}</ul>',
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
        f'<p class="lede">Selected invited talks, keynotes and public engagement.</p><ul class="pubs">{tk}</ul>',
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

    # MEDIA GALLERY (empty until rights-cleared images exist)
    if gallery["images"]:
        g = ""
        for cat in gallery["categories"]:
            imgs = [i for i in gallery["images"] if i.get("category")==cat and valid_url(i.get("src",""))]
            if not imgs: continue
            g += f'<h2>{esc(cat.replace("-"," ").title())}</h2><div class="grid-img">'
            for i in imgs:
                credit = f'<span class="muted">{esc(i["credit"])}</span>' if i.get("credit") else ""
                g += (f'<figure><img src="{esc(i["src"])}" alt="{esc(i.get("alt",""))}" '
                      f'width="{esc(i.get("w",400))}" height="{esc(i.get("h",300))}" loading="lazy">'
                      f'<figcaption>{esc(i.get("caption",""))} {credit}</figcaption></figure>')
            g += '</div>'
        body = f'<p class="lede">Selected photographs from professional academic activities.</p>{g}'
    if not any(valid_url(i.get("src","")) for i in gallery["images"]):
        approved = len(gallery["images"])
        body = (f'<p class="lede">A professional media gallery — conference and keynote photographs, '
                f'research events, awards and research-group activities.</p>'
                f'<p class="note">{approved} photographs have been approved by Dr Afli and are prepared for '
                f'publication, but their image files have not yet been added to the site, so none are displayed '
                f'here. Each has an agreed caption and alternative text and will appear automatically once the '
                f'source file is provided and processed (see the image policy). No image is published until its '
                f'file is present and privacy-reviewed.</p>')
    pages["gallery"] = page("gallery","Media", body,
        "Professional media gallery of Dr Haithem Afli: conferences, talks, research events and awards.", person_ld)

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
        '<p>Key sections: <a href="about.html">biography</a>, <a href="rinn-ai.html">Rinn AI</a>, '
        '<a href="publications.html">publications</a>, <a href="projects.html">projects and funding</a>, '
        '<a href="supervision.html">supervision</a>, <a href="service.html">leadership and service</a>.</p>'
        '<p class="note">The downloadable PDF curriculum vitae is dated April 2026 and does not yet include the '
        'Rinn AI appointments above; this website carries the more recent roles. An updated PDF will be added '
        'when generated intentionally.</p>',
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
ol.agenda{padding-left:1.2rem}ol.agenda li{margin:.4rem 0}"""

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

def main():
    check = "--check" in sys.argv
    data = {n: load(n+".json") for n in ["profile","publications","supervision","projects","news","service","teaching","talks","patent","gallery","rinn"]}
    if any(v is None for v in data.values()):
        print("\n".join(warnings)); sys.exit(2)
    # schema smoke-checks
    for p in data["publications"]["publications"]:
        for k in ("title","authors","venue","year","type"):
            if k not in p: warnings.append(f"pub missing {k}: {p.get('title','?')}")
        if p.get("url") and not valid_url(p["url"]): warnings.append(f"bad pub url: {p['title']}")
    if check:
        print("CHECK:", "clean" if not warnings else f"{len(warnings)} warning(s)")
        print("\n".join(" - "+w for w in warnings)); sys.exit(1 if warnings else 0)
    OUT.mkdir(exist_ok=True)
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
    print(f"BUILD OK: {len(pages)} pages -> {OUT}")
    if warnings: print("WARNINGS:\n"+"\n".join(" - "+w for w in warnings))

if __name__ == "__main__":
    main()
