# Insurance research harness

Build a reusable US GAAP P&C research harness. Travelers is the first issuer; company
identity and disclosure adapters belong in configuration. Keep insurance schedules,
historical source mappings and report generation independent of unrelated models.

Read `docs/ARCHITECTURE.md`, `docs/EXECUTION_PLAN.md` and
`docs/SOURCE_COVERAGE_AND_LIMITATIONS.md` before changing calculations or research outputs.
Keep scripts thin and reusable calculations in `bizplan/insurance`. Preserve source
URL, filing or publication date, fiscal period, unit and table or tag locator for
every factual input. Distinguish disclosed, derived, modeled and synthetic values;
never turn missing data into zero.

Build operating schedules before integrated statements. Reconcile balances and
cash movements without plugs. A failing required check blocks a valuation, rating
or price target. Document information cutoffs, forecast assumptions and limitations.
Use unit tests for accounting identities and failure boundaries, and executable BDD
scenarios for business behavior. Keep deterministic tests offline; SEC acquisition
requires a real `SEC_USER_AGENT` application/contact identity.

Do not commit local caches, credentials, conversation transcripts, third-party
source PDFs or teaching workbooks. Keep commits coherent and review generated
artifacts before publication.
Describe observable behavior, source provenance and limitations in documentation
and code comments; avoid promotional claims or statements about the author.

First-party source code uses the MIT SPDX header in `LICENSE`. Run
`python3 scripts/apply_license_headers.py --write` for new source files and
`python3 scripts/apply_license_headers.py --check` before committing. Do not
apply the project license header to third-party source material.
