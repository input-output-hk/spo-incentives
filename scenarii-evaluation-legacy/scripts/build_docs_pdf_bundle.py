#!/usr/bin/env python3
"""
Build PDFs for all markdown documents in scenarii-evaluation/docs and merge them.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

SCENARII_DIR = Path(__file__).resolve().parents[1]
DOCS_DIR = SCENARII_DIR / "docs"
REPO_ROOT = SCENARII_DIR.parents[1]
DEFAULT_BUILD_DIR = REPO_ROOT / "tmp" / "pdfs" / "scenarii-evaluation-docs"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "pdf" / "scenarii-evaluation-docs"
PANDOC_FROM = (
    "markdown+tex_math_dollars+tex_math_double_backslash+"
    "tex_math_single_backslash+pipe_tables+task_lists+gfm_auto_identifiers"
)


@dataclass(frozen=True)
class DocBuild:
    original: Path
    prepared: Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build per-document PDFs and a merged PDF for scenarii-evaluation docs."
    )
    parser.add_argument(
        "--docs-dir",
        type=Path,
        default=DOCS_DIR,
        help="Directory containing markdown documents.",
    )
    parser.add_argument(
        "--build-dir",
        type=Path,
        default=DEFAULT_BUILD_DIR,
        help="Temporary directory used for intermediate files.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Destination directory for final PDF artifacts.",
    )
    parser.add_argument(
        "--merged-name",
        default="scenarii-evaluation-docs-merged.pdf",
        help="Filename for the merged PDF artifact.",
    )
    return parser.parse_args()


def ensure_tool(name: str) -> None:
    if shutil.which(name) is None:
        raise SystemExit(f"Missing required tool: {name}")


def run(cmd: list[str], cwd: Path) -> None:
    subprocess.run(cmd, cwd=cwd, check=True)


def clean_dir(path: Path) -> None:
    shutil.rmtree(path, ignore_errors=True)
    path.mkdir(parents=True, exist_ok=True)


def strip_manual_contents(lines: list[str]) -> list[str]:
    output: list[str] = []
    index = 0
    removable_headings = {"## Table of Contents", "## Contents"}

    while index < len(lines):
        if lines[index].strip() in removable_headings:
            index += 1
            while index < len(lines) and not lines[index].startswith("#"):
                index += 1
            continue
        output.append(lines[index])
        index += 1

    return output


def sanitize_markdown(text: str) -> str:
    lines = text.splitlines()
    lines = strip_manual_contents(lines)
    return "\n".join(lines).rstrip() + "\n"


def prepare_markdown_sources(docs: list[Path], docs_dir: Path) -> list[DocBuild]:
    prepared_docs: list[DocBuild] = []

    for doc in docs:
        prepared_path = docs_dir / f".pdf-src-{doc.stem}.md"
        prepared_path.write_text(sanitize_markdown(doc.read_text(encoding="utf-8")), encoding="utf-8")
        prepared_docs.append(DocBuild(original=doc, prepared=prepared_path))

    return prepared_docs


def pandoc_base_command() -> list[str]:
    return [
        "pandoc",
        f"--from={PANDOC_FROM}",
        "--standalone",
        "--pdf-engine=xelatex",
        "--pdf-engine-opt=-interaction=nonstopmode",
        "--pdf-engine-opt=-halt-on-error",
        "--resource-path=.:..",
        "-V",
        "geometry:margin=1in",
        "-V",
        "papersize:letter",
    ]


def build_individual_pdfs(docs: list[Path], docs_dir: Path, output_dir: Path) -> list[Path]:
    generated: list[Path] = []

    for doc in docs:
        final_path = output_dir / f"{doc.stem}.pdf"
        cmd = pandoc_base_command() + [
            "-V",
            "documentclass:article",
            "-o",
            str(final_path),
            doc.name,
        ]
        run(cmd, cwd=docs_dir)
        generated.append(final_path)

    return generated


def build_merged_pdf(docs: list[DocBuild], docs_dir: Path, output_dir: Path, merged_name: str) -> Path:
    final_path = output_dir / merged_name
    build_date = datetime.now().astimezone().strftime("%B %d, %Y %H:%M %Z")
    cmd = pandoc_base_command() + [
        "--toc",
        "--toc-depth=2",
        "--top-level-division=chapter",
        "-V",
        "documentclass:report",
        "-V",
        "classoption:oneside",
        "-M",
        "title=Scenarii Evaluation Documents",
        "-M",
        f"date={build_date}",
        "-M",
        "author=Codex",
        "-o",
        str(final_path),
        *[doc.prepared.name for doc in docs],
    ]
    run(cmd, cwd=docs_dir)
    return final_path


def merge_pdfs(pdf_paths: list[Path], merged_path: Path) -> None:
    run(["pdfunite", *[str(path) for path in pdf_paths], str(merged_path)], cwd=merged_path.parent)


def main() -> int:
    args = parse_args()
    docs_dir = args.docs_dir.resolve()
    build_dir = args.build_dir.resolve()
    output_dir = args.output_dir.resolve()

    ensure_tool("pandoc")
    ensure_tool("xelatex")
    ensure_tool("pdfunite")

    docs = sorted(path for path in docs_dir.glob("*.md") if path.is_file())
    if not docs:
        raise SystemExit(f"No markdown documents found in {docs_dir}")

    clean_dir(build_dir)
    clean_dir(output_dir)
    prepared_docs: list[DocBuild] = []

    try:
        prepared_docs = prepare_markdown_sources(docs, docs_dir)
        build_individual_pdfs(docs, docs_dir, output_dir)
        merged_from_sources = build_merged_pdf(prepared_docs, docs_dir, output_dir, args.merged_name)

        ordered_pdfs = [output_dir / f"{doc.stem}.pdf" for doc in docs]
        merged_bundle = output_dir / "scenarii-evaluation-docs-concatenated.pdf"
        merge_pdfs(ordered_pdfs, merged_bundle)

        print(f"Built {len(ordered_pdfs)} individual PDFs in {output_dir}")
        print(f"Merged markdown-aware PDF: {merged_from_sources}")
        print(f"Concatenated merged PDF: {merged_bundle}")
        return 0
    finally:
        for doc in prepared_docs:
            doc.prepared.unlink(missing_ok=True)


if __name__ == "__main__":
    sys.exit(main())
