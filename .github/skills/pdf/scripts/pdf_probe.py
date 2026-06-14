#!/usr/bin/env python3
"""Probe a PDF for reliable reading: metadata, text extraction, page selection, and PNG rendering."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any, Optional


KEYWORDS = [
    "abstract",
    "introduction",
    "method",
    "approach",
    "model",
    "objective",
    "experiment",
    "evaluation",
    "ablation",
    "table",
    "figure",
    "appendix",
    "limitation",
    "conclusion",
]


def run(cmd: list[str]) -> tuple[int, str, str]:
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout, proc.stderr


def parse_pdfinfo(text: str) -> dict[str, str]:
    data: dict[str, str] = {}
    for line in text.splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            data[key.strip()] = value.strip()
    return data


def page_count_with_pypdf(pdf: Path) -> Optional[int]:
    try:
        from pypdf import PdfReader

        return len(PdfReader(str(pdf)).pages)
    except Exception:
        return None


def extract_pdfplumber(pdf: Path, out: Path) -> list[dict[str, Any]]:
    pages: list[dict[str, Any]] = []
    try:
        import pdfplumber
    except Exception as exc:
        out.write_text(f"pdfplumber unavailable: {exc}\n", encoding="utf-8")
        return pages

    chunks: list[str] = []
    try:
        with pdfplumber.open(str(pdf)) as doc:
            for idx, page in enumerate(doc.pages, start=1):
                text = page.extract_text(x_tolerance=1, y_tolerance=3) or ""
                table_count = 0
                try:
                    table_count = len(page.extract_tables() or [])
                except Exception:
                    table_count = 0
                pages.append(
                    {
                        "page": idx,
                        "chars": len(text),
                        "tables": table_count,
                        "keyword_hits": [
                            kw for kw in KEYWORDS if kw in text.lower()
                        ],
                    }
                )
                chunks.append(f"\n\n===== PAGE {idx} =====\n{text}")
    except Exception as exc:
        chunks.append(f"pdfplumber extraction failed: {exc}\n")

    out.write_text("".join(chunks), encoding="utf-8")
    return pages


def select_pages(page_info: list[dict[str, Any]], page_count: int, max_pages: int) -> list[int]:
    selected: list[int] = [1]
    scored: list[tuple[int, int]] = []
    for info in page_info:
        page = int(info["page"])
        score = 0
        score += len(info.get("keyword_hits", [])) * 3
        score += min(int(info.get("tables", 0)), 3) * 2
        if page <= 2:
            score += 2
        if score:
            scored.append((score, page))

    for _, page in sorted(scored, reverse=True):
        if page not in selected:
            selected.append(page)
        if len(selected) >= max_pages:
            break

    if page_count and page_count not in selected and len(selected) < max_pages:
        selected.append(page_count)
    return sorted(p for p in selected if 1 <= p <= max(page_count, 1))


def render_pages(pdf: Path, pages: list[int], out_dir: Path, dpi: int) -> list[str]:
    rendered: list[str] = []
    pdftoppm = shutil.which("pdftoppm")
    if not pdftoppm:
        return rendered

    pages_dir = out_dir / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    for page in pages:
        prefix = pages_dir / f"page-{page}"
        before = set(pages_dir.glob(f"page-{page}*.png"))
        code, _, err = run(
            [
                pdftoppm,
                "-f",
                str(page),
                "-l",
                str(page),
                "-r",
                str(dpi),
                "-png",
                str(pdf),
                str(prefix),
            ]
        )
        after = set(pages_dir.glob(f"page-{page}*.png"))
        new_files = sorted(after - before)
        if code == 0 and new_files:
            rendered.extend(str(p) for p in new_files)
        elif err:
            (out_dir / "render-errors.log").open("a", encoding="utf-8").write(
                f"page {page}: {err}\n"
            )
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe PDF metadata, text, and rendered pages.")
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--max-pages", type=int, default=8)
    parser.add_argument("--dpi", type=int, default=160)
    args = parser.parse_args()

    pdf = args.pdf.expanduser().resolve()
    if not pdf.exists():
        raise SystemExit(f"PDF not found: {pdf}")

    out = args.out or Path("tmp/pdfs") / pdf.stem
    out = out.expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)

    manifest: dict[str, Any] = {
        "pdf": str(pdf),
        "out": str(out),
        "tools": {
            "pdfinfo": bool(shutil.which("pdfinfo")),
            "pdftotext": bool(shutil.which("pdftotext")),
            "pdftoppm": bool(shutil.which("pdftoppm")),
        },
    }

    if shutil.which("pdfinfo"):
        code, stdout, stderr = run(["pdfinfo", str(pdf)])
        (out / "pdfinfo.txt").write_text(stdout + stderr, encoding="utf-8")
        manifest["pdfinfo"] = parse_pdfinfo(stdout)
        try:
            manifest["page_count"] = int(manifest["pdfinfo"].get("Pages", "0"))
        except ValueError:
            manifest["page_count"] = None
    else:
        manifest["pdfinfo"] = {}
        manifest["page_count"] = None

    if not manifest.get("page_count"):
        manifest["page_count"] = page_count_with_pypdf(pdf)

    if shutil.which("pdftotext"):
        layout_out = out / "pdftotext-layout.txt"
        code, _, stderr = run(["pdftotext", "-layout", str(pdf), str(layout_out)])
        manifest["pdftotext_layout"] = str(layout_out) if code == 0 else None
        if code != 0:
            (out / "pdftotext-errors.log").write_text(stderr, encoding="utf-8")

    page_info = extract_pdfplumber(pdf, out / "pdfplumber-pages.txt")
    manifest["pdfplumber_pages"] = page_info

    page_count = int(manifest.get("page_count") or len(page_info) or 1)
    selected = select_pages(page_info, page_count, max(args.max_pages, 1))
    manifest["selected_pages"] = selected
    manifest["rendered_pages"] = render_pages(pdf, selected, out, args.dpi)

    (out / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
