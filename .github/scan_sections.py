#!/usr/bin/env python3
"""Compatibility wrapper for section-level wikilink checks."""

from scanlink import VAULT, scan


def main() -> int:
    result = scan()
    for item in sorted(
        result.broken_headings,
        key=lambda x: (x.source.as_posix(), x.target, x.heading),
    ):
        src = item.source.relative_to(VAULT).as_posix()
        print(f"BROKEN SECTION: [{src}] -> [[{item.raw}]]")
    if result.broken_headings:
        print(f"\nTotal: {len(result.broken_headings)} broken section links")
        return 1
    print("No broken section-level links found!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
