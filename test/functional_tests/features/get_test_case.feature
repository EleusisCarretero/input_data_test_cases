Feature: Get test cases

    Scenario: Getting a test case by id successfully
        Given The API has been launched
        When I request for a test case's parameters by using an exisitng id 
        Then I receive a positive response for my GET request
        And the test case's parameter are in the response
