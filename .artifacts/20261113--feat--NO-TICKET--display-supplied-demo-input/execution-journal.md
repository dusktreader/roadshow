# Execution Journal: Display Supplied Demo Input

A journal covering execution of the approved task plan at the path below.

## Source plan

`.artifacts/20261113--feat--NO-TICKET--display-supplied-demo-input/task-plan.md`

## Status

Complete.

## Tasks

### Task: Complete approved task plan

#### Status

Complete.

#### Overview

Implemented `input_lines` support for demo configuration, capture overrides, and rendering. `display_demo()` now renders
both effective args/options and stdin before captured output. Updated the capture demo, feature documentation, and
unit-test target. All planned checks pass.

#### Steps taken

- Added core and rendering regression tests and confirmed they failed before implementation.
- Added input validation and newline normalization shared by decorator configuration, capture overrides, and rendering.
- Added titled panels for non-empty effective stdin and args/options without changing captured stdout or stderr panels.
- Updated the capture demo and feature documentation.
- Fixed `qa/test/unit` to run the tests in `tests/unit` without a redundant marker filter; the original target selected no tests.
- Added args/options rendering for configured and overridden `argv` values, including token-preserving display.
- Removed the trailing blank line noted in execution review T01.
- Ran `make qa/test/unit`: 51 passed and coverage reached 98.50%.
- Ran `make qa/lint`, `make qa/types`, and `make docs/build`: all passed.
- Ran `git diff --check` after resolving T01: passed.

#### Files modified

- UPDATED: `src/roadshow/core.py`
- UPDATED: `src/roadshow/render.py`
- UPDATED: `tests/unit/test_core.py`
- UPDATED: `tests/unit/test_render.py`
- UPDATED: `src/roadshow_demo/capture.py`
- UPDATED: `docs/source/features.md`
- UPDATED: `Makefile`
- UPDATED: `.artifacts/20261113--feat--NO-TICKET--display-supplied-demo-input/execution-journal.md`
- UPDATED: `.artifacts/20261113--feat--NO-TICKET--display-supplied-demo-input/plan-deviations.md`

#### Acceptance criteria validation

##### Satisfied AC01: Line-list stdin normalization

`test_capture_demo_normalizes_decorator_input_lines` verifies `['Ada', 'Grace']` supplies `Ada\nGrace\n` and an empty
list supplies an empty stream (`tests/unit/test_core.py:166`). The override path is covered at
`tests/unit/test_core.py:174`.

##### Satisfied AC02: Existing string input compatibility and overrides

`test_capture_demo_normalizes_input_lines_override_and_preserves_input_text` confirms configured `input_text` remains
unchanged and method-level string and line-list overrides replace the decorator fixture (`tests/unit/test_core.py:174`).

##### Satisfied AC03: Conflicting input forms are rejected

The decorator rejects both forms at `tests/unit/test_core.py:114`; capture and display overrides are tested by
`test_capture_demo_rejects_both_input_forms` and `test_display_demo_rejects_both_input_forms`.

##### Satisfied AC04: Supplied stdin is rendered

`test_display_demo_renders_configured_stdin`, `test_display_demo_renders_overridden_stdin`, and
`test_display_demo_omits_stdin_panel_without_nonempty_input` cover configured input, override input, panel order, and
omission for an empty fixture (`tests/unit/test_render.py:29`, `tests/unit/test_render.py:86`,
`tests/unit/test_render.py:123`). Args/options panel behavior is covered by the configured, overridden, and empty-argv
cases at `tests/unit/test_render.py:42`, `tests/unit/test_render.py:55`, and `tests/unit/test_render.py:72`.

##### Satisfied AC05: Project QA commands pass

`make qa/test/unit` passes all 51 tests with 98.50% coverage. `make qa/lint`, `make qa/types`, and `make docs/build` also
pass.

#### Additional notes

Execution review C01 identified that the original unit-test target deselected all tests. The redundant marker filter was
removed and recorded as a post-plan deviation; the target then passed.

The human requested args/options to be displayed alongside stdin during execution feedback. The effective configured or
overridden `argv` is shown as one quoted token per line in a separate panel. The panel title is “Supplied args/opts” to
match the supplied stdin panel.
