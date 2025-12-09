#!/usr/bin/env python3
"""Launch 3D Slicer, load a NIfTI volume, and inject an implant stem from a seedplan."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import tempfile
import textwrap
from string import Template
from typing import Optional

from load_nifti_with_slicer import find_slicer_executable


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load a NIfTI volume together with the femoral stem encoded in a seedplan.xml file."
    )
    parser.add_argument(
        "--nifti",
        required=True,
        help="Path to the NIfTI file to visualize (.nii or .nii.gz)",
    )
    parser.add_argument(
        "--seedplan",
        required=True,
        help="Path to the seedplan.xml file containing the femoral stem definition",
    )
    parser.add_argument(
        "--slicer-path",
        dest="slicer_path",
        default=None,
        help="Path to the Slicer executable (defaults to $SLICER_EXECUTABLE or PATH lookup)",
    )
    parser.add_argument(
        "--stem-length",
        type=float,
        default=120.0,
        help="Placeholder stem cylinder length in millimeters (default: 120)",
    )
    parser.add_argument(
        "--stem-radius",
        type=float,
        default=7.0,
        help="Placeholder stem cylinder radius in millimeters (default: 7)",
    )
    parser.add_argument(
        "--stl-folder",
        dest="stl_folders",
        action="append",
        default=[],
        help=(
            "Directory to search for implant surface models (repeatable). "
            "If provided, the script attempts to load the matching STL using view_implant's search logic; "
            "otherwise it falls back to a procedural cylinder."
        ),
    )
    parser.add_argument(
        "--compute-stem-scalars",
        action="store_true",
        help="Probe the image volume onto the stem geometry and attach the resulting scalar field",
    )
    parser.add_argument(
        "--pre-transform-lps-to-ras",
        action="store_true",
        help="Apply a pre-multiplication that converts LPS coordinates to RAS before seedplan transforms",
    )
    parser.add_argument(
        "--pre-rotate-z-180",
        action="store_true",
        help="Rotate the stem 180 degrees around the Z axis before applying the seedplan transform",
    )
    parser.add_argument(
        "--post-rotate-z-180",
        action="store_true",
        help="Rotate the stem 180 degrees around the Z axis after applying the seedplan transform",
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
    parser.add_argument(
        "--rotation-mode",
        choices=["auto", "mathys", "johnson", "none"],
        default="auto",
        help="Override automatic manufacturer-based rotation handling",
    )
    parser.add_argument(
        "--export-stem-screenshots",
        action="store_true",
        help=(
            "Capture four PNG screenshots (AP front/back, sagittal left/right) of the stem with its LUT "
            "applied and store them next to the NIfTI volume"
        ),
    )
    parser.add_argument(
        "--exit-after-run",
        action="store_true",
        help=(
            "Request the launched Slicer instance to close itself once processing finishes (useful when running with a GUI)"
        ),
    )
    return parser.parse_args()


def build_slicer_script(
    volume_path: str,
    seedplan_path: str,
    repo_root: str,
    stem_length: float,
    stem_radius: float,
    stl_folders: list[str],
    pre_transform_lps_to_ras: bool,
    pre_rotate_z_180: bool,
    post_rotate_z_180: bool,
    compute_stem_scalars: bool,
    rotation_mode: str,
    export_stem_screenshots: bool,
    exit_after_run: bool,
) -> str:
    stl_folders_literal = "[{}]".format(
        ", ".join(f"r\"{folder}\"" for folder in stl_folders)
    )
    template = Template(textwrap.dedent(
        """
        import os
        import sys
        import xml.etree.ElementTree as ET
        import slicer
        import vtk
        import qt

        REPO_ROOT = r"$REPO_ROOT"
        if REPO_ROOT and REPO_ROOT not in sys.path:
            sys.path.insert(0, REPO_ROOT)

        try:
            from implant_registry import resolve_stem_uid
        except Exception:
            resolve_stem_uid = None

        VOLUME_PATH = r"$VOLUME_PATH"
        SEEDPLAN_PATH = r"$SEEDPLAN_PATH"
        STEM_LENGTH = $STEM_LENGTH
        STEM_RADIUS = $STEM_RADIUS
        STL_ROOTS = $STL_ROOTS
        PRE_TRANSFORM_LPS_TO_RAS = $PRE_TRANSFORM_LPS_TO_RAS
        PRE_ROTATE_Z_180 = $PRE_ROTATE_Z_180
        POST_ROTATE_Z_180 = $POST_ROTATE_Z_180
        COMPUTE_STEM_SCALARS = $COMPUTE_STEM_SCALARS
        EXPORT_STEM_SCREENSHOTS = $EXPORT_STEM_SCREENSHOTS
        AUTO_ROTATION_MODE = r"$AUTO_ROTATION_MODE"
        EXIT_AFTER_RUN = $EXIT_AFTER_RUN
        SCREENSHOT_DIR = os.path.join(os.path.dirname(SEEDPLAN_PATH), "Slicer-exports")
        EZPLAN_LUT_NAME = "EZplan HU Zones"
        EZPLAN_LUT_CATEGORY = "Implant Scalars"
        EZPLAN_ZONE_DEFS = [
            (-200.0, 100.0, (0.0, 0.0, 1.0), "Loosening"),
            (100.0, 400.0, (1.0, 0.0, 1.0), "MicroMove"),
            (400.0, 1000.0, (0.0, 1.0, 0.0), "Stable"),
            (1000.0, 1500.0, (1.0, 0.0, 0.0), "Cortical"),
        ]
        OUTPUT_DIR_CLEARED = False

        if not os.path.exists(VOLUME_PATH):
            raise FileNotFoundError(VOLUME_PATH)
        if not os.path.exists(SEEDPLAN_PATH):
            raise FileNotFoundError(SEEDPLAN_PATH)

        IDENTITY_4X4 = [
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            0.0, 0.0, 0.0, 1.0,
        ]

        def _parse_matrix(value):
            values = [float(x) for x in value.strip().split()]
            if len(values) != 16:
                raise ValueError("Stem matrix expected 16 values, got {}".format(len(values)))
            return values

        def _flip_polydata_lps_to_ras(polydata):
            if polydata is None:
                return None
            flip = vtk.vtkTransform()
            flip.Scale(-1.0, -1.0, 1.0)
            transformer = vtk.vtkTransformPolyDataFilter()
            transformer.SetTransform(flip)
            transformer.SetInputData(polydata)
            transformer.Update()
            return transformer.GetOutput()

        def _right_multiply(target, operand):
            temp = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(target, operand, temp)
            target.DeepCopy(temp)

        def _left_multiply(target, operand):
            temp = vtk.vtkMatrix4x4()
            vtk.vtkMatrix4x4.Multiply4x4(operand, target, temp)
            target.DeepCopy(temp)

        def _lower_markers(info):
            markers = (
                info.get("manufacturer"),
                info.get("stem_enum_name"),
                info.get("stem_friendly_name"),
            )
            return [marker.lower() for marker in markers if marker]

        def _needs_mathys_flip(info):
            for marker in _lower_markers(info):
                if "mathys" in marker:
                    return True
            return False

        def _resolve_rotation_mode(info):
            mode = (AUTO_ROTATION_MODE or "").strip().lower()
            if mode and mode != "auto":
                return mode
            markers = _lower_markers(info)
            if any("mathys" in marker for marker in markers):
                return "mathys"
            if any("actis" in marker or "corail" in marker for marker in markers):
                return "johnson"
            return "none"

        def _ensure_ezplan_lut():
            existing = slicer.mrmlScene.GetFirstNodeByName(EZPLAN_LUT_NAME)
            if existing and existing.IsA("vtkMRMLColorNode"):
                return existing
            color_node = slicer.vtkMRMLProceduralColorNode()
            color_node.SetName(EZPLAN_LUT_NAME)
            color_node.SetAttribute("Category", EZPLAN_LUT_CATEGORY)
            color_tf = vtk.vtkColorTransferFunction()
            for zone_min, zone_max, (r, g, b), label in EZPLAN_ZONE_DEFS:
                color_tf.AddRGBPoint(zone_min, r, g, b)
                color_tf.AddRGBPoint(zone_max, r, g, b)
            color_node.SetAndObserveColorTransferFunction(color_tf)
            color_node.SetAttribute("lut.source", "load_nifti_and_stem")
            slicer.mrmlScene.AddNode(color_node)
            print("Registered color node '%s' for stem scalar visualization" % EZPLAN_LUT_NAME)
            return color_node

        def _apply_scalar_display(model_node, array_name, color_node):
            if not model_node or not color_node:
                return
            if not model_node.GetDisplayNode():
                model_node.CreateDefaultDisplayNodes()
            display = model_node.GetDisplayNode()
            if not display:
                return
            display.SetScalarVisibility(True)
            display.SetAndObserveColorNodeID(color_node.GetID())
            zone_min = EZPLAN_ZONE_DEFS[0][0]
            zone_max = EZPLAN_ZONE_DEFS[-1][1]
            display.SetScalarRange(zone_min, zone_max)
            poly_data = model_node.GetPolyData()
            if poly_data:
                point_data = poly_data.GetPointData()
                if point_data:
                    array = point_data.GetArray(array_name)
                    if array:
                        point_data.SetActiveScalars(array_name)
                        poly_data.Modified()

        def _copy_scalar_array(source_node, target_node, array_name):
            if source_node is target_node:
                return
            if not source_node or not target_node:
                return
            source_poly = source_node.GetPolyData()
            target_poly = target_node.GetPolyData()
            if not source_poly or not target_poly:
                return
            source_array = source_poly.GetPointData().GetArray(array_name)
            if source_array is None:
                return
            new_array = vtk.vtkDoubleArray()
            new_array.DeepCopy(source_array)
            point_data = target_poly.GetPointData()
            existing = point_data.GetArray(array_name)
            if existing:
                point_data.RemoveArray(array_name)
            point_data.AddArray(new_array)
            point_data.SetActiveScalars(array_name)
            target_poly.Modified()

        def _stem_output_prefix(clear_dir=False):
            global OUTPUT_DIR_CLEARED
            if not os.path.isdir(SCREENSHOT_DIR):
                os.makedirs(SCREENSHOT_DIR, exist_ok=True)
                print("Created screenshot directory: %s" % SCREENSHOT_DIR)
            if clear_dir and not OUTPUT_DIR_CLEARED:
                print("Clearing existing exports in: %s" % SCREENSHOT_DIR)
                for entry in os.listdir(SCREENSHOT_DIR):
                    path = os.path.join(SCREENSHOT_DIR, entry)
                    try:
                        if os.path.isfile(path):
                            os.remove(path)
                        elif os.path.isdir(path):
                            import shutil
                            shutil.rmtree(path)
                    except Exception as exc:
                        print("Warning: unable to remove '%s' (%s)" % (path, exc))
                OUTPUT_DIR_CLEARED = True
            base = os.path.basename(VOLUME_PATH)
            lower = base.lower()
            if lower.endswith(".nii.gz"):
                base = base[:-7]
            else:
                base = os.path.splitext(base)[0]
            return os.path.join(SCREENSHOT_DIR, base + "_stem")

        def _configure_view_background(view_node):
            if not view_node:
                return
            if hasattr(view_node, "SetUseGradientBackground"):
                view_node.SetUseGradientBackground(False)
            view_node.SetBackgroundColor(1.0, 1.0, 1.0)
            if hasattr(view_node, "SetBackgroundColor2"):
                view_node.SetBackgroundColor2(1.0, 1.0, 1.0)
            if hasattr(view_node, "SetOrientationMarkerType"):
                try:
                    view_node.SetOrientationMarkerType(view_node.OrientationMarkerTypeNone)
                except AttributeError:
                    pass
            if hasattr(view_node, "SetBoxVisible"):
                view_node.SetBoxVisible(False)

        def _capture_stem_screenshots(model_node):
            poly = model_node.GetPolyData()
            if poly is None:
                print("Model has no polydata; skipping screenshots")
                return
            layout_manager = slicer.app.layoutManager()
            if layout_manager is None:
                raise RuntimeError(
                    "Screenshot capture requires a GUI session (layout manager unavailable; run without --no-main-window)"
                )
            widget = layout_manager.threeDWidget(0)
            if widget is None:
                print("No 3D widget available; skipping screenshots")
                return
            view = widget.threeDView()
            view_node = view.mrmlViewNode()
            _configure_view_background(view_node)
            cameras_logic = slicer.modules.cameras.logic()
            camera_node = None
            if hasattr(cameras_logic, "GetCameraNode"):
                camera_node = cameras_logic.GetCameraNode(view_node)
            if camera_node is None and hasattr(cameras_logic, "GetViewActiveCameraNode"):
                camera_node = cameras_logic.GetViewActiveCameraNode(view_node)
            if camera_node is None:
                try:
                    camera_node = slicer.modules.cameras.logic().GetActiveCameraNode()
                except AttributeError:
                    camera_node = None
            if camera_node is None:
                print("Unable to locate camera node; creating temporary camera")
                camera_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLCameraNode", "ScreenshotCamera")
                if camera_node:
                    camera_node.SetAndObserveViewNodeID(view_node.GetID())
                else:
                    print("Failed to create camera node; skipping screenshots")
                    return
            camera = camera_node.GetCamera()
            if camera is None:
                print("Camera node missing vtkCamera; skipping screenshots")
                return
            camera.ParallelProjectionOn()
            bounds = [0.0] * 6
            poly.GetBounds(bounds)
            center = [
                0.5 * (bounds[0] + bounds[1]),
                0.5 * (bounds[2] + bounds[3]),
                0.5 * (bounds[4] + bounds[5]),
            ]
            max_extent = max(bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])
            if max_extent <= 0:
                max_extent = 100.0
            distance = max_extent * 2.5
            half_extent = max_extent * 0.5
            orientations = [
                ("AP_front", (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
                ("AP_back", (0.0, -1.0, 0.0), (0.0, 0.0, 1.0)),
                ("SAG_left", (-1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
                ("SAG_right", (1.0, 0.0, 0.0), (0.0, 0.0, 1.0)),
            ]
            prefix = _stem_output_prefix(clear_dir=True)
            for label, axis, up in orientations:
                position = [center[i] + axis[i] * distance for i in range(3)]
                camera.SetFocalPoint(*center)
                camera.SetPosition(*position)
                camera.SetViewUp(*up)
                camera.SetParallelScale(max(half_extent, 1.0))
                camera.Modified()
                view.renderWindow().Render()
                qt.QApplication.processEvents()
                file_path = "{}_{}.png".format(prefix, label)
                pixmap = view.grab()
                pixmap.save(file_path)
                print("Saved screenshot: %s" % file_path)

        def _export_original_stem(model_node):
            poly = model_node.GetPolyData()
            if poly is None:
                print("Model has no polydata; skipping stem export")
                return
            prefix = _stem_output_prefix(clear_dir=True)
            file_path = prefix + "_original.vtp"
            writer = vtk.vtkXMLPolyDataWriter()
            writer.SetFileName(file_path)
            writer.SetInputData(poly)
            writer.SetDataModeToBinary()
            try:
                success = writer.Write()
            except Exception as exc:
                print("Warning: unable to write original stem export (%s)" % exc)
                return
            if success == 0:
                print("Warning: vtkXMLPolyDataWriter reported failure for %s" % file_path)
            else:
                print("Saved original (non-hardened) stem with scalars: %s" % file_path)

        def _probe_volume_onto_model(volume_node, model_node, array_name=None):
            image_data = volume_node.GetImageData()
            if not image_data:
                raise RuntimeError("Volume node has no image data to sample")
            source_poly_data = model_node.GetPolyData()
            if not source_poly_data:
                raise RuntimeError("Model node has no polydata to sample")

            sampling_poly = vtk.vtkPolyData()
            parent_transform = model_node.GetParentTransformNode()
            if parent_transform:
                clone_node = slicer.mrmlScene.AddNewNodeByClass(
                    "vtkMRMLModelNode",
                    "StemSamplingClone",
                )
                clone_poly = vtk.vtkPolyData()
                clone_poly.DeepCopy(source_poly_data)
                clone_node.SetAndObservePolyData(clone_poly)
                clone_node.SetAndObserveTransformNodeID(parent_transform.GetID())
                clone_node.HardenTransform()
                clone_node.SetAndObserveTransformNodeID(None)
                sampling_poly.DeepCopy(clone_node.GetPolyData())
                slicer.mrmlScene.RemoveNode(clone_node)
            else:
                sampling_poly.DeepCopy(source_poly_data)

            source_array = image_data.GetPointData().GetScalars()
            source_name = None
            if source_array is not None:
                source_name = source_array.GetName()
                source_range = source_array.GetRange()
                if source_range:
                    print(
                        "Volume scalar '%s' range: %.2f .. %.2f"
                        % (
                            source_name or "ImageScalars",
                            source_range[0],
                            source_range[1],
                        )
                    )
            if not array_name:
                array_name = source_name or "ImageScalars"
            print("Sampling model '%s' using scalar array '%s'" % (model_node.GetName(), array_name))

            sampling_poly_ijk = vtk.vtkPolyData()
            ras_to_ijk_matrix = vtk.vtkMatrix4x4()
            volume_node.GetRASToIJKMatrix(ras_to_ijk_matrix)
            ras_to_ijk_transform = vtk.vtkTransform()
            ras_to_ijk_transform.SetMatrix(ras_to_ijk_matrix)
            ras_to_ijk_filter = vtk.vtkTransformPolyDataFilter()
            ras_to_ijk_filter.SetTransform(ras_to_ijk_transform)
            ras_to_ijk_filter.SetInputData(sampling_poly)
            ras_to_ijk_filter.Update()
            sampling_poly_ijk.DeepCopy(ras_to_ijk_filter.GetOutput())

            probe = vtk.vtkProbeFilter()
            probe.SetInputData(sampling_poly_ijk)
            probe.SetSourceData(image_data)
            probe.Update()

            sampled = probe.GetOutput()
            sampled_point_data = sampled.GetPointData()
            scalar_array = sampled_point_data.GetScalars()
            if scalar_array is None:
                raise RuntimeError("Probe filter did not produce a scalar array")

            scalar_array.SetName(array_name)
            copied_array = vtk.vtkDoubleArray()
            copied_array.DeepCopy(scalar_array)
            target_point_data = source_poly_data.GetPointData()
            existing = target_point_data.GetArray(array_name)
            if existing:
                target_point_data.RemoveArray(array_name)
            target_point_data.AddArray(copied_array)
            target_point_data.SetActiveScalars(array_name)
            source_poly_data.Modified()
            sampled_range = copied_array.GetRange()
            if sampled_range:
                print(
                    "Model '%s' scalar '%s' range: %.2f .. %.2f"
                    % (model_node.GetName(), array_name, sampled_range[0], sampled_range[1])
                )
            return source_poly_data

        def _print_scalar_percentages(model_node, array_name="ImageScalars"):
            poly_data = model_node.GetPolyData()
            if not poly_data:
                print("No polydata available on model '%s'" % model_node.GetName())
                return
            array = poly_data.GetPointData().GetArray(array_name)
            if array is None:
                print("No scalar field named '%s' on model '%s'" % (array_name, model_node.GetName()))
                return
            num_points = poly_data.GetNumberOfPoints()
            if num_points == 0:
                print("Model '%s' has no points to summarize" % model_node.GetName())
                return
            zones = {
                "Loosening": (-200.0, 100.0),
                "MicroMove": (100.0, 400.0),
                "Stable": (400.0, 1000.0),
                "Cortical": (1000.0, 1500.0),
            }
            zone_counts = {name: 0 for name in zones}
            for idx in range(num_points):
                value = array.GetTuple1(idx)
                for zone_name, (low, high) in zones.items():
                    if low <= value < high:
                        zone_counts[zone_name] += 1
                        break
            print("Zone distribution for '%s' (array '%s'):" % (model_node.GetName(), array_name))
            for zone_name, count in zone_counts.items():
                pct = count / num_points * 100.0
                print("  %-10s %6d pts (%5.2f%%)" % (zone_name + ":", count, pct))

        def _extract_stem_info(xml_path):
            tree = ET.parse(xml_path)
            root = tree.getroot()
            hip_configs = root.findall(".//hipImplantConfig")
            history_configs = root.findall(".//hipImplantConfigHistoryList/hipImplantConfig")
            for source_label, configs in (("active", hip_configs), ("history", history_configs)):
                for hip_config in configs:
                    fem_config = hip_config.find("./femImplantConfig")
                    if fem_config is None:
                        continue
                    stem_shape = fem_config.find(".//s3Shape[@part='stem']")
                    if stem_shape is None:
                        continue
                    info = {}
                    info["requested_side"] = fem_config.attrib.get("requestedSide")
                    info["configured_side"] = fem_config.attrib.get("side")
                    info["state"] = fem_config.attrib.get("state")
                    info["source"] = source_label
                    uid_attr = stem_shape.attrib.get("uid")
                    if uid_attr:
                        try:
                            uid_val = int(uid_attr)
                        except ValueError:
                            uid_val = None
                        else:
                            info["uid"] = uid_val
                            if resolve_stem_uid:
                                lookup = resolve_stem_uid(uid_val)
                                if lookup:
                                    info["manufacturer"] = lookup.manufacturer
                                    info["stem_enum_name"] = lookup.enum_name
                                    info["stem_friendly_name"] = lookup.friendly_name
                                    info["rcc_id"] = lookup.rcc_id
                    matrix_elem = stem_shape.find("matrix4[@name='mat']")
                    if matrix_elem is None:
                        matrix_elem = stem_shape.find("matrix4")
                    if matrix_elem is not None:
                        info["matrix_raw"] = matrix_elem.attrib.get("value")
                    local_elem = stem_shape.find("matrix4[@name='localMat']")
                    if local_elem is not None:
                        info["local_matrix_raw"] = local_elem.attrib.get("value")
                    return info
            raise RuntimeError("Unable to locate femoral stem definition in seedplan")

        stem_info = _extract_stem_info(SEEDPLAN_PATH)
        matrix_raw = stem_info.get("matrix_raw")
        if not matrix_raw:
            raise RuntimeError("Stem matrix missing in {}".format(SEEDPLAN_PATH))
        matrix_vals = _parse_matrix(matrix_raw)
        local_matrix_raw = stem_info.get("local_matrix_raw")
        if local_matrix_raw:
            try:
                local_matrix_vals = _parse_matrix(local_matrix_raw)
            except ValueError as exc:
                print("Warning: invalid local matrix ({}); using identity".format(exc))
                local_matrix_vals = IDENTITY_4X4
        else:
            local_matrix_vals = IDENTITY_4X4

        volume_node = loadVolume(VOLUME_PATH)
        if volume_node is None:
            raise RuntimeError("Failed to load volume: {}".format(VOLUME_PATH))
        setSliceViewerLayers(background=volume_node)
        layout_manager = slicer.app.layoutManager()
        if layout_manager:
            layout_manager.resetSliceViews()
        else:
            print("Info: layout manager unavailable (likely headless mode); skipping slice reset")

        matrix_global = vtk.vtkMatrix4x4()
        for row in range(4):
            for col in range(4):
                matrix_global.SetElement(row, col, matrix_vals[col * 4 + row])

        matrix_local = vtk.vtkMatrix4x4()
        for row in range(4):
            for col in range(4):
                matrix_local.SetElement(row, col, local_matrix_vals[col * 4 + row])

        matrix = vtk.vtkMatrix4x4()
        vtk.vtkMatrix4x4.Multiply4x4(matrix_global, matrix_local, matrix)

        rotation_mode = _resolve_rotation_mode(stem_info)
        auto_pre = rotation_mode == "johnson"
        auto_post = rotation_mode in ("johnson", "mathys")
        if auto_pre and not PRE_ROTATE_Z_180:
            print("Auto: applying pre-rotate Z 180° for Johnson stem")
            PRE_ROTATE_Z_180 = True
        if auto_post and not POST_ROTATE_Z_180:
            print("Auto: applying post-rotate Z 180° for %s stem" % rotation_mode.capitalize())
            POST_ROTATE_Z_180 = True

        if PRE_TRANSFORM_LPS_TO_RAS:
            flip = vtk.vtkMatrix4x4()
            flip.Identity()
            flip.SetElement(0, 0, -1)
            flip.SetElement(1, 1, -1)
            _right_multiply(matrix, flip)

        if PRE_ROTATE_Z_180:
            rot = vtk.vtkMatrix4x4()
            rot.Identity()
            rot.SetElement(0, 0, -1)
            rot.SetElement(1, 1, -1)
            _right_multiply(matrix, rot)

        if POST_ROTATE_Z_180:
            rot_post = vtk.vtkMatrix4x4()
            rot_post.Identity()
            rot_post.SetElement(0, 0, -1)
            rot_post.SetElement(1, 1, -1)
            _left_multiply(matrix, rot_post)
        transform_node = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLLinearTransformNode", "StemTransform"
        )
        transform_node.SetMatrixTransformToParent(matrix)

        model_node = None

        search_folders = []
        if STL_ROOTS:
            for root in STL_ROOTS:
                if not root:
                    continue
                if not os.path.isdir(root):
                    print("Warning: STL root '%s' not found" % root)
                    continue
                for dirpath, dirnames, filenames in os.walk(root):
                    search_folders.append(dirpath)

        if search_folders:
            try:
                import view_implant
            except Exception as exc:
                print("Warning: could not import view_implant (%s); falling back to cylinder" % exc)
            else:
                tokens = [
                    stem_info.get("rcc_id"),
                    stem_info.get("stem_enum_name"),
                    str(stem_info.get("uid")) if stem_info.get("uid") is not None else None,
                ]
                tokens = [token for token in tokens if token]
                if tokens:
                    try:
                        stl_path, _ = view_implant.find_matching_stl(search_folders, tokens)
                    except Exception as exc:
                        print("Warning: %s; using procedural cylinder" % exc)
                    else:
                        model_node = loadModel(str(stl_path))
                        if model_node is None:
                            print("Warning: loadModel failed for %s; using cylinder" % stl_path)
                        elif _needs_mathys_flip(stem_info):
                            flipped = _flip_polydata_lps_to_ras(model_node.GetPolyData())
                            if flipped:
                                model_node.SetAndObservePolyData(flipped)
                                model_node.SetAttribute("stem.geometryCoordinateSystem", "RAS (Mathys)")
                            else:
                                print("Warning: failed to flip Mathys STL to RAS; proceeding with original data")

        if model_node is None:
            cylinder = vtk.vtkCylinderSource()
            cylinder.SetRadius(STEM_RADIUS)
            cylinder.SetHeight(STEM_LENGTH)
            cylinder.SetResolution(64)
            cylinder.SetCenter(0, 0, STEM_LENGTH * 0.5)
            cylinder.CappingOn()
            cylinder.Update()

            model_node = slicer.mrmlScene.AddNewNodeByClass("vtkMRMLModelNode", "ImplantStem")
            model_node.SetAndObservePolyData(cylinder.GetOutput())
            model_node.CreateDefaultDisplayNodes()
            display = model_node.GetDisplayNode()
            display.SetColor(0.85, 0.33, 0.1)
            display.SetOpacity(0.7)

        model_node.SetAndObserveTransformNodeID(transform_node.GetID())

        base_name = model_node.GetName() or "Stem"
        hardened_name = slicer.mrmlScene.GenerateUniqueName(f"{base_name} (Hardened)")
        hardened_clone = slicer.mrmlScene.AddNewNodeByClass(
            "vtkMRMLModelNode",
            hardened_name,
        )
        clone_poly_data = vtk.vtkPolyData()
        clone_poly_data.DeepCopy(model_node.GetPolyData())
        hardened_clone.SetAndObservePolyData(clone_poly_data)
        hardened_clone.CreateDefaultDisplayNodes()
        source_display = model_node.GetDisplayNode()
        clone_display = hardened_clone.GetDisplayNode()
        if source_display and clone_display:
            clone_display.Copy(source_display)
        hardened_clone.SetAndObserveTransformNodeID(transform_node.GetID())
        hardened_clone.HardenTransform()
        hardened_clone.SetAndObserveTransformNodeID(None)
        hardened_clone.SetAttribute("stem.clone", "hardened")

        for key, value in stem_info.items():
            if value is None:
                continue
            attr_value = str(value)
            model_node.SetAttribute("stem.%s" % key, attr_value)
            hardened_clone.SetAttribute("stem.%s" % key, attr_value)

        if COMPUTE_STEM_SCALARS:
            target_node = hardened_clone or model_node
            try:
                _probe_volume_onto_model(volume_node, target_node, array_name="VolumeScalars")
            except Exception as exc:
                print("Warning: unable to sample scalars onto '%s' (%s)" % (target_node.GetName(), exc))
            else:
                _print_scalar_percentages(target_node, array_name="VolumeScalars")
                lut_node = _ensure_ezplan_lut()
                _apply_scalar_display(target_node, array_name="VolumeScalars", color_node=lut_node)
                if target_node is not model_node:
                    _copy_scalar_array(target_node, model_node, "VolumeScalars")
                    _apply_scalar_display(model_node, array_name="VolumeScalars", color_node=lut_node)
                print("Stored sampled scalars on '{}' and applied '{}' LUT".format(
                    target_node.GetName(), EZPLAN_LUT_NAME
                ))
                _export_original_stem(model_node)
                if EXPORT_STEM_SCREENSHOTS:
                    original_display = model_node.GetDisplayNode()
                    original_visibility = None
                    if original_display:
                        original_visibility = original_display.GetVisibility()
                        original_display.SetVisibility(False)
                    clone_display = target_node.GetDisplayNode()
                    if clone_display:
                        clone_display.SetVisibility(True)
                    try:
                        _capture_stem_screenshots(target_node)
                    finally:
                        if original_display and original_visibility is not None:
                            original_display.SetVisibility(original_visibility)

        print("Loaded volume: {}".format(volume_node.GetName()))
        print("Added implant stem UID: {}".format(stem_info.get("uid")))

        if EXIT_AFTER_RUN:
            print("Exit-after-run requested; closing Slicer session...")
            util_module = getattr(slicer, "util", None)
            exited = False
            if util_module and hasattr(util_module, "exit"):
                try:
                    util_module.exit()
                except Exception as exc:
                    print("Warning: slicer.util.exit() raised %s" % exc)
                else:
                    exited = True
            if not exited:
                app = qt.QApplication.instance()
                if app:
                    app.quit()
                    exited = True
            raise SystemExit(0)
        """
    ))

    return template.substitute(
        REPO_ROOT=repo_root,
        VOLUME_PATH=volume_path,
        SEEDPLAN_PATH=seedplan_path,
        STEM_LENGTH=stem_length,
        STEM_RADIUS=stem_radius,
        STL_ROOTS=stl_folders_literal,
        PRE_TRANSFORM_LPS_TO_RAS="True" if pre_transform_lps_to_ras else "False",
        PRE_ROTATE_Z_180="True" if pre_rotate_z_180 else "False",
        POST_ROTATE_Z_180="True" if post_rotate_z_180 else "False",
        COMPUTE_STEM_SCALARS="True" if compute_stem_scalars else "False",
        EXPORT_STEM_SCREENSHOTS="True" if export_stem_screenshots else "False",
        AUTO_ROTATION_MODE=rotation_mode,
        EXIT_AFTER_RUN="True" if exit_after_run else "False",
    )


def write_temp_script(contents: str) -> str:
    handle = tempfile.NamedTemporaryFile("w", suffix="_load_nifti_and_stem.py", delete=False)
    handle.write(contents)
    handle.flush()
    handle.close()
    return handle.name


def main() -> int:
    args = parse_args()

    nifti_path = os.path.abspath(args.nifti)
    seedplan_path = os.path.abspath(args.seedplan)

    missing = [path for path in (nifti_path, seedplan_path) if not os.path.exists(path)]
    if missing:
        print("Error: missing input(s):", ", ".join(missing), file=sys.stderr)
        return 1

    try:
        slicer_exec = find_slicer_executable(args.slicer_path)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    repo_root = os.path.dirname(os.path.abspath(__file__))
    slicer_script = build_slicer_script(
        nifti_path,
        seedplan_path,
        repo_root,
        args.stem_length,
        args.stem_radius,
        args.stl_folders,
        args.pre_transform_lps_to_ras,
        args.pre_rotate_z_180,
        args.post_rotate_z_180,
        args.compute_stem_scalars,
        args.rotation_mode,
        args.export_stem_screenshots,
        args.exit_after_run,
    )
    temp_script = write_temp_script(slicer_script)

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
