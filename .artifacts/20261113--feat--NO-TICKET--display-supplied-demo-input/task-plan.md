# Task plan: Display Supplied Demo Input

Render the effective stdin fixture when a demo supplies input, and accept line lists as an alternative to `input_text`.
Keep the existing string API and the captured stdin behavior compatible.

## Goal

Extend demo input configuration and overrides in `demo()`, `capture_demo()`, and `display_demo()` so callers can provide
lines without embedding newline escapes and `display_demo()` visibly renders non-empty stdin before the demo's results.
Preserve the exact behavior of existing `input_text` callers. Do not change argv, output capture, or interactive input.

## Project commands

### Run unit tests

Command:

```shell
make qa/test/unit
```

Expected output:

All unit tests pass and the configured coverage threshold is met.

### Run lint checks

Command:

```shell
make qa/lint
```

Expected output:

Ruff and typos complete without findings.

### Run type checks

Command:

```shell
make qa/types
```

Expected output:

`ty` reports no type errors in the package, tests, or demo package.

### Build documentation

Command:

```shell
make docs/build
```

Expected output:

Zensical builds the documentation successfully.

## Project standards

- [Contribution guidelines](../../CONTRIBUTING.md)
- [Makefile quality and documentation commands](../../Makefile)
- [Python and pytest configuration](../../pyproject.toml)
- [Feature documentation](../../docs/source/features.md)

## Steps

1. Add failing unit tests in `tests/unit/test_core.py` for line-list validation and stdin normalization through decorator
   configuration and `capture_demo()` overrides; cover multiple lines, an empty list, and rejection of scalar strings and
   bytes or line breaks inside a line for `input_lines`.
2. Add failing cases in `tests/unit/test_render.py` confirming `display_demo()` shows the effective supplied stdin for
   configured and overridden input, and omits the input panel when no non-empty input is supplied.
3. Run `make qa/test/unit` and confirm the new cases fail for the missing behavior.
4. Add an `input_lines` alternative to `demo()`, `capture_demo()`, and `display_demo()` in `src/roadshow/core.py` and
   `src/roadshow/render.py`. Use `None` to distinguish an omitted input option, keep the omitted decorator fixture
   equivalent to an empty string, validate a non-string sequence of strings, rejecting scalar strings, bytes, and line breaks inside a line; normalize each line to newline-terminated stdin (for
   example, `['Ada', 'Grace']` becomes `"Ada\nGrace\n"` and `[]` becomes `""`), and reject calls that provide both forms.
5. Keep `input_text` accepted as-is and preserve existing decorator defaults and method-level overrides. Use the same
   normalized effective stdin for both capture and rendering.
6. Render a clearly titled stdin panel in `src/roadshow/render.py` only when the effective stdin is non-empty. Display
   its supplied contents, including line breaks, without changing captured stdout/stderr panels.
7. Update `src/roadshow_demo/capture.py` to demonstrate the line-list configuration and update the input section in
   `docs/source/features.md` to document both forms, normalization, overrides, and the rendered input panel.
8. Run `make qa/test/unit` and confirm all unit tests pass; then run `make qa/lint`, `make qa/types`, and `make docs/build`.

## Acceptance criteria

- AC01: `demo(..., input_lines=['Ada', 'Grace'])` and `capture_demo(..., input_lines=['Ada', 'Grace'])` supply
  `"Ada\nGrace\n"` to stdin; an empty line list supplies an empty stream.
- AC02: Existing `input_text` calls continue to supply their exact string unchanged, and method-level input overrides
  still replace decorator-configured input.
- AC03: Providing both `input_text` and `input_lines` to the same API raises the project's `RoadshowError` validation
  error.
- AC04: `display_demo()` renders a distinct stdin panel containing effective non-empty input from decorator
  configuration or an explicit override, and renders no stdin panel when no input is supplied.
- AC05: `make qa/test/unit`, `make qa/lint`, `make qa/types`, and `make docs/build` all complete successfully.

## Technical notes

The current input fixture is stored by `demo()` and converted to `io.StringIO` in `capture_demo()`; `display_demo()` calls
`capture_demo()` but currently renders only stdout, stderr, errors, and exit status. Relevant paths are
`src/roadshow/core.py:56`, `src/roadshow/core.py:139`, and `src/roadshow/render.py:17`. Existing input behavior is covered in
`tests/unit/test_core.py:132`, `tests/unit/test_app.py:35`, and `tests/unit/test_render.py:13`; usage docs are in
`docs/source/features.md:59`.

Treat each item in `input_lines` as one logical input line and terminate it with `\n`; this makes a one-line list
`['Ada']` equivalent to the existing common fixture `input_text='Ada\n'` while keeping the legacy string API byte-for-byte
unchanged. The unit test target is `make qa/test/unit`; `make qa/lint`, `make qa/types`, and `make docs/build` are defined
in the project Makefile.
