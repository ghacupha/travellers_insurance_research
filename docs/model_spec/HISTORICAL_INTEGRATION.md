# Audited statement integration: 2019–2025

`balance_sheet_detail_tables.json` adds the remaining consolidated balance-sheet
presentation lines from the Travelers annual-report PDF copies. The source pages are
2019 p. 145, 2021 p. 146 (2020 and 2021 columns), 2023 p. 147 (2022 and 2023), and
2025 p. 159 (2024 and 2025). Each normalized numeric fact in
`historical_integration.json` retains the PDF URL, SHA-256, page and SEC filing date.
An absent line is `null` in the transcription and creates no asserted zero fact.

Run `python3 scripts/build_historical_integration.py` after rebuilding historical
actuals and statement controls. This yields 86 detail facts and 28 exact controls:
assets by line, liabilities by line, four equity components, and assets less
liabilities and equity for each 2019–2025 period. The page-text audit checks all 86
numeric facts against the locally cached annual-report PDF text. The workbook's
historical Model section links every input to Sources, computes 28 corresponding
balance checks, and builds 2020–2025 GAAP income from premiums, investment income,
fees, gains, other revenue, claims, DAC amortization, G&A, interest and tax. Its
24 income checks reconcile reported revenue, expenses, net income and cash-flow net
income. These controls establish historical statement arithmetic; they do not
explain the separately displayed UPR, DAC, investment or debt stock movements.

At 2025 year-end, held-for-sale assets of $4,550m and liabilities of $2,542m are
separate balance-sheet lines. Travelers [completed the sale of its Canadian personal
insurance business and most of its Canadian commercial insurance business on
January 2, 2026](https://investor.travelers.com/newsroom/press-releases/news-details/2026/Travelers-Completes-Sale-of-Canadian-Personal-Insurance-Business-and-Majority-of-Its-Canadian-Commercial-Insurance-Business-to-Definity/default.aspx).
The current 2026–2030 P&C operating scenario holds the FY2025 perimeter constant and
does not model this disposal, its run-rate earnings, proceeds or gain. It is a
counterfactual illustration, not a Travelers guidance or valuation forecast. A
transaction-adjusted opening balance and operating scope must be sourced and
reconciled before integrated forecast statements or a price target can be approved.

The complete balance-sheet detail has been independently checked against PDF page
text, but original SEC HTML parity remains bounded to the separately documented
sample in `SEC_PARITY.md`. The information cutoff is 2026-02-12, not today's date.
