"""Prompt module for the interactive UI."""

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style, merge_styles

from log.clogger import get_central_logger
from modules.connections.interface import NetworkInterface

# from modules.connections.socket_connection import SocketConnection
from modules.ui.menu.table import TableCreator
from modules.ui.prompt.commands import COMMANDS, CommandCompleter, CommandHandler
from modules.ui.prompt.commands.history import ChadHistory
from modules.utils import constants, exception

from .helpers import get_tokens


class CommandPrompt(object):
    """
    Command prompt for the interactive UI.

    Args:
        loop (asyncio.AbstractEventLoop): Event loop.

    Attributes:
        commands (dict): Dictionary of commands.
        cmd_handler (CommandHandler): Command handler.
        completer (CommandCompleter): Command completer.
        history (ChadHistory): Command history.
        style (Style): Prompt style.
        _break (bool): Break flag.
        prompt_session (PromptSession): Prompt session.
        network_interface (NetworkInterface): Network interface class instance.
        status_info (dict): Network interface status information.
        status (str): Network interface status value.
        interface_name (str): Network interface name.
        connected_ip (str): Connected IP address.
        connected_port (str): Connected port number.
        logger (Logger): Central logger.
        loop (asyncio.AbstractEventLoop): Event loop.
    """

    def __init__(self, loop) -> None:
        self.commands = self.get_commands()
        self.cmd_handler = CommandHandler(self.commands)
        self.completer = CommandCompleter(self.commands)
        self.history = ChadHistory()
        self.style = self.get_style()
        self._break = False
        self.prompt_session = PromptSession(
            completer=self.completer,
            style=self.style,
            bottom_toolbar=self.bottom_toolbar,
            auto_suggest=AutoSuggestFromHistory(),
            history=self.history,
        )
        self.network_interface = NetworkInterface(interface="any", loop=loop)
        self.status_info = self.network_interface.get_status_info()
        self.status = self.status_info["status"]
        self.interface_name = self.status_info["interface"]
        self.connected_ip = self.status_info["connected_ip"]
        self.connected_port = self.status_info["connected_port"]
        self.logger = get_central_logger()
        self.loop = loop
        super(CommandPrompt, self).__init__()

    # --------------------------------------------------------------- #

    def get_commands(self) -> dict:
        return COMMANDS

    # --------------------------------------------------------------- #

    def get_prompt(self) -> HTML:
        return HTML("<b>> </b>")

    # --------------------------------------------------------------- #

    def get_style(self) -> Style | None:
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

    def intro_message(self) -> None:
        self.logger.info("Starting prompt...")
        self.logger.info("Welcome to the Chad interactive prompt!")

    # --------------------------------------------------------------- #

    def exit_message(self) -> None:
        self.logger.info("Exiting prompt...")

    # --------------------------------------------------------------- #

    def handle_exit(self, tokens: list) -> None:
        if len(tokens) > 0:
            if tokens[0] in ("exit", "quit", "q"):
                raise exception.ChadProgramExit

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

    def bottom_toolbar(self) -> HTML | None:
        return None

    # --------------------------------------------------------------- #

    def start_prompt(self) -> None:
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
            except exception.ChadProgramExit:
                break
            except EOFError:
                self.handle_exit(["exit"])
                break
        self.exit_message()


class ChadPrompt(CommandPrompt):
    """
    Wrapper class for the CommandPrompt.

    Args:
        loop (asyncio.AbstractEventLoop): Event loop.
    """

    def __init__(self, loop) -> None:
        super().__init__(loop)

    # ================================================================#
    # CommandPrompt Overridden Functions                              #
    # ================================================================#

    def get_commands(self) -> dict:
        """Contains the full list of commands."""
        commands = super().get_commands()
        commands.update(
            {
                "help": {
                    "desc": "Displays the help menu.",
                    "exec": self._cmd_help,
                },
                "start": {
                    "desc": "Starts the network interface.",
                    "exec": self._cmd_start,
                },
                "stop": {
                    "desc": "Stops the network interface.",
                    "exec": self._cmd_stop,
                },
                "list_interfaces": {
                    "desc": "Lists all available network interfaces.",
                    "exec": self._cmd_list_interfaces,
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
                "unit_test": {
                    "desc": "Runs unit tests for a provided module.",
                    "exec": self._cmd_unit_test,
                },
                "clear": {
                    "desc": "Clears the screen.",
                    "exec": lambda x: print("\033[H\033[J"),
                },
                "history": {
                    "desc": "Displays the command history.",
                    "exec": self._cmd_history,
                },
            }
        )
        return commands

    # --------------------------------------------------------------- #

    def get_prompt(self) -> HTML:
        return HTML("<b>> </b>")

    # --------------------------------------------------------------- #

    def bottom_toolbar(self) -> HTML:
        if self.status == "Connected":
            status_tag = "active"
        else:
            status_tag = "inactive"

        toolbar_message = HTML(
            f" <b>Status: </b><{status_tag}>{self.status}</{status_tag}> | "
            f"<b>IP: </b><host>{self.status_info['connected_ip']}</host> | "
            f"<b>Port: </b><port>{self.status_info['connected_port']}</port> | "
            f"<b>Interface: </b><iface>{self.interface_name}</iface>"
        )
        self.refresh_prompt()
        return toolbar_message

    # ================================================================#
    # Command handlers                                                #
    # ================================================================#

    def _cmd_help(self, tokens: list) -> None:
        """Displays the help menu."""
        table = TableCreator()
        [table.display_table_from_file(section) for section in ["Core", "Networking"]]
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
            available_interfaces = self.network_interface.list_interfaces()
            if tokens[0] not in available_interfaces:
                print_formatted_text(
                    HTML("<b>Invalid interface. Available interfaces: </b>")
                )
                for interface in available_interfaces:
                    print_formatted_text(HTML(f"<b>{interface}</b>"))
                return None
            self.logger.info(f"Setting interface to {tokens[0]}")
            self.interface_name = tokens[0]
            self.refresh_prompt()
        else:
            print_formatted_text(HTML("<b>Usage: set interface [interface]</b>"))
        return None

    def _cmd_set_ip(self, tokens: list) -> None:
        """Sets the IP address."""
        if len(tokens) > 0:
            self.logger.info(f"Setting IP to {tokens[0]}")
            self.connected_ip = tokens[0]
            self.refresh_prompt()
        else:
            print_formatted_text(HTML("<b>Usage: set ip [ip]</b>"))
        return None

    def _cmd_set_port(self, tokens: list) -> None:
        """Sets the port number."""
        if len(tokens) > 0:
            self.logger.info(f"Setting port to {tokens[0]}")
            self.connected_port = tokens[0]
            self.refresh_prompt()
        else:
            print_formatted_text(HTML("<b>Usage: set port [port]</b>"))
        return None

    # --------------------------------------------------------------- #

    def _cmd_list_interfaces(self, tokens: list) -> None:
        """Lists all available network interfaces."""
        interfaces = self.network_interface.list_interfaces()
        for interface in interfaces:
            print_formatted_text(HTML(f"<b>{interface}</b>"))
        return None

    def _cmd_list_config(self, tokens: list) -> None:
        """Lists the current configuration."""
        print_formatted_text(HTML(f"<b>Interface: {self.interface_name}</b>"))
        print_formatted_text(HTML(f"<b>IP: {self.connected_ip}</b>"))
        print_formatted_text(HTML(f"<b>Port: {self.connected_port}</b>"))

    # --------------------------------------------------------------- #

    def _cmd_start(self, tokens: list) -> None:
        """Starts the network interface."""
        self.status = "Connected"
        self.refresh_prompt()
        self.logger.info("Starting network interface...")
        self.network_interface.start_capture()

    def _cmd_stop(self, tokens: list) -> None:
        """Stops the network interface."""
        self.status = "Disconnected"
        self.refresh_prompt()

    # --------------------------------------------------------------- #

    def _cmd_unit_test(self, tokens: list) -> None:
        """Runs unit tests for a provided module."""
        if len(tokens) > 0:
            self.logger.info(f"Running unit tests for {tokens[0]}")
            from tests.unit_test import ChadUnitTest

            test_runner = ChadUnitTest(tokens[0])
            test_runner.run_unit_tests()
        else:
            print_formatted_text(HTML("<b>Usage: unit_test [module]</b>"))
        return None

    # --------------------------------------------------------------- #

    def _cmd_history(self, tokens: list) -> None:
        """Displays the command history."""
        self.history.list_history()
        return None

    # --------------------------------------------------------------- #

    def refresh_prompt(self) -> None:
        """Refresh the prompt session to update the toolbar."""
        self.prompt_session.app.invalidate()
        self.prompt_session = PromptSession(
            completer=self.completer,
            style=self.style,
            bottom_toolbar=self.bottom_toolbar,
            auto_suggest=AutoSuggestFromHistory(),
            history=self.history,
        )

    # --------------------------------------------------------------- #

    def get_style(self) -> Style | None:
        return merge_styles([super().get_style(), Style.from_dict(constants.STYLE)])
