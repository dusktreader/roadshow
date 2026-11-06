Feature: main module

  Scenario: main prints the package version
    When the main function is called
    Then the output contains "roadshow "
