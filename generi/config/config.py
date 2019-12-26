from dataclasses import dataclass
import itertools
from pathlib import Path
from typing import Optional, List, Dict

import yaml

from .registry import Registry


# Type for strings that still have to be rendered
# using jinja
JinjaString = str


@dataclass
class Config:
    # Set of parameters configured in the yaml file
    parameters: dict

    # Path to the template, relative to config file
    template: JinjaString

    # Path to the output location, relative to config file
    output: JinjaString

    # Name of the image
    name: JinjaString

    # Registry to which the images should be pushed
    registry: Optional[Registry]

    # Path of the config file
    path: Path

    # Amount of images that are built in parallel
    parallel: int = 4

    @staticmethod
    def load(path: Path) -> 'Config':
        """ Read in a config from a given config file """
        with path.open() as f:
            raw = yaml.load(f, Loader=yaml.FullLoader)

        try:
            return Config(
                path=path,
                parameters=raw['parameters'],
                template=raw['template'],
                output=raw['output'],
                name=raw['image'],
                registry=Registry.load(raw)
            )
        except IndexError:
            raise ValueError('Your schema is invalid')

    @property
    def parameter_matrix(self) -> List[Dict[str, str]]:
        """ Matrix of all parameters """
        parameter_names = list(self.parameters.keys())
        matrix = itertools.product(*self.parameters.values())

        return [{
            parameter: mix[index]
            for index, parameter in enumerate(parameter_names)
        } for mix in matrix]

    @property
    def base_path(self) -> Path:
        """
        Directory in which the config is stored. Serves as the base for all
        paths defined inside the config file.
        """
        return (Path.cwd() / self.path).parent

    @property
    def dockerfile(self) -> List[str]:
        """
        Return the used dockerfile as lines.
        """
        with (self.base_path / self.template / 'Dockerfile').open() as dockerfile:
            return dockerfile.readlines()

