# End-to-end Travelers research release

Run `python3 scripts/build_travelers_release.py` from the repository root with the
Codex bundled Python runtime (or another Python environment with `reportlab`) and
Node.js plus `@oai/artifact-tool` available. The script rebuilds sourced history,
statement controls, operating movements, the dated Canadian disposal bridge and
forecast parity reference. It runs the company-neutral insurance harness, renders
the formula-linked workbook, creates the research PDF, and copies both final files
and their SHA-256 manifest to `examples/travelers/deliverables/`.

The workbook remains a **February 12, 2026 information-cutoff** historical model with
illustrative, constant-FY2025-perimeter operating scenarios. The PDF explicitly
separates those facts from the **April 16, 2026** sale evidence and includes no
price target, rating or recommendation. A complete issuer valuation report is still
gated by the transaction-adjusted gross/ceded premium, UPR, investment, earnings,
tax, capital and three-statement forecast schedules.

The output run directory under `output/` retains the harness manifest, input
snapshot, research JSON/Markdown, workbook previews and generated artifacts for
local audit. `examples/travelers/deliverables/release_manifest.json` records the
committed example artifacts, their SHA-256 hashes, the run ID, cutoff dates and
source/input fingerprint. Re-running creates a fresh run and overwrites the example
deliverables; review the diff before committing generated binaries.
