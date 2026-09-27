# Research quality and publication review

Reviewed 2026-09-27. This is an assessment of the current Travelers example release,
not a claim that it is a finished equity valuation or investment recommendation.

## Reference standard

[CFA Institute's Equity Research Report Essentials](https://www.cfainstitute.org/sites/default/files/-/media/documents/support/research-challenge/challenge/rc-equity-research-report-essentials.pdf)
describes business and industry analysis, historical and forecast financial analysis,
valuation, investment risks and clear basic security information as common elements of
a full report. Its [diligence standard](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-a)
calls for source checks and model-output validation. Its [communication standard](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-v-b)
emphasizes material assumptions, limitations and separation of fact from forecast or
opinion. [Conflict disclosure](https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-vi-a)
also matters if an eventual report includes a recommendation.

## Current evidence boundary

- The repo has a dated inventory of seven issuer annual reports (2019–2025), with
  URLs, local-cache hashes and reviewed page locators in
  `examples/travelers/source_inventory.json`. The normalized historical datasets
  carry source IDs, URLs, fiscal periods, units, status and filing dates.
- The 2022–2025 selected SEC comparison checks 88 premium and reserve rows. This is
  **partial parity**, not verification of every 2020–2025 fact against the original
  SEC filing. Annual-report PDF publication dates remain unconfirmed in the inventory.
- The example PDF names the FY2025 10-K, Q1 2026 10-Q and webcast as primary sources,
  and its historical source appendix links each displayed year/metric group to the
  issuer PDF and page. The workbook has a `Sources` sheet. Exact SEC HTML row links
  and original-row checks are still incomplete, so the PDF is not yet a fully
  verified valuation report.
- Six premium-earning bridges remain open. The 2026–2030 cases are illustrative and
  retain the FY2025 business perimeter; the Canadian disposal is separately dated.
  There is no integrated transaction-adjusted forecast, market-price input,
  calibrated valuation, rating or price target. The PDF correctly says so.

## Prioritized improvements

1. **Complete original-filing references.** The PDF now maps its historical figures
   to annual-report PDF pages. Extend those citations to original SEC HTML table/row
   or XBRL tags and filing dates for every displayed fact, and retain the explicit
   issuer-PDF-only status until each row has been checked. Keep the February history
   cutoff separate from April disposal evidence.
2. **Finish the historical evidence gate.** Recheck 2020–2021 and remaining statement
   rows against original SEC HTML/XBRL; resolve the six UPR earning movements and
   outstanding segment, DAC, investment, reserve and capital bridges. Publish a
   machine-readable exceptions table that distinguishes missing, disclosed, derived
   and modeled values. The current `Sources` sheet and checks are a strong base.
3. **Complete the insurer forecast before valuation.** Rebase premiums, reserves,
   investment assets/income, tax, equity and shares for the Canadian disposal;
   integrate income statement, balance sheet and cash flow with explicit checks.
   Test catastrophe, reserve-development, pricing and reinvestment downside cases.
4. **Build a dated valuation and complete report.** Add market price/shares/float,
   a defensible insurer valuation hierarchy (for example, residual income and
   payout-based methods with P/B and P/E cross-checks), scenario sensitivities,
   thesis, variant view, catalysts, peer/industry comparison, risks and disclosure
   of any material conflicts. No recommendation or target should appear before
   source, statement, market-input and valuation gates pass.
5. **Make the analysis independently repeatable.** Pin runtime dependencies and
   specify a standard non-Codex setup path; add an artifact provenance manifest
   covering every input and transformation; recalculate the XLSX in a spreadsheet
   engine and compare its three cases with Python; use a clean-checkout release
   workflow. The current JSON manifests and offline unit/BDD suite provide a start.

## Redistribution and local-record hygiene

The tracked example deliverables are generated Travelers outputs. Third-party
teaching workbooks, issuer source PDFs and unrelated research drafts are excluded.
The local `data/` cache is gitignored. This review found no clearly third-party
binary in the curated snapshot, but it is not a legal clearance of every source.

The [U.S. Copyright Office](https://copyright.gov/help/faq/faq-general.html) explains
that facts, ideas and methods are distinct from protected expression; its
[fair-use guidance](https://copyright.gov/fair-use/) makes clear that permission
questions depend on circumstances. Citing an external workbook would not, by itself,
grant redistribution rights. This project should retain citations to public source
documents and distribute original analysis and code rather than source-document PDFs
or third-party model files.

The curated snapshot starts from a new root commit so that unrelated historical
files are not reachable through its published branch. Existing external clones or
cached historical objects, if any, require separate handling.
