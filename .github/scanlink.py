#!/usr/bin/env python3
"""Scan and conservatively repair Obsidian wikilinks in this vault.

Default scan roots intentionally skip hidden/config folders and Backups.  The
repair mode only applies mechanical fixes that are safe for repeated use:

1. ``[[Target\]]`` -> ``[[Target]]`` for accidental escaped closing brackets.
2. Treat ``[[Target\|Alias]]`` as a valid alias link in Markdown tables.
3. ``[[Target#Missing heading|Alias]]`` -> ``[[Target|Alias]]`` when the file
   exists but the heading does not.
"""

from __future__ import annotations

import argparse
import dataclasses
import re
from pathlib import Path
from typing import Iterable


VAULT = Path(__file__).resolve().parents[1]
DEFAULT_SCAN_ROOTS = (
    "Foundations",
    "PapersRecap",
    "Projects",
    "Quiz",
    "MergeBuffer",
    "Example",
    "README.md",
)
KNOWN_TARGET_RENAMES = {
    "ANYmal Parkour Recap": "ANYmal parkour Learning agile navigation for quadrupedal robots",
    "Beyond Human Demonstrations Recap": "Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training",
    "CMA-ES Tutorial Recap": "The CMA Evolution Strategy: A Tutorial",
    "Curiosity-Driven Exploration Recap": "Curiosity-Driven Exploration via Latent Bayesian Surprise",
    "Curious Exploration via Structured WM Recap": "Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation",
    "Deep Dynamics Models Recap": "Deep Dynamics Models for Learning Dexterous Manipulation",
    "DeXtreme Recap": "DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality",
    "DexNDM- Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model": "DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model",
    "DexterityGen Recap": "DEXTERITYGEN- Foundation Controller for Unprecedented Dexterity",
    "DiWA- Diffusion Policy Adaptation with World Models Recap": "DiWA- Diffusion Policy Adaptation with World Models",
    "Diffusion Policy Recap": "Diffusion Policy: Visuomotor Policy",
    "Finetuning Offline WM Recap": "Finetuning Offline World Models in the Real World",
    "FLD Recap": "FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning",
    "From Simple to Complex Skills Recap": "From Simple to Complex Skills- The Case of In-Hand Object Reorientation",
    "Improving Policy Optimization GSL Recap": "Improving Policy Optimization with Generalist-Specialist Learning",
    "Is Attention Required for ICL Recap": "IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY",
    "Latent Space Survey Recap": "The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook",
    "Learning to Walk in Minutes Recap": "Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models",
    "Paired Open-Ended Trailblazer (POET)": "Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions",
    "Prioritized Level Replay Recap": "Prioritized Level Replay",
    "SafeDreamer Recap": "SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL",
    "Sim-to-Real Agile Locomotion Recap": "Sim-to-Real: Learning Agile Locomotion For Quadruped Robots",
    "Solving Rubiks Cube Recap": "SOLVING RUBIK’S CUBE WITH A ROBOT HAND",
    "SOLVING RUBIK'S CUBE WITH A ROBOT HAND": "SOLVING RUBIK’S CUBE WITH A ROBOT HAND",
    "STORM Recap": "STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning",
}
SKIP_DIRS = {
    ".git",
    ".obsidian",
    ".vscode",
    ".claude",
    ".claudian",
    ".github",
    "Backups",
    "tmp",
}
TEXT_EXTENSIONS = {".md"}
IGNORED_LINK_SCHEMES = ("http://", "https://", "mailto:")
ASSET_EXTENSIONS = {
    ".base",
    ".canvas",
    ".gif",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".mp4",
    ".ogg",
    ".pdf",
    ".png",
    ".svg",
    ".txt",
    ".webp",
}

WIKILINK_RE = re.compile(r"(!?)\[\[([^\]\n]+?)\]\]")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
ESCAPED_CLOSE_RE = re.compile(r"(?<=\[\[)([^\]\n]*?)\\(?=\]\])")


@dataclasses.dataclass(frozen=True)
class WikiLink:
    source: Path
    embed: bool
    raw: str
    target: str
    heading: str | None
    alias: str | None


@dataclasses.dataclass(frozen=True)
class BrokenFileLink:
    source: Path
    target: str
    raw: str


@dataclasses.dataclass(frozen=True)
class BrokenHeadingLink:
    source: Path
    target: str
    heading: str
    alias: str | None
    raw: str


@dataclasses.dataclass
class ScanResult:
    broken_files: list[BrokenFileLink]
    broken_headings: list[BrokenHeadingLink]

    @property
    def ok(self) -> bool:
        return not self.broken_files and not self.broken_headings


def iter_scan_paths(scan_roots: Iterable[str] = DEFAULT_SCAN_ROOTS) -> list[Path]:
    paths: list[Path] = []
    for root in scan_roots:
        path = VAULT / root
        if not path.exists():
            continue
        if path.is_file() and path.suffix in TEXT_EXTENSIONS:
            paths.append(path)
            continue
        if path.is_dir():
            for child in path.rglob("*"):
                if any(part in SKIP_DIRS for part in child.relative_to(VAULT).parts):
                    continue
                if child.is_file() and child.suffix in TEXT_EXTENSIONS:
                    paths.append(child)
    return sorted(set(paths))


def iter_all_vault_files() -> list[Path]:
    files: list[Path] = []
    for child in VAULT.rglob("*"):
        if any(part in SKIP_DIRS for part in child.relative_to(VAULT).parts):
            continue
        if child.is_file():
            files.append(child)
    return sorted(files)


def strip_code_fences(text: str) -> str:
    """Blank fenced code blocks so example wikilinks are not treated as links."""
    lines = text.splitlines(keepends=True)
    in_fence = False
    output: list[str] = []
    for line in lines:
        if re.match(r"^\s*(```|~~~)", line):
            in_fence = not in_fence
            output.append("\n")
        elif in_fence:
            output.append("\n")
        else:
            output.append(line)
    return "".join(output)


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`\n]*`", lambda match: " " * len(match.group(0)), text)


def parse_wikilink(source: Path, embed: str, body: str) -> WikiLink | None:
    body = body.strip()
    if not body or body.startswith(IGNORED_LINK_SCHEMES):
        return None
    target_part, alias = split_alias(body)
    target_part = target_part.strip()
    alias = alias.strip() if alias else None

    target, heading = split_once(target_part, "#")
    target = target.strip()
    heading = heading.strip() if heading else None
    if not target:
        return None
    return WikiLink(source, bool(embed), body, target, heading, alias)


def split_once(text: str, separator: str) -> tuple[str, str | None]:
    if separator not in text:
        return text, None
    left, right = text.split(separator, 1)
    return left, right


def split_alias(text: str) -> tuple[str, str | None]:
    """Split Obsidian aliases, accepting escaped pipes used inside tables."""
    escaped = r"\|"
    if escaped in text:
        left, right = text.split(escaped, 1)
        return left, right
    return split_once(text, "|")


def extract_wikilinks(path: Path) -> list[WikiLink]:
    text = strip_inline_code(strip_code_fences(path.read_text(encoding="utf-8")))
    links: list[WikiLink] = []
    for match in WIKILINK_RE.finditer(text):
        link = parse_wikilink(path, match.group(1), match.group(2))
        if link:
            links.append(link)
    return links


def build_target_index() -> set[str]:
    """Build all names Obsidian-style links can reasonably resolve to."""
    targets: set[str] = set()
    for path in iter_all_vault_files():
        rel = path.relative_to(VAULT).as_posix()
        stem_rel = path.with_suffix("").relative_to(VAULT).as_posix()
        targets.add(path.name)
        targets.add(path.stem)
        targets.add(rel)
        targets.add(stem_rel)
        parts = rel.split("/")
        stem_parts = stem_rel.split("/")
        for i in range(1, len(parts)):
            targets.add("/".join(parts[i:]))
        for i in range(1, len(stem_parts)):
            targets.add("/".join(stem_parts[i:]))
    return targets


def collect_headings(paths: Iterable[Path]) -> dict[str, set[str]]:
    headings: dict[str, set[str]] = {}
    for path in paths:
        rel = path.relative_to(VAULT).as_posix()
        keys = {path.stem, rel, path.with_suffix("").relative_to(VAULT).as_posix()}
        text = strip_code_fences(path.read_text(encoding="utf-8"))
        file_headings = set()
        for line in text.splitlines():
            match = HEADING_RE.match(line)
            if match:
                file_headings.add(match.group(2).strip())
        for key in keys:
            headings[key] = file_headings
    return headings


def is_asset_target(target: str) -> bool:
    return Path(target).suffix.lower() in ASSET_EXTENSIONS


def target_exists(target: str, target_index: set[str]) -> bool:
    if target in target_index:
        return True
    if is_asset_target(target):
        return target in target_index or Path(target).name in target_index
    return False


def scan(scan_roots: Iterable[str] = DEFAULT_SCAN_ROOTS) -> ScanResult:
    paths = iter_scan_paths(scan_roots)
    target_index = build_target_index()
    headings = collect_headings(paths)
    broken_files: list[BrokenFileLink] = []
    broken_headings: list[BrokenHeadingLink] = []

    for path in paths:
        for link in extract_wikilinks(path):
            if not target_exists(link.target, target_index):
                broken_files.append(BrokenFileLink(path, link.target, link.raw))
                continue
            if link.heading and not link.heading.startswith("^"):
                target_headings = headings.get(link.target)
                if target_headings is not None and link.heading not in target_headings:
                    broken_headings.append(
                        BrokenHeadingLink(
                            link.source,
                            link.target,
                            link.heading,
                            link.alias,
                            link.raw,
                        )
                    )
    return ScanResult(dedupe(broken_files), dedupe(broken_headings))


def dedupe(items: list):
    seen = set()
    result = []
    for item in items:
        key = dataclasses.astuple(item)
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


def deanchor_broken_heading(raw: str) -> str:
    target_part, alias = split_once(raw, "|")
    target, _heading = split_once(target_part, "#")
    if alias:
        return f"{target}|{alias}"
    return target


def fix_escape_sequences(paths: Iterable[Path]) -> int:
    changed = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        new_text = ESCAPED_CLOSE_RE.sub(lambda match: match.group(1), text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


def fix_broken_headings(result: ScanResult) -> int:
    by_file: dict[Path, list[BrokenHeadingLink]] = {}
    for item in result.broken_headings:
        by_file.setdefault(item.source, []).append(item)

    changed = 0
    for path, links in by_file.items():
        text = path.read_text(encoding="utf-8")
        new_text = text
        for link in sorted(links, key=lambda item: len(item.raw), reverse=True):
            replacement = deanchor_broken_heading(link.raw)
            new_text = new_text.replace(f"[[{link.raw}]]", f"[[{replacement}]]")
            new_text = new_text.replace(f"![[{link.raw}]]", f"![[{replacement}]]")
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


def replace_target(raw: str, new_target: str) -> str:
    target_part, alias = split_alias(raw)
    _target, heading = split_once(target_part, "#")
    replacement = new_target
    if heading:
        replacement = f"{replacement}#{heading}"
    if alias:
        separator = r"\|" if r"\|" in raw else "|"
        replacement = f"{replacement}{separator}{alias}"
    return replacement


def fix_known_file_renames(result: ScanResult) -> int:
    by_file: dict[Path, list[BrokenFileLink]] = {}
    for item in result.broken_files:
        if item.target in KNOWN_TARGET_RENAMES:
            by_file.setdefault(item.source, []).append(item)

    changed = 0
    for path, links in by_file.items():
        text = path.read_text(encoding="utf-8")
        new_text = text
        for link in sorted(links, key=lambda item: len(item.raw), reverse=True):
            replacement = replace_target(link.raw, KNOWN_TARGET_RENAMES[link.target])
            new_text = new_text.replace(f"[[{link.raw}]]", f"[[{replacement}]]")
            new_text = new_text.replace(f"![[{link.raw}]]", f"![[{replacement}]]")
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


def print_result(result: ScanResult) -> None:
    for item in sorted(result.broken_files, key=lambda x: (x.source.as_posix(), x.target)):
        src = item.source.relative_to(VAULT).as_posix()
        print(f"BROKEN FILE: [{src}] -> [[{item.raw}]]")
    for item in sorted(
        result.broken_headings,
        key=lambda x: (x.source.as_posix(), x.target, x.heading),
    ):
        src = item.source.relative_to(VAULT).as_posix()
        print(f"BROKEN HEADING: [{src}] -> [[{item.raw}]]")

    if result.ok:
        print("No broken wikilinks found!")
    else:
        print(
            f"\nTotal: {len(result.broken_files)} file links, "
            f"{len(result.broken_headings)} heading links"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fix", action="store_true", help="apply conservative repairs")
    parser.add_argument(
        "--roots",
        nargs="*",
        default=list(DEFAULT_SCAN_ROOTS),
        help="vault-relative files or directories to scan",
    )
    args = parser.parse_args()

    if args.fix:
        paths = iter_scan_paths(args.roots)
        escape_files = fix_escape_sequences(paths)
        first_pass = scan(args.roots)
        rename_files = fix_known_file_renames(first_pass)
        second_pass = scan(args.roots)
        heading_files = fix_broken_headings(second_pass)
        print(f"Fixed escaped wikilinks in {escape_files} files.")
        print(f"Repaired known renamed wikilinks in {rename_files} files.")
        print(f"Removed broken heading anchors in {heading_files} files.")

    result = scan(args.roots)
    print_result(result)
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
