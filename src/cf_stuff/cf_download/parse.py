from __future__ import annotations

import html
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser

from cf_stuff.cf_download.refs import ProblemRef
from cf_stuff.errors import DownloadError


@dataclass
class Node:
    tag: str | None = None
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node | str"] = field(default_factory=list)

    def has_class(self, name: str) -> bool:
        return name in self.attrs.get("class", "").split()


class TreeParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.stack = [self.root]

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        node = Node(tag, {key: value or "" for key, value in attrs})
        self.stack[-1].children.append(node)
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}:
            self.stack.append(node)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.stack[-1].children.append(Node(tag, {key: value or "" for key, value in attrs}))

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, 0, -1):
            if self.stack[index].tag == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self.stack[-1].children.append(data)


@dataclass(frozen=True)
class ParsedProblem:
    title: str
    time_limit: str
    memory_limit: str
    statement: Node
    samples: list[tuple[str, str]]


def parse_problem_page(html_text: str, ref: ProblemRef) -> ParsedProblem:
    parser = TreeParser()
    parser.feed(html_text)

    statement = first_by_class(parser.root, "problem-statement")
    if statement is None:
        raise DownloadError("could not find Codeforces problem statement in the downloaded page")

    title = _clean_text(_text_of(first_by_class(statement, "title"))) or f"{ref.problem}. Problem"
    time_limit = strip_metadata_label(_clean_text(_text_of(first_by_class(statement, "time-limit"))), "time limit")
    memory_limit = strip_metadata_label(_clean_text(_text_of(first_by_class(statement, "memory-limit"))), "memory limit")
    samples = extract_samples(statement)
    if not samples:
        raise DownloadError("could not find sample input/output pairs")

    return ParsedProblem(title, time_limit, memory_limit, statement, samples)


def strip_metadata_label(value: str, label: str) -> str:
    value = re.sub(rf"^{re.escape(label)}\s*:?\s*", "", value, flags=re.IGNORECASE)
    return re.sub(r"(per test)(?=\d)", r"\1 ", value)


def extract_samples(statement: Node) -> list[tuple[str, str]]:
    sample_test = first_by_class(statement, "sample-test")
    if sample_test is None:
        return []

    inputs = [_pre_text(pre) for block in all_by_class(sample_test, "input") for pre in _direct_tags(block, "pre")]
    outputs = [_pre_text(pre) for block in all_by_class(sample_test, "output") for pre in _direct_tags(block, "pre")]
    if len(inputs) != len(outputs):
        raise DownloadError(f"found {len(inputs)} sample input(s) but {len(outputs)} sample output(s)")
    return list(zip(inputs, outputs))


def _pre_text(node: Node) -> str:
    return html.unescape(_pre_text_inner(node)).strip("\n")


def _pre_text_inner(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag == "br":
            parts.append("\n")
        elif child.has_class("test-example-line"):
            parts.append(_text_of(child))
            parts.append("\n")
        else:
            parts.append(_pre_text_inner(child))
    return "".join(parts)


def _text_of(node: Node | None) -> str:
    if node is None:
        return ""
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag == "br":
            parts.append("\n")
        else:
            parts.append(_text_of(child))
    return "".join(parts)


def _clean_text(value: str) -> str:
    value = html.unescape(value).replace("\xa0", " ").replace("$$$", "$")
    value = value.replace("$$^{\\text{∗}}$", "$*")
    value = value.replace("$^{\\text{∗}}$", "*")
    value = value.replace("$$^{\\text{*}}$", "$*")
    value = value.replace("$^{\\text{*}}$", "*")
    lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip() for line in value.splitlines()]
    value = "\n".join(line for line in lines if line).strip()
    if value.startswith("*") and not value.startswith("* ") and not value.startswith("**") and not value.startswith("*$"):
        return "* " + value[1:]
    return value


def first_by_class(node: Node, class_name: str) -> Node | None:
    if node.has_class(class_name):
        return node
    for child in node.children:
        if isinstance(child, Node):
            found = first_by_class(child, class_name)
            if found is not None:
                return found
    return None


def all_by_class(node: Node, class_name: str) -> list[Node]:
    found = [node] if node.has_class(class_name) else []
    for child in node.children:
        if isinstance(child, Node):
            found.extend(all_by_class(child, class_name))
    return found


def _direct_tags(node: Node, tag: str) -> list[Node]:
    return [child for child in node.children if isinstance(child, Node) and child.tag == tag]
