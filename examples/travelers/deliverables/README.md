# Travelers example research release

- `Travelers_Insurance_Operating_Model.xlsx`: formula-linked historical P&C workbook
  with 2020-2025 actuals, 2019 opening balances and illustrative 2026-2030 cases.
  Its information cutoff is 2026-02-12. The forecast excludes the Canadian sale.
- `Travelers_Equity_Research_Status.pdf`: source-led research status report with
  a historical annual-report source appendix. It separately labels April 16, 2026
  disposal evidence and provides no
  rating, price target or recommendation.
- `release_manifest.json`: source/input fingerprint, run ID, cutoff dates and SHA-256 hashes.

Reproduce from the repository root with
`python3 scripts/build_travelers_release.py` using Python with `reportlab`, Node.js,
and `@oai/artifact-tool`. See `docs/model_spec/E2E_RELEASE.md` for scope and gates.
