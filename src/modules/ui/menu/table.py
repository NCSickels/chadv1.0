"""
Class for creating help menu tables from JSON data through the rich library.
"""

import json
import os

from rich.console import Console
from rich.table import Table

from config import settings


class TableCreator:
    """
    A class for creating help menu tables from JSON data.

    Attributes:
        console (Console): The rich console object.
        json_file (str): The path to the JSON file containing the table data.
    """

    def __init__(self):
        self.console = Console()
        self.json_file = os.path.dirname(os.path.abspath(__file__)) + "/menu_data.json"

    @staticmethod
    def read_json(file_path: str) -> dict:
        with open(file_path) as f:
            data = json.load(f)
            return data

    def create_table(
        self, header_data: dict, column_data: list, row_data: list, column_keys: list
    ) -> None:
        table = Table(
            show_header=header_data.get("show_header", True),
            header_style=header_data.get("header_style", "bold white"),
            title=header_data.get("title", ""),
            width=int(header_data.get("width", 84)),
            show_lines=True,
        )
        for i, column in enumerate(column_data):
            table.add_column(
                column.get("title", ""),
                style=column.get("style", ""),
                justify=column.get("justify", "right"),
                width=column.get("width", 30),
            )
        column_keys += [None] * (len(column_data) - len(column_keys))
        for row in row_data:
            row_values = [
                str(row.get(column_keys[i], "")) for i in range(len(column_data))
            ]
            table.add_row(*row_values)
        return table

    def display_table(self, json_data: dict, module: str) -> None:
        column_keys_dict = {
            "Main": ["option", "modules", "description"],
            "Core": ["command", "description"],
        }
        for table in json_data[module]:
            header_data = table.get("header", [{}])[0]
            column_data = table.get("columns", [])
            row_data = table.get("rows", [])
            column_keys = column_keys_dict.get(module, [])
            table = self.create_table(header_data, column_data, row_data, column_keys)
            self.console.print(table)
            print("\n")

    def display_table_from_file(self, module: str) -> None:
        if settings.GENERAL_SETTINGS.use_rich_tables:
            json_data = self.read_json(self.json_file)
            self.display_table(json_data, module)
        else:
            pass
