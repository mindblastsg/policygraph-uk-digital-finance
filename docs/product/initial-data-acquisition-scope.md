# Initial data acquisition scope

## Decision

The first real-data increment will build a **bounded, reviewable UK digital-finance corpus**, not crawl the entire UK statute book. It will test whether PolicyGraph can acquire, normalise and cite representative primary material before the project invests in broad crawling or semantic answer generation.

The discovery ceiling is **250 candidate records** and the publishable corpus target is **60–100 accepted documents**. Every accepted document must have an authoritative URL, publisher, publication or made date, retrieval timestamp, content hash, rights decision, topic labels and explicit policy status.

## Research questions

1. Can the open adapter contract handle legislation and policy publications without publisher-specific logic leaking into the graph?
2. Can reviewers recover the exact source passage for every material event and relationship?
3. Does the corpus cover all five launch topics well enough to construct representative benchmark questions?
4. Which source formats, amendments and attachments create the largest review burden?

## Included subject matter

- Distributed ledger technology and wholesale-market infrastructure.
- Tokenisation and digital securities.
- Digital Securities Sandbox legislation, consultations and implementation material.
- Fiat-backed stablecoins, payments regulation and relevant prudential material.
- UK cryptoasset regulation, financial promotions and the regulatory perimeter.

Discovery uses the terms `digital securities sandbox`, `distributed ledger`, `DLT`, `tokenisation`, `tokenization`, `stablecoin`, `cryptoasset`, `crypto asset`, `digital asset` and `financial promotions`. Terms identify candidates; they do not prove relevance.

The main date window is **1 January 2020 onward**. Earlier instruments are included only when an accepted source cites them as foundational and a reviewer records the reason.

## Source tiers

| Tier | Initial source | Acquisition route | Scope rule |
| --- | --- | --- | --- |
| 1 | legislation.gov.uk | Structured XML/HTML representations and stable instrument identifiers | UK Public General Acts and UK Statutory Instruments returned by the topic discovery set, including enacted and revised representations where available |
| 1 | GOV.UK / HM Treasury | GOV.UK Content API by reviewed content path | Consultations, responses, policy papers, speeches and implementation updates directly related to an included topic |
| 2 | Financial Conduct Authority | Authenticated Handbook API after account/terms review; reviewed seed-list adapter for other FCA publications | Current/future Handbook content plus consultations, policy statements and discussion papers directly related to the included topics; do not infer historical Handbook coverage from the API |
| 2 | Bank of England and PRA | Publisher adapter after robots, terms and format review | Sandbox, stablecoin, wholesale-settlement and prudential publications selected from a reviewed seed list |
| 3 | UK Parliament | Metadata and documents referenced by accepted primary sources | Bills, committee material and explanatory evidence needed to connect an included policy chronology |

The GOV.UK Content API is preferred to HTML scraping because it returns published GOV.UK content and metadata as structured JSON, requires no authentication and documents a maximum rate of 10 requests per second. PolicyGraph will cap itself at **2 requests per second** for GOV.UK and **1 request per second** elsewhere, with exponential backoff, caching and conditional requests.

## Explicit exclusions

- A complete historical mirror of UK legislation.
- Case law, legal commentary, news reporting, social media and paywalled research.
- Personal data, consultation respondent submissions and unpublished material.
- Automated OCR of scanned attachments in the first increment.
- Inferred commencement, legal effect or current-law status without explicit source evidence.
- Autonomous AI publication, unsupervised graph edges, general-purpose chat and legal advice.
- Live network access in pull-request CI.

## Acquisition and provenance contract

1. **Discover:** produce candidate metadata only; do not automatically publish candidates.
2. **Review:** confirm topical relevance, authoritative publisher, rights basis, document status and canonical URL.
3. **Fetch:** allow only approved HTTPS hosts; cap redirects, response size and content types; record final URL, retrieval time, response metadata and SHA-256.
4. **Parse:** preserve instrument, part, section, regulation, heading, paragraph and attachment boundaries where the source exposes them.
5. **Normalise:** emit the versioned PolicyGraph document schema without overwriting the source representation.
6. **Extract:** create proposed claims, entities, events and relationships with exact evidence locators.
7. **Review and publish:** require human acceptance for material relationships and policy status before the graph build.

Full retrieved files remain in a local or managed cache unless their reuse terms and repository-size impact have been approved. The public repository receives the registry, hashes, transformation code, small rights-cleared fixtures, review decisions and generated graph—not an indiscriminate document dump.

OGL material must retain the specified source acknowledgement and a link to the applicable licence. A source-specific decision is required for content containing third-party rights or governed by publisher terms; Crown-body status must not be treated as proof that every attachment is reusable.

## Deliverables

- Reviewed seed registry and machine-readable acquisition manifest.
- Legislation and GOV.UK adapters with deterministic contract fixtures.
- Source-specific decision records for FCA, Bank of England/PRA and Parliament.
- Fetch ledger containing canonical/final URLs, timestamps, hashes, status and failure reason.
- Normalised real-document sample with provision-level evidence locators.
- Human-review queue and an accepted/rejected decision log.
- Corpus coverage report by publisher, topic, year, format and policy status.
- Held-back evaluation set and benchmark-question specification.

## Release gates

| Gate | Threshold |
| --- | --- |
| Accepted corpus | 60–100 documents, at least three publishers, all five topics represented |
| Provenance completeness | 100% of accepted records have source, retrieval, hash, rights and locator metadata |
| Retrieval repeatability | At least 95% of unchanged reviewed URLs refetch or resolve from the content-addressed cache |
| Citation agreement | At least 90% on a held-back reviewer-authored sample |
| Unsupported material relationships | Zero |
| Status-critical errors | Zero |
| Duplicate rate after canonicalisation | Under 2% of accepted documents |
| Reviewability | Every failure and rejection has a stable reason code; no silent drops |

These are engineering and corpus-quality gates, not proof of user value. The five moderated analyst sessions in the evaluation plan remain a separate product gate.

## Semantic-research handoff

Semantic work begins only after the accepted corpus and held-back evidence keys exist. The first retrieval experiment will compare keyword, embedding and hybrid retrieval over the same provision-level chunks using **25 reviewer-authored questions** across the five topics. It will report recall at 10, citation agreement, unsupported synthesis and latency; no generated answer will be exposed publicly unless it can return exact source locators and pass the existing zero-unsupported-relationship gate.

## Expansion decision

Expand beyond the 100-document ceiling only if the adapters are repeatable, rights decisions are recorded, the held-back gates pass and the coverage report identifies a user-relevant gap. A full legislation.gov.uk mirror, cross-domain semantic index and automated refresh service are separate epics requiring storage, update, amendment-version and operating-cost decisions.

## Authoritative references

- [GOV.UK Content API overview](https://content-api.publishing.service.gov.uk/)
- [GOV.UK Content API reference](https://content-api.publishing.service.gov.uk/reference.html)
- [legislation.gov.uk developer guidance](https://www.legislation.gov.uk/developer)
- [FCA Handbook API launch and access conditions](https://handbook.fca.org.uk/latest-news/news-details/8e0653c7-1376-44b8-8bf1-9b41130dc50c)
- [UK Parliament developer hub](https://developer.parliament.uk/)
- [UK Government Licensing Framework](https://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/)
- [Open Government Licence](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
