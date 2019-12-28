import os
from typing import Dict, Optional, List
from pathlib import Path

import aiodocker
from aiodocker.exceptions import DockerError
from jinja2 import Template, Environment, FileSystemLoader

from .config import Config
from .context import create_tar


class DockerArtifact:
    config: Config
    parameters: dict
    name: str
    template_path: Path
    output_path: Path

    ordered_parameters: Optional[list]

    def __init__(self, parameters: dict, config: Config):
        self.config = config
        self.parameters = parameters

        self.template_path = (
            config.base_path /
            Template(config.template).render(**parameters)
        ).resolve()

        self.output_path = config.base_path / os.path.normpath(
            Template(config.output).render(**parameters)
        )

        self.context_path = (
            config.base_path /
            Template(config.context).render(**parameters)
        ).resolve() if config.context else self.output_path

        self.name = Template(config.name).render(**parameters)

    def write(self):
        """ Render and write all templates to their desired path. """
        print(f'Write {self.tag} to {self.output_path}')
        for file, template in self.templates.items():
            content = template.render(**self.parameters)

            if not self.output_path.exists():
                os.makedirs(str(self.output_path))

            with (self.output_path / file).open('w+') as f:
                f.write(content)

    async def build(self, client: aiodocker.Docker):
        """ Build image """
        f = create_tar(self.context_path)

        dockerfile_path = self.output_path / 'Dockerfile'
        if not dockerfile_path.exists():
            print(f'There is no dockerfile in {self.output_path}')
            pass

        relative_dockerfile_path = dockerfile_path.relative_to(self.context_path)

        try:
            # print(f'Start building {self.name}')
            await client.images.build(
                tag=self.name,
                fileobj=f,
                path_dockerfile=relative_dockerfile_path,
                encoding="gzip",
            )
        except DockerError as e:
            print(f'Error building image {self.name}')
            print(f'> {e.message}')
        else:
            # print(f'Finished building {self.name}')
            pass

        return self

    async def push(self, client: aiodocker.Docker, auth: dict):
        """ Push image to registry """
        print(f'Start pushing {self.tag}')

        await client.images.push(name=self.repository, tag=self.tag, auth=auth)
        print(f'Finished pushing {self.tag}')

    @property
    def templates(self) -> Dict[str, Template]:
        """
        Returns a dictionary with all templates that belong to an artifact.

        The keys are the names of the files and the values are the templates to be rendered.
        """
        if self.template_path.is_dir():
            env = Environment(loader=FileSystemLoader(str(self.template_path)))
            return {
                file.name: env.get_template(file.name)
                for file in self.template_path.iterdir()
            }
        else:
            with self.template_path.open() as f:
                return {
                    self.template_path.name: Template(f.read())
                }

    @property
    def repository(self):
        return self.name.split(':', 1)[0]

    @property
    def tag(self):
        return self.name.split(':', 1)[1]

    @staticmethod
    def load(config: Config) -> List['DockerArtifact']:
        """
        Return the list of artifacts.
        """
        return [DockerArtifact(
            parameters=combination,
            config=config
        ) for combination in config.parameter_matrix]
