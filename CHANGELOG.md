# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).

## v0.3.0 - 2026-11-23

### Added

- Configure feature group order with `Roadshow(feature_order=...)`.
- Override demo function order with `@demo(..., order=...)`.
- Run the Roadshow demo and read its CLI usage documentation.

## v0.2.1 - 2026-11-16

### Added

- Show a "Loading <demo function name>" spinner while a demo function is running.
- Add a `spinner` demo feature to `roadshow_demo`.

## v0.2.0 - 2026-11-16

### Added

- Provide `linput_lines` and `argv` helpers to set up input and args for demo functions.

## v0.1.2 - 2026-11-06

### Fixed

- Correct broken image links for pypi.org.

### Added

- Provide terminal screenshots on README and home page.

## v0.1.1 - 2026-11-06

### Fixed

- Include `roadshow_demo` package in install targets.

### Added

- Make examples runnable
- Provide `get_standalone_module()` helper for demos that are not part of a package.

## v0.1.0 - 2026-11-06

### Added

- Add a `@demo` decorator to tag demo functions, group them by feature, and configure lifecycle hooks, standard input,
  and command-line arguments.
- Discover demos in modules and packages, then run them through a Typer CLI with feature selection, interactive prompts,
  and a non-interactive mode.
- Capture demo output, exceptions, and exit codes with `capture_demo()`, including optional `HOME` and XDG environment
  isolation.
- Inspect demo documentation and source, then render the source and captured results with Rich.
- Add a runnable `roadshow-demo` application, usage examples, and user and API documentation.
