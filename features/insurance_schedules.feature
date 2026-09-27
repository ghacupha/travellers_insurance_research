Feature: Insurance schedules reflect the economics of coverage and claims
  Scenario: Only the elapsed coverage is earned
    Given annual gross written premium of 100 with 20 ceded
    When three months of uniform coverage have elapsed
    Then net written premium is 80 and net earned premium is 20

  Scenario: An unpaid repair is still an incurred claim
    Given a covered repair estimated at 15000
    When the insurer has paid only 5000
    Then incurred losses are 15000 and the outstanding reserve is 10000

  Scenario Outline: Prior year development changes incurred losses
    Given opening net claims reserves of 100 and current year incurred losses of 40
    When prior year development is <development> and paid losses are 30
    Then closing net reserves are <reserve> and total incurred is <incurred>

    Examples:
      | development | reserve | incurred |
      | -5          | 105     | 35       |
      | 5           | 115     | 45       |

  Scenario: Travelers reported combined ratio includes fee adjustments
    Given the verified Travelers 2025 annual disclosures
    When the reported ratio adjustments are applied
    Then the loss numerator is 26990 and the expense numerator is 12501
    And the combined ratio rounds to 89.9 percent

  Scenario: Research cannot use a future release
    Given an information cutoff of 2025-12-31
    When the 2025 earnings release published in January 2026 is loaded
    Then the research run is rejected for unavailable information
