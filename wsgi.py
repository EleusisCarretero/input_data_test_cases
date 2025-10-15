from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC
config = {
        'MYSQL_HOST': "shuttle.proxy.rlwy.net",
        'MYSQL_USER': "root",
        'MYSQL_PASSWORD': "EdUDAyFiRRaDKBjPKHwBCXbelEChMHES",
        'MYSQL_DB': "railway",
        'MYSQL_PORT':28374
    }
app = EcommerceDataTC(config).app  # <- importante: exponer "app"

