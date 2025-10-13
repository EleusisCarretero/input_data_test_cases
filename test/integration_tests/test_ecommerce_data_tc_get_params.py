import time
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
import pytest
import os
from flask_sqlalchemy import SQLAlchemy
import subprocess
import yaml
import os
import json


class TestEcommerceDataTCGetParamsException(Exception):
    pass


class TestEcommerceDataTCGetParams():
    CREATE_TABLE_BASE_QUERY = "CREATE TABLE IF NOT EXISTS {table_name}({columns_to_insert})"
    INSERT_NEW_VALUE_BASE_QUERY = "INSERT INTO parameters ({columns}) VALUES ({placeholders})"

    @pytest.fixture(autouse=True)
    def setup_db(self):
        self.app = None
        self.client = None
        self._app_ctx = None
        self.mysql = None
        # import test data
        self.test_data = self._import_test_data('test_data.yml')
        # init docker compose
        self.init_docker_compose()
        # Config
        self.config = {key: os.getenv(key, value) for key, value in self.test_data['data_base'].items()}
        self.setup_app()
        self.init_database(
            self.test_data['table'],
            self.test_data['init_values']['data']
            )
        yield
        self._app_ctx.pop()
        self.teardown()

    def setup_app(self):
        self.app = EcommerceDataTC(config=self.config)
        self.client = self.app.app.test_client()
        self._app_ctx = self.app.app.app_context()
        self._app_ctx.push()
        self.mysql = self.app.client
        self._wait_for_mysql_ready(max_seconds=30)
    
    def _wait_for_mysql_ready(self, max_seconds=30):
        import MySQLdb
        start = time.time()
        while True:
            try:
                cur = self.mysql.connection.cursor()
                cur.execute("SELECT 1")
                cur.fetchall()
                cur.close()
                return
            except Exception:
                if time.time() - start > max_seconds:
                    raise
                time.sleep(1)

    def init_database(self, table, data):

        try:
            cur = next(self._handle_cursor())
        except Exception as e:
            raise TestEcommerceDataTCGetParamsException("Unable to create cursor") from e

        self._create_db(
            cur=cur,
            table_name=table['name'],
            columns=table['columns']
        )
        self._insert_values_db(
            cur=cur,
            data=data
        )
    
    def _create_db(self, cur, table_name, columns):
        columns_to_insert = ""
        for i, column in enumerate(columns):
            cmd = " ".join([column['name'], column['type']])
            if column['type'].upper() == 'VARCHAR':
                cmd= f"{cmd}({column.get('length', 255)})"
            if column.get('primary', False):
                cmd+= ' PRIMARY KEY'
            if i < len(columns) - 1:
                columns_to_insert += cmd + "," 
            else:
                columns_to_insert += cmd
        self._query_cmd(
            cur=cur,
            base_query=self.CREATE_TABLE_BASE_QUERY,
            kwarg={'table_name':table_name, 'columns_to_insert':columns_to_insert},
        )
    
    def _insert_values_db(self, cur, data):
        for datum in data:
            columns = ",".join(map(str, list(datum.keys())))
            values = []
            for v in datum.values():
                if isinstance(v, (dict, list)):
                    values.append(json.dumps(v))
                else:
                    values.append(v)
            placeholders = ",".join(["%s"] * len(values))  # %s,%s,%s
            self._query_cmd(
                cur=cur,
                base_query=self.INSERT_NEW_VALUE_BASE_QUERY,
                kwarg={'columns':columns, 'placeholders':placeholders},
                extra=values
            )

    def _handle_cursor(self):
        cur = self.mysql.connection.cursor()
        yield cur
        cur.close()

    def _query_cmd(self, cur, base_query, kwarg, extra=None):
        cmd = base_query.format(**kwarg)
        if extra:
            cur.execute(cmd, tuple(extra))
        else:
            cur.execute(cmd)
        self.mysql.connection.commit()

    def _import_test_data(self, test_data_file):
        full_path = os.path.join(os.path.dirname(__file__), test_data_file)
        with open(full_path, 'r') as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        return data

    def init_docker_compose(self):
        compose_path = os.path.abspath("docker-compose.yaml")
        subprocess.check_output(['docker', 'compose', '-f', compose_path, 'up', '-d'])

    def down_docker_compose(self):
        subprocess.check_output(['docker', 'compose', 'down'])
    
    def teardown(self):
        self.down_docker_compose()

    def test_get_test_case_by_id(self):
        for values in  self.test_data['init_values']['data']:
            id = values['id']
            r = self.client.get(f"/test_case?id={id}")
            assert r.status_code, 200
