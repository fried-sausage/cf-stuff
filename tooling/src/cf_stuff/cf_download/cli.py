from __future__ import annotations

import argparse
import sys

from cf_stuff.cf_download.fetch import fetch_problem
from cf_stuff.cf_download.parse import parse_problem_page
from cf_stuff.cf_download.refs import parse_problem_ref
from cf_stuff.cf_download.render import markdown_for_problem
from cf_stuff.cf_download.write import write_problem
from cf_stuff.errors import DownloadError


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Download one Codeforces problem into this repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="cf-download <contest-id> <problem-id>\n"
        "       cf-download <problem-url>",
        epilog="""accepted forms:
  cf-download 2204 A
  cf-download 2185 C
  cf-download https://codeforces.com/contest/2204/problem/A
  cf-download https://codeforces.com/problemset/problem/2204/A

writes:
  contest-<contest-id>/<problem-id>/statement.md
  contest-<contest-id>/<problem-id>/tests/sample-*.in
  contest-<contest-id>/<problem-id>/tests/sample-*.out

existing solution files are left untouched.""",
    )
    parser.add_argument(
        "problem",
        nargs="+",
        metavar="PROBLEM",
        help="Either '<contest-id> <problem-id>' or '<problem-url>'",
    )
    args = parser.parse_args(argv)

    try:
        ref = parse_problem_ref(args.problem)
    except DownloadError as exc:
        print(f"cf-download: {exc}", file=sys.stderr)
        return 1

    try:
        html_text = fetch_problem(ref.fetch_url)
        problem = parse_problem_page(html_text, ref)
        markdown = markdown_for_problem(
            ref,
            problem.title,
            problem.time_limit,
            problem.memory_limit,
            problem.statement,
        )
        write_problem(ref, markdown, problem.samples)
    except DownloadError as exc:
        print(f"cf-download: {exc}", file=sys.stderr)
        return 1

    print(f"Downloaded {ref.contest_id}{ref.problem} to {ref.local_dir}")
    print(f"Wrote statement.md and {len(problem.samples)} sample test(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
