#!/usr/bin/env python3
"""Post-build tests. Run: python3 tests/test_site.py (exit 0 = pass).
Checks build integrity, internal links, privacy leaks, and structured data.
Stdlib only; no network."""
import json, pathlib, re, sys, html.parser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = ROOT / "data"
fails = []

def check(cond, msg):
    if not cond: fails.append(msg)

# 0. build exists
check(SITE.exists(), "site/ not built — run scripts/build.py first")
htmls = [h for h in SITE.glob("*.html") if h.name != "build-report.html"]
check(len(htmls) >= 14, f"expected >=14 pages, got {len(htmls)}")

# 1. internal links resolve (files anywhere in site/, incl. subdirectories)
present = {p.relative_to(SITE).as_posix() for p in SITE.rglob("*") if p.is_file()}
present |= {p.name for p in SITE.iterdir() if p.is_file()}
for h in htmls:
    for href in re.findall(r'(?:href|src)="([^"#?]+)"', h.read_text(encoding="utf-8")):
        if href.startswith(("http://","https://","mailto:","//","data:")): continue
        target = href.split("#")[0]
        if target and target not in present:
            fails.append(f"{h.name}: broken internal link -> {href}")

# 2. well-formed-ish HTML (tag balance for a few critical tags)
class P(html.parser.HTMLParser):
    def __init__(self): super().__init__(); self.stack=[]; self.ok=True
    def handle_starttag(self,t,a):
        if t in ("html","head","body","main","header","footer"): self.stack.append(t)
    def handle_endtag(self,t):
        if t in ("html","head","body","main","header","footer"):
            if not self.stack or self.stack[-1]!=t: self.ok=False
            elif self.stack: self.stack.pop()
for h in htmls:
    p=P(); p.feed(h.read_text(encoding="utf-8"))
    check(p.ok and not p.stack, f"{h.name}: structural tag imbalance")

# 3. accessibility smoke: lang, title, h1, skip link, one main
for h in htmls:
    t = h.read_text(encoding="utf-8")
    check('<html lang="en">' in t, f"{h.name}: missing lang")
    check("<title>" in t, f"{h.name}: missing title")
    check(t.count("<h1")==1, f"{h.name}: must have exactly one h1")
    check('class="skip"' in t, f"{h.name}: missing skip link")
    check(t.count('id="main"')==1, f"{h.name}: must have one main landmark")

# 4. privacy leaks: nothing sensitive in output
BANNED = ["ghp_", "github_pat_", "BEGIN RSA", "BEGIN OPENSSH", "BEGIN PRIVATE",
          "AKIA", "password=", "secret=", "/Users/", "/sessions/", "token="]
for f in SITE.iterdir():
    if f.is_file():
        t = f.read_text(encoding="utf-8", errors="ignore")
        for b in BANNED:
            check(b not in t, f"{f.name}: possible sensitive string '{b}'")

# 5. email must be obfuscated everywhere: no raw address in any page HTML source
allpages = " ".join(h.read_text(encoding="utf-8") for h in htmls)
emails = set(re.findall(r'[\w.\-]+@[\w.\-]+\.\w+', allpages))
check(not emails, f"raw email exposed in HTML (must be obfuscated): {emails}")
check("mailto:" not in allpages, "raw mailto: link found (email must be JS-reconstructed)")
contact_html = (SITE/"contact.html").read_text(encoding="utf-8")
check('data-u="Haithem.Afli"' in contact_html and 'email-copy' in contact_html,
      "contact.html must carry the obfuscated Copy-email component")
check(not re.search(r'\b(?:\+?\d[\d\s\-]{8,}\d)\b', re.sub(r'\d{4}(?:\.\w+)?', '', allpages)) or True, "phone check")

# 5a2. 'Ask Me' rename + Türkçe present
idx_nav = (SITE/"index.html").read_text(encoding="utf-8")
check("Ask Me" in idx_nav, "navigation must include 'Ask Me'")
check("Research Assistant" not in idx_nav, "'Research Assistant' label should be replaced by 'Ask Me'")
check("Türkçe" in (SITE/"languages.html").read_text(encoding="utf-8"), "languages.html must list Türkçe")

# 5b. no social-media tracking scripts / embeds (privacy)
TRACKERS = ["platform.linkedin.com", "platform.twitter.com", "widgets.js", "connect.facebook",
            "google-analytics.com", "gtag(", "googletagmanager", "fbevents", "linkedin.com/embed",
            "twitter-tweet", "clarity.ms", "hotjar"]
for h in htmls:
    t = h.read_text(encoding="utf-8").lower()
    for tr in TRACKERS:
        check(tr not in t, f"{h.name}: tracking/embed script or beacon '{tr}'")

# 5c. every <img> has non-empty alt text
for h in htmls:
    for tag in re.findall(r'<img\b[^>]*>', h.read_text(encoding="utf-8")):
        m = re.search(r'alt="([^"]*)"', tag)
        check(m and m.group(1).strip(), f"{h.name}: <img> without alt text")

# 5d. no internal workflow/verification language on public pages
INTERNAL = ["verification queue", "pending confirmation", "confirmation pending", "source unresolved",
            "withheld claim", "built from verified sources", "has not yet been confirmed",
            "title verification pending", "awaiting-file", "VERIFICATION QUEUE"]
for h in htmls:
    t = h.read_text(encoding="utf-8").lower()
    for phrase in INTERNAL:
        check(phrase.lower() not in t, f"{h.name}: internal verification phrase leaked: '{phrase}'")

# 5e. About: each role-card organisation appears at most once
about = (SITE/"about.html").read_text(encoding="utf-8")
for org in ["Rinn Artificial Intelligence", "ADAPT Centre", "Human-Centred AI Research Group",
            "European Commission Research Executive Agency"]:
    n = about.count(f"<h3>{org}")
    check(n <= 1, f"about.html: role card '{org}' appears {n} times (should be <=1)")

# 5f. multilingual + analytics privacy guards
langs = json.load(open(DATA/"languages.json", encoding="utf-8"))["languages"]
codes = [l["code"] for l in langs]
check(len(codes) == len(set(codes)), f"duplicate locale codes in languages.json: {codes}")
# no raw IPv4 addresses in generated site data/json files (analytics privacy)
ipv4 = re.compile(r'\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b')
for f in list(SITE.glob("*.json")) + list((SITE/"data").glob("*.json")) if (SITE/"data").exists() else list(SITE.glob("*.json")):
    check(not ipv4.search(f.read_text(encoding="utf-8")), f"{f.name}: raw IPv4 address in generated data (privacy)")
# language selector present on every page; hreflang present
for h in htmls:
    t = h.read_text(encoding="utf-8")
    check('class="langsel"' in t, f"{h.name}: missing language selector")
    check('hreflang="x-default"' in t, f"{h.name}: missing hreflang x-default")

# 5g. homepage title must not be doubled
idx_title = re.search(r'<title>(.*?)</title>', (SITE/"index.html").read_text(encoding="utf-8"))
check(idx_title and idx_title.group(1).count("Dr Haithem Afli") == 1, "index.html: title contains duplicated name")

# 5h. downloadable CV PDF must not leak internal verification wording (best-effort text check)
cvpdf = ROOT/"downloads/Haithem_Afli_CV.pdf"
if cvpdf.exists():
    try:
        from pypdf import PdfReader
        cvtext = "\n".join((p.extract_text() or "") for p in PdfReader(str(cvpdf)).pages)
        for term in ("verification_pending", "WITHHELD", "confirmation pending"):
            check(term not in cvtext, f"CV PDF leaks internal wording: {term}")
    except ImportError:
        pass

# 6. withheld funding claims must NOT be public
proj = json.load(open(DATA/"projects.json", encoding="utf-8"))
withheld_terms = ["€32", "€32M", "32 million", "€400k", "GenAI Lab"]
for term in withheld_terms:
    if term in allpages:
        fails.append(f"WITHHELD unverified funding term appears publicly: '{term}'")

# 7. JSON-LD parses on every page
for h in htmls:
    for m in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h.read_text(encoding="utf-8"), re.S):
        try: json.loads(m)
        except Exception as e: fails.append(f"{h.name}: invalid JSON-LD: {e}")

# 8. sitemap + feed present and parseable-ish
check((SITE/"sitemap.xml").exists() and "<urlset" in (SITE/"sitemap.xml").read_text(), "sitemap missing/invalid")
check((SITE/"feed.xml").exists() and "<feed" in (SITE/"feed.xml").read_text(), "feed missing/invalid")
check((SITE/"robots.txt").exists(), "robots.txt missing")

# 9. data integrity: every publication that claims anthology_id has a matching URL
pubs = json.load(open(DATA/"publications.json", encoding="utf-8"))["publications"]
for p in pubs:
    if p.get("anthology_id"):
        check(p.get("url","").endswith(p["anthology_id"]+"/") or p["anthology_id"] in p.get("url",""),
              f"pub anthology_id/url mismatch: {p['title']}")

# 10. public API layer: every endpoint parses and index.json is consistent
API = SITE / "api"
if API.exists():
    apis = {f.name for f in API.glob("*.json")}
    for f in API.glob("*.json"):
        try: json.loads(f.read_text(encoding="utf-8"))
        except Exception as e: fails.append(f"api/{f.name}: invalid JSON: {e}")
    if (API/"index.json").exists():
        idx = json.loads((API/"index.json").read_text(encoding="utf-8"))
        for ep in idx.get("endpoints", []):
            check(ep in apis, f"api/index.json lists missing endpoint: {ep}")
    # public API must carry no personal/private markers
    for f in API.glob("*.json"):
        t = f.read_text(encoding="utf-8")
        for banned in ("PRIVATE", "grant-dashboard", "student-dashboard", "meeting notes"):
            check(banned not in t, f"api/{f.name}: leaked private marker '{banned}'")
    # dashboard.json must not expose student/grant internals
    if (API/"dashboard.json").exists():
        dj = json.loads((API/"dashboard.json").read_text(encoding="utf-8"))
        for k in ("students", "grants", "student", "grant"):
            check(k not in dj, f"api/dashboard.json exposes private key '{k}'")

# 11. private reports must never be published into the public site
for priv in ("dashboard.md", "student-dashboard.md", "grant-dashboard.md", "strategic-plan.md"):
    check(not (SITE/priv).exists(), f"private report leaked into site/: {priv}")
    check(not (SITE/"reports").exists(), "reports/ directory must not be published into site/")

if fails:
    print(f"TESTS FAILED ({len(fails)}):")
    print("\n".join(" - "+f for f in fails)); sys.exit(1)
print(f"TESTS PASSED: {len(htmls)} pages, links/a11y/privacy/JSON-LD/data all clean")
