#!/usr/bin/env python3
"""Lightweight VTP viewer that mimics the EZplan LUT from load_nifti_and_stem."""

from __future__ import annotations

import argparse
import os
import sys
import xml.etree.ElementTree as ET
from importlib import import_module
from pathlib import Path

import vtk


EZPLAN_ZONE_DEFS = [
	(-200.0, 100.0, (0.0, 0.0, 1.0), "Loosening"),
	(100.0, 400.0, (1.0, 0.0, 1.0), "MicroMove"),
	(400.0, 1000.0, (0.0, 1.0, 0.0), "Stable"),
	(1000.0, 1500.0, (1.0, 0.0, 0.0), "Cortical"),
]
DEFAULT_ARRAY = "VolumeScalars"


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"View a VTP stem file with the same EZplan HU LUT used by load_nifti_and_stem."
		)
	)
	parser.add_argument("vtp", help="Path to the .vtp file exported from Slicer")
	parser.add_argument(
		"--array",
		default=DEFAULT_ARRAY,
		help="Point-data scalar array to display (default: %(default)s)",
	)
	parser.add_argument(
		"--hu-array",
		default=DEFAULT_ARRAY,
		help="HU scalar array to use when masking by Gruen zones (default: %(default)s)",
	)
	parser.add_argument(
		"--wireframe",
		action="store_true",
		help="Render the mesh in wireframe mode to inspect topology",
	)
	parser.add_argument(
		"--opacity",
		type=float,
		default=1.0,
		help="Set stem opacity (0.0 transparent .. 1.0 opaque, default: 1.0)",
	)
	parser.add_argument(
		"--base-color",
		default=None,
		help="Override base stem color as r,g,b (e.g., 0.7,0.7,0.7). If omitted, uses the scalar map.",
	)
	parser.add_argument(
		"--side",
		choices=("auto", "left", "right"),
		default="auto",
		help="Override side when mirroring annotations (default: auto)",
	)
	parser.add_argument(
		"--local-frame",
		action="store_true",
		help="Treat the VTP coordinates as the local stem frame (enables Gruen/cut-plane helpers)",
	)
	parser.add_argument(
		"--seedplan",
		help="Optional seedplan.xml path to infer implant annotations",
	)
	parser.add_argument(
		"--config-index",
		type=int,
		help="1-based hip implant configuration index to use when resolving annotations",
	)
	parser.add_argument(
		"--neck-point",
		help="Neck point in local frame (x,y,z) used for Gruen zone reference",
	)
	parser.add_argument(
		"--show-neck-point",
		action="store_true",
		help="Render the neck point marker",
	)
	parser.add_argument(
		"--show-cut-plane",
		action="store_true",
		help="Render the cut plane in the local frame",
	)
	parser.add_argument(
		"--cut-plane-origin",
		help="Cut plane origin in local frame (x,y,z)",
	)
	parser.add_argument(
		"--cut-plane-normal",
		help="Cut plane normal in local frame (x,y,z)",
	)
	parser.add_argument(
		"--cut-plane-size",
		type=float,
		default=60.0,
		help="Cut plane size (mm) when rendered (default: 60)",
	)
	parser.add_argument(
		"--gruen-zones",
		action="store_true",
		help="Compute Gruen zones in local frame",
	)
	parser.add_argument(
		"--show-gruen-zones",
		action="store_true",
		help="Display the stem colored by Gruen zones",
	)
	parser.add_argument(
		"--gruen-hu-zones",
		help="Comma-separated Gruen zones to show HU values for (e.g., 1,2,3)",
	)
	parser.add_argument(
		"--print-gruen-stats",
		action="store_true",
		help="Print point counts per Gruen zone",
	)
	parser.add_argument(
		"--show-axes",
		action="store_true",
		help="Display an XYZ axes frame in the scene",
	)
	parser.add_argument(
		"--axes-size",
		type=float,
		default=60.0,
		help="Total length (mm) of the XYZ axes (default: 60)",
	)
	return parser.parse_args()


def _load_polydata(path: str) -> vtk.vtkPolyData:
	if not os.path.isfile(path):
		raise FileNotFoundError(path)
	reader = vtk.vtkXMLPolyDataReader()
	reader.SetFileName(path)
	reader.Update()
	poly = reader.GetOutput()
	if not poly or poly.GetNumberOfPoints() == 0:
		raise RuntimeError("VTP file '%s' produced empty polydata" % path)
	return poly


def _derive_config_labels(source_label: str, ordinal: int, *candidates: str | None) -> tuple[str, str]:
	for candidate in candidates:
		if candidate and candidate.strip():
			friendly = candidate.strip()
			break
	else:
		friendly = f"{source_label}_{ordinal:02d}"
	sanitized = "".join(
		ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in friendly
	).strip("_")
	if not sanitized:
		sanitized = f"{source_label}_{ordinal:02d}"
	return friendly, sanitized


def _extract_stem_infos(xml_path: Path) -> list[dict[str, object]]:
	tree = ET.parse(xml_path)
	root = tree.getroot()
	hip_configs = root.findall(".//hipImplantConfig")
	history_configs = root.findall(".//hipImplantConfigHistoryList/hipImplantConfig")
	entries: list[dict[str, object]] = []
	for source_label, configs in (("active", hip_configs), ("history", history_configs)):
		for hip_config in configs:
			fem_config = hip_config.find("./femImplantConfig")
			if fem_config is None:
				continue
			stem_shape = fem_config.find(".//s3Shape[@part='stem']")
			if stem_shape is None:
				continue
			info: dict[str, object] = {}
			info["requested_side"] = fem_config.attrib.get("requestedSide")
			info["configured_side"] = fem_config.attrib.get("side")
			info["state"] = fem_config.attrib.get("state")
			info["source"] = source_label
			info["config_index"] = len(entries)
			hip_label = hip_config.attrib.get("name")
			fallback_label = fem_config.attrib.get("name")
			raw_label = hip_label or fallback_label
			friendly, sanitized = _derive_config_labels(source_label, len(entries) + 1, raw_label)
			info["config_label"] = friendly
			info["config_folder"] = sanitized
			info["hip_config_name"] = hip_label or fallback_label or friendly
			pretty_name = hip_config.findtext("./prettyName") or hip_config.attrib.get("prettyName")
			if pretty_name is not None:
				pretty_name_clean = pretty_name.strip()
				if pretty_name_clean:
					info["hip_config_pretty_name"] = pretty_name_clean
			uid_attr = stem_shape.attrib.get("uid")
			if uid_attr:
				try:
					uid_val = int(uid_attr)
				except ValueError:
					uid_val = None
				else:
					info["uid"] = uid_val
			entries.append(info)
	if not entries:
		raise RuntimeError("Unable to locate femoral stem definition in seedplan")
	return entries


def _parse_metrics_xml(xml_path: Path) -> tuple[Path | None, int | None, str | None]:
	try:
		tree = ET.parse(xml_path)
		root = tree.getroot()
	except Exception:
		return None, None, None
	if root.tag != "stemMetrics":
		return None, None, None
	seedplan_value = root.attrib.get("seedplanPath")
	seedplan_path = Path(seedplan_value).resolve() if seedplan_value else None
	config_raw = root.attrib.get("stemConfigIndex")
	try:
		config_index = int(config_raw) + 1 if config_raw is not None else None
	except ValueError:
		config_index = None
	requested_side = root.attrib.get("requestedSide")
	configured_side = root.attrib.get("configuredSide")
	if not requested_side or not configured_side:
		stem_node = root.find("./stem")
		if stem_node is not None:
			requested_side = requested_side or stem_node.attrib.get("requestedSide")
			configured_side = configured_side or stem_node.attrib.get("configuredSide")
	return seedplan_path, config_index, (requested_side or configured_side)


def _read_metrics_array_name(xml_path: Path) -> str | None:
	try:
		tree = ET.parse(xml_path)
		root = tree.getroot()
	except Exception:
		return None
	if root.tag != "stemMetrics":
		return None
	array_name = root.attrib.get("array")
	if array_name:
		return array_name.strip()
	return None


def _find_seedplan_for_vtp(vtp_path: str, explicit: str | None) -> tuple[Path | None, int | None, str | None]:
	if explicit:
		return Path(explicit).resolve(), None, None
	vtp_parent = Path(vtp_path).resolve().parent
	metrics_candidates = sorted(vtp_parent.glob("*_stem_metrics.xml"))
	for metrics_path in metrics_candidates:
		seedplan, config_index, side = _parse_metrics_xml(metrics_path)
		if seedplan is not None:
			return seedplan, config_index, side
	parents = [vtp_parent]
	for _ in range(2):
		if parents[-1].parent != parents[-1]:
			parents.append(parents[-1].parent)
	for parent in parents:
		seedplan = parent / "seedplan.xml"
		if seedplan.exists():
			return seedplan, None, None
		xml_candidates = sorted(parent.glob("*.xml"))
		if len(xml_candidates) == 1:
			return xml_candidates[0], None, None
	return None, None, None


def _find_metrics_array_for_vtp(vtp_path: str) -> str | None:
	vtp_parent = Path(vtp_path).resolve().parent
	metrics_candidates = sorted(vtp_parent.glob("*_stem_metrics.xml"))
	for metrics_path in metrics_candidates:
		array_name = _read_metrics_array_name(metrics_path)
		if array_name:
			return array_name
	return None


def _pick_scalar_array(poly: vtk.vtkPolyData, preferred: str | None) -> str | None:
	point_data = poly.GetPointData()
	if preferred and point_data.GetArray(preferred) is not None:
		return preferred
	available = [
		point_data.GetArrayName(i)
		for i in range(point_data.GetNumberOfArrays())
		if point_data.GetArrayName(i)
	]
	if not available:
		return None
	if preferred:
		lower = preferred.lower()
		for name in available:
			if lower in name.lower():
				return name
	for token in ("scalars", "volume", "hu"):
		for name in available:
			if token in name.lower():
				return name
	return available[0]


def _resolve_implant_module(uid: int | None):
	if uid is None:
		return None, None
	module_names = (
		"amedacta_complete",
		"mathys_optimys_complete",
		"johnson_corail_complete",
		"johnson_actis_complete",
	)
	for module_name in module_names:
		try:
			module = import_module(module_name)
		except Exception:
			continue
		enum_cls = getattr(module, "S3UID", None)
		if enum_cls is None:
			continue
		try:
			uid_member = enum_cls(int(uid))
		except (TypeError, ValueError):
			continue
		return module, uid_member
	return None, None


def _resolve_stem_annotation_defaults(
	vtp_path: str,
	seedplan: str | None,
	config_index: int | None,
) -> tuple[
	tuple[float, float, float] | None,
	tuple[float, float, float] | None,
	tuple[float, float, float] | None,
	str | None,
]:
	seedplan_path, inferred_index, inferred_side = _find_seedplan_for_vtp(vtp_path, seedplan)
	if config_index is None:
		config_index = inferred_index
	if seedplan_path is None or not seedplan_path.exists():
		return None, None, None, inferred_side
	try:
		stem_infos = _extract_stem_infos(seedplan_path)
	except Exception:
		return None, None, None, inferred_side
	selected_info: dict[str, object] | None = None
	if config_index is not None:
		idx = max(config_index - 1, 0)
		if idx < len(stem_infos):
			selected_info = stem_infos[idx]
	else:
		parent_name = Path(vtp_path).resolve().parent.name
		for info in stem_infos:
			if info.get("config_folder") == parent_name:
				selected_info = info
				break
	if selected_info is None:
		selected_info = stem_infos[0]
	uid_val = selected_info.get("uid") if selected_info else None
	module, uid_member = _resolve_implant_module(uid_val if isinstance(uid_val, int) else None)
	if module is None or uid_member is None:
		return None, None, None, inferred_side
	neck_point = None
	cut_origin = None
	cut_normal = None
	get_neck_origin = getattr(module, "get_neck_origin", None)
	if callable(get_neck_origin):
		try:
			origin = get_neck_origin(uid_member)
			neck_point = (float(origin[0]), float(origin[1]), float(origin[2]))
		except Exception:
			neck_point = None
	get_cut_plane = getattr(module, "get_cut_plane", None)
	if callable(get_cut_plane):
		try:
			plane = get_cut_plane(uid_member)
			origin = getattr(plane, "origin", None)
			normal = getattr(plane, "normal", None)
			if origin is not None and normal is not None:
				cut_origin = (float(origin[0]), float(origin[1]), float(origin[2]))
				cut_normal = (float(normal[0]), float(normal[1]), float(normal[2]))
		except Exception:
			cut_origin = None
			cut_normal = None
	return neck_point, cut_origin, cut_normal, inferred_side


def _build_ezplan_transfer_function() -> vtk.vtkColorTransferFunction:
	tf = vtk.vtkColorTransferFunction()
	for zone_min, zone_max, (r, g, b), _label in EZPLAN_ZONE_DEFS:
		tf.AddRGBPoint(zone_min, r, g, b)
		tf.AddRGBPoint(zone_max, r, g, b)
	return tf


def _build_gruen_lookup_table() -> vtk.vtkLookupTable:
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfTableValues(15)
	lut.Build()
	colors = [
		(0.6, 0.6, 0.6),
		(0.9, 0.2, 0.2),
		(0.9, 0.5, 0.2),
		(0.9, 0.8, 0.2),
		(0.6, 0.6, 0.6),
		(0.2, 0.8, 0.2),
		(0.2, 0.8, 0.6),
		(0.2, 0.8, 0.9),
		(0.2, 0.2, 0.9),
		(0.2, 0.5, 0.9),
		(0.2, 0.8, 0.9),
		(0.6, 0.6, 0.6),
		(0.9, 0.2, 0.6),
		(0.9, 0.2, 0.9),
		(0.6, 0.2, 0.9),
	]
	for idx in range(15):
		r, g, b = colors[idx]
		lut.SetTableValue(idx, r, g, b, 1.0)
	return lut


def _parse_vector(value: str) -> tuple[float, float, float]:
	parts = [item.strip() for item in value.split(",") if item.strip()]
	if len(parts) != 3:
		raise ValueError("Expected vector as 'x,y,z'")
	return (float(parts[0]), float(parts[1]), float(parts[2]))


def _normalize(vec: tuple[float, float, float]) -> tuple[float, float, float]:
	x, y, z = vec
	length = (x * x + y * y + z * z) ** 0.5
	if length <= 1e-6:
		return (0.0, 0.0, 0.0)
	return (x / length, y / length, z / length)


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
	return (
		a[1] * b[2] - a[2] * b[1],
		a[2] * b[0] - a[0] * b[2],
		a[0] * b[1] - a[1] * b[0],
	)


def _compute_principal_axis(poly: vtk.vtkPolyData) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
	points = poly.GetPoints()
	count = points.GetNumberOfPoints()
	mean = [0.0, 0.0, 0.0]
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		mean[0] += x
		mean[1] += y
		mean[2] += z
	mean = [coord / count for coord in mean]
	var = [[0.0, 0.0, 0.0] for _ in range(3)]
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		dx = x - mean[0]
		dy = y - mean[1]
		dz = z - mean[2]
		var[0][0] += dx * dx
		var[0][1] += dx * dy
		var[0][2] += dx * dz
		var[1][0] += dy * dx
		var[1][1] += dy * dy
		var[1][2] += dy * dz
		var[2][0] += dz * dx
		var[2][1] += dz * dy
		var[2][2] += dz * dz
	if count > 1:
		inv = 1.0 / (count - 1)
		for row in range(3):
			for col in range(3):
				var[row][col] *= inv
	vec = _normalize((1.0, 1.0, 1.0))
	for _ in range(24):
		vec = _normalize((
			var[0][0] * vec[0] + var[0][1] * vec[1] + var[0][2] * vec[2],
			var[1][0] * vec[0] + var[1][1] * vec[1] + var[1][2] * vec[2],
			var[2][0] * vec[0] + var[2][1] * vec[1] + var[2][2] * vec[2],
		))
	return vec, (mean[0], mean[1], mean[2])


def _compute_gruen_zone(z_norm: float, group: str) -> int:
	if z_norm < 0.05:
		return 4 if group in ("lateral", "medial") else 11
	if z_norm < 0.40:
		return {"lateral": 3, "medial": 5, "anterior": 10, "posterior": 12}[group]
	if z_norm < 0.80:
		return {"lateral": 2, "medial": 6, "anterior": 9, "posterior": 13}[group]
	return {"lateral": 1, "medial": 7, "anterior": 8, "posterior": 14}[group]



def _apply_gruen_zones(
	poly: vtk.vtkPolyData,
	neck_point: tuple[float, float, float] | None,
	cut_plane_origin: tuple[float, float, float] | None,
	cut_plane_normal: tuple[float, float, float] | None,
	side: str,
) -> str:
	axis_dir, mean = _compute_principal_axis(poly)
	points = poly.GetPoints()
	count = points.GetNumberOfPoints()
	projections = []
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		projections.append(axis_dir[0] * x + axis_dir[1] * y + axis_dir[2] * z)
	min_proj = min(projections)
	max_proj = max(projections)
	if neck_point is not None:
		neck_proj = axis_dir[0] * neck_point[0] + axis_dir[1] * neck_point[1] + axis_dir[2] * neck_point[2]
		if abs(neck_proj - min_proj) < abs(neck_proj - max_proj):
			min_proj, max_proj = max_proj, min_proj
			axis_dir = (-axis_dir[0], -axis_dir[1], -axis_dir[2])
	if cut_plane_origin is not None:
		cut_proj = axis_dir[0] * cut_plane_origin[0] + axis_dir[1] * cut_plane_origin[1] + axis_dir[2] * cut_plane_origin[2]
		if cut_proj > min_proj:
			max_proj = cut_proj
	axis_len = max(max_proj - min_proj, 1e-6)
	ref = (0.0, 0.0, 1.0)
	if abs(_dot(axis_dir, ref)) > 0.9:
		ref = (0.0, 1.0, 0.0)
	x_axis = _normalize(_cross(ref, axis_dir))
	y_axis = _normalize(_cross(axis_dir, x_axis))
	zones = vtk.vtkIntArray()
	zones.SetName("GruenZone")
	zones.SetNumberOfComponents(1)
	zones.SetNumberOfTuples(count)
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		xp = _dot((x, y, z), x_axis)
		yp = _dot((x, y, z), y_axis)
		zproj = _dot((x, y, z), axis_dir)
		z_norm = (zproj - min_proj) / axis_len
		if abs(xp) >= abs(yp):
			if side == "left":
				group = "lateral" if xp <= 0 else "medial"
			else:
				group = "lateral" if xp >= 0 else "medial"
		else:
			group = "anterior" if yp >= 0 else "posterior"
		zones.SetTuple1(idx, float(_compute_gruen_zone(z_norm, group)))
	point_data = poly.GetPointData()
	if point_data.GetArray("GruenZone"):
		point_data.RemoveArray("GruenZone")
	point_data.AddArray(zones)
	point_data.SetActiveScalars("GruenZone")
	poly.Modified()
	return "GruenZone"


def _apply_hu_zone_mask(poly: vtk.vtkPolyData, hu_array: str, zones: list[int]) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(hu_array)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array)
	zone_array = point_data.GetArray("GruenZone")
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	masked_name = f"{hu_array}_Gruen"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	allowed = set(zones)
	for idx in range(source_array.GetNumberOfTuples()):
		zone_id = int(zone_array.GetTuple1(idx))
		if zone_id in allowed:
			masked.SetTuple1(idx, source_array.GetTuple1(idx))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _configure_mapper(
	poly: vtk.vtkPolyData,
	array_name: str,
	scalar_range: tuple[float, float] | None = None,
	lookup_table: vtk.vtkScalarsToColors | None = None,
	nan_color: tuple[float, float, float, float] | None = None,
) -> tuple[vtk.vtkPolyDataMapper, tuple[float, float], str]:
	point_data = poly.GetPointData()
	selected_array_name = array_name
	array = point_data.GetArray(selected_array_name)
	if array is None:
		available = [point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays()) if point_data.GetArrayName(i)]
		if available:
			selected_array_name = available[0]
			array = point_data.GetArray(selected_array_name)
			print(
				"Scalar array '%s' not found; using '%s' instead." % (array_name, selected_array_name),
				file=sys.stderr,
			)
		else:
			raise RuntimeError(
				"Scalar array '%s' not found. Available arrays: <none>" % array_name
			)
	array_range = array.GetRange()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(poly)
	mapper.SetScalarModeToUsePointFieldData()
	mapper.SelectColorArray(selected_array_name)
	mapper.SetColorModeToMapScalars()
	if scalar_range:
		mapper.SetScalarRange(*scalar_range)
	else:
		mapper.SetScalarRange(EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
	if lookup_table is not None:
		mapper.SetLookupTable(lookup_table)
		mapper.UseLookupTableScalarRangeOn()
		if nan_color is not None and hasattr(lookup_table, "SetNanColor"):
			if len(nan_color) >= 3:
				lookup_table.SetNanColor(nan_color[0], nan_color[1], nan_color[2])
	mapper.ScalarVisibilityOn()
	if nan_color is not None and hasattr(mapper, "SetNanColor"):
		if len(nan_color) >= 3:
			mapper.SetNanColor(nan_color[0], nan_color[1], nan_color[2])
	return mapper, array_range, selected_array_name


def _build_actor(
	mapper: vtk.vtkPolyDataMapper,
	wireframe: bool,
	opacity: float,
	base_color: tuple[float, float, float] | None,
) -> vtk.vtkActor:
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	props = actor.GetProperty()
	props.SetAmbient(0.2)
	props.SetDiffuse(0.8)
	props.SetSpecular(0.3)
	props.SetSpecularPower(20.0)
	props.SetInterpolationToPhong()
	props.SetOpacity(max(0.0, min(opacity, 1.0)))
	if base_color is not None:
		props.SetColor(*base_color)
	if wireframe:
		props.SetRepresentationToWireframe()
	return actor


def _add_scalar_bar(
	renderer: vtk.vtkRenderer,
	lookup_table: vtk.vtkScalarsToColors,
	title: str,
	label_count: int,
):
	scalar_bar = vtk.vtkScalarBarActor()
	scalar_bar.SetLookupTable(lookup_table)
	scalar_bar.SetTitle(title)
	scalar_bar.GetLabelTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.GetTitleTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.SetNumberOfLabels(label_count)
	renderer.AddActor2D(scalar_bar)


def _attach_lut(mapper: vtk.vtkPolyDataMapper, transfer_function: vtk.vtkColorTransferFunction):
	mapper.SetLookupTable(transfer_function)
	mapper.UseLookupTableScalarRangeOn()


def _add_axes(renderer: vtk.vtkRenderer, length: float):
	axes = vtk.vtkAxesActor()
	axes.SetTotalLength(length, length, length)
	axes.SetShaftTypeToCylinder()
	axes.SetCylinderRadius(0.02)
	axes.SetConeRadius(0.1)
	axes.SetSphereRadius(0.15)
	renderer.AddActor(axes)


def _build_cut_plane_actor(origin: tuple[float, float, float], normal: tuple[float, float, float], size: float):
	normal_vec = _normalize(normal)
	if normal_vec == (0.0, 0.0, 0.0):
		return None
	reference = (0.0, 0.0, 1.0) if abs(normal_vec[2]) < 0.9 else (0.0, 1.0, 0.0)
	tangent = _normalize(_cross(normal_vec, reference))
	if tangent == (0.0, 0.0, 0.0):
		tangent = (1.0, 0.0, 0.0)
	bitangent = _normalize(_cross(normal_vec, tangent))
	extent = max(size, 1.0)
	half = extent * 0.5
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


def _build_neck_point_actor(point: tuple[float, float, float]):
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


def _print_summary(path: str, array_name: str, array_range: tuple[float, float], color_label: str):
	print("Loaded '%s'" % path)
	print("Using scalar array '%s' (range %.2f .. %.2f)" % (array_name, array_range[0], array_range[1]))
	print("Color mapping: %s" % color_label)


def main() -> int:
	args = _parse_args()
	poly = _load_polydata(args.vtp)

	needs_local = any([
		args.show_neck_point,
		args.show_cut_plane,
		args.gruen_zones,
		args.show_gruen_zones,
		bool(args.gruen_hu_zones),
	])
	if needs_local and not args.local_frame:
		raise RuntimeError("Local-frame options require --local-frame")

	neck_point = _parse_vector(args.neck_point) if args.neck_point else None
	cut_plane_origin = _parse_vector(args.cut_plane_origin) if args.cut_plane_origin else None
	cut_plane_normal = _parse_vector(args.cut_plane_normal) if args.cut_plane_normal else None
	base_color = _parse_vector(args.base_color) if args.base_color else None

	if args.local_frame and (neck_point is None or cut_plane_origin is None or cut_plane_normal is None):
		auto_neck, auto_origin, auto_normal, auto_side = _resolve_stem_annotation_defaults(
			args.vtp,
			args.seedplan,
			args.config_index,
		)
		if neck_point is None:
			neck_point = auto_neck
		if cut_plane_origin is None:
			cut_plane_origin = auto_origin
		if cut_plane_normal is None:
			cut_plane_normal = auto_normal
		if args.side == "auto" and auto_side:
			args.side = "left" if auto_side.strip().lower().startswith("l") else "right"

	if args.side == "left":
		if neck_point is not None:
			neck_point = (-neck_point[0], neck_point[1], neck_point[2])
		if cut_plane_origin is not None:
			cut_plane_origin = (-cut_plane_origin[0], cut_plane_origin[1], cut_plane_origin[2])
		if cut_plane_normal is not None:
			cut_plane_normal = (-cut_plane_normal[0], cut_plane_normal[1], cut_plane_normal[2])

	if args.show_neck_point and neck_point is None:
		raise RuntimeError("--show-neck-point requires --neck-point or a seedplan.xml")
	if args.show_cut_plane and (cut_plane_origin is None or cut_plane_normal is None):
		raise RuntimeError("--show-cut-plane requires cut plane inputs or a seedplan.xml")

	if args.gruen_zones or args.show_gruen_zones or args.gruen_hu_zones:
		_apply_gruen_zones(poly, neck_point, cut_plane_origin, cut_plane_normal, args.side)
		if args.print_gruen_stats:
			zone_array = poly.GetPointData().GetArray("GruenZone")
			if zone_array is not None:
				counts = {idx: 0 for idx in range(1, 15)}
				for idx in range(zone_array.GetNumberOfTuples()):
					zone_id = int(zone_array.GetTuple1(idx))
					if zone_id in counts:
						counts[zone_id] += 1
					print("Gruen zone counts:")
					for zone_id in sorted(counts):
						print(f"  Zone {zone_id}: {counts[zone_id]}")

	if args.gruen_hu_zones:
		metrics_array = _find_metrics_array_for_vtp(args.vtp)
		selected_hu_array = _pick_scalar_array(poly, args.hu_array)
		if selected_hu_array is None and metrics_array:
			selected_hu_array = _pick_scalar_array(poly, metrics_array)
		if selected_hu_array is None:
			raise RuntimeError("No scalar arrays available for HU masking")
		args.hu_array = selected_hu_array

	active_array = args.array
	color_label = "HU (EZplan LUT)"
	lookup_table: vtk.vtkScalarsToColors
	scalar_range: tuple[float, float]
	label_count = len(EZPLAN_ZONE_DEFS) + 1
	if args.gruen_hu_zones:
		zones = [int(item) for item in args.gruen_hu_zones.split(",") if item.strip()]
		if not zones:
			raise RuntimeError("--gruen-hu-zones must list at least one zone")
		active_array = _apply_hu_zone_mask(poly, args.hu_array, zones)
		lookup_table = _build_ezplan_transfer_function()
		scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
	elif args.show_gruen_zones:
		active_array = "GruenZone"
		lookup_table = _build_gruen_lookup_table()
		scalar_range = (1.0, 14.0)
		color_label = "Gruen zones"
		label_count = 14
	else:
		lookup_table = _build_ezplan_transfer_function()
		scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])

	use_scalar_overlay = True
	nan_color = None
	if args.gruen_hu_zones:
		if base_color is not None:
			nan_color = (base_color[0], base_color[1], base_color[2], 1.0)
		else:
			nan_color = (0.7, 0.7, 0.7, 1.0)

	mapper, array_range, active_array = _configure_mapper(
		poly,
		active_array,
		scalar_range=scalar_range,
		lookup_table=lookup_table,
		nan_color=nan_color,
	)
	actor = _build_actor(mapper, args.wireframe, args.opacity, base_color)
	base_actor = None
	if base_color is not None and use_scalar_overlay:
		base_mapper = vtk.vtkPolyDataMapper()
		base_mapper.SetInputData(poly)
		base_mapper.ScalarVisibilityOff()
		base_actor = _build_actor(base_mapper, args.wireframe, args.opacity, base_color)

	renderer = vtk.vtkRenderer()
	if base_actor is not None:
		renderer.AddActor(base_actor)
	renderer.AddActor(actor)
	renderer.SetBackground(1.0, 1.0, 1.0)
	renderer.ResetCamera()
	_add_scalar_bar(renderer, lookup_table, color_label, label_count)
	if args.show_axes:
		_add_axes(renderer, max(args.axes_size, 1.0))
	if args.show_neck_point and neck_point is not None:
		neck_actor = _build_neck_point_actor(neck_point)
		renderer.AddActor(neck_actor)
	if args.show_cut_plane and cut_plane_origin is not None and cut_plane_normal is not None:
		plane_actor = _build_cut_plane_actor(cut_plane_origin, cut_plane_normal, args.cut_plane_size)
		if plane_actor is not None:
			renderer.AddActor(plane_actor)

	render_window = vtk.vtkRenderWindow()
	render_window.SetWindowName("Stem Viewer (EZplan LUT)")
	render_window.AddRenderer(renderer)
	render_window.SetSize(900, 700)

	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)
	style = vtk.vtkInteractorStyleTrackballCamera()
	interactor.SetInteractorStyle(style)

	_print_summary(args.vtp, active_array, array_range, color_label)
	interactor.Initialize()
	render_window.Render()
	interactor.Start()
	return 0


if __name__ == "__main__":
	try:
		raise SystemExit(main())
	except RuntimeError as exc:
		print("Error:", exc)
		raise SystemExit(1)
