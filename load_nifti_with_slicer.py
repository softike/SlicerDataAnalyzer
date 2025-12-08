#!/usr/bin/env python3
"""Utility to launch 3D Slicer with a NIfTI volume pre-loaded for visualization."""

import argparse
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import textwrap
from typing import List, Optional


def find_slicer_executable(explicit_path: Optional[str]) -> str:
    """Resolve the Slicer executable path, honoring CLI flag, env var, and PATH."""
    candidates: List[str] = []

    if explicit_path:
        candidates.append(explicit_path)

    env_candidate = os.environ.get("SLICER_EXECUTABLE")
    if env_candidate:
        candidates.append(env_candidate)

    candidates.append("Slicer")

    for candidate in candidates:
        if not candidate:
            continue

        resolved = candidate
        if not os.path.isabs(candidate):
            resolved = shutil.which(candidate) or ""
            if not resolved:
                continue

        if os.path.isdir(resolved):
            potential = os.path.join(resolved, "Slicer")
            if os.path.isfile(potential):
                resolved = potential

        if os.path.isfile(resolved) and os.access(resolved, os.X_OK):
            return os.path.abspath(resolved)

    raise FileNotFoundError(
        "Unable to locate a Slicer executable. Use --slicer-path or set SLICER_EXECUTABLE."
    )


def build_slicer_python_code(nifti_path: str) -> str:
    """Return the Python code string executed inside the Slicer interpreter."""
    escaped_path = nifti_path.replace("\\", "\\\\")
    # Keep the snippet compact so it remains manageable on the cmd line
    return textwrap.dedent(
        f"""
        import os
        import slicer
        from slicer.util import loadVolume, setSliceViewerLayers

        volume_path = r"{escaped_path}"
        if not os.path.exists(volume_path):
            raise FileNotFoundError(volume_path)

        node = loadVolume(volume_path)
        if node is None:
            raise RuntimeError("Failed to load volume: {escaped_path}")

        setSliceViewerLayers(background=node)
        slicer.app.layoutManager().resetSliceViews()
        print(f"Loaded volume: {escaped_path}")
        """
    ).strip()


def write_temp_script(contents: str) -> str:
    """Persist Python snippet to a temporary file and return its path."""
    temp_file = tempfile.NamedTemporaryFile("w", suffix="_load_nifti.py", delete=False)
    temp_file.write(contents)
    temp_file.flush()
    temp_file.close()
    return temp_file.name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Launch 3D Slicer and display a provided NIfTI volume."
    )
    parser.add_argument(
        "nifti",
        nargs="?",
        help="Path to the NIfTI file to visualize (.nii or .nii.gz)",
    )
    parser.add_argument(
        "--nifti",
        dest="nifti_flag",
        help="Explicit path to the NIfTI file (overrides positional argument)",
    )
    parser.add_argument(
        "--slicer-path",
        dest="slicer_path",
        default=None,
        help="Path to the Slicer executable (falls back to $SLICER_EXECUTABLE or PATH lookup)",
    )
    parser.add_argument(
        "--no-splash",
        action="store_true",
        help="Suppress the Slicer splash screen when launching",
    )
    parser.add_argument(
        "--extra-arg",
        dest="extra_args",
        action="append",
        default=[],
        help="Additional argument(s) forwarded to the Slicer launcher (repeatable)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    nifti_source = args.nifti_flag or args.nifti
    if not nifti_source:
        print("Error: provide a NIfTI path via positional argument or --nifti", file=sys.stderr)
        return 1

    nifti_path = os.path.abspath(nifti_source)
    if not os.path.exists(nifti_path):
        print(f"Error: NIfTI file not found at {nifti_path}", file=sys.stderr)
        return 1

    try:
        slicer_exec = find_slicer_executable(args.slicer_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    slicer_code = build_slicer_python_code(nifti_path)
    temp_script = write_temp_script(slicer_code)

    command = [slicer_exec]
    if args.no_splash:
        command.append("--no-splash")
    command.extend(args.extra_args)
    command.extend(["--python-script", temp_script])

    print("Running:", " ".join(shlex.quote(part) for part in command))
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as exc:
        print(f"Slicer exited with code {exc.returncode}", file=sys.stderr)
        return exc.returncode or 1
    finally:
        try:
            os.remove(temp_script)
        except OSError:
            pass

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
