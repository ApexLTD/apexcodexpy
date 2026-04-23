# codexpy

The Non-Destructive Configuration Steward for Python Projects.

codexpy is a CLI tool designed to enforce consistent linting and typing standards across multiple projects.
Unlike standard runners, codexpy synchronizes your pyproject.toml with a "Gold Standard" configuration
without destroying existing project-specific settings or comments.

## 🚀 Purpose

Modern Python development often suffers from "Config Drift"—where different projects slowly diverge in their ruff or mypy settings. codexpy solves this by:

### Enforcing Standards

Overwriting critical linting rules with a centralized set of best practices.

### Preserving Context

Using tomlkit to ensure that your hand-written comments and formatting remain intact.

### Dry-Run Capability

Allowing developers to see exactly what would change before any modifications are written to disk.

## 📦 Installation & Integration
From PyPI

Since codexpy is available on PyPI, you can add it directly to your project using Poetry:

```sh
poetry add apexcodexpy --group dev
```

## 🛠 Usage

### 1. Synchronize Configuration

Align your pyproject.toml with the codexpy standards.

```sh
# Preview changes (Dry Run)
codex update --dry-run

# Apply changes
codex update
```

### 2. Run Linting & Formatting checks

Run the enforced toolchain (Ruff and Mypy) on your project.

```sh
# Standard run (verbose)
codex lint

# No output (suppress stdout/stderr)
codex lint --silent
```

### 3. Auto formating and fixing

Run the enforced toolchain (Ruff and Mypy) on your project.

```sh
# Standard run (verbose)
codex fix

# No output (suppress stdout/stderr)
codex fix --silent
```

## 🧩 Standards Enforced

codexpy currently enforces a strict ruff.lint.select list including:

| Name                    | Code |
|-------------------------|------|
| pyflakes                | F    |
| pycodestyle (Errors)    | E    |
| pycodestyle (Warnings)  | W    |
| isort                   | I    |
| pep8-naming             | N    |
| pyupgrade               | UP   |
| flake8-bugbear          | B    |
| flake8-builtins         | A    |
| flake8-comprehensions   | C4   |
| flake8-print            | T20  |
| flake8-pytest-style     | PT   |
| flake8-raise            | RSE  |
| flake8-return           | RET  |
| flake8-simplify         | SIM  |
| flake8-unused-arguments | ARG  |


It also enforces mypy.strict = true.


## 👨‍💻 For Developers: How it Works

Non-Destructive Merge

The core logic resides in a functional deep_merge. It takes the project's current TOML and the codexpy standards,
returns a new sorted configuration, and preserves all tomlkit item metadata (inline comments).

### Architecture: Strategy Pattern

- Task Protocol: implementations run various tools and report their results.
- Device Protocol: used by reporter to output results. 
- Reporter: standard output format.
- PyCodex: Class that ties everything together.

### To add a new tool:

- Create a new Task implementation.
- Add the tool's standard config to get_standards().
- Register the task in PyCodex.
- Add CLI command using the above mentioned PyCodex method.
