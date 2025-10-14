import time
import json
from enum import Enum
from flask_mysqldb import MySQL


class ModifyTableQuery(str, Enum):
    CREATE_TABLE_BASE_QUERY = "CREATE TABLE IF NOT EXISTS {table_name}({columns_to_insert})"
    INSERT_NEW_VALUE_BASE_QUERY = "INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    DELETE_VALUE_WHERE_COLUMN_EQUALS = 'DELETE FROM {table_name} where {column} = "{value}"'
    UPDATE_VALUE_WHERE_COLUMN_EQUALS = 'UPDATE {table_name} set {updates} where {column} = "{value}"'


class ConsultTableQuery(str, Enum):
    WHERE_COLUMN_EQUALS = 'select params from {table_name} where {column} = "{value}"',


class SQLDBHandlerException(Exception):
    pass


class SQLDBHandler():
   

    def __init__(self, engine):
        self.engine = engine
        self.param_symbol = "%s" if isinstance(engine, MySQL) else "?"
        self._app_ctx = self.engine.app.app_context()
        self._app_ctx.push()
        self.conn = engine.connect
        self.cursor =  self.conn.cursor()
        self._wait_for_mysql_ready(max_seconds=60)
    
    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def commit(self):
        self.conn.commit()
    
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()
        self.conn.close()

    def _wait_for_mysql_ready(self, max_seconds=30):
        start = time.time()
        while True:
            try:
                self.cursor.execute("SELECT 1")
                self.fetchall()
                return
            except Exception:
                if time.time() - start > max_seconds:
                    raise
                time.sleep(1)
    
    def modify_table(self, base_query:ModifyTableQuery, kwargs, params=()):
        self._query_cmd(
            base_query=base_query,
            kwargs=kwargs,
            params=params
        )
        self.commit()
        return self.rowcount()
    
    def consult_table(self, base_query:ConsultTableQuery, kwargs, params=()):
        self._query_cmd(
            base_query=base_query,
            kwargs=kwargs,
            params=params
        )
        return self.fetchone()

    def _query_cmd(self, base_query, kwargs, params):
        query = base_query.format(**kwargs)
        self.cursor.execute(query, params)
    
    def init_database(self, table, data):
        self.create_db(
            table_name=table['name'],
            columns=table['columns']
        )
        self.insert_new_value(
            table_name=table['name'],
            data=data
        )
    
    def create_db(self, table_name, columns):
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
        self.modify_table(
            base_query=ModifyTableQuery.CREATE_TABLE_BASE_QUERY,
            kwargs={'table_name':table_name, 'columns_to_insert':columns_to_insert},
        )

    def insert_new_value(self, table_name, data):
        for datum in data:
            columns = ",".join(map(str, list(datum.keys())))
            values = []
            for v in datum.values():
                if isinstance(v, (dict, list)):
                    values.append(json.dumps(v))
                else:
                    values.append(v)
            placeholders = ",".join([self.param_symbol] * len(values))  # %s,%s,%s
            self.modify_table(
                base_query=ModifyTableQuery.INSERT_NEW_VALUE_BASE_QUERY,
                kwargs={'table_name':table_name,'columns':columns, 'placeholders':placeholders},
                params=values
            )
