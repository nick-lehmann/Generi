import signal
import sys
import fire

from .commands import (
    build,
    push,
    write
)
from .console import Cursor


def exit(sig, frame):
    print()
    print('Aborted by user')
    Cursor().show()
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, exit)
    fire.Fire({
        'build': build,
        'push': push,
        'write': write
    })


if __name__ == '__main__':
    main()
