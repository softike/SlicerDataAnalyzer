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
        from slicer.util import loadVolume, setSliceViewerLayers, loadModel

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

        def _needs_mathys_flip(info):
            markers = (
                info.get("manufacturer"),
                info.get("stem_enum_name"),
                info.get("stem_friendly_name"),
            )
            for marker in markers:
                if marker and "mathys" in marker.lower():
                    return True
            return False

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
        slicer.app.layoutManager().resetSliceViews()

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

        for key, value in stem_info.items():
            if value is None:
                continue
            model_node.SetAttribute("stem.%s" % key, str(value))

        print("Loaded volume: {}".format(volume_node.GetName()))
        print("Added implant stem UID: {}".format(stem_info.get("uid")))
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
