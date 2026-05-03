from __future__ import annotations

import argparse
import difflib
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


RUN_TIMEOUT_SECONDS = 2.0
MAX_DIFF_LINES = 80


class TestError(Exception):
    pass


@dataclass(frozen=True)
class Sample:
    name: str
    input_path: Path
    output_path: Path


@dataclass(frozen=True)
class RunResult:
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool = False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a local Codeforces solution against its sample tests.",
        usage="cf-test [--lang cpp|python] <contest-id> <problem-id>",
    )
    parser.add_argument("contest_id", help="Codeforces contest id, for example: 2204")
    parser.add_argument("problem_id", help="Codeforces problem id, for example: A")
    parser.add_argument(
        "--lang",
        choices=("cpp", "python"),
        default="cpp",
        help="Solution language to run. Defaults to cpp.",
    )
    args = parser.parse_args(argv)

    try:
        problem_dir = resolve_problem_dir(args.contest_id, args.problem_id)
        samples = find_samples(problem_dir)
        if args.lang == "cpp":
            solution = require_file(problem_dir / "solution.cpp")
            command = compile_cpp(solution, problem_dir)
        else:
            solution = require_file(problem_dir / "solution.py")
            command = [sys.executable, str(solution)]

        print(f"Running {solution}")
        passed = run_samples(command, samples)
    except TestError as exc:
        print(f"cf-test: {exc}", file=sys.stderr)
        return 1

    return 0 if passed else 1


def resolve_problem_dir(contest_id: str, problem_id: str) -> Path:
    if not contest_id.isdigit():
        raise TestError("contest id must be numeric")

    problem_id = problem_id.strip().upper()
    if not problem_id:
        raise TestError("problem id must not be empty")

    problem_dir = Path(f"contest-{contest_id}") / problem_id
    if not problem_dir.is_dir():
        raise TestError(f"missing problem directory: {problem_dir}")
    return problem_dir


def require_file(path: Path) -> Path:
    if not path.is_file():
        raise TestError(f"missing file: {path}")
    return path


def find_samples(problem_dir: Path) -> list[Sample]:
    tests_dir = problem_dir / "tests"
    if not tests_dir.is_dir():
        raise TestError(f"missing tests directory: {tests_dir}")

    samples: list[Sample] = []
    for input_path in sorted(tests_dir.glob("sample-*.in")):
        output_path = input_path.with_suffix(".out")
        if not output_path.is_file():
            raise TestError(f"missing expected output for {input_path}: {output_path}")
        samples.append(Sample(input_path.stem, input_path, output_path))

    if not samples:
        raise TestError(f"no sample inputs found in {tests_dir}")
    return samples


def compile_cpp(solution: Path, problem_dir: Path) -> list[str]:
    build_dir = Path(".cache") / "cf-test" / problem_dir.parts[0] / problem_dir.parts[1]
    build_dir.mkdir(parents=True, exist_ok=True)
    binary = build_dir / "solution"
    command = [
        "g++",
        "-std=c++20",
        "-O2",
        "-Wall",
        "-Wextra",
        str(solution),
        "-o",
        str(binary),
    ]
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        print(result.stderr.rstrip(), file=sys.stderr)
        raise TestError(f"failed to compile {solution}")
    return [str(binary)]


def run_samples(command: list[str], samples: list[Sample]) -> bool:
    passed = True
    for sample in samples:
        result = run_one(command, sample.input_path.read_text(encoding="utf-8"))
        expected = sample.output_path.read_text(encoding="utf-8")

        if result.timed_out:
            passed = False
            print(f"{sample.name}: time limit exceeded ({RUN_TIMEOUT_SECONDS:g}s)")
            if result.stderr.strip():
                print(result.stderr.rstrip(), file=sys.stderr)
            continue

        if result.returncode != 0:
            passed = False
            print(f"{sample.name}: runtime error ({result.returncode})")
            if result.stderr.strip():
                print(result.stderr.rstrip(), file=sys.stderr)
            continue

        if normalize_output(result.stdout) == normalize_output(expected):
            print(f"{sample.name}: OK")
            continue

        passed = False
        print(f"{sample.name}: WA")
        print_diff(expected, result.stdout)

    return passed


def run_one(command: list[str], stdin: str) -> RunResult:
    try:
        result = subprocess.run(
            command,
            input=stdin,
            text=True,
            capture_output=True,
            check=False,
            timeout=RUN_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        return RunResult(-1, _timeout_text(exc.stdout), _timeout_text(exc.stderr), timed_out=True)
    return RunResult(result.returncode, result.stdout, result.stderr)


def normalize_output(value: str) -> str:
    return "\n".join(line.rstrip() for line in value.rstrip().splitlines())


def print_diff(expected: str, actual: str) -> None:
    expected_lines = normalize_output(expected).splitlines()
    actual_lines = normalize_output(actual).splitlines()
    diff = difflib.unified_diff(
        expected_lines,
        actual_lines,
        fromfile="expected",
        tofile="actual",
        lineterm="",
    )
    for index, line in enumerate(diff, start=1):
        if index > MAX_DIFF_LINES:
            print(f"... diff truncated after {MAX_DIFF_LINES} lines")
            break
        print(line)


def _timeout_text(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


if __name__ == "__main__":
    raise SystemExit(main())
