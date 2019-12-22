import itertools
import os
from typing import List, Dict

import docker
from pathos.pools import ProcessPool
import yaml

from .artifact import DockerArtifact
from .optim import create_build_queue

parallel = 4


class Generi:
    parameters: dict
    template_path_from_schema: str
    output_path: str
    schema_path: str
    tag: str
    _artifacts: List[DockerArtifact]

    registry: Dict[str, str]

    def __init__(self, schema_path):
        self.schema_path = schema_path
        with open(schema_path) as f:
            raw_data = yaml.load(f, Loader=yaml.FullLoader)

        self.parameters = raw_data['parameters']
        self.template_path_from_schema = raw_data['template']
        self.output_path = os.path.join(
            self.schema_directory,
            raw_data['output']
        )
        self.tag = raw_data['tag']

        self.registry = raw_data.get('registry')

        self._artifacts = []

    def write(self):
        """ Generate all files """
        for artifact in self.artifacts:
            artifact.write()

    def build(self):
        """ Build all artifacts """
        client = docker.from_env()
        queue = create_build_queue(self.artifacts, self.parameter_ordering)

        if parallel > 1:
            print(f'Start parallel build with {parallel} process at a time')
            with ProcessPool(parallel) as p:
                p.map(DockerArtifact.build, queue, [client] * len(queue))
        else:
            for artifact in queue:
                artifact.build()

    def push(self):
        """ Push all images to your registry """
        client = docker.from_env()
        client.login(
            username=self.registry['username'],
            password=self.registry.get('password', input('Please enter the password for this registry: ')),
            registry=self.registry.get('host', '')
        )

        for artifact in self.artifacts:
            artifact.push(client)

    @property
    def parameter_matrix(self):
        parameter_names = list(self.parameters.keys())
        matrix = itertools.product(*self.parameters.values())

        return [{
            parameter: mix[index]
            for index, parameter in enumerate(parameter_names)
        } for mix in matrix]

    @property
    def schema_directory(self):
        """
        Serves as the base for all paths specified
        in the schema.
        """
        return os.path.dirname(
            os.path.join(os.getcwd(), self.schema_path)
        )

    @property
    def template_path(self):
        """
        Absolute path to the templates.
        """
        return os.path.join(
            self.schema_directory,
            self.template_path_from_schema
        )

    @property
    def artifacts(self) -> List[DockerArtifact]:
        if not self._artifacts:
            self._artifacts = [DockerArtifact(
                parameters=mix,
                template_path=self.template_path,
                output_dir=self.output_path,
                tag=self.tag
            ) for mix in self.parameter_matrix]

        return self._artifacts

    @property
    def dockerfile(self):
        with open(os.path.join(self.template_path, 'Dockerfile')) as dockerfile:
            return dockerfile.readlines()

    @property
    def parameter_ordering(self):
        parameter_ordering = list()
        for line in self.dockerfile:
            parameter_ordering += [
                parameter for parameter in self.parameters
                if parameter in line and '{{' in line and parameter not in parameter_ordering
            ]
        return parameter_ordering

