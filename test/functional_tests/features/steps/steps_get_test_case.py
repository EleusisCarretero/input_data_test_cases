"""
Step definitions for API validation.

Includes:
- Checking API availability
- Retrieving test case parameters by id
"""
from behave import given, when, then


@given("The API has been launched")
def step_check_api_is_up(context):
    """
    Ensures the API is reachable and returns HTTP 200.

    Uses:
    - `context.config.userdata['BASE_URL']` (set in behave.ini or via `-D BASE_URL=...`)
    - `context.session`: a persistent requests.Session
    - `context.result`: helper for safe assertions and checks
    """
    context.logger.info("Checking if the server is up")
    # Base url
    url = context.config.userdata.get("BASE_URL").rstrip("/")
    response = context.result.check_not_raises_any_exception(
        context.session.request,
        "Check API is up",
        "GET",
        url,
    )

    context.result.check_equals_to(
        actual_value=response.status_code,
        expected_value=200,
        step_msg="Verify server health check",
    )
    context.BASE_URL = url

@when("I request test case parameters using id {testcase_id:d}")
def step_get_testcase_by_id(context, testcase_id: int):
    """
    Performs a GET request to retrieve test case parameters.

    :param testcase_id: ID of the existing test case (int)
    Stores results in:
    - `context.response`
    - `context.status_code`
    - `context.test_case_params`
    """
    endpoint = context.config.userdata.get("TESTCASE_ENDPOINT").rstrip("/")
    url = f"{context.BASE_URL}/{endpoint}"
    params = {"id": testcase_id}

    response = context.result.check_not_raises_any_exception(
        context.session.request,
        "GET test_case by id",
        "GET",
        url,
        params=params,
    )

    context.test_case_params = context.result.check_not_raises_any_exception(
        response.json,
        f"Response is not valid JSON: {response.text[:300]}"
    )

    context.response = response
    context.status_code = response.status_code

@then("I receive a positive response for my GET request")
def step_check_http_status_code(context):
    """
    Verifies that the HTTP response code equals 200.
    """
    context.result.check_equals_to(
        actual_value=context.status_code,
        expected_value=200,
        step_msg=f"HTTP status was {context.status_code}"
    )

@then("the test case parameters are present in the response")
def step_check_testcase_params(context):
    """
    Ensures that the JSON response contains valid parameters.
    """
    data = getattr(context, "test_case_params", None)
    context.result.check_not_equals_to(
        actual_value=data,
        expected_value=None,
        step_msg="Empty or missing JSON payload"
    )
