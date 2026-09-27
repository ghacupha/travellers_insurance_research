Feature: Audited statements reconcile without hidden balance-sheet plugs

  Scenario: Every consolidated balance-sheet line ties to audited totals
    Given the Travelers 2019 through 2025 detailed balance-sheet rows
    When the audited balance-sheet detail is integrated at the February 2026 cutoff
    Then all 28 asset, liability, equity and accounting-equation controls pass
    And 2025 held-for-sale assets and liabilities remain separate
