"""Discover, inspect, and capture Python demo functions."""

from __future__ import annotations

import ast
import inspect
import io
import os
import sys
import tempfile
import textwrap
from collections.abc import Callable, Sequence
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from dataclasses import dataclass
from pathlib import Path
from types import FunctionType, ModuleType
from unittest.mock import patch

from roadshow.errors import RoadshowError

DemoFunction = FunctionType


@dataclass(frozen=True)
class DemoDetails:
    """Store the displayable parts of a demo function."""

    module: str
    name: str
    docstring: str
    source: str


@dataclass
class DemoResult:
    """Store output and failures captured while running a demo."""

    error: Exception | None = None
    stdout: str | None = None
    stderr: str | None = None
    exit_code: int | str | None = None

    @property
    def succeeded(self) -> bool:
        """Return whether the demo completed without an error or nonzero exit."""
        return self.error is None and self.exit_code in (None, 0)


_DEMO_FEATURE_ATTRIBUTE = "__roadshow_feature__"
_DEMO_BEFORE_ATTRIBUTE = "__roadshow_before__"
_DEMO_AFTER_ATTRIBUTE = "__roadshow_after__"
_DEMO_INPUT_TEXT_ATTRIBUTE = "__roadshow_input_text__"
_DEMO_ARGV_ATTRIBUTE = "__roadshow_argv__"


def demo(
    feature: str,
    *,
    before: Callable[[], object] | None = None,
    after: Callable[[], object] | None = None,
    input_text: str = "",
    argv: Sequence[str] = (),
) -> Callable[[DemoFunction], DemoFunction]:
    """Mark a function as a demo and attach its feature, hooks, and input fixtures."""
    RoadshowError.require_condition(
        isinstance(feature, str) and feature and feature == feature.strip(),
        "A demo feature must be a non-empty string without surrounding whitespace",
    )
    RoadshowError.require_condition(before is None or callable(before), "A demo before hook must be callable")
    RoadshowError.require_condition(after is None or callable(after), "A demo after hook must be callable")
    RoadshowError.require_condition(isinstance(input_text, str), "A demo's input_text must be a string")
    RoadshowError.require_condition(
        isinstance(argv, Sequence) and not isinstance(argv, (str, bytes)) and all(isinstance(arg, str) for arg in argv),
        "A demo's argv must be a sequence of strings",
    )
    demo_argv = tuple(argv)

    def decorate(function: DemoFunction) -> DemoFunction:
        function.__dict__[_DEMO_FEATURE_ATTRIBUTE] = feature
        function.__dict__[_DEMO_BEFORE_ATTRIBUTE] = before
        function.__dict__[_DEMO_AFTER_ATTRIBUTE] = after
        function.__dict__[_DEMO_INPUT_TEXT_ATTRIBUTE] = input_text
        function.__dict__[_DEMO_ARGV_ATTRIBUTE] = demo_argv
        return function

    return decorate


def discover_demos(module: ModuleType) -> list[DemoFunction]:
    """Return featured demo functions defined in a module, sorted by name."""
    demos = [
        member
        for _, member in inspect.getmembers(module, inspect.isfunction)
        if member.__module__ == module.__name__ and getattr(member, _DEMO_FEATURE_ATTRIBUTE, None)
    ]
    return sorted(demos, key=lambda function: function.__name__)


def decompose_demo(function: DemoFunction) -> DemoDetails:
    """Extract a demo function's docstring and executable body."""
    docstring = inspect.getdoc(function) or f"{function.__name__}() demo"

    source_lines, _ = inspect.getsourcelines(function)
    source_text = textwrap.dedent("".join(source_lines))
    syntax_tree = ast.parse(source_text)
    function_node = RoadshowError.enforce_defined(
        next(
            (
                node
                for node in syntax_tree.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == function.__name__
            ),
            None,
        ),
        f"Could not locate the source for demo function {function.__name__!r}",
    )

    body = function_node.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]

    function_node.decorator_list = []
    function_node.body = body
    source = ast.unparse(function_node) + "\n"

    return DemoDetails(
        module=function.__module__.rsplit(".", maxsplit=1)[-1],
        name=function.__name__,
        docstring=docstring,
        source=source,
    )


def capture_demo(
    function: DemoFunction,
    *,
    input_text: str | None = None,
    argv: Sequence[str] | None = None,
    isolate_home: bool = True,
) -> DemoResult:
    """Run a demo while capturing standard streams, input, and process exit."""
    configured_input_text: str = function.__dict__.get(_DEMO_INPUT_TEXT_ATTRIBUTE, "")
    configured_argv: Sequence[str] = function.__dict__.get(_DEMO_ARGV_ATTRIBUTE, ())
    effective_input_text = configured_input_text if input_text is None else input_text
    effective_argv = configured_argv if argv is None else argv
    result = DemoResult()
    stdout = io.StringIO()
    stderr = io.StringIO()
    stdin = io.StringIO(effective_input_text)

    before = function.__dict__.get(_DEMO_BEFORE_ATTRIBUTE)
    after = function.__dict__.get(_DEMO_AFTER_ATTRIBUTE)
    with ExitStack() as stack:
        stack.enter_context(redirect_stdout(stdout))
        stack.enter_context(redirect_stderr(stderr))
        stack.enter_context(patch.object(sys, "stdin", stdin))
        stack.enter_context(patch.object(sys, "argv", [function.__name__, *effective_argv]))

        try:
            try:
                if before is not None:
                    before()
                with ExitStack() as environment_stack:
                    if isolate_home:
                        temporary_home = environment_stack.enter_context(
                            tempfile.TemporaryDirectory(prefix="roadshow-")
                        )
                        home = Path(temporary_home)
                        cache_home = home / ".cache"
                        config_home = home / ".config"
                        state_home = home / ".local" / "state"
                        for path in (cache_home, config_home, state_home):
                            path.mkdir(parents=True, exist_ok=True)
                        environment_stack.enter_context(
                            patch.dict(
                                os.environ,
                                {
                                    "HOME": temporary_home,
                                    "USERPROFILE": temporary_home,
                                    "XDG_CACHE_HOME": str(cache_home),
                                    "XDG_CONFIG_HOME": str(config_home),
                                    "XDG_STATE_HOME": str(state_home),
                                    "COLUMNS": "80",
                                },
                            )
                        )

                    function()
            finally:
                if after is not None:
                    after()
        except SystemExit as exited:
            code = exited.code
            result.exit_code = 0 if code is None else code if isinstance(code, (int, str)) else str(code)
        except Exception as error:
            result.error = error

    result.stdout = stdout.getvalue() or None
    result.stderr = stderr.getvalue() or None
    return result
