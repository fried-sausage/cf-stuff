from __future__ import annotations

from pathlib import Path

import cf_stuff.cf_test.cli as cf_test_cli


def write_problem(root: Path, *, cpp: str | None = None, python: str | None = None, expected: str = "3\n") -> None:
    problem_dir = root / "contest-1000" / "A"
    tests_dir = problem_dir / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "sample-1.in").write_text("1 2\n", encoding="utf-8")
    (tests_dir / "sample-1.out").write_text(expected, encoding="utf-8")
    if cpp is not None:
        (problem_dir / "solution.cpp").write_text(cpp, encoding="utf-8")
    if python is not None:
        (problem_dir / "solution.py").write_text(python, encoding="utf-8")


def test_cpp_solution_passes(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    write_problem(
        tmp_path,
        cpp="""\
#include <iostream>

int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << '\\n';
}
""",
    )

    assert cf_test_cli.main(["1000", "A"]) == 0

    captured = capsys.readouterr()
    assert "sample-1: OK" in captured.out


def test_python_solution_passes_when_selected(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    write_problem(
        tmp_path,
        cpp="""\
int main() {
    return 1;
}
""",
        python="""\
a, b = map(int, input().split())
print(a + b)
""",
    )

    assert cf_test_cli.main(["--lang", "python", "1000", "A"]) == 0

    captured = capsys.readouterr()
    assert "solution.py" in captured.out
    assert "sample-1: OK" in captured.out


def test_selected_python_file_must_exist(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    write_problem(
        tmp_path,
        cpp="""\
int main() {
    return 0;
}
""",
    )

    assert cf_test_cli.main(["--lang", "python", "1000", "A"]) == 1

    captured = capsys.readouterr()
    assert "missing file: contest-1000/A/solution.py" in captured.err


def test_wrong_answer_fails(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    write_problem(
        tmp_path,
        python="""\
print(4)
""",
    )

    assert cf_test_cli.main(["--lang", "python", "1000", "A"]) == 1

    captured = capsys.readouterr()
    assert "sample-1: WA" in captured.out
    assert "--- expected" in captured.out
    assert "+++ actual" in captured.out


def test_slow_solution_times_out(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cf_test_cli, "RUN_TIMEOUT_SECONDS", 0.1)
    write_problem(
        tmp_path,
        python="""\
while True:
    pass
""",
    )

    assert cf_test_cli.main(["--lang", "python", "1000", "A"]) == 1

    captured = capsys.readouterr()
    assert "sample-1: time limit exceeded (0.1s)" in captured.out


def test_large_diff_is_truncated(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(cf_test_cli, "MAX_DIFF_LINES", 10)
    write_problem(
        tmp_path,
        python="""\
for value in range(100):
    print(value)
""",
    )

    assert cf_test_cli.main(["--lang", "python", "1000", "A"]) == 1

    captured = capsys.readouterr()
    assert "sample-1: WA" in captured.out
    assert "... diff truncated after 10 lines" in captured.out
