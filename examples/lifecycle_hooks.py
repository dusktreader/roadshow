"""
Demonstrate how Roadshow can use the `before` and `after` lifecycle hooks around a demo function.

Note:
    Since this demo is not a part of a package, we need to use `get_standalone_module()`.
    For demos that are part of a package, just pass the package name as the first arg to `Roadshow()` or use the special
    `__package__` variable.

"""
from roadshow import Roadshow, demo, get_standalone_module


def announce_start():
    print("Before the demo function")


def announce_finish():
    print("After the demo function")


@demo("Lifecycle Hooks", before=announce_start, after=announce_finish)
def before_and_after():
    """This function shows how Roadshow runs `before` and `after` lifecycle hooks around a demo function."""
    print("Inside the demo function")


if __name__ == "__main__":
    Roadshow(get_standalone_module(), title="examples").run()
