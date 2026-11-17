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

    The `before` hook is always run before a demo function and the `after` hook is always run after. Even if the demo
    function (or any of its calls) raise an exception, the `after` hook will still be run.
    """
    print("In demo function")
    raise RuntimeError("Boom!")



def _show_xdg_environment(stage: str) -> None:
    """
    Note:
        This function is replicated in the `show_xdg_isolation()` function. This is by design since demos print out the
        function body and the logic for the print loop is useful to see there. The logic is bundled in this function so
        that it can be used in the `before` and `after` hook.
    """
    XDG_ENVIRONMENT_VARIABLES = ("HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME")
    print(f"Environment {stage} demo:")
    for variable in XDG_ENVIRONMENT_VARIABLES:
        print(f"{variable}: {os.environ.get(variable, '(unset)')}")
    print()


@roadshow.demo("lifecycle", before=lambda: _show_xdg_environment("before"), after=lambda: _show_xdg_environment("after"))
def show_xdg_isolation() -> None:
    """
    This demo shows how Roadshow isolates `HOME` and XDG variables with temporary location for a demo function.

    This provides isolation so that you can place files for the code in the demo (or any of its calls) to read from
    standard locations. When the demo is complete, the temporary folders are discarded and the environment variables are
    restored to their prior values.
    """
    XDG_ENVIRONMENT_VARIABLES = ("HOME", "XDG_CACHE_HOME", "XDG_CONFIG_HOME", "XDG_STATE_HOME")
    print("Environment during demo:")
    for variable in XDG_ENVIRONMENT_VARIABLES:
        print(f"{variable}: {os.environ.get(variable, '(unset)')}")
    print()
