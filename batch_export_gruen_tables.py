#!/usr/bin/env python3
"""Batch-export partitioned Gruen HU tables using view_vtp.py in headless mode."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

VIEW_VTP = Path(__file__).with_name("view_vtp.py")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan for stem_local.vtp files and invoke view_vtp.py to export partitioned Gruen HU XML tables."
        )
    )
    parser.add_argument(
        "--root",
        required=True,
        help="Root directory to scan for *_stem_local.vtp files.",
    )
    parser.add_argument(
        "--pattern",
        default="**/*_stem_local.vtp",
        help="Glob pattern relative to --root (default: %(default)s).",
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Enable recursive search (default uses --pattern as provided).",
    )
    parser.add_argument(
        "--side",
        choices=("auto", "left", "right"),
        default="auto",
        help="Override side (forwarded to view_vtp.py).",
    )
    parser.add_argument(
        "--config-index",
        type=int,
        help="Optional config index (forwarded to view_vtp.py) when seedplan is shared.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print commands without executing.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print progress information while processing.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"Error: root directory '{root}' does not exist", file=sys.stderr)
        return 1
    if not VIEW_VTP.is_file():
        print(f"Error: view_vtp.py not found at {VIEW_VTP}", file=sys.stderr)
        return 1

    if args.recursive and "**" not in args.pattern:
        pattern = args.pattern
        vtp_iter = root.rglob(pattern)
    else:
        pattern = args.pattern
        vtp_iter = root.glob(pattern)
    vtp_files = sorted(path for path in vtp_iter if path.is_file())
    if not vtp_files:
        print(f"No VTP files found under {root} with pattern '{pattern}'.")
        return 0

    if args.verbose:
        print(f"Found {len(vtp_files)} VTP file(s) under {root}")

    failures = 0
    for vtp_path in vtp_files:
        command = [
            sys.executable,
            str(VIEW_VTP),
            str(vtp_path),
            "--local-frame",
            "--gruen-zones",
            "--partitioned-gruen",
            "--export-hu-xml",
            "--headless",
            "--side",
            args.side,
        ]
        if args.config_index is not None:
            command.extend(["--config-index", str(args.config_index)])
        if args.verbose:
            print(f"Processing {vtp_path}")
        print("Command:", " ".join(command))
        if args.dry_run:
            continue
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            failures += 1
            print(f"Warning: command failed ({exc.returncode}) for {vtp_path}", file=sys.stderr)

    if failures:
        print(f"Completed with {failures} failure(s).", file=sys.stderr)
        return 2
    print("Completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
