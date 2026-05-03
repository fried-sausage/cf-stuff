from __future__ import annotations

from cf_stuff.cf_download.refs import ProblemRef


def write_problem(ref: ProblemRef, markdown: str, samples: list[tuple[str, str]]) -> None:
    problem_dir = ref.local_dir
    tests_dir = problem_dir / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    (problem_dir / "statement.md").write_text(markdown, encoding="utf-8")

    for pattern in ("sample-*.in", "sample-*.out"):
        for old_sample in tests_dir.glob(pattern):
            old_sample.unlink()

    for index, (sample_input, sample_output) in enumerate(samples, start=1):
        (tests_dir / f"sample-{index}.in").write_text(ensure_final_newline(sample_input), encoding="utf-8")
        (tests_dir / f"sample-{index}.out").write_text(ensure_final_newline(sample_output), encoding="utf-8")


def ensure_final_newline(value: str) -> str:
    return value if value.endswith("\n") else value + "\n"
