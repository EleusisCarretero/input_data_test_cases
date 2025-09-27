
from flask_mysqldb import MySQL
import MySQLdb.cursors as mysql_c
from abc import abstractmethod
from input_data_test_cases.base_api import BaseApi


class MyslApiException(Exception):
    pass

class MysqlApi(BaseApi):

    def setup_client(self):
        self.app.config = {**self.app.config, **self.config}
        return MySQL(self.app)

    def connect_data_base(self, command):
        cursor = self.client.connection.cursor(mysql_c.DictCursor)
        cursor.execute(command)
        data = cursor.fetchone()
        if not data:
            raise MyslApiException("Unable to execute command")
        return data

    @abstractmethod
    def define_queries(self, key):
        raise MyslApiException("Method not implemented yet")
