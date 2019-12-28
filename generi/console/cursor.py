import colorama
import sys


class Cursor:
    current_line: int

    def __init__(self):
        colorama.init()
        self.current_line = 0

    def up(self, rows: int):
        self.write("\033[{}F".format(rows))

        if self.current_line >= rows:
            self.current_line -= rows
        else:
            self.current_line = 0

    def down(self, rows: int):
        self.write("\033[{}E".format(rows))
        self.current_line += rows

    def hide(self):
        self.write("\033[?25l")

    def show(self):
        self.write("\033[?25h")

    def clear_line(self):
        self.write("\033[2K")

    def move_to_line(self, line):
        if self.current_line < line:
            self.down(line - self.current_line)

        if self.current_line > line:
            self.up(self.current_line - line)

    def write(self, message):
        sys.stdout.write(message)
        sys.stdout.flush()
