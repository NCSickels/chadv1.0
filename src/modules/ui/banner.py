"""Banner for the CLI"""

import os

BANNER_SEPARATOR = """
============================================
"""
CHAD_BANNER_SECTION1 = """\n\
     ██████╗██╗  ██╗ █████╗ ██████╗\n\
    ██╔════╝██║  ██║██╔══██╗██╔══██╗\n\
"""

CHAD_BANNER_SECTION2 = """\
    ██║     ███████║███████║██║  ██║\n\
    ██║     ██╔══██║██╔══██║██║  ██║\n\
"""

CHAD_BANNER_SECTION3 = """\
    ╚██████╗██║  ██║██║  ██║██████╔╝\n\
     ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝\n\
"""

BANNER_FOOTER = """
============================================
    Charger Active Defense v{version}
============================================
"""


def no_color() -> bool:
    return int(os.environ.get("NO_COLOR", "0")) == 1


def print_banner() -> None:
    DARK_BLUE = "\x1b[38;5;20m"
    DARK_PURPLE = "\x1b[38;5;92m"
    DARK_RED = "\x1b[38;5;1m"
    END = "\033[0m"

    VERSION_FOOTER = BANNER_FOOTER.format(version="0.5.0")
    banner_string = (
        f"{BANNER_SEPARATOR}{DARK_BLUE}{CHAD_BANNER_SECTION1}"
        + f"{DARK_PURPLE}{CHAD_BANNER_SECTION2}{DARK_RED}{CHAD_BANNER_SECTION3}{END}"
        + f"{VERSION_FOOTER}\n"
    )
    print(banner_string)
