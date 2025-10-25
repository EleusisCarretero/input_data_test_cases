Feature: API availability and test case retrieval
  As a consumer of the API
  I want to verify the service is reachable
  So that I can successfully retrieve test case parameters

  Background:
    Given The API has been launched

  Scenario Outline: Get parameters for multiple test case ids
    When I request test case parameters using id <id>
    Then I receive a positive response for my GET request
    And the test case parameters are present in the response

    Examples:
    | id |
    | 1  |
    | 2  |

  Scenario Outline: Get parameters for multiple test case names
    When I request test case parameters using test case name <name>
    Then I receive a positive response for my GET request
    And the test case parameters are present in the response

    Examples:
    |       name              |
    |  test_case_dummy        |
    |  test_case_login_dummy  |
  
  Scenario Outline: Add a new test case
    When I request to add a new test case <test_case> parameters <parameters>
    Then I receive a positive response for my POST request
    And I request test case parameters using test case name <test_case>
    Then the test case parameters are present in the response
    And the parameters <parameters> are the same I request to add

    Examples:
    |    test_case           |              parameters               |
    |  test_new_test_case    |  [{"timeout":"10"}, {"timeout":"20"}] |
