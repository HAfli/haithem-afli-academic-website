# Release 3.3 — Linguistic quality report

**Date of checks:** 2026-11-03.
**Material checked:** every translated segment in `locales/<code>.json` (1,182 segments per language), exported as plain text with placeholders replaced by spaces. Protected (`translate="no"`) content is not translated and was not checked.
**Translation method:** AI-assisted translation (Claude), followed by the automated checks below and manual review of every flagged item by the same AI. Corrections were applied to the catalogues and the build re-run.

> **No native-speaker review has taken place for any language.** The tools below detect spelling, grammar, typography and terminology problems; they do not certify fluency, register or meaning. Every translated page says so, and the English page is authoritative.

## 1. Tools actually used

| Tool | Version / source | Languages | How used |
|---|---|---|---|
| LanguageTool public API (`api.languagetool.org/v2/check`) | server 6.9-SNAPSHOT | fr, ar, ga-IE, es, pt-PT, zh-CN | All segments, chunked within the free-tier limits. Every match was triaged (§3). Arabic needed 8 KB requests because larger requests returned HTTP 500. |
| Hunspell dictionaries via `nspell` 2.1.5 | `dictionary-fr` 3.0.0 (Grammalecte), `dictionary-es` 4.0.0 (RLA-ES), `dictionary-tr` 2.0.0 (OpenOffice), `dictionary-ga` 3.0.0 (gaelspell), `dictionary-pt-pt` 2.0.0 (Natura, pt-PT) | fr, es, tr, ga (pt: see §5) | Out-of-vocabulary words, skipping tokens carried over from the English source (names, acronyms). |
| zeyrek (Python port of Zemberek morphology) | pip, 2026-11-03 | tr | Morphological analysis of every Turkish word type; unanalysable words were checked in TDK. |
| TDK Güncel Türkçe Sözlük (`sozluk.gov.tr/gts`) | online, 2026-11-03 | tr | 38 look-ups (`reports/release-3.3-linguistic-qa/tdk-lookups.json`). |
| Foclóir.ie (English–Irish dictionary) | online, 2026-11-03 | ga | 23 headword look-ups (`reports/release-3.3-linguistic-qa/focloir-lookups.json`). |
| Priberam Dicionário | online, 2026-11-03 | pt | Look-ups for flagged terms (arguência/arguente). |
| OpenCC (`opencc-python-reimplemented`, t2s) | pip | zh | Detection of Traditional characters in Simplified text. |
| jieba | pip | zh | Segmentation; out-of-lexicon multi-character words reviewed. |
| Rule-based script checks (written for this release) | — | ar, zh, fr | Arabic: Latin punctuation next to Arabic, Eastern digits, tatweel, spacing. Chinese: half-width punctuation, CJK–Latin spacing. French: spaces before high punctuation and guillemets. |
| Glossary consistency check (written for this release) | `data/translation_glossary.json` | all seven | Wherever the English source contains a glossary term (640 occurrences per language), the translation must use the preferred form or an accepted variant. Irish mutations, Arabic clitics and Turkish casing are normalised. |

### Tools not used, and why

| Tool | Reason |
|---|---|
| LanguageTool for Turkish | Not supported by LanguageTool. Turkish was checked with Hunspell, zeyrek and TDK instead. |
| LanguageTool desktop/offline (Java) | The installed Java runtime cannot run on this machine (Intel JDK on Apple Silicon); the public API was used instead. |
| téarma.ie (Irish terminology) | Protected by an ALTCHA bot challenge. Not bypassed, so not used. |
| IATE (EU terminology) | API returned HTTP 500 during the release. |
| RAE / DLE, Infopédia, Almaany | Returned HTTP 403 to automated requests. Not bypassed. |
| CAMeL Tools (Arabic morphology) | Requires a large separate data download; not installed. Arabic relied on LanguageTool plus the rule-based checks. |
| Hunspell Arabic dictionary | No packaged dictionary available for `nspell`. |
| TDK Yazım Kılavuzu API | The endpoint returns the web application, not data; abbreviations such as *örn.* could not be verified by tool. |

## 2. Results by language

| Language | Checks run | Raw flags | Real issues found and corrected | Notes |
|---|---|---|---|---|
| French | LanguageTool, Hunspell (fr), French typography check, glossary | LT 1,249 (first pass); Hunspell 56 → 27 types after fixes | Guillemet spacing in 52 segments (import bug: space before « removed); *co-responsable* → *coresponsable* (27), *Co-direction* → *Codirection*; language-pair hyphens (*anglais-irlandais*, *bhojpuri-hindi*, *irlandais-anglais*, 9); *23e* → *23ᵉ*; *intersites* → *entre sites*; heading *Langues multiples* → *Multilinguisme*. | Kept: *explicabilité*, *interprétabilité*, *signeur* (sign-language research term), *irlandophones*, *questions-réponses*; agreement flags on *IA … inclusive* were false positives. |
| Arabic | LanguageTool, rule-based checks, glossary | LT 2,321 (1,525 on carried-over names); 796 reviewed | None required. Arabic punctuation used throughout, Western digits, no stray spaces; tatweel only in لـ/فـ before Latin-script names (standard). Numeral and gender agreement flags (أحد الأزرار, أربعة التزامات, السجلات نفسها التي) checked and correct. | Remaining LT flags are prescriptive style preferences between equally standard MSA forms (رئيسي/رئيس, مشاريع/مشروعات, أبحاث/بحوث, من خلال), optional diacritics, and Hunspell gaps for names and established terms (الحوكمة, الجينوم). Glossary differences are morphological variants (مجموعة … البحثية, accusative باحثًا رئيسيًا), added to the glossary. |
| Turkish | Hunspell (tr), zeyrek, TDK, glossary | Hunspell 88 types; zeyrek 31 unanalysable types | *önyargı* → *ön yargı* (TDK); *mentorluk* → *rehberlik* (5, TDK); *öğretim portfolyosu* → *öğretim portföyü* (3, TDK); *İğnelemenin* → *Alaycılığın* (sarcasm, TDK). | The OpenOffice dictionary predates current TDK rules and wrongly flags *zekâ*, *resmî*, *dâhil*, *hâl* and words with dotted İ. zeyrek lacks some common verb forms (*yapılmış*, *gösterir*). Kept and flagged for review: *genomik*, *mikrobiyom*, *sosyoteknik*, *tokenizasyon*, *stokastik*, *nöral*, *algoritmik* (technical loanwords not in GTS). |
| Irish | LanguageTool (An Gramadóir rules), Hunspell (gaelspell), Foclóir.ie, glossary | LT 2,676 (1,555 on carried-over names); Hunspell 120 types | Keynote *príomhchaint* → *eochairchaint* (25 occurrences, mutations adjusted); sign language *teanga comharthaíochta* → *teanga na comharthaíochta* (12); lenition after slender plurals: *Cláir thaighde* (3), *thaifid mhaoirseachta*, *foláirimh fhaisnéise*, *Síntiúis fhéilire*; *chronologach* → *chroineolaíoch*; English *tokenization* given an Irish description; heading → *Ilteangachas*. | Most grammar flags were false positives on correct Caighdeán usage (*na Mumhan*, *ar fáil*, *ó gach*, *bhí sé*, *an tionscail*). Confirmed on Foclóir.ie: *príobháideachas*, *piarmheasúnaithe*, *ríomhaireachtúil*, *iardhochtúireachta*, *meantóireacht*. Compounds missing from gaelspell (*Príomhthaighdeoir*, *Comhcheannaire*) were left as they are. Not verifiable (no Foclóir entry, téarma.ie blocked): *leabuithe* (embeddings), *cascáideach* (cascaded), *ilmhódach* (multimodal), *géanómaíocht* (genomics). |
| Spanish | LanguageTool, Hunspell (es), glossary | LT 1,008 (869 on names); Hunspell 76 → 49 types | *preprint(s)* → *prepublicación/prepublicaciones* (6, FundéuRAE recommendation); *suscribibles* rephrased. | Valid words missing from the dictionaries: *pymes*, *mentoría*, *entregables*, *sénior*, *codirección*, *posdoctoral*, *microbioma*. The raya in *—publicaciones …—* is a correct aside. |
| Portuguese (pt-PT) | LanguageTool (pt-PT), glossary, Priberam | LT 1,110 (934 on names) | *IA fiável* → *IA de confiança* for "trustworthy" (7, glossary/EU usage; *fiável* kept for "reliable"); *newsletter* → *boletim informativo* (10, with articles adjusted); *Arguência* → *Arguição externa*; keynote *palestra principal* → *conferência plenária*. | Kept: *gestuante* (signer, LGP usage), *colíder*, *coinventor*, *cofundou* (AO 1990 prefix rules). |
| Chinese | LanguageTool (zh-CN), OpenCC, jieba, rule-based checks, glossary | LT 8; jieba 35 unknown words; 12 CJK–Latin spacing hits | 1 missing space between Chinese and Latin text. | No Traditional characters; no half-width punctuation inside Chinese text. LT matches (的/地, 与) and jieba unknowns were segmentation artefacts or correct usage; 博杰普尔语 (Bhojpuri) is the standard transliteration. |

### 2.1 Second LanguageTool pass (after corrections)

French was re-run after corrections: 1,236 matches, of which 1,032 are carried-over names; the remaining 204 were all reviewed as false positives or export artefacts (the acronym *TAL*, M€/k€, *questions-réponses*, the protected name *ADAPT–MTU HAI*, accepted technical terms). The Irish, Spanish, Portuguese, Chinese and Arabic runs used the corrected export (placeholders replaced by spaces); their corrections are listed in §2 and were verified in the catalogues.

## 3. Triage method

1. Spelling flags on tokens that also occur in the English source (names, acronyms, titles carried over verbatim) were set aside automatically. For example, 1,020 of 1,249 French and 1,555 of 2,676 Irish matches were names such as *Afli*, *MTU*, *ADAPT* or *Rinn*.
2. Flags caused by stripped markup were identified as artefacts. Placeholders were removed for checking, so " ." and " ," appear before protected titles and dates, and words from neighbouring elements run together. The checks were re-run after changing the export to replace each placeholder with a space; the raw catalogues contain no such spacing errors (verified by script for all languages).
3. Every remaining flag was read in context. A change was made only when a dictionary, terminology resource or grammar rule supported it; each change is logged with its reason in `reports/release-3.3-linguistic-qa/corrections.tsv` (52 correction rules, 123 segments) and applied identically to the catalogue and to the authoring files.

## 4. Glossary consistency (after corrections)

| | fr | ar | tr | ga | es | pt | zh |
|---|---|---|---|---|---|---|---|
| Occurrences checked | 640 | 640 | 640 | 640 | 640 | 640 | 640 |
| Not using a glossary form | 3 | 6 | 0 | 0 | 2 | 3 | 0 |

The remaining differences were all reviewed and are acceptable: noun forms of "multilingual" (*multilingüismo*, تعدد اللغات), protected English names (Human-Centred AI group, Rinn Artificial Intelligence, journal and course titles), and Chinese 主旨报告/主旨演讲 for keynote. The glossary gained the term *keynote* and accepted variants for Arabic *research group*, Turkish *evaluation* and Chinese *keynote*.

## 5. Limitations

- **No native-speaker review** for any language.
- **Turkish** has no grammar checker: LanguageTool does not support it. Only spelling and morphology were checked.
- **Arabic** has no dedicated spelling dictionary or morphological analyser; checking relied on LanguageTool and rule-based checks.
- **Portuguese Hunspell (Natura pt-PT):** the `nspell` run was stopped after 23 minutes of CPU without finishing (the dictionary's affix rules are very large). Portuguese spelling was checked by LanguageTool's pt-PT dictionary instead.
- **Irish terminology** for several NLP terms could not be confirmed: téarma.ie was blocked by a bot challenge and Foclóir.ie has no entries. These terms are listed above for native review.
- **Automated tools cannot assess** register, idiom or fidelity of meaning. Those require native review.

## 6. Recommended native-speaker review priorities

1. Pages with the most prose: About, Research Vision, Journey, Teaching, Innovation, Rinn AI.
2. Terminology listed as unconfirmed (Irish NLP terms, Turkish loanwords).
3. The Languages page and the translation notice, which make statements about the translation process.
