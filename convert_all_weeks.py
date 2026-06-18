#!/usr/bin/env python3
"""
convert_all_weeks.py

This is designed to act on all subfolders it is run in
with names week1, week2, week3, etc..
see below for the true range.

The first argument is mandatory and must point to the folder containing
convert.py. The script then runs convert.py against every .Rmd file in
week1 .. week11, producing:

    weekN/_basename.qmd

via:

    python convert.py weekN/basename.Rmd weekN/_basename.qmd

Usage:
    python3 convert_all_weeks.py convert_dir [--dry-run] [--archive-rmds]

    convert_dir      required directory containing convert.py
    --dry-run        print what would happen without converting or moving files
    --archive-rmds   after successful conversion, move .Rmd files to old-rmds/weekN/

Examples:
    python3 convert_all_weeks.py . --dry-run
    python3 convert_all_weeks.py .
    python3 convert_all_weeks.py ../converter --dry-run --archive-rmds
"""

import subprocess
import sys
import shutil
from pathlib import Path

WEEK_RANGE = range(1, 12)  # week1 .. week11


USAGE = """Usage:
    python3 convert_all_weeks.py convert_dir [--dry-run] [--archive-rmds]

Arguments:
    convert_dir      required directory containing convert.py

Options:
    --dry-run        print what would happen without converting or moving files
    --archive-rmds   after successful conversion, move .Rmd files to old-rmds/weekN/
"""


def main():
    args = sys.argv[1:]

    if "--help" in args or "-h" in args:
        print(USAGE)
        sys.exit(0)

    dry_run = "--dry-run" in args
    archive_rmds = "--archive-rmds" in args

    recognised_flags = {"--dry-run", "--archive-rmds"}
    positional_args = [arg for arg in args if arg not in recognised_flags]

    unknown_flags = [arg for arg in positional_args if arg.startswith("-")]
    if unknown_flags:
        print(f"Error: unknown option(s): {', '.join(unknown_flags)}", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    if len(positional_args) != 1:
        print("Error: you must provide exactly one convert_dir argument.", file=sys.stderr)
        print(USAGE, file=sys.stderr)
        sys.exit(2)

    convert_dir = Path(positional_args[0])
    convert_script = convert_dir / "convert.py"

    if not convert_dir.is_dir():
        print(f"Error: convert_dir is not a directory: {convert_dir}", file=sys.stderr)
        sys.exit(1)

    if not convert_script.is_file():
        print(f"Error: convert.py not found at {convert_script}", file=sys.stderr)
        sys.exit(1)

    archive_root = Path("old-rmds")
    if archive_rmds and not dry_run:
        archive_root.mkdir(exist_ok=True)

    if dry_run:
        print("Dry run: no files will be converted or moved.")

    for n in WEEK_RANGE:
        week_dir = Path(f"week{n}")
        if not week_dir.is_dir():
            continue

        for rmd_file in sorted(week_dir.glob("*.Rmd")):
            output = week_dir / f"_{rmd_file.stem}.qmd"
            command = ["python", str(convert_script), str(rmd_file), str(output)]

            if dry_run:
                print(f"[dry-run] would run: {' '.join(command)}")
            else:
                result = subprocess.run(command)

                if result.returncode != 0:
                    print(
                        f"  ! convert.py exited {result.returncode} on {rmd_file}",
                        file=sys.stderr,
                    )
                    continue

            if archive_rmds:
                archive_week_dir = archive_root / week_dir.name
                archive_target = archive_week_dir / rmd_file.name

                if dry_run:
                    print(f"[dry-run] would move: {rmd_file} -> {archive_target}")
                else:
                    archive_week_dir.mkdir(parents=True, exist_ok=True)
                    shutil.move(
                        str(rmd_file),
                        str(archive_target)
                    )


if __name__ == "__main__":
    main()
