import sys
from .config import Config


def main():
    config = Config.load(sys.argv[1])
    print(config)
