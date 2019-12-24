from ..artifact import DockerArtifact
from ..config import Config


def write(config: str):
    """ Generate all files """
    config = Config.load(config)
    artifacts = DockerArtifact.load(config)

    for artifact in artifacts:
        artifact.write()

