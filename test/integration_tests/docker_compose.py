import os
import subprocess

class DockerCompose:
    def __init__(self, docker_compose_file):
        self.compose_path = os.path.abspath(docker_compose_file)
    
    def init_docker_compose(self):
        subprocess.check_output(['docker', 'compose', '-f', self.compose_path, 'up', '-d'])

    def down_docker_compose(self):
        subprocess.check_output(['docker', 'compose', 'down'])