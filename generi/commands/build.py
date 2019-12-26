import asyncio
import aiodocker
from pathlib import Path

from ..artifact import DockerArtifact
from ..config import Config
from ..optim import create_build_queue, parameter_order


async def _build_parallel(config: Config, loop: asyncio.events.AbstractEventLoop):
    client = aiodocker.Docker()
    queue = create_build_queue(
        jobs=DockerArtifact.load(config),
        order=parameter_order(config)
    )
    build_tasks = set()

    for job in queue:
        if len(build_tasks) >= config.parallel:
            _done, build_tasks = await asyncio.wait(
                build_tasks,
                return_when=asyncio.FIRST_COMPLETED
            )
        build_tasks.add(loop.create_task(job.build(client)))

    await asyncio.wait(build_tasks)
    await client.close()


def build(config: str):
    """ Build all artifacts in parallel """
    config = Path(config)
    config = Config.load(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_build_parallel(config, loop))
    loop.close()
