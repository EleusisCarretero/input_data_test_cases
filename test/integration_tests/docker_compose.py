import os
import subprocess
import time

class DockerCompose:
    def __init__(self, docker_compose_file):
        self.compose_path = os.path.abspath(docker_compose_file)
    
    def init_docker_compose(self, timeout=45):
        subprocess.check_output(['docker', 'compose', '-f', self.compose_path, 'up', '-d'])
        self.wait_for_container("my-db", timeout)

    def wait_for_container(self, container, timeout=45):
        for _ in range(timeout):
            status = subprocess.getoutput(f"docker inspect --format='{{{{.State.Health.Status}}}}' {container}")
            if status.strip("'") == "healthy":
                return True
            time.sleep(1)
        raise TimeoutError(f"{container} is not healthy on time")

    def down_docker_compose(self):
        subprocess.check_output(['docker', 'compose', 'down'])
    
    def __delattr__(self, name):
        self.down_docker_compose()