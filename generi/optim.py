from collections import defaultdict
from typing import List

from .artifact import DockerArtifact


DockerArtifacts = List[DockerArtifact]


def count_equal_from_left(original: list, new: list) -> int:
    """
    Count the number of equal elements starting from the element
    with index 0.
    """
    for index, (e1, e2) in enumerate(zip(original, new)):
        if e1 != e2:
            return index
    return min(len(original), len(new))


def calculate_similarities(queue: DockerArtifacts, jobs: DockerArtifacts):
    """
    Calculate the similarity of each job compared to all items
    already in the queue.
    """
    similarities = defaultdict(list)
    for job in jobs:
        similarity = max(
            count_equal_from_left(existing.ordered_parameters, job.ordered_parameters)
            for existing in queue
        )
        similarities[similarity] += [job]

    return similarities


def get_next_build_candidate(queue: DockerArtifacts, jobs: DockerArtifacts) -> DockerArtifact:
    """
    The next build candidate should add as much layers to the cache as possible.
    Thereby, the similarity of the next build candidate should be a minimum to all
    who are already built.
    """
    similarities = calculate_similarities(queue, jobs)
    least_similarity = min(similarities.keys())
    return similarities[least_similarity][0]


def order_parameters_of_jobs(jobs: DockerArtifacts, ordering: List[str]) -> DockerArtifacts:
    for job in jobs:
        job.ordered_parameters = [
            job.parameters[parameter]
            for parameter in ordering
        ]


def parameter_order(config) -> List[str]:
    """
    Return the order in which the parameters occur in the given dockerfile.

    This is needed for optimising the order in which the images are built.
    """
    order = list()
    for line in config.dockerfile:
        order += [
            parameter for parameter in config.parameters
            if parameter in line and '{{' in line and parameter not in order
        ]
    return order


def create_build_queue(jobs: DockerArtifacts, order: List[str]):
    """
    Create a build queue that pumps will initially pump
    as many layers into cache as possible.
    """
    order_parameters_of_jobs(jobs, order)

    queue = [jobs.pop(0)]

    while jobs:
        next_build_candidate = get_next_build_candidate(queue, jobs)
        jobs.remove(next_build_candidate)
        queue += [next_build_candidate]

    return queue
