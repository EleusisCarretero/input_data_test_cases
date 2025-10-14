from flask import request
from functools import wraps
from input_data_test_cases.base_api import StatusCode
from input_data_test_cases.mysql_api.db_handler import ConsultTableQuery, ModifyTableQuery
from input_data_test_cases.mysql_api.mysql_api import MysqlApi, MyslApiException


def verify_test_case_fields(function):

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        id = request.args.get('id', None)
        name = request.args.get('name', None)
        if id is None and name is None:
            return self.format_response({'message': "Missing id or testcase name"}, status_code=StatusCode.BAD_REQUEST)
        elif id and name:
            return self.format_response({'message': "You just can choose id or name, not both"}, status_code=StatusCode.BAD_REQUEST)
        elif id:
            try:
                int(id)
            except ValueError:
                return self.format_response({'message': "ID should be an integer"}, status_code=StatusCode.BAD_REQUEST)
        elif name:
            try:
                int(name)
                return self.format_response({'message': "Name should be a string"}, status_code=StatusCode.BAD_REQUEST)
            except ValueError:
                pass
        else:
            pass
        value = id or name
        column = 'id' if id and not name else 'name'
        return function(self, value, column, *args, **kwargs)
    return wrapper


class EcommerceDataTCException(Exception):
    pass


class EcommerceDataTC(MysqlApi):
    TABLE_NAME = "parameters"

    def __init__(self, config):
        super().__init__(config)

    def define_routes(self):
        self.app.add_url_rule("/",view_func=self.home)
        self.app.add_url_rule("/test_case",endpoint="get_test_case",view_func=self.get_test_case,methods=["GET"])
        self.app.add_url_rule("/test_case",endpoint="post_test_case",view_func=self.post_test_case,methods=["POST"])
        self.app.add_url_rule("/test_case",endpoint="delete_test_case",view_func=self.delete_test_case,methods=["DELETE"])
        self.app.add_url_rule("/test_case",endpoint="update_test_case",view_func=self.update_test_case,methods=["PUT"])


    def define_queries(self, key):
        return {
            'GET_TESTCASE_PARAMS': ConsultTableQuery.WHERE_COLUMN_EQUALS,
            'POST_TESTCASE_PARAMS': ModifyTableQuery.INSERT_NEW_VALUE_BASE_QUERY,
            'DELETE_TEST_CASE': ModifyTableQuery.DELETE_VALUE_WHERE_COLUMN_EQUALS,
            'UPDATE_TEST_CASE': ModifyTableQuery.UPDATE_VALUE_WHERE_COLUMN_EQUALS
        }.get(key, None)

    def home(self):
        return self.format_response({'message': "Base url"}, status_code=StatusCode.OK)

    @verify_test_case_fields
    def get_test_case(self, value, column):
        response = {}
        try:
            base_query = self.define_queries(key='GET_TESTCASE_PARAMS')
            response = self.query(
                base_query=base_query,
                kwargs={'table_name': self.TABLE_NAME,'column': column, 'value':value},
            )
            status_code = StatusCode.OK
        except MyslApiException:
            response = {'message': 'Unable find the desired test case'}
            status_code = StatusCode.NOT_FOUND
        return self.format_response(response, status_code=status_code)

    def post_test_case(self):
        name = request.form.get('name', None)
        params = request.form.get('params', None)
        if name is None or params is None:
            return self.format_response({'message': 'Missing arguments'}, status_code=StatusCode.BAD_REQUEST)
        columns = "name, params"
        values =  [name, str(params)]
        placeholders = ",".join(["%s"] * len(values))  # %s,%s,%s
        base_query = self.define_queries(key='POST_TESTCASE_PARAMS')
        try:
            self.query(
                base_query=base_query,
                kwargs={'table_name': self.TABLE_NAME,'columns': columns, 'placeholders':placeholders},
                params=values
            )
            response = {'message': "New test case added successfully"}
            status_code = StatusCode.OK
        except MyslApiException:
            response = {'message': 'Unable created the new test case'}
            status_code = StatusCode.NOT_FOUND
        return self.format_response(response, status_code=status_code)

    @verify_test_case_fields
    def delete_test_case(self, value, column):
        response = {}
        try:
            base_query = self.define_queries(key='DELETE_TEST_CASE')
            self.query(
                base_query=base_query,
                kwargs={'table_name': self.TABLE_NAME,'column': column, 'value':value},
            )
            response = {'message': 'Test case deleted successfully'}
            status_code = StatusCode.OK
        except MyslApiException:
            response = {'message': 'Unable deleted the desired test case'}
            status_code = StatusCode.NOT_FOUND
        return self.format_response(response, status_code=status_code)
    
    @verify_test_case_fields
    def update_test_case(self, value, column):
        response = {}
        data = {}
        for field in ['name', 'params']:
            v = request.form.get(field, None)
            if v is not None:
                data.update({field: v})
        try:
            base_query = self.define_queries(key='UPDATE_TEST_CASE')
            updates = ",".join([f"{k} = '{v}'" for k, v in data.items()])
            self.query(
                base_query=base_query,
                kwargs={'table_name': self.TABLE_NAME,'updates': updates, 'value':value, 'column': column},
            )
            response = {'message': 'Test case deleted successfully'}
            status_code = StatusCode.OK
        except MyslApiException:
            response = {'message': 'Unable deleted the desired test case'}
            status_code = StatusCode.NOT_FOUND
        return self.format_response(response, status_code=status_code)


if __name__ == "__main__":
    config = {
        'MYSQL_HOST': "shuttle.proxy.rlwy.net",
        'MYSQL_USER': "root",
        'MYSQL_PASSWORD': "EdUDAyFiRRaDKBjPKHwBCXbelEChMHES",
        'MYSQL_DB': "railway",
        'MYSQL_PORT':28374
    }
    mysqlapi = EcommerceDataTC(config=config)
    mysqlapi.run(debug=True)
