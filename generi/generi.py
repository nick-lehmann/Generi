import itertools
import os
from typing import List

import yaml

from .artifact import DockerArtifact


class Generi:
    parameters: dict
    template_path_from_schema: str
    output_path: str
    schema_path: str
    tag: str
    _artifacts: List[DockerArtifact]

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

        self._artifacts = []

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

    def write(self):
        """ Generate all files """
        for artifact in self.artifacts:
            artifact.write()

    def build(self):
        """ Build all artifacts """
        for artifact in self.artifacts:
            artifact.build()
