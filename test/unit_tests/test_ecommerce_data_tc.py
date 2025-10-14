import unittest
from flask import Flask, jsonify
from unittest.mock import patch, call, Mock
from input_data_test_cases.base_api import StatusCode
from input_data_test_cases.mysql_api.db_handler import ConsultTableQuery, ModifyTableQuery
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
from input_data_test_cases.mysql_api.mysql_api import MyslApiException


class TestEcommerceDataTC(unittest.TestCase):

    @patch("input_data_test_cases.mysql_api.mysql_api.MySQL")
    def setUp(self, mock_mysql):
        config = {
        'MYSQL_HOST': 'fake_host',
        'MYSQL_USER': 'fake_user',
        'MYSQL_PASSWORD': 'fake_pssw',
        'MYSQL_DB': 'fake_db',
        'MYSQL_PORT': 1111,
        }
        self.api = EcommerceDataTC(config=config)
        self.app = self.api.app
        self.mock_db = mock_mysql
    
    @staticmethod
    def mocking_format(payload, status_code):
        return jsonify(payload), status_code

    @patch.object(Flask, "add_url_rule")
    @patch.object(EcommerceDataTC, "update_test_case")
    @patch.object(EcommerceDataTC, "delete_test_case")
    @patch.object(EcommerceDataTC, "post_test_case")
    @patch.object(EcommerceDataTC, "get_test_case")
    @patch.object(EcommerceDataTC, "home")
    def test_define_routes(
        self,
        patch_home,
        patch_get_test_case,
        patch_post_test_case,
        patch_delete_test_case,
        patch_update_test_case,
        add_url_rule_patch):
        self.api.define_routes()
        expected_calls = [
            call(
                "/",
                view_func=patch_home
                ),
            call(
                "/test_case",
                endpoint="get_test_case",
                view_func=patch_get_test_case,
                methods=["GET"]
            ),
            call(
                "/test_case",
                endpoint="post_test_case",
                view_func=patch_post_test_case,
                methods=["POST"]
            ),
             call(
                "/test_case",
                endpoint="delete_test_case",
                view_func=patch_delete_test_case,
                methods=["DELETE"]
            ),
             call(
                "/test_case",
                endpoint="update_test_case",
                view_func=patch_update_test_case,
                methods=["PUT"]
            )
        ]
        add_url_rule_patch.assert_has_calls(expected_calls, any_order=False)
    
    @patch.object(EcommerceDataTC, "format_response")
    def test_home(self, patch_format):
        base_url_msg = {'message': "Base url"}
        expected_code = StatusCode.OK
        patch_format.side_effect = lambda payload, status_code: self.mocking_format(payload, status_code)
        with self.app.test_request_context("/"):
            resp, code = self.api.home()

        patch_format.assert_called_once_with(base_url_msg, status_code=expected_code)
        data = resp.get_json()
        self.assertEqual(data, base_url_msg)
        self.assertEqual(code, expected_code)

    def test_define_queries(self):
        expected_map_quieries = {
            'GET_TESTCASE_PARAMS': ConsultTableQuery.WHERE_COLUMN_EQUALS,
            'POST_TESTCASE_PARAMS': ModifyTableQuery.INSERT_NEW_VALUE_BASE_QUERY,
            'DELETE_TEST_CASE': ModifyTableQuery.DELETE_VALUE_WHERE_COLUMN_EQUALS,
            'UPDATE_TEST_CASE': ModifyTableQuery.UPDATE_VALUE_WHERE_COLUMN_EQUALS,
            'INVALID_KEY': None
        }
        for key, expect_query in expected_map_quieries.items():
            actual_query = self.api.define_queries(key)
            self.assertEqual(actual_query, expect_query)

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "connect_data_base")
    def test_get_test_case_invalid_requests(self, patch_connect_db, patch_queries, patch_format):
        expected_code = StatusCode.BAD_REQUEST
        endpoint_error_msg = {
            '/test_case': "Missing id or testcase name",
            '/test_case?id=1&name=test_case_dummy': "You just can choose id or name, not both",
            '/test_case?id=test_case': "ID should be an integer",
            '/test_case?name=2': "Name should be a string"
            }
        patch_format.side_effect = lambda payload, status_code: self.mocking_format(payload, status_code)
        for endpoint, error_msg in endpoint_error_msg.items():
            
            with self.app.test_request_context(endpoint):
                resp, code = self.api.get_test_case(Mock(), Mock())

            patch_connect_db.assert_not_called()
            patch_queries.assert_not_called()
            patch_format.assert_called_once_with({'message': error_msg}, status_code=expected_code)
            
            data = resp.get_json()
            self.assertEqual(data.get('message'), error_msg)
            self.assertEqual(code, expected_code)
            #Reset mocks
            patch_format.reset_mock()
            patch_connect_db.reset_mock()
            patch_queries.reset_mock()

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "query")
    def test_get_test_case_valid_requests(self, patch_connect_db, patch_queries, patch_format):
        expected_code = StatusCode.OK
        endpoint_response = {
            '/test_case?id=1': {'params': [{'timeout': 2}]},
            '/test_case?name=test_timeout': {'params': [{'timeout': 2}]},
            }
        patch_format.side_effect = lambda payload, status_code: self.mocking_format(payload, status_code)
        patch_queries.return_value = 'select params from parameters where {column} = "{value}"'
        for endpoint, response in endpoint_response.items():
            patch_connect_db.return_value = response
            patch_format.return_value = {'message': response}
            with self.app.test_request_context(endpoint):
                resp, code = self.api.get_test_case()

                patch_queries.assert_called_once_with(key='GET_TESTCASE_PARAMS')
                patch_format.assert_called_once_with(response, status_code=expected_code)

                data = resp.get_json()
                self.assertEqual(data, response)
                self.assertEqual(code, expected_code)
            #Reset mocks
            patch_format.reset_mock()
            patch_connect_db.reset_mock()
            patch_queries.reset_mock()

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "query")
    def test_get_test_case_raise_exception(self, query_connect_db, patch_queries, patch_format):
        expected_code = StatusCode.NOT_FOUND
        query_connect_db.side_effect = MyslApiException("Unable to execute command")
        patch_format.side_effect = lambda payload, status_code: self.mocking_format(payload, status_code)
        patch_format.return_value = {'message': 'Unable find the desired test case'}
        with self.app.test_request_context('/test_case?id=1'):
            resp, code = self.api.get_test_case()
        patch_format.assert_called_once_with({'message': 'Unable find the desired test case'}, status_code=expected_code)
        patch_queries.assert_called_once_with(key='GET_TESTCASE_PARAMS')
        data = resp.get_json()
        self.assertEqual(data.get('message'), 'Unable find the desired test case')
        self.assertEqual(code, expected_code)
