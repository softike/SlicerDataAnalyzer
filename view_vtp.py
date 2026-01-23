#!/usr/bin/env python3
"""Lightweight VTP viewer that mimics the EZplan LUT from load_nifti_and_stem."""

from __future__ import annotations

import argparse
import math
import os
import random
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
GRUEN_ZONE_ID_REMAP_LEFT = {
	1: 3,
	5: 2,
	9: 1,
	2: 5,
	6: 6,
	10: 7,
	3: 12,
	7: 13,
	11: 14,
	4: 10,
	8: 9,
	12: 8,
}
GRUEN_ZONE_ID_REMAP_RIGHT = {
	1: 5,
	5: 6,
	9: 7,
	2: 3,
	6: 2,
	10: 1,
	3: 12,
	7: 13,
	11: 14,
	4: 10,
	8: 9,
	12: 8,
}
DEFAULT_ARRAY = "VolumeScalars"
OFFSET_COLORS = (
	(1.0, 0.85, 0.1),
	(0.2, 0.75, 1.0),
	(0.9, 0.4, 0.4),
	(0.2, 0.9, 0.4),
	(0.95, 0.6, 0.1),
)


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"View a VTP stem file with the same EZplan HU LUT used by load_nifti_and_stem."
		)
	)
	parser.add_argument(
		"vtp",
		nargs="?",
		default=None,
		help="Path to the .vtp file exported from Slicer",
	)
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
		"--voxel-zones",
		action="store_true",
		help="Compute Gruen zones on a voxel shell around the surface for uniform sampling",
	)
	parser.add_argument(
		"--voxel-size",
		type=float,
		default=1.5,
		help="Voxel size (mm) for the surface shell (default: 1.5)",
	)
	parser.add_argument(
		"--voxel-shell",
		type=float,
		default=1.5,
		help="Shell thickness (mm) around the surface (default: 1.5)",
	)
	parser.add_argument(
		"--visible-voxels",
		action="store_true",
		help="Mask scalar display to voxels visible from standard camera views",
	)
	parser.add_argument(
		"--visibility-views",
		default="front,back,left,right",
		help="Comma-separated views for visibility masking (front,back,left,right)",
	)
	parser.add_argument(
		"--visibility-method",
		choices=("zbuffer", "hardware"),
		default="zbuffer",
		help="Visibility method (default: zbuffer)",
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
		"--show-tip-point",
		action="store_true",
		help="Render the tip point marker",
	)
	parser.add_argument(
		"--show-bottom-point",
		action="store_true",
		help="Render the bottom point marker",
	)
	parser.add_argument(
		"--show-offset",
		action="store_true",
		help="Render the default head-to-stem offset using head_to_stem_offset().",
	)
	parser.add_argument(
		"--show-junction-point",
		action="store_true",
		help="Render the junction between the neck-offset axis and the stem axis (from bottom).",
	)
	parser.add_argument(
		"--show-junction-axes",
		action="store_true",
		help="Render axes from head offset→junction and junction→bottom.",
	)
	parser.add_argument(
		"--offset-head",
		default="AUTO",
		help=(
			"Head enum name to use when computing the offset point (default: AUTO, "
			"uses HEAD_P0 or the first HEAD_UID)."
		),
	)
	parser.add_argument(
		"--show-all-offsets",
		action="store_true",
		help="Render every head-to-stem offset defined in HEAD_UIDS (if available).",
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
		"--largest-region-only",
		action="store_true",
		help="Keep only the largest connected region per Gruen zone",
	)
	parser.add_argument(
		"--composite-gruen",
		action="store_true",
		help="Use composite Gruen zones (1+7, 2+6, 3+5, 8+14, 9+13, 10+12)",
	)
	parser.add_argument(
		"--partitioned-gruen",
		action="store_true",
		help="Use partitioned Gruen zones (top, mediumtop, mediumbottom, bottom)",
	)
	parser.add_argument(
		"--gruen-remapped",
		action="store_true",
		help=(
			"Remap Gruen zone IDs using the alternate numbering "
			"(1→5, 2→3, 3→10, 4→12, 5→6, 6→2, 7→9, 8→13, 9→7, 10→1, 11→8, 12→14)"
		),
	)
	parser.add_argument(
		"--partitioned-gruen-viewports",
		action="store_true",
		help="Show 4 viewports for partitioned Gruen zones (top/mediumtop/mediumbottom/bottom)",
	)
	parser.add_argument(
		"--hu-range",
		help="Filter HU values to a named range: loosening, micromove, stable, cortical",
	)
	parser.add_argument(
		"--show-hu-summary",
		action="store_true",
		help="Display HU range percentage summary for the selected zone",
	)
	parser.add_argument(
		"--hu-table",
		action="store_true",
		help="Print a summary table of HU ranges and percentages",
	)
	parser.add_argument(
		"--dominant-hu-zone",
		help="Report the Gruen zone with the most values for a HU tag (loosening, micromove, stable, cortical)",
	)
	parser.add_argument(
		"--show-dominant-hu-zone",
		action="store_true",
		help="Display the dominant HU zone on screen",
	)
	parser.add_argument(
		"--highlight-dominant-hu-zone",
		action="store_true",
		help="Overlay the dominant HU zone on the surface",
	)
	parser.add_argument(
		"--headless",
		action="store_true",
		help="Run without opening a render window (for batch exports)",
	)
	parser.add_argument(
		"--export-hu-xml",
		action="store_true",
		help="Export HU tag summary per partitioned zone to XML in the VTP folder",
	)
	parser.add_argument(
		"--export-gruen-hu-xml",
		action="store_true",
		help="Export HU tag summary per Gruen zone to XML in the VTP folder",
	)
	parser.add_argument(
		"--gruen-hu-remesh",
		action="store_true",
		help="Use a remeshed surface (with interpolated scalars) for Gruen HU statistics",
	)
	parser.add_argument(
		"--gruen-hu-remesh-input",
		action="store_true",
		help="Use the input mesh as the remeshed surface for Gruen HU statistics",
	)
	parser.add_argument(
		"--envelope-gruen-input",
		action="store_true",
		help="Use the input mesh as the remeshed surface for envelope Gruen zones",
	)
	parser.add_argument(
		"--gruen-bottom-sphere-radius",
		type=float,
		default=0.0,
		help="Radius (mm) around the bottom point to use for Gruen zones 4/11 HU stats",
	)
	parser.add_argument(
		"--show-side-label",
		action="store_true",
		help="Display resolved side label in the render window",
	)
	parser.add_argument(
		"--show-axes",
		action="store_true",
		help="Display an XYZ axes frame in the scene",
	)
	parser.add_argument(
		"--show-normals",
		action="store_true",
		help="Visualize point normals as arrows",
	)
	parser.add_argument(
		"--normal-scale",
		type=float,
		default=5.0,
		help="Scale factor (mm) for normal glyphs (default: 5.0)",
	)
	parser.add_argument(
		"--remesh-iso",
		action="store_true",
		help="Remesh the surface to near-uniform triangle sizes using pyacvd",
	)
	parser.add_argument(
		"--remesh-target",
		type=int,
		default=30000,
		help="Target number of points for isotropic remesh (default: 30000)",
	)
	parser.add_argument(
		"--remesh-target-factor",
		type=float,
		default=1.0,
		help="Multiplier applied to remesh target (default: 1.0)",
	)
	parser.add_argument(
		"--remesh-subdivide",
		type=int,
		default=2,
		help="Number of pyacvd subdivisions before clustering (default: 2)",
	)
	parser.add_argument(
		"--batch-remesh-input",
		help=(
			"Root folder containing VTPs or STLs to remesh recursively. "
			"When set, runs batch remesh and skips viewer."
		),
	)
	parser.add_argument(
		"--batch-remesh-output",
		help="Destination root folder for remeshed VTPs (preserves subfolders).",
	)
	parser.add_argument(
		"--batch-remesh-glob",
		default="**/*.vtp",
		help="Glob pattern relative to input root (default: **/*.vtp)",
	)
	parser.add_argument(
		"--batch-remesh-overwrite",
		action="store_true",
		help="Overwrite existing outputs in batch remesh",
	)
	parser.add_argument(
		"--batch-remesh-verbose",
		action="store_true",
		help="Verbose progress output for batch remesh",
	)
	parser.add_argument(
		"--normal-ray-filter",
		action="store_true",
		help="Filter internal faces by ray-casting along cell normals",
	)
	parser.add_argument(
		"--normal-ray-length",
		type=float,
		default=0.0,
		help="Ray length for normal filtering (0 uses bbox diagonal)",
	)
	parser.add_argument(
		"--normal-ray-eps",
		type=float,
		default=0.1,
		help="Normal offset (mm) to avoid self-intersections (default: 0.1)",
	)
	parser.add_argument(
		"--normal-ray-auto-orient",
		action="store_true",
		help="Auto-orient normals before normal-ray filtering",
	)
	parser.add_argument(
		"--export-normal-ray-mesh",
		help="Write the normal-ray filtered mesh to this path",
	)
	parser.add_argument(
		"--batch-export-normal-ray",
		action="store_true",
		help="Export normal-ray filtered meshes alongside batch outputs",
	)
	parser.add_argument(
		"--pre-mc-fill-holes",
		action="store_true",
		help="Fill holes before implicit reconstruction",
	)
	parser.add_argument(
		"--pre-mc-hole-size",
		type=float,
		default=100.0,
		help="Maximum hole size (mm) to fill before implicit reconstruction (default: 100)",
	)
	parser.add_argument(
		"--show-convex-hull",
		action="store_true",
		help="Render the convex envelope of the stem (clipped to cut plane when available)",
	)
	parser.add_argument(
		"--convex-hull-only",
		action="store_true",
		help="Render only the convex envelope (hide the original mesh)",
	)
	parser.add_argument(
		"--convex-hull-mc",
		action="store_true",
		help="Reconstruct the convex envelope using implicit sampling + marching cubes",
	)
	parser.add_argument(
		"--convex-hull-mc-spacing",
		type=float,
		default=1.0,
		help="Voxel spacing (mm) for marching cubes reconstruction (default: 1.0)",
	)
	parser.add_argument(
		"--stem-mc",
		action="store_true",
		help="Reconstruct the stem surface using implicit sampling + marching cubes",
	)
	parser.add_argument(
		"--stem-mc-spacing",
		type=float,
		default=1.0,
		help="Voxel spacing (mm) for stem marching cubes reconstruction (default: 1.0)",
	)
	parser.add_argument(
		"--cache-remesh",
		action="store_true",
		help="Cache remeshed stem/envelope VTPs under the Slicer export folder",
	)
	parser.add_argument(
		"--cache-remesh-refresh",
		action="store_true",
		help="Force recompute remesh caches even if cache files exist",
	)
	parser.add_argument(
		"--stem-mc-hausdorff",
		action="store_true",
		help="Report Hausdorff-style distance stats between original and implicit-remeshed stem",
	)
	parser.add_argument(
		"--stem-mc-hausdorff-sweep",
		default=None,
		help=(
			"Sweep spacing to see convergence, format: start,end,steps (e.g., 2.0,0.4,6)"
		),
	)
	parser.add_argument(
		"--envelope-gruen",
		action="store_true",
		help=(
			"Compute envelope-based Gruen zones using a rectangular box split along Z (40/40/20)"
		),
	)
	parser.add_argument(
		"--envelope-gruen-mode",
		choices=("position", "normal"),
		default="position",
		help="Side assignment for envelope zones: position or normal (default: position)",
	)
	parser.add_argument(
		"--envelope-z-bands",
		default="0.4,0.4,0.2",
		help="Z band fractions for envelope zones (default: 0.4,0.4,0.2)",
	)
	parser.add_argument(
		"--show-envelope-gruen",
		action="store_true",
		help="Display the envelope-based Gruen zones",
	)
	parser.add_argument(
		"--envelope-hu",
		action="store_true",
		help="Show HU scalar values masked by the envelope zones (uses --zone-only)",
	)
	parser.add_argument(
		"--envelope-hu-viewports",
		action="store_true",
		help="Show two viewports: full HU and envelope-zone HU (requires --zone-only)",
	)
	parser.add_argument(
		"--envelope-hu-cortical",
		action="store_true",
		help="In envelope HU viewports, auto-select zones containing cortical HU (1000-1500)",
	)
	parser.add_argument(
		"--envelope-hu-stable",
		action="store_true",
		help="In envelope HU viewports, auto-select zones containing stable HU (400-1000)",
	)
	parser.add_argument(
		"--envelope-top-zones",
		type=int,
		default=None,
		help="Show only the N largest envelope zones (by point count)",
	)
	parser.add_argument(
		"--show-envelope-contours",
		action="store_true",
		help="Overlay zone contour lines for envelope-based Gruen zones",
	)
	parser.add_argument(
		"--show-zone-contours",
		action="store_true",
		help="Overlay solid contour lines to delineate zone boundaries",
	)
	parser.add_argument(
		"--solid-zones",
		action="store_true",
		help="Render zone colors fully opaque (ignores --opacity for zone views)",
	)
	parser.add_argument(
		"--zone-only",
		type=int,
		default=None,
		help="Show only a specific zone id for the active zone view",
	)
	parser.add_argument(
		"--merge-zone-islands",
		action="store_true",
		help="Merge small isolated zone islands into the surrounding dominant zone",
	)
	parser.add_argument(
		"--merge-zone-min-points",
		type=int,
		default=200,
		help="Minimum island size to keep as its own zone (default: 200 points)",
	)
	parser.add_argument(
		"--convex-hull-opacity",
		type=float,
		default=0.25,
		help="Opacity for convex envelope overlay (default: 0.25)",
	)
	parser.add_argument(
		"--convex-hull-color",
		default="0.2,0.2,0.2",
		help="Convex envelope color as r,g,b (default: 0.2,0.2,0.2)",
	)
	parser.add_argument(
		"--rotate-z-180",
		action="store_true",
		help="Force rotate the stem and annotations 180° around Z (auto-applied for left side)",
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


def _load_polydata_any(path: str) -> vtk.vtkPolyData:
	if not os.path.isfile(path):
		raise FileNotFoundError(path)
	suffix = Path(path).suffix.lower()
	if suffix == ".vtp":
		return _load_polydata(path)
	if suffix == ".stl":
		reader = vtk.vtkSTLReader()
		reader.SetFileName(path)
		reader.Update()
		poly = reader.GetOutput()
		if not poly or poly.GetNumberOfPoints() == 0:
			raise RuntimeError("STL file '%s' produced empty polydata" % path)
		return poly
	raise RuntimeError(f"Unsupported mesh format: {suffix}")


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
 	object | None,
 	object | None,
]:
	seedplan_path, inferred_index, inferred_side = _find_seedplan_for_vtp(vtp_path, seedplan)
	if config_index is None:
		config_index = inferred_index
	if seedplan_path is None or not seedplan_path.exists():
		return None, None, None, inferred_side, None, None
	try:
		stem_infos = _extract_stem_infos(seedplan_path)
	except Exception:
		return None, None, None, inferred_side, None, None
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
		return None, None, None, inferred_side, None, None
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
	return neck_point, cut_origin, cut_normal, inferred_side, module, uid_member


def _build_ezplan_transfer_function() -> vtk.vtkColorTransferFunction:
	tf = vtk.vtkColorTransferFunction()
	for zone_min, zone_max, (r, g, b), _label in EZPLAN_ZONE_DEFS:
		tf.AddRGBPoint(zone_min, r, g, b)
		tf.AddRGBPoint(zone_max, r, g, b)
	return tf


def _build_gruen_lookup_table() -> vtk.vtkLookupTable:
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfTableValues(15)
	lut.SetRange(1.0, 14.0)
	lut.Build()
	rng = random.Random(42)
	colors = [(0.6, 0.6, 0.6)]
	for _ in range(14):
		colors.append((rng.random(), rng.random(), rng.random()))
	# Ensure zones 5 and 6 are clearly distinct.
	colors[5] = (0.95, 0.15, 0.15)
	colors[6] = (0.15, 0.15, 0.95)
	for idx, (r, g, b) in enumerate(colors):
		lut.SetTableValue(idx, r, g, b, 1.0)
	return lut


def _build_partition_lookup_table() -> vtk.vtkLookupTable:
	lut = vtk.vtkLookupTable()
	lut.SetNumberOfTableValues(5)
	lut.SetRange(1.0, 4.0)
	lut.Build()
	colors = [
		(0.6, 0.6, 0.6),
		(0.2, 0.6, 1.0),
		(0.2, 0.8, 0.2),
		(0.9, 0.7, 0.2),
		(0.8, 0.2, 0.2),
	]
	for idx in range(5):
		r, g, b = colors[idx]
		lut.SetTableValue(idx, r, g, b, 1.0)
	return lut


def _parse_vector(value: str) -> tuple[float, float, float]:
	parts = [item.strip() for item in value.split(",") if item.strip()]
	if len(parts) != 3:
		raise ValueError("Expected vector as 'x,y,z'")
	return (float(parts[0]), float(parts[1]), float(parts[2]))


def _coerce_point(value: object) -> tuple[float, float, float]:
	try:
		return (float(value[0]), float(value[1]), float(value[2]))
	except Exception as exc:
		raise ValueError("Invalid point") from exc


def _vec_add(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
	return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_sub(a: tuple[float, float, float], b: tuple[float, float, float]) -> tuple[float, float, float]:
	return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_scale(a: tuple[float, float, float], scale: float) -> tuple[float, float, float]:
	return (a[0] * scale, a[1] * scale, a[2] * scale)


def _normalize(vec: tuple[float, float, float]) -> tuple[float, float, float]:
	x, y, z = vec
	length = (x * x + y * y + z * z) ** 0.5
	if length <= 1e-6:
		return (0.0, 0.0, 0.0)
	return (x / length, y / length, z / length)




def _rotate_z_point(point: tuple[float, float, float] | None, degrees: float) -> tuple[float, float, float] | None:
	if point is None:
		return None
	rad = math.radians(degrees)
	cos_v = math.cos(rad)
	sin_v = math.sin(rad)
	x, y, z = point
	return (x * cos_v - y * sin_v, x * sin_v + y * cos_v, z)


def _rotate_z_vector(vec: tuple[float, float, float] | None, degrees: float) -> tuple[float, float, float] | None:
	if vec is None:
		return None
	rad = math.radians(degrees)
	cos_v = math.cos(rad)
	sin_v = math.sin(rad)
	x, y, z = vec
	return _normalize((x * cos_v - y * sin_v, x * sin_v + y * cos_v, z))


def _rotate_x_point(point: tuple[float, float, float] | None, degrees: float) -> tuple[float, float, float] | None:
	if point is None:
		return None
	rad = math.radians(degrees)
	cos_v = math.cos(rad)
	sin_v = math.sin(rad)
	x, y, z = point
	return (x, y * cos_v - z * sin_v, y * sin_v + z * cos_v)


def _rotate_x_vector(vec: tuple[float, float, float] | None, degrees: float) -> tuple[float, float, float] | None:
	if vec is None:
		return None
	rad = math.radians(degrees)
	cos_v = math.cos(rad)
	sin_v = math.sin(rad)
	x, y, z = vec
	return _normalize((x, y * cos_v - z * sin_v, y * sin_v + z * cos_v))


def _rotate_x_180_point(point: tuple[float, float, float] | None) -> tuple[float, float, float] | None:
	if point is None:
		return None
	x, y, z = point
	return (x, -y, -z)


def _rotate_y_180_point(point: tuple[float, float, float] | None) -> tuple[float, float, float] | None:
	if point is None:
		return None
	x, y, z = point
	return (-x, y, -z)


def _rotate_y_180_vector(vec: tuple[float, float, float] | None) -> tuple[float, float, float] | None:
	if vec is None:
		return None
	x, y, z = vec
	return _normalize((-x, y, -z))


def _vector_length(vec: tuple[float, float, float]) -> float:
	return (vec[0] * vec[0] + vec[1] * vec[1] + vec[2] * vec[2]) ** 0.5


def _dot(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _closest_points_between_lines(
	point1: tuple[float, float, float],
	dir1: tuple[float, float, float],
	point2: tuple[float, float, float],
	dir2: tuple[float, float, float],
) -> tuple[tuple[float, float, float], tuple[float, float, float]] | None:
	d1 = _normalize(dir1)
	d2 = _normalize(dir2)
	if _vector_length(d1) <= 1e-6 or _vector_length(d2) <= 1e-6:
		return None
	r = _vec_sub(point1, point2)
	a = _dot(d1, d1)
	e = _dot(d2, d2)
	b = _dot(d1, d2)
	c = _dot(d1, r)
	f = _dot(d2, r)
	denom = a * e - b * b
	if abs(denom) <= 1e-6:
		return None
	s = (b * f - c * e) / denom
	t = (a * f - b * c) / denom
	p1 = _vec_add(point1, _vec_scale(d1, s))
	p2 = _vec_add(point2, _vec_scale(d2, t))
	return p1, p2


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


def _compute_tip_bottom_points(
	poly: vtk.vtkPolyData,
	neck_point: tuple[float, float, float] | None,
) -> tuple[tuple[float, float, float] | None, tuple[float, float, float] | None]:
	points = poly.GetPoints()
	if points is None:
		return None, None
	count = points.GetNumberOfPoints()
	if count == 0:
		return None, None
	axis_dir, _mean = _compute_principal_axis(poly)
	min_proj = float("inf")
	max_proj = float("-inf")
	min_point = None
	max_point = None
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		proj = _dot((x, y, z), axis_dir)
		if proj < min_proj:
			min_proj = proj
			min_point = (x, y, z)
		if proj > max_proj:
			max_proj = proj
			max_point = (x, y, z)
	if min_point is None or max_point is None:
		return None, None
	if neck_point is not None:
		neck_proj = _dot(neck_point, axis_dir)
		if abs(neck_proj - min_proj) < abs(neck_proj - max_proj):
			return min_point, max_point
	return max_point, min_point


def _apply_side_rotation_point(
	point: tuple[float, float, float] | None,
	side: str,
	rotate_z_180: bool,
) -> tuple[float, float, float] | None:
	if point is None:
		return None
	x, y, z = point
	if side == "left":
		x = -x
	elif side == "right":
		x = -x
		y = -y
	if rotate_z_180:
		x = -x
		y = -y
	return (x, y, z)


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
	cut_plane_mode: str = "below",
) -> str:
	axis_dir, mean = _compute_principal_axis(poly)
	point_data = poly.GetPointData()
	normals = point_data.GetNormals()
	if normals is None:
		normals = point_data.GetArray("Normals")
	if normals is None:
		normals_filter = vtk.vtkPolyDataNormals()
		normals_filter.SetInputData(poly)
		normals_filter.ComputePointNormalsOn()
		normals_filter.ComputeCellNormalsOff()
		normals_filter.SplittingOff()
		normals_filter.ConsistencyOn()
		normals_filter.AutoOrientNormalsOn()
		normals_filter.Update()
		normals_output = normals_filter.GetOutput()
		computed = normals_output.GetPointData().GetNormals()
		if computed is not None:
			point_data.AddArray(computed)
			point_data.SetNormals(computed)
			normals = computed
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
	bottom_point, _tip = _compute_tip_bottom_points(poly, neck_point)
	if bottom_point is not None and neck_point is not None:
		bottom_proj = axis_dir[0] * bottom_point[0] + axis_dir[1] * bottom_point[1] + axis_dir[2] * bottom_point[2]
		neck_proj = axis_dir[0] * neck_point[0] + axis_dir[1] * neck_point[1] + axis_dir[2] * neck_point[2]
		min_proj = bottom_proj
		max_proj = neck_proj
		if max_proj < min_proj:
			min_proj, max_proj = max_proj, min_proj
			axis_dir = (-axis_dir[0], -axis_dir[1], -axis_dir[2])
	if cut_plane_origin is not None and cut_plane_normal is not None:
		cut_proj = axis_dir[0] * cut_plane_origin[0] + axis_dir[1] * cut_plane_origin[1] + axis_dir[2] * cut_plane_origin[2]
		neck_side = None
		if neck_point is not None:
			neck_side = (
				(neck_point[0] - cut_plane_origin[0]) * cut_plane_normal[0]
				+ (neck_point[1] - cut_plane_origin[1]) * cut_plane_normal[1]
				+ (neck_point[2] - cut_plane_origin[2]) * cut_plane_normal[2]
			)
		def _is_below_plane(sign: float) -> bool:
			if neck_side is None or abs(neck_side) < 1e-6:
				return sign <= 0.0
			return sign <= 0.0 if neck_side > 0.0 else sign >= 0.0
		keep_below = cut_plane_mode != "above"
		filtered_min = float("inf")
		filtered_max = float("-inf")
		found = False
		for idx in range(count):
			x, y, z = points.GetPoint(idx)
			plane_sign = (
				(x - cut_plane_origin[0]) * cut_plane_normal[0]
				+ (y - cut_plane_origin[1]) * cut_plane_normal[1]
				+ (z - cut_plane_origin[2]) * cut_plane_normal[2]
			)
			is_below = _is_below_plane(plane_sign)
			if keep_below != is_below:
				continue
			proj = axis_dir[0] * x + axis_dir[1] * y + axis_dir[2] * z
			filtered_min = min(filtered_min, proj)
			filtered_max = max(filtered_max, proj)
			found = True
		if found:
			min_proj, max_proj = filtered_min, filtered_max
		if cut_plane_mode == "above":
			min_proj = cut_proj
		else:
			max_proj = cut_proj
		align = (
			axis_dir[0] * cut_plane_normal[0]
			+ axis_dir[1] * cut_plane_normal[1]
			+ axis_dir[2] * cut_plane_normal[2]
		)
		want_positive = cut_plane_mode == "above"
		if (align > 0 and not want_positive) or (align < 0 and want_positive):
			axis_dir = (-axis_dir[0], -axis_dir[1], -axis_dir[2])
			min_proj, max_proj = -max_proj, -min_proj
	axis_len = max(max_proj - min_proj, 1e-6)
	x_axis = (1.0, 0.0, 0.0)
	if side == "right":
		x_axis = (-1.0, 0.0, 0.0)
	y_axis = (0.0, 1.0, 0.0)
	zones = vtk.vtkIntArray()
	zones.SetName("GruenZone")
	zones.SetNumberOfComponents(1)
	zones.SetNumberOfTuples(count)
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		if normals is not None:
			nx, ny, nz = normals.GetTuple(idx)
			to_point = (x - mean[0], y - mean[1], z - mean[2])
			if _dot((nx, ny, nz), to_point) < 0:
				nx, ny, nz = -nx, -ny, -nz
			norm_len = (nx * nx + ny * ny + nz * nz) ** 0.5
			if norm_len > 1e-6:
				nx, ny, nz = nx / norm_len, ny / norm_len, nz / norm_len
			xp = _dot((nx, ny, nz), x_axis)
			yp = _dot((nx, ny, nz), y_axis)
		else:
			to_point = (x - mean[0], y - mean[1], z - mean[2])
			to_point = _normalize(to_point)
			xp = _dot(to_point, x_axis)
			yp = _dot(to_point, y_axis)
		zproj = _dot((x, y, z), axis_dir)
		z_norm = (zproj - min_proj) / axis_len
		if abs(xp) >= abs(yp):
			group = "lateral" if xp <= 0 else "medial"
		else:
			if side == "right":
				group = "anterior" if yp <= 0 else "posterior"
			else:
				group = "anterior" if yp >= 0 else "posterior"
		if side == "right" and group in ("lateral", "medial"):
			group = "medial" if group == "lateral" else "lateral"
		zones.SetTuple1(idx, float(_compute_gruen_zone(z_norm, group)))
	point_data = poly.GetPointData()
	if point_data.GetArray("GruenZone"):
		point_data.RemoveArray("GruenZone")
	point_data.AddArray(zones)
	point_data.SetActiveScalars("GruenZone")
	poly.Modified()
	return "GruenZone"


def _build_envelope_lookup_table() -> vtk.vtkLookupTable:
	lookup = vtk.vtkLookupTable()
	lookup.SetNumberOfTableValues(12)
	lookup.SetRange(1.0, 12.0)
	colors = [
		(0.2, 0.6, 1.0), (0.2, 0.8, 0.2), (0.9, 0.7, 0.2), (0.8, 0.2, 0.2),
		(0.6, 0.2, 0.8), (0.2, 0.7, 0.7), (0.9, 0.4, 0.8), (0.4, 0.4, 0.9),
		(0.6, 0.6, 0.2), (0.3, 0.7, 0.3), (0.7, 0.3, 0.3), (0.3, 0.3, 0.7),
	]
	for idx, color in enumerate(colors):
		lookup.SetTableValue(idx, color[0], color[1], color[2], 1.0)
	lookup.Build()
	return lookup


def _apply_envelope_gruen_zones(
	poly: vtk.vtkPolyData,
	cut_plane_origin: tuple[float, float, float] | None,
	cut_plane_normal: tuple[float, float, float] | None,
	neck_point: tuple[float, float, float] | None = None,
	mode: str = "position",
	band_fractions: tuple[float, float, float] = (0.4, 0.4, 0.2),
) -> str:
	points = poly.GetPoints()
	if points is None:
		raise RuntimeError("Polydata has no points")
	count = points.GetNumberOfPoints()
	if count == 0:
		raise RuntimeError("Polydata has no points")
	bounds = poly.GetBounds()
	min_x, max_x, min_y, max_y, min_z, max_z = bounds
	center_x = (min_x + max_x) * 0.5
	center_y = (min_y + max_y) * 0.5
	height = max(max_z - min_z, 1e-6)
	f1, f2, f3 = band_fractions
	if f1 <= 0 or f2 <= 0 or f3 <= 0:
		f1, f2, f3 = (0.4, 0.4, 0.2)
	sum_f = f1 + f2 + f3
	if sum_f <= 1e-6:
		f1, f2, f3 = (0.4, 0.4, 0.2)
		sum_f = 1.0
	band_1 = min_z + height * (f1 / sum_f)
	band_2 = min_z + height * ((f1 + f2) / sum_f)
	normals = None
	if mode == "normal":
		normals = _ensure_point_normals(poly)
		if normals is None:
			raise RuntimeError("Envelope zones (normal mode) require point normals")
	zones = vtk.vtkDoubleArray()
	zones.SetName("EnvelopeZone")
	zones.SetNumberOfComponents(1)
	zones.SetNumberOfTuples(count)
	neck_side = None
	if cut_plane_origin is not None and cut_plane_normal is not None and neck_point is not None:
		neck_side = (
			(neck_point[0] - cut_plane_origin[0]) * cut_plane_normal[0]
			+ (neck_point[1] - cut_plane_origin[1]) * cut_plane_normal[1]
			+ (neck_point[2] - cut_plane_origin[2]) * cut_plane_normal[2]
		)
	def _is_below_plane(sign: float) -> bool:
		if neck_side is None or abs(neck_side) < 1e-6:
			return sign <= 0.0
		return sign <= 0.0 if neck_side > 0.0 else sign >= 0.0
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		if cut_plane_origin is not None and cut_plane_normal is not None:
			dx = x - cut_plane_origin[0]
			dy = y - cut_plane_origin[1]
			dz = z - cut_plane_origin[2]
			plane_sign = dx * cut_plane_normal[0] + dy * cut_plane_normal[1] + dz * cut_plane_normal[2]
			if not _is_below_plane(plane_sign):
				zones.SetTuple1(idx, float("nan"))
				continue
		if z <= band_1:
			band = 0
		elif z <= band_2:
			band = 1
		else:
			band = 2
		if mode == "normal":
			nx, ny, _nz = normals.GetTuple(idx)
			if abs(nx) >= abs(ny):
				face = 0 if nx >= 0 else 1
			else:
				face = 2 if ny >= 0 else 3
		else:
			dx = x - center_x
			dy = y - center_y
			if abs(dx) >= abs(dy):
				face = 0 if dx >= 0 else 1
			else:
				face = 2 if dy >= 0 else 3
		zone_id = band * 4 + face + 1
		zones.SetTuple1(idx, float(zone_id))
	point_data = poly.GetPointData()
	if point_data.GetArray("EnvelopeZone"):
		point_data.RemoveArray("EnvelopeZone")
	point_data.AddArray(zones)
	point_data.SetActiveScalars("EnvelopeZone")
	poly.Modified()
	return "EnvelopeZone"


def _apply_gruen_zone_remap(
	poly: vtk.vtkPolyData,
	array_name: str,
	output_name: str,
	side: str,
) -> str:
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray(array_name)
	if zone_array is None:
		raise RuntimeError(f"Zone array '{array_name}' not found")
	remap_table = GRUEN_ZONE_ID_REMAP_RIGHT if side == "right" else GRUEN_ZONE_ID_REMAP_LEFT
	remapped = vtk.vtkIntArray()
	remapped.SetName(output_name)
	remapped.SetNumberOfComponents(1)
	remapped.SetNumberOfTuples(zone_array.GetNumberOfTuples())
	for idx in range(zone_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			remapped.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_value)
		remapped_id = remap_table.get(zone_id, zone_id)
		remapped.SetTuple1(idx, remapped_id)
	if point_data.GetArray(output_name):
		point_data.RemoveArray(output_name)
	point_data.AddArray(remapped)
	point_data.SetActiveScalars(output_name)
	poly.Modified()
	return output_name


def _apply_top_envelope_zones(poly: vtk.vtkPolyData, top_n: int) -> str:
	if top_n <= 0:
		return "EnvelopeZone"
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray("EnvelopeZone")
	if zone_array is None:
		raise RuntimeError("EnvelopeZone array missing")
	counts = {idx: 0 for idx in range(1, 13)}
	for idx in range(zone_array.GetNumberOfTuples()):
		zone_val = zone_array.GetTuple1(idx)
		if zone_val != zone_val:
			continue
		zone_id = int(zone_val)
		if zone_id in counts:
			counts[zone_id] += 1
	ordered = sorted(counts.items(), key=lambda item: item[1], reverse=True)
	keep_ids = {zone_id for zone_id, _count in ordered[:top_n]}
	masked = vtk.vtkDoubleArray()
	masked.SetName("EnvelopeZoneTop")
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(zone_array.GetNumberOfTuples())
	for idx in range(zone_array.GetNumberOfTuples()):
		zone_val = zone_array.GetTuple1(idx)
		if zone_val != zone_val:
			masked.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_val)
		if zone_id in keep_ids:
			masked.SetTuple1(idx, float(zone_id))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray("EnvelopeZoneTop"):
		point_data.RemoveArray("EnvelopeZoneTop")
	point_data.AddArray(masked)
	point_data.SetActiveScalars("EnvelopeZoneTop")
	poly.Modified()
	return "EnvelopeZoneTop"


def _apply_zone_only(poly: vtk.vtkPolyData, array_name: str, zone_id: int) -> str:
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray(array_name)
	if zone_array is None:
		raise RuntimeError(f"Zone array '{array_name}' not found")
	masked_name = f"{array_name}_Only"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(zone_array.GetNumberOfTuples())
	for idx in range(zone_array.GetNumberOfTuples()):
		value = zone_array.GetTuple1(idx)
		if value != value or int(value) != zone_id:
			masked.SetTuple1(idx, float("nan"))
		else:
			masked.SetTuple1(idx, float(zone_id))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _count_zone_ids(array: vtk.vtkDataArray) -> tuple[int, dict[int, int]]:
	counts: dict[int, int] = {}
	for idx in range(array.GetNumberOfTuples()):
		value = array.GetTuple1(idx)
		if value != value:
			continue
		zone_id = int(value)
		counts[zone_id] = counts.get(zone_id, 0) + 1
	return len(counts), counts


def _merge_zone_islands(
	poly: vtk.vtkPolyData,
	array_name: str,
	min_points: int,
) -> str:
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray(array_name)
	if zone_array is None:
		raise RuntimeError(f"Zone array '{array_name}' not found")
	if min_points <= 0:
		return array_name
	point_count = poly.GetNumberOfPoints()
	neighbors: list[list[int]] = [[] for _ in range(point_count)]
	cells = poly.GetPolys()
	if cells is None:
		return array_name
	cells.InitTraversal()
	ids = vtk.vtkIdList()
	while cells.GetNextCell(ids):
		cell_ids = [ids.GetId(i) for i in range(ids.GetNumberOfIds())]
		for i in range(len(cell_ids)):
			pid = cell_ids[i]
			for j in range(len(cell_ids)):
				if i == j:
					continue
				neighbors[pid].append(cell_ids[j])
	visited = [False] * point_count
	new_array = vtk.vtkDoubleArray()
	new_array.DeepCopy(zone_array)
	new_array.SetName(f"{array_name}Merged")
	for start in range(point_count):
		val = zone_array.GetTuple1(start)
		if val != val:
			continue
		zone_id = int(val)
		if visited[start]:
			continue
		stack = [start]
		component: list[int] = []
		visited[start] = True
		while stack:
			pid = stack.pop()
			component.append(pid)
			for nbr in neighbors[pid]:
				if visited[nbr]:
					continue
				val_n = zone_array.GetTuple1(nbr)
				if val_n != val_n or int(val_n) != zone_id:
					continue
				visited[nbr] = True
				stack.append(nbr)
		if len(component) >= min_points:
			continue
		neighbor_counts: dict[int, int] = {}
		for pid in component:
			for nbr in neighbors[pid]:
				val_n = zone_array.GetTuple1(nbr)
				if val_n != val_n:
					continue
				neighbor_id = int(val_n)
				if neighbor_id == zone_id:
					continue
				neighbor_counts[neighbor_id] = neighbor_counts.get(neighbor_id, 0) + 1
		if not neighbor_counts:
			continue
		replace_id = max(neighbor_counts.items(), key=lambda item: item[1])[0]
		for pid in component:
			new_array.SetTuple1(pid, float(replace_id))
	if point_data.GetArray(new_array.GetName()):
		point_data.RemoveArray(new_array.GetName())
	point_data.AddArray(new_array)
	point_data.SetActiveScalars(new_array.GetName())
	poly.Modified()
	return new_array.GetName()


def _build_zone_contours_actor(
	poly: vtk.vtkPolyData,
	array_name: str,
	max_zone: int,
	color: tuple[float, float, float] = (0.1, 0.1, 0.1),
	radius: float = 0.4,
) -> vtk.vtkActor | None:
	point_data = poly.GetPointData()
	array = point_data.GetArray(array_name)
	if array is None:
		return None
	contour = vtk.vtkContourFilter()
	contour.SetInputData(poly)
	contour.SetInputArrayToProcess(
		0,
		0,
		0,
		vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
		array_name,
	)
	for idx in range(1, max_zone):
		contour.SetValue(idx - 1, idx + 0.5)
	contour.Update()
	if contour.GetOutput().GetNumberOfPoints() == 0:
		return None
	tube = vtk.vtkTubeFilter()
	tube.SetInputConnection(contour.GetOutputPort())
	tube.SetRadius(max(radius, 0.05))
	tube.SetNumberOfSides(12)
	tube.CappingOn()
	tube.Update()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(tube.GetOutputPort())
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(*color)
	actor.GetProperty().SetOpacity(0.9)
	return actor


def _apply_hu_zone_mask(poly: vtk.vtkPolyData, hu_array: str, zones: list[int]) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(hu_array)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array)
	zone_array = (
		point_data.GetArray("GruenZonePartition")
		or point_data.GetArray("GruenZoneComposite")
		or point_data.GetArray("GruenZoneLargest")
		or point_data.GetArray("GruenZone")
	)
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	keep_array = point_data.GetArray("GruenZoneKeep")
	masked_name = f"{hu_array}_Gruen"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	allowed = set(zones)
	for idx in range(source_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			masked.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_value)
		keep_ok = True
		if keep_array is not None:
			keep_ok = int(keep_array.GetTuple1(idx)) == 1
		if keep_ok and zone_id in allowed:
			masked.SetTuple1(idx, source_array.GetTuple1(idx))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _apply_hu_zone_mask_by_array(
	poly: vtk.vtkPolyData,
	hu_array: str,
	zone_array_name: str,
	zones: list[int],
) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(hu_array)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array)
	zone_array = point_data.GetArray(zone_array_name)
	if zone_array is None:
		raise RuntimeError("Zone array '%s' not found" % zone_array_name)
	masked_name = f"{hu_array}_{zone_array_name}"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	allowed = set(zones)
	for idx in range(source_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			masked.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_value)
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


def _apply_hu_presence_mask_by_array(
	poly: vtk.vtkPolyData,
	hu_array: str,
	zone_array_name: str,
) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(hu_array)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array)
	zone_array = point_data.GetArray(zone_array_name)
	if zone_array is None:
		raise RuntimeError("Zone array '%s' not found" % zone_array_name)
	masked_name = f"{hu_array}_{zone_array_name}_All"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	for idx in range(source_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			masked.SetTuple1(idx, float("nan"))
			continue
		masked.SetTuple1(idx, source_array.GetTuple1(idx))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _find_zones_with_hu_range_by_array(
	poly: vtk.vtkPolyData,
	hu_array_name: str,
	zone_array_name: str,
	hu_range: tuple[float, float],
) -> list[int]:
	point_data = poly.GetPointData()
	hu_array = point_data.GetArray(hu_array_name)
	if hu_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array_name)
	zone_array = point_data.GetArray(zone_array_name)
	if zone_array is None:
		raise RuntimeError("Zone array '%s' not found" % zone_array_name)
	low, high = hu_range
	zones_with_range: set[int] = set()
	for idx in range(hu_array.GetNumberOfTuples()):
		value = hu_array.GetTuple1(idx)
		if value != value:
			continue
		if not (low <= value <= high):
			continue
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			continue
		zones_with_range.add(int(zone_value))
	return sorted(zones_with_range)

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
	position_x: float | None = None,
	position_y: float | None = None,
	title_separation: int | None = None,
):
	scalar_bar = vtk.vtkScalarBarActor()
	scalar_bar.SetLookupTable(lookup_table)
	scalar_bar.SetTitle(title)
	scalar_bar.GetLabelTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.GetTitleTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.SetLabelFormat(" %.0f")
	scalar_bar.SetNumberOfLabels(label_count)
	if position_x is not None or position_y is not None:
		scalar_bar.SetPosition(position_x if position_x is not None else 0.90, position_y if position_y is not None else 0.05)
	if title_separation is not None and hasattr(scalar_bar, "SetVerticalTitleSeparation"):
		scalar_bar.SetVerticalTitleSeparation(title_separation)
	if hasattr(scalar_bar, "SetTextPad"):
		scalar_bar.SetTextPad(6)
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


def _build_tip_point_actor(point: tuple[float, float, float]):
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


def _build_bottom_point_actor(point: tuple[float, float, float]):
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


def _build_offset_actor(point: tuple[float, float, float], color: tuple[float, float, float]):
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


def _build_junction_actor(point: tuple[float, float, float]):
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


def _build_line_actor(
	start: tuple[float, float, float],
	end: tuple[float, float, float],
	color: tuple[float, float, float] = (0.2, 0.2, 0.2),
	radius: float = 0.6,
) -> vtk.vtkActor:
	line = vtk.vtkLineSource()
	line.SetPoint1(*start)
	line.SetPoint2(*end)
	line.Update()
	tube = vtk.vtkTubeFilter()
	tube.SetInputConnection(line.GetOutputPort())
	tube.SetRadius(max(radius, 0.1))
	tube.SetNumberOfSides(18)
	tube.CappingOn()
	tube.Update()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(tube.GetOutputPort())
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(*color)
	actor.GetProperty().SetOpacity(1.0)
	return actor


def _ensure_point_normals(poly: vtk.vtkPolyData) -> vtk.vtkDataArray | None:
	point_data = poly.GetPointData()
	normals = point_data.GetNormals()
	if normals is None:
		normals = point_data.GetArray("Normals")
	if normals is None:
		normals_filter = vtk.vtkPolyDataNormals()
		normals_filter.SetInputData(poly)
		normals_filter.ComputePointNormalsOn()
		normals_filter.ComputeCellNormalsOff()
		normals_filter.SplittingOff()
		normals_filter.ConsistencyOn()
		normals_filter.AutoOrientNormalsOn()
		normals_filter.Update()
		output = normals_filter.GetOutput()
		computed = output.GetPointData().GetNormals()
		if computed is not None:
			point_data.AddArray(computed)
			point_data.SetNormals(computed)
			normals = computed
	return normals


def _build_normals_actor(poly: vtk.vtkPolyData, scale: float) -> vtk.vtkActor | None:
	if scale <= 0:
		return None
	normals = _ensure_point_normals(poly)
	if normals is None:
		return None
	arrow = vtk.vtkArrowSource()
	arrow.SetTipLength(0.25)
	arrow.SetTipRadius(0.1)
	arrow.SetShaftRadius(0.03)
	arrow.Update()
	glyph = vtk.vtkGlyph3D()
	glyph.SetInputData(poly)
	glyph.SetSourceConnection(arrow.GetOutputPort())
	glyph.SetVectorModeToUseNormal()
	glyph.OrientOn()
	glyph.ScalingOff()
	glyph.SetScaleFactor(scale)
	glyph.Update()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputConnection(glyph.GetOutputPort())
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(0.2, 0.2, 0.2)
	actor.GetProperty().SetOpacity(0.9)
	return actor


def _clip_poly_by_plane(
	poly: vtk.vtkPolyData,
	origin: tuple[float, float, float],
	normal: tuple[float, float, float],
) -> vtk.vtkPolyData:
	plane = vtk.vtkPlane()
	plane.SetOrigin(*origin)
	plane.SetNormal(*normal)
	clip = vtk.vtkClipPolyData()
	clip.SetInputData(poly)
	clip.SetClipFunction(plane)
	clip.InsideOutOn()
	clip.Update()
	return clip.GetOutput()


def _build_convex_hull_actor(
	poly: vtk.vtkPolyData,
	cut_plane_origin: tuple[float, float, float] | None,
	cut_plane_normal: tuple[float, float, float] | None,
	color: tuple[float, float, float],
	opacity: float,
	remesh_iso: bool,
	remesh_target: int,
	remesh_subdivide: int,
	use_marching_cubes: bool,
	mc_spacing: float,
	cache_path: Path | None = None,
	refresh_cache: bool = False,
) -> vtk.vtkActor | None:
	if cache_path is not None and cache_path.exists() and not refresh_cache:
		cached = _read_vtp_cache(cache_path)
		if cached is not None and cached.GetNumberOfPoints() > 0:
			mapper = vtk.vtkPolyDataMapper()
			mapper.SetInputData(cached)
			mapper.ScalarVisibilityOff()
			actor = vtk.vtkActor()
			actor.SetMapper(mapper)
			actor.GetProperty().SetColor(*color)
			actor.GetProperty().SetOpacity(max(0.0, min(opacity, 1.0)))
			actor.GetProperty().SetRepresentationToSurface()
			return actor
	input_poly = poly
	if cut_plane_origin is not None and cut_plane_normal is not None:
		input_poly = _clip_poly_by_plane(poly, cut_plane_origin, cut_plane_normal)
	if remesh_iso:
		input_poly = _remesh_isotropic(input_poly, remesh_target, remesh_subdivide)
	if input_poly is None or input_poly.GetNumberOfPoints() == 0:
		return None
	delaunay = vtk.vtkDelaunay3D()
	delaunay.SetInputData(input_poly)
	delaunay.Update()
	surface = vtk.vtkDataSetSurfaceFilter()
	surface.SetInputConnection(delaunay.GetOutputPort())
	surface.Update()
	hull_poly = surface.GetOutput()
	if use_marching_cubes:
		mc_spacing = max(mc_spacing, 0.1)
		implicit = vtk.vtkImplicitPolyDataDistance()
		implicit.SetInput(hull_poly)
		bounds = hull_poly.GetBounds()
		pad = mc_spacing * 2.0
		min_x = bounds[0] - pad
		max_x = bounds[1] + pad
		min_y = bounds[2] - pad
		max_y = bounds[3] + pad
		min_z = bounds[4] - pad
		max_z = bounds[5] + pad
		dim_x = max(2, int(round((max_x - min_x) / mc_spacing)) + 1)
		dim_y = max(2, int(round((max_y - min_y) / mc_spacing)) + 1)
		dim_z = max(2, int(round((max_z - min_z) / mc_spacing)) + 1)
		sample = vtk.vtkSampleFunction()
		sample.SetImplicitFunction(implicit)
		sample.SetModelBounds(min_x, max_x, min_y, max_y, min_z, max_z)
		sample.SetSampleDimensions(dim_x, dim_y, dim_z)
		sample.ComputeNormalsOff()
		sample.Update()
		contour = vtk.vtkContourFilter()
		contour.SetInputConnection(sample.GetOutputPort())
		contour.SetValue(0, 0.0)
		contour.Update()
		hull_poly = contour.GetOutput()
	if cache_path is not None:
		_write_vtp_cache(hull_poly, cache_path)
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(hull_poly)
	mapper.ScalarVisibilityOff()
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(*color)
	actor.GetProperty().SetOpacity(max(0.0, min(opacity, 1.0)))
	actor.GetProperty().SetRepresentationToSurface()
	return actor


def _reconstruct_surface_mc(poly: vtk.vtkPolyData, spacing: float) -> vtk.vtkPolyData:
	spacing = max(spacing, 0.1)
	implicit = vtk.vtkImplicitPolyDataDistance()
	implicit.SetInput(poly)
	bounds = poly.GetBounds()
	pad = spacing * 2.0
	min_x = bounds[0] - pad
	max_x = bounds[1] + pad
	min_y = bounds[2] - pad
	max_y = bounds[3] + pad
	min_z = bounds[4] - pad
	max_z = bounds[5] + pad
	dim_x = max(2, int(round((max_x - min_x) / spacing)) + 1)
	dim_y = max(2, int(round((max_y - min_y) / spacing)) + 1)
	dim_z = max(2, int(round((max_z - min_z) / spacing)) + 1)
	sample = vtk.vtkSampleFunction()
	sample.SetImplicitFunction(implicit)
	sample.SetModelBounds(min_x, max_x, min_y, max_y, min_z, max_z)
	sample.SetSampleDimensions(dim_x, dim_y, dim_z)
	sample.ComputeNormalsOff()
	sample.Update()
	contour = vtk.vtkContourFilter()
	contour.SetInputConnection(sample.GetOutputPort())
	contour.SetValue(0, 0.0)
	contour.Update()
	return contour.GetOutput()


def _filter_external_by_normal(
	poly: vtk.vtkPolyData,
	ray_length: float,
	ray_eps: float,
	auto_orient: bool,
	verbose: bool = False,
) -> vtk.vtkPolyData:
	if poly.GetNumberOfCells() == 0:
		return poly
	bounds = poly.GetBounds()
	dx = bounds[1] - bounds[0]
	dy = bounds[3] - bounds[2]
	dz = bounds[5] - bounds[4]
	diag = (dx * dx + dy * dy + dz * dz) ** 0.5
	if diag <= 0:
		return poly
	if ray_length <= 0:
		ray_length = diag * 2.0
	ray_eps = max(ray_eps, 0.0)
	normals = vtk.vtkPolyDataNormals()
	normals.SetInputData(poly)
	normals.ComputePointNormalsOff()
	normals.ComputeCellNormalsOn()
	normals.SplittingOff()
	normals.ConsistencyOn()
	if auto_orient:
		normals.AutoOrientNormalsOn()
	normals.Update()
	poly_norm = normals.GetOutput()
	cell_normals = poly_norm.GetCellData().GetNormals()
	if cell_normals is None:
		return poly
	obb = vtk.vtkOBBTree()
	obb.SetDataSet(poly_norm)
	obb.BuildLocator()
	keep_ids = vtk.vtkIdTypeArray()
	keep_ids.SetNumberOfComponents(1)
	cell_count = poly_norm.GetNumberOfCells()
	for cell_id in range(cell_count):
		cell = poly_norm.GetCell(cell_id)
		points = cell.GetPoints()
		if points is None or points.GetNumberOfPoints() == 0:
			continue
		cx = cy = cz = 0.0
		for idx in range(points.GetNumberOfPoints()):
			px, py, pz = points.GetPoint(idx)
			cx += px
			cy += py
			cz += pz
		inv = 1.0 / points.GetNumberOfPoints()
		center = (cx * inv, cy * inv, cz * inv)
		nx, ny, nz = cell_normals.GetTuple(cell_id)
		nx, ny, nz = _normalize((nx, ny, nz))
		if nx == 0.0 and ny == 0.0 and nz == 0.0:
			keep_ids.InsertNextValue(cell_id)
			continue
		def _count_hits(direction: tuple[float, float, float]) -> int:
			off = _vec_scale(direction, ray_eps)
			p0 = _vec_add(center, off)
			p1 = _vec_add(center, _vec_scale(direction, ray_length))
			hit_points = vtk.vtkPoints()
			hit_ids = vtk.vtkIdList()
			obb.IntersectWithLine(p0, p1, hit_points, hit_ids)
			count = 0
			for hit_idx in range(hit_ids.GetNumberOfIds()):
				hit_id = hit_ids.GetId(hit_idx)
				if hit_id != cell_id:
					count += 1
			return count
		hits_plus = _count_hits((nx, ny, nz))
		hits_minus = _count_hits((-nx, -ny, -nz))
		if hits_plus == 0 or hits_minus == 0:
			keep_ids.InsertNextValue(cell_id)
	if verbose:
		print(f"Normal-ray filter: kept {keep_ids.GetNumberOfTuples()} / {cell_count} cells")
	selection_node = vtk.vtkSelectionNode()
	selection_node.SetFieldType(vtk.vtkSelectionNode.CELL)
	selection_node.SetContentType(vtk.vtkSelectionNode.INDICES)
	selection_node.SetSelectionList(keep_ids)
	selection = vtk.vtkSelection()
	selection.AddNode(selection_node)
	extract = vtk.vtkExtractSelection()
	extract.SetInputData(0, poly_norm)
	extract.SetInputData(1, selection)
	extract.Update()
	geom = vtk.vtkGeometryFilter()
	geom.SetInputConnection(extract.GetOutputPort())
	geom.Update()
	return geom.GetOutput()


def _read_vtp_cache(path: Path) -> vtk.vtkPolyData | None:
	reader = vtk.vtkXMLPolyDataReader()
	reader.SetFileName(str(path))
	reader.Update()
	output = reader.GetOutput()
	if output is None or output.GetNumberOfPoints() == 0:
		return None
	return output


def _write_vtp_cache(poly: vtk.vtkPolyData, path: Path) -> None:
	try:
		path.parent.mkdir(parents=True, exist_ok=True)
		writer = vtk.vtkXMLPolyDataWriter()
		writer.SetFileName(str(path))
		writer.SetInputData(poly)
		writer.Write()
	except OSError:
		pass


def _write_polydata_output(poly: vtk.vtkPolyData, path: Path) -> None:
	path.parent.mkdir(parents=True, exist_ok=True)
	suffix = path.suffix.lower()
	if suffix == ".vtp":
		writer = vtk.vtkXMLPolyDataWriter()
		writer.SetFileName(str(path))
		writer.SetInputData(poly)
		if writer.Write() == 0:
			raise RuntimeError(f"Failed to write VTP output: {path}")
		return
	if suffix == ".stl":
		triangulate = vtk.vtkTriangleFilter()
		triangulate.SetInputData(poly)
		triangulate.Update()
		writer = vtk.vtkSTLWriter()
		writer.SetFileName(str(path))
		writer.SetInputData(triangulate.GetOutput())
		if writer.Write() == 0:
			raise RuntimeError(f"Failed to write STL output: {path}")
		return
	raise RuntimeError(f"Unsupported output mesh format: {suffix}")


def _fill_holes(poly: vtk.vtkPolyData, hole_size: float) -> vtk.vtkPolyData:
	if hole_size <= 0:
		return poly
	fill = vtk.vtkFillHolesFilter()
	fill.SetInputData(poly)
	fill.SetHoleSize(hole_size)
	fill.Update()
	clean = vtk.vtkCleanPolyData()
	clean.SetInputData(fill.GetOutput())
	clean.Update()
	return clean.GetOutput()


def _batch_remesh_vtps(
	input_root: Path,
	output_root: Path,
	pattern: str,
	remesh_iso: bool,
	remesh_target: int,
	remesh_target_factor: float,
	remesh_subdivide: int,
	stem_mc: bool,
	stem_mc_spacing: float,
	overwrite: bool,
	verbose: bool,
	normal_ray_filter: bool,
	normal_ray_length: float,
	normal_ray_eps: float,
	normal_ray_auto_orient: bool,
	batch_export_normal_ray: bool,
	pre_mc_fill_holes: bool,
	pre_mc_hole_size: float,
) -> int:
	if not input_root.exists():
		raise FileNotFoundError(str(input_root))
	if not input_root.is_dir():
		raise NotADirectoryError(str(input_root))
	if not remesh_iso and not stem_mc:
		raise RuntimeError("Batch remesh requires --remesh-iso and/or --stem-mc")
	inputs = sorted(path for path in input_root.glob(pattern) if path.is_file())
	if not inputs and pattern == "**/*.vtp":
		inputs = sorted(path for path in input_root.glob("**/*.stl") if path.is_file())
	if not inputs:
		print("No input mesh files found for batch remesh.")
		return 0
	processed = 0
	skipped = 0
	total = len(inputs)
	for idx, src_path in enumerate(inputs, start=1):
		try:
			rel_path = src_path.relative_to(input_root)
		except ValueError:
			continue
		dst_path = output_root / rel_path
		if dst_path.exists() and not overwrite:
			if verbose:
				print(f"[{idx}/{total}] skip {rel_path}")
			skipped += 1
			continue
		if verbose:
			print(f"[{idx}/{total}] remesh {rel_path}")
		poly = _load_polydata_any(str(src_path))
		if normal_ray_filter:
			poly = _filter_external_by_normal(
				poly,
				normal_ray_length,
				normal_ray_eps,
				normal_ray_auto_orient,
				verbose=verbose,
			)
			if batch_export_normal_ray:
				ray_path = dst_path.with_suffix("")
				ray_path = ray_path.with_name(f"{ray_path.name}_premc").with_suffix(".stl")
				_write_polydata_output(poly, ray_path)
		if stem_mc:
			if pre_mc_fill_holes:
				poly = _fill_holes(poly, pre_mc_hole_size)
			reconstructed = _reconstruct_surface_mc(poly, stem_mc_spacing)
			poly = _interpolate_point_arrays(poly, reconstructed, nearest=True)
		if remesh_iso:
			effective_target = _effective_remesh_target(poly, remesh_target, remesh_target_factor)
			poly = _remesh_isotropic(poly, effective_target, remesh_subdivide)
		_write_polydata_output(poly, dst_path)
		processed += 1
	print(
		f"Batch remesh complete: {processed} written, {skipped} skipped, "
		f"source={input_root}, output={output_root}"
	)
	return processed


def _parse_hausdorff_sweep(value: str | None) -> tuple[float, float, int] | None:
	if not value:
		return None
	parts = [item.strip() for item in value.split(",") if item.strip()]
	if len(parts) != 3:
		raise ValueError("--stem-mc-hausdorff-sweep expects start,end,steps")
	start = float(parts[0])
	end = float(parts[1])
	steps = int(parts[2])
	if steps < 2:
		raise ValueError("--stem-mc-hausdorff-sweep steps must be >= 2")
	return start, end, steps


def _distance_stats(points: vtk.vtkPoints, implicit: vtk.vtkImplicitFunction) -> dict[str, float]:
	count = points.GetNumberOfPoints()
	if count == 0:
		return {"max": 0.0, "mean": 0.0, "p95": 0.0, "p99": 0.0, "rms": 0.0}
	dists: list[float] = []
	sum_val = 0.0
	sum_sq = 0.0
	max_val = 0.0
	for idx in range(count):
		x, y, z = points.GetPoint(idx)
		val = abs(implicit.EvaluateFunction(x, y, z))
		dists.append(val)
		sum_val += val
		sum_sq += val * val
		if val > max_val:
			max_val = val
	dists.sort()
	mean = sum_val / count
	rms = (sum_sq / count) ** 0.5
	idx95 = min(count - 1, int(round(0.95 * (count - 1))))
	idx99 = min(count - 1, int(round(0.99 * (count - 1))))
	return {
		"max": max_val,
		"mean": mean,
		"p95": dists[idx95],
		"p99": dists[idx99],
		"rms": rms,
	}


def _hausdorff_stats(a: vtk.vtkPolyData, b: vtk.vtkPolyData) -> dict[str, float]:
	implicit_a = vtk.vtkImplicitPolyDataDistance()
	implicit_a.SetInput(a)
	implicit_b = vtk.vtkImplicitPolyDataDistance()
	implicit_b.SetInput(b)
	stats_ab = _distance_stats(a.GetPoints(), implicit_b)
	stats_ba = _distance_stats(b.GetPoints(), implicit_a)
	return {
		"max": max(stats_ab["max"], stats_ba["max"]),
		"mean": 0.5 * (stats_ab["mean"] + stats_ba["mean"]),
		"p95": max(stats_ab["p95"], stats_ba["p95"]),
		"p99": max(stats_ab["p99"], stats_ba["p99"]),
		"rms": 0.5 * (stats_ab["rms"] + stats_ba["rms"]),
	}


def _remesh_isotropic(
	poly: vtk.vtkPolyData,
	target_points: int,
	subdivide: int,
) -> vtk.vtkPolyData:
	if target_points <= 0:
		return poly
	try:
		import pyvista as pv
		import pyacvd
	except ImportError as exc:
		raise RuntimeError("pyacvd and pyvista are required for --remesh-iso") from exc
	mesh = pv.wrap(poly)
	cluster = pyacvd.Clustering(mesh)
	if subdivide > 0:
		cluster.subdivide(subdivide)
	cluster.cluster(target_points)
	remeshed = cluster.create_mesh().triangulate()
	sampled = remeshed.sample(mesh)
	if not isinstance(sampled, pv.PolyData):
		sampled = sampled.extract_surface()
	return sampled


def _effective_remesh_target(
	poly: vtk.vtkPolyData,
	target_points: int,
	factor: float,
) -> int:
	base = target_points
	if base <= 0:
		base = max(1, poly.GetNumberOfPoints())
	if factor <= 0:
		factor = 1.0
	return max(1, int(round(base * factor)))


def _build_voxel_shell_polydata(
	poly: vtk.vtkPolyData,
	voxel_size: float,
	shell_thickness: float,
) -> vtk.vtkPolyData:
	bounds = poly.GetBounds()
	pad = max(shell_thickness, voxel_size)
	min_x = bounds[0] - pad
	max_x = bounds[1] + pad
	min_y = bounds[2] - pad
	max_y = bounds[3] + pad
	min_z = bounds[4] - pad
	max_z = bounds[5] + pad
	spacing = max(voxel_size, 0.5)
	implicit = vtk.vtkImplicitPolyDataDistance()
	implicit.SetInput(poly)
	points = vtk.vtkPoints()
	verts = vtk.vtkCellArray()
	idx = 0
	z = min_z
	while z <= max_z:
		y = min_y
		while y <= max_y:
			x = min_x
			while x <= max_x:
				dist = implicit.EvaluateFunction((x, y, z))
				if abs(dist) <= shell_thickness:
					points.InsertNextPoint(x, y, z)
					verts.InsertNextCell(1)
					verts.InsertCellPoint(idx)
					idx += 1
				x += spacing
			y += spacing
		z += spacing
	voxel_poly = vtk.vtkPolyData()
	voxel_poly.SetPoints(points)
	voxel_poly.SetVerts(verts)
	return voxel_poly


def _interpolate_point_scalars(
	source: vtk.vtkPolyData,
	target: vtk.vtkPolyData,
) -> vtk.vtkPolyData:
	normals = source.GetPointData().GetNormals()
	if normals is None:
		normals_filter = vtk.vtkPolyDataNormals()
		normals_filter.SetInputData(source)
		normals_filter.ComputePointNormalsOn()
		normals_filter.ComputeCellNormalsOff()
		normals_filter.SplittingOff()
		normals_filter.ConsistencyOn()
		normals_filter.AutoOrientNormalsOn()
		normals_filter.Update()
		source = normals_filter.GetOutput()
	interpolator = vtk.vtkPointInterpolator()
	interpolator.SetSourceData(source)
	interpolator.SetInputData(target)
	interpolator.SetNullPointsStrategyToClosestPoint()
	interpolator.SetKernel(vtk.vtkGaussianKernel())
	interpolator.GetKernel().SetSharpness(2.0)
	interpolator.GetKernel().SetRadius(3.0)
	interpolator.Update()
	return interpolator.GetOutput()


def _interpolate_point_arrays(
	source: vtk.vtkPolyData,
	target: vtk.vtkPolyData,
	nearest: bool = False,
) -> vtk.vtkPolyData:
	interpolator = vtk.vtkPointInterpolator()
	interpolator.SetSourceData(source)
	interpolator.SetInputData(target)
	interpolator.SetNullPointsStrategyToClosestPoint()
	if nearest:
		kernel = vtk.vtkVoronoiKernel()
	else:
		kernel = vtk.vtkGaussianKernel()
		kernel.SetSharpness(2.0)
		kernel.SetRadius(3.0)
	interpolator.SetKernel(kernel)
	interpolator.Update()
	return interpolator.GetOutput()


def _build_voxel_glyph_actor(
	poly: vtk.vtkPolyData,
	voxel_size: float,
	mapper: vtk.vtkPolyDataMapper,
) -> vtk.vtkActor:
	cube = vtk.vtkCubeSource()
	cube.SetXLength(voxel_size)
	cube.SetYLength(voxel_size)
	cube.SetZLength(voxel_size)
	glyph = vtk.vtkGlyph3D()
	glyph.SetSourceConnection(cube.GetOutputPort())
	glyph.SetInputData(poly)
	glyph.ScalingOff()
	glyph.Update()
	mapper.SetInputConnection(glyph.GetOutputPort())
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	return actor


def _parse_views(value: str) -> list[str]:
	views = [item.strip().lower() for item in value.split(",") if item.strip()]
	valid = {"front", "back", "left", "right"}
	return [view for view in views if view in valid]


def _compute_visible_ids(
	poly: vtk.vtkPolyData,
	views: list[str],
	method: str,
) -> set[int]:
	if not views:
		return set()
	ids = vtk.vtkGenerateIds()
	ids.SetInputData(poly)
	ids.PointIdsOn()
	ids.CellIdsOff()
	ids.SetPointIdsArrayName("OrigId")
	ids.Update()
	poly_with_ids = ids.GetOutput()
	bounds = poly_with_ids.GetBounds()
	center = (
		(bounds[0] + bounds[1]) * 0.5,
		(bounds[2] + bounds[3]) * 0.5,
		(bounds[4] + bounds[5]) * 0.5,
	)
	max_dim = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
	dist = max(max_dim * 2.5, 100.0)
	view_dirs = {
		"front": (0.0, -1.0, 0.0),
		"back": (0.0, 1.0, 0.0),
		"left": (1.0, 0.0, 0.0),
		"right": (-1.0, 0.0, 0.0),
	}
	renderer = vtk.vtkRenderer()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(poly_with_ids)
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	renderer.AddActor(actor)
	render_window = vtk.vtkRenderWindow()
	render_window.SetOffScreenRendering(1)
	render_window.SetSize(600, 600)
	render_window.AddRenderer(renderer)
	visible_ids: set[int] = set()
	for view in views:
		dir_vec = view_dirs.get(view)
		if not dir_vec:
			continue
		camera = renderer.GetActiveCamera()
		camera.SetFocalPoint(*center)
		camera.SetPosition(
			center[0] + dir_vec[0] * dist,
			center[1] + dir_vec[1] * dist,
			center[2] + dir_vec[2] * dist,
		)
		camera.SetViewUp(0.0, 0.0, 1.0)
		renderer.ResetCameraClippingRange()
		render_window.Render()
		if method == "hardware":
			print("Hardware selector not available; falling back to zbuffer.", file=sys.stderr)
		select = vtk.vtkSelectVisiblePoints()
		select.SetInputData(poly_with_ids)
		select.SetRenderer(renderer)
		select.Update()
		visible = select.GetOutput()
		id_array = visible.GetPointData().GetArray("OrigId")
		if id_array is None:
			continue
		for idx in range(id_array.GetNumberOfTuples()):
			visible_ids.add(int(id_array.GetTuple1(idx)))
	return visible_ids


def _set_camera_z_up(renderer: vtk.vtkRenderer, bounds: tuple[float, float, float, float, float, float] | None) -> None:
	if bounds is None:
		renderer.ResetCamera()
		camera = renderer.GetActiveCamera()
		camera.SetViewUp(0.0, 0.0, 1.0)
		renderer.ResetCameraClippingRange()
		return
	center = (
		(bounds[0] + bounds[1]) * 0.5,
		(bounds[2] + bounds[3]) * 0.5,
		(bounds[4] + bounds[5]) * 0.5,
	)
	max_dim = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
	dist = max(max_dim * 2.5, 100.0)
	camera = renderer.GetActiveCamera()
	camera.SetFocalPoint(*center)
	camera.SetPosition(center[0], center[1] - dist, center[2])
	camera.SetViewUp(0.0, 0.0, 1.0)
	renderer.ResetCameraClippingRange()


def _apply_visibility_mask(poly: vtk.vtkPolyData, array_name: str, visible_ids: set[int]) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(array_name)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % array_name)
	masked_name = f"{array_name}_Visible"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	for idx in range(source_array.GetNumberOfTuples()):
		if idx in visible_ids:
			masked.SetTuple1(idx, source_array.GetTuple1(idx))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _apply_visibility_mask_by_zone(
	poly: vtk.vtkPolyData,
	array_name: str,
	zone_array: vtk.vtkDataArray,
	visible_by_view: dict[str, set[int]],
	zone_view_map: dict[int, str],
) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(array_name)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % array_name)
	masked_name = f"{array_name}_Visible"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	for idx in range(source_array.GetNumberOfTuples()):
		zone_id = int(zone_array.GetTuple1(idx))
		view_key = zone_view_map.get(zone_id)
		if view_key and idx in visible_by_view.get(view_key, set()):
			masked.SetTuple1(idx, source_array.GetTuple1(idx))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _apply_largest_region_mask(
	poly: vtk.vtkPolyData,
	source_poly: vtk.vtkPolyData | None = None,
) -> None:
	source = source_poly or poly
	point_data = source.GetPointData()
	zone_array = point_data.GetArray("GruenZone")
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	ids = vtk.vtkGenerateIds()
	ids.SetInputData(source)
	ids.PointIdsOn()
	ids.CellIdsOff()
	ids.SetPointIdsArrayName("OrigId")
	ids.Update()
	poly_with_ids = ids.GetOutput()
	keep = vtk.vtkIntArray()
	keep.SetName("GruenZoneKeep")
	keep.SetNumberOfComponents(1)
	keep.SetNumberOfTuples(poly_with_ids.GetNumberOfPoints())
	for idx in range(keep.GetNumberOfTuples()):
		keep.SetTuple1(idx, 0)
	for zone_id in range(1, 15):
		threshold = vtk.vtkThreshold()
		threshold.SetInputData(poly_with_ids)
		threshold.SetInputArrayToProcess(
			0,
			0,
			0,
			vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
			"GruenZone",
		)
		if hasattr(threshold, "ThresholdBetween"):
			threshold.ThresholdBetween(zone_id, zone_id)
		else:
			threshold.SetLowerThreshold(zone_id)
			threshold.SetUpperThreshold(zone_id)
			threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
		threshold.Update()
		geometry = vtk.vtkGeometryFilter()
		geometry.SetInputConnection(threshold.GetOutputPort())
		geometry.Update()
		connect = vtk.vtkConnectivityFilter()
		connect.SetInputConnection(geometry.GetOutputPort())
		connect.SetExtractionModeToLargestRegion()
		connect.Update()
		region = connect.GetOutput()
		id_array = region.GetPointData().GetArray("OrigId")
		if id_array is None:
			continue
		for idx in range(id_array.GetNumberOfTuples()):
			orig_id = int(id_array.GetTuple1(idx))
			keep.SetTuple1(orig_id, 1)
	if source is not poly:
		source.GetPointData().AddArray(keep)
		mapped = _interpolate_point_arrays(source, poly, nearest=True)
		mapped_keep = mapped.GetPointData().GetArray("GruenZoneKeep")
		if mapped_keep is None:
			mapped_keep = keep
		point_data = poly.GetPointData()
		if point_data.GetArray("GruenZoneKeep"):
			point_data.RemoveArray("GruenZoneKeep")
		point_data.AddArray(mapped_keep)
		keep = mapped_keep
	else:
		if point_data.GetArray("GruenZoneKeep"):
			point_data.RemoveArray("GruenZoneKeep")
		point_data.AddArray(keep)
		point_data = poly.GetPointData()
	masked = vtk.vtkDoubleArray()
	masked.SetName("GruenZoneLargest")
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(poly.GetNumberOfPoints())
	for idx in range(poly.GetNumberOfPoints()):
		if int(keep.GetTuple1(idx)) == 1:
			masked.SetTuple1(idx, poly.GetPointData().GetArray("GruenZone").GetTuple1(idx))
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray("GruenZoneLargest"):
		point_data.RemoveArray("GruenZoneLargest")
	point_data.AddArray(masked)
	point_data.SetActiveScalars("GruenZoneLargest")
	poly.Modified()


def _apply_composite_gruen(poly: vtk.vtkPolyData) -> str:
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray("GruenZone")
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	composite = vtk.vtkIntArray()
	composite.SetName("GruenZoneComposite")
	composite.SetNumberOfComponents(1)
	composite.SetNumberOfTuples(zone_array.GetNumberOfTuples())
	for idx in range(zone_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			composite.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_value)
		if zone_id in (1, 7):
			composite_id = 1
		elif zone_id in (2, 6):
			composite_id = 2
		elif zone_id in (3, 5):
			composite_id = 3
		elif zone_id in (8, 14):
			composite_id = 8
		elif zone_id in (9, 13):
			composite_id = 9
		elif zone_id in (10, 12):
			composite_id = 10
		else:
			composite_id = zone_id
		composite.SetTuple1(idx, composite_id)
	if point_data.GetArray("GruenZoneComposite"):
		point_data.RemoveArray("GruenZoneComposite")
	point_data.AddArray(composite)
	point_data.SetActiveScalars("GruenZoneComposite")
	poly.Modified()
	return "GruenZoneComposite"


def _apply_partitioned_gruen(poly: vtk.vtkPolyData) -> str:
	point_data = poly.GetPointData()
	zone_array = point_data.GetArray("GruenZone")
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	partition = vtk.vtkIntArray()
	partition.SetName("GruenZonePartition")
	partition.SetNumberOfComponents(1)
	partition.SetNumberOfTuples(zone_array.GetNumberOfTuples())
	for idx in range(zone_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			partition.SetTuple1(idx, float("nan"))
			continue
		zone_id = int(zone_value)
		if zone_id in (1, 7, 8, 14):
			part_id = 1  # top
		elif zone_id in (2, 6, 9, 13):
			part_id = 2  # mediumtop
		elif zone_id in (3, 5, 10, 12):
			part_id = 3  # mediumbottom
		elif zone_id in (4, 11):
			part_id = 4  # bottom
		else:
			part_id = zone_id
		partition.SetTuple1(idx, part_id)
	if point_data.GetArray("GruenZonePartition"):
		point_data.RemoveArray("GruenZonePartition")
	point_data.AddArray(partition)
	point_data.SetActiveScalars("GruenZonePartition")
	poly.Modified()
	return "GruenZonePartition"


def _parse_partition_zones(value: str) -> list[int]:
	if not value:
		return []
	mapping = {
		"top": 1,
		"mediumtop": 2,
		"medium-bottom": 3,
		"mediumbottom": 3,
		"bottom": 4,
	}
	result: list[int] = []
	for raw in value.split(","):
		item = raw.strip().lower()
		if not item:
			continue
		if item.isdigit():
			result.append(int(item))
			continue
		mapped = mapping.get(item)
		if mapped is not None:
			result.append(mapped)
	return result


def _parse_envelope_bands(value: str) -> tuple[float, float, float]:
	parts = [item.strip() for item in value.split(",") if item.strip()]
	if len(parts) != 3:
		raise ValueError("--envelope-z-bands expects three comma-separated values")
	return (float(parts[0]), float(parts[1]), float(parts[2]))


def _resolve_hu_range(label: str | None) -> tuple[float, float] | None:
	if not label:
		return None
	name = label.strip().lower()
	for zone_min, zone_max, _color, zone_label in EZPLAN_ZONE_DEFS:
		if zone_label.lower() == name:
			return (zone_min, zone_max)
	return None


def _apply_hu_range_mask(poly: vtk.vtkPolyData, array_name: str, hu_range: tuple[float, float]) -> str:
	point_data = poly.GetPointData()
	source_array = point_data.GetArray(array_name)
	if source_array is None:
		raise RuntimeError("Scalar array '%s' not found" % array_name)
	masked_name = f"{array_name}_Range"
	masked = vtk.vtkDoubleArray()
	masked.SetName(masked_name)
	masked.SetNumberOfComponents(1)
	masked.SetNumberOfTuples(source_array.GetNumberOfTuples())
	low, high = hu_range
	for idx in range(source_array.GetNumberOfTuples()):
		value = source_array.GetTuple1(idx)
		if value != value:
			masked.SetTuple1(idx, float("nan"))
			continue
		if low <= value <= high:
			masked.SetTuple1(idx, value)
		else:
			masked.SetTuple1(idx, float("nan"))
	if point_data.GetArray(masked_name):
		point_data.RemoveArray(masked_name)
	point_data.AddArray(masked)
	point_data.SetActiveScalars(masked_name)
	poly.Modified()
	return masked_name


def _print_summary(path: str, array_name: str, array_range: tuple[float, float], color_label: str):
	print("Loaded '%s'" % path)
	print("Using scalar array '%s' (range %.2f .. %.2f)" % (array_name, array_range[0], array_range[1]))
	print("Color mapping: %s" % color_label)


def _add_side_label(renderer: vtk.vtkRenderer, side: str):
	label = vtk.vtkTextActor()
	label.SetInput(f"Side: {side}")
	label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
	label.GetTextProperty().SetFontSize(18)
	label.SetDisplayPosition(10, 10)
	renderer.AddActor2D(label)


def _add_hu_summary_label(renderer: vtk.vtkRenderer, text: str):
	label = vtk.vtkTextActor()
	label.SetInput(text)
	label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
	label.GetTextProperty().SetFontSize(16)
	label.SetDisplayPosition(10, 35)
	renderer.AddActor2D(label)


def _add_hu_table_label(renderer: vtk.vtkRenderer, rows: list[tuple[str, float]]):
	lines = ["HU range summary (%):"]
	for label, pct in rows:
		lines.append(f"{label}: {pct:.1f}%")
	label = vtk.vtkTextActor()
	label.SetInput("\n".join(lines))
	label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
	label.GetTextProperty().SetFontSize(14)
	label.SetDisplayPosition(10, 60)
	renderer.AddActor2D(label)


def _add_dominant_zone_label(renderer: vtk.vtkRenderer, text: str):
	label = vtk.vtkTextActor()
	label.SetInput(text)
	label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
	label.GetTextProperty().SetFontSize(16)
	label.SetDisplayPosition(10, 180)
	renderer.AddActor2D(label)


def _build_zone_overlay_actor(
	poly: vtk.vtkPolyData,
	zone_array_name: str,
	zone_id: int,
	color: tuple[float, float, float] = (1.0, 0.85, 0.1),
) -> vtk.vtkActor | None:
	threshold = vtk.vtkThreshold()
	threshold.SetInputData(poly)
	threshold.SetInputArrayToProcess(
		0,
		0,
		0,
		vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS,
		zone_array_name,
	)
	if hasattr(threshold, "ThresholdBetween"):
		threshold.ThresholdBetween(zone_id, zone_id)
	else:
		threshold.SetLowerThreshold(zone_id)
		threshold.SetUpperThreshold(zone_id)
		threshold.SetThresholdFunction(vtk.vtkThreshold.THRESHOLD_BETWEEN)
	threshold.Update()
	geometry = vtk.vtkGeometryFilter()
	geometry.SetInputConnection(threshold.GetOutputPort())
	geometry.Update()
	zone_poly = geometry.GetOutput()
	if zone_poly is None or zone_poly.GetNumberOfPoints() == 0:
		return None
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(zone_poly)
	mapper.ScalarVisibilityOff()
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	actor.GetProperty().SetColor(*color)
	actor.GetProperty().SetOpacity(0.6)
	return actor


def _add_viewport_label(renderer: vtk.vtkRenderer, text: str, x: int = 10, y: int = 10):
	label = vtk.vtkTextActor()
	label.SetInput(text)
	label.GetTextProperty().SetColor(0.1, 0.1, 0.1)
	label.GetTextProperty().SetFontSize(16)
	label.SetDisplayPosition(x, y)
	renderer.AddActor2D(label)


def _compute_hu_table(array: vtk.vtkDataArray) -> list[tuple[str, float]]:
	valid_values = []
	for idx in range(array.GetNumberOfTuples()):
		value = array.GetTuple1(idx)
		if value == value:
			valid_values.append(value)
	if not valid_values:
		return [(zone[3], 0.0) for zone in EZPLAN_ZONE_DEFS]
	counts = {zone[3]: 0 for zone in EZPLAN_ZONE_DEFS}
	for value in valid_values:
		for zone_min, zone_max, _color, label in EZPLAN_ZONE_DEFS:
			if zone_min <= value <= zone_max:
				counts[label] += 1
				break
	total = len(valid_values)
	return [(label, 100.0 * count / total) for label, count in counts.items()]


def _pick_zone_array(point_data: vtk.vtkPointData) -> vtk.vtkDataArray | None:
	return (
		point_data.GetArray("GruenZonePartition")
		or point_data.GetArray("GruenZoneComposite")
		or point_data.GetArray("GruenZoneLargest")
		or point_data.GetArray("GruenZone")
	)


def _compute_dominant_hu_zone(
	poly: vtk.vtkPolyData,
	hu_array_name: str,
	hu_range: tuple[float, float],
) -> tuple[int | None, float]:
	point_data = poly.GetPointData()
	zone_array = _pick_zone_array(point_data)
	if zone_array is None:
		raise RuntimeError("GruenZone array missing; enable --gruen-zones")
	hu_array = point_data.GetArray(hu_array_name)
	if hu_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array_name)
	counts: dict[int, int] = {}
	total = 0
	low, high = hu_range
	for idx in range(hu_array.GetNumberOfTuples()):
		value = hu_array.GetTuple1(idx)
		if value != value:
			continue
		if not (low <= value <= high):
			continue
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			continue
		zone_id = int(zone_value)
		counts[zone_id] = counts.get(zone_id, 0) + 1
		total += 1
	if not counts or total == 0:
		return None, 0.0
	dominant_zone = max(counts.items(), key=lambda item: item[1])[0]
	percent = 100.0 * counts[dominant_zone] / total
	return dominant_zone, percent


def _compute_partition_hu_summary(
	poly: vtk.vtkPolyData,
	hu_array_name: str,
	partition_array: vtk.vtkDataArray,
) -> dict[int, dict[str, tuple[int, float]]]:
	point_data = poly.GetPointData()
	hu_array = point_data.GetArray(hu_array_name)
	if hu_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array_name)
	counts: dict[int, dict[str, int]] = {pid: {z[3]: 0 for z in EZPLAN_ZONE_DEFS} for pid in range(1, 5)}
	totals: dict[int, int] = {pid: 0 for pid in range(1, 5)}
	for idx in range(hu_array.GetNumberOfTuples()):
		part_val = partition_array.GetTuple1(idx)
		if part_val != part_val:
			continue
		part_id = int(part_val)
		if part_id not in counts:
			continue
		value = hu_array.GetTuple1(idx)
		if value != value:
			continue
		totals[part_id] += 1
		for zone_min, zone_max, _color, label in EZPLAN_ZONE_DEFS:
			if zone_min <= value <= zone_max:
				counts[part_id][label] += 1
				break
	result: dict[int, dict[str, tuple[int, float]]] = {}
	for part_id, tag_counts in counts.items():
		part_total = totals.get(part_id, 0)
		result[part_id] = {}
		for label, count in tag_counts.items():
			percent = 100.0 * count / part_total if part_total else 0.0
			result[part_id][label] = (count, percent)
	return result


def _compute_gruen_hu_summary(
	poly: vtk.vtkPolyData,
	hu_array_name: str,
	zone_array: vtk.vtkDataArray,
	max_zone: int = 14,
	bottom_point: tuple[float, float, float] | None = None,
	bottom_radius: float = 0.0,
	bottom_zone_ids: tuple[int, int] = (4, 11),
) -> dict[int, dict[str, tuple[int, float]]]:
	point_data = poly.GetPointData()
	hu_array = point_data.GetArray(hu_array_name)
	if hu_array is None:
		raise RuntimeError("Scalar array '%s' not found" % hu_array_name)
	counts: dict[int, dict[str, int]] = {
		zone_id: {z[3]: 0 for z in EZPLAN_ZONE_DEFS} for zone_id in range(1, max_zone + 1)
	}
	totals: dict[int, int] = {zone_id: 0 for zone_id in range(1, max_zone + 1)}
	for idx in range(hu_array.GetNumberOfTuples()):
		zone_value = zone_array.GetTuple1(idx)
		if zone_value != zone_value:
			continue
		zone_id = int(zone_value)
		if zone_id not in counts:
			continue
		value = hu_array.GetTuple1(idx)
		if value != value:
			continue
		totals[zone_id] += 1
		for zone_min, zone_max, _color, label in EZPLAN_ZONE_DEFS:
			if zone_min <= value <= zone_max:
				counts[zone_id][label] += 1
				break
	result: dict[int, dict[str, tuple[int, float]]] = {}
	if bottom_point is not None and bottom_radius > 0:
		x0, y0, z0 = bottom_point
		r2 = bottom_radius * bottom_radius
		bottom_counts = {z[3]: 0 for z in EZPLAN_ZONE_DEFS}
		bottom_total = 0
		points = poly.GetPoints()
		if points is not None:
			for idx in range(hu_array.GetNumberOfTuples()):
				value = hu_array.GetTuple1(idx)
				if value != value:
					continue
				x, y, z = points.GetPoint(idx)
				dx = x - x0
				dy = y - y0
				dz = z - z0
				if dx * dx + dy * dy + dz * dz > r2:
					continue
				bottom_total += 1
				for zone_min, zone_max, _color, label in EZPLAN_ZONE_DEFS:
					if zone_min <= value <= zone_max:
						bottom_counts[label] += 1
						break
			for zone_id in bottom_zone_ids:
				if zone_id in counts:
					counts[zone_id] = dict(bottom_counts)
					totals[zone_id] = bottom_total
	for zone_id, tag_counts in counts.items():
		zone_total = totals.get(zone_id, 0)
		result[zone_id] = {}
		for label, count in tag_counts.items():
			percent = 100.0 * count / zone_total if zone_total else 0.0
			result[zone_id][label] = (count, percent)
	return result


def _export_partition_hu_xml(
	vtp_path: str,
	poly: vtk.vtkPolyData,
	hu_array_name: str,
) -> str:
	partition_array = poly.GetPointData().GetArray("GruenZonePartition")
	if partition_array is None:
		raise RuntimeError("GruenZonePartition missing; enable --partitioned-gruen")
	summary = _compute_partition_hu_summary(poly, hu_array_name, partition_array)
	zone_labels = {
		1: "top",
		2: "mediumtop",
		3: "mediumbottom",
		4: "bottom",
	}
	root = ET.Element("huSummary", attrib={"array": hu_array_name})
	for part_id in range(1, 5):
		zone_elem = ET.SubElement(root, "zone", attrib={"id": str(part_id), "name": zone_labels[part_id]})
		for label, (count, percent) in summary.get(part_id, {}).items():
			ET.SubElement(
				zone_elem,
				"tag",
				attrib={
					"name": label,
					"count": str(count),
					"percent": f"{percent:.4f}",
				},
			)
	file_path = Path(vtp_path).with_suffix("").name + "_hu_summary.xml"
	output_path = Path(vtp_path).resolve().parent / file_path
	tree = ET.ElementTree(root)
	tree.write(output_path, encoding="utf-8", xml_declaration=True)
	return str(output_path)


def _export_gruen_hu_xml(
	vtp_path: str,
	poly: vtk.vtkPolyData,
	hu_array_name: str,
	zone_array_name: str,
	max_zone: int = 14,
	bottom_point: tuple[float, float, float] | None = None,
	bottom_radius: float = 0.0,
) -> str:
	zone_array = poly.GetPointData().GetArray(zone_array_name)
	if zone_array is None:
		raise RuntimeError(f"{zone_array_name} missing; enable --show-gruen-zones")
	summary = _compute_gruen_hu_summary(
		poly,
		hu_array_name,
		zone_array,
		max_zone=max_zone,
		bottom_point=bottom_point,
		bottom_radius=bottom_radius,
	)
	root = ET.Element("huSummary", attrib={"array": hu_array_name, "zoneArray": zone_array_name})
	for zone_id in range(1, max_zone + 1):
		zone_elem = ET.SubElement(root, "zone", attrib={"id": str(zone_id)})
		for label, (count, percent) in summary.get(zone_id, {}).items():
			ET.SubElement(
				zone_elem,
				"tag",
				attrib={
					"name": label,
					"count": str(count),
					"percent": f"{percent:.4f}",
				},
			)
	file_path = Path(vtp_path).with_suffix("").name + "_stem_local_gruen_hu_summary.xml"
	output_path = Path(vtp_path).resolve().parent / file_path
	tree = ET.ElementTree(root)
	tree.write(output_path, encoding="utf-8", xml_declaration=True)
	return str(output_path)


def main() -> int:
	args = _parse_args()
	if args.batch_remesh_input or args.batch_remesh_output:
		if not args.batch_remesh_input or not args.batch_remesh_output:
			raise RuntimeError("--batch-remesh-input and --batch-remesh-output must be provided together")
		input_root = Path(args.batch_remesh_input).resolve()
		output_root = Path(args.batch_remesh_output).resolve()
		_batch_remesh_vtps(
			input_root,
			output_root,
			args.batch_remesh_glob,
			args.remesh_iso,
			args.remesh_target,
			args.remesh_target_factor,
			args.remesh_subdivide,
			args.stem_mc,
			args.stem_mc_spacing,
			args.batch_remesh_overwrite,
			args.batch_remesh_verbose,
			args.normal_ray_filter,
			args.normal_ray_length,
			args.normal_ray_eps,
			args.normal_ray_auto_orient,
			args.batch_export_normal_ray,
			args.pre_mc_fill_holes,
			args.pre_mc_hole_size,
		)
		return 0
	if not args.vtp:
		raise RuntimeError("Missing VTP path. Provide a VTP file or use --batch-remesh-input")
	poly = _load_polydata(args.vtp)

	needs_local = any([
		args.show_neck_point,
		args.show_cut_plane,
		args.gruen_zones,
		args.show_gruen_zones,
		bool(args.gruen_hu_zones),
		args.show_offset,
		args.show_all_offsets,
		args.partitioned_gruen_viewports,
		args.show_junction_point,
		args.show_junction_axes,
		args.show_convex_hull,
		args.envelope_gruen,
		args.show_envelope_gruen,
		args.envelope_hu_viewports,
	])
	if needs_local and not args.local_frame:
		raise RuntimeError("Local-frame options require --local-frame")

	neck_point = _parse_vector(args.neck_point) if args.neck_point else None
	cut_plane_origin = _parse_vector(args.cut_plane_origin) if args.cut_plane_origin else None
	cut_plane_normal = _parse_vector(args.cut_plane_normal) if args.cut_plane_normal else None
	base_color = _parse_vector(args.base_color) if args.base_color else None
	convex_color = _parse_vector(args.convex_hull_color) if args.convex_hull_color else None

	auto_module = None
	auto_uid = None
	amistem_rotation_deg = 0.0
	actis_rotation_deg = 0.0
	mathys_rotation_x_deg = 0.0
	gruen_cut_plane_mode = "below"
	if args.local_frame and (
		neck_point is None
		or cut_plane_origin is None
		or cut_plane_normal is None
		or args.show_offset
		or args.show_all_offsets
	):
		auto_neck, auto_origin, auto_normal, auto_side, auto_module, auto_uid = (
			_resolve_stem_annotation_defaults(
				args.vtp,
				args.seedplan,
				args.config_index,
			)
		)
		if neck_point is None:
			neck_point = auto_neck
		if cut_plane_origin is None:
			cut_plane_origin = auto_origin
		if cut_plane_normal is None:
			cut_plane_normal = auto_normal
		if args.side == "auto" and auto_side:
			args.side = "left" if auto_side.strip().lower().startswith("l") else "right"
		if auto_module is not None and getattr(auto_module, "__name__", "") == "amedacta_complete":
			if args.side == "right":
				amistem_rotation_deg = 90.0
			elif args.side == "left":
				amistem_rotation_deg = 90.0
			if amistem_rotation_deg:
				neck_point = _rotate_z_point(neck_point, amistem_rotation_deg)
				cut_plane_origin = _rotate_z_point(cut_plane_origin, amistem_rotation_deg)
				cut_plane_normal = _rotate_z_vector(cut_plane_normal, amistem_rotation_deg)
		if auto_module is not None and getattr(auto_module, "__name__", "") == "johnson_actis_complete":
			actis_rotation_deg = 180.0
			neck_point = _rotate_z_point(neck_point, actis_rotation_deg)
			cut_plane_origin = _rotate_z_point(cut_plane_origin, actis_rotation_deg)
			cut_plane_normal = _rotate_z_vector(cut_plane_normal, actis_rotation_deg)
		if auto_module is not None and getattr(auto_module, "__name__", "") == "mathys_optimys_complete":
			neck_point = _rotate_z_point(neck_point, -90.0)
			cut_plane_origin = _rotate_z_point(cut_plane_origin, -90.0)
			cut_plane_normal = _rotate_z_vector(cut_plane_normal, -90.0)
			mathys_rotation_x_deg = 90.0
			neck_point = _rotate_x_point(neck_point, mathys_rotation_x_deg)
			cut_plane_origin = _rotate_x_point(cut_plane_origin, mathys_rotation_x_deg)
			cut_plane_normal = _rotate_x_vector(cut_plane_normal, mathys_rotation_x_deg)
			cut_plane_normal = (-cut_plane_normal[0], -cut_plane_normal[1], -cut_plane_normal[2])
			gruen_cut_plane_mode = "above"

	effective_rotate_z_180 = args.rotate_z_180 or args.side == "left"
	if amistem_rotation_deg:
		transform = vtk.vtkTransform()
		transform.Identity()
		transform.RotateZ(amistem_rotation_deg)
		transformer = vtk.vtkTransformPolyDataFilter()
		transformer.SetTransform(transform)
		transformer.SetInputData(poly)
		transformer.Update()
		poly = transformer.GetOutput()
	if actis_rotation_deg:
		transform = vtk.vtkTransform()
		transform.Identity()
		transform.RotateZ(actis_rotation_deg)
		transformer = vtk.vtkTransformPolyDataFilter()
		transformer.SetTransform(transform)
		transformer.SetInputData(poly)
		transformer.Update()
		poly = transformer.GetOutput()
	if mathys_rotation_x_deg:
		transform = vtk.vtkTransform()
		transform.Identity()
		transform.RotateX(mathys_rotation_x_deg)
		transformer = vtk.vtkTransformPolyDataFilter()
		transformer.SetTransform(transform)
		transformer.SetInputData(poly)
		transformer.Update()
		poly = transformer.GetOutput()
	if effective_rotate_z_180:
		transform = vtk.vtkTransform()
		transform.Identity()
		transform.RotateZ(180.0)
		transformer = vtk.vtkTransformPolyDataFilter()
		transformer.SetTransform(transform)
		transformer.SetInputData(poly)
		transformer.Update()
		poly = transformer.GetOutput()

	if args.side == "left":
		if neck_point is not None:
			neck_point = (-neck_point[0], neck_point[1], neck_point[2])
		if cut_plane_origin is not None:
			cut_plane_origin = (-cut_plane_origin[0], cut_plane_origin[1], cut_plane_origin[2])
		if cut_plane_normal is not None:
			cut_plane_normal = (-cut_plane_normal[0], cut_plane_normal[1], cut_plane_normal[2])
	elif args.side == "right":
		if neck_point is not None:
			neck_point = (-neck_point[0], -neck_point[1], neck_point[2])
		if cut_plane_origin is not None:
			cut_plane_origin = (-cut_plane_origin[0], -cut_plane_origin[1], cut_plane_origin[2])
		if cut_plane_normal is not None:
			cut_plane_normal = (-cut_plane_normal[0], -cut_plane_normal[1], cut_plane_normal[2])
	if effective_rotate_z_180:
		if neck_point is not None:
			neck_point = (-neck_point[0], -neck_point[1], neck_point[2])
		if cut_plane_origin is not None:
			cut_plane_origin = (-cut_plane_origin[0], -cut_plane_origin[1], cut_plane_origin[2])
		if cut_plane_normal is not None:
			cut_plane_normal = (-cut_plane_normal[0], -cut_plane_normal[1], cut_plane_normal[2])
	original_poly = poly
	if args.stem_mc_hausdorff_sweep:
		try:
			sweep = _parse_hausdorff_sweep(args.stem_mc_hausdorff_sweep)
		except ValueError as exc:
			raise RuntimeError(str(exc)) from exc
		if sweep is not None:
			start, end, steps = sweep
			print("Hausdorff sweep (implicit marching cubes):")
			for idx in range(steps):
				factor = idx / (steps - 1)
				spacing = start + (end - start) * factor
				recon = _reconstruct_surface_mc(original_poly, spacing)
				stats = _hausdorff_stats(original_poly, recon)
				print(
					f"  spacing={spacing:.4f} -> max={stats['max']:.4f}, "
					f"mean={stats['mean']:.4f}, rms={stats['rms']:.4f}, "
					f"p95={stats['p95']:.4f}, p99={stats['p99']:.4f}"
				)
	if args.normal_ray_filter:
		poly = _filter_external_by_normal(
			poly,
			args.normal_ray_length,
			args.normal_ray_eps,
			args.normal_ray_auto_orient,
		)
		if args.export_normal_ray_mesh:
			_write_polydata_output(poly, Path(args.export_normal_ray_mesh).resolve())
	if args.stem_mc:
		if args.pre_mc_fill_holes:
			poly = _fill_holes(poly, args.pre_mc_hole_size)
		reconstructed = None
		stem_cache_path = None
		if args.cache_remesh:
			stem_cache_path = (
				Path(args.vtp).resolve().parent
				/ f"{Path(args.vtp).stem}_stem_mc_{args.stem_mc_spacing:.3f}.vtp"
			)
			if stem_cache_path.exists() and not args.cache_remesh_refresh:
				reconstructed = _read_vtp_cache(stem_cache_path)
			if reconstructed is None:
				reconstructed = _reconstruct_surface_mc(poly, args.stem_mc_spacing)
				_write_vtp_cache(reconstructed, stem_cache_path)
		if reconstructed is None:
			reconstructed = _reconstruct_surface_mc(poly, args.stem_mc_spacing)
		poly = _interpolate_point_arrays(poly, reconstructed, nearest=True)
	if args.stem_mc_hausdorff:
		recon = _reconstruct_surface_mc(original_poly, args.stem_mc_spacing)
		stats = _hausdorff_stats(original_poly, recon)
		print(
			"Hausdorff stats (implicit marching cubes): "
			f"max={stats['max']:.4f}, mean={stats['mean']:.4f}, rms={stats['rms']:.4f}, "
			f"p95={stats['p95']:.4f}, p99={stats['p99']:.4f}"
		)

	offset_point = None
	offset_head_label = None
	all_offset_points: list[tuple[str, tuple[float, float, float]]] = []
	if args.show_offset or args.show_all_offsets:
		module = auto_module
		uid_member = auto_uid
		if module is None or uid_member is None:
			raise RuntimeError("Offset points require a seedplan.xml to resolve implant data")
		head_offset_fn = getattr(module, "head_to_stem_offset", None)
		if not callable(head_offset_fn):
			raise RuntimeError("Implant module does not define head_to_stem_offset()")
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
		if args.show_offset and offset_head_uid is not None:
			offset_head_label = (
				offset_head_uid.name if hasattr(offset_head_uid, "name") else str(offset_head_uid)
			)
			try:
				offset_point = _coerce_point(head_offset_fn(offset_head_uid, uid_member))
			except ValueError:
				offset_point = None
			if module is not None and getattr(module, "__name__", "") == "mathys_optimys_complete":
				if offset_point is not None:
					offset_point = (-offset_point[0], offset_point[1], offset_point[2])
			if amistem_rotation_deg:
				offset_point = _rotate_z_point(offset_point, amistem_rotation_deg)
			if actis_rotation_deg:
				offset_point = _rotate_z_point(offset_point, actis_rotation_deg)
			if mathys_rotation_x_deg:
				offset_point = _rotate_x_point(offset_point, mathys_rotation_x_deg)
		if args.show_all_offsets:
			head_uids = getattr(module, "HEAD_UIDS", None)
			if head_uids:
				for head_uid in head_uids:
					label = head_uid.name if hasattr(head_uid, "name") else str(head_uid)
					try:
						point = _coerce_point(head_offset_fn(head_uid, uid_member))
					except ValueError:
						continue
					if module is not None and getattr(module, "__name__", "") == "mathys_optimys_complete":
						point = (-point[0], point[1], point[2])
					if amistem_rotation_deg:
						point = _rotate_z_point(point, amistem_rotation_deg)
					if actis_rotation_deg:
						point = _rotate_z_point(point, actis_rotation_deg)
					if mathys_rotation_x_deg:
						point = _rotate_x_point(point, mathys_rotation_x_deg)
					all_offset_points.append((label, point))
		offset_point = _apply_side_rotation_point(offset_point, args.side, effective_rotate_z_180)
	if all_offset_points:
		all_offset_points = [
				(label, _apply_side_rotation_point(point, args.side, effective_rotate_z_180))
			for label, point in all_offset_points
			if point is not None
		]

	print(f"Resolved side: {args.side}")

	if args.show_neck_point and neck_point is None:
		raise RuntimeError("--show-neck-point requires --neck-point or a seedplan.xml")
	if args.show_cut_plane and (cut_plane_origin is None or cut_plane_normal is None):
		raise RuntimeError("--show-cut-plane requires cut plane inputs or a seedplan.xml")
	if args.show_convex_hull and (cut_plane_origin is None or cut_plane_normal is None):
		raise RuntimeError("--show-convex-hull requires cut plane inputs or a seedplan.xml")
	if (args.envelope_gruen or args.show_envelope_gruen) and (cut_plane_origin is None or cut_plane_normal is None):
		raise RuntimeError("Envelope Gruen zones require cut plane inputs or a seedplan.xml")
	if (args.envelope_gruen or args.show_envelope_gruen) and not args.stem_mc and not args.envelope_gruen_input:
		raise RuntimeError("Envelope Gruen zones require --stem-mc or --envelope-gruen-input")

	voxel_poly = None
	if args.voxel_zones:
		print("Voxel zoning is currently disabled; using triangulated surface instead.")
		args.voxel_zones = False
		voxel_poly = None
	target_poly = poly

	tip_point = None
	bottom_point = None
	if args.show_tip_point or args.show_bottom_point:
		tip_point, bottom_point = _compute_tip_bottom_points(target_poly, neck_point)

	junction_point = None
	if args.show_junction_point:
		if offset_point is None or neck_point is None:
			raise RuntimeError("--show-junction-point requires --show-offset (or --show-all-offsets) and --neck-point")
		if bottom_point is None:
			_tip, bottom_point = _compute_tip_bottom_points(target_poly, neck_point)
		if bottom_point is not None:
			neck_dir = _vec_sub(offset_point, neck_point)
			axis_dir = (0.0, 0.0, 1.0)
			closest = _closest_points_between_lines(neck_point, neck_dir, bottom_point, axis_dir)
			if closest:
				neck_pt, axis_pt = closest
				junction_point = _vec_scale(_vec_add(neck_pt, axis_pt), 0.5)
	if args.show_junction_axes and not args.show_junction_point:
		raise RuntimeError("--show-junction-axes requires --show-junction-point")


	if args.gruen_zones or args.show_gruen_zones or args.gruen_hu_zones or args.partitioned_gruen_viewports:
		_apply_gruen_zones(
			target_poly,
			neck_point,
			cut_plane_origin,
			cut_plane_normal,
			args.side,
			gruen_cut_plane_mode,
		)
		if args.gruen_remapped and (args.partitioned_gruen or args.partitioned_gruen_viewports or args.composite_gruen):
			raise RuntimeError("--gruen-remapped cannot be combined with composite or partitioned Gruen zones")
		if args.largest_region_only:
			if args.voxel_zones:
				_apply_gruen_zones(
					poly,
					neck_point,
					cut_plane_origin,
					cut_plane_normal,
					args.side,
					gruen_cut_plane_mode,
				)
				_apply_largest_region_mask(target_poly, source_poly=poly)
			else:
				_apply_largest_region_mask(target_poly)
		if args.composite_gruen:
			_apply_composite_gruen(target_poly)
		if args.partitioned_gruen or args.partitioned_gruen_viewports:
			_apply_partitioned_gruen(target_poly)
		if args.print_gruen_stats:
			zone_array = (
				target_poly.GetPointData().GetArray("GruenZonePartition")
				or target_poly.GetPointData().GetArray("GruenZoneComposite")
				or target_poly.GetPointData().GetArray("GruenZone")
			)
			if zone_array is not None:
				counts = {idx: 0 for idx in range(1, 15)}
				for idx in range(zone_array.GetNumberOfTuples()):
					zone_id = int(zone_array.GetTuple1(idx))
					if zone_id in counts:
						counts[zone_id] += 1
					print("Gruen zone counts:")
					for zone_id in sorted(counts):
						print(f"  Zone {zone_id}: {counts[zone_id]}")

	if args.envelope_gruen or args.show_envelope_gruen or args.envelope_hu_viewports:
		try:
			band_fractions = _parse_envelope_bands(args.envelope_z_bands)
		except ValueError as exc:
			raise RuntimeError(str(exc)) from exc
		_apply_envelope_gruen_zones(
			target_poly,
			cut_plane_origin,
			cut_plane_normal,
			neck_point,
			mode=args.envelope_gruen_mode,
			band_fractions=band_fractions,
		)
		if args.envelope_top_zones is not None:
			_apply_top_envelope_zones(target_poly, args.envelope_top_zones)
		if args.gruen_remapped:
			source_name = "EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone"
			_apply_gruen_zone_remap(target_poly, source_name, "EnvelopeZoneRemap", args.side)
		zone_array = target_poly.GetPointData().GetArray(
			"EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone"
		)
		if zone_array is not None:
			zone_count, _counts = _count_zone_ids(zone_array)
			print(f"Envelope zones found: {zone_count}")

	if args.gruen_hu_zones or (args.show_envelope_gruen and args.envelope_hu) or args.envelope_hu_viewports:
		metrics_array = _find_metrics_array_for_vtp(args.vtp)
		selected_hu_array = _pick_scalar_array(target_poly, args.hu_array)
		if selected_hu_array is None and metrics_array:
			selected_hu_array = _pick_scalar_array(target_poly, metrics_array)
		if selected_hu_array is None:
			raise RuntimeError("No scalar arrays available for HU masking")
		args.hu_array = selected_hu_array

	active_array = args.array
	color_label = "HU (EZplan LUT)"
	lookup_table: vtk.vtkScalarsToColors
	scalar_range: tuple[float, float]
	label_count = len(EZPLAN_ZONE_DEFS) + 1
	if args.gruen_hu_zones:
		if args.partitioned_gruen:
			zones = _parse_partition_zones(args.gruen_hu_zones)
		else:
			zones = [int(item) for item in args.gruen_hu_zones.split(",") if item.strip()]
		if not zones:
			raise RuntimeError("--gruen-hu-zones must list at least one zone")
		active_array = _apply_hu_zone_mask(target_poly, args.hu_array, zones)
		zone_mask_array = active_array
		display_range = _resolve_hu_range(args.hu_range)
		if display_range is None and args.dominant_hu_zone:
			display_range = _resolve_hu_range(args.dominant_hu_zone)
		if display_range is not None:
			active_array = _apply_hu_range_mask(target_poly, active_array, display_range)
		if args.visible_voxels:
			zone_array = (
				target_poly.GetPointData().GetArray("GruenZonePartition")
				or target_poly.GetPointData().GetArray("GruenZoneComposite")
				or target_poly.GetPointData().GetArray("GruenZone")
			)
			if zone_array is None:
				raise RuntimeError("GruenZone array missing for visibility masking")
			if args.side == "right":
				zone_view_map = {
					1: "right", 2: "right", 3: "right",
					5: "left", 6: "left", 7: "left",
					8: "front", 9: "front", 10: "front",
					12: "back", 13: "back", 14: "back",
					4: "back", 11: "back",
				}
			else:
				zone_view_map = {
					1: "left", 2: "left", 3: "left",
					5: "right", 6: "right", 7: "right",
					8: "front", 9: "front", 10: "front",
					12: "back", 13: "back", 14: "back",
					4: "back", 11: "back",
				}
			views_needed = sorted(set(zone_view_map.values()))
			visible_by_view: dict[str, set[int]] = {}
			for view in views_needed:
				visible_by_view[view] = _compute_visible_ids(target_poly, [view], args.visibility_method)
			active_array = _apply_visibility_mask_by_zone(
				target_poly,
				active_array,
				zone_array,
				visible_by_view,
				zone_view_map,
			)
		lookup_table = _build_ezplan_transfer_function()
		scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
	elif args.show_gruen_zones:
		if args.partitioned_gruen:
			active_array = "GruenZonePartition"
			lookup_table = _build_partition_lookup_table()
			scalar_range = (1.0, 4.0)
			color_label = "Gruen partitions"
			label_count = 4
		elif args.composite_gruen:
			active_array = "GruenZoneComposite"
			lookup_table = _build_gruen_lookup_table()
			scalar_range = (1.0, 14.0)
			color_label = "Gruen zones"
			label_count = 14
		elif args.gruen_remapped:
			source_array = "GruenZoneLargest" if args.largest_region_only else "GruenZone"
			active_array = _apply_gruen_zone_remap(target_poly, source_array, "GruenZoneRemap", args.side)
			lookup_table = _build_gruen_lookup_table()
			scalar_range = (1.0, 14.0)
			color_label = "Gruen zones"
			label_count = 14
		else:
			active_array = "GruenZoneLargest" if args.largest_region_only else "GruenZone"
			lookup_table = _build_gruen_lookup_table()
			scalar_range = (1.0, 14.0)
			color_label = "Gruen zones"
			label_count = 14
	elif args.show_envelope_gruen:
		if args.envelope_hu:
			zone_array_name = (
				"EnvelopeZoneRemap"
				if args.gruen_remapped
				else ("EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone")
			)
			if args.zone_only is None:
				active_array = _apply_hu_presence_mask_by_array(
					target_poly,
					args.hu_array,
					zone_array_name,
				)
			else:
				active_array = _apply_hu_zone_mask_by_array(
					target_poly,
					args.hu_array,
					zone_array_name,
					[args.zone_only],
				)
			lookup_table = _build_ezplan_transfer_function()
			scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
			color_label = "HU (EZplan LUT)"
			label_count = len(EZPLAN_ZONE_DEFS) + 1
		elif args.gruen_remapped:
			active_array = "EnvelopeZoneRemap"
			lookup_table = _build_gruen_lookup_table()
			scalar_range = (1.0, 14.0)
			color_label = "Gruen zones"
			label_count = 14
		else:
			active_array = "EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone"
			lookup_table = _build_envelope_lookup_table()
			scalar_range = (1.0, 12.0)
			color_label = "Envelope zones"
			label_count = 12
	else:
		lookup_table = _build_ezplan_transfer_function()
		scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
	if args.merge_zone_islands and (args.show_gruen_zones or args.show_envelope_gruen):
		active_array = _merge_zone_islands(target_poly, active_array, args.merge_zone_min_points)
	if args.zone_only is not None and (args.show_gruen_zones or args.show_envelope_gruen):
		if not (args.show_envelope_gruen and args.envelope_hu):
			active_array = _apply_zone_only(target_poly, active_array, args.zone_only)

	use_scalar_overlay = True
	nan_color = None
	if args.gruen_hu_zones:
		if base_color is not None:
			nan_color = (base_color[0], base_color[1], base_color[2], 1.0)
		else:
			nan_color = (0.7, 0.7, 0.7, 1.0)

	mapper, array_range, active_array = _configure_mapper(
		target_poly,
		active_array,
		scalar_range=scalar_range,
		lookup_table=lookup_table,
		nan_color=nan_color,
	)
	zone_view = args.show_gruen_zones or args.show_envelope_gruen
	actor_opacity = 1.0 if (args.solid_zones and zone_view) else args.opacity
	if voxel_poly is not None:
		actor = _build_voxel_glyph_actor(target_poly, args.voxel_size, mapper)
		actor.GetProperty().SetOpacity(max(0.0, min(actor_opacity, 1.0)))
	else:
		actor = _build_actor(mapper, args.wireframe, actor_opacity, base_color)
	base_actor = None
	if base_color is not None and use_scalar_overlay:
		base_mapper = vtk.vtkPolyDataMapper()
		base_mapper.SetInputData(poly)
		base_mapper.ScalarVisibilityOff()
		base_actor = _build_actor(base_mapper, args.wireframe, args.opacity, base_color)

	renderer = vtk.vtkRenderer()
	if not args.convex_hull_only:
		if base_actor is not None:
			renderer.AddActor(base_actor)
		renderer.AddActor(actor)
	renderer.SetBackground(1.0, 1.0, 1.0)
	_set_camera_z_up(renderer, target_poly.GetBounds())
	if not args.convex_hull_only:
		_add_scalar_bar(renderer, lookup_table, color_label, label_count)
	if args.show_axes:
		_add_axes(renderer, max(args.axes_size, 1.0))
	if args.show_side_label:
		_add_side_label(renderer, args.side)
	if args.show_hu_summary and args.gruen_hu_zones and args.hu_range:
		hu_range = _resolve_hu_range(args.hu_range)
		if hu_range is not None:
			array = target_poly.GetPointData().GetArray(active_array)
			if array is not None:
				valid = 0
				for idx in range(array.GetNumberOfTuples()):
					value = array.GetTuple1(idx)
					if value == value:
						valid += 1
				total = array.GetNumberOfTuples()
				percent = 100.0 * valid / max(total, 1)
				label = f"{args.hu_range.title()} in zone: {percent:.1f}%"
				_add_hu_summary_label(renderer, label)
	if args.hu_table and args.gruen_hu_zones:
		array_name = zone_mask_array if "zone_mask_array" in locals() else active_array
		array = target_poly.GetPointData().GetArray(array_name)
		if array is not None:
			rows = _compute_hu_table(array)
			print("HU range summary (percent of non-NaN in zone):")
			for label, pct in rows:
				print(f"  {label}: {pct:.1f}%")
			_add_hu_table_label(renderer, rows)
	if args.export_hu_xml:
		if not args.partitioned_gruen:
			raise RuntimeError("--export-hu-xml requires --partitioned-gruen")
		metrics_array = _find_metrics_array_for_vtp(args.vtp)
		selected_hu_array = _pick_scalar_array(target_poly, args.hu_array)
		if selected_hu_array is None and metrics_array:
			selected_hu_array = _pick_scalar_array(target_poly, metrics_array)
		if selected_hu_array is None:
			raise RuntimeError("No scalar arrays available for HU XML export")
		path = _export_partition_hu_xml(args.vtp, target_poly, selected_hu_array)
		print(f"Saved HU summary XML: {path}")
	if args.export_gruen_hu_xml:
		if args.partitioned_gruen or args.composite_gruen:
			raise RuntimeError("--export-gruen-hu-xml requires standard or envelope Gruen zones")
		metrics_array = _find_metrics_array_for_vtp(args.vtp)
		selected_hu_array = _pick_scalar_array(target_poly, args.hu_array)
		if selected_hu_array is None and metrics_array:
			selected_hu_array = _pick_scalar_array(target_poly, metrics_array)
		if selected_hu_array is None:
			raise RuntimeError("No scalar arrays available for Gruen HU XML export")
		export_poly = target_poly
		if args.gruen_hu_remesh and not args.stem_mc and not args.gruen_hu_remesh_input:
			remeshed = _reconstruct_surface_mc(original_poly, args.stem_mc_spacing)
			export_poly = _interpolate_point_arrays(original_poly, remeshed, nearest=True)
			if args.show_envelope_gruen:
				_apply_envelope_gruen_zones(
					export_poly,
					cut_plane_origin,
					cut_plane_normal,
					neck_point,
					mode=args.envelope_gruen_mode,
					band_fractions=_parse_envelope_bands(args.envelope_z_bands),
				)
				if args.envelope_top_zones is not None:
					_apply_top_envelope_zones(export_poly, args.envelope_top_zones)
				if args.gruen_remapped:
					source_name = "EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone"
					_apply_gruen_zone_remap(export_poly, source_name, "EnvelopeZoneRemap", args.side)
			else:
				_apply_gruen_zones(
					export_poly,
					neck_point,
					cut_plane_origin,
					cut_plane_normal,
					args.side,
					gruen_cut_plane_mode,
				)
				if args.largest_region_only:
					_apply_largest_region_mask(export_poly)
				if args.gruen_remapped:
					source_array = "GruenZoneLargest" if args.largest_region_only else "GruenZone"
					_apply_gruen_zone_remap(export_poly, source_array, "GruenZoneRemap", args.side)
		if args.show_envelope_gruen:
			zone_array_name = "EnvelopeZoneRemap" if args.gruen_remapped else (
				"EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone"
			)
			max_zone = 14 if args.gruen_remapped else 12
		else:
			zone_array_name = "GruenZoneRemap" if args.gruen_remapped else (
				"GruenZoneLargest" if args.largest_region_only else "GruenZone"
			)
			max_zone = 14
		bottom_point_export = None
		if args.gruen_bottom_sphere_radius > 0:
			_tip, bottom_point_export = _compute_tip_bottom_points(export_poly, neck_point)
		path = _export_gruen_hu_xml(
			args.vtp,
			export_poly,
			selected_hu_array,
			zone_array_name,
			max_zone=max_zone,
			bottom_point=bottom_point_export,
			bottom_radius=args.gruen_bottom_sphere_radius,
		)
		print(f"Saved Gruen HU summary XML: {path}")
	dominant_zone = None
	if args.dominant_hu_zone:
		hu_range = _resolve_hu_range(args.dominant_hu_zone)
		if hu_range is None:
			raise RuntimeError("Unknown HU tag for --dominant-hu-zone")
		dominant_zone, percent = _compute_dominant_hu_zone(target_poly, args.hu_array, hu_range)
		if dominant_zone is not None:
			message = f"Dominant {args.dominant_hu_zone.title()} zone: {dominant_zone} ({percent:.1f}%)"
			print(message)
			if args.show_dominant_hu_zone:
				_add_dominant_zone_label(renderer, message)
	if args.headless:
		_print_summary(args.vtp, active_array, array_range, color_label)
		return 0
	if args.envelope_hu_viewports:
		if args.envelope_hu_cortical and args.envelope_hu_stable:
			raise RuntimeError("--envelope-hu-cortical and --envelope-hu-stable cannot be combined")
		if args.zone_only is None and not (args.envelope_hu_cortical or args.envelope_hu_stable):
			raise RuntimeError("--envelope-hu-viewports requires --zone-only or --envelope-hu-cortical/--envelope-hu-stable")
		zone_array_name = (
			"EnvelopeZoneRemap"
			if args.gruen_remapped
			else ("EnvelopeZoneTop" if args.envelope_top_zones is not None else "EnvelopeZone")
		)
		cortical_zones: list[int] | None = None
		if args.envelope_hu_cortical:
			cortical_zones = _find_zones_with_hu_range_by_array(
				target_poly,
				args.hu_array,
				zone_array_name,
				(1000.0, 1500.0),
			)
			if not cortical_zones:
				print("Warning: no cortical zones detected for the current HU range.")
		stable_zones: list[int] | None = None
		if args.envelope_hu_stable:
			stable_zones = _find_zones_with_hu_range_by_array(
				target_poly,
				args.hu_array,
				zone_array_name,
				(400.0, 1000.0),
			)
			if not stable_zones:
				print("Warning: no stable zones detected for the current HU range.")
		full_lookup = _build_ezplan_transfer_function()
		full_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
		zone_lookup = full_lookup
		zone_range = full_range
		full_nan_color = None
		zone_nan_color = None
		if base_color is not None:
			full_nan_color = (base_color[0], base_color[1], base_color[2], 1.0)
			zone_nan_color = (base_color[0], base_color[1], base_color[2], 1.0)
		else:
			full_nan_color = (0.7, 0.7, 0.7, 1.0)
			zone_nan_color = (0.7, 0.7, 0.7, 1.0)
		viewports = [
			(0.0, 0.0, 0.5, 1.0),
			(0.5, 0.0, 1.0, 1.0),
		]
		labels = [
			"HU (full)",
			"HU (zone)",
		]
		render_window = vtk.vtkRenderWindow()
		render_window.SetWindowName("Stem Viewer (Envelope HU viewports)")
		render_window.SetSize(1100, 700)
		window_width, _window_height = render_window.GetSize()
		for idx, viewport in enumerate(viewports):
			viewport_poly = vtk.vtkPolyData()
			viewport_poly.ShallowCopy(target_poly)
			if idx == 0:
				active = args.hu_array
				lookup = full_lookup
				scalar_range = full_range
				nan_color = full_nan_color
				opacity = 1.0
			else:
				if cortical_zones is not None:
					zones_for_mask = cortical_zones
				elif stable_zones is not None:
					zones_for_mask = stable_zones
				else:
					zones_for_mask = [args.zone_only]
				active = _apply_hu_zone_mask_by_array(
					viewport_poly,
					args.hu_array,
					zone_array_name,
					zones_for_mask,
				)
				lookup = zone_lookup
				scalar_range = zone_range
				nan_color = zone_nan_color
				opacity = args.opacity
			mapper, _range, _array = _configure_mapper(
				viewport_poly,
				active,
				scalar_range=scalar_range,
				lookup_table=lookup,
				nan_color=nan_color,
			)
			renderer = vtk.vtkRenderer()
			renderer.SetViewport(*viewport)
			renderer.SetBackground(1.0, 1.0, 1.0)
			if base_color is not None:
				base_mapper = vtk.vtkPolyDataMapper()
				base_mapper.SetInputData(viewport_poly)
				base_mapper.ScalarVisibilityOff()
				base_opacity = min(0.25, opacity)
				base_actor = _build_actor(base_mapper, args.wireframe, base_opacity, base_color)
				renderer.AddActor(base_actor)
			actor = _build_actor(mapper, args.wireframe, opacity, None)
			renderer.AddActor(actor)
			label_x = int(viewport[0] * window_width) + 10
			_add_scalar_bar(
				renderer,
				lookup,
				"HU (EZplan LUT)",
				len(EZPLAN_ZONE_DEFS) + 1,
				position_x=0.82,
				position_y=0.20,
				title_separation=12,
			)
			if idx == 0:
				_add_viewport_label(renderer, labels[idx], x=label_x, y=80)
			if idx == 1:
				if cortical_zones is not None:
					zone_list = ", ".join(str(zone_id) for zone_id in cortical_zones) if cortical_zones else "none"
					_add_viewport_label(renderer, f"Cortical zones: {zone_list}", x=label_x, y=80)
				elif stable_zones is not None:
					zone_list = ", ".join(str(zone_id) for zone_id in stable_zones) if stable_zones else "none"
					_add_viewport_label(renderer, f"Stable zones: {zone_list}", x=label_x, y=80)
				else:
					_add_viewport_label(renderer, f"Gruen zone: {args.zone_only}", x=label_x, y=80)
			if args.show_axes:
				_add_axes(renderer, max(args.axes_size, 1.0))
			if args.show_side_label:
				_add_side_label(renderer, args.side)
			if args.show_cut_plane and cut_plane_origin is not None and cut_plane_normal is not None:
				plane_actor = _build_cut_plane_actor(cut_plane_origin, cut_plane_normal, args.cut_plane_size)
				if plane_actor is not None:
					renderer.AddActor(plane_actor)
			_set_camera_z_up(renderer, viewport_poly.GetBounds())
			render_window.AddRenderer(renderer)
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(render_window)
		style = vtk.vtkInteractorStyleTrackballCamera()
		interactor.SetInteractorStyle(style)
		_print_summary(args.vtp, active_array, array_range, color_label)
		interactor.Initialize()
		render_window.Render()
		interactor.Start()
		return 0
	if args.partitioned_gruen_viewports:
		partition_array = target_poly.GetPointData().GetArray("GruenZonePartition")
		if partition_array is None:
			raise RuntimeError("Partitioned viewports require GruenZonePartition")
		metrics_array = _find_metrics_array_for_vtp(args.vtp)
		selected_hu_array = _pick_scalar_array(target_poly, args.hu_array)
		if selected_hu_array is None and metrics_array:
			selected_hu_array = _pick_scalar_array(target_poly, metrics_array)
		if selected_hu_array is None:
			raise RuntimeError("No scalar arrays available for HU heatmap")
		viewport_lookup = _build_ezplan_transfer_function()
		viewport_scalar_range = (EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
		viewport_nan_color = None
		if base_color is not None:
			viewport_nan_color = (base_color[0], base_color[1], base_color[2], 1.0)
		else:
			viewport_nan_color = (0.7, 0.7, 0.7, 1.0)
		viewport_range = _resolve_hu_range(args.hu_range) if args.hu_range else None
		base_rgb = base_color if base_color is not None else (0.75, 0.75, 0.75)
		partition_labels = [
			("Top", 1, (0.2, 0.6, 1.0)),
			("Medium top", 2, (0.2, 0.8, 0.2)),
			("Medium bottom", 3, (0.9, 0.7, 0.2)),
			("Bottom", 4, (0.8, 0.2, 0.2)),
		]
		viewports = [
			(0.0, 0.5, 0.5, 1.0),
			(0.5, 0.5, 1.0, 1.0),
			(0.0, 0.0, 0.5, 0.5),
			(0.5, 0.0, 1.0, 0.5),
		]
		render_window = vtk.vtkRenderWindow()
		render_window.SetWindowName("Stem Viewer (Partitioned Gruen)")
		render_window.SetSize(1100, 850)
		for (label, zone_id, color), viewport in zip(partition_labels, viewports):
			renderer = vtk.vtkRenderer()
			renderer.SetViewport(*viewport)
			renderer.SetBackground(1.0, 1.0, 1.0)
			viewport_poly = vtk.vtkPolyData()
			viewport_poly.ShallowCopy(target_poly)
			viewport_active = _apply_hu_zone_mask(viewport_poly, selected_hu_array, [zone_id])
			if viewport_range is not None:
				viewport_active = _apply_hu_range_mask(viewport_poly, viewport_active, viewport_range)
			viewport_mapper, _viewport_range, _viewport_array = _configure_mapper(
				viewport_poly,
				viewport_active,
				scalar_range=viewport_scalar_range,
				lookup_table=viewport_lookup,
				nan_color=viewport_nan_color,
			)
			if base_color is not None and use_scalar_overlay:
				base_mapper = vtk.vtkPolyDataMapper()
				base_mapper.SetInputData(viewport_poly)
				base_mapper.ScalarVisibilityOff()
				base_actor = _build_actor(base_mapper, args.wireframe, args.opacity, base_rgb)
				renderer.AddActor(base_actor)
			viewport_actor = _build_actor(viewport_mapper, args.wireframe, args.opacity, base_color)
			renderer.AddActor(viewport_actor)
			_add_viewport_label(renderer, f"Partition: {label}")
			if args.show_axes:
				_add_axes(renderer, max(args.axes_size, 1.0))
			_set_camera_z_up(renderer, viewport_poly.GetBounds())
			render_window.AddRenderer(renderer)
		interactor = vtk.vtkRenderWindowInteractor()
		interactor.SetRenderWindow(render_window)
		style = vtk.vtkInteractorStyleTrackballCamera()
		interactor.SetInteractorStyle(style)
		_print_summary(args.vtp, active_array, array_range, color_label)
		interactor.Initialize()
		render_window.Render()
		interactor.Start()
		return 0
	if args.show_neck_point and neck_point is not None:
		neck_actor = _build_neck_point_actor(neck_point)
		renderer.AddActor(neck_actor)
	if args.show_tip_point and tip_point is not None:
		tip_actor = _build_tip_point_actor(tip_point)
		renderer.AddActor(tip_actor)
	if args.show_bottom_point and bottom_point is not None:
		bottom_actor = _build_bottom_point_actor(bottom_point)
		renderer.AddActor(bottom_actor)
	if args.show_offset and offset_point is not None:
		offset_actor = _build_offset_actor(offset_point, OFFSET_COLORS[0])
		renderer.AddActor(offset_actor)
	if args.show_all_offsets and all_offset_points:
		for idx, (label, point) in enumerate(all_offset_points):
			if offset_point is not None and offset_head_label == label:
				continue
			color = OFFSET_COLORS[idx % len(OFFSET_COLORS)]
			if point is not None:
				offset_actor = _build_offset_actor(point, color)
				renderer.AddActor(offset_actor)
	if args.show_junction_point and junction_point is not None:
		junction_actor = _build_junction_actor(junction_point)
		renderer.AddActor(junction_actor)
	if args.show_junction_axes and junction_point is not None and offset_point is not None and bottom_point is not None:
		axis1 = _build_line_actor(offset_point, junction_point, color=(0.9, 0.4, 0.2), radius=0.7)
		axis2 = _build_line_actor(junction_point, bottom_point, color=(0.2, 0.6, 0.9), radius=0.7)
		renderer.AddActor(axis1)
		renderer.AddActor(axis2)
	if args.show_cut_plane and cut_plane_origin is not None and cut_plane_normal is not None:
		plane_actor = _build_cut_plane_actor(cut_plane_origin, cut_plane_normal, args.cut_plane_size)
		if plane_actor is not None:
			renderer.AddActor(plane_actor)
	if args.show_normals:
		normals_actor = _build_normals_actor(target_poly, args.normal_scale)
		if normals_actor is not None:
			renderer.AddActor(normals_actor)
		else:
			print("Warning: unable to compute point normals for visualization.", file=sys.stderr)
	if args.show_convex_hull:
		convex_color = convex_color or (0.2, 0.2, 0.2)
		hull_cache_path = None
		if args.cache_remesh and args.convex_hull_mc:
			hull_cache_path = (
				Path(args.vtp).resolve().parent
				/ (
					f"{Path(args.vtp).stem}_hull_mc_{args.convex_hull_mc_spacing:.3f}"
					f"_iso{int(args.remesh_iso)}_t{args.remesh_target}_s{args.remesh_subdivide}.vtp"
				)
			)
		hull_actor = _build_convex_hull_actor(
			target_poly,
			cut_plane_origin,
			cut_plane_normal,
			convex_color,
			args.convex_hull_opacity,
			args.remesh_iso,
			args.remesh_target,
			args.remesh_subdivide,
			args.convex_hull_mc,
			args.convex_hull_mc_spacing,
			hull_cache_path,
			args.cache_remesh_refresh,
		)
		if hull_actor is not None:
			renderer.AddActor(hull_actor)
		else:
			print("Warning: unable to compute convex hull for the current mesh.", file=sys.stderr)
	if args.show_envelope_contours:
		if args.show_envelope_gruen or args.envelope_hu:
			contour_actor = _build_zone_contours_actor(target_poly, "EnvelopeZone", 12)
			if contour_actor is not None:
				renderer.AddActor(contour_actor)
	if args.show_zone_contours:
		if args.show_envelope_gruen or args.envelope_hu:
			contour_actor = _build_zone_contours_actor(target_poly, "EnvelopeZone", 12)
		elif args.show_gruen_zones:
			max_zone = 4 if args.partitioned_gruen else (14 if not args.composite_gruen else 14)
			array_name = "GruenZonePartition" if args.partitioned_gruen else (
				"GruenZoneComposite" if args.composite_gruen else "GruenZoneLargest"
			)
			contour_actor = _build_zone_contours_actor(target_poly, array_name, max_zone)
		else:
			contour_actor = None
		if contour_actor is not None:
			renderer.AddActor(contour_actor)
	if args.highlight_dominant_hu_zone and dominant_zone is not None:
		zone_array = _pick_zone_array(target_poly.GetPointData())
		if zone_array is not None:
			overlay = _build_zone_overlay_actor(target_poly, zone_array.GetName(), dominant_zone)
			if overlay is not None:
				renderer.AddActor(overlay)

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
