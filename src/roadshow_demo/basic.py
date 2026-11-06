import roadshow


@roadshow.demo("basic")
def show_output() -> None:
    """
    This demo shows how Roadshow automatically captures standard output from a demo function.

    It prints a greeting directly. Roadshow displays the captured text after this function returns without requiring a
    nested function or an explicit call to `capture_demo`.
    """
    print("Hello from a directly captured demo.")


