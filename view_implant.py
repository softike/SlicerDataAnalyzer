"""Utility to locate and visualize an implant STL by S3UID."""

from __future__ import annotations

import argparse
import math
import sys
from importlib import import_module
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple, cast

AVAILABLE_MANUFACTURERS = {
    "medacta": "amedacta_complete",
    "mathys": "mathys_optimys_complete",
    "johnson": "johnson_corail_complete",  # alias for the enhanced CORAIL module
    "johnson-corail": "johnson_corail_complete",
    "johnson-actis": "johnson_actis_complete",
}

Vector3 = Tuple[float, float, float]
OverlayFactory = Callable[[Any], Any]
Color3 = Tuple[float, float, float]
Matrix3 = Tuple[Tuple[float, float, float], Tuple[float, float, float], Tuple[float, float, float]]

OFFSET_COLORS: Tuple[Color3, ...] = (
    (1.0, 0.85, 0.1),
    (0.9, 0.5, 1.0),
    (0.3, 0.95, 0.95),
    (1.0, 0.45, 0.45),
    (0.55, 1.0, 0.45),
)

UP_VECTOR: Vector3 = (0.0, 0.0, 1.0)
IDENTITY_MATRIX3: Matrix3 = (
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)
MATHYS_ALIGNMENT_MATRIX: Matrix3 = (
    (-1.0, 0.0, 0.0),
    (0.0, 0.0, -1.0),
    (0.0, -1.0, 0.0),
)
MEDACTA_ALIGNMENT_MATRIX: Matrix3 = (
    (0.0, -1.0, 0.0),
    (1.0, 0.0, 0.0),
    (0.0, 0.0, 1.0),
)
JOHNSON_ACTIS_ALIGNMENT_MATRIX: Matrix3 = (
    (-1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),
)
JOHNSON_CORAIL_ALIGNMENT_MATRIX: Matrix3 = (
    (-1.0, 0.0, 0.0),
    (0.0, -1.0, 0.0),
    (0.0, 0.0, 1.0),
)
ALIGNMENT_MATRICES: Dict[str, Matrix3] = {
    "mathys": MATHYS_ALIGNMENT_MATRIX,
    "medacta": MEDACTA_ALIGNMENT_MATRIX,
    "johnson-corail": JOHNSON_CORAIL_ALIGNMENT_MATRIX,
}
ALIGNMENT_DESCRIPTIONS: Dict[str, str] = {
    "mathys": "X=-X, Y=-Z, Z=-Y",
    "medacta": "X=-Y, Y=+X, Z=Z",
    "johnson-corail": "X=-X, Y=-Y, Z=Z",
}

ROTATION_BEHAVIOR = {
    "johnson": (True, True),
    "mathys": (True, False),
    "medacta": (True, False),
}


def _infer_rotation_mode(
    manufacturer_name: str | None,
    module: Any,
    override: str | None,
) -> str:
    override_normalized = (override or "").strip().lower()
    if override_normalized and override_normalized != "auto":
        return override_normalized

    markers = [manufacturer_name or "", getattr(module, "__name__", "")]
    lower_markers = [marker.lower() for marker in markers if marker]

    def _matches(tokens: Sequence[str]) -> bool:
        for marker in lower_markers:
            if any(token in marker for token in tokens):
                return True
        return False

    if _matches(("mathys",)):
        return "mathys"
    if _matches(("medacta", "amedacta", "amistem")):
        return "medacta"
    if _matches(("johnson", "corail", "actis")):
        return "johnson"
    return "none"


def _resolve_alignment_key(
    rotation_mode: str,
    manufacturer_name: str | None,
    module: Any,
) -> Optional[str]:
    markers = [manufacturer_name or "", getattr(module, "__name__", "")]
    lower_markers = [marker.lower() for marker in markers if marker]

    def _contains(token: str) -> bool:
        return any(token in marker for marker in lower_markers)

    if rotation_mode in ("mathys", "medacta"):
        return rotation_mode
    if rotation_mode == "johnson" and _contains("corail"):
        return "johnson-corail"
    return None


def _apply_half_turn(vec: Vector3, half_turns: int) -> Vector3:
    if half_turns % 2 == 0:
        return vec
    return (-vec[0], -vec[1], vec[2])


def _apply_half_turn_optional(vec: Optional[Vector3], half_turns: int) -> Optional[Vector3]:
    if vec is None:
        return None
    return _apply_half_turn(vec, half_turns)


def _rotate_polydata_half_turns(polydata: Any, half_turns: int, vtk_module: Any):
    if polydata is None or half_turns % 2 == 0:
        return polydata
    transform = vtk_module.vtkTransform()
    transform.Identity()
    transform.RotateZ(180.0)
    transformer = vtk_module.vtkTransformPolyDataFilter()
    transformer.SetTransform(transform)
    transformer.SetInputData(polydata)
    transformer.Update()
    return transformer.GetOutput()


def _apply_alignment_polydata(polydata: Any, matrix_values: Optional[Matrix3], vtk_module: Any):
    if polydata is None or matrix_values is None:
        return polydata
    matrix = vtk_module.vtkMatrix4x4()
    matrix.Zero()
    for row in range(3):
        for col in range(3):
            matrix.SetElement(row, col, matrix_values[row][col])
    matrix.SetElement(3, 3, 1.0)
    transform = vtk_module.vtkTransform()
    transform.SetMatrix(matrix)
    transformer = vtk_module.vtkTransformPolyDataFilter()
    transformer.SetTransform(transform)
    transformer.SetInputData(polydata)
    transformer.Update()
    return transformer.GetOutput()


def _vec_add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_scale(a: Vector3, factor: float) -> Vector3:
    return (a[0] * factor, a[1] * factor, a[2] * factor)


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


def _apply_alignment(vec: Vector3, matrix: Matrix3) -> Vector3:
    return _matrix_vec_mul(matrix, vec)


def _apply_alignment_optional(vec: Optional[Vector3], matrix: Matrix3) -> Optional[Vector3]:
    if vec is None:
        return None
    return _apply_alignment(vec, matrix)


def _dedupe_points(points: Sequence[Vector3], tolerance: float = 1e-3) -> List[Vector3]:
    unique: List[Vector3] = []
    for point in points:
        if all(_vector_length(_vec_sub(point, existing)) > tolerance for existing in unique):
            unique.append(point)
    return unique


def _closest_points_between_lines(
    p1: Vector3, d1: Vector3, p2: Vector3, d2: Vector3
) -> Optional[Tuple[Vector3, Vector3]]:
    d1_norm = _normalize_vec(d1)
    d2_norm = _normalize_vec(d2)
    r = _vec_sub(p1, p2)
    a = _dot(d1_norm, d1_norm)
    e = _dot(d2_norm, d2_norm)
    b = _dot(d1_norm, d2_norm)
    c = _dot(d1_norm, r)
    f = _dot(d2_norm, r)
    denom = a * e - b * b
    if abs(denom) < 1e-6:
        return None
    s = (b * f - c * e) / denom
    t = (a * f - b * c) / denom
    closest1 = _vec_add(p1, _vec_scale(d1_norm, s))
    closest2 = _vec_add(p2, _vec_scale(d2_norm, t))
    return closest1, closest2


def _coerce_vector(vec: Sequence[float]) -> Vector3:
    return (float(vec[0]), float(vec[1]), float(vec[2]))


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


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


def _build_head_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.5)
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 1.0, 0.2)
        return actor

    return _builder


def _build_reference_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.5)
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.2, 0.6, 1.0)
        return actor

    return _builder


def _build_offset_actor(point: Vector3, color: Color3 = (1.0, 0.85, 0.1)) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.5)
        sphere.SetThetaResolution(24)
        sphere.SetPhiResolution(24)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        return actor

    return _builder


def _build_junction_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(3.0)
        sphere.SetThetaResolution(32)
        sphere.SetPhiResolution(32)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.3, 0.9)
        return actor

    return _builder


def _build_tip_point_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.5)
        sphere.SetThetaResolution(32)
        sphere.SetPhiResolution(32)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.6, 0.1)
        return actor

    return _builder


def _build_bottom_point_actor(point: Vector3) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.5)
        sphere.SetThetaResolution(32)
        sphere.SetPhiResolution(32)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.3, 0.85, 1.0)
        return actor

    return _builder


def _build_axes_actor(length: float = 60.0) -> OverlayFactory:
    def _builder(vtk: Any):
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(length, length, length)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.02)
        axes.SetConeRadius(0.1)
        axes.SetSphereRadius(0.15)
        return axes

    return _builder


def _build_axes_frame_actor(
    matrix: Matrix3,
    length: float = 60.0,
    axis_colors: Optional[Tuple[Color3, Color3, Color3]] = None,
    opacity: float = 1.0,
) -> OverlayFactory:
    def _builder(vtk: Any):
        axes = vtk.vtkAxesActor()
        axes.SetTotalLength(length, length, length)
        axes.SetShaftTypeToCylinder()
        axes.SetCylinderRadius(0.015)
        axes.SetConeRadius(0.08)
        axes.SetSphereRadius(0.12)

        vtk_matrix = vtk.vtkMatrix4x4()
        vtk_matrix.Identity()
        for row in range(3):
            for col in range(3):
                vtk_matrix.SetElement(row, col, matrix[row][col])
        transform = vtk.vtkTransform()
        transform.SetMatrix(vtk_matrix)
        axes.SetUserTransform(transform)

        if axis_colors:
            axes.GetXAxisShaftProperty().SetColor(*axis_colors[0])
            axes.GetXAxisTipProperty().SetColor(*axis_colors[0])
            axes.GetYAxisShaftProperty().SetColor(*axis_colors[1])
            axes.GetYAxisTipProperty().SetColor(*axis_colors[1])
            axes.GetZAxisShaftProperty().SetColor(*axis_colors[2])
            axes.GetZAxisTipProperty().SetColor(*axis_colors[2])

        for prop in (
            axes.GetXAxisShaftProperty(),
            axes.GetXAxisTipProperty(),
            axes.GetYAxisShaftProperty(),
            axes.GetYAxisTipProperty(),
            axes.GetZAxisShaftProperty(),
            axes.GetZAxisTipProperty(),
        ):
            prop.SetOpacity(opacity)

        return axes

    return _builder


def _build_cut_intersection_actor(point: Vector3, color: Color3 = (0.95, 0.95, 0.2)) -> OverlayFactory:
    def _builder(vtk: Any):
        sphere = vtk.vtkSphereSource()
        sphere.SetCenter(*point)
        sphere.SetRadius(2.2)
        sphere.SetThetaResolution(32)
        sphere.SetPhiResolution(32)
        sphere.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(sphere.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(*color)
        return actor

    return _builder


def _build_cut_contour_actor(cut_polydata: Any) -> OverlayFactory:
    def _builder(vtk: Any):
        stripper = vtk.vtkStripper()
        stripper.SetInputData(cut_polydata)
        stripper.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(stripper.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(1.0, 0.9, 0.4)
        actor.GetProperty().SetLineWidth(3.0)
        return actor

    return _builder


def _intersect_polyline_with_plane(
    polydata: Any,
    plane_normal: Vector3,
    plane_offset: float,
    vtk_module: Any,
    on_plane_tolerance: float = 1e-4,
) -> List[Vector3]:
    points = polydata.GetPoints()
    lines = polydata.GetLines()
    if points is None or lines is None:
        return []

    intersections: List[Vector3] = []
    id_list = vtk_module.vtkIdList()
    lines.InitTraversal()

    def _record_segment(
        start_vec: Vector3,
        start_dist: float,
        end_vec: Vector3,
        end_dist: float,
    ) -> None:
        if abs(start_dist) <= on_plane_tolerance:
            intersections.append(start_vec)
        if abs(end_dist) <= on_plane_tolerance:
            intersections.append(end_vec)

        if start_dist * end_dist < 0.0:
            denom = start_dist - end_dist
            if abs(denom) > 1e-9:
                t = start_dist / denom
                intersection = (
                    start_vec[0] + t * (end_vec[0] - start_vec[0]),
                    start_vec[1] + t * (end_vec[1] - start_vec[1]),
                    start_vec[2] + t * (end_vec[2] - start_vec[2]),
                )
                intersections.append(intersection)

    while lines.GetNextCell(id_list):
        count = id_list.GetNumberOfIds()
        if count < 2:
            continue
        first_id = id_list.GetId(0)
        first_point = points.GetPoint(first_id)
        first_vec: Vector3 = (
            float(first_point[0]),
            float(first_point[1]),
            float(first_point[2]),
        )
        first_dist = _dot(plane_normal, first_vec) + plane_offset

        prev_vec = first_vec
        prev_dist = first_dist

        for idx in range(1, count):
            curr_id = id_list.GetId(idx)
            curr_point = points.GetPoint(curr_id)
            curr_vec: Vector3 = (
                float(curr_point[0]),
                float(curr_point[1]),
                float(curr_point[2]),
            )
            curr_dist = _dot(plane_normal, curr_vec) + plane_offset
            _record_segment(prev_vec, prev_dist, curr_vec, curr_dist)
            prev_vec = curr_vec
            prev_dist = curr_dist

        if count > 2 and _vector_length(_vec_sub(prev_vec, first_vec)) > on_plane_tolerance:
            _record_segment(prev_vec, prev_dist, first_vec, first_dist)

    return _dedupe_points(intersections)


def _build_cut_plane_actor(
    origin: Vector3,
    normal: Vector3,
    size: float,
    color: Color3 = (0.1, 0.6, 1.0),
    opacity: float = 0.35,
) -> OverlayFactory:
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
        actor.GetProperty().SetColor(*color)
        actor.GetProperty().SetOpacity(opacity)
        return actor

    return _builder


def _build_shaft_axis_actor(origin: Vector3, direction: Vector3, length: float = 120.0) -> OverlayFactory:
    axis_dir = _normalize_vec(direction)
    half = length / 2.0
    start = (
        origin[0] - axis_dir[0] * half,
        origin[1] - axis_dir[1] * half,
        origin[2] - axis_dir[2] * half,
    )
    end = (
        origin[0] + axis_dir[0] * half,
        origin[1] + axis_dir[1] * half,
        origin[2] + axis_dir[2] * half,
    )

    def _builder(vtk: Any):
        points = vtk.vtkPoints()
        points.InsertNextPoint(*start)
        points.InsertNextPoint(*end)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 1)

        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.95, 0.95, 0.2)
        actor.GetProperty().SetLineWidth(3.0)
        return actor

    return _builder


def _build_vertical_axis_actor(point: Vector3, direction: Vector3, length: float = 100.0) -> OverlayFactory:
    axis_dir = _normalize_vec(direction)
    end = (
        point[0] + axis_dir[0] * length,
        point[1] + axis_dir[1] * length,
        point[2] + axis_dir[2] * length,
    )

    def _builder(vtk: Any):
        points = vtk.vtkPoints()
        points.InsertNextPoint(*point)
        points.InsertNextPoint(*end)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, 0)
        line.GetPointIds().SetId(1, 1)

        cells = vtk.vtkCellArray()
        cells.InsertNextCell(line)

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)
        polydata.SetLines(cells)

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0.95, 0.95, 0.95)
        actor.GetProperty().SetLineWidth(2.0)
        return actor

    return _builder


def _matrix_vec_mul(matrix: Tuple[Tuple[float, float, float], ...], vec: Vector3) -> Vector3:
    return (
        matrix[0][0] * vec[0] + matrix[0][1] * vec[1] + matrix[0][2] * vec[2],
        matrix[1][0] * vec[0] + matrix[1][1] * vec[1] + matrix[1][2] * vec[2],
        matrix[2][0] * vec[0] + matrix[2][1] * vec[1] + matrix[2][2] * vec[2],
    )


def _matrix_multiply(a: Matrix3, b: Matrix3) -> Matrix3:
    def dot(row: Tuple[float, float, float], column: Tuple[float, float, float]) -> float:
        return row[0] * column[0] + row[1] * column[1] + row[2] * column[2]

    columns = (
        (b[0][0], b[1][0], b[2][0]),
        (b[0][1], b[1][1], b[2][1]),
        (b[0][2], b[1][2], b[2][2]),
    )

    return (
        (dot(a[0], columns[0]), dot(a[0], columns[1]), dot(a[0], columns[2])),
        (dot(a[1], columns[0]), dot(a[1], columns[1]), dot(a[1], columns[2])),
        (dot(a[2], columns[0]), dot(a[2], columns[1]), dot(a[2], columns[2])),
    )


def _half_turn_matrix(half_turns: int) -> Matrix3:
    if half_turns % 2 == 0:
        return IDENTITY_MATRIX3
    return (
        (-1.0, 0.0, 0.0),
        (0.0, -1.0, 0.0),
        (0.0, 0.0, 1.0),
    )


def _dominant_eigenvector(
    matrix: Tuple[Tuple[float, float, float], ...],
    iterations: int = 24,
) -> Optional[Vector3]:
    vec: Vector3 = _normalize_vec((1.0, 1.0, 1.0))
    for _ in range(max(1, iterations)):
        vec = _matrix_vec_mul(matrix, vec)
        length = _vector_length(vec)
        if length < 1e-9:
            return None
        vec = (vec[0] / length, vec[1] / length, vec[2] / length)
    return vec


def _compute_polydata_principal_axis(polydata: Any) -> Optional[Tuple[Vector3, Vector3]]:
    points = polydata.GetPoints()
    if points is None:
        return None
    count = points.GetNumberOfPoints()
    if count == 0:
        return None

    sum_x = sum_y = sum_z = 0.0
    for idx in range(count):
        x, y, z = points.GetPoint(idx)
        sum_x += x
        sum_y += y
        sum_z += z
    mean = (sum_x / count, sum_y / count, sum_z / count)

    c_xx = c_xy = c_xz = c_yy = c_yz = c_zz = 0.0
    for idx in range(count):
        x, y, z = points.GetPoint(idx)
        dx = x - mean[0]
        dy = y - mean[1]
        dz = z - mean[2]
        c_xx += dx * dx
        c_xy += dx * dy
        c_xz += dx * dz
        c_yy += dy * dy
        c_yz += dy * dz
        c_zz += dz * dz

    if count > 1:
        inv = 1.0 / (count - 1)
        c_xx *= inv
        c_xy *= inv
        c_xz *= inv
        c_yy *= inv
        c_yz *= inv
        c_zz *= inv

    cov = (
        (c_xx, c_xy, c_xz),
        (c_xy, c_yy, c_yz),
        (c_xz, c_yz, c_zz),
    )

    axis = _dominant_eigenvector(cov)
    if axis is None:
        return None
    return _normalize_vec(axis), mean


def _find_extreme_point_along_axis(
    polydata: Any,
    axis_dir: Vector3,
    minimize: bool = True,
) -> Optional[Vector3]:
    points = polydata.GetPoints()
    if points is None:
        return None
    count = points.GetNumberOfPoints()
    if count == 0:
        return None
    axis = _normalize_vec(axis_dir)
    best_point = points.GetPoint(0)
    best_proj = _dot(best_point, axis)
    for idx in range(1, count):
        candidate = points.GetPoint(idx)
        proj = _dot(candidate, axis)
        if (minimize and proj < best_proj) or (not minimize and proj > best_proj):
            best_point = candidate
            best_proj = proj
    return (float(best_point[0]), float(best_point[1]), float(best_point[2]))


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


def _apply_default_view_orientation(renderer: Any, actor: Any):
    camera = renderer.GetActiveCamera()
    if camera is None:
        return

    renderer.ResetCamera()
    bounds = actor.GetBounds()
    if not bounds:
        return

    center = (
        (bounds[0] + bounds[1]) * 0.5,
        (bounds[2] + bounds[3]) * 0.5,
        (bounds[4] + bounds[5]) * 0.5,
    )
    distance = camera.GetDistance()
    if not math.isfinite(distance) or distance <= 0.0:
        span_x = bounds[1] - bounds[0]
        span_y = bounds[3] - bounds[2]
        span_z = bounds[5] - bounds[4]
        diagonal = math.sqrt(max(span_x * span_x + span_y * span_y + span_z * span_z, 1.0))
        distance = diagonal * 1.5

    camera.SetFocalPoint(*center)
    camera.SetPosition(center[0], center[1] - distance, center[2])
    camera.SetViewUp(0.0, 0.0, 1.0)
    renderer.ResetCameraClippingRange()


def show_stl(
    stl_path: Path,
    overlays: Optional[Sequence[OverlayFactory]] = None,
    stem_opacity: float = 1.0,
    polydata: Any | None = None,
    vtk_module: Any | None = None,
) -> None:
    """Render an STL model in an interactive VTK window."""

    vtk = vtk_module or ensure_vtk()

    if polydata is None:
        reader = vtk.vtkSTLReader()
        reader.SetFileName(str(stl_path))
        reader.Update()
        polydata = reader.GetOutput()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetOpacity(max(0.0, min(1.0, stem_opacity)))

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

    _apply_default_view_orientation(renderer, actor)
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
    parser.add_argument(
        "--stem-opacity",
        type=float,
        default=1.0,
        help="Opacity for the STL surface (0.0 = fully transparent, 1.0 = solid).",
    )
    parser.add_argument(
        "--show-head",
        action="store_true",
        help="Render the head point if the implant module exposes get_head_point().",
    )
    parser.add_argument(
        "--show-offset",
        action="store_true",
        help="Render the default head-to-stem offset using head_to_stem_offset().",
    )
    parser.add_argument(
        "--offset-head",
        default="AUTO",
        help=(
            "Head enum name to use when computing the offset point (default: AUTO,"
            " which prefers HEAD_P0, else the first entry in HEAD_UIDS)."
        ),
    )
    parser.add_argument(
        "--show-all-offsets",
        action="store_true",
        help="Render every head-to-stem offset defined in HEAD_UIDS (if available).",
    )
    parser.add_argument(
        "--show-shaft-axis",
        action="store_true",
        help="Display the shaft axis using get_shaft_angle() relative to the neck origin.",
    )
    parser.add_argument(
        "--show-tip-point",
        action="store_true",
        help="Highlight the stem tip point derived from the STL principal axis analysis.",
    )
    parser.add_argument(
        "--show-bottom-point",
        action="store_true",
        help="Highlight the stem bottom point derived from the STL principal axis analysis.",
    )
    parser.add_argument(
        "--show-cut-plane-intersection",
        action="store_true",
        help="Mark the upper and lower intersection points between the rotated cut plane and the STL surface (aligned to the head/neck/tip plane when possible).",
    )
    parser.add_argument(
        "--show-cut-plane-contour",
        action="store_true",
        help="Render the intersection contour (cut line) between the rotated cut plane and the STL.",
    )
    parser.add_argument(
        "--show-anatomical-plane",
        action="store_true",
        help="Display the plane defined by the STL-derived tip, the head point, and the neck origin.",
    )
    parser.add_argument(
        "--show-axes-reference",
        action="store_true",
        help="Add a global XYZ axes indicator to visualize the coordinate orientation (Z = up).",
    )
    parser.add_argument(
        "--show-axis-frames",
        action="store_true",
        help="Render the implant's initial frame after auto-rotation but before any brand-specific alignment remaps.",
    )
    parser.add_argument(
        "--show-axis-junction",
        action="store_true",
        help="Compute the closest junction between the neck axis and the stem axis (bottom→junction).",
    )
    parser.add_argument(
        "--show-neck-axis",
        action="store_true",
        help="Render the anatomical neck axis derived from head and neck points.",
    )
    parser.add_argument(
        "--rotation-mode",
        choices=("auto", "mathys", "medacta", "johnson", "none"),
        default="auto",
        help=(
            "Apply the same manufacturer-specific Z-axis flips used by the batch scripts (default: auto detects "
            "Mathys/Medacta/Johnson based on the resolved module)."
        ),
    )
    parser.add_argument(
        "--pre-rotate-z-180",
        action="store_true",
        help="Force a 180° rotation around the Z axis before the auto-rotation behavior.",
    )
    parser.add_argument(
        "--post-rotate-z-180",
        action="store_true",
        help="Force a 180° rotation around the Z axis after the auto-rotation behavior.",
    )
    parser.add_argument(
        "--native-orientation",
        action="store_true",
        help=(
            "Display the STL exactly as stored by skipping auto/manufacturer rotations and"
            " alignment remaps (manual pre/post flips are ignored when this flag is set)."
        ),
    )
    parser.add_argument(
        "--verify-ccd-angle",
        action="store_true",
        help=(
            "Compare the measured neck/stem medial angle against the module's CCD (shaft) angle "
            "and exit non-zero if the difference exceeds 1 degree."
        ),
    )
    parser.add_argument(
        "--show-points",
        choices=("RES01", "RES02", "TPR01"),
        type=str.upper,
        action="append",
        help=(
            "Display additional reference points from the legacy tables: RES01 (neck origin),"
            " RES02 (reference point), TPR01 (head point)."
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    """CLI entry point."""

    parser = build_parser()
    args = parser.parse_args(argv)

    module, manufacturer_name, uid_member = resolve_uid(args.uid, args.manufacturer)

    detected_rotation_mode = _infer_rotation_mode(manufacturer_name, module, args.rotation_mode)
    native_orientation = bool(args.native_orientation)
    rotation_mode = detected_rotation_mode
    alignment_key: Optional[str] = None
    if native_orientation:
        pre_rotate = False
        post_rotate = False
        rotation_mode = "none"
    else:
        auto_pre, auto_post = ROTATION_BEHAVIOR.get(rotation_mode, (False, False))
        pre_rotate = bool(args.pre_rotate_z_180 or auto_pre)
        post_rotate = bool(args.post_rotate_z_180 or auto_post)
        alignment_key = _resolve_alignment_key(rotation_mode, manufacturer_name, module)
    rotation_half_turns = (1 if pre_rotate else 0) + (1 if post_rotate else 0)
    rotation_applied = rotation_half_turns % 2 == 1
    if native_orientation:
        alignment_matrix = None
        alignment_description = None
    else:
        alignment_matrix = ALIGNMENT_MATRICES.get(alignment_key)
        alignment_description = ALIGNMENT_DESCRIPTIONS.get(alignment_key)
    axis_matrix_initial = _half_turn_matrix(rotation_half_turns)

    requested_points = {point.upper() for point in (args.show_points or [])}

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
    if cut_plane_info:
        origin_vec = _apply_half_turn(cast(Vector3, cut_plane_info["origin"]), rotation_half_turns)
        normal_vec = _apply_half_turn(cast(Vector3, cut_plane_info["normal"]), rotation_half_turns)
        if alignment_matrix is not None:
            origin_vec = _apply_alignment(origin_vec, alignment_matrix)
            normal_vec = _apply_alignment(normal_vec, alignment_matrix)
        normal_vec = _normalize_vec(normal_vec)
        cut_plane_info = {
            "origin": origin_vec,
            "normal": normal_vec,
            "offset": -_dot(normal_vec, origin_vec),
        }

    head_point: Optional[Vector3] = None
    get_head_fn = getattr(module, "get_head_point", None)
    want_head_point = args.show_head or ("TPR01" in requested_points)
    needs_head_geometry = (
        want_head_point
        or args.show_axis_junction
        or args.show_neck_axis
        or args.show_cut_plane_intersection
        or args.show_anatomical_plane
    )
    if needs_head_geometry and callable(get_head_fn):
        try:
            head_point = _coerce_vector(get_head_fn(uid_member))
        except ValueError:
            head_point = None

    reference_point: Optional[Vector3] = None
    if "RES02" in requested_points:
        get_reference_fn = getattr(module, "get_reference_point", None)
        if callable(get_reference_fn):
            try:
                reference_point = _coerce_vector(get_reference_fn(uid_member))
            except ValueError:
                reference_point = None

    offset_point: Optional[Vector3] = None
    offset_head_label: Optional[str] = None
    all_offset_points: List[Tuple[str, Vector3]] = []
    head_offset_fn = getattr(module, "head_to_stem_offset", None)
    if callable(head_offset_fn):
        if args.show_offset:
            head_enum_cls = getattr(module, "S3UID", None)
            head_token = (args.offset_head or "").strip().upper()
            offset_head_uid = None
            if head_enum_cls is not None and head_token and head_token != "AUTO":
                offset_head_uid = getattr(head_enum_cls, head_token, None)
            if offset_head_uid is None:
                offset_head_uid = getattr(head_enum_cls, "HEAD_P0", None)
            if offset_head_uid is None:
                head_uids = getattr(module, "HEAD_UIDS", None)
                if head_uids:
                    offset_head_uid = head_uids[0]
            if offset_head_uid is not None:
                offset_head_label = (
                    offset_head_uid.name if hasattr(offset_head_uid, "name") else str(offset_head_uid)
                )
                try:
                    offset_point = _coerce_vector(head_offset_fn(offset_head_uid, uid_member))
                except ValueError:
                    offset_point = None
        if args.show_all_offsets:
            head_uids = getattr(module, "HEAD_UIDS", None)
            if head_uids:
                for head_uid in head_uids:
                    label = head_uid.name if hasattr(head_uid, "name") else str(head_uid)
                    try:
                        point = _coerce_vector(head_offset_fn(head_uid, uid_member))
                    except ValueError:
                        continue
                    all_offset_points.append((label, point))

    neck_origin = _apply_half_turn_optional(neck_origin, rotation_half_turns)
    head_point = _apply_half_turn_optional(head_point, rotation_half_turns)
    reference_point = _apply_half_turn_optional(reference_point, rotation_half_turns)
    offset_point = _apply_half_turn_optional(offset_point, rotation_half_turns)
    if alignment_matrix is not None:
        neck_origin = _apply_alignment_optional(neck_origin, alignment_matrix)
        head_point = _apply_alignment_optional(head_point, alignment_matrix)
        reference_point = _apply_alignment_optional(reference_point, alignment_matrix)
        offset_point = _apply_alignment_optional(offset_point, alignment_matrix)
    if all_offset_points:
        all_offset_points = [
            (label, _apply_half_turn(point, rotation_half_turns)) for label, point in all_offset_points
        ]
        if alignment_matrix is not None:
            all_offset_points = [
                (label, _apply_alignment(point, alignment_matrix)) for label, point in all_offset_points
            ]

    vtk_module = None
    polydata = None
    stem_axis_info: Optional[dict[str, object]] = None
    anatomical_plane_info: Optional[dict[str, object]] = None
    cut_plane_intersection_upper: Optional[Vector3] = None
    cut_plane_intersection_lower: Optional[Vector3] = None
    cut_plane_alignment_upper = False
    cut_plane_alignment_lower = False
    plane_alignment_tolerance_mm = 0.35
    cut_plane_contour_polydata: Any | None = None
    plane_contour_intersection_count: Optional[int] = None

    tokens = [rcc_id, uid_member.name, str(uid_member.value)]
    stl_path, additional_matches = find_matching_stl(args.folders, tokens)

    needs_stem_axis = (
        args.show_axis_junction
        or args.verify_ccd_angle
        or args.show_tip_point
        or args.show_bottom_point
        or args.show_cut_plane_intersection
        or args.show_anatomical_plane
    )
    needs_cut_geometry = cut_plane_info is not None and (
        args.show_cut_plane_intersection or args.show_cut_plane_contour
    )
    needs_polydata = needs_stem_axis or rotation_applied or needs_cut_geometry

    if needs_polydata:
        vtk_module = ensure_vtk()
        reader = vtk_module.vtkSTLReader()
        reader.SetFileName(str(stl_path))
        reader.Update()
        polydata = reader.GetOutput()
        polydata = _rotate_polydata_half_turns(polydata, rotation_half_turns, vtk_module)
        if alignment_matrix is not None:
            polydata = _apply_alignment_polydata(polydata, alignment_matrix, vtk_module)
    principal_axis_data: Optional[Tuple[Vector3, Vector3]] = None
    if needs_stem_axis and polydata is not None:
        principal_axis_data = _compute_polydata_principal_axis(polydata)
        axis_seed = principal_axis_data[0] if principal_axis_data else UP_VECTOR
        low_point = _find_extreme_point_along_axis(polydata, axis_seed, minimize=True)
        high_point = _find_extreme_point_along_axis(polydata, axis_seed, minimize=False)
        if low_point and high_point:
            down_dir: Optional[Vector3] = None
            if head_point and neck_origin:
                down_candidate = _vec_sub(neck_origin, head_point)
                down_norm = _normalize_vec(down_candidate)
                if _vector_length(down_norm) > 1e-6:
                    down_dir = down_norm

            if down_dir:
                vec_low = _vec_sub(low_point, head_point)
                vec_high = _vec_sub(high_point, head_point)
                score_low = _dot(_normalize_vec(vec_low), down_dir)
                score_high = _dot(_normalize_vec(vec_high), down_dir)
                if score_low >= score_high:
                    bottom_point = low_point
                    tip_point = high_point
                else:
                    bottom_point = high_point
                    tip_point = low_point
                axis_dir_raw = _vec_scale(down_dir, -1.0)
            else:
                bottom_point = low_point
                tip_point = high_point
                axis_dir_raw = _normalize_vec(_vec_sub(tip_point, bottom_point))

            axis_span = _vector_length(_vec_sub(tip_point, bottom_point))
            stem_axis_info = {
                "axis_dir_raw": axis_dir_raw,
                "axis_dir_display": axis_dir_raw,
                "bottom_point": bottom_point,
                "tip_point": tip_point,
                "axis_span": axis_span,
                "axis_display_length": axis_span,
            }

    if (
        (args.show_cut_plane_intersection or args.show_anatomical_plane)
        and head_point
        and neck_origin
        and stem_axis_info
    ):
        tip_point = cast(Vector3, stem_axis_info["tip_point"])
        vec_head = _vec_sub(head_point, neck_origin)
        vec_tip = _vec_sub(tip_point, neck_origin)
        plane_normal_raw = _cross(vec_head, vec_tip)
        if _vector_length(plane_normal_raw) > 1e-6:
            plane_normal = _normalize_vec(plane_normal_raw)
            anatomical_plane_info = {
                "normal": plane_normal,
                "offset": -_dot(plane_normal, neck_origin),
                "origin": neck_origin,
                "points": {
                    "neck": neck_origin,
                    "head": head_point,
                    "tip": tip_point,
                },
            }

    if needs_cut_geometry and polydata is not None and cut_plane_info is not None:
        vtk_module = vtk_module or ensure_vtk()
        plane = vtk_module.vtkPlane()
        plane.SetOrigin(*cut_plane_info["origin"])
        plane.SetNormal(*cut_plane_info["normal"])
        cutter = vtk_module.vtkCutter()
        cutter.SetCutFunction(plane)
        cutter.SetInputData(polydata)
        cutter.Update()
        cut_output = cutter.GetOutput()
        points = cut_output.GetPoints()
        if points is not None and points.GetNumberOfPoints() > 0:
            cut_plane_contour_polydata = cut_output

            if args.show_cut_plane_intersection:
                count = points.GetNumberOfPoints()
                plane_normal: Optional[Vector3] = None
                plane_offset: Optional[float] = None
                if anatomical_plane_info:
                    plane_normal = cast(Vector3, anatomical_plane_info["normal"])
                    plane_offset = float(anatomical_plane_info["offset"])

                plane_intersections: List[Vector3] = []
                if plane_normal is not None and plane_offset is not None:
                    plane_intersections = _intersect_polyline_with_plane(
                        cut_output,
                        plane_normal,
                        plane_offset,
                        vtk_module,
                    )
                    plane_contour_intersection_count = len(plane_intersections)

                source_points: List[Vector3] = []
                alignment_flag = False

                if plane_intersections:
                    source_points = plane_intersections
                    alignment_flag = True
                else:
                    all_points: List[Vector3] = []
                    for idx in range(count):
                        x, y, z = points.GetPoint(idx)
                        all_points.append((float(x), float(y), float(z)))

                    aligned_points: List[Vector3] = []
                    if plane_normal is not None and plane_offset is not None:
                        for candidate in all_points:
                            signed_distance = _dot(plane_normal, candidate) + plane_offset
                            if abs(signed_distance) <= plane_alignment_tolerance_mm:
                                aligned_points.append(candidate)

                    if aligned_points:
                        source_points = aligned_points
                        alignment_flag = True
                    else:
                        source_points = all_points
                        alignment_flag = False

                if source_points:
                    cut_plane_intersection_upper = max(source_points, key=lambda pt: pt[2])
                    cut_plane_intersection_lower = min(source_points, key=lambda pt: pt[2])
                    cut_plane_alignment_upper = alignment_flag
                    cut_plane_alignment_lower = alignment_flag

    print(
        f"Resolved implant:\n"
        f"  Provided UID: {args.uid}\n"
        f"  Manufacturer: {manufacturer_name}\n"
        f"  S3UID: {uid_member.name} ({uid_member.value})\n"
        f"  RCC ID: {rcc_id}\n"
        f"  STL path: {stl_path}\n"
    )
    log_rotation = (
        args.native_orientation
        or rotation_mode != "none"
        or args.rotation_mode in {"mathys", "medacta", "johnson", "none"}
        or args.pre_rotate_z_180
        or args.post_rotate_z_180
    )
    if args.native_orientation:
        print(
            "  Rotation mode: native/raw STL orientation "
            f"(auto detected {detected_rotation_mode}; pre/post overrides ignored)"
        )
    elif log_rotation:
        print(
            f"  Rotation mode: {rotation_mode} (pre={pre_rotate}, post={post_rotate})"
        )
    if rotation_applied:
        print("  Applied STL Z rotation: 180°")
    if alignment_matrix is not None and alignment_description:
        label = alignment_key or rotation_mode
        print(f"  Applied {label} axis remap: {alignment_description}")
    if neck_origin:
        neck_label = "Neck origin (RES01)" if "RES01" in requested_points else "Neck origin"
        print(f"  {neck_label} (mm): {_format_vector(neck_origin)}")
    if cut_plane_info:
        print(
            f"  Cut plane origin (mm): {_format_vector(cut_plane_info['origin'])}\n"
            f"  Cut plane normal: {_format_vector(cut_plane_info['normal'])}"
            f" (d = {cut_plane_info['offset']:.3f})"
        )
    if args.show_cut_plane_intersection:
        if cut_plane_info is None:
            print("  Cut/stem centered intersection: SKIPPED (cut plane unavailable)")
        elif cut_plane_intersection_upper is None or cut_plane_intersection_lower is None:
            print("  Cut/stem centered intersection: SKIPPED (plane did not intersect STL)")
        else:
            def _annotation(aligned: bool) -> str:
                if aligned:
                    return " (aligned with head/neck/tip plane)"
                if anatomical_plane_info is None:
                    return " (head/neck/tip plane unavailable; using fallback)"
                return f" (alignment > {plane_alignment_tolerance_mm:.2f} mm; using fallback)"

            print(
                "  Cut/stem upper centered intersection (mm): "
                f"{_format_vector(cut_plane_intersection_upper)}{_annotation(cut_plane_alignment_upper)}"
            )
            print(
                "  Cut/stem lower centered intersection (mm): "
                f"{_format_vector(cut_plane_intersection_lower)}{_annotation(cut_plane_alignment_lower)}"
            )
            if plane_contour_intersection_count is not None:
                print(
                    "  Cut contour ∩ anatomical plane: "
                    f"{plane_contour_intersection_count} point(s)"
                )
    if args.show_cut_plane_contour:
        if cut_plane_info is None:
            print("  Cut/stem intersection contour: SKIPPED (cut plane unavailable)")
        elif cut_plane_contour_polydata is None:
            print("  Cut/stem intersection contour: SKIPPED (plane did not intersect STL)")
        else:
            contour_points = cut_plane_contour_polydata.GetNumberOfPoints()
            print(
                "  Cut/stem intersection contour: "
                f"{contour_points} sampled points"
            )
    if head_point and want_head_point:
        print(f"  Head point (mm): {_format_vector(head_point)}")
    if args.show_anatomical_plane:
        if anatomical_plane_info is None:
            print(
                "  Anatomical plane (head/neck/tip): SKIPPED (required points unavailable)"
            )
        else:
            plane_normal = cast(Vector3, anatomical_plane_info["normal"])
            plane_offset = float(anatomical_plane_info["offset"])
            print(
                "  Anatomical plane normal: "
                f"{_format_vector(plane_normal)} (d = {plane_offset:.3f})"
            )
    if reference_point:
        print(f"  Reference point (RES02) (mm): {_format_vector(reference_point)}")
    if offset_point and offset_head_label:
        print(
            f"  Offset point ({offset_head_label}) (mm): "
            f"{_format_vector(offset_point)}"
        )
    if all_offset_points:
        print("  Offset table:")
        for label, point in all_offset_points:
            print(f"    {label}: {_format_vector(point)}")

    neck_axis_dir: Optional[Vector3] = None
    if neck_origin and head_point:
        neck_axis_dir = _normalize_vec(_vec_sub(head_point, neck_origin))

    needs_shaft_angle = bool(neck_origin) and (args.show_shaft_axis or args.verify_ccd_angle)
    shaft_axis_info: Optional[Tuple[Vector3, Vector3, float]] = None
    shaft_angle_deg: Optional[float] = None
    if needs_shaft_angle and neck_origin:
        get_shaft_angle_fn = getattr(module, "get_shaft_angle", None)
        if callable(get_shaft_angle_fn):
            try:
                angle_deg = float(get_shaft_angle_fn(uid_member))
                angle_rad = math.radians(angle_deg)
                axis_dir = _normalize_vec((math.cos(angle_rad), 0.0, math.sin(angle_rad)))
                axis_dir = _apply_half_turn(axis_dir, rotation_half_turns)
                if alignment_matrix is not None:
                    axis_dir = _apply_alignment(axis_dir, alignment_matrix)
                shaft_axis_info = (neck_origin, axis_dir, angle_deg)
                shaft_angle_deg = angle_deg
            except ValueError:
                shaft_axis_info = None
    junction_info: Optional[dict[str, object]] = None
    if (args.show_axis_junction or args.verify_ccd_angle) and neck_origin and neck_axis_dir and stem_axis_info:
        p_neck = neck_origin
        d_neck = neck_axis_dir
        axis_point = cast(Vector3, stem_axis_info["bottom_point"])
        axis_dir_raw = cast(Vector3, stem_axis_info["axis_dir_raw"])
        closest = _closest_points_between_lines(p_neck, d_neck, axis_point, axis_dir_raw)
        if closest:
            neck_pt, tip_pt = closest
            junction_point = _vec_scale(_vec_add(neck_pt, tip_pt), 0.5)
            separation = _vector_length(_vec_sub(neck_pt, tip_pt))
            raw_angle = math.degrees(
                math.acos(
                    _clamp(_dot(_normalize_vec(d_neck), _normalize_vec(axis_dir_raw)), -1.0, 1.0)
                )
            )
            medial_angle = max(0.0, 180.0 - raw_angle)
            junction_info = {
                "junction_point": junction_point,
                "separation": separation,
                "angle": medial_angle,
                "neck_point": neck_pt,
                "tip_point": tip_pt,
            }
            if stem_axis_info and junction_point:
                display_vec = _vec_sub(junction_point, axis_point)
                display_len = _vector_length(display_vec)
                if display_len > 1e-6:
                    stem_axis_info["axis_dir_display"] = _normalize_vec(display_vec)
                    stem_axis_info["axis_display_length"] = display_len

    if shaft_axis_info and args.show_shaft_axis:
        origin, axis_dir, angle_deg = shaft_axis_info
        print(f"  Shaft angle (deg): {angle_deg:.2f}")
        print(f"  Shaft axis direction: {_format_vector(axis_dir)}")
    if neck_axis_dir and (args.show_head or "TPR01" in requested_points or args.show_neck_axis):
        print(f"  Neck axis direction: {_format_vector(neck_axis_dir)}")
    if stem_axis_info and (
        args.show_axis_junction
        or args.verify_ccd_angle
        or args.show_tip_point
        or args.show_bottom_point
    ):
        tip_point = cast(Vector3, stem_axis_info["tip_point"])
        bottom_point = cast(Vector3, stem_axis_info["bottom_point"])
        axis_dir = cast(Vector3, stem_axis_info.get("axis_dir_display", stem_axis_info["axis_dir_raw"]))
        print(f"  Tip point (highest) (mm): {_format_vector(tip_point)}")
        print(f"  Bottom point (mm): {_format_vector(bottom_point)}")
        print(f"  Stem axis direction (bottom->junction): {_format_vector(axis_dir)}")
    if junction_info:
        junction_point = cast(Vector3, junction_info["junction_point"])
        separation = float(junction_info["separation"])
        angle = float(junction_info["angle"])
        print(f"  Neck/Stem axis medial angle (deg): {angle:.2f}")
        print(f"  Axis junction (mm): {_format_vector(junction_point)}")
        if separation > 1e-3:
            print(f"  Axis junction gap (mm): {separation:.3f}")

    verification_failed = False
    if args.verify_ccd_angle:
        tolerance = 1.0
        if shaft_angle_deg is None:
            print("  CCD angle test: SKIPPED (shaft angle unavailable in module)")
        elif not junction_info:
            print("  CCD angle test: SKIPPED (axis junction could not be computed)")
        else:
            medial_angle = float(junction_info["angle"])
            diff = abs(medial_angle - shaft_angle_deg)
            if diff <= tolerance:
                print(
                    f"  CCD angle test: PASS (|Δ| = {diff:.2f}° ≤ {tolerance:.2f}°)"
                )
            else:
                verification_failed = True
                print(
                    f"  CCD angle test: FAIL (|Δ| = {diff:.2f}° > {tolerance:.2f}°)"
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
        if args.show_anatomical_plane and anatomical_plane_info:
            overlay_factories.append(
                _build_cut_plane_actor(
                    anatomical_plane_info["origin"],
                    anatomical_plane_info["normal"],
                    args.plane_size,
                    (0.95, 0.45, 0.45),
                    0.25,
                )
            )
        if head_point and want_head_point:
            overlay_factories.append(_build_head_actor(head_point))
        if offset_point:
            overlay_factories.append(_build_offset_actor(offset_point))
        if all_offset_points:
            for idx, (label, point) in enumerate(all_offset_points):
                if offset_point and offset_head_label == label:
                    continue
                color = OFFSET_COLORS[idx % len(OFFSET_COLORS)]
                overlay_factories.append(_build_offset_actor(point, color))
        if shaft_axis_info and args.show_shaft_axis:
            origin, axis_dir, _ = shaft_axis_info
            overlay_factories.append(
                _build_shaft_axis_actor(
                    origin,
                    axis_dir,
                    args.plane_size * 1.5,
                )
            )
        if neck_axis_dir and neck_origin and args.show_neck_axis:
            if junction_info:
                neck_target = cast(Vector3, junction_info["neck_point"])
                neck_segment = _vec_sub(neck_target, neck_origin)
                axis_length = _vector_length(neck_segment)
                if axis_length < 1e-3:
                    axis_length = args.plane_size * 0.5
                direction = neck_axis_dir
                if _dot(neck_segment, direction) < 0:
                    direction = _vec_scale(direction, -1.0)
                overlay_factories.append(
                    _build_vertical_axis_actor(
                        neck_origin,
                        direction,
                        axis_length,
                    )
                )
            else:
                overlay_factories.append(
                    _build_shaft_axis_actor(
                        neck_origin,
                        neck_axis_dir,
                        args.plane_size * 1.2,
                    )
                )
        if reference_point:
            overlay_factories.append(_build_reference_actor(reference_point))
        if stem_axis_info and args.show_tip_point:
            tip_point = cast(Vector3, stem_axis_info["tip_point"])
            overlay_factories.append(_build_tip_point_actor(tip_point))
        if stem_axis_info and args.show_bottom_point:
            bottom_point = cast(Vector3, stem_axis_info["bottom_point"])
            overlay_factories.append(_build_bottom_point_actor(bottom_point))
        if junction_info:
            junction_point = cast(Vector3, junction_info["junction_point"])
            overlay_factories.append(_build_junction_actor(junction_point))
        if args.show_cut_plane_intersection:
            if cut_plane_intersection_upper:
                overlay_factories.append(
                    _build_cut_intersection_actor(cut_plane_intersection_upper, (0.95, 0.95, 0.2))
                )
            if cut_plane_intersection_lower:
                overlay_factories.append(
                    _build_cut_intersection_actor(cut_plane_intersection_lower, (0.95, 0.7, 0.2))
                )
        if args.show_cut_plane_contour and cut_plane_contour_polydata is not None:
            overlay_factories.append(
                _build_cut_contour_actor(cut_plane_contour_polydata)
            )
        if args.show_axes_reference:
            overlay_factories.append(_build_axes_actor(max(args.plane_size, 40.0)))
        if args.show_axis_frames:
            frame_length = max(args.plane_size * 0.85, 40.0)
            initial_colors = ((0.95, 0.65, 0.65), (0.65, 0.95, 0.65), (0.65, 0.65, 0.95))
            overlay_factories.append(
                _build_axes_frame_actor(
                    axis_matrix_initial,
                    frame_length,
                    initial_colors,
                    0.7,
                )
            )

    show_stl(
        stl_path,
        overlay_factories if overlay_factories else None,
        stem_opacity=args.stem_opacity,
        polydata=polydata,
        vtk_module=vtk_module,
    )

    if args.verify_ccd_angle and verification_failed:
        raise SystemExit("CCD angle verification failed (|Δ| exceeded tolerance).")


if __name__ == "__main__":  # pragma: no cover
    main()
