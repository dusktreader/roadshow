import os

import roadshow


def _prepare_lifecycle_demo() -> None:
    print("Setup hook ran.")


def _clean_up_lifecycle_demo() -> None:
    print("Cleanup hook ran.")


@roadshow.demo("lifecycle", before=_prepare_lifecycle_demo, after=_clean_up_lifecycle_demo)
def show_lifecycle_hooks() -> None:
    """
    This demo shows how `before` and `after` callbacks surround the decorated function.

    The setup hook, this demo's body, and the cleanup hook each print a message. Roadshow captures those messages in
    execution order, demonstrating how to prepare state before a demo and release it afterward.
    """
    print("Demo ran between the setup and cleanup hooks.")


@roadshow.demo("lifecycle", after=_clean_up_lifecycle_demo)
def show_cleanup_after_exception() -> None:
    """
    This demo shows how an `after` hook runs even when a demo raises an exception.

    It raises a `RuntimeError` intentionally. Roadshow captures the failure after running the cleanup hook, so both the
    cleanup output and exception appear in this demo's report.
    """
    raise RuntimeError("example failure after setup")


_XDG_ENVIRONMENT_VARIABLES = ("HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME")


def _show_xdg_environment(stage: str) -> None:
    print(f"Environment {stage} demo:")
    for variable in _XDG_ENVIRONMENT_VARIABLES:
        print(f"{variable}: {os.environ.get(variable, '(unset)')}")
    print()


@roadshow.demo("lifecycle", before=lambda: _show_xdg_environment("before"), after=lambda: _show_xdg_environment("after"))
def show_xdg_isolation() -> None:
    """
    This demo shows how Roadshow restores `HOME` and XDG variables after a demo mutates them.

    The `before` hook prints the original process values. The function sees isolated values, mutates and prints them,
    and the `after` hook prints the restored process values. Roadshow captures all three reports.
    """
    print("Environment during demo:")
    for variable in _XDG_ENVIRONMENT_VARIABLES:
        print(f"{variable}: {os.environ.get(variable, '(unset)')}")
    print()
