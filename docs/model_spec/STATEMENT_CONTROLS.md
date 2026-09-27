# Travelers historical statement controls

This is the second historical batch: selected consolidated audited statement lines for 2020–2025 and 2019 opening balance-sheet stocks. `examples/travelers/statement_control_tables.json` holds the source transcriptions; `statement_controls.json` holds 266 normalized facts with PDF page, source hash and SEC filing-date lineage. It is a statement **control layer**, not a complete three-statement workbook or a portfolio rollforward. The [first premium/reserve batch](HISTORICAL_ACTUALS.md) remains the source for operating schedules.

All amounts are USD millions. Cash-flow investing and financing uses the signed statement convention.

| Year | Total investments | Total assets | Total liabilities | Common equity | Net investment income | Net income | CFO | Closing cash |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2019 opening | 77,884 | 110,122 | 84,179 | 25,943 | — | — | — | 494 |
| 2020 | 84,423 | 116,764 | 87,563 | 29,201 | 2,227 | 2,697 | 6,519 | 721 |
| 2021 | 87,375 | 120,466 | 91,579 | 28,887 | 3,033 | 3,662 | 7,274 | 761 |
| 2022 | 80,454 | 115,717 | 94,157 | 21,560 | 2,562 | 2,842 | 6,465 | 799 |
| 2023 | 88,810 | 125,978 | 101,057 | 24,921 | 2,922 | 2,991 | 7,711 | 650 |
| 2024 | 94,223 | 133,189 | 105,325 | 27,864 | 3,590 | 4,999 | 9,074 | 699 |
| 2025 | 101,182 | 143,708 | 110,814 | 32,894 | 3,959 | 6,288 | 10,606 | 842 |

The 89 zero-residual checks cover investment asset-class sums; assets = liabilities + equity; income revenue, expenses, tax and profit; NEP against the premium schedule; cash-flow section sums; cash opening/closing versus consecutive balance sheets; and overlapping UPR, DAC and reserve balances. The 2025 cash-flow statement reports a 314 increase before removing **171 of cash classified as held for sale**: 699 opening + 10,606 CFO − 7,652 CFI − 2,663 CFF + 23 FX − 171 reclassification = 842 closing. Treating the 171 as a cash expense would distort operations.

The balance-sheet investment total is the sum of fair-value fixed maturities, equity securities, real estate investments, short-term securities and other investments. Fixed-maturity amortized cost is retained as a separate measurement basis and is not added to the fair-value total. The 2025 held-for-sale business also has assets outside continuing-operation investment and insurance lines. Investment purchases, maturities, sales at carrying value, valuation/OCI movements and income by asset class have **not** yet been reconciled as a portfolio rollforward. Equity, debt, DAC and reinsurance movements likewise remain subsequent schedules. No unsupported residual was plugged into cash or another balance.

Original SEC filing dates are carried from `historical_tables.json`. The transcribed annual-report PDF pages and SHA-256 hashes are in `source_inventory.json`. [Selected original SEC row parity](SEC_PARITY.md) now covers 88 premium, reserve and related rows for 2022–2025; most statement lines and 2020–2021 rows remain pending.

Regenerate from the repository root:

```sh
python3 scripts/build_historical.py
python3 scripts/build_statement_controls.py
python3 scripts/build_model_spec.py \
  --inventory examples/travelers/source_inventory.json \
  --actuals examples/travelers/actuals.json \
  --history examples/travelers/historical_actuals.json \
  --statement-controls examples/travelers/statement_controls.json \
  --output-dir docs/model_spec --as-of 2026-02-12
```

With the gitignored PDF caches present, `python3 scripts/audit_historical_pages.py --history examples/travelers/statement_controls.json` checks the source hashes and that every selected numeric value appears on its cited page. It does not establish SEC HTML row parity or semantic correctness by itself.
