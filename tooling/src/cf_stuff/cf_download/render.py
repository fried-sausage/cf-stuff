from __future__ import annotations

import html
import re

from cf_stuff.cf_download.parse import Node
from cf_stuff.cf_download.refs import ProblemRef


def markdown_for_statement(statement: Node) -> str:
    chunks: list[str] = []
    for child in statement.children:
        if isinstance(child, str):
            continue
        classes = child.attrs.get("class", "").split()
        if any(name in classes for name in {"header", "sample-test", "sample-tests"}):
            continue
        rendered = render_block(child)
        if rendered:
            chunks.append(rendered)
    return "\n\n".join(chunks) + "\n"


def markdown_for_problem(
    ref: ProblemRef,
    title: str,
    time_limit: str,
    memory_limit: str,
    statement: Node,
) -> str:
    body = markdown_for_statement(statement)
    header = [
        f"# {title}",
        "",
        f"**Time limit:** {time_limit or 'unknown'}",
        f"**Memory limit:** {memory_limit or 'unknown'}",
        "",
        f"Source: {ref.source_url}",
        "",
    ]
    return "\n".join(header) + "\n" + body.strip() + "\n"


def render_block(node: Node) -> str:
    if node.has_class("section-title"):
        return f"## {clean_inline_text(text_of(node))}"

    if node.tag == "p":
        return clean_inline_text(render_inline(node))
    if node.tag == "ul":
        return "\n".join(f"- {clean_inline_text(render_inline(item))}" for item in direct_tags(node, "li"))
    if node.tag == "ol":
        return "\n".join(f"{index}. {clean_inline_text(render_inline(item))}" for index, item in enumerate(direct_tags(node, "li"), start=1))
    if node.tag == "pre":
        return f"```text\n{pre_text(node).rstrip()}\n```"
    if node.tag == "div":
        chunks = render_children_as_blocks(node)
        return "\n\n".join(chunk for chunk in chunks if chunk)
    if node.tag == "center":
        chunks = [render_block(child) for child in node.children if isinstance(child, Node)]
        return "\n\n".join(chunk for chunk in chunks if chunk)
    if node.tag == "img":
        source = node.attrs.get("src", "")
        return f" ![]({source})" if source else ""
    if node.tag in {"table"}:
        text = clean_inline_text(text_of(node))
        return text

    return clean_inline_text(render_inline(node))


def render_children_as_blocks(node: Node) -> list[str]:
    chunks: list[str] = []
    text_parts: list[str] = []

    def flush_text() -> None:
        text = clean_inline_text("".join(text_parts))
        text_parts.clear()
        if text:
            chunks.append(text)

    for child in node.children:
        if isinstance(child, str):
            text_parts.append(child)
            continue
        flush_text()
        rendered = render_block(child)
        if rendered:
            chunks.append(rendered)

    flush_text()
    return chunks


def render_inline(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
            continue
        if child.tag == "br":
            parts.append("\n")
        elif child.tag == "sup":
            parts.append("^" + clean_inline_text(render_inline(child)))
        elif child.tag == "sub":
            parts.append("_" + clean_inline_text(render_inline(child)))
        elif child.tag in {"strong", "b"}:
            parts.append(f"**{clean_inline_text(render_inline(child))}**")
        elif child.tag in {"em", "i"}:
            parts.append(f"${clean_inline_text(render_inline(child))}$" if child.has_class("tex-font-style-it") else f"*{clean_inline_text(render_inline(child))}*")
        elif child.tag == "code":
            parts.append(f"`{clean_inline_text(render_inline(child))}`")
        elif child.tag == "a":
            label = clean_inline_text(render_inline(child))
            href = child.attrs.get("href", "")
            parts.append(f"[{label}]({href})" if href else label)
        elif child.tag == "img":
            source = child.attrs.get("src", "")
            parts.append(f"![]({source})" if source else "")
        elif child.tag == "span" and ("tex-span" in child.attrs.get("class", "").split()):
            parts.append(f"${clean_inline_text(render_inline(child))}$")
        else:
            parts.append(render_inline(child))
    return "".join(parts)


def pre_text(node: Node) -> str:
    return html.unescape(pre_text_inner(node)).strip("\n")


def pre_text_inner(node: Node) -> str:
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag == "br":
            parts.append("\n")
        elif child.has_class("test-example-line"):
            parts.append(text_of(child))
            parts.append("\n")
        else:
            parts.append(pre_text_inner(child))
    return "".join(parts)


def text_of(node: Node | None) -> str:
    if node is None:
        return ""
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag == "br":
            parts.append("\n")
        else:
            parts.append(text_of(child))
    return "".join(parts)


def clean_inline_text(value: str) -> str:
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


def direct_tags(node: Node, tag: str) -> list[Node]:
    return [child for child in node.children if isinstance(child, Node) and child.tag == tag]
