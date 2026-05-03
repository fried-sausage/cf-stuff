My solutions to CF problems.

## Layout

Problems are grouped by contest:

```text
contest-<id>/<problem>/
  statement.md
  solution.cpp or solution.py
  tests/
    sample-1.in
    sample-1.out
```

`tooling` is for different tools that help me
work with a problem locally.

## HOWTO

Run commands from the repository root.

Download a problem:

```bash
uv run cf-download 2204 A
```

Run a C++ solution against local samples:

```bash
uv run cf-test 2204 A
```

Run a Python solution against local samples:

```bash
uv run cf-test --lang python 2185 G
```

Run all non-skipped solutions against local samples:

```bash
uv run cf-test-all
```

Run the tooling test suite:

```bash
uv run pytest
```
