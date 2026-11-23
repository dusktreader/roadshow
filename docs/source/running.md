# Running the Roadshow demo

The Roadshow package includes a demo application. Its console script is `roadshow-demo`, so the demo is available without a
Roadshow source checkout.


## Starting the demo

You can run the demo without installing `roadshow` into a project's vev. Instead, you can install the `roadshow-demo`
with `uv tool`. To download Roadshow into an isolated environment:

```shell
uv tool install roadshow

```

The, run the demo:

```shell
roadshow-demo
```

A local installation provides the same command directly:

```shell
pip install roadshow
roadshow-demo
```

The welcome panel lists the discovered feature groups and the demo functions in each group. The initial confirmation
starts the interactive run, and another confirmation appears after each demo.


## Finding available options

The `--help` option describes the available command-line options:

```shell
roadshow-demo --help
```

The `--feature` option selects one or more feature groups. Repeated options select multiple groups:

```shell
roadshow-demo --feature capture --feature ordering
```

Without `--feature`, all discovered feature groups run. The Roadshow demo configures its groups in this order: `basic`,
`lifecycle`, `capture`, and `spinner`. The `ordering` group is not listed in `feature_order`, so it appears
alphabetically after the configured groups.


## Running without prompts

The `--non-interactive` option skips confirmation prompts and runs all selected demos:

```shell
roadshow-demo --feature ordering --non-interactive
```

A non-interactive run exits with status `1` when any selected demo fails. Interactive runs display the failure and continue to
the next demo unless the user stops the run.


## Applying the pattern to another project

To use `roadshow` in your project to add a demo, you just need to define the entrypoint in your `pyproject.toml`:

```toml
[project.scripts]
my-project-demo = "my_project_demo.main:main"
```

Its commands then use `my-project-demo` in place of `roadshow-demo`. Feature-group ordering comes from
`Roadshow(feature_order=...)`; function ordering comes from declaration order and any `order` values on `@demo`.

---

## Build your demo:

- [Quickstart](quickstart.md)
- [Features](features.md)
- [API reference](reference.md)
