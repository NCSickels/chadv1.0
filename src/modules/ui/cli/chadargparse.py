"""Chad Argparse module."""

import argparse
import asyncio
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

    def run(self) -> None:
        args = self.parser.parse_args()
        if args.interactive:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            prompt = ChadPrompt(loop=loop)
            prompt.start_prompt()
        else:
            self.parser.print_help()
