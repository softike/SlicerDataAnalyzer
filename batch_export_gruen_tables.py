#!/usr/bin/env python3
"""Batch-export Gruen HU tables using view_vtp.py in headless mode."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

VIEW_VTP = Path(__file__).with_name("view_vtp.py")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Scan for stem_local.vtp files and invoke view_vtp.py to export Gruen HU XML tables."
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
        "--gruen-hu",
        action="store_true",
        help="Export per-Gruen-zone HU summary XML (default exports partitioned zones).",
    )
    parser.add_argument(
        "--envelope-gruen",
        action="store_true",
        help="Use envelope-based Gruen zones for export (requires --stem-mc).",
    )
    parser.add_argument(
        "--envelope-gruen-mode",
        choices=("position", "normal"),
        default="position",
        help="Envelope side assignment mode (default: position).",
    )
    parser.add_argument(
        "--envelope-z-bands",
        default="0.4,0.4,0.2",
        help="Envelope Z band fractions (default: 0.4,0.4,0.2).",
    )
    parser.add_argument(
        "--gruen-remapped",
        action="store_true",
        help="Use remapped Gruen zone IDs.",
    )
    parser.add_argument(
        "--gruen-hu-remesh",
        action="store_true",
        help="Use remeshed surface (with interpolated scalars) for Gruen HU stats.",
    )
    parser.add_argument(
        "--use-input-remesh",
        action="store_true",
        help="Treat the input mesh as already remeshed for Gruen/envelope stats.",
    )
    parser.add_argument(
        "--gruen-bottom-sphere-radius",
        type=float,
        default=0.0,
        help="Bottom-point sphere radius for Gruen zones 4/11 HU stats (mm).",
    )
    parser.add_argument(
        "--stem-mc",
        action="store_true",
        help="Enable implicit remeshing (required for envelope zones).",
    )
    parser.add_argument(
        "--stem-mc-spacing",
        type=float,
        default=0.5,
        help="Implicit remesh spacing in mm (default: 0.5).",
    )
    parser.add_argument(
        "--cache-remesh",
        action="store_true",
        help="Cache remeshed surfaces for reuse.",
    )
    parser.add_argument(
        "--cache-remesh-refresh",
        action="store_true",
        help="Force recompute remesh caches even if cache files exist.",
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

    if args.envelope_gruen and not args.stem_mc and not args.use_input_remesh:
        print("Error: --envelope-gruen requires --stem-mc or --use-input-remesh", file=sys.stderr)
        return 1

    failures = 0
    for vtp_path in vtp_files:
        command = [
            sys.executable,
            str(VIEW_VTP),
            str(vtp_path),
            "--local-frame",
            "--headless",
            "--side",
            args.side,
        ]
        if args.stem_mc:
            command.extend(["--stem-mc", "--stem-mc-spacing", str(args.stem_mc_spacing)])
            if args.cache_remesh:
                command.append("--cache-remesh")
            if args.cache_remesh_refresh:
                command.append("--cache-remesh-refresh")
        if args.envelope_gruen:
            command.extend([
                "--show-envelope-gruen",
                "--envelope-gruen-mode",
                args.envelope_gruen_mode,
                "--envelope-z-bands",
                args.envelope_z_bands,
            ])
            if args.use_input_remesh:
                command.append("--envelope-gruen-input")
        if args.gruen_remapped:
            command.append("--gruen-remapped")
        if args.gruen_hu or args.gruen_remapped or args.envelope_gruen:
            command.append("--export-gruen-hu-xml")
            if not args.envelope_gruen:
                command.append("--gruen-zones")
            if args.gruen_hu_remesh:
                command.append("--gruen-hu-remesh")
            if args.use_input_remesh:
                command.append("--gruen-hu-remesh-input")
            if args.gruen_bottom_sphere_radius > 0:
                command.extend(["--gruen-bottom-sphere-radius", str(args.gruen_bottom_sphere_radius)])
        else:
            command.extend(["--gruen-zones", "--partitioned-gruen", "--export-hu-xml"])
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
