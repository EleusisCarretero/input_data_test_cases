
from flask import request
from input_data_test_cases.mysql_api.mysql_api import MysqlApi

class EcommerceDataTCException(Exception):
    pass

class EcommerceDataTC(MysqlApi):

    def __init__(self, config):
        super().__init__(config)
    
    def define_routes(self):
        self.app.add_url_rule("/",view_func=self.home)
        self.app.add_url_rule("/test_case",endpoint="get_test_case",view_func=self.get_test_case,methods=["GET"])
    
    def define_queries(self, key):
        return {
            'GET_TESTCASE_PARAMS': 'select params from parameters where {column} = "{value}"'
        }.get(key)
    
    def home(self):
        return self.format_response({'message': "Base url"})

    def get_test_case(self):
        response = {}
        id = request.args.get('id', None)
        name = request.args.get('name', None)
        if id is None and name is None:
            return self.format_response({'message': "Missing id or testcase name"})
        elif id and name:
            return self.format_response({'message': "You just can choose id or name, not both"})
        elif id:
            try:
                int(id)
            except ValueError:
                return self.format_response({'message': "ID should be an integer"})
        elif name:
            try:
                int(name)
                return self.format_response({'message': "Name should be a string"})
            except ValueError:
                pass
        value = id or name
        column = 'id' if id and not name else 'name'
        try:
            base_command = self.define_queries(key='GET_TESTCASE_PARAMS')
            response = self.connect_data_base(command=base_command.format(column=column,value=value))
        except EcommerceDataTCException:
            response = {'message': 'Unable to get the desired test case'}
        return self.format_response(response)
    
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