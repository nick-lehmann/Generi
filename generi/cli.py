import asyncio
import sys
from .generi import Generi


def main():
    generator = Generi(sys.argv[1])
    generator.write()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(generator.build())
    loop.close()

