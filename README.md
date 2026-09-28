# Insurance research harness

The first-party source code is available under the [MIT License](LICENSE). To add
MIT SPDX headers to newly added code, run
`python3 scripts/apply_license_headers.py --write`; use `--check` to verify all
first-party source files have a header. Public filings and other third-party
source materials retain their respective owners' rights.

This is an independent research implementation using public issuer and SEC data;
it is not affiliated with or endorsed by The Travelers Companies, CFA Institute,
or Financial Modeling Institute. See the [research quality and reference review](docs/RESEARCH_QUALITY_REVIEW.md)
for the evidence boundary and prioritized improvements.

The target deliverable is a **formula-linked Excel model**,
customized for P&C: 2020–2025 actuals, 2019 opening balances and initial 2026–2030
forecasts. See the [execution plan](docs/EXECUTION_PLAN.md). A first formula-linked
[operating workbook](docs/model_spec/WORKBOOK_STATUS.md) now exists; integrated forecast
statements and valuation remain later work.

The [historical coverage matrix](docs/model_spec/HISTORICAL_COVERAGE.md),
[first sourced actuals batch](docs/model_spec/HISTORICAL_ACTUALS.md),
[statement controls](docs/model_spec/STATEMENT_CONTROLS.md),
[historical statement integration](docs/model_spec/HISTORICAL_INTEGRATION.md),
[Canadian disposal bridge](docs/model_spec/CANADIAN_DISPOSAL.md),
[operating cash/equity schedules](docs/model_spec/OPERATING_MOVEMENTS.md), and
[selected SEC row parity](docs/model_spec/SEC_PARITY.md), alongside the
[workbook specification](docs/model_spec/WORKBOOK_SPEC.md) define the current build stage.
They inventory seven issuer reports, reconcile consolidated premiums, claims reserves
and selected GAAP statement lines, and leave unearned-premium movement gaps explicit.
Regenerate with:

```sh
python3 scripts/build_historical.py
python3 scripts/build_statement_controls.py
python3 scripts/build_historical_integration.py
python3 scripts/build_canadian_disposal_bridge.py
python3 scripts/build_operating_movements.py
python3 scripts/build_operating_forecast_reference.py
python3 scripts/check_sec_parity.py
python3 scripts/audit_historical_pages.py  # optional when the PDF/page-text cache is present
python3 scripts/build_model_spec.py \
  --inventory examples/travelers/source_inventory.json \
  --actuals examples/travelers/actuals.json \
  --history examples/travelers/historical_actuals.json \
  --statement-controls examples/travelers/statement_controls.json \
  --operating-movements examples/travelers/operating_movements.json \
  --output-dir docs/model_spec --as-of 2026-02-12
```

Install the optional release dependencies and rebuild the formula-linked workbook
with Python:

```sh
python3 -m pip install -e '.[release,dev]'
python3 scripts/build_operating_workbook.py
```

This writes `output/travelers_operating_model.xlsx` with XlsxWriter. The build
checks all three cases against the independent Python forecast, verifies historical
statement controls, and tests that an assumption change reaches the output without
changing actuals. Excel formulas and cached Base-case results are saved together;
Excel recalculates the workbook when the scenario selector or an assumption changes.

For a Travelers research release (including the source-linked Excel model and a PDF
equity-research status report), run `python3 scripts/build_travelers_release.py`
with the optional release dependencies above. Final example files are copied into
`examples/travelers/deliverables/`. See [release workflow](docs/model_spec/E2E_RELEASE.md).
The insurance report is deliberately unrated until an integrated, transaction-adjusted
forecast and valuation are reconciled.

A Python-first research harness for **US GAAP property-and-casualty insurers**.
Travelers (TRV) is the first issuer profile. Identity and disclosure definitions are
configuration; SEC acquisition can be reused for other companies.

**This is a foundation, not a completed valuation.** It reproduces Travelers' 2024–2025
reported ratio bridge, reconciles six years of consolidated premium and claims-reserve
tables, reconciles audited equity and financing cash flows, and includes separately
labelled illustrative workbook scenarios plus Python Monte Carlo. Remaining historical
schedule bridges, integrated forecast statements, live market data and calibrated price targets remain
on the [roadmap](docs/ARCHITECTURE.md).

## Run offline

Python 3.9+; no external runtime dependencies. From this directory:

```sh
python3 -m bizplan.insurance run --config examples/travelers/run.json
```

The example uses an explicit **2026-02-12 information cutoff**, not current September
2026 data. Input paths resolve relative to config. Default output is a new directory
under `output/`. To name a run and include the synthetic schedule demo:

```sh
python3 scripts/build_insurance_model.py \
  --config examples/travelers/run.json \
  --demo examples/travelers/synthetic_projection.json \
  --output-dir output/insurance-demo
```

Existing run directories are rejected. Outputs:

- `manifest.json`: run status, stages, input/code hashes, dates and git revision.
- `inputs/`: snapshots of exact inputs.
- `research.json`: historical facts, provenance, ratios and optional synthetic scenarios.
- `research.md`: readable partial research, sources and limitations.

No LLM, subscription or market-data credential is required for offline runs.

## Fetch and normalize a company

Set `SEC_USER_AGENT` in your shell to your real application name and contact email.
Fetch stores content-addressed raw JSON and retrieval metadata:

```sh
python3 scripts/fetch_company.py --cik 0000086312 --cache-dir data/sec
```

Use the returned JSON path in a separate normalization step:

```sh
python3 -m bizplan.insurance normalize \
  --cik 0000086312 --snapshot data/sec/RETURNED_HASH.json \
  --as-of 2026-02-12 --years 2023 2024 2025 \
  --output output/statement-candidates.json
```

This selects five consolidated US GAAP statement concepts, not a complete model.
Selection filters exact annual dates, units and filing dates. Unresolved selections
are listed and return status 2. Candidates still require filing reconciliation and
are not automatically promoted into verified actuals. Company Facts omits custom and
segment disclosures; these need filing/IR adapters.

For another issuer, supply its CIK and create a profile/verified actuals file.
`standard_pc` uses already-reconciled loss/expense numerators; `travelers_reported`
applies Travelers' specific adjustments. Do not apply that adapter blindly elsewhere.
Fetching is company-neutral; models currently reject life/IFRS profiles. For Britam
or a company named Prudential, confirm legal issuer, business and accounting basis
before selecting or developing an engine.

## Tests and development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m behave
```

Optional installation provides a console command:

```sh
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/insurance-research --help
```

BDD covers premium earning, unpaid claims, reserve development, ratio adjustments and
information cutoffs. Unit tests cover source selection, reconciliations, analytics and
run behavior. Tests are offline; a live SEC request requires your contact identity.

The checked-in release has a reconciliation finding: its FY2025 loss numerator and
NEP calculate to 61.46%, while the displayed issuer loss ratio is 61.4%. Both values
are retained and flagged for filing-level investigation. The combined ratio agrees
at the issuer's displayed precision. The harness does not silently change either input.

## Layout

| Location | Purpose |
|---|---|
| `bizplan/insurance/company.py`, `adapters.py` | Issuer profiles and disclosure definitions |
| `sources.py` | SEC acquisition and annual fact selection |
| `schedules.py`, `projection.py` | Operating schedules and drivers |
| `analytics.py` | Regression, DDM primitive and seeded Monte Carlo |
| `pipeline.py`, `harness.py`, `cli.py` | Research, reproducible runs and CLI |
| `specification.py`, `coverage.py` | P&C metric/row contract and dated source-coverage ledger |
| `historical.py`, `scripts/build_historical.py` | Sourced premium/reserve normalization and strict arithmetic checks |
| `statement_controls.py`, `scripts/build_statement_controls.py` | Selected audited statement inputs and cross-statement checks |
| `examples/travelers/` | Historical slice, run profile and separate synthetic demo |
| `tests/`, `features/` | Unit/integration tests and executable Gherkin BDD |
| `docs/ARCHITECTURE.md`, `docs/RESEARCH_QUALITY_REVIEW.md` | Design, evidence boundaries and remaining validation gates |
