from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
import pytest
import os
import yaml
import os


from test.integration_tests.db_handler import DBHandler
from test.integration_tests.docker_compose import DockerCompose


class TestEcommerceDataTCGetParamsException(Exception):
    pass


class TestEcommerceDataTCGetParams():

    @pytest.fixture(autouse=True)
    def setup_db(self):
        self.app = None
        self.client = None
        self._app_ctx = None
        self.mysql = None
        self.db_handler = None
        # import test data
        self.test_data = self._import_test_data('test_data.yml')
        # Config
        self.config = {key: os.getenv(key, value) for key, value in self.test_data['data_base'].items()}
        self.setup_app()
        yield
        self.teardown()

    def setup_app(self):
        self.app = EcommerceDataTC(config=self.config)
        self.docker_compose_hanlder = DockerCompose('docker-compose.yaml')
        self.docker_compose_hanlder.init_docker_compose()
        self.client = self.app.app.test_client()
        self.db_handler = DBHandler(app=self.app)
        self.init_database(
            self.test_data['table'],
            self.test_data['init_values']['data']
        )

    def init_database(self, table, data):
        self.db_handler.init_database(
            table=table,
            data=data
        )

    def _import_test_data(self, test_data_file):
        full_path = os.path.join(os.path.dirname(__file__), test_data_file)
        with open(full_path, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        return data
    
    def teardown(self):
        self.db_handler.teardown()
        self.docker_compose_hanlder.down_docker_compose()

    def test_get_test_case_by_id(self):
        for values in  self.test_data['init_values']['data']:
            id = values['id']
            r = self.client.get(f"/test_case?id={id}")
            assert r.status_code, 200
