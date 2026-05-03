from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from cf_stuff.errors import DownloadError


CODEFORCES_BASE = "https://codeforces.com"
ProblemKind = Literal["contest", "problemset", "gym"]


@dataclass(frozen=True)
class ProblemRef:
    kind: ProblemKind
    contest_id: str
    problem: str

    @property
    def fetch_url(self) -> str:
        if self.kind == "gym":
            return f"{CODEFORCES_BASE}/gym/{self.contest_id}/problem/{self.problem}"
        return f"{CODEFORCES_BASE}/contest/{self.contest_id}/problem/{self.problem}"

    @property
    def source_url(self) -> str:
        return self.fetch_url

    @property
    def local_dir(self) -> Path:
        return Path(f"contest-{self.contest_id}") / self.problem


def parse_problem_ref(problem_args: list[str]) -> ProblemRef:
    if len(problem_args) == 2:
        contest_or_url, problem = problem_args
        if not contest_or_url.isdigit():
            raise DownloadError("contest id must be numeric when problem is passed separately")
        return ProblemRef("contest", contest_or_url, normalize_problem(problem))

    if len(problem_args) != 1:
        raise DownloadError("pass either: cf-download <contest-id> <problem-id>, or cf-download <problem-url>")

    contest_or_url = problem_args[0]
    url_patterns: list[tuple[ProblemKind, str]] = [
        ("contest", r"/contest/(\d+)/problem/([^/?#]+)"),
        ("problemset", r"/problemset/problem/(\d+)/([^/?#]+)"),
        ("gym", r"/gym/(\d+)/problem/([^/?#]+)"),
    ]
    for kind, pattern in url_patterns:
        match = re.search(pattern, contest_or_url)
        if match:
            return ProblemRef(kind, match.group(1), normalize_problem(match.group(2)))

    raise DownloadError("pass either: cf-download <contest-id> <problem-id>, or cf-download <problem-url>")


def normalize_problem(problem: str) -> str:
    problem = problem.strip().upper()
    if not re.fullmatch(r"[A-Z][0-9A-Z]*", problem):
        raise DownloadError(f"invalid problem id: {problem!r}")
    return problem
