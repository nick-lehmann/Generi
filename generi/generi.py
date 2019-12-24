import asyncio
from typing import List

import aiodocker

from .artifact import DockerArtifact
from .config import Config
from .optim import create_build_queue

parallel = 4


def build_artifacts(config) -> List[DockerArtifact]:
    """
    Return the list of artifacts.
    """
    return [DockerArtifact(
        parameters=mix,
        template_path=config.template_path,
        output_dir=config.output_path,
        tag=config.tag
    ) for mix in config.parameter_matrix]


class Generi:
    config: Config

    def __init__(self, schema_path):
        self.config = Config.load(schema_path)

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
