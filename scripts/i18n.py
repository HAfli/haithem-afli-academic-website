#!/usr/bin/env python3
"""Multilingual layer for the generated site (Release 3.3). Stdlib only.

English is the source of truth: scripts/build.py renders the English site into site/, then this module
  1. segments every public English page into translatable units — block-level text runs, with inline
     markup replaced by numbered placeholders ({1}…{/1}; protected/void elements as {2/}), plus
     user-visible attributes (alt, title, aria-label, placeholder) and SEO metadata;
  2. looks each unit up in locales/<lang>.json (keyed by a hash of the English text, so any change to
     the English source makes the old translation visibly missing/outdated rather than silently wrong);
  3. writes site/<lang>/<page>.html with lang/dir, canonical, hreflang alternates, Open Graph locale,
     a page-equivalent language switcher, translated breadcrumb data and a translation notice;
  4. rewrites site/sitemap.xml with language alternates and writes the coverage report.

Content marked translate="no" (publication titles, authors, venues, names, thesis titles) is never
translated. A language is offered as available only when every in-scope page is fully translated.

  python3 scripts/i18n.py extract   # refresh locales/source.json from the built English site
  python3 scripts/i18n.py status    # coverage per language
  python3 scripts/i18n.py build     # generate language versions (called by build.py)
"""
import hashlib, html, json, pathlib, re, sys, datetime

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE, DATA, LOCALES = ROOT / "site", ROOT / "data", ROOT / "locales"
BASE_URL = "https://hafli.github.io/haithem-afli-academic-website"

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
INLINE = {"a", "strong", "em", "b", "i", "span", "code", "abbr", "small", "sup", "sub", "br", "time", "cite",
          "mark", "q", "s", "u", "img", "bdi", "bdo", "kbd", "var"}
SKIP = {"script", "style", "pre", "svg", "noscript", "template", "textarea"}
ATTRS = ("alt", "title", "aria-label", "placeholder")
META_TRANSLATE = {("name", "description"), ("property", "og:title"), ("property", "og:description"),
                  ("name", "twitter:title"), ("name", "twitter:description")}
EXCLUDED_PAGES = {"build-report.html"}          # internal build diagnostics, not public content
OG_LOCALE = {"en": "en_IE", "fr": "fr_FR", "ar": "ar_AR", "tr": "tr_TR", "ga": "ga_IE", "es": "es_ES",
             "pt": "pt_PT", "zh": "zh_CN", "fa": "fa_IR", "he": "he_IL", "de": "de_DE", "it": "it_IT",
             "ru": "ru_RU"}
PH = re.compile(r"\{(\d+)\}|\{/(\d+)\}|\{(\d+)/\}")
LETTER = re.compile(r"[^\W\d_]")


# ---------------------------------------------------------------- minimal lossless HTML tree
class Node:
    __slots__ = ("tag", "attrs", "parent", "ch")
    def __init__(self, tag, attrs, parent):
        self.tag, self.attrs, self.parent, self.ch = tag, list(attrs), parent, []
    def get(self, k, d=None):
        for a, v in self.attrs:
            if a == k: return v
        return d
    def set(self, k, v):
        for i, (a, _) in enumerate(self.attrs):
            if a == k: self.attrs[i] = (k, v); return
        self.attrs.append((k, v))

class Raw(str):
    """Serialized-as-is text (comments, doctype, script bodies, entity references)."""

from html.parser import HTMLParser
class _Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("#root", [], None); self.cur = self.root
    def handle_starttag(self, t, a):
        n = Node(t, a, self.cur); self.cur.ch.append(n)
        if t not in VOID: self.cur = n
    def handle_startendtag(self, t, a): self.cur.ch.append(Node(t, a, self.cur))
    def handle_endtag(self, t):
        n = self.cur
        while n is not self.root and n.tag != t: n = n.parent
        if n is not self.root: self.cur = n.parent
    def handle_data(self, d): self.cur.ch.append(Raw(d) if self.cur.tag in ("script", "style") else d)
    def handle_entityref(self, n): self.cur.ch.append(html.unescape(f"&{n};"))
    def handle_charref(self, n): self.cur.ch.append(html.unescape(f"&#{n};"))
    def handle_comment(self, d): self.cur.ch.append(Raw(f"<!--{d}-->"))
    def handle_decl(self, d): self.cur.ch.append(Raw(f"<!{d}>"))
    def handle_pi(self, d): self.cur.ch.append(Raw(f"<?{d}>"))

def parse(text):
    p = _Parser(); p.feed(text); p.close(); return p.root

def _esc_text(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
def _esc_attr(s): return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;")

def open_tag(n):
    a = "".join(f' {k}' if v is None else f' {k}="{_esc_attr(v)}"' for k, v in n.attrs)
    return f"<{n.tag}{a}>"

def serialize(n):
    if isinstance(n, Raw): return str(n)
    if isinstance(n, str): return _esc_text(n)
    if n.tag == "#root": return "".join(serialize(c) for c in n.ch)
    if n.tag in VOID: return open_tag(n)
    return open_tag(n) + "".join(serialize(c) for c in n.ch) + f"</{n.tag}>"

def text_of(n):
    if isinstance(n, str): return "" if isinstance(n, Raw) else n
    return "".join(text_of(c) for c in n.ch)

def walk(n):
    yield n
    if isinstance(n, Node):
        for c in n.ch: yield from walk(c)

def find(n, pred):
    return next((x for x in walk(n) if isinstance(x, Node) and pred(x)), None)


# ---------------------------------------------------------------- segmentation
def norm(s): return re.sub(r"\s+", " ", s).strip()
def seg_id(src): return hashlib.sha1(src.encode("utf-8")).hexdigest()[:12]
def translatable(src): return bool(LETTER.search(PH.sub("", src)))

def _pure_inline(n):
    """Text, or an inline element whose content is inline; protected inline elements count (as opaque)."""
    if isinstance(n, Raw): return False
    if isinstance(n, str): return True
    return n.tag in INLINE and (n.get("translate") == "no" or all(_pure_inline(c) for c in n.ch))

def _is_run_member(c):
    return not (isinstance(c, Node) and c.tag in SKIP) and _pure_inline(c)

def _encode(run):
    """English run -> (placeholder string, element table). Protected/void elements become {n/}."""
    table, out = [], []
    def enc(nodes):
        for c in nodes:
            if isinstance(c, str): out.append(c.replace("{", "(").replace("}", ")")); continue
            table.append(c); i = len(table)
            if c.get("translate") == "no" or c.tag in VOID: out.append(f"{{{i}/}}")
            else: out.append(f"{{{i}}}"); enc(c.ch); out.append(f"{{/{i}}}")
    enc(run)
    return norm("".join(out)), table

def segments(root):
    """Yield ('run', parent, start, end, src, table) and ('attr', node, name, src)."""
    out = []
    def visit(n):
        if isinstance(n, str) or n.tag in SKIP or n.get("translate") == "no": return
        for k in ATTRS:
            v = n.get(k)
            if v and translatable(norm(v)): out.append(("attr", n, k, norm(v)))
        if n.tag == "meta":
            for kk in ("name", "property"):
                if (kk, n.get(kk)) in META_TRANSLATE and n.get("content") and translatable(norm(n.get("content"))):
                    out.append(("attr", n, "content", norm(n.get("content"))))
        i, ch = 0, n.ch
        while i < len(ch):
            if _is_run_member(ch[i]):
                j = i
                while j < len(ch) and _is_run_member(ch[j]): j += 1
                real = [c for c in ch[i:j] if not (isinstance(c, str) and not c.strip())]
                if len(real) == 1 and isinstance(real[0], Node) and real[0].tag not in VOID and real[0].get("translate") != "no":
                    visit(real[0])   # a run that is one wrapper element (e.g. a nav link) is segmented by its content
                else:
                    src, table = _encode(ch[i:j])
                    if translatable(src): out.append(("run", n, i, j, src, table))
                    for c in ch[i:j]:   # attributes on inline elements (e.g. img alt) inside the run
                        if isinstance(c, Node): _attrs_only(c)
                i = j
            else:
                visit(ch[i]); i += 1
    def _attrs_only(n):
        if n.get("translate") == "no": return
        for k in ATTRS:
            v = n.get(k)
            if v and translatable(norm(v)): out.append(("attr", n, k, norm(v)))
        for c in n.ch:
            if isinstance(c, Node): _attrs_only(c)
    visit(root)
    return out


# ---------------------------------------------------------------- translation application
class PlaceholderError(ValueError): pass

def check_placeholders(src, tgt):
    a = sorted(m.group(0) for m in PH.finditer(src)); b = sorted(m.group(0) for m in PH.finditer(tgt))
    if a != b: raise PlaceholderError(f"placeholders differ: {a} vs {b}")
    stack = []
    for m in PH.finditer(tgt):
        if m.group(1): stack.append(m.group(1))
        elif m.group(2):
            if not stack or stack.pop() != m.group(2): raise PlaceholderError("placeholders badly nested")
    if stack: raise PlaceholderError("unclosed placeholder")

def _rebuild(tgt, table, parent):
    nodes, stack, pos = [], [], 0
    def add(x): (stack[-1].ch if stack else nodes).append(x)
    for m in PH.finditer(tgt):
        if m.start() > pos: add(tgt[pos:m.start()])
        if m.group(1):
            src = table[int(m.group(1)) - 1]
            n = Node(src.tag, src.attrs, parent); add(n); stack.append(n)
        elif m.group(2): stack.pop()
        else: add(table[int(m.group(3)) - 1])
        pos = m.end()
    if pos < len(tgt): add(tgt[pos:])
    return nodes


# ---------------------------------------------------------------- configuration and catalogues
def load_json(p, default=None):
    try: return json.loads(pathlib.Path(p).read_text(encoding="utf-8"))
    except FileNotFoundError: return default

def languages():
    cfg = load_json(DATA / "languages.json", {})
    return cfg.get("languages", [])

def target_langs():
    """Languages with a translation catalogue that the build should generate."""
    return [l for l in languages() if l["code"] != "en" and (LOCALES / f'{l["code"]}.json').exists()]

def catalogue(code):
    c = load_json(LOCALES / f"{code}.json", {}) or {}
    return {k: v for k, v in c.get("segments", {}).items()}

def public_pages():
    return sorted(p.name for p in SITE.glob("*.html") if p.name not in EXCLUDED_PAGES)


def extract():
    """Write locales/source.json: every translatable English segment, with the pages using it."""
    segs = {}
    for name in public_pages():
        root = parse((SITE / name).read_text(encoding="utf-8"))
        for s in segments(root):
            src = s[4] if s[0] == "run" else s[3]
            e = segs.setdefault(seg_id(src), {"src": src, "pages": []})
            if name not in e["pages"]: e["pages"].append(name)
    js = js_strings()
    for k in js:
        e = segs.setdefault(seg_id(k), {"src": k, "pages": []})
        e.setdefault("js", True)
    LOCALES.mkdir(exist_ok=True)
    (LOCALES / "source.json").write_text(json.dumps(
        {"_note": "GENERATED by scripts/i18n.py extract from the English site. Do not edit; translate in locales/<lang>.json.",
         "segments": dict(sorted(segs.items(), key=lambda kv: (kv[1]["pages"][:1], kv[0])))},
        ensure_ascii=False, indent=1), encoding="utf-8")
    return segs


def js_strings():
    """User-visible strings used by the site's JavaScript (looked up via window.I18N at runtime)."""
    return load_json(LOCALES / "js-strings.json", {}).get("strings", [])


# ---------------------------------------------------------------- page generation
def page_url(code, name):
    if code == "en": return f"{BASE_URL}/{name}"
    return f"{BASE_URL}/{code}/" if name == "index.html" else f"{BASE_URL}/{code}/{name}"

def _is_local(u):
    return u and not re.match(r"^(?:[a-z][a-z0-9+.-]*:|//|#)", u, re.I)

def coverage():
    """{lang: {page: (translated, total, missing_ids)}} computed against the current English site."""
    langs = target_langs(); cats = {l["code"]: catalogue(l["code"]) for l in langs}
    cov = {l["code"]: {} for l in langs}
    for name in public_pages():
        root = parse((SITE / name).read_text(encoding="utf-8"))
        ids = {seg_id(s[4] if s[0] == "run" else s[3]) for s in segments(root)}
        for code, cat in cats.items():
            missing = sorted(i for i in ids if i not in cat or not cat[i].get("t"))
            cov[code][name] = (len(ids) - len(missing), len(ids), missing)
    return cov

def available(cov, code):
    """A language is offered only when every in-scope page is completely translated."""
    return bool(cov.get(code)) and all(t == n for t, n, _ in cov[code].values())

def build(verbose=False):
    langs = target_langs(); meta = {l["code"]: l for l in languages()}
    cats = {l["code"]: catalogue(l["code"]) for l in langs}
    cov = coverage()
    live = [l["code"] for l in langs if available(cov, l["code"])]
    import os, shutil
    if os.environ.get("I18N_PREVIEW"):   # local inspection of incomplete catalogues; never used by CI
        live = [l["code"] for l in langs]
    for l in languages():   # language folders are fully regenerated; never leave stale versions behind
        d = SITE / l["code"]
        if l["code"] != "en" and d.is_dir(): shutil.rmtree(d)
    jsdict = {c: {k: cats[c][seg_id(k)]["t"] for k in js_strings() if cats[c].get(seg_id(k), {}).get("t")} for c in live}
    errors, written = [], 0
    for name in public_pages():
        en_html = (SITE / name).read_text(encoding="utf-8")
        for code in ["en"] + live:
            root = parse(en_html)
            if code != "en":
                errors += _translate(root, cats[code], name, code)
                _relocate(root)
                _notice(root, cats[code], name)
                _ltr_islands(root, meta[code])
                _jsonld(root, cats[code], code)
                _js_i18n(root, jsdict[code])
            _head(root, name, code, live, meta)
            _switcher(root, name, code, live, meta, cats)
            out = SITE / name if code == "en" else SITE / code / name
            out.parent.mkdir(exist_ok=True)
            out.write_text(serialize(root), encoding="utf-8"); written += 1
    _sitemap(live)
    _report(cov, live)
    if verbose: print(f"i18n: {written} pages written; languages live: {', '.join(live) or 'none'}")
    return errors, live, cov

def _translate(root, cat, name, code):
    errs = []
    segs = segments(root)
    # attributes first: inline elements rebuilt from a translated run copy their (already translated) attributes
    for s in segs:
        if s[0] != "attr": continue
        _, node, k, src = s
        e = cat.get(seg_id(src))
        if e and e.get("t"): node.set(k, e["t"])
    # apply runs from the end of each parent so earlier indices stay valid
    for s in sorted([s for s in segs if s[0] == "run"], key=lambda s: (id(s[1]), -s[2])):
        _, parent, i, j, src, table = s
        e = cat.get(seg_id(src))
        if not e or not e.get("t"): continue
        try: check_placeholders(src, e["t"])
        except PlaceholderError as ex: errs.append(f"{code}/{name}: {seg_id(src)}: {ex}"); continue
        lead = " " if isinstance(parent.ch[i], str) and parent.ch[i][:1].isspace() else ""
        trail = " " if isinstance(parent.ch[j - 1], str) and parent.ch[j - 1][-1:].isspace() else ""
        new = _rebuild(e["t"], table, parent)
        parent.ch[i:j] = ([lead] if lead else []) + new + ([trail] if trail else [])
    return errs

def _relocate(root):
    """Pages in site/<lang>/: translated pages stay relative; shared assets move up one level."""
    pages = set(public_pages())
    for n in walk(root):
        if not isinstance(n, Node): continue
        for k in ("href", "src"):
            u = n.get(k)
            if not _is_local(u): continue
            path = u.split("#")[0].split("?")[0]
            if path in pages: continue
            n.set(k, "../" + u)
        if n.get("srcset"):
            n.set("srcset", ", ".join(("../" + p.strip()) if _is_local(p.strip()) else p.strip()
                                      for p in n.get("srcset").split(",")))

def _notice(root, cat, name):
    main = find(root, lambda n: n.tag == "main")
    if not main: return
    msg = "This page is a translation of the English original, prepared with AI assistance and checked with automated grammar, spelling and terminology tools. It has not yet been reviewed by a native speaker; the English version is authoritative."
    link_t = "Read this page in English"
    t = cat.get(seg_id(msg), {}).get("t") or msg
    lt = cat.get(seg_id(link_t), {}).get("t") or link_t
    p = Node("p", [("class", "i18n-notice"), ("role", "note")], main)
    a = Node("a", [("href", f"../{name}"), ("hreflang", "en")], p)
    a.ch = [lt]; p.ch = [t + " ", a]
    crumbs = next((k for k, c in enumerate(main.ch) if isinstance(c, Node) and c.get("class") == "crumbs"), -1)
    main.ch.insert(crumbs + 1, p)

def _ltr_islands(root, lang):
    """In right-to-left pages, protected Latin-script content (titles, names, venues) is isolated LTR."""
    if lang.get("dir") != "rtl": return
    rtl_letters = re.compile(r"[\u0590-\u08FF\uFB1D-\uFDFF\uFE70-\uFEFF]")
    for n in walk(root):
        if not isinstance(n, Node) or n.get("dir"): continue
        t = text_of(n)
        if n.get("translate") == "no" and re.search(r"[A-Za-z]", t):
            n.set("dir", "ltr"); n.set("lang", n.get("lang") or "en")
        elif n.tag in INLINE and re.search(r"[A-Za-z]", t) and not rtl_letters.search(t):
            n.set("dir", "ltr")   # Latin-only metadata (e.g. "— venue, 2026") reads as one left-to-right unit

def _jsonld(root, cat, code):
    for n in walk(root):
        if not (isinstance(n, Node) and n.tag == "script" and n.get("type") == "application/ld+json"): continue
        try: data = json.loads("".join(str(c) for c in n.ch))
        except ValueError: continue
        def fix(d):
            if isinstance(d, dict):
                if d.get("@type") == "BreadcrumbList":
                    for it in d.get("itemListElement", []):
                        t = cat.get(seg_id(it.get("name", "")), {}).get("t")
                        if t: it["name"] = t
                        u = it.get("item", "")
                        if u.startswith(BASE_URL + "/"): it["item"] = page_url(code, u[len(BASE_URL) + 1:])
                    d["inLanguage"] = code
                for v in d.values(): fix(v)
            elif isinstance(d, list):
                for v in d: fix(v)
        fix(data)
        n.ch = [Raw(json.dumps(data, ensure_ascii=False))]

def _js_i18n(root, strings):
    head = find(root, lambda n: n.tag == "head")
    if not head: return
    s = Node("script", [], head)
    s.ch = [Raw('window.I18N_BASE="../";window.I18N=' + json.dumps(strings, ensure_ascii=False).replace("</", "<\\/") + ";")]
    pos = next((k for k, c in enumerate(head.ch) if isinstance(c, Node) and c.tag == "link" and c.get("rel") == "stylesheet"), len(head.ch))
    head.ch.insert(pos, s)

def _head(root, name, code, live, meta):
    htm = find(root, lambda n: n.tag == "html")
    htm.set("lang", code); htm.set("dir", meta.get(code, {}).get("dir", "ltr"))
    head = find(root, lambda n: n.tag == "head")
    for n in list(head.ch):   # drop English-only alternates written by build.py; rebuilt below
        if isinstance(n, Node) and n.tag == "link" and n.get("rel") == "alternate" and n.get("hreflang"):
            head.ch.remove(n)
    canon = find(head, lambda n: n.tag == "link" and n.get("rel") == "canonical")
    me = page_url(code, name)
    if canon: canon.set("href", me)
    for n in list(head.ch):
        if isinstance(n, Node) and n.tag == "meta" and n.get("property") == "og:url": n.set("content", me)
        if isinstance(n, Node) and n.tag == "meta" and n.get("property") in ("og:locale", "og:locale:alternate"): head.ch.remove(n)
    anchor = head.ch.index(canon) + 1 if canon else len(head.ch)
    new = [Node("meta", [("property", "og:locale"), ("content", OG_LOCALE.get(code, code))], head)]
    new += [Node("meta", [("property", "og:locale:alternate"), ("content", OG_LOCALE.get(c, c))], head)
            for c in ["en"] + live if c != code]
    for c in ["en"] + live:
        new.append(Node("link", [("rel", "alternate"), ("hreflang", c), ("href", page_url(c, name))], head))
    new.append(Node("link", [("rel", "alternate"), ("hreflang", "x-default"), ("href", page_url("en", name))], head))
    head.ch[anchor:anchor] = new

def _switcher(root, name, code, live, meta, cats):
    det = find(root, lambda n: n.tag == "details" and n.get("class") == "langsel")
    if not det: return
    summ = find(det, lambda n: n.tag == "summary")
    native = meta.get(code, {}).get("native", code)
    label = "Language" if code == "en" else (cats[code].get(seg_id("Language"), {}).get("t") or "Language")
    summ.ch = [f"{label}: {native}" if code not in ("zh",) else f"{label}：{native}"]
    if code != "en":
        al = cats[code].get(seg_id("Choose language"), {}).get("t")
        if al: summ.set("aria-label", al)
    ul = find(det, lambda n: n.tag == "ul")
    ul.ch = []
    up = "" if code == "en" else "../"
    for c in ["en"] + live:
        href = (up + name) if c == "en" else (f"{up}{c}/{name}" if code == "en" else (name if c == code else f"../{c}/{name}"))
        li = Node("li", [], ul)
        a = Node("a", [("href", href), ("lang", c), ("hreflang", c), ("dir", meta.get(c, {}).get("dir", "ltr"))], li)
        if c == code: a.set("aria-current", "true")
        a.ch = [meta.get(c, {}).get("native", c)]; li.ch = [a]; ul.ch.append(li)
    note = find(det, lambda n: n.tag == "p" and n.get("class") == "langnote")
    if note:
        planned = [l["native"] for l in languages() if l["code"] != "en" and l["code"] not in live]
        txt = "English is the reference version."
        t = txt if code == "en" else (cats[code].get(seg_id(txt), {}).get("t") or txt)
        note.ch = [t]
        a = Node("a", [("href", f"{up}languages.html")], note)
        more = "Language availability"
        a.ch = [more if code == "en" else (cats[code].get(seg_id(more), {}).get("t") or more)]
        note.ch += [" ", a]

def _sitemap(live):
    pages = public_pages()
    out = ['<?xml version="1.0" encoding="utf-8"?>',
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">']
    today = datetime.date.today().isoformat()
    for name in pages:
        alts = "".join(f'<xhtml:link rel="alternate" hreflang="{c}" href="{page_url(c, name)}"/>' for c in ["en"] + live)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{page_url("en", name)}"/>'
        for c in ["en"] + live:
            out.append(f"<url><loc>{page_url(c, name)}</loc><lastmod>{today}</lastmod>{alts}</url>")
    out.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(out), encoding="utf-8")

def _report(cov, live):
    data = {"generated": datetime.date.today().isoformat(), "live": live, "languages": {}}
    for code, pages in cov.items():
        tr = sum(t for t, _, _ in pages.values()); tot = sum(n for _, n, _ in pages.values())
        data["languages"][code] = {"segments_translated": tr, "segments_total": tot,
            "pages_complete": sum(1 for t, n, _ in pages.values() if t == n), "pages_total": len(pages),
            "incomplete": {p: len(m) for p, (t, n, m) in pages.items() if m}}
    (SITE / "api").mkdir(exist_ok=True)
    (SITE / "api" / "translation-status.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def status():
    cov = coverage()
    for code, pages in cov.items():
        tr = sum(t for t, _, _ in pages.values()); tot = sum(n for _, n, _ in pages.values())
        done = sum(1 for t, n, _ in pages.values() if t == n)
        print(f"{code}: {tr}/{tot} segments, {done}/{len(pages)} pages complete{'  [LIVE]' if available(cov, code) else ''}")
    return cov

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "extract":
        s = extract(); print(f"{len(s)} source segments, {sum(len(v['src'].split()) for v in s.values())} words")
    elif cmd == "build":
        errs, live, _ = build(verbose=True); print("\n".join(errs)); sys.exit(1 if errs else 0)
    else: status()
