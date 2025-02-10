#!/usr/bin/python3
import argparse
import asyncio

from log.clogger import Logger
from modules.ui.banner import print_banner
from modules.ui.prompt.prompt import ChadPrompt


class ChadArgumentParser:
    """Custom argparse.ArgumentParser class."""

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.parser = argparse.ArgumentParser(
            usage="%(prog)s [options] <command> [<args>]...",
        )
        self.parser.add_argument(
            "-s", "--start", action="store_true", help="Start the application."
        )
        self.parser.add_argument(
            "-i", "--interactive", action="store_true", help="Run in interactive mode."
        )
        self.run()

    def run(self):
        args = self.parser.parse_args()
        if args.start:
            pass
        elif args.interactive:
            prompt = ChadPrompt(self.loop)
            prompt.start_prompt()
        else:
            self.parser.print_help()


def main():
    print_banner()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        Logger()
        ChadArgumentParser()
    except KeyboardInterrupt:
        print("Exiting...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
