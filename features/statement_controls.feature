Feature: Audited statement controls anchor insurance schedules
  Scenario: Three statements agree on 2025 profit and cash
    Given the 2019–2025 Travelers statement controls
    When the audited statement control checks run
    Then 2025 net income agrees between the income and cash-flow statements
    And 2025 cash includes a separately disclosed 171 million held-for-sale reclassification
    And the 2025 balance sheet and investment asset classes balance
