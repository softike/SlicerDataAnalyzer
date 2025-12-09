"""Utility to locate and visualize an implant STL by S3UID."""

from __future__ import annotations

import argparse
import sys
from importlib import import_module
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

AVAILABLE_MANUFACTURERS = {
    "mathys": "mathys_implants",
    "johnson": "johnson_implants_corail",  # backward compatibility alias
    "johnson-corail": "johnson_implants_corail",
    "johnson-actis": "johnson_implants_actis",
}


def ensure_vtk():
    """Import vtk lazily so --help can run without the dependency installed."""

    try:
        import vtk  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - environment specific
        raise SystemExit(
            "vtk is required to display STL files. Install it with 'pip install vtk'."
        ) from exc

    return vtk


def _match_rcc_id(module, candidate: str):
    """Return S3UID enum member if candidate matches an RCC ID in the module."""

    mapping = getattr(module, "RCC_ID_NAME", None)
    if not mapping:
        return None

    candidate_normalized = candidate.strip().lower()
    for enum_member, rcc_value in mapping.items():
        if str(rcc_value).strip().lower() == candidate_normalized:
            return enum_member
    return None


def resolve_uid(uid_token: str, manufacturer: str | None):
    """Return the implant module, its label, and the resolved enum member."""

    normalized_name = uid_token.strip()
    numeric_value = None
    if "_" not in normalized_name:
        sanitized_numeric = normalized_name.replace("_", "")
        try:
            numeric_value = int(normalized_name, 0)
        except ValueError:
            try:
                numeric_value = int(sanitized_numeric, 0)
            except ValueError:
                numeric_value = None

    if numeric_value is None:
        lookup_name = normalized_name.upper()
    else:
        lookup_name = normalized_name

    module_candidates: Iterable[Tuple[str, str]]
    if manufacturer:
        if manufacturer not in AVAILABLE_MANUFACTURERS:
            raise SystemExit(
                f"Unknown manufacturer '{manufacturer}'. "
                f"Valid options: {', '.join(sorted(AVAILABLE_MANUFACTURERS))}."
            )
        module_candidates = [(manufacturer, AVAILABLE_MANUFACTURERS[manufacturer])]
    else:
        module_candidates = AVAILABLE_MANUFACTURERS.items()

    for manufacturer_name, module_path in module_candidates:
        module = import_module(module_path)
        enum_cls = getattr(module, "S3UID", None)
        if enum_cls is None:
            continue

        uid_member = None
        if numeric_value is not None:
            try:
                uid_member = enum_cls(numeric_value)
            except ValueError:
                uid_member = None

        if uid_member is None:
            uid_member = getattr(enum_cls, lookup_name, None)

        if uid_member is None and numeric_value is None:
            uid_member = _match_rcc_id(module, normalized_name)

        if uid_member is not None:
            return module, manufacturer_name, uid_member

    if numeric_value is not None:
        missing_desc = f"value {numeric_value}"
    else:
        missing_desc = f"name '{lookup_name}'"

    raise SystemExit(
        f"Could not find S3UID {missing_desc} in available implant modules. "
        f"Try specifying --manufacturer explicitly."
    )


def find_matching_stl(folders: Sequence[str], tokens: Sequence[str]) -> Tuple[Path, List[Path]]:
    """Search provided folders for an STL whose name contains one of the tokens."""

    exact_matches: List[Path] = []
    partial_matches: List[Path] = []
    normalized_tokens = [token.lower() for token in tokens]

    for folder in folders:
        root = Path(folder).expanduser()
        try:
            # Some network shares (e.g., SMB exposed by Linux) do not support
            # Windows' GetFinalPathNameByHandle, so fall back to an absolute path
            # when resolve() raises OSError.
            root = root.resolve(strict=False)
        except OSError:
            root = root.absolute()

        if not root.is_dir():
            raise SystemExit(f"Folder '{folder}' does not exist or is not a directory.")

        for stl_path in root.rglob("*.stl"):
            stem = stl_path.stem.lower()
            if any(stem == token for token in normalized_tokens):
                exact_matches.append(stl_path)
            elif any(token in stem for token in normalized_tokens):
                partial_matches.append(stl_path)

    if exact_matches:
        return exact_matches[0], exact_matches[1:]
    if partial_matches:
        return partial_matches[0], partial_matches[1:]

    raise SystemExit(
        "No STL file matched any of the expected identifiers in the supplied folders."
    )


def show_stl(stl_path: Path) -> None:
    """Render an STL model in an interactive VTK window."""

    vtk = ensure_vtk()

    reader = vtk.vtkSTLReader()
    reader.SetFileName(str(stl_path))
    reader.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(reader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.SetBackground(0.1, 0.1, 0.1)
    renderer.AddActor(actor)

    render_window = vtk.vtkRenderWindow()
    render_window.SetSize(1024, 768)
    render_window.SetWindowName(f"Implant Viewer - {stl_path.name}")
    render_window.AddRenderer(renderer)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)

    renderer.ResetCamera()
    render_window.Render()
    interactor.Initialize()
    interactor.Start()


def build_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser."""

    parser = argparse.ArgumentParser(
        description=(
            "Locate an STL file for a given S3UID by scanning one or more folders, "
            "then visualize it using VTK."
        )
    )
    parser.add_argument(
        "uid",
        help=(
            "S3UID name or numeric value (e.g., STEM_STD_1, STEM_KS_STD135_4, 130506)."
        ),
    )
    parser.add_argument(
        "folders",
        nargs="+",
        help="One or more directories to search for STL files.",
    )
    parser.add_argument(
        "--manufacturer",
        choices=sorted(AVAILABLE_MANUFACTURERS),
        help=(
            "Restrict the search to a specific implant module. If omitted, all known "
            "manufacturers are searched."
        ),
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print additional debugging information while locating files.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)

    module, manufacturer_name, uid_member = resolve_uid(args.uid, args.manufacturer)

    try:
        rcc_id = module.get_rcc_id(uid_member)
    except KeyError as exc:  # pragma: no cover - defensive programming
        raise SystemExit(
            f"The UID '{args.uid}' does not have an RCC mapping in {manufacturer_name}."
        ) from exc

    tokens = [rcc_id, uid_member.name, str(uid_member.value)]
    stl_path, additional_matches = find_matching_stl(args.folders, tokens)

    if args.verbose:
        print(
            f"Resolved implant:\n"
            f"  Manufacturer: {manufacturer_name}\n"
            f"  UID: {uid_member.name} ({uid_member.value})\n"
            f"  RCC ID: {rcc_id}\n"
            f"  STL path: {stl_path}\n",
            file=sys.stderr,
        )
        if additional_matches:
            print("Additional matches:", file=sys.stderr)
            for candidate in additional_matches:
                print(f"  - {candidate}", file=sys.stderr)

    show_stl(stl_path)


if __name__ == "__main__":  # pragma: no cover
    main()
