---
name: pdf
description: Read, inspect, extract from, create, or review PDF files when rendering, layout, formulas, tables, figures, citations, or visual fidelity matter. Use for paper PDFs, folders of PDFs, PDF recap preparation, PDF text extraction, PDF visual review, PDF generation, or validating that a PDF renders correctly; prefer Poppler rendering plus pdfplumber/pypdf/pdftotext extraction instead of relying on plain text alone.
---

# PDF

Use this skill whenever a task depends on PDF content or rendering. For research papers, use this before writing a recap: PDF text extraction alone is not reliable enough for two-column layouts, equations, tables, figure captions, ligatures, and appendix details.

## Core Rule

Do not rely on a single extractor. Use a layered pass:

1. `pdfinfo` for page count and metadata.
2. `pdftotext -layout` for fast full-text extraction.
3. `pdfplumber` or `pypdf` for page-level text, tables, and extraction cross-checks.
4. `pdftoppm` to render representative pages to PNG.
5. Visual inspection of rendered PNGs when layout, formulas, tables, figures, or reading accuracy matters.

For paper recaps, combine this skill with `$paper-recap-insight`: run the PDF probe first, then use the rendered pages and extracted text to reconstruct theory, variables, experiments, tables, and ablations.

## Workspace Workflow

1. Put intermediate artifacts under `tmp/pdfs/` from the current workspace when possible.
   - Use one subdirectory per PDF stem.
   - Remove temporary files when they are not useful to keep.
2. For a folder of PDFs, process one PDF at a time. Do not merge unrelated papers into one reading context.
3. Before writing outputs, inspect local project conventions.
   - If a sibling recap folder exists, such as `RelatedPapersRecap/`, put recap notes there.
   - Preserve the PDF basename exactly for recap filenames unless the user says otherwise: `Paper Name.pdf` -> `Paper Name.md`.
   - Keep `paper-pdf` frontmatter pointing to the exact PDF filename/path.

## Reading Workflow

### 1. Probe the PDF

Prefer the bundled script:

```bash
python3 /Users/yang/.codex/skills/pdf/scripts/pdf_probe.py "paper.pdf" --out "tmp/pdfs/paper"
```

If working from a repo-local skill, use:

```bash
python3 .github/skills/pdf/scripts/pdf_probe.py "paper.pdf" --out "tmp/pdfs/paper"
```

The probe writes:

- `manifest.json` with metadata, selected pages, rendered PNG paths, and extraction notes.
- `pdftotext-layout.txt` with layout-preserving text.
- `pdfplumber-pages.txt` with page-separated text.
- `pages/page-*.png` rendered by Poppler.

### 2. Inspect Rendered Pages

Render at least:

- page 1 for title, authors, venue, abstract, and layout.
- pages containing `method`, `approach`, `model`, `experiment`, `ablation`, `table`, `appendix`, or `limitations`.
- representative table/figure pages when the recap depends on numbers or visual evidence.

Use image inspection for rendered pages. If a table, equation, or figure is unreadable in extracted text, trust the PNG and manually reconstruct the content from the rendered page.

### 3. Extract With Cross-Checks

Use `pdftotext -layout` for broad search:

```bash
pdftotext -layout "paper.pdf" "tmp/pdfs/paper/pdftotext-layout.txt"
```

Use `pdfplumber` for page-level text and table attempts. Use `pypdf` when `pdfplumber` fails or for quick metadata/page count checks. Treat all extracted formulas as suspect until checked against rendering.

Search the extracted text for:

```text
Abstract
Introduction
Method
Approach
Model
Objective
Experiment
Ablation
Table
Figure
Appendix
Limitations
Conclusion
```

### 4. Read Tables And Figures

For tables:

- Preserve task names, metrics, baselines, and headline numbers.
- If extraction breaks columns, render the table page and read visually.
- Never infer numbers from a garbled text row.

For figures:

- Read captions visually when extraction is incomplete.
- Use figures to recover method information flow, architecture, experiment setup, and ablation meaning.

For equations:

- Reconstruct from rendered pages when text extraction drops symbols.
- Check that LaTeX commands survive as visible backslash commands; watch for broken `\theta`, `\tau`, `\right`, and `\text` caused by string escaping.

## Creating Or Reviewing PDFs

When creating PDFs programmatically:

- Use `reportlab` for generated PDFs.
- Render final pages with `pdftoppm`.
- Inspect PNGs for clipped text, overlaps, unreadable glyphs, broken tables, black squares, poor margins, and bad page transitions.

Rendering command:

```bash
pdftoppm -png "$INPUT_PDF" "$OUTPUT_PREFIX"
```

Final delivery requires the latest rendered PNG inspection to show no visual or formatting defects.

## Quality Gate

Before using PDF-derived content in a final answer or recap, check:

- Page count and metadata were recorded.
- Title, abstract, method, experiments, ablations, limitations, and appendix were searched.
- At least representative pages were rendered to PNG.
- Tables/figures/equations that matter were checked visually.
- Extracted formulas do not contain broken control-character artifacts.
- Output location follows the workspace convention, not just the PDF directory.
- Temporary files are organized under `tmp/pdfs/` or removed.
