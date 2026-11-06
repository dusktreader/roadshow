"""
Demonstrate how Roadshow will capture exceptions raised in a demo function.

Note:
    Since this demo is not a part of a package, we need to use `get_standalone_module()`.
    For demos that are part of a package, just pass the package name as the first arg to `Roadshow()` or use the special
    `__package__` variable.

"""
from roadshow import Roadshow, demo, get_standalone_module


@demo("Error Handling")
def explode():
    """This function shows how Roadshow captures exceptions raised from a demo function."""
    print("Now we'll raise an error that Roadshow will capture and display")
    raise RuntimeError("Boom!")


if __name__ == "__main__":
    Roadshow(get_standalone_module(), title="examples").run()
