#!/usr/bin/python3
# import argparse
from modules.ui.banner import print_banner
from log.clogger import Logger
from modules.ui.prompt.prompt import ChadPrompt


def main():
    print_banner()
    logger = Logger()
    prompt = ChadPrompt()
    prompt.start_prompt()


if __name__ == "__main__":
    main()
