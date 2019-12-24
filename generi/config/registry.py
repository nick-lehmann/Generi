from dataclasses import dataclass
from typing import Optional


@dataclass
class Registry:
    username: str
    host: str = None
    password: str = None

    @staticmethod
    def load(raw: dict) -> Optional['Registry']:
        try:
            registry = raw['registry']
            return Registry(
                host=registry.get('host'),
                username=registry['username'],
                password=registry.get('password')
            )
        except IndexError:
            return None

    def get_password(self) -> str:
        if not self.password:
            return input('Please enter the password for this registry: ')

        return self.password
