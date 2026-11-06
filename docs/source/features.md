# Features

Roadshow turns tagged Python functions into demos that can be discovered, run, captured, and rendered.


## Tag demos and build a CLI

Mark each demo with one feature name. Roadshow groups tagged functions by feature and displays each function's docstring
with its source and output.

```python
--8<-- "examples/feature_groups.py"
```

Create an entrypoint that scans the package and starts the CLI:

```python
from roadshow import Roadshow


def main() -> None:
    Roadshow("my_app", title="My app").run()


if __name__ == "__main__":
    main()
```

Select one or more feature groups with `--feature`; repeat the option to select multiple groups. Omit it to run every
group. By default, Roadshow asks for confirmation before starting and after each demo. `--non-interactive` skips those
prompts, runs all selected demos, and exits with status 1 if any demo fails. Roadshow displays a failure and continues to
the next demo unless the user stops an interactive run.

The `errors` demo below intentionally raises an exception, so its command displays the captured error and exits 1:

```shell
--8<-- "examples/run_cli.sh"
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


## Supply input and arguments

Set `input_text` and `argv` on the decorator to give a demo predictable standard input and command-line arguments. The
first `sys.argv` value is the demo function name.

```python
--8<-- "examples/input_helpers.py"
```

The demo reads `Ada` from `input()` and sees `("--formal",)` in `sys.argv[1:]`. Explicit `input_text` or `argv`
arguments to `capture_demo()` and `display_demo()` override the decorator fixtures.


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


## Raise application errors

`RoadshowError` derives from `buzz.Buzz`. Use it or its Buzz validation methods when a demo needs to report invalid setup:

```python
--8<-- "examples/error_handling.py"
```
