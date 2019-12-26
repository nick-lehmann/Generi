from pathlib import Path

from ..artifact import DockerArtifact
from ..config import Config


def write(config: str):
    """ Generate all files """
    config = Path(config)
    config = Config.load(config)
    artifacts = DockerArtifact.load(config)

    for artifact in artifacts:
        artifact.write()

    print(f'Successfully wrote {len(artifacts)} artifacts')

