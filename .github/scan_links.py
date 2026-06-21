#!/usr/bin/env python3
"""Compatibility wrapper for file-level wikilink checks."""

from scanlink import VAULT, scan


def main() -> int:
    result = scan()
    for item in sorted(result.broken_files, key=lambda x: (x.source.as_posix(), x.target)):
        src = item.source.relative_to(VAULT).as_posix()
        print(f"BROKEN: [{src}] -> [[{item.raw}]]")
    if result.broken_files:
        print(f"\nTotal: {len(result.broken_files)} broken links")
        return 1
    print("No broken wikilinks found!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
