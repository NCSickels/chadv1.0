"""Prompt module for the interactive UI."""

import sys

from prompt_toolkit import HTML, PromptSession, print_formatted_text
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.styles import Style

from log.clogger import Logger

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
        print_formatted_text(HTML("<b>Starting prompt...</b>"))

    # --------------------------------------------------------------- #

    def exit_message(self):
        print_formatted_text(HTML("<b>Exiting prompt...</b>"))

    # --------------------------------------------------------------- #

    def handle_exit(self, tokens: list) -> None:
        if len(tokens) > 0:
            if tokens[0] in ("exit", "quit", "q"):
                # TODO: exit gracefully
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
        self.logger.info("Starting interactive prompt...")
        # self.intro_message()
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
