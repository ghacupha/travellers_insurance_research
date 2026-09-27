# Travelers historical premiums and claims reserves: first sourced batch

This batch transcribes consolidated premium and P&C reserve tables for fiscal 2020–2025, with 2019 stock openings. The machine-readable source rows are `examples/travelers/historical_tables.json`; `historical_actuals.json` contains normalized facts, source URLs/hashes, SEC filing dates, and exact arithmetic checks. It is **partial history**, not an integrated statement model or price target. The 2024/2025 NWP and NEP values also agree with the separately dated issuer earnings release.

Amounts below are USD millions. Positive ceded premiums, unpaid recoverables, and claims paid are shown as positive magnitudes to subtract in the schedule. Negative prior-year incurred adjustments are favorable on the reserve-table basis.

| Fiscal year | GWP | Ceded written | NWP | Gross earned | Ceded earned | NEP | Gross UPR | Ceded UPR | Net UPR |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 opening | — | — | — | — | — | — | 14,604 | 689 | 13,915 |
| 2020 | 31,763 | 2,031 | 29,732 | 30,988 | 1,944 | 29,044 | 15,222 | 772 | 14,450 |
| 2021 | 34,244 | 2,285 | 31,959 | 33,009 | 2,154 | 30,855 | 16,469 | 902 | 15,567 |
| 2022 | 37,876 | 2,462 | 35,414 | 36,093 | 2,330 | 33,763 | 18,240 | 1,024 | 17,216 |
| 2023 | 42,972 | 2,771 | 40,201 | 40,410 | 2,649 | 37,761 | 20,872 | 1,150 | 19,722 |
| 2024 | 46,550 | 3,194 | 43,356 | 45,078 | 3,137 | 41,941 | 22,289 | 1,202 | 21,087 |
| 2025 | 47,730 | 3,343 | 44,387 | 47,152 | 3,238 | 43,914 | 22,431 | 1,283 | 21,148 |

| Fiscal year | Gross P&C reserve | Unpaid recoverables | Net P&C reserve | Current-year incurred | Signed prior-year incurred | Paid current/prior |
|---|---:|---:|---:|---:|---:|---:|
| 2019 opening | 51,836 | 8,035 | 43,801 | — | — | — |
| 2020 | 54,510 | 8,153 | 46,357 | 19,285 | −267 | 7,497 / 9,092 |
| 2021 | 56,897 | 8,209 | 48,688 | 20,698 | −484 | 8,401 / 9,470 |
| 2022 | 58,643 | 7,790 | 50,853 | 23,308 | −537 | 9,406 / 10,945 |
| 2023 | 61,621 | 7,817 | 53,804 | 26,159 | −38 | 10,852 / 12,424 |
| 2024 | 64,088 | 7,669 | 56,419 | 27,508 | −548 | 10,924 / 13,227 |
| 2025 | 67,643 | 7,797 | 59,846 | 28,051 | −939 | 10,606 / 13,307 |

The balance sheet reports **gross UPR as a liability** and ceded UPR separately as an asset; net UPR above is derived as gross less ceded. All six direct/assumed/ceded written and earned bridges match the disclosed NWP/NEP totals exactly. All six reserve rollforwards match their disclosed ending net and gross balances exactly. The 2020 rollforward includes a **separate $53 million accounting-adoption movement** before net beginning reserves. The 2025 P&C gross reserve also bridges to the balance sheet: 67,643 + 3 accident/health − 1,909 held for sale = 65,737. The 2025 held-for-sale disclosure separately identifies 514 of gross unearned premium reserves and 285 of reinsurance recoverables; neither is buried in the continuing-operation lines.

The net premium-earning bridge `NWP + opening net UPR − closing net UPR` does **not** equal reported NEP in any of the six years. The unexplained differences (NEP less that formula) are −153, +13, −2, +66, −50, and −412 for 2020–2025. The separately disclosed 2025 held-for-sale UPR is **gross**; its ceded counterpart is not separately disclosed, so it cannot be subtracted directly from this net bridge. FX, acquisition and presentation movements may contribute, but no amount has been assigned to those causes without a source. These differences are open issues, not balancing entries.

The FY2025 reserve-table prior-year adjustment of −939 and issuer-reported favorable prior-year development of −1,036 remain distinct. The issuer ratio bridge also retains its separate FY2025 loss-ratio discrepancy. Segment premium/reserve detail, gross/ceded UPR earning movements, paid reinsurance collections, other balance-sheet lines, and all three integrated statements remain to be extracted and reconciled.

Source tables were transcribed from the issuer's annual-report PDF copies; original Form 10-K filing dates were checked against [SEC EDGAR](https://www.sec.gov/edgar/browse/?CIK=0000086312). The 2025 [Form 10-K filing index](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/0000086312-26-000065-index.htm) confirms a 2026-02-12 filing date, and [SEC Schedule VI](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/R30.htm) independently shows 2023–2025 selected premium and reserve figures. The later annual-report PDF's posting date and exact parity of every transcribed row to the originally filed SEC HTML have **not** been independently certified; downstream research must retain that provenance boundary. All source PDFs and their SHA-256 hashes are listed in `examples/travelers/source_inventory.json`. Local PDF copies are cached under gitignored `data/travelers/annual_reports/`.

Rebuild the normalized history and updated coverage ledger from the repository root:

```sh
python3 scripts/build_historical.py
python3 scripts/build_model_spec.py \
  --inventory examples/travelers/source_inventory.json \
  --actuals examples/travelers/actuals.json \
  --history examples/travelers/historical_actuals.json \
  --output-dir docs/model_spec --as-of 2026-02-12
```

The Python checks reconcile disclosed totals and rollforwards without spreadsheet recalculation. The formula-linked workbook has not yet been rendered.
If the gitignored PDF and page-text caches are present, `python3 scripts/audit_historical_pages.py`
also checks their hashes and that each transcribed numeric token appears on its cited PDF page.
This is a lightweight page-location check, not SEC HTML row-level parity.
The subsequent [statement-control batch](STATEMENT_CONTROLS.md) ties the first
operating facts to selected income, balance-sheet and cash-flow lines.
