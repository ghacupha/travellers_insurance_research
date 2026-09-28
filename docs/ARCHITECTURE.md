# Insurance research harness — Travelers as the first issuer

## Design and boundaries

The controlling delivery plan is `docs/EXECUTION_PLAN.md`: 2020–2025 actuals,
2019 opening balances, 2026–2030 initial forecasts, and a required formula-linked
FMI-style workbook. A first source-linked operating workbook now exists; integrated
statements and valuation remain open. JSON/Markdown are supporting outputs. The
project's own workbook specification governs layout; do not imply FMI certification.

Issuer identity (name/ticker/CIK), business model, accounting basis and ratio adapter
are configuration in `examples/<issuer>/run.json`. `fetch_company.py` accepts any CIK.
Company Facts acquisition has no Travelers constants. `adapters.py` isolates the
Travelers ratio bridge; `standard_pc` accepts reconciled numerator inputs from other
P&C disclosures. A synthetic second issuer is tested. Life/IFRS model profiles fail
explicitly until their schedules exist; SEC acquisition itself is not P&C-specific.

Python is the calculation authority. Acquisition, normalization, schedules, analytics
and rendering are separate modules; scripts only parse/delegate. JSON config is data,
not executable code. Insurance modules depend only on this package and standard
runtime dependencies.

The dependency order is:

1. Raw SEC/IR documents and dated market observations, cached with hashes.
2. Normalized facts with entity, period start/end, unit, source, filing/publication date,
   table or tag locator, and disclosed/derived/modeled status.
3. Premium, claims/reserves, reinsurance, DAC/expenses, investments, tax and capital schedules.
4. Integrated income statement, balance sheet, cash flow and reconciliation checks.
5. Scenarios, regression, Monte Carlo, equity valuation and sensitivities.
6. Validated outputs -> required formula-linked Excel model and supporting research reports.

Today `sources.py` handles SEC snapshots and annual consolidated selection;
`schedules.py` holds pure functions; `projection.py` applies annual operating drivers;
`analytics.py` holds small reusable analytical primitives; `pipeline.py` validates
verified historical ratios and renders partial research. `harness.py` owns run
identity/configuration/manifests; `cli.py` exposes commands. `operating_movements.py`
validates audited cash/equity flows and leaves stock bridge differences visible.
`historical_integration.py` validates all disclosed consolidated balance-sheet lines
against audited totals and the accounting equation for 2019–2025. The workbook links
these inputs and historical GAAP income formulas to the Sources ledger. The January
2026 Canadian divestiture is a forecast-perimeter gate: current scenarios are
constant-FY2025-perimeter illustrations, not transaction-adjusted projections.
`disposal.py` preserves separate February 12 and April 16 evidence views. The later
view supplies net reserves disposed and FY2025 divested net premiums but does not
alter the earlier workbook. Gross/ceded premium, UPR, sale gain and tax effects
remain forecast-integration gates.
The formula workbook renders linked actuals and checks its illustrative formulas
against `projection.py` for all three cases. New renderers must consume validated
facts and compare calculation outputs with Python, never invent source values.
No generic plugin registry is needed yet.

## Accounting conventions

- USD millions; ratios are fractions; shares will be in millions and per-share values USD.
- GWP = direct + assumed written premium. NWP = GWP - ceded written premium.
- Gross/ceded earned = written + opening UPR - closing UPR + other UPR changes.
  NEP = gross earned - ceded earned. Other changes explicitly capture FX/transfers.
- Net reserve = gross reserve - recoverables on **unpaid** claims. Recoverables on
  paid claims and prepaid reinsurance are separate assets, not offsets to reserves.
- Net incurred = current accident-year incurred + signed prior-year development.
  Favorable development is negative. Current catastrophe losses are part of current
  incurred, so do not add them again. Closing net reserve = opening net + incurred
  - paid + FX/acquisition/other changes. Policyholder dividends are excluded from
  reserve incurred and separately removed from Travelers' claims-line ratio bridge.
- Travelers' reported loss and expense ratios use NEP and issuer-specific fee
  allocations. Statutory expense ratios use a different denominator. Underlying
  combined ratio removes catastrophe and signed development impacts.
- Investment income is separate from realized gains and OCI. The initial kernel uses
  a net yield on average carrying assets; detailed fixed-income amortized-cost yields,
  fair values, maturities, reinvestment, alternatives and credit losses are next.
- GAAP common equity, statutory surplus and risk-based capital are different measures.
  Opening equity + net income + OCI - dividends - repurchases + issuance + other
  changes = closing equity. Never substitute bank Tier 1 capital for equity.

## Historical mapping and provenance

Primary filing target: [2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/trv-20251231.htm),
accession `0000086312-26-000065`, filed 2026-02-12; CIK `0000086312`.
Selected SEC premium and reserve rows have been compared with the original HTML;
remaining rows, including most 2020–2021 lines, have not. Do not label those
pending mappings verified.

The checked-in 2024/2025 inputs are manually transcribed from the annual columns of
the [issuer's FY2025 earnings release](https://investor.travelers.com/newsroom/press-releases/news-details/2026/Travelers-Reports-Excellent-Fourth-Quarter-and-Full-Year-Results/default.aspx),
published 2026-01-21. Locators identify its consolidated results and combined-ratio
reconciliation. Source publication date gates use in a backtest. These comparative
2024 figures cannot be used at a 2024 information cutoff. FY2025 loss-ratio amounts
calculate to 61.46% versus the issuer's displayed 61.4%; this is flagged as unresolved,
not explained away as rounding. Combined ratio agrees at displayed precision.

| Schedule | Primary disclosure to map | State |
|---|---|---|
| NWP, NEP, ratios | IR annual consolidated/combined-ratio reconciliation | 2024–2025 loaded; combined ratio agrees; 2025 loss-ratio display difference flagged |
| GWP/ceded, gross/net earned, UPR | 10-K segment MD&A and reinsurance notes | Mapping/extraction pending |
| Paid/incurred, current/prior accident years, gross/net reserves | 10-K claims-reserve rollforward and development disclosures | Kernel implemented; facts pending |
| Paid/unpaid recoverables, prepaid reinsurance | Reinsurance and balance-sheet notes | Separate mapping required |
| DAC and expenses | GAAP income statement, DAC policy and ratio bridge | Ratio bridge loaded; DAC rollforward pending |
| Investments and yield | Investment note, MD&A income/yield tables | Kernel implemented; asset-class data pending |
| Equity/OCI/shares/buybacks | Equity statement, EPS note, repurchase tables | Equity kernel; historical reconciliation pending |
| Statements | Consolidated GAAP statements and cash-flow notes | SEC standard-tag candidates only |
| Statutory capital | Statutory statements and insurance capital disclosures | Pending; no CBK/Basel substitution |
| Price, benchmark, peers | Dated public market series with split/dividend treatment | Provider adapter pending |

[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
limits Company Facts to standard taxonomy, entity-wide facts. It cannot replace
custom Travelers tags or segment tables. The selector filters exact period dates,
units, annual forms and filing date, retains accession, selects the latest known
restatement and rejects ambiguous same-date values. Missing values are unresolved,
never zero. The five standard mappings are candidates until verified against filings.

## Incremental delivery plan

**Implemented modules:** provenance-bearing ratio actuals, premium/reserve/portfolio/
equity kernels, illustrative operating projections, scenario/seeded simulation,
regression and DDM primitives, JSON/Markdown research, unit tests and Gherkin BDD.

**Current planning contract:** `docs/model_spec/WORKBOOK_SPEC.md` and
`HISTORICAL_COVERAGE.md` index the 2019–2025 issuer reports, dynamic metric rows and
unresolved data. Table locations are not validated values.

`HISTORICAL_ACTUALS.md` now documents the first sourced six-year consolidated premium
and reserve batch, including its exact checks, 2019 openings and unresolved UPR
movements. It is not yet an integrated model or a fully SEC-verified dataset.
`STATEMENT_CONTROLS.md` adds selected income, balance-sheet and cash-flow totals
with 2019 opening stocks and explicit cash/reclassification checks.

**Next acceptance milestone:** verify original filing dates, fetch/cache full 10-K and supplements; reconcile at least
six historical years (2020–2025), 2019 opening balances, all three reportable segments,
premium earning and reserves, following `docs/EXECUTION_PLAN.md`.
Add schemas for per-fact provenance on every future input. Add 10-Q/YTD-aware updates,
explicit original versus restated basis, FX, acquisitions/divestitures and held-for-sale
bridges. The current two-year slice and annual-only selector are intentionally narrower.

**Then statements:** expenses/DAC/receivables, reinsurance cash collection, debt/interest,
tax/deferred tax, investments/OCI, shares/dividends/buybacks. Carry all opening balances
from reconciled actuals. Derive cash via CFO/CFI/CFF; test both cash movement and balance
sheet equality without plugs. Verify equity/OCI, EPS and portfolio rollforwards.

**Then valuation/report:** calibrated forecasts; residual income with clean-surplus/OCI
adjustments; dividends plus explicit buyback/share-count treatment; insurer P/B versus
ROE regression with peer dates, diagnostics and sensitivity. Align valuation dates and
discount terminal comparables. Add a market-provider interface before beta estimation.
Simulation must eventually calibrate catastrophe severity, inflation, reserve uncertainty
and dependence; the existing truncated-normal demo is not a catastrophe risk model.

No arbitrary valuation blend or Buy/Hold/Sell label is produced by this increment.
The current DDM helper is a tested primitive, not a calibrated TRV price target.

## Development and verification

Use unit tests for accounting identities, boundary failures, source selection and
reproducibility. Use `features/*.feature` for business-readable Given/When/Then
acceptance behavior. Add a failing scenario for a changed business rule before changing
the engine. Keep deterministic tests offline; live-provider checks are separate.

Legacy bank files and old report SOPs remain reference material during replacement.
Only renderer styling may be reused directly. Once a full insurance reporting path
exists, remove the obsolete bank subtree and SOPs in a separate, reviewable commit.
