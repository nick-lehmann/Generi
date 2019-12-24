import os
from dataclasses import dataclass
import itertools
from typing import Optional, List

import yaml


@dataclass
class Registry:
    username: str
    host: str = None
    password: str = None

    @staticmethod
    def load(raw: dict) -> Optional['Registry']:
        try:
            registry = raw['registry']
            return Registry(
                host=registry.get('host'),
                username=registry['username'],
                password=registry.get('password')
            )
        except IndexError:
            return None


@dataclass
class Config:
    parameters: dict
    template: str
    output: str
    tag: str
    registry: Optional[Registry]
    schema_path: str

    @staticmethod
    def load(schema_path) -> 'Config':
        with open(schema_path) as f:
            raw = yaml.load(f, Loader=yaml.FullLoader)

        try:
            return Config(
                schema_path=schema_path,
                parameters=raw['parameters'],
                template=raw['template'],
                output=raw['output'],
                tag=raw['tag'],
                registry=Registry.load(raw)
            )
        except IndexError:
            raise ValueError('Your schema is invalid')

    @property
    def parameter_matrix(self):
        """ Matrix of all parameters """
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
            self.template
        )

    @property
    def dockerfile(self) -> List[str]:
        """
        Return the used dockerfile as lines.
        """
        with open(os.path.join(self.template_path, 'Dockerfile')) as dockerfile:
            return dockerfile.readlines()

