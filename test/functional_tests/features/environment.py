
import os
import requests
from test_utils.logger_manager import LoggerManager
from test_utils.result_manager import ResultManagerClass
from test.utils.utils import DockerCompose, import_test_data
from input_data_test_cases.mysql_api.db_handler import SQLDBHandler
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC

def before_all(context):
    test_data = import_test_data(os.path.dirname(__file__), "data\\test_data.yml")
    config = {
        key: os.getenv(key, value)
        for key, value in test_data["data_base"].items()
    }
    context.logger = LoggerManager.get_logger('step_logger')
    context.result = ResultManagerClass()
    context.docker_compose_handler = DockerCompose("docker-compose.yaml")
    context.docker_compose_handler.init_docker_compose()
    context.db_handler = SQLDBHandler(engine=EcommerceDataTC(config=config).client)
    context.db_handler.init_database(table=test_data['table'], data=test_data['init_values']['data'])
    context.session = requests.Session()

def after_all(context):
    context.db_handler.close()
    context.docker_compose_handler.down_docker_compose()