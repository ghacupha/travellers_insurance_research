# Source coverage and limitations

The current Travelers example release is an operating model and unrated research
status report. It does not include an integrated forecast or valuation.

## Current evidence boundary

- The repo has a dated inventory of seven issuer annual reports (2019–2025), with
  URLs, local-cache hashes and recorded page locators in
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
  calibrated valuation, rating or price target. The PDF identifies these limits.

## Outstanding work

1. **Complete original-filing references.** The PDF now maps its historical figures
   to annual-report PDF pages. Extend those citations to original SEC HTML table/row
   or XBRL tags and filing dates for every displayed fact, and retain the explicit
   issuer-PDF-only status until each row has been checked. Keep the February history
   cutoff separate from April disposal evidence.
2. **Finish the historical evidence gate.** Recheck 2020–2021 and remaining statement
   rows against original SEC HTML/XBRL; resolve the six UPR earning movements and
   outstanding segment, DAC, investment, reserve and capital bridges. Publish a
   machine-readable exceptions table that distinguishes missing, disclosed, derived
   and modeled values. The current `Sources` sheet records source metadata and checks.
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
5. **Make the analysis independently repeatable.** The Python package extras now
   provide a public setup path, and a clean public clone builds the release. Pin
   runtime dependencies for bit-for-bit reproducibility, extend the artifact
   provenance manifest across every transformation, and recalculate the XLSX in a
   native spreadsheet engine across all three cases. The current JSON manifests
   and offline unit/BDD suite cover selected stages.

## Redistribution and local-record hygiene

The tracked example deliverables are generated Travelers outputs. Third-party
teaching workbooks, issuer source PDFs and unrelated research drafts are excluded.
The local `data/` cache is gitignored. The tracked binaries are generated example
deliverables; source-document PDFs and third-party teaching workbooks are excluded.

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
