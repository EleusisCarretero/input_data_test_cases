import time
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
import pytest
import os
from flask_sqlalchemy import SQLAlchemy

class TestEcommerceDataTCGetParams():

    def setup(self):
        self.config = {
        'MYSQL_HOST': os.getenv("TEST_HOST", "127.0.0.1"),
        'MYSQL_USER':  os.getenv("TEST_USER", "root"),
        'MYSQL_PASSWORD':  os.getenv("TEST_PSSW", "root"),
        'MYSQL_DB':  os.getenv("TEST_DB", "testdb"),
        'MYSQL_PORT': os.getenv("TEST_PORT", 3306)
        }
        self.app = EcommerceDataTC(config=self.config)
        self.db = SQLAlchemy(self.app.app)
        time.sleep(2)
        self.client = self.app.app.test_client()
        with self.app.app.app_context():
            self.db.create_all()
            self.db.session.execute("INSERT INTO users (id,name) VALUES (1,'Kiki')")
            self.db.session.commit()
    
    def teardown(self):
        with self.app.app.app_context():
             self.db.drop_all()


    def test_get_test_case_by_id(self):
        r = self.client.get("/users")
        assert r.status_code, 200
        assert "Kiki" in r.get_data(as_text=True)
