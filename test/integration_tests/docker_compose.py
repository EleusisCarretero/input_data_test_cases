"""
Docker compose class
"""
import os
import time
import subprocess
from enum import StrEnum

class CompCmd(StrEnum):
    UP = \
        'docker,compose,-f,{compose_path},up,-d'
    DOWN = \
        'docker,compose,down'
    INSP = \
        ("docker inspect --format="
        "'{{{{.State.Health.Status}}}}' {container}")


class DockerCompose:
    """
    Helper class to manage a Docker Compose environment programmatically.

    Provides methods to start, stop, and wait for containers defined in a
    Docker Compose file. Useful in integration tests or automated setups
    where you need to spin up dependent services (e.g., databases) before
    running your test suite.
    """

    def __init__(self, docker_compose_file: str):
        """
        Initialize the DockerCompose helper.

        Args:
            docker_compose_file (str): Path to the Docker
            Compose YAML file.
        """
        self.compose_path = os.path.abspath(docker_compose_file)
    
    @staticmethod
    def _convert_list(cmd, c=","):
        return cmd.split(c)

    def init_docker_compose(self, timeout: int = 45):
        """
        Start the Docker Compose environment in detached mode and
        wait for the database container to become healthy.

        Args:
            timeout (int, optional): Maximum time in seconds
            to wait for the "my-db" container to reach a healthy state.
            Defaults to 45.

        Raises:
            subprocess.CalledProcessError:
                If the `docker compose up` command fails.
            TimeoutError:
                If the container is not healthy within
                the given timeout.
        """
        cmd = CompCmd.UP.format(compose_path=self.compose_path)
        subprocess.check_output(
            self._convert_list(cmd)
        )
        self.wait_for_container("my-db", timeout)

    def wait_for_container(
            self,
            container: str,
            timeout: int = 45
        ) -> bool:
        """
        Poll a container's health status until it becomes healthy
            or timeout is reached.

        Args:
            container (str): Name or ID of the container to check.
            timeout (int, optional): Maximum time in seconds to wait.
            Defaults to 45.

        Returns:
            bool: True if the container is healthy before timeout.

        Raises:
            TimeoutError: If the container does not become healthy
            within the given timeout.
        """
        cmd = CompCmd.INSP.format(container=container)
        for _ in range(timeout):
            status = subprocess.getoutput(
                cmd
            )
            if status.strip("'") == "healthy":
                return True
            time.sleep(1)
        raise TimeoutError(f"{container} is not healthy on time")

    def down_docker_compose(self):
        """
        Stop and remove the Docker Compose environment, including containers,
        networks, and volumes defined in the compose file.

        Raises:
            subprocess.CalledProcessError:
                If the `docker compose down` command fails.
        """
        cmd = CompCmd.DOWN
        subprocess.check_output(
            self._convert_list(cmd)
        )

    def __delattr__(self, name: str):
        """
        Ensure Docker Compose environment is cleaned up when 
        the attribute is deleted. Calls `docker compose down`.

        Args:
            name (str): The attribute name being deleted.
        """
        self.down_docker_compose()
