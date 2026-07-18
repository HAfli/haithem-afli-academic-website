#!/usr/bin/env python3
"""Generate downloads/Haithem_Afli_CV.pdf from the website's canonical structured data.
Requires reportlab. The HTML site and this PDF read the same JSON, so they cannot
contradict each other. Run standalone or via scripts/admin_sync.py --cv.
"""
import json, pathlib, datetime, sys, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"
OUTDIR = ROOT / "downloads"

def load(n): return json.load(open(D/n, encoding="utf-8"))

def main():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib import colors
    except ImportError:
        print("reportlab not installed; CV PDF not generated"); return 1
    profile = load("profile.json"); rinn = load("rinn.json"); projects = load("projects.json")
    pubs = load("publications.json"); sup = load("supervision.json"); service = load("service.json")
    teaching = load("teaching.json"); patent = load("patent.json")
    OUTDIR.mkdir(exist_ok=True)
    gen_date = datetime.date.today().isoformat()
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Title"], fontSize=18, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#5a5f66"), spaceAfter=8)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12, textColor=colors.HexColor("#0b5c8a"),
                        spaceBefore=10, spaceAfter=3)
    body = ParagraphStyle("body", parent=styles["Normal"], fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=body, fontSize=8.5, textColor=colors.HexColor("#5a5f66"))
    doc = SimpleDocTemplate(str(OUTDIR/"Haithem_Afli_CV.pdf"), pagesize=A4,
                            topMargin=16*mm, bottomMargin=14*mm, leftMargin=16*mm, rightMargin=16*mm,
                            title="Haithem Afli — Curriculum Vitae", author="Haithem Afli")
    E = []
    E.append(Paragraph("Dr Haithem Afli", h1))
    E.append(Paragraph(f"{profile['title']}, Munster Technological University, Cork, Ireland &nbsp;·&nbsp; "
                       f"{profile['email']} &nbsp;·&nbsp; ORCID {profile['orcid']}", sub))

    def section(title, items):
        E.append(Paragraph(title, h2))
        for it in items:
            E.append(Paragraph("• " + it, body))

    section("Current appointments and research leadership", [
        "Lecturer in Artificial Intelligence, Munster Technological University",
        "Institutional Co-Lead, Rinn Artificial Intelligence at MTU",
        "Deputy Theme Lead, Inclusive Language Model &amp; Translation Methods (Rinn AI)",
        "Principal Investigator, Rinn Artificial Intelligence",
        "Principal Investigator and MTU Lead, ADAPT Centre",
        "Founder and Lead, Human-Centred AI Research Group",
        "Chair, Computer Science Postgraduate Research Board",
        "Elected Member, MTU Academic Council",
        "External Expert, European Commission Research Executive Agency",
        "IEEE Senior Member",
    ])
    section("Education", [f"{e['degree']}, {e['institution']}, {e['year']}"
                         + (f" — {e['thesis']}" if e.get("thesis") else "") for e in profile["education"]])
    section("Research interests",
            [", ".join(t["name"] for t in profile["themes"]) + "."])
    E.append(Paragraph("Research centres and funding", h2))
    E.append(Paragraph(f"Rinn Artificial Intelligence — {rinn['funder']}; Institutional Co-Lead at MTU, Deputy Theme "
                       f"Lead, Principal Investigator. National centre award {rinn['facts']['national_investment']} "
                       f"(total centre award, not personally allocated).", body))
    def clean(s):  # strip internal verification wording from any public field
        s = re.sub(r"\s*\((?:exact title )?verification_pending\)", "", s or "")
        for term in ("verification_pending", "WITHHELD", "confirmation pending", "pending official confirmation"):
            s = s.replace(term, "")
        return re.sub(r"\s{2,}", " ", s).strip(" ;")
    for p in projects["national_projects"] + projects["eu_projects"]:
        if "WITHHELD" in p.get("note",""): continue
        amt = []
        if p.get("total"): amt.append(f"total {p['total']}")
        if p.get("mtu"): amt.append(f"MTU {p['mtu']}")
        role = clean(p.get("role",""))
        E.append(Paragraph(f"• {clean(p['name'])} — {clean(p.get('funder') or p.get('programme',''))}; {role}; "
                           f"{'; '.join(amt)}; {p.get('period','')}.", small))
    section("Teaching", [f"{p['name']} — {p['detail']} ({p['period']})" for p in teaching["programmes"]])
    E.append(Paragraph("Doctoral supervision (completed)", h2))
    for p in sup["doctoral_completed"]:
        E.append(Paragraph(f"• {p['name']} — {p['institution']}, {p['period']}; {p.get('role','')}; {p.get('area','')}.", small))
    E.append(Paragraph("Patent", h2))
    E.append(Paragraph(f"• {patent['patent']['title']} — {patent['patent']['number']}, filed {patent['patent']['filing_date']}.", small))
    E.append(Paragraph("Selected publications", h2))
    for p in pubs["publications"][:12]:
        authors = ", ".join(p["authors"])
        E.append(Paragraph(f"• {authors}. {p['title']}. <i>{p['venue']}</i>, {p['year']}.", small))
    E.append(Paragraph("Service (selected)", h2))
    for s in service["governance"][:4] + service["committees"][:3]:
        E.append(Paragraph(f"• {s}", small))
    E.append(Spacer(1, 8))
    E.append(Paragraph(f"Generated from the current website record on {gen_date}.", small))
    doc.build(E)
    print(f"CV PDF generated: downloads/Haithem_Afli_CV.pdf ({gen_date})")
    return 0

if __name__ == "__main__":
    sys.exit(main())
