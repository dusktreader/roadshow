import roadshow


@roadshow.demo("basic")
def show_output() -> None:
    """
    This demo shows how Roadshow automatically captures standard output from a demo function.

    Anything sent to `sys.stdout` will be captured by Roadshow and printed within the demo display.
    """
    print("Hello from a directly captured demo.")


