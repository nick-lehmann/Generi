import os
from typing import Dict, Optional

import aiodocker
from jinja2 import Template, Environment, FileSystemLoader

import tempfile
import tarfile


class DockerArtifact:
    parameters: dict

    template_path: str
    output_dir: str
    tag: str

    ordered_parameters: Optional[list]

    def __init__(self, parameters: dict, template_path: str,
                 output_dir: str, tag: str):
        self.template_path = os.path.normpath(
            Template(template_path).render(**parameters)
        )
        self.output_dir = os.path.normpath(
            Template(output_dir).render(**parameters)
        )
        self.tag = Template(tag).render(**parameters)

        self.parameters = parameters

    def write(self):
        """
        Render all templates and write them to their desired path.
        """
        for file, template in self.templates.items():
            content = template.render(**self.parameters)

            if not os.path.exists(self.output_dir):
                os.makedirs(self.output_dir)

            output_path = os.path.join(self.output_dir, file)
            with open(output_path, 'w+') as f:
                f.write(content)

    async def build(self, client: aiodocker.Docker):
        """ Build image """
        f = tempfile.NamedTemporaryFile()
        tar = tarfile.open(mode="w:gz", fileobj=f)
        context_path = self.output_dir + '/'

        print(f'Start building {self.tag}')

        for file in os.listdir(context_path):
            tar.add(os.path.join(context_path, file), arcname=file)

        tar.close()
        f.seek(0)

        await client.images.build(fileobj=f, encoding="gzip", tag=self.tag)
        print(f'Finished building {self.tag}')
        tar.close()

    async def push(self, client: aiodocker.Docker, auth: dict):
        """ Push image to registry """
        print(f'Start pushing {self.tag}')
        repository, tag = self.tag.split(':', 1)

        await client.images.push(name=repository, tag=tag, auth=auth)
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
