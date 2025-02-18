"""Command history module."""

import os

from prompt_toolkit.history import History


class ChadHistory(History):
    """
    Custom history class for the Chad prompt.

    Args:
        History (class): Base history class.
    """

    def __init__(self):
        super().__init__()
        self.last_command = None
        self.history_file_path = os.path.join(os.path.dirname(__file__), "history.txt")
        self.load_history_strings()

    def load_history_strings(self):
        """Load history strings from a persistent storage."""
        history_strings = []
        try:
            with open(self.history_file_path, "r") as file:
                for line in file:
                    history_strings.append(line.strip())
        except FileNotFoundError:
            pass
        return history_strings

    def store_string(self, string):
        """Store a string in persistent storage."""
        if string != self.last_command:
            with open(self.history_file_path, "a") as file:
                file.write(f"{string}\n")
            self.last_command = string

    def list_history(self):
        """List the history of commands."""
        for index, command in enumerate(self.load_history_strings()):
            print(f"{index + 1}: {command}")
