"""Chad Argparse module."""

import argparse

from modules.ui.prompt.prompt import ChadPrompt


class ChadArgumentParser:
    """Custom argparse.ArgumentParser class."""

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            usage="%(prog)s [options] <command> [<args>]...",
        )
        self.parser.add_argument(
            "-i", "--interactive", action="store_true", help="Run in interactive mode."
        )
        self.run()

    def run(self):
        args = self.parser.parse_args()
        if args.interactive:
            prompt = ChadPrompt()
            prompt.start_prompt()
        else:
            self.parser.print_help()
