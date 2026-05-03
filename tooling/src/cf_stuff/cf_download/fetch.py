from __future__ import annotations

import time
import urllib.error
import urllib.request
from pathlib import Path

from cf_stuff.errors import DownloadError


MIN_REQUEST_INTERVAL_SECONDS = 3.0


def fetch_problem(url: str) -> str:
    wait_for_rate_limit()
    headers = {
        "User-Agent": "cf-stuff problem downloader (https://codeforces.com; one problem at a time)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }
    headers.update(read_headers_file(Path("headers.txt")))
    cookie = read_cookie_file(Path("cookie.txt"))
    if cookie:
        headers["Cookie"] = cookie

    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read()
            remember_request_time()
            charset = response.headers.get_content_charset() or "utf-8"
            return body.decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        remember_request_time()
        if exc.code == 429:
            raise DownloadError("Codeforces returned 429 Too Many Requests; wait a bit and retry") from exc
        raise DownloadError(f"Codeforces returned HTTP {exc.code} for {url}") from exc
    except urllib.error.URLError as exc:
        remember_request_time()
        raise DownloadError(f"failed to fetch {url}: {exc.reason}") from exc


def wait_for_rate_limit() -> None:
    path = Path(".cache") / "codeforces-last-request"
    try:
        last_request = float(path.read_text(encoding="utf-8").strip())
    except (FileNotFoundError, ValueError):
        return

    elapsed = time.monotonic() - last_request
    remaining = MIN_REQUEST_INTERVAL_SECONDS - elapsed
    if remaining > 0:
        time.sleep(remaining)


def remember_request_time() -> None:
    path = Path(".cache") / "codeforces-last-request"
    path.parent.mkdir(exist_ok=True)
    path.write_text(str(time.monotonic()), encoding="utf-8")


def read_headers_file(path: Path) -> dict[str, str]:
    if not path.exists():
        return {}

    headers: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            raise DownloadError(f"invalid header line in {path}: {line!r}")
        name, value = line.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def read_cookie_file(path: Path) -> str:
    if not path.exists():
        return ""
    return "; ".join(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
