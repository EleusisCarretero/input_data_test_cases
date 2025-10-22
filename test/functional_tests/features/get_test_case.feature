Feature: API availability and test case retrieval
  As a consumer of the API
  I want to verify the service is reachable
  So that I can successfully retrieve test case parameters

  Background:
    Given The API has been launched

  Scenario: Get parameters for an existing test case id
    When I request test case parameters using id 1
    Then I receive a positive response for my GET request
    And the test case parameters are present in the response
