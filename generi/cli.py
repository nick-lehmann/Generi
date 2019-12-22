import asyncio
import sys
from .generi import Generi


def main():
    generator = Generi(sys.argv[1])
    # generator.write()
    generator.build()
