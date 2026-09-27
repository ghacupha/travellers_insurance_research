Feature: Original SEC disclosures agree with selected historical facts

  Scenario: Continuing P&C reserves keep held-for-sale business separate
    Given the selected original SEC Travelers disclosure rows
    When the SEC row comparisons run at the February 2026 cutoff
    Then all 88 selected SEC rows match the sourced historical facts
    And the 2025 continuing P&C reserve is 65734 million after held-for-sale classification
    And 2020 and 2021 remain outside this SEC row comparison
