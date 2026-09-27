# Historical coverage matrix

Issuer: The Travelers Companies, Inc. Information cutoff: 2026-02-12.

**D** = source PDF cached/indexed; row-level extraction and cutoff verification pending. **T** = relevant consolidated table located; specific row/value extraction still pending. **E** = release value extracted, schedule reconciliation pending. **P** = PDF row extracted, wider schedule/presentation unresolved. **R** = PDF premium/reserve arithmetic reconciled; selected SEC parity tracked separately. **C** = selected statement row passed statement control checks; full mapping pending. **O** = selected audited operating cash/equity row passed controls. **!** = open discrepancy. **A** = source after cutoff. **M** = source missing.

No cell in this matrix is a fully certified historical statement. Source availability is not numeric completeness.

Coverage records: 1129; status counts: {'pdf_reconciled': 106, 'document_indexed': 659, 'pdf_extracted': 25, 'table_located': 95, 'extracted_unreconciled': 19, 'statement_control_checked': 182, 'issue_open': 1, 'operating_control_checked': 42}.

## Source files

| FY | PDF pages | SHA-256 prefix | Source |
|---|---:|---|---|
| 2019 | 264 | e0093d65a080 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/annual/2019/TRV_2019_Annual_Report.pdf) |
| 2020 | 258 | b0f912a2cacd | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2020/ar/Travelers-2020-Annual-Report.pdf) |
| 2021 | 254 | 3e42291a1ec9 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2021/ar/Travelers-2021-Annual-Report.pdf) |
| 2022 | 258 | 294fc17bdf19 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2022/ar/B/Travelers-2022-Annual-Report-pdf.pdf) |
| 2023 | 254 | 53f73eab62a8 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2023/ar/Travelers-2023-Annual__Report.pdf) |
| 2024 | 260 | 7a58a170cab4 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2024/ar/v2/Travelers-2024-Annual-Report.pdf) |
| 2025 | 270 | 94fc0b121687 | [Annual report](https://s26.q4cdn.com/410417801/files/doc_financials/2025/AR/2026-Travelers-Annual-Report-Final.pdf) |

Full hashes, cache paths and candidate page locators are in source_inventory.json.
Original SEC filing dates for 2019–2025 are recorded in historical_tables.json. Issuer annual-report PDF posting dates remain unverified; selected SEC HTML row parity is in SEC_PARITY.md.

## Reviewed table locations

One-based PDF pages, not printed page numbers. Table presence does not certify every requested line.

| FY | Income | Balance sheet | Equity | Cash flow | Premium/reinsurance | Reserve rollforward |
|---|---:|---:|---:|---:|---:|---:|
| 2019 | 143 | 145 | 146 | 147 | 177 | 180 |
| 2020 | 146 | 148 | 149 | 150 | 182 | 185 |
| 2021 | 144 | 146 | 147 | 148 | 179 | 182 |
| 2022 | 145 | 147 | 148 | 149 | 179 | 182 |
| 2023 | 145 | 147 | 148 | 149 | 178 | 181 |
| 2024 | 148 | 150 | 151 | 152 | 182 | 186 |
| 2025 | 157 | 159 | 160 | 161 | 193 | 195 |

## Consolidated metrics

| Metric | Basis | 2019 opening | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 |
|---|---|---|---|---|---|---|---|---|
| Direct written premiums (`direct_written`) | direct | — | R | R | R | R | R | R |
| Assumed written premiums (`assumed_written`) | assumed | — | R | R | R | R | R | R |
| Gross written premiums (`gwp`) | gross | — | R | R | R | R | R | R |
| Ceded written premiums (`ceded_written`) | ceded | — | R | R | R | R | R | R |
| Net written premiums (`nwp`) | net | — | R | R | R | R | R | R |
| Gross unearned premium reserve (`gross_upr`) | gross | P | P | P | P | P | P | P |
| Ceded unearned premiums (`ceded_upr`) | ceded | P | P | P | P | P | P | P |
| Net unearned premium reserve (`net_upr`) | net | P | P | P | P | P | P | P |
| Gross unearned premium reserves classified as held for sale (`held_for_sale_upr`) | gross | D | D | D | D | D | D | P |
| Gross UPR FX/transfers/other earning movements (`gross_upr_other_change`) | gross | — | T | T | T | T | T | T |
| Ceded UPR FX/transfers/other earning movements (`ceded_upr_other_change`) | ceded | — | T | T | T | T | T | T |
| Gross earned premiums (`gross_earned`) | gross | — | R | R | R | R | R | R |
| Ceded earned premiums (`ceded_earned`) | ceded | — | R | R | R | R | R | R |
| Net earned premiums (`nep`) | net | — | R | R | R | R | R | R |
| Net UPR FX/transfers/other earning movements (`upr_other_change`) | net | — | T | T | T | T | T | T |
| Gross P&C loss and LAE reserves before held-for-sale presentation (`gross_reserves`) | gross | R | R | R | R | R | R | R |
| Recoverables on unpaid P&C losses (reserve-table basis) (`unpaid_recoverables`) | ceded | R | R | R | R | R | R | R |
| Net P&C loss and LAE reserves (`net_reserves`) | net | R | R | R | R | R | R | R |
| Current accident-year losses and LAE incurred (`current_incurred`) | net | — | R | R | R | R | R | R |
| Prior accident-year incurred adjustment in reserve rollforward (`reserve_prior_incurred`) | net | — | R | R | R | R | R | R |
| Total P&C incurred in reserve rollforward (`reserve_total_incurred`) | net | — | R | R | R | R | R | R |
| Paid losses and LAE for current accident year (`paid_current`) | net | — | R | R | R | R | R | R |
| Paid losses and LAE for prior accident years (`paid_prior`) | net | — | R | R | R | R | R | R |
| Reserve FX/acquisition/other movements (`reserve_fx_other`) | net | — | R | R | R | R | R | R |
| Reported catastrophe losses, net of reinsurance (`catastrophes`) | net | — | D | D | D | D | E | E |
| Reported prior-year development used in underwriting ratios (`reported_development`) | net | — | D | D | D | D | E | E |
| Accretion of claims-reserve discount (`discount_accretion`) | net | — | T | T | T | T | T | T |
| Balance-sheet reinsurance recoverables net of allowance (`total_recoverables`) | consolidated_gaap | C | C | C | C | C | C | C |
| Recoverables on paid losses (`paid_recoverables`) | consolidated_gaap | D | D | D | D | D | D | D |
| Allowance for uncollectible reinsurance (`reinsurance_allowance`) | consolidated_gaap | D | D | D | D | D | D | D |
| Cash collected from reinsurers (`reinsurance_collections`) | consolidated_gaap | — | D | D | D | D | D | D |
| Claims reserves classified as held for sale (`held_for_sale_reserves`) | consolidated_gaap | D | D | D | D | D | D | P |
| Accident/health and other claims reserves outside P&C rollforward (`other_insurance_reserves`) | consolidated_gaap | T | T | T | T | T | T | R |
| Reported balance-sheet claims and LAE reserves (`balance_sheet_claim_reserves`) | consolidated_gaap | C | C | C | C | C | C | P |
| Recoverables classified as held for sale (`held_for_sale_recoverables`) | consolidated_gaap | D | D | D | D | D | D | P |
| Deferred acquisition costs (`dac`) | consolidated_gaap | C | C | C | C | C | C | C |
| Capitalized acquisition costs (`dac_additions`) | consolidated_gaap | — | D | D | D | D | D | D |
| Amortization of deferred acquisition costs (`dac_amortization`) | consolidated_gaap | — | C | C | C | C | C | C |
| DAC FX/transfers/other movements (`dac_other`) | consolidated_gaap | — | D | D | D | D | D | D |
| General and administrative expenses (`general_admin`) | consolidated_gaap | — | C | C | C | C | C | C |
| GAAP claims and claim adjustment expense line (`claims`) | consolidated_gaap | — | C | C | C | C | C | C |
| Policyholder dividends (`policyholder_dividends`) | consolidated_gaap | — | D | D | D | D | E | E |
| Fees allocated against loss-ratio numerator (`loss_allocated_fees`) | consolidated_gaap | — | D | D | D | D | E | E |
| Fees allocated against expense-ratio numerator (`expense_allocated_fees`) | consolidated_gaap | — | D | D | D | D | E | E |
| Non-insurance G&A excluded from expense ratio (`noninsurance_admin`) | consolidated_gaap | — | D | D | D | D | E | E |
| Billing/policy fees and other ratio adjustments (`billing_fees_other`) | consolidated_gaap | — | D | D | D | D | E | E |
| Reported loss and LAE ratio (`reported_loss_ratio`) | consolidated_gaap | — | D | D | D | D | E | ! |
| Reported underwriting expense ratio (`reported_expense_ratio`) | consolidated_gaap | — | D | D | D | D | E | E |
| Reported combined ratio (`reported_combined_ratio`) | consolidated_gaap | — | D | D | D | D | E | E |
| Reported underlying combined ratio (`underlying_combined_ratio`) | consolidated_gaap | — | D | D | D | D | D | D |
| Fixed maturities at amortized cost (`fixed_maturity_cost`) | amortized_cost | C | C | C | C | C | C | C |
| Fixed maturities at fair value (`fixed_maturity_fair`) | fair_value | C | C | C | C | C | C | C |
| Equity securities (`equity_investments`) | fair_value | C | C | C | C | C | C | C |
| Short-term investments (`short_term_investments`) | consolidated_gaap | C | C | C | C | C | C | C |
| Real estate and other investments (separate child classes) (`other_investments`) | consolidated_gaap | C | C | C | C | C | C | C |
| Investment purchases (`investment_purchases`) | consolidated_gaap | — | T | T | T | T | T | T |
| Investment sale proceeds (`investment_sales`) | consolidated_gaap | — | T | T | T | T | T | T |
| Investment maturity proceeds (`investment_maturities`) | consolidated_gaap | — | T | T | T | T | T | T |
| Carrying value of investments disposed (`investment_disposal_carrying`) | consolidated_gaap | — | D | D | D | D | D | D |
| Net investment income (`investment_income`) | consolidated_gaap | — | C | C | C | C | C | C |
| Net realized investment gains/losses (`realized_gains`) | consolidated_gaap | — | C | C | C | C | C | C |
| Investment-related OCI, after tax (`investment_oci`) | consolidated_gaap | — | T | T | T | T | T | T |
| Net investment yield on defined average asset basis (`investment_yield`) | consolidated_gaap | — | D | D | D | D | D | D |
| Total income tax expense (`tax_expense`) | consolidated_gaap | — | C | C | C | C | C | C |
| Current income tax expense (`current_tax`) | consolidated_gaap | — | D | D | D | D | D | D |
| Deferred income tax expense (`deferred_tax`) | consolidated_gaap | — | D | D | D | D | D | D |
| Deferred tax assets/liabilities, net (`deferred_tax_balance`) | consolidated_gaap | D | D | D | D | D | D | D |
| Income taxes paid (`cash_tax`) | consolidated_gaap | — | O | O | O | O | O | O |
| Debt outstanding (`debt`) | consolidated_gaap | C | C | C | C | C | C | C |
| Debt issuance proceeds (`debt_issuance`) | consolidated_gaap | — | O | O | O | O | O | O |
| Debt principal repaid (`debt_repayment`) | consolidated_gaap | — | O | O | O | O | O | O |
| Interest expense (`interest_expense`) | consolidated_gaap | — | C | C | C | C | C | C |
| Common shareholders equity (`equity`) | consolidated_gaap | C | C | C | C | C | C | C |
| Total other comprehensive income (`total_oci`) | consolidated_gaap | — | O | O | O | O | O | O |
| Accumulated other comprehensive income (`aoci`) | consolidated_gaap | T | O | O | O | O | O | O |
| Common dividends (`dividends`) | consolidated_gaap | — | O | O | O | O | O | O |
| Share repurchases (authorization and employee separately) (`buybacks`) | consolidated_gaap | — | T | T | T | T | T | T |
| Share issuance and share-based compensation equity movements (`share_issuance`) | consolidated_gaap | — | T | T | T | T | T | T |
| Period-end common shares (`closing_shares`) | consolidated_gaap | T | O | O | O | O | O | O |
| Diluted weighted-average shares (`diluted_shares`) | consolidated_gaap | — | T | T | T | T | T | T |
| Statutory capital and surplus (specified legal entity scope) (`statutory_surplus`) | statutory | D | D | D | D | D | D | D |
| Cash including restricted cash, balance-sheet presentation (`cash`) | consolidated_gaap | C | C | C | C | C | C | C |
| Premium receivables (`premium_receivables`) | consolidated_gaap | C | C | C | C | C | C | C |
| Investment income accrued (`accrued_investment_income`) | consolidated_gaap | C | C | C | C | C | C | C |
| Other assets with disclosed child lines (`other_assets`) | consolidated_gaap | T | T | T | T | T | T | T |
| Other liabilities with disclosed child lines (`other_liabilities`) | consolidated_gaap | T | T | T | T | T | T | T |
| Reported total assets control (`total_assets`) | consolidated_gaap | C | C | C | C | C | C | C |
| Reported total liabilities control (`total_liabilities`) | consolidated_gaap | C | C | C | C | C | C | C |
| Net income (`net_income`) | consolidated_gaap | — | C | C | C | C | C | C |
| Fee and other revenue (disclosed child lines) (`fee_other_income`) | consolidated_gaap | — | T | T | T | T | T | T |
| Cash flow from operations (`cfo`) | consolidated_gaap | — | C | C | C | C | C | C |
| Cash flow from investing (`cfi`) | consolidated_gaap | — | C | C | C | C | C | C |
| Cash flow from financing (`cff`) | consolidated_gaap | — | C | C | C | C | C | C |
| Exchange-rate effect on cash (`cash_fx`) | consolidated_gaap | — | C | C | C | C | C | C |
| Cash/restricted cash at end of cash-flow statement (`cash_flow_closing`) | consolidated_gaap | T | C | C | C | C | C | C |

## Segment coverage

Business Insurance, Bond & Specialty Insurance and Personal Insurance each have separate metric/year records in the JSON. None is marked extracted merely because a consolidated value exists. Opening records exist only for balance metrics.

| Requested metric | Business Insurance | Bond & Specialty | Personal Insurance |
|---|---|---|---|
| Direct written premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Assumed written premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross written premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Ceded written premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net written premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross unearned premium reserve | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Ceded unearned premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net unearned premium reserve | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross unearned premium reserves classified as held for sale | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross UPR FX/transfers/other earning movements | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Ceded UPR FX/transfers/other earning movements | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross earned premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Ceded earned premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net earned premiums | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net UPR FX/transfers/other earning movements | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Gross P&C loss and LAE reserves before held-for-sale presentation | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Recoverables on unpaid P&C losses (reserve-table basis) | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net P&C loss and LAE reserves | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Current accident-year losses and LAE incurred | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Prior accident-year incurred adjustment in reserve rollforward | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Total P&C incurred in reserve rollforward | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Paid losses and LAE for current accident year | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Paid losses and LAE for prior accident years | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Reserve FX/acquisition/other movements | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Reported catastrophe losses, net of reinsurance | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Reported prior-year development used in underwriting ratios | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Accretion of claims-reserve discount | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |
| Net investment income | D: 2020–2025 | D: 2020–2025 | D: 2020–2025 |

## Next extraction batches

1. Verify transcribed PDF rows against the original SEC filing and explain net UPR earning movements.
2. Extract the remaining statement openings, investment, expense/DAC, tax and equity detail.
3. Add segment schedules and bridges; verify disclosure definitions before filling unavailable splits.
