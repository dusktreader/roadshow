# Quickstart

Mark regular Python functions with `@demo` decorators and watch Roadshow demonstrate all your projects awesome features!


## Requirements

Roadshow requires Python 3.11 or newer.


## Install

Install Roadshow and its CLI dependencies with `pip`:

```shell
pip install roadshow
```


## Define tagged demos

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


## Bind the CLI entrypoint

Create a `main.py` function that configures Roadshow and starts its Typer CLI:

```python
from roadshow import Roadshow


def main():
    Roadshow("my_project", title="My project").run()
```

Bind the function as a console script in `pyproject.toml`:

```toml
[project.scripts]
my-project-demo = "my_project.main:main"
```


## Run the demo

Now you can run your demo!

```shell
my-project-demo
```

You can check out options available by passing `--help` to the command.


## Learn about more features

Go to the [Features](features.md) page to learn about all the features `roadshow` provides.
