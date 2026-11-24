from importlib import import_module
from io import StringIO
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
import roadshow.app as app_module
import typer
from rich.console import Console
from roadshow import DemoResult, Roadshow, demo, get_standalone_module

from tests.unit import test_core


def test_roadshow_groups_module_demos_by_feature_in_configured_order():
    groups = Roadshow(test_core, feature_order=("features", "errors")).discover()

    assert list(groups)[:2] == ["features", "errors"]
    assert [function.__name__ for function in groups["errors"]] == ["ordered_errors", "sample_exit", "sample_error"]
    assert [function.__name__ for function in groups["input"]] == ["sample_read_input"]
    assert [function.__name__ for function in groups["source"]] == ["sample_source"]

    default_groups = Roadshow(test_core).discover()
    assert list(default_groups) == ["errors", "features", "input", "output", "source"]


def test_roadshow_orders_demos_after_combining_modules(monkeypatch: pytest.MonkeyPatch):
    root_module = ModuleType("demo_package")
    root_module.__path__ = []
    first_module = ModuleType("demo_package.first")
    second_module = ModuleType("demo_package.second")

    def later_ordered_demo():
        pass

    def earlier_ordered_demo():
        pass

    later_ordered_demo.__module__ = first_module.__name__
    earlier_ordered_demo.__module__ = second_module.__name__
    demo("shared", order=10)(later_ordered_demo)
    demo("shared", order=1)(earlier_ordered_demo)
    first_module.__dict__["later_ordered_demo"] = later_ordered_demo
    second_module.__dict__["earlier_ordered_demo"] = earlier_ordered_demo
    modules = {
        root_module.__name__: root_module,
        first_module.__name__: first_module,
        second_module.__name__: second_module,
    }

    monkeypatch.setattr(
        app_module.pkgutil,
        "walk_packages",
        lambda package_path, prefix: [
            SimpleNamespace(name=first_module.__name__),
            SimpleNamespace(name=second_module.__name__),
        ],
    )
    monkeypatch.setattr(app_module, "import_module", lambda name: modules[name])

    groups = Roadshow(root_module).discover()

    assert [function.__name__ for function in groups["shared"]] == [
        "earlier_ordered_demo",
        "later_ordered_demo",
    ]


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
