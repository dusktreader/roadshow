# Change Log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/)
and this project adheres to [Semantic Versioning](http://semver.org/).


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
