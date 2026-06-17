# Codex Task Pack · GitHub Pages Research Portal Upgrade v1.0

## Scope

Repository: `sangziwang91-design/sangziwang91-design.github.io`  
Related repository: `sangziwang91-design/model-behavior-observatory`

Goal: upgrade the existing GitHub Pages personal site into a public research portal that links the homepage, GitHub repository, Zenodo records, public-safe evidence packages, and next validation gate.

This is not a product build and not a private-core disclosure task.

---

## Current Verified State

- The site is currently a single-page `index.html`.
- The site already contains navigation for Research, Records, Architecture, Stack, Status, Scope, Disclosure, Claim Ceiling, and Contact.
- The site already lists 10 Zenodo public records and one manuscript submission-status note.
- The site already distinguishes public methodology, semi-public runtime evidence, and private runtime core.
- New starter data files are expected in this upgrade path:
  - `data/records.json`
  - `data/systems.json`
  - `scripts/validate_site_data.py`

---

## Public Boundary

Do not publish internal mechanisms, exact operational triggers, hidden scoring settings, private workspace links, raw private logs, unpublished experiment details, or private automation chains.

Allowed material:

- public methodology names and high-level definitions
- DOI records and public-safe summaries
- claim ceilings and validation limits
- public evidence-package schemas
- external validation gate plans
- repository navigation and public research positioning

---

## Execution Order

### Phase 0 — Read and Snapshot

1. Read `index.html`.
2. Read `data/records.json`, `data/systems.json`, and `scripts/validate_site_data.py` if present.
3. Read related main repository README: `sangziwang91-design/model-behavior-observatory`.
4. Create a working branch: `site-portal-v1`.
5. Do not modify protected runtime/private-core content.

### Phase 1 — Validate Data Foundation

Run:

```bash
python scripts/validate_site_data.py
```

Expected:

```text
PASS: site data files are valid.
```

If it fails, fix only the data field issue. Do not add private details to satisfy validation.

### Phase 2 — Refactor Site Without Overbuilding

Preferred implementation:

- Keep the site static and GitHub Pages compatible.
- Keep `index.html` as the public entry.
- Add modular public data loading only if it remains simple and readable.
- Do not introduce React/Vite/Next.js unless explicitly approved.
- Avoid dependencies.

Required sections:

1. Hero
2. Research Focus
3. Public Records
4. Research Stack
5. Validation Gate
6. Public Evidence Package
7. Disclosure Boundary
8. Claim Ceiling
9. Contact / Citation

### Phase 3 — Add Public Evidence Package Page or Section

Add a section or page named `Public Evidence Package`.

Required content:

- What can be shared
- What is withheld
- How public records should be cited
- What evidence level each asset supports
- How to use the materials for external review
- Claim ceiling

Do not include private task packs, prompt chains, hidden gates, or raw logs.

### Phase 4 — Add Validation Gate Page or Section

Add a section or page named `Validation Gate`.

Required content:

- Current evidence
- Missing external validation
- Pilot design
- Rater protocol
- Minimum reproducible subset
- Report output
- Acceptance criteria

Canonical gate:

```text
N ≥ 20 real-model multi-turn pilot
2–3 external raters
blinded scoring
public-safe benchmark subset
updated technical report
```

### Phase 5 — Add Lightweight Site QA

Add or update only low-risk tooling:

- Keep `scripts/validate_site_data.py`.
- Optionally add `scripts/check_site_links.py`.
- Optionally add `.github/workflows/site-check.yml` only after local validation passes.

Do not add deployment secrets or external service credentials.

### Phase 6 — Final Test

Run:

```bash
python scripts/validate_site_data.py
```

If a link checker is added:

```bash
python scripts/check_site_links.py
```

Manual checks:

- Page renders locally.
- Mobile width works.
- Navigation anchors work.
- No private details leaked.
- Claim ceiling remains conservative.
- Submission language does not imply acceptance.
- Zenodo records are described as timestamped public deposits; no peer-review implication.

---

## Done Definition

Deliver a final report with:

1. Files changed
2. Validation commands and outputs
3. Public/private boundary check result
4. Any unresolved limitations
5. Next single action

Do not mark complete unless `scripts/validate_site_data.py` passes.

---

## Recommended Commit Message

```text
Upgrade GitHub Pages research portal foundation
```

---

## Handoff Summary

This task should convert the existing page from a static self-description into a maintainable public research portal:

```text
GitHub Pages homepage
→ public record index
→ research stack map
→ evidence package
→ validation gate
→ conservative claim boundary
```

The endpoint is not visual complexity. The endpoint is external readability, citation readiness, and public-safe validation discipline.
