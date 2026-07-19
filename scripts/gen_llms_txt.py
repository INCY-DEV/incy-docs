#!/usr/bin/env python3
"""Generate llms.txt + llms-full.txt for the INCY dev-docs.

Runs AFTER `mkdocs build`, independently of any MkDocs plugin, so it does not
interfere with the mkdocs-static-i18n suffix scheme (RU `*.md` + EN `*.en.md`).
It reads the nav from mkdocs.yml and the Russian source Markdown files, then
writes:

  - <site>/llms.txt       — the llms.txt index (title, blurb, grouped links)
  - <site>/llms-full.txt  — the whole doc corpus concatenated, for tools that
                            want everything in one file

The links point at the raw Markdown on the docs site (`<page>.md`), which the
build already publishes next to the HTML, and at the GitHub raw source as a
fallback. Only stdlib is used — no new build dependency.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = REPO_ROOT / "ru" / "dev-docs"
MKDOCS_YML = REPO_ROOT / "mkdocs.yml"

SITE_URL = "https://docs.incy.cc"
GITHUB_RAW = "https://raw.githubusercontent.com/INCY-DEV/incy-docs/main/ru/dev-docs"

SITE_NAME = "INCY Developer Documentation"
SITE_BLURB = (
    "Technical documentation for integrating with the INCY app: subscription "
    "format, share-link parameters, full Xray configs, routing, deep links, "
    "HWID, Premium API, provider settings, and examples. Bilingual (RU default, "
    "EN copies live at /en/)."
)


def parse_nav(mkdocs_text: str) -> list[tuple[str, list[tuple[str, str]]]]:
    """Extract nav as [(section_title, [(page_title, filename.md), ...]), ...].

    Handrolled parse of the `nav:` block — avoids a YAML dependency. Top-level
    entries are either `- Title: file.md` (a page in the implicit root section)
    or `- Section:` followed by indented `- Title: file.md` children.
    """
    lines = mkdocs_text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines) if ln.rstrip() == "nav:")
    except StopIteration:
        return []

    sections: list[tuple[str, list[tuple[str, str]]]] = []
    root_pages: list[tuple[str, str]] = []
    current_section: str | None = None
    current_pages: list[tuple[str, str]] = []

    # nav entry patterns
    top_page = re.compile(r"^  - (?P<title>[^:]+):\s*(?P<file>\S+\.md)\s*$")
    top_section = re.compile(r"^  - (?P<title>[^:]+):\s*$")
    child_page = re.compile(r"^      - (?P<title>[^:]+):\s*(?P<file>\S+\.md)\s*$")

    for ln in lines[start + 1 :]:
        # nav ends at the next top-level key (no leading space, non-empty).
        if ln and not ln.startswith(" ") and not ln.startswith("\t"):
            break
        if not ln.strip():
            continue

        m = top_page.match(ln)
        if m:
            if current_section is not None:
                sections.append((current_section, current_pages))
                current_section, current_pages = None, []
            root_pages.append((m.group("title").strip(), m.group("file").strip()))
            continue

        m = top_section.match(ln)
        if m:
            if current_section is not None:
                sections.append((current_section, current_pages))
            current_section = m.group("title").strip()
            current_pages = []
            continue

        m = child_page.match(ln)
        if m and current_section is not None:
            current_pages.append((m.group("title").strip(), m.group("file").strip()))
            continue

    if current_section is not None:
        sections.append((current_section, current_pages))

    # Prepend root pages as their own implicit section if any.
    result: list[tuple[str, list[tuple[str, str]]]] = []
    if root_pages:
        result.append(("Overview", root_pages))
    result.extend(sections)
    return result


def first_paragraph(md_text: str) -> str:
    """First non-heading, non-blank line — used as the per-link description."""
    for raw in md_text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("---"):
            continue
        # strip basic markdown emphasis/links for a clean one-liner
        line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
        line = re.sub(r"[*_`]", "", line)
        return line[:200]
    return ""


def page_url(filename: str) -> str:
    """Public URL of a page. MkDocs publishes clean URLs (a per-page directory
    with index.html), NOT the raw .md — so `app-management.md` is served at
    `/app-management/`, and `README.md` is the site root. We link to those."""
    stem = filename[:-3] if filename.endswith(".md") else filename
    if stem.upper() == "README":
        return f"{SITE_URL}/"
    return f"{SITE_URL}/{stem}/"


def build_llms_txt(sections) -> str:
    out: list[str] = [f"# {SITE_NAME}", "", f"> {SITE_BLURB}", ""]
    for section_title, pages in sections:
        if not pages:
            continue
        out.append(f"## {section_title}")
        for title, filename in pages:
            src = DOCS_DIR / filename
            desc = first_paragraph(src.read_text(encoding="utf-8")) if src.exists() else ""
            suffix = f": {desc}" if desc else ""
            out.append(f"- [{title}]({page_url(filename)}){suffix}")
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def build_llms_full_txt(sections) -> str:
    out: list[str] = [f"# {SITE_NAME} — Full documentation", "", f"> {SITE_BLURB}", ""]
    for section_title, pages in sections:
        for title, filename in pages:
            src = DOCS_DIR / filename
            if not src.exists():
                continue
            out.append("")
            out.append(f"# {title}")
            out.append(f"Source: {GITHUB_RAW}/{filename}")
            out.append("")
            out.append(src.read_text(encoding="utf-8").rstrip())
            out.append("")
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    site_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO_ROOT / "site"
    if not MKDOCS_YML.exists():
        print(f"error: {MKDOCS_YML} not found", file=sys.stderr)
        return 1
    sections = parse_nav(MKDOCS_YML.read_text(encoding="utf-8"))
    if not sections:
        print("error: could not parse nav from mkdocs.yml", file=sys.stderr)
        return 1

    site_dir.mkdir(parents=True, exist_ok=True)
    (site_dir / "llms.txt").write_text(build_llms_txt(sections), encoding="utf-8")
    (site_dir / "llms-full.txt").write_text(build_llms_full_txt(sections), encoding="utf-8")

    total_pages = sum(len(p) for _, p in sections)
    print(f"wrote llms.txt + llms-full.txt to {site_dir} ({total_pages} pages, {len(sections)} sections)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
