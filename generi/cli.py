import fire
from .commands import (
    build,
    push,
    write
)


def main():
    fire.Fire({
        'build': build,
        'push': push,
        'write': write
    })
