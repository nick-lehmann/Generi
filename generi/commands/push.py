import asyncio
import aiodocker

from ..artifact import DockerArtifact
from ..config import Config


async def _push_parallel(config: Config):
    client = aiodocker.Docker()
    artifacts = DockerArtifact.load(config)

    authentication = {
        'username': config.registry.username,
        'password': config.registry.get_password()
    }

    for artifact in artifacts:
        await artifact.push(client, authentication)

    await client.close()


def push(config: str):
    """ Push all images to your registry """
    config = Config.load(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_push_parallel(config))
    loop.close()
