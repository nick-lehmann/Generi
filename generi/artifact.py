import os
from typing import Dict, Optional
from collections import OrderedDict

from docker import DockerClient
from docker.errors import BuildError
from docker.models.images import Image
from jinja2 import Template, Environment, FileSystemLoader


class DockerArtifact:
    parameters: dict

    template_path: str
    output_dir: str
    tag: str

    image: Image

    ordered_parameters: Optional[list]

    def __init__(self, parameters: OrderedDict, template_path: str,
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

    def build(self, client: DockerClient):
        dockerfile = os.path.join(self.output_dir, 'Dockerfile')

        print(f'Start building image')
        print(f'- Tag:        {self.tag}')
        print(f'- Context:    {self.output_dir}')
        print(f'- Dockerfile: {dockerfile}')

        try:
            self.image, logs = client.images.build(
                path=self.output_dir,
                dockerfile=dockerfile,
                tag=self.tag
            )
        except BuildError as e:
            print(f'Building image {self.tag} failed')
            for log in e.build_log:
                if 'errorDetail' not in log:
                    print(log['stream'].rstrip('\n'))
                else:
                    print(log['errorDetail']['message'].rstrip('\n'))

    def push(self, client: DockerClient):
        repository, tag = self.tag.split(':', 1)
        client.images.push(repository=repository, tag=tag)

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
