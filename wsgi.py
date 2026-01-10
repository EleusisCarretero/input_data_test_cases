import os
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC

def load_mysql_config(mode: str) -> dict:
    if mode == "remote":
        return {
            "MYSQL_USER": os.environ["DB_USER"],
            "MYSQL_PASSWORD": os.environ["DB_PASS"],
            "MYSQL_HOST": os.environ["DB_HOST"],
            "MYSQL_PORT": int(os.getenv("DB_PORT", "17494")),
            "MYSQL_DB": os.environ["DB_NAME"],
        }
    else:
        return {
            "MYSQL_USER": os.getenv("DB_USER", "root"),
            "MYSQL_PASSWORD": os.getenv("DB_PASS", "root"),
            "MYSQL_HOST": os.getenv("DB_HOST", "db"),
            "MYSQL_PORT": int(os.getenv("DB_PORT", "3306")),
            "MYSQL_DB": os.getenv("DB_NAME", "ecommerce"),
        }


mode = os.getenv("DB_MODE", "remote")

app = EcommerceDataTC(load_mysql_config(mode)).app
