from __future__ import annotations

from pathlib import Path

import pytest

from cf_stuff.cf_download.parse import parse_problem_page
from cf_stuff.cf_download.refs import ProblemRef
from cf_stuff.cf_download.render import markdown_for_problem


FIXTURES_DIR = Path(__file__).parent / "fixtures" / "problems"


def fixture_ids() -> list[str]:
    return sorted(path.name for path in FIXTURES_DIR.iterdir() if path.is_dir())


@pytest.mark.parametrize("fixture_id", fixture_ids())
def test_parse_problem_page_and_markdown_for_problem(fixture_id: str) -> None:
    fixture_dir = FIXTURES_DIR / fixture_id
    contest_id, problem = fixture_id.split("-", 1)
    ref = ProblemRef("contest", contest_id, problem)

    parsed = parse_problem_page((fixture_dir / "page.html").read_text(encoding="utf-8"), ref)
    markdown = markdown_for_problem(
        ref,
        parsed.title,
        parsed.time_limit,
        parsed.memory_limit,
        parsed.statement,
    )

    assert markdown == (fixture_dir / "statement.md").read_text(encoding="utf-8")
    assert parsed.samples == expected_samples(fixture_dir / "samples")


def expected_samples(samples_dir: Path) -> list[tuple[str, str]]:
    samples: list[tuple[str, str]] = []
    for input_path in sorted(samples_dir.glob("sample-*.in")):
        output_path = input_path.with_suffix(".out")
        assert output_path.exists(), f"missing expected sample output: {output_path}"
        samples.append(
            (
                input_path.read_text(encoding="utf-8").rstrip("\n"),
                output_path.read_text(encoding="utf-8").rstrip("\n"),
            )
        )
    return samples
