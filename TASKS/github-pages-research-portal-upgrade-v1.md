# GitHub Pages Research Portal Upgrade v1.1

## Scope

Repository: `sangziwang91-design/sangziwang91-design.github.io`
Related public repository: `sangziwang91-design/model-behavior-observatory`

Goal: maintain a static GitHub Pages research portal that links the homepage, public repository, Zenodo records, public-safe evidence packages, and calibration-first validation gate.

This is not a product build, not a private-core disclosure task, and not a manuscript-status page.

## Public Boundary

Allowed material:

- public methodology names and high-level definitions
- DOI records and public-safe summaries
- claim ceilings and validation limits
- public evidence-package schemas
- external validation gate plans
- repository navigation and public research positioning

Withheld material:

- internal mechanisms
- exact operational triggers
- hidden scoring settings
- private workspace links
- unpublished logs
- unpublished experiment details
- private automation chains

No manuscript status is displayed unless the status is current, explicitly authorized for public display, and dated.

## Execution Order

### Phase 0: Read and Snapshot

1. Read `index.html`.
2. Read `data/records.json`, `data/systems.json`, and all scripts under `scripts/`.
3. Read the related public repository README.
4. Confirm the working branch and remote state.
5. Do not modify private-core content or repository visibility.

### Phase 1: Canonical Data Foundation

1. Keep public record metadata in `data/records.json`.
2. Keep public-safe system map data in `data/systems.json`.
3. Do not duplicate record lists or system layers manually in `index.html`.
4. Run:

```bash
python scripts/validate_site_data.py
```

Expected:

```text
PASS: site data files are valid.
```

### Phase 2: Generated Static Output

Run:

```bash
python scripts/build_site.py
python scripts/build_site.py --check
```

Expected check output:

```text
PASS: generated site sections are current.
```

Generated sections:

- `PUBLIC_RECORDS`
- `SYSTEM_MAP`

### Phase 3: Public Evidence Package

The public portal must include `section id="evidence-package"` with:

- What is public
- What is withheld
- Evidence levels
- How to cite
- How to review
- Reproducible subset
- Claim ceiling

The evidence note must be linked as:

```text
evidence/full1000-pilot-note.html
```

### Phase 4: Calibration-First Validation Gate

The next validation gate is calibration-first:

- freeze a public-safe BRC coding manual and rule version
- preserve complete item-level scoring evidence and evidence spans
- document final-label rules and gate reasons
- retest BRC-1 / BRC-6 / BRC-7 boundary cases
- inspect rare BRC-2 / BRC-3 / BRC-5 samples
- run a limited blinded scoring check
- publish a small reproducible subset only after calibration issues are resolved

Do not present peer-review, benchmark, production, or manuscript-status claims without current authorized evidence.

### Phase 5: Site QA

Run:

```bash
python scripts/validate_site_data.py
python scripts/build_site.py --check
python scripts/check_records_parity.py
python scripts/check_site_links.py
python scripts/check_public_boundary.py
```

Expected outputs:

```text
PASS: site data files are valid.
PASS: generated site sections are current.
PASS: index public record block matches data/records.json.
PASS: all local site links resolve.
PASS: public boundary checks passed.
```

Also run:

```bash
git diff --check
```

## Done Definition

Do not mark complete unless all of the following pass:

1. `python scripts/validate_site_data.py`
2. `python scripts/build_site.py --check`
3. `python scripts/check_records_parity.py`
4. `python scripts/check_site_links.py`
5. `python scripts/check_public_boundary.py`
6. `git diff --check`
7. no stale manuscript claims in public files
8. no private component identifiers in public files
9. no local/private paths in public files
10. live GitHub Pages validation after merge

## Recommended Commit Messages

```text
Finalize canonical public data and boundary validation
Add public site integrity checks
```

## Handoff Summary

The endpoint is a static, public-safe research portal:

```text
GitHub Pages homepage
-> canonical public records
-> public-safe system map
-> evidence package
-> calibration-first validation gate
-> conservative claim boundary
```

The endpoint is not visual complexity. The endpoint is external readability, citation readiness, build reproducibility, and public-safe validation discipline.
