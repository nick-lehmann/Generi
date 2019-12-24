import os
import tarfile
import tempfile
from typing import Dict, Optional, List

import aiodocker
from jinja2 import Template, Environment, FileSystemLoader

from .config import Config


class DockerArtifact:
    config: Config
    parameters: dict
    name: str
    template_path: str
    output_path: str

    ordered_parameters: Optional[list]

    def __init__(self, parameters: dict, config: Config):
        self.config = config
        self.parameters = parameters

        self.template_path = os.path.normpath(
            Template(config.template_path).render(**parameters)
        )
        self.output_path = os.path.normpath(
            Template(config.output).render(**parameters)
        )
        self.name = Template(config.name).render(**parameters)

    def write(self):
        """
        Render all templates and write them to their desired path.
        """
        for file, template in self.templates.items():
            content = template.render(**self.parameters)

            if not os.path.exists(self.output_path):
                os.makedirs(self.output_path)

            output_path = os.path.join(self.output_path, file)
            with open(output_path, 'w+') as f:
                f.write(content)

    async def build(self, client: aiodocker.Docker):
        """ Build image """
        f = tempfile.NamedTemporaryFile()
        tar = tarfile.open(mode="w:gz", fileobj=f)
        context_path = self.output_path + '/'

        print(f'Start building {self.tag} from {context_path}')

        for file in os.listdir(context_path):
            print(f'Adding {os.path.join(context_path, file)}')
            tar.add(os.path.join(context_path, file), arcname=file)

        tar.close()
        f.seek(0)

        await client.images.build(fileobj=f, encoding="gzip", tag=self.tag)
        print(f'Finished building {self.tag}')
        tar.close()

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
        if os.path.isdir(self.template_path):
            env = Environment(loader=FileSystemLoader(self.template_path))
            return {
                file: env.get_template(file)
                for file in os.listdir(self.template_path)
            }
        else:
            with open(self.template_path) as f:
                return {
                    os.path.basename(self.template_path): Template(f.read())
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
