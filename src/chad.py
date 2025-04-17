#!/usr/bin/python3
import argparse
import asyncio

import nest_asyncio

from log.clogger import Logger
from modules.ui.banner import print_banner
from modules.ui.prompt.prompt import ChadPrompt
from modules.utils.exception import ChadProgramExit
from modules.ui.cli.chadcli import ChadCLI


class ChadArgumentParser:
    """
    Custom argparse.ArgumentParser class.

    Attributes:
        loop (asyncio.AbstractEventLoop): The asyncio event loop.
        parser (argparse.ArgumentParser): The argparse parser.
    """

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.parser = argparse.ArgumentParser(
            usage="%(prog)s [options] <command> [<args>]...",
        )
        # Interactive mode
        self.parser.add_argument(
            "-i", "--interactive", action="store_true", help="Run in interactive mode."
        )
        # Command line argument mode, not applicable for interactive mode
        # interactive mode pulls from the default config file
        self.parser.add_argument(
            "-s", "--start", action="store_true", help="Start the application."
        )
        self.parser.add_argument(
            "--interface",
            nargs="?",
            default="enp0s8",
            type=str,
            help="The network interface to use.",
            metavar="INTERFACE",
            dest="interface",
        )
        self.parser.add_argument(
            "-t",
            "--ip",
            nargs="?",
            default="127.0.0.1",
            help="The IP address to use.",
            metavar="IP_ADDRESS",
            dest="ip_address",
        )
        self.parser.add_argument(
            "-p",
            "--port",
            nargs="?",
            default=22,
            type=int,
            help="The port on the target to use.",
            metavar="PORT",
            dest="port",
        )
        self.run()

    def run(self) -> None:
        args = self.parser.parse_args()
        if args.start:
            chadcli = ChadCLI(args.interface, args.ip_address, args.port, server=True)
            chadcli.run()
        elif args.interactive:
            prompt = ChadPrompt(self.loop)
            prompt.start_prompt()
        else:
            self.parser.print_help()


def main() -> None:
    print_banner()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    nest_asyncio.apply()
    Logger()

    try:
        ChadArgumentParser()
    except ChadProgramExit:
        pass
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pending = asyncio.all_tasks(loop)
        for task in pending:
            task.cancel()
        try:
            loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
        except asyncio.CancelledError:
            pass
        finally:
            loop.run_until_complete(loop.shutdown_asyncgens())
            loop.close()


if __name__ == "__main__":
    main()
