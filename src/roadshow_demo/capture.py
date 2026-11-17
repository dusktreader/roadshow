import sys

import roadshow


@roadshow.demo("capture")
def show_exception_capture() -> None:
    """
    This demo shows how Roadshow captures an exception raised directly by a demo function.

    Any exception raised within a demo function (or any of its calls) will be captured and printed in the demo display.
    """
    raise ValueError("example failure")


@roadshow.demo("capture")
def show_exit_capture() -> None:
    """
    This demo shows how Roadshow captures a non-zero `SystemExit` raised directly by a demo function.

    Any `system.exit()` called or `SystemExit` exception raised within a demo function (or any of its calls) will be
    captured with its exit code and printed in the demo display.
    """
    sys.exit(7)


@roadshow.demo("capture")
def show_stream_capture() -> None:
    """
    This demo shows how Roadshow captures standard output and standard error from a demo function.

    Anything printed to `sys.stdout` or `sys.stderr` within a demo function (or any of its calls) will be captured and
    printed in the demo display.
    """
    print("This message is captured from standard output.")
    print("This warning is captured from standard error.", file=sys.stderr)


@roadshow.demo("capture", input_lines=["input-line-1", "input-line-2"], argv=("arg1", "--opt1", "--opt2=hello"))
def show_input_capture() -> None:
    """
    This demo shows how to provide `sys.stdin` data for a demo function.

    Any reads from `sys.stdin` within a demo function (or any of its calls) will receive the supplied `input_lines`.
    """
    while True:
        try:
            print(f"Input: {input()}")
        except EOFError:
            break


@roadshow.demo("capture", argv=("arg1", "--opt1", "--opt2=hello"))
def show_arv_capture() -> None:
    """
    This demo shows how to provide `sys.argv` for a demo function.

    Any reads from `sys.argv` within a demo function (or any of its calls) will receive the supplied `sys.argv`.
    """
    print(f"Arguments: {sys.argv[1:]}")

