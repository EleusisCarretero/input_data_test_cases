import unittest
from flask import jsonify
from unittest.mock import patch, Mock
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC



class TestEcommerceDataTC(unittest.TestCase):
    def setUp(self):
        self.api = EcommerceDataTC(config={})
        self.app = self.api.app

    @patch.object(EcommerceDataTC, "format_response")
    @patch.object(EcommerceDataTC, "define_queries")
    @patch.object(EcommerceDataTC, "connect_data_base")
    def test_get_test_case_invalid_requests(self, patch_connect_db, patch_queries,patch_format):
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

