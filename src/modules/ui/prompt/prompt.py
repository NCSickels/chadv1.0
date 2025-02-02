"""Prompt module for the interactive UI."""

import sys

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style, merge_styles
from log.clogger import Logger
from modules.connections.interface import NetworkInterface

# from modules.connections.socket_connection import SocketConnection
from modules.ui.menu.table import TableCreator
from modules.utils import constants

from .commands import COMMANDS, CommandCompleter, CommandHandler
from .helpers import get_tokens


class CommandPrompt(object):
    """
    Command prompt for the interactive UI.

    Attributes:
        commands (dict): Dictionary of commands.
        cmd_handler (CommandHandler): Command handler.
        completer (CommandCompleter): Command completer.
        style (Style): Prompt style.
        _break (bool): Break flag.
        prompt_session (PromptSession): Prompt session.
        logger (Logger): Logger instance.

    Methods:
        get_commands() -> dict: Returns the commands dictionary.
        get_prompt() -> HTML: Returns the prompt.
        get_style() -> Style: Returns the prompt style.
        intro_message(): Prints the intro message.
        exit_message(): Prints the exit message.
        handle_exit(tokens: list) -> None: Handles the exit command.
        handle_break(tokens: list) -> bool: Handles the break command.
        handle_command(tokens: list) -> None: Handles a command.
        bottom_toolbar(): Returns the bottom toolbar.
        start_prompt() -> None: Starts the prompt session.
    """

    def __init__(self) -> None:
        self.commands = self.get_commands()
        self.cmd_handler = CommandHandler(self.commands)
        self.completer = CommandCompleter(self.commands)
        self.style = self.get_style()
        self._break = False
        self.prompt_session = PromptSession(
            completer=self.completer,
            style=self.style,
            bottom_toolbar=self.bottom_toolbar,
            auto_suggest=AutoSuggestFromHistory(),
        )
        self.network_interface = NetworkInterface(interface="eth0")
        self.status_info = self.network_interface.get_status_info()
        self.status = self.status_info["status"]
        self.network_interface = self.status_info["interface"]
        self.connected_ip = self.status_info["connected_ip"]
        self.connected_port = self.status_info["connected_port"]
        self.logger = Logger()
        super(CommandPrompt, self).__init__()

    # --------------------------------------------------------------- #

    def get_commands(self) -> dict:
        return COMMANDS

    # --------------------------------------------------------------- #

    def get_prompt(self) -> HTML:
        return HTML("<b>> </b>")

    # --------------------------------------------------------------- #

    def get_style(self):
        Style.from_dict(
            {
                "completion-menu.completion": "bg:#008888 #ffffff",
                "completion-menu.completion.current": "bg:#00aaaa #000000",
                "scrollbar.background": "bg:#88aaaa",
                "scrollbar.button": "bg:#222222",
                "token.literal.string.single": "#98ff75",
            }
        )

    # --------------------------------------------------------------- #

    def intro_message(self):
        self.logger.info("Starting prompt...")
        self.logger.info("Welcome to the Chad interactive prompt!")
        # print_formatted_text(HTML("<b>Starting prompt...</b>"))

    # --------------------------------------------------------------- #

    def exit_message(self):
        self.logger.info("Exiting prompt...")
        # print_formatted_text(HTML("<b>Exiting prompt...</b>"))

    # --------------------------------------------------------------- #

    def handle_exit(self, tokens: list) -> None:
        if len(tokens) > 0:
            if tokens[0] in ("exit", "quit", "q"):
                sys.exit(0)

    # --------------------------------------------------------------- #

    def handle_break(self, tokens: list) -> bool:
        if tokens[0] in ("c", "continue"):
            return True
        else:
            return False

    # --------------------------------------------------------------- #

    def handle_command(self, tokens: list) -> None:
        if len(tokens) > 0:
            self.cmd_handler.handle_command(tokens)

    # --------------------------------------------------------------- #

    def bottom_toolbar(self):
        return None

    # --------------------------------------------------------------- #

    def start_prompt(self) -> None:
        # self.logger.info("Starting interactive prompt...")
        self.intro_message()
        while True:
            try:
                cmd = self.prompt_session.prompt(
                    self.get_prompt,
                )

                tokens = get_tokens(cmd)

                if not self.handle_break(tokens):
                    self.handle_exit(tokens)
                    self.handle_command(tokens)

            except KeyboardInterrupt:
                continue
            except EOFError:
                # self.handle_exit(['exit'])
                break
        self.exit_message()


class ChadPrompt(CommandPrompt):
    def __init__(self) -> None:
        super().__init__()
        # self.interface = NetworkInterface(interface="eth0")

    # ================================================================#
    # CommandPrompt Overridden Functions                              #
    # ================================================================#

    def get_commands(self):
        """Contains the full list of commands."""
        commands = super().get_commands()
        commands.update(
            {
                "help": {
                    "desc": "Displays the help menu.",
                    "exec": self._cmd_help,
                },
                "set_interface": {
                    "desc": "Set network interface.",
                    "exec": self._cmd_set_interface,
                },
                "set_ip": {
                    "desc": "Set IP address.",
                    "exec": self._cmd_set_ip,
                },
                "set_port": {
                    "desc": "Set port number.",
                    "exec": self._cmd_set_port,
                },
                "start": {
                    "desc": "Starts an active connection with the network interface.",
                    "exec": self._cmd_start,
                },
                "stop": {
                    "desc": "Stops the active connection with the network interface.",
                    "exec": self._cmd_stop,
                },
            }
        )
        return commands

    # --------------------------------------------------------------- #

    def get_prompt(self):
        return HTML("<b>> </b>")

    # --------------------------------------------------------------- #

    def bottom_toolbar(self):
        if self.status == "Connected":
            status_tag = "active"
        else:
            status_tag = "inactive"

        toolbar_message = HTML(
            f" <b>Status: </b><{status_tag}>{self.status}</{status_tag}> | "
            f"<b>IP: </b><host>{self.status_info['connected_ip']}</host> | "
            f"<b>Port: </b><port>{self.status_info['connected_port']}</port> | "
            f"<b>Interface: </b><iface>{self.network_interface}</iface>"
        )
        self.refresh_prompt()
        return toolbar_message

    # ================================================================#
    # Command handlers                                                #
    # ================================================================#

    def _cmd_help(self) -> None:
        """Displays the help menu."""
        table = TableCreator()
        [table.display_table_from_file(section) for section in ["Main", "Core"]]
        return None

    # --------------------------------------------------------------- #
    def _cmd_set_(self, tokens: list) -> None:
        """Sets various parameters."""
        if len(tokens) > 0:
            if tokens[0] == "interface":
                self._cmd_set_interface(tokens[1:])
            elif tokens[0] == "ip":
                self._cmd_set_ip(tokens[1:])
            elif tokens[0] == "port":
                self._cmd_set_port(tokens[1:])
        else:
            print_formatted_text(
                HTML("<b>Usage: set [interface, port, ip] <value></b>")
            )

        return None

    def _cmd_set_interface(self, tokens: list) -> None:
        """Sets the network interface."""
        if len(tokens) > 0:
            # self.interface = NetworkInterface(interface=tokens[0])
            self.logger.info(f"Setting interface to {tokens[0]}")
            self.network_interface = tokens[0]
        else:
            print_formatted_text(HTML("<b>Usage: set interface [interface]</b>"))
        return None

    def _cmd_set_ip(self, tokens: list) -> None:
        """Sets the IP address."""
        if len(tokens) > 0:
            # self.interface.ip = tokens[0]
            self.logger.info(f"Setting IP to {tokens[0]}")
            self.connected_ip = tokens[0]
        else:
            print_formatted_text(HTML("<b>Usage: set ip [ip]</b>"))
        return None

    def _cmd_set_port(self, tokens: list) -> None:
        """Sets the port number."""
        if len(tokens) > 0:
            # self.interface.port = int(tokens[0])
            self.logger.info(f"Setting port to {tokens[0]}")
            self.connected_port = tokens[0]
        else:
            print_formatted_text(HTML("<b>Usage: set port [port]</b>"))
        return None

    # --------------------------------------------------------------- #

    def _cmd_start(self, tokens: list) -> None:
        """Starts the network interface."""
        # self.logger.info("Starting interface...")
        self.status = "Connected"
        # self.interface.start_capture(self.interface.ip, self.interface.port)
        self.refresh_prompt()

    def _cmd_stop(self, tokens: list) -> None:
        """Stops the network interface."""
        # self.logger.info("Stopping interface...")
        self.status = "Disconnected"
        # self.interface.stop_capture()
        self.refresh_prompt()

    # --------------------------------------------------------------- #

    def refresh_prompt(self) -> None:
        """Refresh the prompt session to update the toolbar."""
        self.prompt_session.app.invalidate()
        self.prompt_session = PromptSession(
            completer=self.completer,
            style=self.style,
            bottom_toolbar=self.bottom_toolbar,
            auto_suggest=AutoSuggestFromHistory(),
        )

    # --------------------------------------------------------------- #

    def get_style(self):
        return merge_styles([super().get_style(), Style.from_dict(constants.STYLE)])
