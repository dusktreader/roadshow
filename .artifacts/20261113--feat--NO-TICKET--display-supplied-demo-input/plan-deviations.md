# Post-plan changes: Display Supplied Demo Input

A chronological record of changes made after approval of the task plan, including implementation, code review, and QA.

## Source plans

- Design plan: None
- Task plan: `.artifacts/20261113--feat--NO-TICKET--display-supplied-demo-input/task-plan.md`

## Changes

### Change 01: Fix the unit-test target

#### Stage and source

Execution review, finding C01 in `execution-review--whole-plan--01.md`.

#### Request

The reviewer found that `make qa/test/unit` selected no tests and failed the coverage threshold. The review requested
aligning the target with the unit tests and rerunning the documented checks.

#### Plan alignment

This change is outside the approved plan's implementation steps, but required to satisfy AC05, which requires
`make qa/test/unit` to pass.

#### Change made

Removed the redundant `-m unit` filter from `Makefile`, so the target runs the tests located in `tests/unit`.

#### Reason

No separate human-provided reason was supplied. The change addresses reviewer finding C01 and the failed planned QA gate.

#### Verification

`make qa/test/unit` passes all 51 tests with 98.50% coverage. `make qa/lint`, `make qa/types`, `make docs/build`, and
`git diff --check` pass.

### Change 02: Render captured args and options

#### Stage and source

Execution human feedback, user request: “we'll also need to show the args/opts captured as well as the input”.

#### Request

Display the effective arguments and options captured for a demo along with its supplied stdin.

#### Plan alignment

This addition is not covered by the approved plan, which only requires rendering supplied stdin.

#### Change made

Added a titled args/options panel in `src/roadshow/render.py`, showing each effective `argv` token separately. Added tests
for configured, overridden, and empty `argv` values in `tests/unit/test_render.py`. Updated the feature documentation.

#### Reason

The user requested args/options be shown alongside input.

#### Verification

`uv run pytest tests/unit/test_render.py -k argv` passed all three targeted tests. `make qa/test/unit` passes all 51
tests with 98.50% coverage. `make qa/lint`, `make qa/types`, and `make docs/build` pass.

### Change 03: Remove trailing blank line

#### Stage and source

Execution review, finding T01 in `execution-review--whole-plan--03.md`.

#### Request

The reviewer noted an unnecessary blank line at the end of `src/roadshow_demo/capture.py`.

#### Plan alignment

This cleanup is not specified in the approved plan and does not change runtime behavior.

#### Change made

Removed the extra blank line from `src/roadshow_demo/capture.py`.

#### Reason

No separate reason was provided; this resolves reviewer finding T01.

#### Verification

`git diff --check` passes.

### Change 04: Match supplied-input panel wording

#### Stage and source

Execution human feedback, user request: use “supplied args/opts” to match the supplied-input panel.

#### Request

Change the args/options panel title from “Captured args/opts” to “Supplied args/opts”.

#### Plan alignment

This is a user-directed wording refinement to the args/options panel added after plan approval.

#### Change made

Renamed the panel to “Supplied args/opts” and updated render assertions in `tests/unit/test_render.py`.

#### Reason

The user requested wording consistent with the supplied-input panel.

#### Verification

`make qa/test/unit` passes all 51 tests with 98.50% coverage. `make qa/lint`, `make qa/types`, and `make docs/build` pass.
