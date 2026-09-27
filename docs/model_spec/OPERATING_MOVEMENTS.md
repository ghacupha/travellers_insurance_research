# Travelers operating cash and equity schedules

The audited FY2022 and FY2025 annual-report copies supply comparative cash-flow and shareholders' equity rows for 2020–2025. `examples/travelers/operating_movement_tables.json` is the manual transcription; `operating_movements.json` contains 180 facts with PDF page, source hash and filing-date provenance. Thirty equity and financing controls pass. The cash-flow and equity rows have not yet been matched one by one to original SEC HTML.

Positive dividends, repurchases, investment purchases, maturities and sale proceeds are magnitudes. Negative short-term net sales represent net purchases. Opening common equity is derived from prior closing equity rather than labeled a separately disclosed current-year line.

| Fiscal year | Gross earning difference | Ceded earning difference | Net earning difference | DAC stock difference | Investment cash proxy difference | Debt stock difference |
|---|---:|---:|---:|---:|---:|---:|
| 2020 | −157 | −4 | −153 | 4 | 2,024 | 2 |
| 2021 | 12 | −1 | 13 | 0 | −1,908 | 1 |
| 2022 | −12 | −10 | −2 | −15 | −10,281 | 2 |
| 2023 | 70 | 4 | 66 | 7 | 2,080 | 1 |
| 2024 | −55 | −5 | −50 | −12 | −1,117 | 2 |
| 2025 | −436 | −24 | −412 | −83 | −304 | 1 |

All amounts are USD millions. Premium earning differences compare earned premiums with written premiums plus the change in UPR on matching gross or ceded bases. The 2025 gross UPR classified as held for sale is disclosed separately; its ceded counterpart is not, so the −412 net difference remains open. The DAC difference compares closing DAC with opening DAC plus cash-flow capitalized costs less income-statement amortization. Cash-flow investment proceeds are **not disposal carrying value**; the investment difference is a cash proxy diagnostic, not a portfolio reconciliation or a balancing entry. Debt differences likewise await carrying-value and other detail. None of these differences is inserted into an asset, liability, earnings or cash balance.

The equity schedule reconciles common equity from opening balance, net income, OCI, employee share issuance/compensation, dividends and both authorized and employee treasury repurchases. Dividends in the equity statement are declared amounts; cash-flow dividends can differ because of payment timing. The financing cash-flow control uses cash-paid amounts on its own basis.

Rebuild and check locally:

```sh
python3 scripts/build_operating_movements.py
python3 scripts/audit_historical_pages.py --history examples/travelers/operating_movements.json
```
