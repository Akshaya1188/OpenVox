# Contributing to OpenVox

Thanks for your interest in improving OpenVox! This project aims to stay
small, readable, and easy for beginners to extend, so contributions that
keep that spirit are especially welcome.

## Getting started

1. Fork the repository and clone your fork.
2. Create a conda or venv environment and install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pytest
   ```
3. Create a branch for your change:
   ```bash
   git checkout -b feature/my-improvement
   ```

## Making changes

- Keep new code in `openvox/core/` organized by responsibility (speech,
  commands, profile, assistant orchestration).
- Avoid hardcoding values that belong in `openvox/config.py` — assistant
  name, language, voice settings, and file paths should all be
  configurable.
- Avoid platform-specific APIs (e.g. `sapi5`, `win32api`) unless they are
  behind an optional, clearly-labeled platform check.
- Prefer small, focused functions over large ones.
- Add or update tests for any new command or behavior. Tests must not
  depend on a physical microphone — use a fake/mock speech object, as
  shown in `tests/test_commands.py`.

## Adding a new voice command

1. Add a `cmd_your_feature` method to `CommandHandler` in
   `openvox/core/commands.py`.
2. Register it in `_build_routes()` with the trigger phrases it should
   respond to. Put more specific triggers above more general ones.
3. Add a short mention of the command to `cmd_help`.
4. Add a test in `tests/test_commands.py`.
5. Update the "Available Commands" section of `README.md`.

## Running tests

```bash
cd tests
pytest
```

(or `pytest` from the repository root, since `conftest.py` configures
the import path automatically).

## Submitting a pull request

- Keep pull requests focused on a single change where possible.
- Describe what the change does and why in the PR description.
- Make sure `pytest` passes before submitting.

## Questions

Open a GitHub issue if you're not sure whether a change fits the
project's scope — happy to discuss before you write code.
