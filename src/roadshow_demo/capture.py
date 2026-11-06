import sys

import roadshow


@roadshow.demo("capture")
def show_exception_capture() -> None:
    """
    This demo shows how Roadshow captures an exception raised directly by a demo function.

    It raises a `ValueError` so Roadshow can display the exception and mark this demo as failed without stopping the
    remaining demos from running.
    """
    raise ValueError("example failure")


@roadshow.demo("capture")
def show_exit_capture() -> None:
    """
    This demo shows how Roadshow captures a non-zero `SystemExit` raised directly by a demo function.

    It exits with status 7 so Roadshow can display the exit status and mark this demo as failed without terminating the
    process immediately.
    """
    raise SystemExit(7)


@roadshow.demo("capture")
def show_stream_capture() -> None:
    """
    This demo shows how Roadshow captures standard output and standard error from a demo function.

    It writes one message to each stream directly. Roadshow displays the captured streams after this function returns.
    """
    print("This message is captured from standard output.")
    print("This warning is captured from standard error.", file=sys.stderr)


@roadshow.demo("capture", input_text="Ada\n", argv=("--example",))
def show_input_capture() -> None:
    """
    This demo shows how to configure input and command-line arguments for one demo with `@demo`.

    It reads the configured name from standard input and displays the configured arguments from `sys.argv`, using the
    normal Roadshow capture path without a nested `capture_demo` call.
    """
    print(f"Hello, {input()}.")
    print(f"Arguments: {sys.argv[1:]}")


