#!/usr/bin/python3
# import argparse
from modules.ui.banner import print_banner
from modules.ui.prompt.prompt import ChadPrompt


def main():
    print_banner()
    prompt = ChadPrompt()
    prompt.start_prompt()


if __name__ == "__main__":
    main()
