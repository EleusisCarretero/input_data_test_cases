"""
Behave environment setup for functional tests.

Initializes all shared resources:
- Logger and result managers
- Docker Compose environment
- MySQL test database
- HTTP session for API requests

The configuration is loaded from:
- `data/test_data.yml` for defaults
- Environment variables (override)
"""

import os
from pathlib import Path

from test_utils.logger_manager import LoggerManager
from test_utils.result_manager import ResultManagerClass
from test.utils.utils import DockerCompose, RestAdapter, import_test_data
from input_data_test_cases.mysql_api.db_handler import SQLDBHandler
from input_data_test_cases.mysql_api.ecommerce_data_test_cases.ecommerce_data_tc import EcommerceDataTC


def before_all(context):
    """
    Global setup hook executed once before all features.

    Loads test configuration, initializes Docker, database, session,
    and logging utilities, making them available via the `context` object.
    """
    # Load YAML test data
    base_dir = Path(__file__).parent
    test_data = import_test_data(base_dir, "data/test_data.yml")

    # Merge with environment variables
    db_config = {
        key: os.getenv(key, value)
        for key, value in test_data["data_base"].items()
    }

    # Initialize logger and result helper
    context.logger = LoggerManager.get_logger("step_logger")
    context.result = ResultManagerClass()

    # Initialize Docker environment
    context.docker_compose_handler = DockerCompose("docker-compose.yaml")
    context.logger.info("Starting Docker environment...")
    context.docker_compose_handler.init_docker_compose()

    # Initialize test database
    context.logger.info("Setting up test database...")
    db_client = EcommerceDataTC(config=db_config).client
    context.db_handler = SQLDBHandler(engine=db_client)
    context.db_handler.init_database(
        table=test_data["table"],
        data=test_data["init_values"]["data"],
    )

    # Initialize HTTP session
    context.session = RestAdapter()
    context.logger.info("Environment setup completed successfully.")
    # Global Constants
    context.custom_tags = {}

def before_tag(context, tag):
    if '=' in tag:
        context.logger.info(f"Custom tag {tag}")
        value, key = tag.split('=')
        context.custom_tags.update({value: key})

def before_feature(context, feature):
    # Get tags
    context.timeout = int(context.custom_tags.get('timeout', 5))

def after_all(context):
    """
    Global teardown hook executed once after all features.

    Cleans up resources such as database connections and Docker containers.
    """
    context.logger.info("Tearing down test environment...")

    # Close database connection
    if getattr(context, "db_handler", None):
        context.db_handler.close()
        context.logger.info("Database connection closed.")

    # Stop Docker containers
    if getattr(context, "docker_compose_handler", None):
        context.docker_compose_handler.down_docker_compose()
        context.logger.info("Docker environment stopped.")

    # Close HTTP session
    if getattr(context, "session", None):
        context.session.session.close()
        context.logger.info("HTTP session closed.")

    context.logger.info("Environment teardown completed.")
