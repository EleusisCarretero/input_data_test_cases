"""
Functional integration tests for the EcommerceDataTC API.

This module:
- Spins up dependencies via Docker Compose (e.g., database).
- Seeds the database with known values.
- Validates API responses using Flask's test client.
"""
import os
from typing import Any, Dict, List

import pytest
import yaml

from input_data_test_cases.mysql_api.ecommerce_data_test_cases import (
    ecommerce_data_tc as ec_data
)
from test.integration_tests.docker_compose import DockerCompose


class TestEcommerceDataTCGetParams:
    """
    Integration tests for validating retrieval of test case parameters.

    General flow:
    - Start required services with Docker Compose.
    - Initialize the database with seed data.
    - Use Flask test client to send requests to the API.
    """

    @pytest.fixture(autouse=True)
    def setup_db(self) -> None:
        """
        Autouse fixture that prepares and tears
        down the environment
        for each test.

        - Loads test data from YAML and environment
        variables.
        - Starts services with Docker Compose and
        creates the Flask app.
        - Seeds the database with initial
        records.
        - Tears down by closing DB connections
        and stopping Docker Compose.
        """
        self.test_data = self._import_test_data("test_data.yml")
        self.config = {
            key: os.getenv(key, value)
            for key, value in self.test_data["data_base"].items()
        }
        self._setup_app()
        yield
        self._teardown()

    def _setup_app(self) -> None:
        """
        Start Docker Compose services and set up
        the Flask test application.

        Creates:
            - self.docker_compose_handler
            - self.app (wrapper that holds the Flask app)
            - self.client (Flask test client)
            - self.db_handler (database handler)
        """
        self.docker_compose_handler = DockerCompose("docker-compose.yaml")
        self.docker_compose_handler.init_docker_compose()
        self.app = ec_data.EcommerceDataTC(config=self.config)
        self.client = self.app.app.test_client()
        self.db_handler = self.app.db_handler
        self._init_database(
            table=self.test_data["table"],
            data=self.test_data["init_values"]["data"],
        )

    def _init_database(self, table: str, data: List[Dict[str, Any]]) -> None:
        """
        Seed the database with initial test data.

        Args:
            table: Name of the target table.
            data: List of records (dicts) to insert.
        """
        self.db_handler.init_database(table=table, data=data)

    def _import_test_data(self, test_data_file: str) -> Dict[str, Any]:
        """
        Load and parse the YAML file containing test data.

        Args:
            test_data_file: File name of the YAML
            file (relative to this directory).

        Returns:
            Dictionary with database config,
            table name, and seed data.
        """
        full_path = os.path.join(os.path.dirname(__file__), test_data_file)
        with open(full_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data

    def _teardown(self) -> None:
        """
        Clean up resources after each test.

        - Close the database handler.
        - Bring down Docker Compose services.
        """
        self.db_handler.close()
        self.docker_compose_handler.down_docker_compose()

    def test_get_test_case_by_id(self) -> None:
        """
        Validate that each seeded record is retrievable
        by its ID through the API.

        For each record in the initial dataset:
        - Call GET /test_case?id=<id>
        - Assert that the response has HTTP 200 OK status.
        """
        for values in self.test_data["init_values"]["data"]:
            case_id = values["id"]
            resp = self.client.get(f"/test_case?id={case_id}")
            assert resp.status_code == 200
