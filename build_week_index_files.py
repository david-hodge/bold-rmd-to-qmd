#!/usr/bin/env python3
"""
build_week_index_files.py

Walks folders week1 .. week11, each expected to contain a weekN.yaml
file describing that unit's content, and:

  1. Renames any .qmd file in those folders that doesn't already start
     with an underscore, prefixing it with "_" (so Quarto treats it as
     a partial, not a standalone chapter).
  2. Reads weekN.yaml and writes unitN.qmd in the same folder, using the
     yaml's "title" as a level-1 heading and one {{< include >}} line per
     content entry, e.g.:

         # Lists and Dictionaries

         {{< include _intro.qmd >}}

         {{< include _lists.qmd >}}

Step 1 always runs before step 2, so the freshly-created unitN.qmd files
(which intentionally do NOT start with an underscore) never get caught
and renamed by step 1.

Usage:
    python build_week_index_files.py [base_dir] [--dry-run]

    base_dir   directory containing week1/ ... week11/ (default: ".")
    --dry-run  print what would happen without touching the filesystem

Requires: pyyaml  (pip install pyyaml)
"""

import sys
from pathlib import Path

import yaml

WEEK_RANGE = range(1, 12)     
WEEK_DIR_PATTERN = "week{n}"
WEEK_YAML_PATTERN = "week{n}.yaml"
UNIT_FILE_PATTERN = "unit{n}.qmd"


def add_underscore_prefix(base_dir: Path, dry_run: bool = False) -> None:
    """
    Step 1: in each weekN folder, rename .qmd files that don't start
    with "_" so that they do. Must run before generate_unit_files().

    The unitN.qmd file itself (this folder's generated output, from a
    previous run of this script) is deliberately left alone, otherwise
    re-running the script would keep renaming unitN.qmd to _unitN.qmd
    and then regenerating a fresh unitN.qmd, leaving stray duplicates.
    """
    for n in WEEK_RANGE:
        week_dir = base_dir / WEEK_DIR_PATTERN.format(n=n)
        if not week_dir.is_dir():
            continue

        unit_filename = UNIT_FILE_PATTERN.format(n=n)

        for qmd_file in sorted(week_dir.glob("*.qmd")):
            if qmd_file.name.startswith("_"):
                continue
            if qmd_file.name == unit_filename:
                continue

            new_path = qmd_file.with_name(f"_{qmd_file.name}")
            if new_path.exists():
                print(f"  ! skip {qmd_file.relative_to(base_dir)}: "
                      f"{new_path.name} already exists")
                continue

            if dry_run:
                print(f"  [dry-run] would rename "
                      f"{qmd_file.relative_to(base_dir)} -> {new_path.name}")
            else:
                qmd_file.rename(new_path)
                print(f"  renamed {qmd_file.relative_to(base_dir)} -> {new_path.name}")


def src_to_include(src: str) -> str:
    """
    Turn a content entry's `src` (e.g. 'intro.Rmd') into the include
    target used inside unitN.qmd (e.g. '_intro.qmd').
    """
    stem = Path(src).stem
    return f"_{stem}.qmd"


def generate_unit_files(base_dir: Path, dry_run: bool = False) -> None:
    """
    Step 2: read weekN.yaml and write unitN.qmd in the same folder.
    """
    for n in WEEK_RANGE:
        week_dir = base_dir / WEEK_DIR_PATTERN.format(n=n)
        yaml_path = week_dir / WEEK_YAML_PATTERN.format(n=n)

        if not yaml_path.is_file():
            print(f"  ! {yaml_path.relative_to(base_dir)} not found, skipping")
            continue

        with yaml_path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        title = data.get("title", "")
        content = data.get("content") or []

        lines = [f"# {title}", ""]
        for item in content:
            src = (item or {}).get("src")
            if not src:
                continue
            lines.append(f"{{{{< include {src_to_include(src)} >}}}}")
            lines.append("")

        while lines and lines[-1] == "":
            lines.pop()
        unit_text = "\n".join(lines) + "\n"

        unit_path = week_dir / UNIT_FILE_PATTERN.format(n=n)

        if dry_run:
            print(f"  [dry-run] would write {unit_path.relative_to(base_dir)}:")
            print("    " + "\n    ".join(unit_text.splitlines()))
        else:
            unit_path.write_text(unit_text, encoding="utf-8")
            print(f"  wrote {unit_path.relative_to(base_dir)}")


def main():
    args = sys.argv[1:]
    dry_run = "--dry-run" in args
    args = [a for a in args if a != "--dry-run"]

    base_dir = Path(args[0]).resolve() if args else Path(".").resolve()

    print(f"Base directory: {base_dir}")
    if dry_run:
        print("(dry run -- no files will be changed)")

    print("\nStep 1: prefixing existing qmd partials with underscore...")
    add_underscore_prefix(base_dir, dry_run=dry_run)

    print("\nStep 2: generating unitN.qmd files from weekN.yaml...")
    generate_unit_files(base_dir, dry_run=dry_run)


if __name__ == "__main__":
    main()
