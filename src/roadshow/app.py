"""Build and run tagged demo applications."""

from __future__ import annotations

import pkgutil
from collections import defaultdict
from importlib import import_module
from types import ModuleType
from typing import Annotated

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Confirm

from roadshow.core import _DEMO_FEATURE_ATTRIBUTE, DemoFunction, discover_demos
from roadshow.errors import RoadshowError
from roadshow.render import display_demo


class Roadshow:
    """Discover tagged demos in a package and expose them through a Typer CLI."""

    def __init__(self, package: str | ModuleType, *, title: str | None = None):
        """Create a Roadshow app for one package or module."""
        self.package = package
        self.package_name = package if isinstance(package, str) else package.__name__
        self.title = title or self.package_name

    def discover(self) -> dict[str, list[DemoFunction]]:
        """Import the package's modules and group their demos by feature tag."""
        if isinstance(self.package, str):
            with RoadshowError.handle_errors(f"Could not import demo package {self.package!r}"):
                root_module = import_module(self.package)
        else:
            root_module = self.package

        modules = [root_module]
        package_path = getattr(root_module, "__path__", None)
        if package_path is not None:
            with RoadshowError.handle_errors(f"Could not discover demo modules in {root_module.__name__!r}"):
                module_infos = list(pkgutil.walk_packages(package_path, f"{root_module.__name__}."))
            for module_info in module_infos:
                with RoadshowError.handle_errors(f"Could not import demo module {module_info.name!r}"):
                    modules.append(import_module(module_info.name))

        feature_map: defaultdict[str, list[DemoFunction]] = defaultdict(list)
        for module in modules:
            for function in discover_demos(module):
                feature = function.__dict__[_DEMO_FEATURE_ATTRIBUTE]
                feature_map[feature].append(function)

        return {
            feature: sorted(demos, key=lambda function: (function.__module__, function.__name__))
            for feature, demos in sorted(feature_map.items())
        }

    def run(self) -> None:
        """Start the Typer CLI for this Roadshow app."""
        typer.run(self.start)

    def start(
        self,
        feature: Annotated[
            list[str] | None,
            typer.Option(
                "--feature",
                "-f",
                help="Features to run. Repeat this option to select multiple features; omit it to run all features.",
            ),
        ] = None,
        non_interactive: Annotated[
            bool,
            typer.Option("--non-interactive", help="Run all selected demos without prompts."),
        ] = False,
    ) -> None:
        """Run the selected demo features and report captured failures."""
        all_features = self.discover()
        selected_features = list(dict.fromkeys(feature or all_features))
        unknown_features = sorted(set(selected_features) - all_features.keys())
        if unknown_features:
            available = ", ".join(all_features) or "none"
            raise typer.BadParameter(f"Unknown feature tag(s): {', '.join(unknown_features)}. Available: {available}")

        greeting_lines = [
            f"This program shows the demos available in `{self.title}`.",
            "",
            "Selected features:",
        ]
        for selected_feature in selected_features:
            greeting_lines.append(f"- `{selected_feature}`")
            greeting_lines.extend(f"  - `{function.__name__}()`" for function in all_features[selected_feature])
        if not selected_features:
            greeting_lines.append("- No tagged demos found.")

        console = Console()
        console.print(
            Panel(
                Markdown("\n".join(greeting_lines)),
                title=f"[green]Welcome to {self.title}[/green]",
                title_align="left",
                padding=1,
                border_style="green",
            )
        )
        console.print()
        console.print()
        if not non_interactive and not Confirm.ask("Would you like to continue?", default=True):
            return

        demos_to_run = [
            (selected_feature, function)
            for selected_feature in selected_features
            for function in all_features[selected_feature]
        ]
        total_demos = len(demos_to_run)
        failed = False
        for demo_number, (selected_feature, function) in enumerate(demos_to_run, start=1):
            console.clear()
            result = display_demo(
                function,
                console,
                label=selected_feature,
                progress=(demo_number, total_demos),
            )
            failed |= not result.succeeded
            if not non_interactive and not Confirm.ask("Would you like to continue?", default=True):
                break

        console.clear()
        console.print(
            Panel(
                f"Thanks for checking out {self.title}.",
                title="[green]Done[/green]",
                title_align="left",
                padding=1,
                border_style="green",
            )
        )
        console.print()
        console.print()
        if failed and non_interactive:
            raise typer.Exit(1)
