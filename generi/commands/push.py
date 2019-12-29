import asyncio
import aiodocker
from pathlib import Path

from ..artifact import DockerArtifact
from ..config import Config
from ..console import Status


PENDING = '⏳ Pending: {}'
RUNNING = '⏫ Pushing: {}'
FINISHED = '✅ Finished: {}'


async def _push_parallel(config: Config):
    client = aiodocker.Docker()
    artifacts = DockerArtifact.load(config)

    authentication = {
        'username': config.registry.username,
        'password': config.registry.get_password()
    }

    lines = [
        f'{len(artifacts)} image will be pushed'
    ] + [PENDING.format(artifact) for artifact in artifacts]

    with Status(lines) as status:
        for index, artifact in enumerate(artifacts, 1):
            status[index] = RUNNING.format(artifact)
            await artifact.push(client, authentication)
            status.cursor.down(1)
            status.cursor.up(1)
            status[index] = FINISHED.format(artifact)

    await client.close()


def push(config: str):
    """ Push all images to your registry """
    config = Path(config)
    config = Config.load(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_push_parallel(config))
    loop.close()
