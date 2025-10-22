

import requests
from behave import Given, When, Then



@Given("The API has been launched")
def step_check_api_is_up(context):
    context.logger.info("Checking server is up")
    url = context.config.userdata.get("BASE_URL")
    response = context.result.check_not_raises_any_exception(
        context.session.request,
        "Check API us up",
        "GET", url
    )
    context.result.check_equals_to(
        actual_value=response.status_code,
        expected_value=200,
        step_msg="Check The server is up")
    


@When('I request for a test case\'s parameters by using an exisitng id')
def step_impl(context):
    response = context.session.request(
        url="http://localhost:8000/test_case?id=1",
        method="GET"
    )
    context.status_code = response.status_code
    context.test_case_params = response.json()

@Then('I receive a positive response for my GET request')
def step_validate_response(context):
    assert context.status_code == 200

@Then('the test case\'s parameter are in the response')
def step_validate_body(context):
    assert context.test_case_params != False