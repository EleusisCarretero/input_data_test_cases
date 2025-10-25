"""
Step definitions for API validation.

Includes:
- Checking API availability
- Retrieving test case parameters by id
"""
from result import is_ok
from behave import given, when, then


def by_parameter_decorator(func):
    """
    Decorator for Behave step functions that automatically performs
    a GET request to BASE_URL/TESTCASE_ENDPOINT using parameters returned by the step.

    The decorated function must return a dict of query parameters.
    Example:

        @when("I request test case by id {testcase_id:d}")
        @by_parameter_decorator
        def step_get_test_case(context, testcase_id):
            return {"id": testcase_id}
    """

    def wrapper(context, *args, **kwargs):
        base_url = context.config.userdata.get("BASE_URL", "").rstrip("/")
        endpoint = context.config.userdata.get("TESTCASE_ENDPOINT", "").strip("/")
        if not base_url or not endpoint:
            raise RuntimeError("Missing BASE_URL or TESTCASE_ENDPOINT in userdata")
        url = f"{base_url}/{endpoint}"
        req_kwargs = {}
        params_or_data, method = func(context, *args, **kwargs)
        if not isinstance(params_or_data, dict):
            raise TypeError(f"Expected dict from {func.__name__}, got {type(params_or_data).__name__}")
        if method == "GET":
            req_kwargs = {'params': params_or_data}
            context.logger.info(f"Requesting {url} with params={params_or_data}")
        elif method == "POST":
            req_kwargs = {'payload': params_or_data}
            context.logger.info(f"Requesting {url} with json={params_or_data}")
        else:
            pass
        context.logger.info(f"Requesting {url} with params={params_or_data}")
        result = context.result.check_not_raises_any_exception(
            context.session.query,
            f"{method} {endpoint} by {','.join(params_or_data.keys())}",
            method,
            url,
            **req_kwargs,
        )
        assert is_ok(result)
        response = result.value
        context.response = response
        context.status_code = response.status_code
        if method == "GET":
            context.test_case_params = context.result.check_not_raises_any_exception(
                response.json,
                "Validate response JSON",
            )

        return response

    return wrapper

"""
    Common through all api requests
"""
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
    result = context.result.check_not_raises_any_exception(
        context.session.query,
        "Check API is up",
        "GET",
        url,
    )
    assert is_ok(result)
    response = result.value
    context.result.check_equals_to(
        actual_value=response.status_code,
        expected_value=200,
        step_msg="Verify server health check",
    )
    context.BASE_URL = url

"""
    Get request steps
"""
@when("I request test case parameters using id {testcase_id:d}")
@by_parameter_decorator
def step_get_testcase_by_id(context, testcase_id: int):
    """
    Performs a GET request to retrieve test case parameters.

    :param testcase_id: ID of the existing test case (int)
    Stores results in:
    - `context.response`
    - `context.status_code`
    - `context.test_case_params`
    """
    return {"id": testcase_id}, "GET"

@when("I request test case parameters using test case name {testcase_name}")
@then("I request test case parameters using test case name {testcase_name}")
@by_parameter_decorator
def step_get_testcase_by_name(context, testcase_name: str):
    """
    Performs a GET request to retrieve test case parameters.

    :param testcase_name: Name of the existing test case (int)
    Stores results in:
    - `context.response`
    - `context.status_code`
    - `context.test_case_params`
    """
    return {"name": testcase_name}, "GET"

@then("I receive a positive response for my GET request")
def step_check_http_status_code(context):
    """
    Verifies that the HTTP response code equals 200.
    """
    context.result.check_equals_to(
        actual_value=context.status_code,
        expected_value=200,
        step_msg=f"Check HTTP status was {context.status_code}"
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
        step_msg="Check is not Empty or missing JSON payload"
    )

"""
    Post requests steps
"""

@when("I request to add a new test case {test_case} parameters {parameters}")
@by_parameter_decorator
def step_add_new_test_case(context, test_case:str, parameters):
    return {'name': test_case, 'params': parameters}, "POST"

@then("I receive a positive response for my POST request")
def step_check_http_status_code(context):
    """
    Verifies that the HTTP response code equals 201.
    """
    context.result.check_equals_to(
        actual_value=context.status_code,
        expected_value=201,
        step_msg=f"Check HTTP status was {context.status_code}"
    )

@then("the parameters {parameters} are the same I request to add")
def step_check_parameters(context, parameters:str):
    data = getattr(context, "test_case_params", None)
    context.result.check_equals_to(
        actual_value=data,
        expected_value=parameters,
        step_msg=f"Check the test cases parameters are the same"
    )