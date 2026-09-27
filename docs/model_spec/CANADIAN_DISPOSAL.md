# Canadian disposal bridge and information cutoffs

Run `python3 scripts/build_canadian_disposal_bridge.py` after rebuilding the 2025
historical inputs. It produces two immutable, separately dated bridge outputs:
`examples/travelers/canadian_disposal_2026-02-12.json` and
`examples/travelers/canadian_disposal_2026-04-16.json`. The April disclosures are **not**
inputs to the February 12 research workbook or its existing illustrative forecast.
The source records carry URL, availability date and locator, and the builder rejects
duplicate, missing or incorrectly sourced facts.

The [FY2025 Form 10-K](https://www.sec.gov/Archives/edgar/data/86312/000008631226000065/trv-20251231.htm)
discloses the following held-for-sale classes at December 31, 2025 (USD millions):

| Assets | Amount | Liabilities | Amount |
|---|---:|---|---:|
| Fixed maturities | 3,243 | Gross claims reserves | 1,909 |
| Premium receivables | 263 | Gross unearned premiums | 514 |
| Reinsurance recoverables | 285 | Remaining liabilities | 119 |
| Goodwill | 208 | **Total liabilities** | **2,542** |
| Remaining assets | 551 | | |
| **Total assets** | **4,550** | | |

The February bridge reconciles those classes to the audited consolidated balance
sheet and existing reserve/UPR disclosures. Disposed **book net assets are 2,008**.
The 2025 balance-sheet UPR line of 22,431 already excludes the separately presented
514 held for sale; subtracting 514 again would double count the disposal. The
reserve rollforward gross closing balance of 67,643 includes the 1,909 disposal
group, leaving 65,734 on the continuing P&C basis. That is distinct from the
65,737 consolidated balance-sheet claims line, which includes 3 of accident and
health reserves. The 2025 balance-sheet investment total of 101,182 and cash of
842 likewise already exclude held-for-sale assets; subtracting the sold fixed
maturities or cash again would understate continuing invested assets and cash.

The [Q1 2026 Form 10-Q](https://www.sec.gov/Archives/edgar/data/86312/000008631226000111/trv-20260331.htm),
filed April 16, reports **1,627 of net claims reserves disposed** in its reserve
rollforward and **2,384 of cash proceeds** in investing cash flow. Combining the
December gross disposal reserve with the Q1 net disposal line implies 282 of
recoverables on unpaid claims and 3 of other reinsurance recoverables within the
285 held-for-sale asset. These are explicitly *cross-date inferences*, not a
separately disclosed decomposition. After the reserve rollforward's disposal
movement, the opening continuing P&C basis is 58,219 net reserves, 7,515 unpaid
recoverables and 65,734 gross reserves.

The [Q1 2026 Travelers webcast, PDF page 19](https://s26.q4cdn.com/410417801/files/doc_financials/2026/q1/1Q26-Webcast-FINAL.pdf)
reports 2025 premiums of the divested operations by segment:

| USD millions | Business | Bond & Specialty | Personal | Total |
|---|---:|---:|---:|---:|
| Net written | 283 | 56 | 650 | **989** |
| Earned | 309 | 56 | 670 | **1,035** |

Subtracting these from audited 2025 consolidated values yields a **comparable 2025
continuing base** of 43,398 net written premiums and 42,879 net earned premiums.
This is a comparison base, not restated GAAP actuals. Travelers retained Canadian
surety, so the divested premiums are not all Canadian premiums.

The difference between 2,384 cash proceeds and 2,008 December book net assets is
376. The bridge names it a diagnostic; it is **not a sale gain**. Closing purchase
price adjustments, cash included in the disposal group, transaction costs, taxes,
foreign-currency translation reclassification and the January closing basis are
not reconciled here. Divested gross written and ceded written premiums, ceded UPR,
and loss/expense run rates also remain unextracted or unreconciled on a consistent basis.
These missing inputs prevent the existing gross-premium-driven scenario from
becoming a transaction-adjusted Travelers forecast. Later 2026 filings should be
added to a new dated research run, not silently backfilled into the February one.
