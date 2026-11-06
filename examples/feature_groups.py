"""
Demonstrate how Roadshow groups demos by the feature they are showing off.

Note:
    Since this demo is not a part of a package, we need to use `get_standalone_module()`.
    For demos that are part of a package, just pass the package name as the first arg to `Roadshow()` or use the special
    `__package__` variable.

"""
from roadshow import Roadshow, demo, get_standalone_module


@demo("First Feature")
def feature_1_1():
    """This function demonstrates the first aspect of feature 1."""
    print("Look at how cool feature 1 is!")

@demo("First Feature")
def feature_1_2():
    """This function demonstrates the second aspect of feature 1."""
    print("Look at what else feature 1 can do!")


@demo("Second Feature")
def feature_2_1():
    """This function demonstrates the first aspect of feature 2."""
    print("Look at how cool feature 2 is!")

@demo("Second Feature")
def feature_2_2():
    """This function demonstrates the second aspect of feature 2."""
    print("Look at what else feature 2 can do!")


if __name__ == "__main__":
    Roadshow(get_standalone_module(), title="examples").run()
