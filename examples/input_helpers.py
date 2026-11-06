"""
Demonstrate how Roadshow can supply cli args and input to a demo function.

Note:
    Since this demo is not a part of a package, we need to use `get_standalone_module()`.
    For demos that are part of a package, just pass the package name as the first arg to `Roadshow()` or use the special
    `__package__` variable.

"""
import sys

from roadshow import Roadshow, demo, get_standalone_module


@demo("Input Helpers", input_text="Ada\n", argv=("--formal",))
def input_helpers():
    """This demo shows how Roadshow can set stdin and argv for a demo function."""
    print(f"Hello, {input()}.")
    print(sys.argv[1:])


if __name__ == "__main__":
    Roadshow(get_standalone_module(), title="examples").run()
