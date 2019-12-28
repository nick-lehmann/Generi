from typing import List
from .cursor import Cursor


class Status:
    """
    Shows the status of multiple jobs and updates their individual status.
    """
    cursor: Cursor
    lines: List[str]

    def __init__(self, lines: List[str]):
        self.cursor = Cursor()
        self.lines = lines

        for line in lines:
            self.cursor.write(line)
            self.cursor.down(1)

        self.cursor.hide()

    def __getitem__(self, key: str):
        return self.lines[key]

    def __setitem__(self, key: int, value: str):
        self.lines[key] = value
        self.cursor.move_to_line(key)
        self.cursor.clear_line()
        self.cursor.write(value)

    def __del__(self):
        self.cursor.move_to_line(len(self.lines))
        self.cursor.show()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        del self
