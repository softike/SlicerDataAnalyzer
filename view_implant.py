"""Utility to locate and visualize an implant STL by S3UID."""

from __future__ import annotations

import argparse
import math
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional, Sequence, Tuple

AVAILABLE_MANUFACTURERS = {
    "medacta": "amedacta_complete",
    "mathys": "mathys_optimys_complete",
    "johnson": "johnson_corail_complete",  # alias for the enhanced CORAIL module
    "johnson-corail": "johnson_corail_complete",
    "johnson-actis": "johnson_actis_complete",
}

Vector3 = Tuple[float, float, float]
OverlayFactory = Callable[[Any], Any]


def _format_vector(vec: Vector3) -> str:
    return f"({vec[0]:.2f}, {vec[1]:.2f}, {vec[2]:.2f})"


def _dot(a: Vector3, b: Vector3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _vector_length(vec: Vector3) -> float:
    return math.sqrt(_dot(vec, vec))


def _normalize_vec(vec: Vector3) -> Vector3:
    length = _vector_length(vec)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return (vec[0] / length, vec[1] / length, vec[2] / length)


def _cross(a: Vector3, b: Vector3) -> Vector3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _coerce_vector(vec: Sequence[float]) -> Vector3:
    return (float(vec[0]), float(vec[1]), float(vec[2]))


def _build_neck_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.0)
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.2, 0.2)
        return actor

    return _builder


def _build_cut_plane_actor(origin: Vector3, normal: Vector3, size: float) -> OverlayFactory:
    normal_vec = _normalize_vec(normal)
    extent = max(size, 1.0)

    reference = (0.0, 0.0, 1.0) if abs(normal_vec[2]) < 0.9 else (0.0, 1.0, 0.0)
    tangent = _normalize_vec(_cross(normal_vec, reference))
    if _vector_length(tangent) == 0.0:
        tangent = (1.0, 0.0, 0.0)
    bitangent = _normalize_vec(_cross(normal_vec, tangent))

    half = extent / 2.0
    origin_corner = (
        origin[0] - tangent[0] * half - bitangent[0] * half,
        origin[1] - tangent[1] * half - bitangent[1] * half,
        origin[2] - tangent[2] * half - bitangent[2] * half,
    )
    point1 = (
        origin_corner[0] + tangent[0] * extent,
        origin_corner[1] + tangent[1] * extent,
        origin_corner[2] + tangent[2] * extent,
    )
    point2 = (
        origin_corner[0] + bitangent[0] * extent,
        origin_corner[1] + bitangent[1] * extent,
        origin_corner[2] + bitangent[2] * extent,
    )

    def _builder(vtk: Any):
        plane = vtk.vtkPlaneSource()
        plane.SetOrigin(*origin_corner)
        plane.SetPoint1(*point1)
        plane.SetPoint2(*point2)
        plane.SetXResolution(1)
        plane.SetYResolution(1)
        plane.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(plane.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.1, 0.6, 1.0)
        actor.GetProperty().SetOpacity(0.35)
        return actor

    return _builder


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

    def _token_variants(token: str) -> List[str]:
        base = token.lower()
        variants = {base}
        variants.add(base.replace(" ", "_"))
        variants.add(base.replace(" ", ""))
        alnum_only = "".join(ch for ch in base if ch.isalnum())
        variants.add(alnum_only)
        return [variant for variant in variants if variant]

    normalized_tokens: List[str] = []
    for token in tokens:
        normalized_tokens.extend(_token_variants(token))

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


def show_stl(stl_path: Path, overlays: Optional[Sequence[OverlayFactory]] = None) -> None:
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

    if overlays:
        for factory in overlays:
            if factory is None:
                continue
            overlay_actor = factory(vtk)
            if overlay_actor is not None:
                renderer.AddActor(overlay_actor)

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
    parser.add_argument(
        "--plane-size",
        type=float,
        default=60.0,
        help="Edge length (in mm) for the rendered cut-plane overlay (default: 60).",
    )
    parser.add_argument(
        "--no-overlays",
        action="store_true",
        help="Disable rendering of the neck center and cut-plane helpers.",
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

    neck_origin: Optional[Vector3] = None
    get_neck_fn = getattr(module, "get_neck_origin", None)
    if callable(get_neck_fn):
        try:
            neck_origin = _coerce_vector(get_neck_fn(uid_member))
        except ValueError:
            neck_origin = None

    cut_plane_info: Optional[dict[str, object]] = None
    get_cut_plane_fn = getattr(module, "get_cut_plane", None)
    if callable(get_cut_plane_fn):
        try:
            plane = get_cut_plane_fn(uid_member)
        except ValueError:
            plane = None
        if plane is not None:
            origin = getattr(plane, "origin", None)
            normal = getattr(plane, "normal", None)
            if origin is not None and normal is not None:
                origin_vec = _coerce_vector(origin)
                normal_vec = _normalize_vec(_coerce_vector(normal))
                cut_plane_info = {
                    "origin": origin_vec,
                    "normal": normal_vec,
                    "offset": -_dot(normal_vec, origin_vec),
                }

    tokens = [rcc_id, uid_member.name, str(uid_member.value)]
    stl_path, additional_matches = find_matching_stl(args.folders, tokens)

    print(
        f"Resolved implant:\n"
        f"  Provided UID: {args.uid}\n"
        f"  Manufacturer: {manufacturer_name}\n"
        f"  S3UID: {uid_member.name} ({uid_member.value})\n"
        f"  RCC ID: {rcc_id}\n"
        f"  STL path: {stl_path}\n"
    )
    if neck_origin:
        print(f"  Neck origin (mm): {_format_vector(neck_origin)}")
    if cut_plane_info:
        print(
            f"  Cut plane origin (mm): {_format_vector(cut_plane_info['origin'])}\n"
            f"  Cut plane normal: {_format_vector(cut_plane_info['normal'])}"
            f" (d = {cut_plane_info['offset']:.3f})"
        )
    if args.verbose and additional_matches:
        print("Additional matches:", file=sys.stderr)
        for candidate in additional_matches:
            print(f"  - {candidate}", file=sys.stderr)

    overlay_factories: List[OverlayFactory] = []
    if not args.no_overlays:
        if neck_origin:
            overlay_factories.append(_build_neck_actor(neck_origin))
        if cut_plane_info:
            overlay_factories.append(
                _build_cut_plane_actor(
                    cut_plane_info["origin"],
                    cut_plane_info["normal"],
                    args.plane_size,
                )
            )

    show_stl(stl_path, overlay_factories if overlay_factories else None)


if __name__ == "__main__":  # pragma: no cover
    main()
