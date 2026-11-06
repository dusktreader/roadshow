import os
import sys
from collections.abc import Callable
from types import ModuleType
from typing import cast

import pytest
from buzz import Buzz
from roadshow import RoadshowError, demo
from roadshow.core import capture_demo, decompose_demo, discover_demos


@demo("source")
def sample_source():
    """Print a sample value for source extraction."""
    print("source sample")


@demo("input")
def sample_read_input():
    """Read the injected input and display the temporary home."""
    print(input())
    print(sys.argv[1])
    print(os.environ["HOME"])


@demo("errors")
def sample_exit():
    """Exit with a nonzero status."""
    raise SystemExit(4)


@demo("errors")
def sample_error():
    """Raise a sample error."""
    raise RuntimeError("sample failure")


@demo("output")
def sample_stderr():
    """Write a warning to standard error."""
    print("warning", file=sys.stderr)


def nested_demo():
    """Call a nested function."""

    def nested():
        print("nested output")

    nested()


def unmarked_helper():
    """Remain undiscovered because this function is not marked."""


def test_discover_demos_returns_only_marked_local_functions_in_order():
    demos = discover_demos(sys.modules[__name__])

    assert [function.__name__ for function in demos] == [
        "sample_error",
        "sample_exit",
        "sample_read_input",
        "sample_source",
        "sample_stderr",
    ]
    assert unmarked_helper not in demos


def test_discover_demos_ignores_marked_functions_from_other_modules():
    foreign_module = ModuleType("foreign_module")
    foreign_module.__dict__["sample_source"] = sample_source

    assert discover_demos(foreign_module) == []


def test_demo_requires_exactly_one_nonempty_feature():
    assert issubclass(RoadshowError, Buzz)
    call_demo = cast(Callable[..., object], demo)

    with pytest.raises(TypeError):
        call_demo()
    with pytest.raises(TypeError):
        call_demo("basic", "extra")
    with pytest.raises(RoadshowError, match="non-empty string"):
        demo("")
    with pytest.raises(RoadshowError, match="surrounding whitespace"):
        demo(" basic")
    with pytest.raises(RoadshowError, match="non-empty string"):
        call_demo(None)
    with pytest.raises(RoadshowError, match="before hook must be callable"):
        call_demo("basic", before="not callable")
    with pytest.raises(RoadshowError, match="after hook must be callable"):
        call_demo("basic", after="not callable")
    with pytest.raises(RoadshowError, match="input_text must be a string"):
        call_demo("basic", input_text=1)
    with pytest.raises(RoadshowError, match="argv must be a sequence of strings"):
        call_demo("basic", argv=("valid", None))


def test_decompose_demo_extracts_docstring_and_function_body():
    details = decompose_demo(sample_source)

    assert details.name == "sample_source"
    assert details.module == "test_core"
    assert details.docstring == "Print a sample value for source extraction."
    assert details.source == "print('source sample')\n"


def test_decompose_demo_handles_nested_blocks():
    details = decompose_demo(nested_demo)
    source_lines = details.source.splitlines()

    assert source_lines[0] == "def nested():"
    assert source_lines[1].startswith("    print(")
    assert source_lines[-1] == "nested()"


def test_decompose_demo_requires_a_docstring():
    def missing_docstring():
        pass

    with pytest.raises(RoadshowError, match="has no docstring"):
        decompose_demo(missing_docstring)


def test_capture_demo_captures_output_input_argv_and_isolates_home(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HOME", "/original/home")

    result = capture_demo(sample_read_input, input_text="Ada\n", argv=("--example",))

    assert result.succeeded
    assert result.stdout is not None
    assert result.stdout.startswith("Ada\n--example\n")
    assert "/original/home" not in result.stdout
    assert os.environ["HOME"] == "/original/home"


def test_capture_demo_captures_exit_code():
    result = capture_demo(sample_exit)

    assert result.exit_code == 4
    assert not result.succeeded


def test_capture_demo_captures_exception():
    result = capture_demo(sample_error)

    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "sample failure"
    assert not result.succeeded


def test_capture_demo_runs_lifecycle_hooks_and_captures_their_output():
    events: list[str] = []

    def before():
        events.append("before")
        print("setup")

    def example():
        events.append("demo")
        print("running")

    def after():
        events.append("after")
        print("cleanup")

    function = demo("hooks", before=before, after=after)(example)
    result = capture_demo(function)

    assert events == ["before", "demo", "after"]
    assert result.stdout == "setup\nrunning\ncleanup\n"
    assert result.succeeded


def test_capture_demo_runs_after_hook_when_demo_raises():
    events: list[str] = []

    def example():
        raise RuntimeError("demo failed")

    def after():
        events.append("after")

    result = capture_demo(demo("hooks", after=after)(example))

    assert events == ["after"]
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "demo failed"


def test_capture_demo_runs_after_hook_when_before_hook_raises():
    events: list[str] = []

    def before():
        raise RuntimeError("setup failed")

    def example() -> None:
        pass

    def after():
        events.append("after")

    result = capture_demo(demo("hooks", before=before, after=after)(example))

    assert events == ["after"]
    assert isinstance(result.error, RuntimeError)
    assert str(result.error) == "setup failed"
