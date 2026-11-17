"""Render demo descriptions and captured output with Rich."""

from __future__ import annotations

from collections.abc import Sequence

from rich.console import Console, Group
from rich.markdown import Markdown
from rich.panel import Panel
from rich.rule import Rule
from rich.syntax import Syntax
from rich.text import Text

from roadshow.core import (
    DemoFunction,
    DemoResult,
    _resolve_demo_argv,
    _resolve_demo_input,
    capture_demo,
    decompose_demo,
)


def display_demo(
    function: DemoFunction,
    console: Console,
    *,
    label: str | None = None,
    input_text: str | None = None,
    input_lines: Sequence[str] | None = None,
    argv: Sequence[str] | None = None,
    isolate_home: bool = True,
    progress: tuple[int, int] | None = None,
) -> DemoResult:
    """Display a demo and its captured result, optionally showing progress in the outer panel."""
    details = decompose_demo(function)
    effective_input_text = _resolve_demo_input(function, input_text, input_lines)
    effective_argv = _resolve_demo_argv(function, argv)
    # Bind the spinner to the real output stream now, since capture_demo redirects sys.stdout while the demo runs.
    spinner_console = Console(file=console.file, force_terminal=console.is_terminal)
    if console.is_terminal:
        with spinner_console.status(f"Loading [yellow]{details.name}()[/yellow]...", spinner="dots"):
            result = capture_demo(
                function, input_text=effective_input_text, argv=effective_argv, isolate_home=isolate_home
            )
    else:
        result = capture_demo(function, input_text=effective_input_text, argv=effective_argv, isolate_home=isolate_home)
    parts = [
        Markdown(details.docstring),
        Rule(characters=" "),
        Rule(characters=" "),
        Panel(
            Syntax(details.source or "pass\n", "python", line_numbers=True),
            title=f"Source for [yellow]{details.name}()[/yellow]",
            title_align="left",
            expand=False,
            padding=1,
            border_style="yellow",
        ),
    ]

    if effective_argv:
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    Text("\n".join(repr(argument) for argument in effective_argv)),
                    title=f"Supplied args/opts to [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style="magenta",
                ),
            ]
        )

    if effective_input_text:
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    Text(effective_input_text),
                    title=f"Supplied stdin to [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style="cyan",
                ),
            ]
        )

    if result.stdout:
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    Text(result.stdout.rstrip()),
                    title=f"Captured stdout from [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style="green",
                ),
            ]
        )
    if result.stderr:
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    Text(result.stderr.rstrip()),
                    title=f"Captured stderr from [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style="yellow",
                ),
            ]
        )
    if result.error is not None:
        exception = Text()
        exception.append(result.error.__class__.__name__, style="red")
        exception.append(": ")
        exception.append(str(result.error), style="yellow")
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    exception,
                    title=f"[red]Uncaught exception[/red] from [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style="red",
                ),
            ]
        )
    if result.exit_code is not None:
        exit_style = "green" if result.exit_code in (0, "0") else "red"
        parts.extend(
            [
                Rule(characters=" "),
                Rule(characters=" "),
                Panel(
                    Text(str(result.exit_code), style=exit_style),
                    title=f"Exit code from [yellow]{details.name}()[/yellow]",
                    title_align="left",
                    expand=False,
                    padding=1,
                    border_style=exit_style,
                ),
            ]
        )

    display_title = (
        f"[green]{label}[/green]: [yellow]{details.name}()[/yellow]" if label else f"[yellow]{details.name}()[/yellow]"
    )
    console.print(
        Panel(
            Group(*parts),
            title=display_title,
            title_align="left",
            subtitle=f"Demo {progress[0]} of {progress[1]}" if progress is not None else None,
            subtitle_align="left",
            padding=1,
            border_style="blue",
        )
    )
    console.print(Rule(characters=" "))
    console.print(Rule(characters=" "))
    return result
