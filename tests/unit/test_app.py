from importlib import import_module
from io import StringIO
from unittest.mock import Mock

import pytest
import roadshow.app as app_module
import typer
from rich.console import Console
from roadshow import DemoResult, Roadshow, get_standalone_module

from tests.unit import test_core


def test_roadshow_groups_module_demos_by_feature_in_configured_order():
    groups = Roadshow(test_core, feature_order=("features", "errors")).discover()

    assert list(groups)[:2] == ["features", "errors"]
    assert [function.__name__ for function in groups["errors"]] == ["ordered_errors", "sample_exit", "sample_error"]
    assert [function.__name__ for function in groups["input"]] == ["sample_read_input"]
    assert [function.__name__ for function in groups["source"]] == ["sample_source"]

    default_groups = Roadshow(test_core).discover()
    assert list(default_groups) == ["errors", "features", "input", "output", "source"]


def test_start_filters_selected_features(monkeypatch: pytest.MonkeyPatch):
    output = StringIO()
    monkeypatch.setattr(app_module, "Console", lambda: Console(file=output, width=100))
    displayed: list[str] = []
    progress_values: list[tuple[int, int] | None] = []

    def display(function, console, *, label=None, progress: tuple[int, int] | None = None):
        displayed.append(function.__name__)
        progress_values.append(progress)
        return DemoResult()

    monkeypatch.setattr(app_module, "display_demo", display)
    Roadshow(test_core, title="test app").start(feature=["source", "input"], non_interactive=True)

    assert displayed == ["sample_source", "sample_read_input"]
    assert progress_values == [(1, 2), (2, 2)]
    assert "test app" in output.getvalue()


def test_start_clears_screen_before_each_demo_and_after_last_demo(monkeypatch: pytest.MonkeyPatch):
    events: list[str] = []
    console = Mock()
    console.clear.side_effect = lambda: events.append("clear")
    console.print.side_effect = lambda *args: events.append("print")
    monkeypatch.setattr(app_module, "Console", lambda: console)

    def display(function, console, *, label=None, progress=None):
        events.append("display")
        return DemoResult()

    monkeypatch.setattr(app_module, "display_demo", display)
    Roadshow(test_core).start(feature=["source", "input"], non_interactive=True)

    assert events == [
        "print",
        "print",
        "print",
        "clear",
        "display",
        "clear",
        "display",
        "clear",
        "print",
        "print",
        "print",
    ]


def test_start_rejects_unknown_feature_tags():
    with pytest.raises(typer.BadParameter, match="Unknown feature tag"):
        Roadshow(test_core).start(feature=["missing"], non_interactive=True)


def test_run_invokes_typer_with_the_bound_entrypoint(monkeypatch: pytest.MonkeyPatch):
    typer_run = Mock()
    monkeypatch.setattr(app_module.typer, "run", typer_run)
    app = Roadshow(test_core)

    app.run()

    typer_run.assert_called_once_with(app.start)


def test_get_standalone_module_returns_the_main_module():
    assert get_standalone_module() is import_module("__main__")
