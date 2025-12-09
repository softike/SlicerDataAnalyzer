#!/usr/bin/env python3
"""Batch-drive load_nifti_and_stem.py to generate LUT-colored stem screenshots."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable

from implant_registry import resolve_stem_uid

LOAD_SCRIPT = Path(__file__).with_name("load_nifti_and_stem.py")
VALID_NIFTI_SUFFIXES = (".nii", ".nii.gz")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Locate each seedplan.xml under a planning root, find the matching NIfTI under an image root, "
            "and invoke load_nifti_and_stem.py headlessly to generate scalar screenshots."
        )
    )
    parser.add_argument("--image-root", required=True, help="Root directory that contains per-case NIfTI files")
    parser.add_argument(
        "--planning-root",
        required=True,
        help="Root directory that contains per-case planning folders with seedplan.xml",
    )
    parser.add_argument(
        "--case",
        action="append",
        dest="cases",
        default=[],
        help="Specific case identifier to process (repeatable). If omitted, all seedplans are processed.",
    )
    parser.add_argument(
        "--cases-file",
        help="Optional text file listing case identifiers (one per line); combined with any --case entries.",
    )
    parser.add_argument(
        "--stl-folder",
        action="append",
        dest="stl_folders",
        default=[],
        help="Folder to search for implant STLs (forwarded to load_nifti_and_stem.py).",
    )
    parser.add_argument(
        "--pre-transform-lps-to-ras",
        action="store_true",
        help="Forwarded flag so every invocation applies the LPS→RAS pre-transform.",
    )
    parser.add_argument(
        "--pre-rotate-z-180",
        action="store_true",
        help="Forwarded flag so every invocation pre-rotates the stem 180° around Z.",
    )
    parser.add_argument(
        "--post-rotate-z-180",
        action="store_true",
        help="Forwarded flag so every invocation post-rotates the stem 180° around Z.",
    )
    parser.add_argument(
        "--slicer-extra-arg",
        action="append",
        dest="extra_args",
        nargs=1,
        metavar="ARG",
        default=None,
        help=(
            "Argument forwarded to Slicer via load_nifti_and_stem.py --extra-arg. Defaults to --no-main-window; "
            "repeat to add more flags."
        ),
    )
    parser.add_argument(
        "--exit-after-run",
        action="store_true",
        help="Request each launched Slicer instance to close itself automatically when processing completes.",
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        help="Optional limit on the number of cases to process (useful for smoke tests).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the resolved commands without launching Slicer.",
    )
    return parser.parse_args()


def _read_cases_file(path: str | None) -> list[str]:
    if not path:
        return []
    cases: list[str] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line and not line.startswith("#"):
                cases.append(line)
    return cases


def _collect_seedplans(planning_root: Path, requested_cases: Iterable[str] | None) -> list[tuple[str, Path]]:
    requested = set(case.strip() for case in (requested_cases or []) if case and case.strip())
    seedplans: list[tuple[str, Path]] = []

    if requested:
        for case in sorted(requested):
            matches = list(planning_root.rglob(f"{case}/Mediplan3D/seedplan.xml"))
            if not matches:
                print(f"Warning: seedplan not found for case '{case}' under {planning_root}")
                continue
            if len(matches) > 1:
                print(f"Warning: multiple seedplans found for case '{case}'; using first match")
            seedplans.append((case, matches[0]))
        return seedplans

    for seedplan in planning_root.rglob("seedplan.xml"):
        try:
            case_id = seedplan.parent.parent.name
        except AttributeError:
            continue
        if not case_id:
            continue
        seedplans.append((case_id, seedplan))
    seedplans.sort(key=lambda item: item[0])
    return seedplans


def _find_unique_nifti(image_root: Path, case_id: str) -> Path | None:
    candidates: list[Path] = []
    for suffix in VALID_NIFTI_SUFFIXES:
        pattern = f"**/{case_id}/**/*{suffix}"
        candidates.extend(image_root.glob(pattern))
    if not candidates:
        print(f"Warning: no NIfTI found for case '{case_id}' under {image_root}")
        return None
    # Prefer .nii.gz files, then shorter paths to break ties.
    candidates.sort(key=lambda p: (0 if p.suffix == ".gz" or p.name.endswith(".nii.gz") else 1, len(str(p))))
    # Deduplicate identical files
    unique_candidates = []
    seen = set()
    for cand in candidates:
        resolved = cand.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique_candidates.append(cand)
    if len(unique_candidates) > 1:
        print(
            f"Warning: multiple NIfTI files found for case '{case_id}'. Using '{unique_candidates[0]}', "
            "skipping the rest."
        )
    return unique_candidates[0]


def _detect_rotation_mode(seedplan_path: Path, case_id: str | None = None) -> str:
    label = f"case '{case_id}'" if case_id else str(seedplan_path)
    try:
        tree = ET.parse(seedplan_path)
        root = tree.getroot()
    except Exception as exc:
        print(f"Warning: unable to parse seedplan for {label}: {exc}")
        return "auto"

    hip_configs = root.findall(".//hipImplantConfig")
    history_configs = root.findall(".//hipImplantConfigHistoryList/hipImplantConfig")
    for configs in (hip_configs, history_configs):
        for hip_config in configs:
            fem_config = hip_config.find("./femImplantConfig")
            if fem_config is None:
                continue
            stem_shape = fem_config.find(".//s3Shape[@part='stem']")
            if stem_shape is None:
                continue
            uid_attr = stem_shape.attrib.get("uid")
            if not uid_attr:
                continue
            try:
                uid_val = int(uid_attr)
            except (TypeError, ValueError):
                continue
            lookup = resolve_stem_uid(uid_val)
            if lookup is None:
                continue
            tokens = [
                (lookup.manufacturer or "").lower(),
                (lookup.enum_name or "").lower(),
                (lookup.friendly_name or "").lower(),
            ]
            if any("mathys" in token for token in tokens if token):
                return "mathys"
            if any(
                token
                and ("corail" in token or "actis" in token or "johnson" in token)
                for token in tokens
            ):
                return "johnson"
    return "auto"


def _build_command(
    nifti_path: Path,
    seedplan_path: Path,
    args: argparse.Namespace,
    auto_pre_rotate: bool = False,
    auto_post_rotate: bool = False,
) -> list[str]:
    command: list[str] = [sys.executable, str(LOAD_SCRIPT)]
    command.extend(["--nifti", str(nifti_path)])
    command.extend(["--seedplan", str(seedplan_path)])
    for folder in args.stl_folders:
        command.extend(["--stl-folder", folder])
    if args.pre_transform_lps_to_ras:
        command.append("--pre-transform-lps-to-ras")
    if args.pre_rotate_z_180 or auto_pre_rotate:
        command.append("--pre-rotate-z-180")
    if args.post_rotate_z_180 or auto_post_rotate:
        command.append("--post-rotate-z-180")
    command.append("--no-splash")
    command.append("--compute-stem-scalars")
    command.append("--export-stem-screenshots")
    if args.exit_after_run:
        command.append("--exit-after-run")
    extras_raw = args.extra_args if args.extra_args else [["--no-main-window"]]
    extras: list[str] = []
    for chunk in extras_raw:
        if isinstance(chunk, (list, tuple)):
            extras.extend(str(item) for item in chunk if item)
        elif chunk:
            extras.append(str(chunk))
    for extra in extras:
        if not extra:
            continue
        command.append(f"--extra-arg={extra}")
    return command


def main() -> int:
    args = parse_args()
    image_root = Path(args.image_root).resolve()
    planning_root = Path(args.planning_root).resolve()
    if not image_root.is_dir():
        print(f"Error: image root '{image_root}' not found", file=sys.stderr)
        return 1
    if not planning_root.is_dir():
        print(f"Error: planning root '{planning_root}' not found", file=sys.stderr)
        return 1
    if not LOAD_SCRIPT.is_file():
        print(f"Error: missing loader script at {LOAD_SCRIPT}", file=sys.stderr)
        return 1

    requested_cases = args.cases or []
    requested_cases.extend(_read_cases_file(args.cases_file))
    seedplan_entries = _collect_seedplans(planning_root, requested_cases)
    if args.max_cases is not None:
        seedplan_entries = seedplan_entries[: args.max_cases]

    if not seedplan_entries:
        print("No seedplans found to process.")
        return 0

    processed = 0
    failures = 0

    for case_id, seedplan_path in seedplan_entries:
        nifti_path = _find_unique_nifti(image_root, case_id)
        if not nifti_path:
            failures += 1
            continue
        rotation_mode = _detect_rotation_mode(seedplan_path, case_id)
        auto_pre = rotation_mode == "johnson"
        auto_post = rotation_mode in ("johnson", "mathys")
        if rotation_mode != "auto":
            forced = []
            if auto_pre:
                forced.append("pre-rotate Z 180°")
            if auto_post:
                forced.append("post-rotate Z 180°")
            forced_str = " and ".join(forced) if forced else "no extra rotations"
            print(
                f"Detected {rotation_mode.capitalize()} stem for case '{case_id}'; applying {forced_str} automatically"
            )
        command = _build_command(nifti_path, seedplan_path, args, auto_pre_rotate=auto_pre, auto_post_rotate=auto_post)
        print("\nCase %s" % case_id)
        print("Seedplan:", seedplan_path)
        print("NIfTI:   ", nifti_path)
        print("Command: ", " ".join(map(str, command)))
        if args.dry_run:
            processed += 1
            continue
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as exc:
            failures += 1
            print(f"Warning: command failed with exit code {exc.returncode} for case '{case_id}'")
        else:
            processed += 1

    print(f"\nCompleted {processed} case(s); {failures} failure(s).")
    return 0 if failures == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
