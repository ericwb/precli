# Copyright 2023 Secure Saurce LLC
import linecache

from rich import console
from rich.padding import Padding

from precli.core.level import Level
from precli.core.result import Rule
from precli.renderers.renderer import Renderer


class Plain(Renderer):
    def __init__(self, no_color: bool = False):
        super().__init__(no_color=no_color)
        self.console = console.Console(highlight=False)

    def render(self, results: list):
        for result in results:
            rule = Rule.get_by_id(result.rule_id)

            if self._no_color is True:
                style = ""
            else:
                match result.level:
                    case Level.ERROR:
                        style = "red"

                    case Level.WARNING:
                        style = "yellow"

                    case Level.NOTE:
                        style = "blue"

            self.console.print(
                f"{rule.id}: {rule.cwe.name}",
            )
            self.console.print(
                f'  File "{result.location.file_name}", line '
                f"{result.location.start_line}, in <module>",
            )
            code_line = linecache.getline(
                filename=result.location.file_name,
                lineno=result.location.start_line,
            )
            underline_width = (
                result.location.end_column - result.location.start_column
            )
            underline = (
                " " * result.location.start_column + "^" * underline_width
            )
            self.console.print(
                Padding(code_line + underline, (0, 4)),
            )
            self.console.print(
                f"{result.level.name.title()}: ",
                style=style,
                end="",
            )
            self.console.print(
                f"{result.message}",
            )
            self.console.print()