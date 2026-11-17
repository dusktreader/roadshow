from io import StringIO

import pytest
from rich.console import Console
from roadshow import RoadshowError, demo
from roadshow.render import display_demo

from tests.unit.test_core import make_sample_read_stdin, sample_error, sample_exit, sample_source, sample_stderr


def sample_without_docstring():
    print("fallback demo")


def test_display_demo_renders_source_and_captured_output():
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=100)

    result = display_demo(sample_source, console, label="examples")

    rendered = output.getvalue()
    assert result.succeeded
    assert "examples: sample_source()" in rendered
    assert "def sample_source():" in rendered
    assert "print('source sample')" in rendered
    assert "source sample" in rendered


def test_display_demo_renders_configured_stdin():
    output = StringIO()
    function = demo("input", input_lines=["Ada", "Grace"], argv=("--formal",))(make_sample_read_stdin())

    display_demo(function, Console(file=output, force_terminal=False, width=100))

    rendered = output.getvalue()
    assert "Supplied args/opts" in rendered
    assert "'--formal'" in rendered
    assert "Supplied stdin" in rendered
    assert "Ada" in rendered
    assert "Grace" in rendered
    assert rendered.index("Supplied args/opts") < rendered.index("Supplied stdin")
    assert rendered.index("Supplied stdin") < rendered.index("Captured stdout")


def test_display_demo_renders_configured_argv():
    output = StringIO()
    function = demo("input", argv=("--formal", "Ada Lovelace"))(make_sample_read_stdin())

    display_demo(function, Console(file=output, force_terminal=False, width=100))

    rendered = output.getvalue()
    assert "Supplied args/opts" in rendered
    assert "'--formal'" in rendered
    assert "'Ada Lovelace'" in rendered
    assert rendered.index("Supplied args/opts") < rendered.index("Captured stdout")


def test_display_demo_renders_overridden_argv():
    output = StringIO()
    function = demo("input", argv=("--configured",))(make_sample_read_stdin())

    display_demo(
        function,
        Console(file=output, force_terminal=False, width=100),
        argv=("--override", "Ada Lovelace"),
    )

    rendered = output.getvalue()
    assert "Supplied args/opts" in rendered
    assert "'--override'" in rendered
    assert "'Ada Lovelace'" in rendered
    assert "--configured" not in rendered


def test_display_demo_omits_argv_panel_when_no_args_or_opts_are_supplied():
    output = StringIO()
    function = demo("input", argv=[])(sample_without_docstring)

    display_demo(function, Console(file=output, force_terminal=False, width=100))

    assert "Supplied args/opts" not in output.getvalue()


def test_display_demo_renders_overridden_stdin():
    output = StringIO()
    function = demo("input", input_text="Configured\ninput")(make_sample_read_stdin())

    display_demo(
        function,
        Console(file=output, force_terminal=False, width=100),
        input_lines=["Ada", "Grace"],
    )

    rendered = output.getvalue()
    assert "Supplied stdin" in rendered
    assert "Ada" in rendered
    assert "Grace" in rendered
    assert "Configured" not in rendered


def test_display_demo_rejects_both_input_forms():
    with pytest.raises(RoadshowError, match="input_text and input_lines cannot both be provided"):
        display_demo(
            sample_source,
            Console(file=StringIO(), force_terminal=False, width=100),
            input_text="Ada",
            input_lines=[],
        )


def test_display_demo_omits_stdin_panel_without_nonempty_input():
    output = StringIO()
    function = demo("input", input_lines=[])(make_sample_read_stdin())

    display_demo(function, Console(file=output, force_terminal=False, width=100))

    assert "Supplied stdin" not in output.getvalue()


def test_display_demo_uses_function_name_when_docstring_is_missing():
    output = StringIO()

    display_demo(sample_without_docstring, Console(file=output, force_terminal=False, width=100))

    assert "sample_without_docstring() demo" in output.getvalue()


def test_display_demo_renders_progress_left_aligned_in_the_outer_panel_footer():
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=100)

    display_demo(sample_source, console, progress=(2, 5))

    footer = next(line for line in output.getvalue().splitlines() if "Demo 2 of 5" in line)
    assert footer.index("Demo 2 of 5") == 3


def test_display_demo_uses_method_name_when_feature_is_absent():
    output = StringIO()

    display_demo(sample_source, Console(file=output, force_terminal=False, width=100))

    assert "sample_source()" in output.getvalue()
    assert " for test_core()" not in output.getvalue()


def test_display_demo_renders_stderr():
    output = StringIO()
    result = display_demo(sample_stderr, Console(file=output, force_terminal=False, width=100))

    assert result.stderr == "warning\n"
    assert "Captured stderr" in output.getvalue()
    assert "warning" in output.getvalue()


def test_display_demo_renders_an_exception():
    output = StringIO()
    result = display_demo(sample_error, Console(file=output, force_terminal=False, width=100))

    assert not result.succeeded
    assert "Uncaught exception" in output.getvalue()
    assert "RuntimeError: sample failure" in output.getvalue()


def test_display_demo_renders_an_exit_code():
    output = StringIO()
    result = display_demo(sample_exit, Console(file=output, force_terminal=False, width=100))

    assert result.exit_code == 4
    assert "Exit code" in output.getvalue()
    assert "4" in output.getvalue()
