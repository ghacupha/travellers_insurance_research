Feature: A dated Canadian disposal bridge preserves the research cutoff

  Scenario: February research cannot consume April premium and reserve evidence
    Given the Travelers Canadian disposal disclosures
    When the Canadian disposal bridge is built at the February 2026 cutoff
    Then the bridge shows 2008 million of held-for-sale book net assets
    And April 2026 reserve and premium facts are absent

  Scenario: Later evidence rebases reserves without calling a cash difference a gain
    Given the Travelers Canadian disposal disclosures
    When the Canadian disposal bridge is built at the April 2026 cutoff
    Then continuing opening net claims reserves are 58219 million
    And the divested 2025 net written and earned premiums are 989 and 1035 million
    And cash proceeds less December book net assets remains a diagnostic
