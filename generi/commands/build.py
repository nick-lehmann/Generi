import asyncio
import aiodocker
import time
from pathlib import Path

from ..artifact import DockerArtifact
from ..config import Config
from ..console import Status
from ..optim import create_build_queue, parameter_order


job_pending = '⏳ Pending: {}'
job_running = '🔨 Building: {}'
job_finished = '✅ Finished: {}'


async def _build_parallel(config: Config, loop: asyncio.events.AbstractEventLoop):
    client = aiodocker.Docker()
    queue = create_build_queue(
        jobs=DockerArtifact.load(config),
        order=parameter_order(config)
    )
    build_tasks = set()

    lines = [
        f'{len(queue)} images will be built'
    ] + [job_pending.format(job) for job in queue]

    with Status(lines) as status:
        for index, job in enumerate(queue, 1):
            if len(build_tasks) >= config.parallel:
                done, build_tasks = await asyncio.wait(
                    build_tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                for task in list(done):
                    finished_artifact = task.result()
                    status[queue.index(finished_artifact) + 1] = job_finished.format(finished_artifact)

            build_tasks.add(loop.create_task(job.build(client)))
            status[index] = job_running.format(job)

        done, _ = await asyncio.wait(build_tasks)
        for task in list(done):
            finished_artifact = task.result()
            status[queue.index(finished_artifact) + 1] = job_finished.format(finished_artifact)
            time.sleep(0.1)
        await client.close()


def build(config: str):
    """ Build all artifacts in parallel """
    config = Path(config)
    config = Config.load(config)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_build_parallel(config, loop))
    loop.close()
