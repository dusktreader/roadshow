import os
from importlib import import_module
from io import StringIO
from unittest.mock import Mock

import pytest
import roadshow.app as app_module
import typer
from rich.console import Console
from roadshow import DemoResult, Roadshow, get_standalone_module
from roadshow.core import capture_demo
from roadshow_demo.capture import show_input_capture
from roadshow_demo.lifecycle import show_cleanup_after_exception, show_xdg_isolation

from tests.unit import test_core


def test_roadshow_discovers_package_demos_and_groups_them_by_feature():
    groups = Roadshow("roadshow_demo").discover()

    assert [function.__name__ for function in groups["basic"]] == ["show_output"]
    assert [function.__name__ for function in groups["capture"]] == [
        "show_exception_capture",
        "show_exit_capture",
        "show_input_capture",
        "show_stream_capture",
    ]
    assert [function.__name__ for function in groups["lifecycle"]] == [
        "show_cleanup_after_exception",
        "show_lifecycle_hooks",
        "show_xdg_isolation",
    ]


def test_input_capture_demo_uses_per_demo_fixtures():
    result = capture_demo(show_input_capture)
    assert result.stdout == "Hello, Ada.\nArguments: ['--example']\n"

    overridden = capture_demo(show_input_capture, input_text="Grace\n", argv=("--override",))
    assert overridden.stdout == "Hello, Grace.\nArguments: ['--override']\n"


def test_xdg_demo_shows_isolated_and_restored_environment(monkeypatch: pytest.MonkeyPatch):
    variables = ("HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME")
    for variable in variables:
        monkeypatch.setenv(variable, f"/original/{variable}")
    originals = {variable: os.environ[variable] for variable in variables}

    result = capture_demo(show_xdg_isolation)

    assert result.succeeded
    assert result.stdout is not None
    lines = result.stdout.splitlines()
    before_index = lines.index("Environment before demo:")
    during_index = lines.index("Environment during demo:")
    after_index = lines.index("Environment after demo:")
    before_values = dict(
        line.split(": ", maxsplit=1) for line in lines[before_index + 1 : during_index] if ": " in line
    )
    during_values = dict(line.split(": ", maxsplit=1) for line in lines[during_index + 1 : after_index] if ": " in line)
    after_values = dict(line.split(": ", maxsplit=1) for line in lines[after_index + 1 :] if ": " in line)

    assert before_values == originals
    assert set(during_values) == set(variables)
    assert all(during_values[variable] != originals[variable] for variable in variables)
    assert after_values == originals
    assert {variable: os.environ[variable] for variable in variables} == originals


def test_after_hook_output_is_captured_when_demo_raises():
    result = capture_demo(show_cleanup_after_exception)

    assert result.stdout == "Cleanup hook ran.\n"
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "example failure after setup"


def test_roadshow_groups_module_demos_by_feature():
    groups = Roadshow(test_core).discover()

    assert [function.__name__ for function in groups["errors"]] == ["sample_error", "sample_exit"]
    assert [function.__name__ for function in groups["input"]] == ["sample_read_input"]
    assert [function.__name__ for function in groups["source"]] == ["sample_source"]


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


def test_example_main_package_is_used_by_the_entrypoint():
    main_module = import_module("roadshow_demo.main")

    assert main_module.__package__ == "roadshow_demo"
