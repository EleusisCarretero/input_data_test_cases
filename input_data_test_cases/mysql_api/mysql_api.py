
from flask_mysqldb import MySQL
import MySQLdb.cursors as mysql_c
from abc import abstractmethod
from input_data_test_cases.base_api import BaseApi
from input_data_test_cases.mysql_api.db_handler import ConsultTableQuery, ModifyTableQuery, SQLDBHandler


class MyslApiException(Exception):
    pass

class MysqlApi(BaseApi):

    def __init__(self, config):
        super().__init__(config)
        self.db_handler = SQLDBHandler(engine=self.client)

    def setup_client(self):
        self.app.config = {**self.app.config, **self.config}
        return MySQL(self.app)

    def connect_data_base(self, command, extra=None):
        cursor = self.client.connection.cursor(mysql_c.DictCursor)
        if extra:
            cursor.execute(command, extra)
        else:
            cursor.execute(command)
        #data = cursor.fetchone()
        data= cursor.connection.commit()
        if not data:
            raise MyslApiException("Unable to execute command")
        return data

    @abstractmethod
    def define_queries(self, key):
        raise MyslApiException("Method not implemented yet")

    def query(self, base_query, kwargs, params=()):
        response = None
        if isinstance(base_query, ConsultTableQuery):
            response = self.db_handler.consult_table(
                base_query=base_query,
                kwargs=kwargs,
                params=params
                )
            if response is None:
                raise MyslApiException("Unable to execute command")
        elif isinstance(base_query, ModifyTableQuery):
            response = self.db_handler.modify_table(
                base_query=base_query,
                kwargs=kwargs,
                params=params
            )
            if response <= 0:
                raise MyslApiException("Unable to create/delete")
        else:
            raise MyslApiException("Unknown query type")
        return response
