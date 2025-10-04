import time
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
import pytest
import os
from flask_sqlalchemy import SQLAlchemy
import subprocess

class TestEcommerceDataTCGetParams():

    @pytest.fixture(autouse=True)
    def setup_db(self):
        # Config
        self.config = {
            'MYSQL_HOST': os.getenv("TEST_HOST", "127.0.0.1"),
            'MYSQL_USER': os.getenv("TEST_USER", "root"),
            'MYSQL_PASSWORD': os.getenv("TEST_PSSW", "root"),
            'MYSQL_DB': os.getenv("TEST_DB", "testdb"),
            'MYSQL_PORT': int(os.getenv("TEST_PORT", 3306)),
        }

        self.app = EcommerceDataTC(config=self.config)
        self.client = self.app.app.test_client()

        self.init_docker_compose()

        self._app_ctx = self.app.app.app_context()
        self._app_ctx.push()

        self.mysql = self.app.client  # tu wrapper MySQL(self.app)

        self._wait_for_mysql_ready(max_seconds=30)

        cur = self.mysql.connection.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users(
                id INT PRIMARY KEY,
                name VARCHAR(255)
            )
        """)
        cur.execute("REPLACE INTO users (id, name) VALUES (1, 'Kiki')")
        self.mysql.connection.commit()
        cur.close()

        yield

        self._app_ctx.pop()
        self.teardown()


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
    
    def init_docker_compose(self):
        subprocess.check_output(['docker', 'compose', '-f', 'E:\\11)_Eleusis_Git_Stuf\\input_data_test_cases\\docker-compose.yaml', 'up', '-d'])

    def down_docker_compose(self):
        subprocess.check_output('docker compose down')
    
    def teardown(self):
        self.down_docker_compose()

    def test_get_test_case_by_id(self):
        r = self.client.get("/users")
        assert r.status_code, 200
        assert "Kiki" in r.get_data(as_text=True)
