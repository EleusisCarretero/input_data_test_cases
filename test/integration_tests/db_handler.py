import time
import json


class DBHandlerException(Exception):
    pass


class DBHandler():
    CREATE_TABLE_BASE_QUERY = "CREATE TABLE IF NOT EXISTS {table_name}({columns_to_insert})"
    INSERT_NEW_VALUE_BASE_QUERY = "INSERT INTO parameters ({columns}) VALUES ({placeholders})"

    def __init__(self, app):
        self._app_ctx = app.app.app_context()
        self._app_ctx.push()
        self.mysql = app.client
        self._wait_for_mysql_ready(max_seconds=30)

    def teardown(self):
        self._app_ctx.pop()
    
    def _wait_for_mysql_ready(self, max_seconds=30):
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
    
    def init_database(self, table, data):

        try:
            cur = next(self._handle_cursor())
        except Exception as e:
            raise DBHandlerException("Unable to create cursor") from e

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
