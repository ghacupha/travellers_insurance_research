Feature: Audited operating flows preserve unknown stock changes

  Scenario: Equity reconciles without using DAC or investment gaps as plugs
    Given the Travelers audited cash-flow and equity rows for 2020 through 2025
    When the operating schedules are built at the February 2026 cutoff
    Then all 30 equity and financing controls reconcile
    And the 2025 DAC stock bridge remains an open 83 million decrease
    And the 2025 investment cash proxy remains a diagnostic, not a balancing entry
