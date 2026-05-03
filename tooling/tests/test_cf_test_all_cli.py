from __future__ import annotations

from pathlib import Path

from cf_stuff.cf_test.all_cli import main


def write_sample(problem_dir: Path) -> None:
    tests_dir = problem_dir / "tests"
    tests_dir.mkdir(parents=True)
    (tests_dir / "sample-1.in").write_text("1 2\n", encoding="utf-8")
    (tests_dir / "sample-1.out").write_text("3\n", encoding="utf-8")


def test_checks_cpp_and_python_solutions(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    problem_dir = tmp_path / "contest-1000" / "A"
    write_sample(problem_dir)
    (problem_dir / "solution.cpp").write_text(
        """\
#include <iostream>

int main() {
    int a, b;
    std::cin >> a >> b;
    std::cout << a + b << '\\n';
}
""",
        encoding="utf-8",
    )
    (problem_dir / "solution.py").write_text(
        """\
a, b = map(int, input().split())
print(a + b)
""",
        encoding="utf-8",
    )

    assert main([]) == 0

    captured = capsys.readouterr()
    assert "contest-1000/A (cpp)" in captured.out
    assert "contest-1000/A (python)" in captured.out
    assert "Checked 2 solution(s)" in captured.out


def test_skip_file_skips_problem_directory(tmp_path: Path, monkeypatch, capsys) -> None:
    monkeypatch.chdir(tmp_path)
    problem_dir = tmp_path / "contest-1000" / "A"
    write_sample(problem_dir)
    (problem_dir / "solution.py").write_text("print(4)\n", encoding="utf-8")
    skip_file = tmp_path / "ci-skip-solutions.txt"
    skip_file.write_text("contest-1000/A\n", encoding="utf-8")

    assert main(["--skip-file", str(skip_file)]) == 1

    captured = capsys.readouterr()
    assert "no solutions found" in captured.err
