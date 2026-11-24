# Quickstart

Mark regular Python functions with `@demo` decorators and watch Roadshow demonstrate all your projects awesome features!


## The basics

### Requirements

Roadshow requires Python 3.11 or newer.

### Install

Install Roadshow and its CLI dependencies with `pip`:

```shell
pip install roadshow
```

### Try the Roadshow demo

To see the features in action, you can run the Roadshow demo (built with Roadshow):

```shell
roadshow-demo
```


## Build your own demo

Now, you're ready to get started building your own demos for your project!

### Define tagged demos

Use `@demo` with one feature name. Function names do not need a special prefix.

```python
from roadshow import demo


@demo("basics")
def hello_world():
    """Print a greeting."""
    print("Hello from my project.")


@demo("configuration")
def show_configuration():
    """Print the active configuration."""
    print("configuration values")
```

Demos within a feature run in declaration order. An `order` value overrides a function's position:

```python
@demo("basics", order=1)
def hello_world():
    """Print a greeting before other basics demos."""
    print("Hello from my project.")
```

### The CLI entrypoint

A `main.py` function configures Roadshow and starts its Typer CLI. Feature groups are alphabetical by default; a `feature_order` value places selected groups first in a specific order. Any groups not listed remain alphabetical after them:

```python
from roadshow import Roadshow

import my_project_demo


def main():
    Roadshow(
        my_project_demo,
        title="My project",
        feature_order=("basics", "configuration"),
    ).run()

if __name__ == "__main__":
    main()
```

!!! note

```text
You must pass the module where your demos are defined to `Roadshow()`. This can be the imported module, a string
with the name of the module (will auto-import), or the special `__package__` variable. This will allow `Roadshow`
to automatically gather all the demos you have defined in that package.
```

Bind the function as a console script in `pyproject.toml`:

```toml
[project.scripts]
my-project-demo = "my_project_demo.main:main"
```

### Install your project

Before you can run the demo, you will need to install your python package locally. Typically, you will want to install
in editable mode so you can tinker on the demos while you build them:

```shell
pip install --editable .
```

### Run the demo

Since you defined an entry point in your pyproject.toml, the executable should now be available in your shell:

```shell
my-project-demo
```

You can check out options available by passing `--help` to the command.

---

## Learn about more:

- [Features](features.md)
- [Usage Examples](https://github.com/dusktreader/roadshow/tree/main/examples)
- [API reference](reference.md)
