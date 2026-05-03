from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from cf_stuff.cf_test import cli as cf_test


SKIP_FILE = Path("ci-skip-solutions.txt")


@dataclass(frozen=True)
class Solution:
    contest_id: str
    problem_id: str
    lang: str
    path: Path

    @property
    def problem_dir(self) -> Path:
        return self.path.parent

    @property
    def label(self) -> str:
        return f"{self.problem_dir} ({self.lang})"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run every local Codeforces solution against its sample tests.",
    )
    parser.add_argument(
        "--skip-file",
        default=str(SKIP_FILE),
        help="Root-relative skip file. Defaults to ci-skip-solutions.txt.",
    )
    args = parser.parse_args(argv)

    try:
        skipped = read_skip_file(Path(args.skip_file))
        solutions = find_solutions(skipped)
    except cf_test.TestError as exc:
        print(f"cf-test-all: {exc}", file=sys.stderr)
        return 1

    if not solutions:
        print("cf-test-all: no solutions found", file=sys.stderr)
        return 1

    failed: list[Solution] = []
    for solution in solutions:
        print(f"==> {solution.label}")
        test_args = [solution.contest_id, solution.problem_id]
        if solution.lang == "python":
            test_args = ["--lang", "python", *test_args]
        if cf_test.main(test_args) != 0:
            failed.append(solution)

    if failed:
        print()
        print("Failed solutions:")
        for solution in failed:
            print(f"- {solution.label}")
        return 1

    print()
    print(f"Checked {len(solutions)} solution(s)")
    return 0


def read_skip_file(path: Path) -> set[Path]:
    if not path.exists():
        return set()

    skipped: set[Path] = set()
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        skip_path = Path(line)
        if skip_path.is_absolute() or ".." in skip_path.parts:
            raise cf_test.TestError(f"invalid skip path at {path}:{line_number}: {line!r}")
        skipped.add(skip_path)
    return skipped


def find_solutions(skipped: set[Path]) -> list[Solution]:
    solutions: list[Solution] = []
    for contest_dir in sorted(Path().glob("contest-*")):
        if not contest_dir.is_dir():
            continue
        contest_id = contest_dir.name.removeprefix("contest-")
        if not contest_id.isdigit():
            continue

        for problem_dir in sorted(path for path in contest_dir.iterdir() if path.is_dir()):
            if is_skipped(problem_dir, skipped):
                continue
            problem_id = problem_dir.name
            cpp_solution = problem_dir / "solution.cpp"
            python_solution = problem_dir / "solution.py"
            if cpp_solution.is_file():
                solutions.append(Solution(contest_id, problem_id, "cpp", cpp_solution))
            if python_solution.is_file():
                solutions.append(Solution(contest_id, problem_id, "python", python_solution))
    return solutions


def is_skipped(problem_dir: Path, skipped: set[Path]) -> bool:
    return problem_dir in skipped or any(parent in skipped for parent in problem_dir.parents)


if __name__ == "__main__":
    raise SystemExit(main())
