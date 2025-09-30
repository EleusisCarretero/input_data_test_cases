import unittest
from flask import jsonify
from unittest.mock import patch
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
from input_data_test_cases.mysql_api.mysql_api import MyslApiException



class TestEcommerceDataTC(unittest.TestCase):
    def setUp(self):
        self.api = EcommerceDataTC(config={})
        self.app = self.api.app
    
    @patch.object(EcommerceDataTC, "format_response")
    def test_home(self, patch_format):
        base_url_msg = {'message': "Base url"}
        patch_format.side_effect = lambda payload: jsonify(payload)
        with self.app.test_request_context("/"):
            resp = self.api.home()

        patch_format.assert_called_once_with(base_url_msg)
        data = resp.get_json()
        self.assertEqual(data, base_url_msg)

    def test_define_queries(self):
        expected_map_quieries = {
            'GET_TESTCASE_PARAMS': 'select params from parameters where {column} = "{value}"',
            'INVALID_KEY': None
        }
        for key, expect_query in expected_map_quieries.items():
            actual_query = self.api.define_queries(key)
            self.assertEqual(actual_query, expect_query)


    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "connect_data_base")
    def test_get_test_case_invalid_requests(self, patch_connect_db, patch_queries, patch_format):
        endpoint_error_msg = {
            '/test_case': "Missing id or testcase name",
            '/test_case?id=1&name=test_case_dummy': "You just can choose id or name, not both",
            '/test_case?id=test_case': "ID should be an integer",
            '/test_case?name=2': "Name should be a string"
            }
        patch_format.side_effect = lambda payload: jsonify(payload)
        for endpoint, error_msg in endpoint_error_msg.items():
            
            with self.app.test_request_context(endpoint):
                resp = self.api.get_test_case()

            patch_connect_db.assert_not_called()
            patch_queries.assert_not_called()
            patch_format.assert_called_once_with({'message': error_msg})
            
            data = resp.get_json()
            self.assertEqual(data.get('message'), error_msg)
            #Reset mocks
            patch_format.reset_mock()
            patch_connect_db.reset_mock()
            patch_queries.reset_mock()

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "connect_data_base")
    def test_get_test_case_valid_requests(self, patch_connect_db, patch_queries, patch_format):
        endpoint_response = {
            '/test_case?id=1': {'params': [{'timeout': 2}]},
            '/test_case?name=test_timeout': {'params': [{'timeout': 2}]},
            }
        patch_format.side_effect = lambda payload: jsonify(payload)
        patch_queries.return_value = 'select params from parameters where {column} = "{value}"'
        for endpoint, response in endpoint_response.items():
            patch_connect_db.return_value = response
            patch_format.return_value = {'message': response}
            with self.app.test_request_context(endpoint):
                resp = self.api.get_test_case()

                patch_queries.assert_called_once_with(key='GET_TESTCASE_PARAMS')
                patch_format.assert_called_once_with(response)

                data = resp.get_json()
                self.assertEqual(data, response)
            #Reset mocks
            patch_format.reset_mock()
            patch_connect_db.reset_mock()
            patch_queries.reset_mock()

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "connect_data_base")
    def test_get_test_case_raise_exception(self, patch_connect_db, patch_queries, patch_format):
        patch_connect_db.side_effect = MyslApiException("Unable to execute command")
        patch_format.side_effect = lambda payload: jsonify(payload)
        patch_format.return_value = {'message': 'Unable to get the desired test case'}
        with self.app.test_request_context('/test_case?id=1'):
            resp = self.api.get_test_case()
        patch_format.assert_called_once_with({'message': 'Unable to get the desired test case'})
        patch_queries.assert_called_once_with(key='GET_TESTCASE_PARAMS')
        data = resp.get_json()
        self.assertEqual(data.get('message'), 'Unable to get the desired test case')
