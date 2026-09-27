Feature: Sourced historical insurance schedules preserve accounting movements
  Scenario: A change in accounting guidance is a separate reserve movement
    Given the 2019–2025 Travelers premium and reserve tables
    When the historical schedules are reconciled at the February 2026 cutoff
    Then 2020 reserves include a separately disclosed 53 million adoption movement
    And the 2020 reserve rollforward balances without a plug

  Scenario: Held-for-sale presentation does not mask a premium-earning gap
    Given the 2019–2025 Travelers premium and reserve tables
    When the historical schedules are reconciled at the February 2026 cutoff
    Then the 2025 claims reserve presentation bridges to 65737 million
    And the 2025 net premium earning bridge retains a 412 million unresolved movement
