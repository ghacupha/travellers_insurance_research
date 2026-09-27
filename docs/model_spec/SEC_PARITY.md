# Selected original SEC row parity

`examples/travelers/sec_parity_tables.json` transcribes **88 selected rows** from the original SEC HTML disclosures, independently of the issuer annual-report PDF transcriptions. `scripts/check_sec_parity.py` compares these values with normalized history and statement controls, and writes a result with the SEC URL, filing date, comparison basis and input hashes. Every selected comparison matches at the 2026-02-12 cutoff.

| SEC disclosure | Fiscal rows checked | Scope |
|---|---|---|
| [FY2024 Reinsurance](https://www.sec.gov/Archives/edgar/data/86312/000008631225000012/R14.htm) | 2022–2024 | Direct, assumed, ceded, net written and earned premiums |
| [FY2025 Reinsurance](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/R14.htm) | 2023–2025 | The same premium rows, including overlapping comparatives |
| [FY2024 Insurance Claim Reserves](https://www.sec.gov/Archives/edgar/data/86312/000008631225000012/R16.htm) | 2022–2024 | Incurred, paid, reserve FX, ending gross/net P&C reserves and unpaid recoverables |
| [FY2025 Schedule VI](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/R30.htm) | 2025 | Premium, incurred/paid, DAC, investment income, UPR and continuing P&C reserves |

All amounts are USD millions. Ceded premium is a positive magnitude in the model although it is parenthesized in the SEC table; prior-year favorable incurred is negative on both bases. The FY2025 Schedule VI P&C claims reserve of **65,734** excludes **1,909** classified as held for sale: the underlying gross P&C reserve **67,643 − 1,909 = 65,734**. It is not the consolidated balance-sheet claims line of 65,737, which also includes 3 of accident and health reserves.

This is a manually transcribed, selected-row comparison, not an automated check of every SEC filing line or a completed three-statement model. Original SEC row parity for 2020–2021 and most statement lines remains open. The annual-report PDFs retain separate hashes and page locators in the historical source inventory. Run `python3 scripts/check_sec_parity.py` after rebuilding history and statement controls.
