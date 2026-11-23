# Features

Roadshow turns tagged Python functions into demos that can be discovered, run, captured, and rendered.


## Tag demos and build a CLI

Each demo has one feature name. Roadshow groups tagged functions by feature and displays each function's docstring with
its source and output.

```python
from roadshow import demo


@demo("First Feature")
def feature_1_1():
    """Demonstrate the first aspect of feature 1."""
    print("Look at how cool feature 1 is!")


@demo("First Feature")
def feature_1_2():
    """Demonstrate the second aspect of feature 1."""
    print("Look at what else feature 1 can do!")
```

An entrypoint scans the package and starts the CLI:

```python
from roadshow import Roadshow


def main() -> None:
    Roadshow("my_app", title="My app").run()


if __name__ == "__main__":
    main()
```


## Use the CLI

The `--help` option describes the available CLI options, including feature selection:

```shell
my-project-demo --help
```

The initial welcome panel lists the discovered feature groups and their demos. The `--feature` option selects one or more
feature groups; repeated options select multiple groups. Without the option, all feature groups run. The
`--non-interactive` option skips confirmation prompts, runs all selected demos, and exits with status 1 if any demo fails.
Roadshow displays a failure and continues to the next demo unless the user stops an interactive run.

The `errors` demo below intentionally raises an exception, so its command displays the captured error and exits 1:

```shell
my-project-demo --feature errors --non-interactive
```


## Discover demos in modules and packages

`discover_demos(module)` returns tagged functions defined directly in that module. `Roadshow(package).discover()` imports
a package and its submodules, then returns demos grouped by feature. Package discovery imports every submodule, so their
module-level code runs during discovery.

```python
from my_app import demos
from roadshow import Roadshow, discover_demos

module_demos = discover_demos(demos)
package_demos = Roadshow("my_app").discover()
```

Use `Roadshow(get_standalone_module()).run()` to discover demos in a directly executed script that is not an importable
package. The helper supplies the current `__main__` module in the same position as a package name.


## Control demo order

Functions within a feature run in declaration order by default. An `order` value overrides that position. Feature groups
are alphabetical by default; `feature_order` places listed groups first in the specified order. Groups not listed in
`feature_order` remain alphabetical after the listed groups.

```python
from roadshow import Roadshow, demo


@demo("features", order=2)
def show_features():
    """Show the product features second."""


@demo("features", order=1)
def show_feature_intro():
    """Show the feature introduction first."""


@demo("features", order=3)
def show_feature_details():
    """Show the feature details third."""


@demo("errors")
def show_errors():
    """Show error handling after the features."""


Roadshow("my_app", feature_order=("features", "errors"))
```


## Supply input and arguments

Set `input_text` and `argv` on the decorator to give a demo predictable standard input and command-line arguments. Use
`input_lines` instead when each logical input line should be separate: `["Ada", "Grace"]` supplies `"Ada\nGrace\n"` and
`[]` supplies an empty stream. Roadshow adds a newline after each line. The first `sys.argv` value is the demo function
name.

```python
--8<-- "examples/input_helpers.py"
```

The demo reads `Ada` from `input()` and sees `("--formal",)` in `sys.argv[1:]`. Explicit `input_text` or
`input_lines` arguments to `capture_demo()` and `display_demo()` replace the decorator's stdin fixture; `argv` overrides
the configured arguments. `input_text` is supplied unchanged, and callers cannot provide both input forms in one call.
`display_demo()` renders non-empty effective `argv` tokens and stdin in titled panels before captured output. The args/opts
panel shows each token separately and is omitted when `argv` is empty; the stdin panel is omitted when stdin is empty.


## Run setup and cleanup hooks

Pass zero-argument callables as `before` and `after`. Roadshow captures their output along with the demo output. It runs
`before` before home isolation. With isolation enabled, it runs `after` in a `finally` block after restoring the
caller's `HOME` and XDG values. The cleanup hook still runs if setup or the demo raises.

```python
--8<-- "examples/lifecycle_hooks.py"
```


## Capture execution results

Use `capture_demo()` to run a demo without rendering it. The result contains captured stdout and stderr, and records an
exception or exit code when one occurs. Check `succeeded` to determine whether it completed successfully.

```python
from roadshow import capture_demo


def show_report():
    print("Three records found.")


result = capture_demo(show_report)
print(result.stdout or "", end="")
if not result.succeeded:
    print(result.error or result.exit_code)
```

Capture redirects standard input, output, and error. It records ordinary exceptions in `error` and `SystemExit` in
`exit_code`. By default, it temporarily points `HOME` and the XDG cache, config, and state directories at a temporary
home, then restores the caller's environment. Pass `isolate_home=False` to retain the existing home and environment.
Capture runs code in the current process; it is not a sandbox, does not undo arbitrary side effects, and should not run
concurrently from multiple threads.


## Inspect and render demos

`decompose_demo()` returns a `DemoDetails` value with a demo's module, name, docstring, and source. The source includes
the function signature and executable body. If a demo has no docstring, Roadshow uses `function_name() demo` as its
description.

```python
from rich.console import Console
from roadshow import decompose_demo, demo
from roadshow.render import display_demo


@demo("reports")
def show_report():
    """Print a report summary."""
    print("Three records found.")


details = decompose_demo(show_report)
print(details.source)
display_demo(show_report, Console())
```

`display_demo()` runs and captures the demo before rendering its documentation, source, output, errors, and exit status.

---

## Next, check out:

- [Usage Examples](https://github.com/dusktreader/roadshow/tree/main/examples)
- [API reference](reference.md)
