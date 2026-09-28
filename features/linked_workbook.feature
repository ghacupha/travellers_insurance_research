Feature: The insurance workbook is built from Python with live scenario links

  Scenario: A release workbook exposes editable scenarios and linked research output
    Given the Python Travelers workbook is built
    Then its scenario selector offers Base, Upside and Downside
    And its active assumptions feed the forecast schedules
    And its final research output links to the selected forecast
    And its saved Base case contains calculated output values
