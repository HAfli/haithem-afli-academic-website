# Privacy Policy & Pre-Deployment Privacy Audit

## Objective
Maximise verified professional discoverability while minimising unnecessary personal exposure. The site is a professional research profile, not a personal dossier.

## Published (approved)
Professional institutional email (Haithem.Afli@mtu.ie), affiliation, verified scholarly profiles (ORCID, ACL Anthology, ADAPT, DBLP, Scholar, ACM, OpenReview, ResearchGate, LinkedIn, X), publications, projects with funding qualification, supervision (academically relevant fields only), teaching, service, talks, news.

## Never published
Personal email; private phone; home address; personal travel; family information; private calendar; health; personal finance; political/religious identity; student emails/IDs/grades/personal circumstances; confidential grant/review information; internal MTU documents; credentials/tokens/env vars; EXIF/location metadata; AI-generated imagery of Dr Afli; images copied from third-party sites.

## Pre-deployment privacy audit (run every deployment — enforced by tests/test_site.py)
Automated checks in the test suite scan generated output for: token/secret/key signatures, filesystem paths, unexpected email addresses (only the approved one permitted), withheld funding terms, and phone-like patterns. Manual checks before first deploy and after supervision/contact changes: no student personal data beyond approved academic fields; no hidden document metadata in any downloadable asset; image EXIF stripped (when a photo is added).

## Student data
Supervision records include only: name, degree/role, institution, period, project title, broad area, neutral supervision-role wording, and verified linked research outputs. No contact details, IDs, grades, or personal circumstances. Current employment shown only with a verification date, or omitted.

## Images
No photograph is published until Dr Afli provides an approved one; on receipt, EXIF is stripped, web-optimised versions are generated, alt text is written, the original is kept privately, and source/permission are documented (see image-policy.md).
