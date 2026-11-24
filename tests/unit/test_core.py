import os
import sys
from collections.abc import Callable
from types import ModuleType
from typing import cast

import pytest
from buzz import Buzz
from roadshow import RoadshowError, demo
from roadshow.core import capture_demo, decompose_demo, discover_demos


@demo("features")
def ordered_features():
    """Show a feature before errors."""


@demo("errors")
def ordered_errors():
    """Show errors after features."""


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


def make_sample_read_stdin():
    def read_stdin():
        """Read all injected input."""
        print(f"<{sys.stdin.read()}>")

    return read_stdin


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
        "ordered_features",
        "ordered_errors",
        "sample_source",
        "sample_read_input",
        "sample_exit",
        "sample_error",
        "sample_stderr",
    ]
    assert unmarked_helper not in demos


def test_discover_demos_applies_order_override():
    ordered_module = ModuleType("ordered_module")

    def declared_first():
        pass

    def declared_second():
        pass

    declared_first.__module__ = ordered_module.__name__
    declared_second.__module__ = ordered_module.__name__
    demo("ordered", order=2)(declared_first)
    demo("ordered", order=1)(declared_second)
    ordered_module.__dict__.update(declared_first=declared_first, declared_second=declared_second)

    assert [function.__name__ for function in discover_demos(ordered_module)] == [
        "declared_second",
        "declared_first",
    ]


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
    with pytest.raises(RoadshowError, match="input_lines must be a sequence of strings"):
        call_demo("basic", input_lines="Ada")
    with pytest.raises(RoadshowError, match="input_lines must be a sequence of strings"):
        call_demo("basic", input_lines=b"Ada")
    with pytest.raises(RoadshowError, match="input_lines must be a sequence of strings"):
        call_demo("basic", input_lines=("Ada", None))
    with pytest.raises(RoadshowError, match="input_lines must not contain line breaks"):
        call_demo("basic", input_lines=("Ada\nGrace",))
    with pytest.raises(RoadshowError, match="input_text and input_lines cannot both be provided"):
        call_demo("basic", input_text="Ada", input_lines=("Grace",))
    with pytest.raises(RoadshowError, match="argv must be a sequence of strings"):
        call_demo("basic", argv=("valid", None))


def test_decompose_demo_extracts_docstring_signature_and_body():
    details = decompose_demo(sample_source)

    assert details.name == "sample_source"
    assert details.module == "test_core"
    assert details.docstring == "Print a sample value for source extraction."
    assert details.source == "def sample_source():\n    print('source sample')\n"


def test_decompose_demo_handles_nested_blocks():
    details = decompose_demo(nested_demo)
    source_lines = details.source.splitlines()

    nonblank_source_lines = [line for line in source_lines if line]

    assert nonblank_source_lines[0] == "def nested_demo():"
    assert nonblank_source_lines[1] == "    def nested():"
    assert nonblank_source_lines[2].startswith("        print(")
    assert nonblank_source_lines[-1] == "    nested()"


def test_decompose_demo_uses_function_name_when_docstring_is_missing():
    def missing_docstring():
        pass

    details = decompose_demo(missing_docstring)

    assert details.docstring == "missing_docstring() demo"


def test_capture_demo_captures_output_input_argv_and_isolates_home(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("HOME", "/original/home")

    result = capture_demo(sample_read_input, input_text="Ada\n", argv=("--example",))

    assert result.succeeded
    assert result.stdout is not None
    assert result.stdout.startswith("Ada\n--example\n")
    assert "/original/home" not in result.stdout
    assert os.environ["HOME"] == "/original/home"


@pytest.mark.parametrize(
    ("input_lines", "expected"),
    [(["Ada", "Grace"], "<Ada\nGrace\n>\n"), ([], "<>\n")],
)
def test_capture_demo_normalizes_decorator_input_lines(input_lines, expected):
    function = demo("input", input_lines=input_lines)(make_sample_read_stdin())

    result = capture_demo(function)

    assert result.stdout == expected


def test_capture_demo_normalizes_input_lines_override_and_preserves_input_text():
    function = demo("input", input_text="Configured\ninput")(make_sample_read_stdin())

    configured_result = capture_demo(function)
    line_result = capture_demo(function, input_lines=["Ada", "Grace"])
    text_result = capture_demo(function, input_text="Unchanged")

    assert configured_result.stdout == "<Configured\ninput>\n"
    assert line_result.stdout == "<Ada\nGrace\n>\n"
    assert text_result.stdout == "<Unchanged>\n"


@pytest.mark.parametrize(
    "input_lines",
    ["Ada", b"Ada", ["Ada\nGrace"], ["Ada\rGrace"]],
)
def test_capture_demo_rejects_invalid_input_lines(input_lines):
    with pytest.raises(RoadshowError):
        capture_demo(make_sample_read_stdin(), input_lines=input_lines)


def test_capture_demo_rejects_both_input_forms():
    with pytest.raises(RoadshowError, match="input_text and input_lines cannot both be provided"):
        capture_demo(make_sample_read_stdin(), input_text="Ada", input_lines=[])


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
