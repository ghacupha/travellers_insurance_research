Feature: Insurance equity research distinguishes verified history from valuation

  Scenario: A full run may publish an unrated research PDF while valuation remains open
    Given a validated Travelers insurance research run
    When the insurance report data is prepared
    Then six audited annual periods are included in the report
    And the report distinguishes February history from April disposal evidence
    And no price target or rating is published
