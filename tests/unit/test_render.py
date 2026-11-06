from io import StringIO

from rich.console import Console
from roadshow.render import display_demo

from tests.unit.test_core import sample_error, sample_exit, sample_source, sample_stderr


def test_display_demo_renders_source_and_captured_output():
    output = StringIO()
    console = Console(file=output, force_terminal=False, width=100)

    result = display_demo(sample_source, console, label="examples")

    rendered = output.getvalue()
    assert result.succeeded
    assert "examples: sample_source()" in rendered
    assert "print('source sample')" in rendered
    assert "source sample" in rendered


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
