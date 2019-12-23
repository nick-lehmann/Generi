import asyncio
import itertools
import os
from typing import List, Dict

import aiodocker
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

    async def _build_parallel(self, loop: asyncio.events.AbstractEventLoop):
        client = aiodocker.Docker()
        queue = create_build_queue(self.artifacts, self.parameter_ordering)
        build_tasks = set()

        for job in queue:
            if len(build_tasks) >= parallel:
                _done, build_tasks = await asyncio.wait(
                    build_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
            build_tasks.add(loop.create_task(job.build(client)))

        await asyncio.wait(build_tasks)
        await client.close()

    def build(self):
        """ Build all artifacts in parallel """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._build_parallel(loop))
        loop.close()

    async def _push_parallel(self):
        client = aiodocker.Docker()
        try:
            password = self.registry['password']
        except IndexError:
            password = input('Please enter the password for this registry: ')

        authentication = {
            'username': self.registry['username'],
            'password': password
        }

        for artifact in self.artifacts:
            await artifact.push(client, authentication)

        await client.close()

    def push(self):
        """ Push all images to your registry """
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._push_parallel())
        loop.close()

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
            self.template_path_from_schema
        )

    @property
    def artifacts(self) -> List[DockerArtifact]:
        """
        Return the list of artifacts.
        """
        if not self._artifacts:
            self._artifacts = [DockerArtifact(
                parameters=mix,
                template_path=self.template_path,
                output_dir=self.output_path,
                tag=self.tag
            ) for mix in self.parameter_matrix]

        return self._artifacts

    @property
    def dockerfile(self) -> List[str]:
        """
        Return the used dockerfile as lines.
        """
        with open(os.path.join(self.template_path, 'Dockerfile')) as dockerfile:
            return dockerfile.readlines()

    @property
    def parameter_ordering(self) -> List[str]:
        """
        Return the order in which the parameters occur in the given dockerfile.

        This is needed for optimising the order in which the images are built.
        """
        parameter_ordering = list()
        for line in self.dockerfile:
            parameter_ordering += [
                parameter for parameter in self.parameters
                if parameter in line and '{{' in line and parameter not in parameter_ordering
            ]
        return parameter_ordering

