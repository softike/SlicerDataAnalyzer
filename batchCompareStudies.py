#!/usr/bin/env python3
"""
# and supports more advanced formatting options# Note: openpyxl is preferred as it allows both reading and writing Excel files# xlsxwriter>=1.3.0# Option 2: xlsxwriter (alternative - creates .xlsx files, good performance)openpyxl>=3.0.0# Option 1: openpyxl (recommended - supports .xlsx files with formatting)# Excel file format engines (install at least one)pandas>=1.0.0# Core dependency for Excel exportBatch comparison script for medical planning data across multiple testers.
This script automatically finds corresponding case folders across H001, H002, H003 directories
and generates a consolidated HTML report with all case comparisons.

Usage:
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --pdf
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --excel
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --excel-detailed
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --pdf --excel --translation-only
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --output-path /tmp/reports
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

from implant_registry import resolve_stem_uid

TESTER_IDS = ("H001", "H002", "H003")
STEM_ROTATION_KEYS = (
    "R11",
    "R12",
    "R13",
    "R21",
    "R22",
    "R23",
    "R31",
    "R32",
    "R33",
)
STEM_TRANSLATION_KEYS = ("Tx", "Ty", "Tz")

# Import the main comparison functions from the existing script
from compareResults_3Studies import (
    comparePlanningData,
    extractPlanningData_plain,
    calculate_femoral_anteversion,
    calculate_femoral_anteversion_from_dict,
    generate_comparison_stats,
    create_individual_comparison_plots,
    export_to_pdf,
    extract_patient_side,
    validate_patient_sides,
    filter_tags_by_side,
    TAGS_XPATHS,
)


def _decompose_matrix_components(matrix_value):
    """Split a flattened 4x4 matrix string into rotation and translation parts."""

    components = {"rotation": {}, "translation": {}}
    if not matrix_value:
        return components

    try:
        values = [float(x) for x in matrix_value.strip().split()]
    except (TypeError, ValueError):
        return components

    if len(values) != 16:
        return components

    rotation = {}
    for row in range(3):
        for col in range(3):
            rotation[f"R{row + 1}{col + 1}"] = values[row * 4 + col]

    components["rotation"] = rotation
    components["translation"] = {
        "Tx": values[12],
        "Ty": values[13],
        "Tz": values[14],
    }
    return components


def _normalize_side_label(side_value):
    """Convert side strings like 'Left', 'SideFree', 'R' into canonical Left/Right labels."""

    if not side_value:
        return None

    cleaned = side_value.strip().lower()
    if not cleaned:
        return None

    if cleaned in {"left", "l", "sideleft"}:
        return "Left"
    if cleaned in {"right", "r", "sideright"}:
        return "Right"

    return None


def extract_stem_info_from_xml(xml_path):
    """Collect implant stem metadata from every hipImplantConfig block in a seedplan."""

    def _blank_entry():
        return {
            "xml_path": xml_path,
            "uid": None,
            "matrix_raw": None,
            "rotation": {},
            "translation": {},
            "requested_side": None,
            "configured_side": None,
            "state": None,
            "hip_config_uid": None,
            "hip_config_index": None,
            "hip_config_name": None,
            "source": None,
            "manufacturer": None,
            "stem_enum_name": None,
            "stem_friendly_name": None,
            "rcc_id": None,
            "error": None,
        }

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
    except Exception as exc:
        error_entry = _blank_entry()
        error_entry["error"] = f"parse_error: {exc}"
        return [error_entry]

    entries = []
    hip_configs = root.findall(".//hipImplantConfig")
    history_configs = root.findall(".//hipImplantConfigHistoryList/hipImplantConfig")
    config_index = 0

    for source_label, configs in (("active", hip_configs), ("history", history_configs)):
        for hip_config in configs:
            entry = _blank_entry()
            entry["hip_config_uid"] = hip_config.attrib.get("uid")
            entry["hip_config_index"] = config_index
            entry["source"] = source_label
            pretty_name = hip_config.findtext("prettyName") or hip_config.attrib.get("prettyName")
            if not pretty_name:
                pretty_name = hip_config.attrib.get("name")
            if pretty_name:
                entry["hip_config_name"] = pretty_name.strip()
            elif entry["hip_config_uid"]:
                entry["hip_config_name"] = f"{source_label} config {entry['hip_config_uid']}"
            else:
                entry["hip_config_name"] = f"{source_label} config {config_index}"
            config_index += 1

            fem_config = hip_config.find("./femImplantConfig")
            if fem_config is None:
                entry["error"] = "fem_implant_config_missing"
                entries.append(entry)
                continue

            entry["requested_side"] = fem_config.attrib.get("requestedSide")
            entry["configured_side"] = fem_config.attrib.get("side")
            entry["state"] = fem_config.attrib.get("state")

            stem_shape = fem_config.find(".//s3Shape[@part='stem']")
            if stem_shape is None:
                entry["error"] = "stem_shape_missing"
                entries.append(entry)
                continue

            uid_attr = stem_shape.attrib.get("uid")
            if uid_attr:
                try:
                    entry["uid"] = int(uid_attr)
                except ValueError:
                    entry["error"] = f"invalid_uid: {uid_attr}"
                else:
                    lookup = resolve_stem_uid(entry["uid"])
                    if lookup:
                        entry["manufacturer"] = lookup.manufacturer
                        entry["stem_enum_name"] = lookup.enum_name
                        entry["stem_friendly_name"] = lookup.friendly_name
                        entry["rcc_id"] = lookup.rcc_id

            matrix_elem = stem_shape.find("matrix4[@name='mat']")
            if matrix_elem is None:
                matrix_elem = stem_shape.find("matrix4")
            if matrix_elem is not None:
                entry["matrix_raw"] = matrix_elem.attrib.get("value")
                components = _decompose_matrix_components(entry["matrix_raw"])
                entry["rotation"] = components.get("rotation", {})
                entry["translation"] = components.get("translation", {})
            else:
                entry["error"] = entry["error"] or "stem_matrix_missing"

            entries.append(entry)

    if not entries:
        empty_entry = _blank_entry()
        empty_entry["error"] = "stem_not_found"
        entries.append(empty_entry)

    return entries

def find_case_folders(base_path):
    """
    Find all corresponding case folders across H001, H002, H003 directories.
    
    Args:
        base_path: Base path containing H001, H002, H003 directories
        
    Returns:
        List of tuples (case_name, h001_path, h002_path, h003_path)
    """
    case_sets = []
    
    # Find all case folders in H001 first (use as reference)
    h001_path = os.path.join(base_path, 'H001')
    if not os.path.exists(h001_path):
        print(f"H001 directory not found at {h001_path}")
        return case_sets
    
    # Get all case folders in H001
    h001_cases = [d for d in os.listdir(h001_path) 
                  if os.path.isdir(os.path.join(h001_path, d))]
    
    for case_name in h001_cases:
        # Check if corresponding case exists in H002 and H003
        h002_case_path = os.path.join(base_path, 'H002', case_name)
        h003_case_path = os.path.join(base_path, 'H003', case_name)
        
        if os.path.exists(h002_case_path) and os.path.exists(h003_case_path):
            # Look for seedplan.xml files
            h001_xml = os.path.join(h001_path, case_name, 'Mediplan3D', 'seedplan.xml')
            h002_xml = os.path.join(h002_case_path, 'Mediplan3D', 'seedplan.xml')
            h003_xml = os.path.join(h003_case_path, 'Mediplan3D', 'seedplan.xml')
            
            if all(os.path.exists(xml_path) for xml_path in [h001_xml, h002_xml, h003_xml]):
                case_sets.append((case_name, h001_xml, h002_xml, h003_xml))
                print(f"Found complete case set: {case_name}")
            else:
                print(f"Missing seedplan.xml files for case: {case_name}")
        else:
            print(f"Case {case_name} not found in all tester directories")
    
    return case_sets

def generate_case_comparison_data(xml_path1, xml_path2, xml_path3, case_name, output_dir, translation_only=False, side_filter='Both', no_landmark_rotation=False):
    """
    Generate comparison data for a single case across three testers.
    
    Returns:
        Dictionary containing comparison results and plot information
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    import numpy as np
    
    # Determine actual side filter based on mode
    actual_side_filter = side_filter
    detected_side = None  # Initialize to ensure it's always defined
    
    if side_filter == 'Auto':
        xml_paths = [xml_path1, xml_path2, xml_path3]
        is_consistent, detected_side, sides_list = validate_patient_sides(xml_paths, case_name)
        
        if not is_consistent:
            return {
                'case_name': case_name,
                'status': 'inconsistent_patient_side',
                'common_tags': [],
                'plot_files': [],
                'stats_html': f'<p>Auto mode failed: Inconsistent PatientSide values: {sides_list}</p>',
                'side_error': f'Auto mode failed: Inconsistent PatientSide values: {sides_list}',
                'side_info': {
                    'side_filter': side_filter,
                    'detected_side': None,
                    'actual_side_filter': None,
                    'is_auto_mode': True,
                    'sides_list': sides_list,
                    'is_consistent': False
                }
            }
        elif detected_side is None:
            print(f"Warning: Could not determine PatientSide for case {case_name}. Using 'Both' mode.")
            actual_side_filter = 'Both'
        else:
            actual_side_filter = detected_side
            print(f"Info: Auto-detected PatientSide '{detected_side}' for case {case_name}.")
    
    # Validate patient sides consistency if filtering is requested
    elif side_filter != 'Both':
        xml_paths = [xml_path1, xml_path2, xml_path3]
        is_consistent, detected_side, sides_list = validate_patient_sides(xml_paths, case_name)
        
        if not is_consistent:
            return {
                'case_name': case_name,
                'status': 'inconsistent_patient_side',
                'common_tags': [],
                'plot_files': [],
                'stats_html': f'<p>Inconsistent PatientSide values: {sides_list}</p>',
                'side_error': f'Inconsistent PatientSide values: {sides_list}',
                'side_info': {
                    'side_filter': side_filter,
                    'detected_side': detected_side,
                    'actual_side_filter': None,
                    'is_auto_mode': False,
                    'sides_list': sides_list,
                    'is_consistent': False
                }
            }
    
    # Create case-specific output prefix
    case_output_prefix = os.path.join(output_dir, f"case_{case_name}")
    
    # Extract data from all three XML files (similar to comparePlanningData function)
    def extract_data_from_xml(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        planning_data = {}
        
        def get_elem_value(elem):
            if elem is not None and 'value' in elem.attrib:
                return elem.attrib['value']
            return None
        
        # Use centralized definition of tags and XPaths
        tags_xpaths = TAGS_XPATHS
        
        for tag, xpath in tags_xpaths:
            elem = root.find(xpath)
            planning_data[tag] = get_elem_value(elem)
        
        return planning_data
    
    # Extract data from all three files
    data1 = extract_data_from_xml(xml_path1)
    data2 = extract_data_from_xml(xml_path2)
    data3 = extract_data_from_xml(xml_path3)
    
    # Get common tags
    common_tags = set(data1.keys()) & set(data2.keys()) & set(data3.keys())
    common_tags = [tag for tag in common_tags if data1[tag] and data2[tag] and data3[tag]]
    
    if not common_tags:
        return {
            'case_name': case_name,
            'status': 'no_common_data',
            'common_tags': [],
            'plot_files': [],
            'stats_html': '<p>No common data found for this case.</p>'
        }
    
    # Generate comparison plots
    plot_files = create_individual_comparison_plots(data1, data2, data3, common_tags, case_output_prefix, translation_only, actual_side_filter, no_landmark_rotation)
    
    # Generate statistics
    stats_html = generate_comparison_stats(data1, data2, data3, common_tags)
    
    # Determine side information for reporting
    side_info = {
        'side_filter': side_filter,
        'detected_side': detected_side if side_filter == 'Auto' else None,
        'actual_side_filter': actual_side_filter,
        'is_auto_mode': side_filter == 'Auto'
    }

    stem_details = []
    for tester_label, xml_path in zip(TESTER_IDS, [xml_path1, xml_path2, xml_path3]):
        stem_entries = extract_stem_info_from_xml(xml_path)
        for entry in stem_entries:
            entry['tester'] = tester_label
            stem_details.append(entry)
    
    return {
        'case_name': case_name,
        'status': 'success',
        'common_tags': common_tags,
        'plot_files': plot_files,
        'stats_html': stats_html,
        'xml_paths': [xml_path1, xml_path2, xml_path3],
        'side_info': side_info,
        'raw_data': (data1, data2, data3),  # Store raw data for Excel export
        'anteversion_angles': extract_anteversion_from_data(data1, data2, data3),  # Store anteversion angles
        'stem_info': stem_details,
    }

def extract_anteversion_from_data(data1, data2, data3):
    """
    Extract femoral anteversion angles from the raw data for each side.
    
    Args:
        data1, data2, data3: Raw planning data dictionaries from three testers
        
    Returns:
        Dictionary with anteversion angles organized by side
    """
    anteversion_angles = {'Right': [None, None, None], 'Left': [None, None, None]}
    
    datasets = [data1, data2, data3]
    
    for side in ['Right', 'Left']:
        side_suffix = 'R' if side == 'Right' else 'L'
        
        for i, data in enumerate(datasets):
            try:
                angle = calculate_femoral_anteversion_from_dict(data, side)
                anteversion_angles[side][i] = angle
            except Exception:
                pass
    
    return anteversion_angles

def generate_anteversion_summary_table(anteversion_data, case_results):
    """
    Generate HTML table summarizing femoral anteversion angles across all cases and testers.
    
    Args:
        anteversion_data: dict with case_name -> {'Right': [H001, H002, H003], 'Left': [...]}
        case_results: list of case comparison results with side information
    
    Returns:
        str: HTML table with femoral anteversion angle summary
    """
    if not anteversion_data:
        return ""
    
    # Create a map of case_name -> side_info for easy lookup
    case_side_info = {}
    for result in case_results:
        if 'side_info' in result:
            case_side_info[result['case_name']] = result['side_info']
    
    table_html = """
    <div class="anteversion-summary">
        <h2>Femoral Anteversion Angle Summary</h2>
        <p>This table shows the femoral anteversion angles (degrees) measured between S3FemurFrame and S3BCP matrices for each case and tester.</p>
        
        <table class="anteversion-table">
            <thead>
                <tr>
                    <th rowspan="2">Case</th>
                    <th colspan="3">Right Femoral Anteversion Angle (°)</th>
                    <th colspan="3">Left Femoral Anteversion Angle (°)</th>
                    <th colspan="2">Right Side Statistics</th>
                    <th colspan="2">Left Side Statistics</th>
                </tr>
                <tr>
                    <th>H001</th>
                    <th>H002</th>
                    <th>H003</th>
                    <th>H001</th>
                    <th>H002</th>
                    <th>H003</th>
                    <th>Mean ± SD</th>
                    <th>Range</th>
                    <th>Mean ± SD</th>
                    <th>Range</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Process each case
    for case_name in sorted(anteversion_data.keys()):
        case_data = anteversion_data[case_name]
        side_info = case_side_info.get(case_name, {})
        
        # Determine case name styling based on side information
        case_name_class = 'case-name'
        side_indicator = ''
        
        if side_info:
            if side_info.get('is_consistent', True):  # Default to True if not specified
                if side_info.get('is_auto_mode', False):
                    detected_side = side_info.get('detected_side')
                    if detected_side:
                        case_name_class += ' auto-detected-side'
                        side_indicator = f" <span class='side-indicator auto-{detected_side.lower()}'>[Auto: {detected_side}]</span>"
                else:
                    actual_side = side_info.get('actual_side_filter')
                    if actual_side and actual_side != 'Both':
                        case_name_class += ' explicit-side'
                        side_indicator = f" <span class='side-indicator explicit-{actual_side.lower()}'>[{actual_side}]</span>"
            else:
                case_name_class += ' inconsistent-side'
                sides_list = side_info.get('sides_list', [])
                side_indicator = f" <span class='side-indicator inconsistent'>⚠ Inconsistent: {sides_list}</span>"
        
        table_html += f"<tr><td class='{case_name_class}'>{case_name}{side_indicator}</td>"
        
        # Right side angles
        right_angles = case_data.get('Right', [None, None, None])
        for angle in right_angles:
            if angle is not None:
                table_html += f"<td class='angle-value'>{angle:.2f}</td>"
            else:
                table_html += "<td class='angle-missing'>N/A</td>"
        
        # Left side angles
        left_angles = case_data.get('Left', [None, None, None])
        for angle in left_angles:
            if angle is not None:
                table_html += f"<td class='angle-value'>{angle:.2f}</td>"
            else:
                table_html += "<td class='angle-missing'>N/A</td>"
        
        # Right side statistics
        valid_right = [a for a in right_angles if a is not None]
        if len(valid_right) >= 2:
            import numpy as np
            mean_right = np.mean(valid_right)
            std_right = np.std(valid_right)
            min_right = min(valid_right)
            max_right = max(valid_right)
            table_html += f"<td class='stats-value'>{mean_right:.2f} ± {std_right:.2f}</td>"
            table_html += f"<td class='stats-value'>{min_right:.2f} - {max_right:.2f}</td>"
        else:
            table_html += "<td class='stats-missing'>N/A</td><td class='stats-missing'>N/A</td>"
        
        # Left side statistics
        valid_left = [a for a in left_angles if a is not None]
        if len(valid_left) >= 2:
            import numpy as np
            mean_left = np.mean(valid_left)
            std_left = np.std(valid_left)
            min_left = min(valid_left)
            max_left = max(valid_left)
            table_html += f"<td class='stats-value'>{mean_left:.2f} ± {std_left:.2f}</td>"
            table_html += f"<td class='stats-value'>{min_left:.2f} - {max_left:.2f}</td>"
        else:
            table_html += "<td class='stats-missing'>N/A</td><td class='stats-missing'>N/A</td>"
        
        table_html += "</tr>"
    
    table_html += """
            </tbody>
        </table>
        
        <div class="table-notes">
            <h4>Notes:</h4>
            <ul>
                <li><strong>Angle Calculation:</strong> Angle between the projected femoral neck vector (S3FemurFrame + S3FemoralSphere) and the transformed S3BCP line</li>
                <li><strong>N/A:</strong> Data not available (missing matrix data or calculation error)</li>
                <li><strong>Statistics:</strong> Mean ± Standard Deviation and Range calculated from available measurements</li>
                <li><strong>H001/H002/H003:</strong> Different testers/operators performing the measurements</li>
            </ul>
        </div>
    </div>
    """
    
    return table_html

def extract_femoral_anteversion_angles(case_results):
    """
    Extract femoral anteversion angles for each case and tester.
    
    Returns:
        dict: Case name -> {'Right': [H001_angle, H002_angle, H003_angle], 'Left': [...]}
    """
    anteversion_data = {}
    
    for result in case_results:
        if result['status'] != 'success':
            continue
            
        case_name = result['case_name']
        anteversion_data[case_name] = {}
        
        # Process each side
        for side in ['Right', 'Left']:
            suffix = side[0]
            femur_tag = f'S3FemurFrame_{suffix}_matrix'
            bcp_tag = f'S3BCP_{suffix}_matrix'
            sphere_tag = f'S3FemoralSphere_{suffix}_matrix'
            p0_tag = f'S3BCP_{suffix}_p0'
            p1_tag = f'S3BCP_{suffix}_p1'
            
            angles = []
            
            # Calculate angle for each tester's data
            for xml_path in result['xml_paths']:
                try:
                    # Extract data from XML file
                    tree = ET.parse(xml_path)
                    root = tree.getroot()
                    
                    def get_elem_value(elem):
                        if elem is not None and 'value' in elem.attrib:
                            return elem.attrib['value']
                        return None
                    
                    # Get matrix values
                    femur_elem = root.find(f".//s3Shape[@name='S3FemurFrame_{suffix}']/matrix4[@name='mat']")
                    bcp_elem = root.find(f".//s3Shape[@name='S3BCP_{suffix}']/matrix4[@name='mat']")
                    sphere_elem = root.find(f".//s3Shape[@name='S3FemoralSphere_{suffix}']/matrix4[@name='mat']")
                    p0_elem = root.find(f".//s3Shape[@name='S3BCP_{suffix}']/vector3[@name='p0']")
                    p1_elem = root.find(f".//s3Shape[@name='S3BCP_{suffix}']/vector3[@name='p1']")

                    femur_matrix = get_elem_value(femur_elem)
                    bcp_matrix = get_elem_value(bcp_elem)
                    sphere_matrix = get_elem_value(sphere_elem)
                    p0_vector = get_elem_value(p0_elem)
                    p1_vector = get_elem_value(p1_elem)

                    if all([femur_matrix, bcp_matrix, sphere_matrix, p0_vector, p1_vector]):
                        try:
                            angle = calculate_femoral_anteversion(
                                femur_matrix,
                                bcp_matrix,
                                femoral_sphere_matrix_str=sphere_matrix,
                                bcp_p0_str=p0_vector,
                                bcp_p1_str=p1_vector,
                                side=side,
                            )
                        except ValueError:
                            angle = None
                        angles.append(angle)
                    else:
                        angles.append(None)
                        
                except Exception as e:
                    angles.append(None)
            
            anteversion_data[case_name][side] = angles
    
    return anteversion_data

def generate_consolidated_html_report(case_results, output_prefix, export_pdf=False, inter_rater_results=None):
    """
    Generate a consolidated HTML report containing all case comparisons.
    """
    html_filename = f"{output_prefix}.html"
    report_dir = os.path.dirname(html_filename) or os.curdir

    def _relative_to_report(path):
        if not path:
            return path
        try:
            return os.path.relpath(path, start=report_dir)
        except ValueError:
            return path
    
    # Generate navigation menu
    nav_html = """
    <div class="navigation">
        <h3>Case Navigation</h3>
        <ul class="case-list">
    """
    
    for result in case_results:
        if result['status'] == 'success':
            nav_html += f'<li><a href="#case-{result["case_name"]}">{result["case_name"]}</a> ({len(result["common_tags"])} parameters)</li>'
        elif result['status'] == 'inconsistent_patient_side':
            nav_html += f'<li class="error">{result["case_name"]} (Side mismatch: {result.get("side_error", "Unknown error")})</li>'
        else:
            nav_html += f'<li class="error">{result["case_name"]} (No data)</li>'
    
    nav_html += """
        </ul>
    </div>
    """
    
    # Generate summary statistics
    total_cases = len(case_results)
    successful_cases = len([r for r in case_results if r['status'] == 'success'])
    total_plots = sum(len(r['plot_files']) for r in case_results if r['status'] == 'success')
    
    summary_html = f"""
    <div class="summary-section">
        <h2>Batch Processing Summary</h2>
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-value">{total_cases}</span>
                <span class="stat-label">Total Cases Found</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{successful_cases}</span>
                <span class="stat-label">Successfully Processed</span>
            </div>
            <div class="stat-item">
                <span class="stat-value">{total_plots}</span>
                <span class="stat-label">Total Plots Generated</span>
            </div>
        </div>
    </div>
    """
    
    # Generate femoral anteversion angle summary table
    anteversion_data = extract_femoral_anteversion_angles(case_results)
    anteversion_table_html = generate_anteversion_summary_table(anteversion_data, case_results)
    
    # Generate inter-rater analysis section
    inter_rater_html = generate_inter_rater_html_section(inter_rater_results, report_dir) if inter_rater_results else ""
    
    # Generate individual case sections
    cases_html = ""
    for result in case_results:
        if result['status'] == 'inconsistent_patient_side':
            cases_html += f"""
            <div class="case-section" id="case-{result['case_name']}">
                <h2>Case: {result['case_name']}</h2>
                <div class="error-message">
                    <p>⚠️ PatientSide inconsistency: {result.get('side_error', 'Unknown error')}</p>
                    <p>This case has different PatientSide values across the three testers and cannot be processed reliably.</p>
                </div>
            </div>
            """
            continue
        elif result['status'] != 'success':
            cases_html += f"""
            <div class="case-section" id="case-{result['case_name']}">
                <h2>Case: {result['case_name']}</h2>
                <div class="error-message">
                    <p>❌ No common data found for this case</p>
                </div>
            </div>
            """
            continue
        
        # Generate plots grid for this case
        plots_html = ""
        for plot_info in result['plot_files']:
            img_src = _relative_to_report(plot_info['filename'])
            plots_html += f"""
            <div class="plot-item">
                <h4>{plot_info['title']}</h4>
                <img src="{img_src}" alt="{plot_info['title']}" class="individual-plot">
            </div>
            """
        
        # Generate side information for case header
        side_info_text = ""
        side_header_class = "case-section"
        
        if 'side_info' in result:
            side_info = result['side_info']
            if side_info.get('is_auto_mode', False):
                detected_side = side_info.get('detected_side')
                if detected_side:
                    side_info_text = f" <span class='case-side-indicator auto-{detected_side.lower()}'>Auto-detected: {detected_side}</span>"
                    side_header_class += " auto-detected"
            else:
                actual_side = side_info.get('actual_side_filter')
                if actual_side and actual_side != 'Both':
                    side_info_text = f" <span class='case-side-indicator explicit-{actual_side.lower()}'>Side: {actual_side}</span>"
                    side_header_class += " explicit-side"
        
        cases_html += f"""
        <div class="{side_header_class}" id="case-{result['case_name']}">
            <h2>Case: {result['case_name']}{side_info_text}</h2>
            
            <div class="case-info">
                <h3>File Paths:</h3>
                <ul>
                    <li><strong>H001:</strong> {result['xml_paths'][0]}</li>
                    <li><strong>H002:</strong> {result['xml_paths'][1]}</li>
                    <li><strong>H003:</strong> {result['xml_paths'][2]}</li>
                </ul>
                <p><strong>Common parameters:</strong> {len(result['common_tags'])}</p>
            </div>
            
            <div class="plots-grid">
                {plots_html}
            </div>
            
            <div class="stats-section">
                <h3>Statistical Comparison</h3>
                {result['stats_html']}
            </div>
            
            <hr class="case-separator">
        </div>
        """
    
    # Complete HTML document
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch Planning Data Comparison Report</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0 0;
            font-size: 1.1em;
            opacity: 0.9;
        }}
        .content {{
            display: flex;
            min-height: calc(100vh - 200px);
        }}
        .navigation {{
            width: 300px;
            background-color: #f8f9fa;
            padding: 20px;
            border-right: 1px solid #dee2e6;
            position: sticky;
            top: 0;
            height: fit-content;
        }}
        .navigation h3 {{
            color: #495057;
            margin-top: 0;
        }}
        .case-list {{
            list-style: none;
            padding: 0;
        }}
        .case-list li {{
            margin: 8px 0;
        }}
        .case-list a {{
            color: #007bff;
            text-decoration: none;
            padding: 8px 12px;
            display: block;
            border-radius: 4px;
            transition: background-color 0.3s;
        }}
        .case-list a:hover {{
            background-color: #e3f2fd;
        }}
        .case-list .error {{
            color: #dc3545;
            padding: 8px 12px;
            font-style: italic;
        }}
        .main-content {{
            flex: 1;
            padding: 20px;
        }}
        .summary-section {{
            background-color: #e3f2fd;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }}
        .summary-stats {{
            display: flex;
            justify-content: space-around;
            margin-top: 15px;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            display: block;
            font-size: 2em;
            font-weight: bold;
            color: #1976d2;
        }}
        .stat-label {{
            font-size: 0.9em;
            color: #666;
        }}
        .case-section {{
            margin-bottom: 40px;
            padding: 20px;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            background-color: #fff;
        }}
        .case-section h2 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .case-info {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
        }}
        .case-info ul {{
            margin: 10px 0;
        }}
        .plots-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .plot-item {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            border: 1px solid #dee2e6;
        }}
        .plot-item h4 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 14px;
        }}
        .individual-plot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .inter-rater-analysis .plots-grid {{
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        }}
        .inter-rater-analysis .plot-item {{
            padding: 12px;
        }}
        .inter-rater-plot {{
            width: 100%;
            max-width: 100%;
            max-height: 320px;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            display: block;
            object-fit: contain;
            background-color: #fff;
            margin: 0 auto;
        }}
        .plot-stats {{
            margin-top: 10px;
            font-size: 0.85em;
            color: #495057;
        }}
        .stats-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .stats-section table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12px;
        }}
        .stats-section th, .stats-section td {{
            padding: 8px;
            text-align: left;
            border: 1px solid #ddd;
        }}
        .stats-section th {{
            background-color: #e9ecef;
        }}
        .case-separator {{
            border: none;
            height: 2px;
            background: linear-gradient(90deg, transparent, #007bff, transparent);
            margin: 30px 0;
        }}
        .error-message {{
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }}
        .footer {{
            background-color: #343a40;
            color: white;
            text-align: center;
            padding: 20px;
            margin-top: 40px;
        }}
        
        /* Anteversion Summary Table Styles */
        .anteversion-summary {{
            margin: 30px 0;
            padding: 20px;
            background-color: #f8f9fa;
            border-radius: 8px;
            border: 1px solid #dee2e6;
        }}
        .anteversion-summary h2 {{
            color: #495057;
            margin-bottom: 10px;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .anteversion-summary p {{
            color: #6c757d;
            margin-bottom: 20px;
            font-style: italic;
        }}
        .anteversion-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .anteversion-table th {{
            background-color: #007bff;
            color: white;
            padding: 12px 8px;
            text-align: center;
            font-weight: bold;
            font-size: 12px;
            border: 1px solid #0056b3;
        }}
        .anteversion-table td {{
            padding: 10px 8px;
            text-align: center;
            border: 1px solid #dee2e6;
            font-size: 13px;
        }}
        .anteversion-table .case-name {{
            background-color: #e9ecef;
            font-weight: bold;
            text-align: left;
            min-width: 120px;
        }}
        .anteversion-table .angle-value {{
            background-color: #d4edda;
            color: #155724;
            font-weight: bold;
        }}
        .anteversion-table .angle-missing {{
            background-color: #f8d7da;
            color: #721c24;
            font-style: italic;
        }}
        .anteversion-table .stats-value {{
            background-color: #d1ecf1;
            color: #0c5460;
            font-weight: bold;
        }}
        .anteversion-table .stats-missing {{
            background-color: #f8d7da;
            color: #721c24;
            font-style: italic;
        }}
        .table-notes {{
            margin-top: 20px;
            padding: 15px;
            background-color: #e9ecef;
            border-radius: 5px;
        }}
        .table-notes h4 {{
            color: #495057;
            margin-bottom: 10px;
        }}
        .table-notes ul {{
            margin: 0;
            padding-left: 20px;
        }}
        .table-notes li {{
            margin-bottom: 5px;
            color: #6c757d;
        }}
        
        /* Side Indicator Styles */
        .side-indicator {{
            font-size: 0.85em;
            font-weight: normal;
            padding: 2px 6px;
            border-radius: 3px;
            margin-left: 8px;
        }}
        
        .auto-detected-side .side-indicator.auto-left {{
            background-color: #e3f2fd;
            color: #1565c0;
            border: 1px solid #90caf9;
        }}
        
        .auto-detected-side .side-indicator.auto-right {{
            background-color: #f3e5f5;
            color: #7b1fa2;
            border: 1px solid #ce93d8;
        }}
        
        .explicit-side .side-indicator.explicit-left {{
            background-color: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #81c784;
        }}
        
        .explicit-side .side-indicator.explicit-right {{
            background-color: #fff3e0;
            color: #ef6c00;
            border: 1px solid #ffcc02;
        }}
        
        .inconsistent-side .side-indicator.inconsistent {{
            background-color: #ffebee;
            color: #c62828;
            border: 1px solid #ef5350;
            font-weight: bold;
        }}
        
        .case-name.auto-detected-side {{
            background-color: #f8f9ff;
        }}
        
        .case-name.explicit-side {{
            background-color: #f8fff8;
        }}
        
        .case-name.inconsistent-side {{
            background-color: #fff8f8;
        }}
        
        /* Case Header Side Indicators */
        .case-side-indicator {{
            font-size: 0.7em;
            font-weight: normal;
            padding: 4px 8px;
            border-radius: 4px;
            margin-left: 12px;
            vertical-align: middle;
        }}
        
        .case-side-indicator.auto-left {{
            background-color: #e3f2fd;
            color: #1565c0;
            border: 1px solid #90caf9;
        }}
        
        .case-side-indicator.auto-right {{
            background-color: #f3e5f5;
            color: #7b1fa2;
            border: 1px solid #ce93d8;
        }}
        
        .case-side-indicator.explicit-left {{
            background-color: #e8f5e8;
            color: #2e7d32;
            border: 1px solid #81c784;
        }}
        
        .case-side-indicator.explicit-right {{
            background-color: #fff3e0;
            color: #ef6c00;
            border: 1px solid #ffcc02;
        }}
        
        .case-section.auto-detected {{
            border-left: 4px solid #90caf9;
        }}
        
        .case-section.explicit-side {{
            border-left: 4px solid #81c784;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Batch Planning Data Comparison Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="content">
            {nav_html}
            
            <div class="main-content">
                {summary_html}
                {anteversion_table_html}
                {inter_rater_html}
                {cases_html}
            </div>
        </div>
        
        <div class="footer">
            <p>Generated by SlicerDataAnalyzer Batch Comparison Tool</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Save HTML report
    with open(html_filename, 'w') as f:
        f.write(html_content)
    
    print(f"Consolidated HTML report generated: {html_filename}")
    
    # Export to PDF if requested
    if export_pdf:
        # Collect all plot files for PDF export
        all_plot_files = []
        for result in case_results:
            if result['status'] == 'success':
                all_plot_files.extend(result['plot_files'])
        
        if all_plot_files:
            success, pdf_filename = export_to_pdf(html_content, all_plot_files, output_prefix, 
                                                title="Batch Planning Data Comparison Report")
            if success:
                print(f"PDF report generated: {pdf_filename}")
    
    return html_filename

def main():
    parser = argparse.ArgumentParser(description="Batch comparison of planning data across multiple testers.")
    parser.add_argument("--base_path", required=True, 
                       help="Base path containing H001, H002, H003 directories")
    parser.add_argument("--output", "-o", default="batch_comparison_report",
                       help="Output filename prefix (without extension). Combined with --output-path when provided.")
    parser.add_argument("--output-path", default=None,
                       help="Directory to store all generated files. Defaults to current working directory.")
    parser.add_argument("--pdf", action="store_true", 
                       help="Also export results to PDF format")
    parser.add_argument("--excel", action="store_true",
                       help="Export raw data to Excel spreadsheet format (.xlsx)")
    parser.add_argument("--excel-detailed", action="store_true",
                       help="Export detailed Excel with matrices and vectors broken into individual components")
    parser.add_argument("--translation-only", action="store_true", 
                       help="Only display translation (positional) data from matrices")
    parser.add_argument("--no-landmark-rotation", action="store_true",
                       help="Exclude rotation analysis for anatomical landmarks (S3GreaterTroch, S3TopLesserTroch, S3FemoralSphere)")
    parser.add_argument("--side", choices=['Left', 'Right', 'Both', 'Auto'], default='Both',
                       help="Filter data by patient side: Left, Right, Both, or Auto (detect from XML) - default: Both")
    
    args = parser.parse_args()

    # Resolve output prefix and ensure destination directory exists when requested
    output_prefix = args.output
    if args.output_path:
        output_base = os.path.abspath(os.path.expanduser(args.output_path))
        os.makedirs(output_base, exist_ok=True)
        if not os.path.isabs(output_prefix):
            output_prefix = os.path.join(output_base, output_prefix)

    output_parent_dir = os.path.dirname(output_prefix)
    if output_parent_dir:
        os.makedirs(output_parent_dir, exist_ok=True)
    
    # Validate base path
    if not os.path.exists(args.base_path):
        print(f"Error: Base path {args.base_path} does not exist")
        sys.exit(1)
    
    # Create output directory for individual case plots
    output_dir = f"{output_prefix}_plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all case sets
    print("Scanning for case folders...")
    case_sets = find_case_folders(args.base_path)
    
    if not case_sets:
        print("No complete case sets found. Please check your directory structure.")
        sys.exit(1)
    
    print(f"Found {len(case_sets)} complete case sets for comparison")
    
    # Process each case
    case_results = []
    for i, (case_name, h001_xml, h002_xml, h003_xml) in enumerate(case_sets, 1):
        print(f"Processing case {i}/{len(case_sets)}: {case_name}")
        
        try:
            result = generate_case_comparison_data(
                h001_xml, h002_xml, h003_xml, 
                case_name, output_dir, 
                args.translation_only, args.side, args.no_landmark_rotation
            )
            case_results.append(result)
            
            if result['status'] == 'success':
                print(f"  ✓ Generated {len(result['plot_files'])} plots")
            else:
                print(f"  ⚠ {result['status']}")
                
        except Exception as e:
            print(f"  ❌ Error processing case {case_name}: {str(e)}")
            case_results.append({
                'case_name': case_name,
                'status': 'error',
                'common_tags': [],
                'plot_files': [],
                'stats_html': f'<p>Error: {str(e)}</p>'
            })
    
    # Generate consolidated report
    print("\nGenerating consolidated HTML report...")
    
    # Generate inter-rater analysis
    print("Generating inter-rater analysis...")
    inter_rater_results = generate_inter_rater_analysis(case_results, output_dir)
    
    html_filename = generate_consolidated_html_report(case_results, output_prefix, args.pdf, inter_rater_results)
    
    # Export to Excel if requested
    if args.excel:
        print("Exporting raw data to Excel...")
        excel_filename = export_to_excel(case_results, output_prefix)
        if excel_filename:
            print(f"Excel export saved as: {excel_filename}")
    
    # Export to detailed Excel if requested  
    if args.excel_detailed:
        print("Exporting detailed component-wise data to Excel...")
        detailed_excel_filename = export_to_excel_detailed(case_results, output_prefix)
        if detailed_excel_filename:
            print(f"Detailed Excel export saved as: {detailed_excel_filename}")
    
    # Print summary
    successful_cases = len([r for r in case_results if r['status'] == 'success'])
    total_plots = sum(len(r['plot_files']) for r in case_results if r['status'] == 'success')
    
    print(f"\nBatch processing complete!")
    print(f"Cases processed: {len(case_results)}")
    print(f"Successful: {successful_cases}")
    print(f"Total plots generated: {total_plots}")
    print(f"Report saved as: {html_filename}")

def generate_inter_rater_html_section(inter_rater_results, report_dir=None):
    """
    Generate HTML section for inter-rater analysis results.
    
    Args:
        inter_rater_results: Results from generate_inter_rater_analysis()
        report_dir: Directory that will contain the final HTML file
    
    Returns:
        HTML string for inter-rater analysis section
    """
    if not inter_rater_results:
        return ""
    base_dir = report_dir or os.curdir

    def _relative_path(path):
        if not path:
            return path
        try:
            return os.path.relpath(path, start=base_dir)
        except ValueError:
            return path
    
    html = """
    <div class="inter-rater-analysis">
        <h2>Inter-Rater Reliability Analysis</h2>
        <p>Comprehensive analysis of measurement agreement and reliability between the three testers (H001, H002, H003).</p>
        
        <!-- Reliability Metrics Summary -->
        <div class="reliability-summary">
            <h3>Reliability Metrics</h3>
            <div class="metrics-grid">
    """
    
    # Add ICC values
    reliability_metrics = inter_rater_results.get('reliability_metrics', {})
    for metric_name, metric_data in reliability_metrics.items():
        side = metric_name.replace('_ICC', '')
        icc_value = metric_data['value']
        ci_lower = metric_data['ci_lower']
        ci_upper = metric_data['ci_upper']
        n_cases = metric_data['n_cases']
        
        # Interpret ICC value
        if icc_value < 0.5:
            interpretation = "Poor"
            color_class = "poor"
        elif icc_value < 0.75:
            interpretation = "Moderate"
            color_class = "moderate"
        elif icc_value < 0.9:
            interpretation = "Good"
            color_class = "good"
        else:
            interpretation = "Excellent"
            color_class = "excellent"
        
        html += f"""
                <div class="metric-card {color_class}">
                    <h4>{side} Side Femoral Anteversion</h4>
                    <div class="metric-value">ICC = {icc_value:.3f}</div>
                    <div class="metric-ci">95% CI: [{ci_lower:.3f}, {ci_upper:.3f}]</div>
                    <div class="metric-interpretation">{interpretation} Reliability</div>
                    <div class="metric-n">n = {n_cases} cases</div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Bland-Altman Plots -->
        <div class="bland-altman-section">
            <h3>Bland-Altman Agreement Analysis</h3>
            <p>These plots show the agreement between pairs of testers. Points should be randomly distributed around zero with minimal bias.</p>
            <div class="plots-grid">
    """
    
    # Add Bland-Altman plots
    for plot_info in inter_rater_results.get('bland_altman_plots', []):
        img_src = _relative_path(plot_info['filename'])
        side = plot_info['side']
        testers = plot_info['testers']
        stats = plot_info['stats']
        
        html += f"""
                <div class="plot-item">
                    <h4>{side} Side: {testers}</h4>
                    <img src="{img_src}" alt="Bland-Altman {side} {testers}" class="inter-rater-plot">
                    <div class="plot-stats">
                        <span>Mean Diff: {stats['mean_diff']:.3f}°</span> | 
                        <span>SD: {stats['std_diff']:.3f}°</span> | 
                        <span>n = {stats['n_pairs']}</span>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Correlation Analysis -->
        <div class="correlation-section">
            <h3>Correlation Analysis</h3>
            <p>Scatter plots showing linear relationships between tester measurements with correlation coefficients.</p>
            <div class="plots-grid">
    """
    
    # Add correlation plots
    for plot_info in inter_rater_results.get('correlation_plots', []):
        img_src = _relative_path(plot_info['filename'])
        side = plot_info['side']
        testers = plot_info['testers']
        stats = plot_info['stats']
        
        html += f"""
                <div class="plot-item">
                    <h4>{side} Side: {testers}</h4>
                    <img src="{img_src}" alt="Correlation {side} {testers}" class="inter-rater-plot">
                    <div class="plot-stats">
                        <span>r = {stats['correlation']:.3f}</span> | 
                        <span>R² = {stats['r_squared']:.3f}</span> | 
                        <span>p = {stats['p_value']:.3e}</span>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Distribution Analysis -->
        <div class="distribution-section">
            <h3>Measurement Distribution</h3>
            <p>Box plots showing the distribution of measurements for each tester, useful for identifying systematic biases.</p>
            <div class="plots-grid">
    """
    
    # Add distribution plots
    for plot_info in inter_rater_results.get('distribution_plots', []):
        img_src = _relative_path(plot_info['filename'])
        side = plot_info['side']
        stats = plot_info['stats']
        
        html += f"""
                <div class="plot-item">
                    <h4>{side} Side Distribution</h4>
                    <img src="{img_src}" alt="Distribution {side}" class="inter-rater-plot">
                    <div class="plot-stats">
                        <span>H001: μ={stats['means'][0]:.2f}°</span> | 
                        <span>H002: μ={stats['means'][1]:.2f}°</span> | 
                        <span>H003: μ={stats['means'][2]:.2f}°</span>
                    </div>
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <div class="inter-rater-notes">
            <h4>Interpretation Guidelines:</h4>
            <ul>
                <li><strong>ICC Values:</strong> &lt;0.5 Poor, 0.5-0.75 Moderate, 0.75-0.9 Good, &gt;0.9 Excellent reliability</li>
                <li><strong>Bland-Altman:</strong> Points should scatter randomly around zero; systematic patterns indicate bias</li>
                <li><strong>Correlation:</strong> High correlation (r&gt;0.8) indicates strong linear relationship between testers</li>
                <li><strong>Distribution:</strong> Similar box plot shapes indicate consistent measurement distributions</li>
            </ul>
        </div>
    </div>
    """
    
    return html

def create_bland_altman_plot(data1, data2, title, output_filename, tester1="H001", tester2="H002"):
    """
    Create Bland-Altman plot for inter-rater agreement analysis.
    
    Args:
        data1, data2: Arrays of measurements from two testers
        title: Plot title
        output_filename: Output file path
        tester1, tester2: Names of the testers being compared
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Remove any None values
    valid_pairs = [(d1, d2) for d1, d2 in zip(data1, data2) if d1 is not None and d2 is not None]
    if len(valid_pairs) < 2:
        return None
    
    data1_clean, data2_clean = zip(*valid_pairs)
    data1_clean = np.array(data1_clean)
    data2_clean = np.array(data2_clean)
    
    # Calculate means and differences
    means = (data1_clean + data2_clean) / 2
    differences = data1_clean - data2_clean
    
    # Calculate statistics
    mean_diff = np.mean(differences)
    std_diff = np.std(differences)
    
    # Create plot
    plt.figure(figsize=(5, 4))
    plt.scatter(means, differences, alpha=0.6, s=50)
    
    # Add horizontal lines for mean and limits of agreement
    plt.axhline(mean_diff, color='red', linestyle='-', linewidth=2, label=f'Mean difference: {mean_diff:.3f}')
    plt.axhline(mean_diff + 1.96*std_diff, color='red', linestyle='--', linewidth=1, 
                label=f'+1.96 SD: {mean_diff + 1.96*std_diff:.3f}')
    plt.axhline(mean_diff - 1.96*std_diff, color='red', linestyle='--', linewidth=1, 
                label=f'-1.96 SD: {mean_diff - 1.96*std_diff:.3f}')
    plt.axhline(0, color='black', linestyle='-', alpha=0.3)
    
    plt.xlabel(f'Mean of {tester1} and {tester2}')
    plt.ylabel(f'Difference ({tester1} - {tester2})')
    plt.title(f'Bland-Altman Plot: {title}\n({tester1} vs {tester2})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add text box with statistics
    textstr = f'n = {len(valid_pairs)}\nMean diff = {mean_diff:.3f}\nSD = {std_diff:.3f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'mean_diff': mean_diff,
        'std_diff': std_diff,
        'n_pairs': len(valid_pairs),
        'limits_agreement': (mean_diff - 1.96*std_diff, mean_diff + 1.96*std_diff)
    }

def create_correlation_plot(data1, data2, title, output_filename, tester1="H001", tester2="H002"):
    """
    Create correlation scatter plot with regression line and statistics.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    from scipy import stats
    
    # Remove any None values
    valid_pairs = [(d1, d2) for d1, d2 in zip(data1, data2) if d1 is not None and d2 is not None]
    if len(valid_pairs) < 2:
        return None
    
    data1_clean, data2_clean = zip(*valid_pairs)
    data1_clean = np.array(data1_clean)
    data2_clean = np.array(data2_clean)
    
    # Calculate correlation and regression
    correlation, p_value = stats.pearsonr(data1_clean, data2_clean)
    slope, intercept, r_value, p_val, std_err = stats.linregress(data1_clean, data2_clean)
    
    # Create plot
    plt.figure(figsize=(5, 4))
    plt.scatter(data1_clean, data2_clean, alpha=0.6, s=50)
    
    # Add regression line
    line_x = np.linspace(min(data1_clean), max(data1_clean), 100)
    line_y = slope * line_x + intercept
    plt.plot(line_x, line_y, 'r-', linewidth=2, 
             label=f'y = {slope:.3f}x + {intercept:.3f}')
    
    # Add identity line for reference
    min_val = min(min(data1_clean), min(data2_clean))
    max_val = max(max(data1_clean), max(data2_clean))
    plt.plot([min_val, max_val], [min_val, max_val], 'k--', alpha=0.5, label='Perfect agreement')
    
    plt.xlabel(f'{tester1} Measurements')
    plt.ylabel(f'{tester2} Measurements')
    plt.title(f'Correlation Plot: {title}\n({tester1} vs {tester2})')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Add text box with statistics
    textstr = f'n = {len(valid_pairs)}\nr = {correlation:.3f}\nR² = {r_value**2:.3f}\np = {p_value:.3e}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
    plt.text(0.05, 0.95, textstr, transform=plt.gca().transAxes, fontsize=10,
             verticalalignment='top', bbox=props)
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'correlation': correlation,
        'p_value': p_value,
        'r_squared': r_value**2,
        'slope': slope,
        'intercept': intercept,
        'n_pairs': len(valid_pairs)
    }

def create_box_plot_distribution(data_dict, title, output_filename):
    """
    Create box plot showing distribution of measurements across testers.
    
    Args:
        data_dict: Dict with keys 'H001', 'H002', 'H003' and list values
        title: Plot title
        output_filename: Output file path
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    # Prepare data for box plot
    tester_names = ['H001', 'H002', 'H003']
    plot_data = []
    labels = []
    
    for tester in tester_names:
        if tester in data_dict:
            clean_data = [x for x in data_dict[tester] if x is not None]
            if clean_data:
                plot_data.append(clean_data)
                labels.append(f'{tester}\n(n={len(clean_data)})')
    
    if not plot_data:
        return None
    
    # Create box plot with adjusted figure size for 2-column grid
    plt.figure(figsize=(8, 5))
    box_plot = plt.boxplot(plot_data, tick_labels=labels, patch_artist=True)
    
    # Color the boxes
    colors = ['lightblue', 'lightgreen', 'lightcoral']
    for patch, color in zip(box_plot['boxes'], colors[:len(plot_data)]):
        patch.set_facecolor(color)
    
    plt.ylabel('Measurement Value')
    plt.title(f'Distribution Comparison: {title}')
    plt.grid(True, alpha=0.3)
    
    # Add statistics text
    stats_text = []
    for i, (data, label) in enumerate(zip(plot_data, labels)):
        mean_val = np.mean(data)
        std_val = np.std(data)
        stats_text.append(f'{tester_names[i]}: μ={mean_val:.3f}, σ={std_val:.3f}')
    
    plt.text(0.02, 0.98, '\n'.join(stats_text), transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'means': [np.mean(data) for data in plot_data],
        'stds': [np.std(data) for data in plot_data],
        'n_values': [len(data) for data in plot_data]
    }

def calculate_icc(data_matrix):
    """
    Calculate Intraclass Correlation Coefficient (ICC) for inter-rater reliability.
    
    Args:
        data_matrix: 2D array where rows are subjects and columns are raters
    
    Returns:
        ICC value and 95% confidence interval
    """
    import numpy as np
    from scipy import stats
    
    # Remove rows with any missing data
    clean_matrix = []
    for row in data_matrix:
        if all(x is not None for x in row):
            clean_matrix.append(row)
    
    if len(clean_matrix) < 2:
        return None, None, None
    
    data = np.array(clean_matrix)
    n_subjects, n_raters = data.shape
    
    # Calculate ICC(2,1) - Two-way random effects, single measures, absolute agreement
    # This is the most common ICC for inter-rater reliability
    
    # Calculate means
    subject_means = np.mean(data, axis=1)
    rater_means = np.mean(data, axis=0)
    grand_mean = np.mean(data)
    
    # Calculate sum of squares
    SST = np.sum((data - grand_mean)**2)
    SSB = n_raters * np.sum((subject_means - grand_mean)**2)  # Between subjects
    SSW = np.sum((data - subject_means[:, np.newaxis])**2)    # Within subjects
    SSE = SSW - (n_subjects * np.sum((rater_means - grand_mean)**2))  # Error
    
    # Calculate mean squares
    MSB = SSB / (n_subjects - 1)
    MSE = SSE / ((n_subjects - 1) * (n_raters - 1))
    
    # Calculate ICC
    icc = (MSB - MSE) / (MSB + (n_raters - 1) * MSE)
    
    # Calculate confidence interval (approximate)
    F = MSB / MSE
    df1 = n_subjects - 1
    df2 = (n_subjects - 1) * (n_raters - 1)
    
    F_lower = F / stats.f.ppf(0.975, df1, df2)
    F_upper = F / stats.f.ppf(0.025, df1, df2)
    
    ci_lower = (F_lower - 1) / (F_lower + n_raters - 1)
    ci_upper = (F_upper - 1) / (F_upper + n_raters - 1)
    
    return icc, ci_lower, ci_upper

def generate_inter_rater_analysis(case_results, output_dir):
    """
    Generate comprehensive inter-rater analysis plots and statistics.
    
    Args:
        case_results: List of case comparison results
        output_dir: Directory to save plots
    
    Returns:
        Dictionary with analysis results and plot filenames
    """
    import os
    import numpy as np
    
    # Create inter-rater analysis subdirectory
    inter_rater_dir = os.path.join(output_dir, "inter_rater_analysis")
    os.makedirs(inter_rater_dir, exist_ok=True)
    
    analysis_results = {
        'bland_altman_plots': [],
        'correlation_plots': [],
        'distribution_plots': [],
        'reliability_metrics': {}
    }
    
    # Extract femoral anteversion angles for analysis
    anteversion_data = extract_femoral_anteversion_angles(case_results)
    
    if anteversion_data:
        # Prepare data for analysis
        right_h001 = []
        right_h002 = []
        right_h003 = []
        left_h001 = []
        left_h002 = []
        left_h003 = []
        
        for case_name, case_data in anteversion_data.items():
            right_angles = case_data.get('Right', [None, None, None])
            left_angles = case_data.get('Left', [None, None, None])
            
            right_h001.append(right_angles[0])
            right_h002.append(right_angles[1])
            right_h003.append(right_angles[2])
            
            left_h001.append(left_angles[0])
            left_h002.append(left_angles[1])
            left_h003.append(left_angles[2])
        
        # Generate Bland-Altman plots for each pair of testers
        tester_pairs = [('H001', 'H002'), ('H001', 'H003'), ('H002', 'H003')]
        
        for side, side_data in [('Right', (right_h001, right_h002, right_h003)), 
                               ('Left', (left_h001, left_h002, left_h003))]:
            h001_data, h002_data, h003_data = side_data
            data_arrays = [h001_data, h002_data, h003_data]
            
            for i, (tester1, tester2) in enumerate(tester_pairs):
                data1 = data_arrays[0] if tester1 == 'H001' else (data_arrays[1] if tester1 == 'H002' else data_arrays[2])
                data2 = data_arrays[0] if tester2 == 'H001' else (data_arrays[1] if tester2 == 'H002' else data_arrays[2])
                
                # Bland-Altman plot
                ba_filename = os.path.join(inter_rater_dir, f"bland_altman_{side.lower()}_{tester1}_{tester2}.png")
                ba_stats = create_bland_altman_plot(data1, data2, f"{side} Femoral Anteversion Angle", 
                                                  ba_filename, tester1, tester2)
                if ba_stats:
                    analysis_results['bland_altman_plots'].append({
                        'filename': ba_filename,
                        'side': side,
                        'testers': f"{tester1} vs {tester2}",
                        'stats': ba_stats
                    })
                
                # Correlation plot
                corr_filename = os.path.join(inter_rater_dir, f"correlation_{side.lower()}_{tester1}_{tester2}.png")
                corr_stats = create_correlation_plot(data1, data2, f"{side} Femoral Anteversion Angle", 
                                                   corr_filename, tester1, tester2)
                if corr_stats:
                    analysis_results['correlation_plots'].append({
                        'filename': corr_filename,
                        'side': side,
                        'testers': f"{tester1} vs {tester2}",
                        'stats': corr_stats
                    })
            
            # Distribution box plot
            dist_filename = os.path.join(inter_rater_dir, f"distribution_{side.lower()}_all_testers.png")
            dist_stats = create_box_plot_distribution({
                'H001': h001_data,
                'H002': h002_data, 
                'H003': h003_data
            }, f"{side} Femoral Anteversion Angle", dist_filename)
            if dist_stats:
                analysis_results['distribution_plots'].append({
                    'filename': dist_filename,
                    'side': side,
                    'stats': dist_stats
                })
            
            # Calculate ICC for this side
            data_matrix = []
            for h1, h2, h3 in zip(h001_data, h002_data, h003_data):
                if all(x is not None for x in [h1, h2, h3]):
                    data_matrix.append([h1, h2, h3])
            
            if len(data_matrix) >= 2:
                icc, ci_lower, ci_upper = calculate_icc(data_matrix)
                if icc is not None:
                    analysis_results['reliability_metrics'][f'{side}_ICC'] = {
                        'value': icc,
                        'ci_lower': ci_lower,
                        'ci_upper': ci_upper,
                        'n_cases': len(data_matrix)
                    }
    
    return analysis_results

def export_to_excel(case_results, output_prefix):
    """
    Export raw planning data from all cases to Excel format.
    
    Args:
        case_results: List of case comparison results
        output_prefix: Output filename prefix (without extension)
    
    Returns:
        Excel filename if successful, None if failed
    """
    try:
        import pandas as pd
    except ImportError:
        print("Warning: pandas not available. Install with: pip install pandas")
        print("Excel export skipped.")
        return None
    
    try:
        import openpyxl
        excel_engine = 'openpyxl'
    except ImportError:
        try:
            import xlsxwriter
            excel_engine = 'xlsxwriter'
        except ImportError:
            print("Warning: Neither openpyxl nor xlsxwriter available.")
            print("Install with: pip install openpyxl  OR  pip install xlsxwriter")
            print("Excel export skipped.")
            return None
    
    # Prepare data for Excel export
    all_data_rows = []
    stem_sheet_rows = []
    config_anteversion_rows = []
    tester_index_map = {tester: idx for idx, tester in enumerate(TESTER_IDS)}
    
    for result in case_results:
        if result['status'] != 'success':
            continue
        
        case_name = result['case_name']

        # Precompute anteversion lookup per tester/side for this case
        case_angles = result.get('anteversion_angles') or {}
        tester_angle_lookup = {}
        for tester_label, tester_idx in tester_index_map.items():
            tester_angle_lookup[tester_label] = {}
            for side in ('Left', 'Right'):
                side_values = case_angles.get(side)
                angle_value = None
                if isinstance(side_values, (list, tuple)) and tester_idx < len(side_values):
                    angle_value = side_values[tester_idx]
                tester_angle_lookup[tester_label][side] = angle_value
        
        # Extract raw data from each case
        if 'raw_data' in result:
            data1, data2, data3 = result['raw_data']
            common_tags = result['common_tags']
            
            for tag in common_tags:
                # Get values from all three testers
                value1 = data1.get(tag)
                value2 = data2.get(tag)  
                value3 = data3.get(tag)
                
                # Determine data type based on tag name and content
                data_type = "Unknown"
                if "matrix" in tag.lower() or "mat" in tag.lower():
                    data_type = "Matrix"
                elif "vector" in tag.lower() or any(x in tag.lower() for x in ['p0', 'p1', 'normal']):
                    data_type = "Vector"
                elif any(x in tag.lower() for x in ['angle', 'length', 'distance', 'radius']):
                    data_type = "Scalar"
                elif value1 and len(str(value1).split()) == 16:
                    data_type = "Matrix" 
                elif value1 and len(str(value1).split()) == 3:
                    data_type = "Vector"
                else:
                    data_type = "Scalar"
                
                # Determine anatomical side
                anatomical_side = "Both"
                if "_R" in tag or "_Right" in tag:
                    anatomical_side = "Right"
                elif "_L" in tag or "_Left" in tag:
                    anatomical_side = "Left"
                
                # Add row for this measurement
                row = {
                    'Case': case_name,
                    'Parameter': tag,
                    'Data_Type': data_type,
                    'Anatomical_Side': anatomical_side,
                    'H001_Value': value1,
                    'H002_Value': value2,
                    'H003_Value': value3
                }
                all_data_rows.append(row)

        for stem_entry in result.get('stem_info', []):
            rotation = stem_entry.get('rotation') or {}
            translation = stem_entry.get('translation') or {}
            tester_label = stem_entry.get('tester')
            normalized_side = _normalize_side_label(stem_entry.get('configured_side')) or _normalize_side_label(stem_entry.get('requested_side'))
            angle_value = None
            if tester_label in tester_angle_lookup and normalized_side:
                angle_value = tester_angle_lookup[tester_label].get(normalized_side)
            row = {
                'Case': case_name,
                'Tester': stem_entry.get('tester'),
                'Stem_UID': stem_entry.get('uid'),
                'Manufacturer': stem_entry.get('manufacturer'),
                'Stem_Model': stem_entry.get('stem_enum_name'),
                'Stem_Label': stem_entry.get('stem_friendly_name'),
                'RCC_ID': stem_entry.get('rcc_id'),
                'Requested_Side': stem_entry.get('requested_side'),
                'Configured_Side': stem_entry.get('configured_side'),
                'Config_State': stem_entry.get('state'),
                'Hip_Config_UID': stem_entry.get('hip_config_uid'),
                'Hip_Config_Index': stem_entry.get('hip_config_index'),
                'Hip_Config_Name': stem_entry.get('hip_config_name'),
                'Matrix_Source': stem_entry.get('source'),
                'Matrix_Value': stem_entry.get('matrix_raw'),
                'XML_Path': stem_entry.get('xml_path'),
                'Error': stem_entry.get('error'),
            }

            for key in STEM_ROTATION_KEYS:
                row[f'Rot_{key}'] = rotation.get(key)
            for key in STEM_TRANSLATION_KEYS:
                row[f'Trans_{key}'] = translation.get(key)

            stem_sheet_rows.append(row)

            config_row = {
                'Case': case_name,
                'Tester': tester_label,
                'Hip_Config_Index': stem_entry.get('hip_config_index'),
                'Hip_Config_UID': stem_entry.get('hip_config_uid'),
                'Hip_Config_Name': stem_entry.get('hip_config_name'),
                'Config_Source': stem_entry.get('source'),
                'Config_State': stem_entry.get('state'),
                'Requested_Side': stem_entry.get('requested_side'),
                'Configured_Side': stem_entry.get('configured_side'),
                'Side_Normalized': normalized_side,
                'Anteversion_Angle_Deg': angle_value,
                'Stem_UID': stem_entry.get('uid'),
                'Stem_Model': stem_entry.get('stem_enum_name'),
                'Stem_Label': stem_entry.get('stem_friendly_name'),
                'Manufacturer': stem_entry.get('manufacturer'),
                'RCC_ID': stem_entry.get('rcc_id'),
                'Matrix_Value': stem_entry.get('matrix_raw'),
                'XML_Path': stem_entry.get('xml_path'),
                'Notes': stem_entry.get('error'),
            }
            config_anteversion_rows.append(config_row)
    
    if not all_data_rows:
        print("Warning: No data available for Excel export.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(all_data_rows)
    
    # Create Excel file with multiple sheets
    excel_filename = f"{output_prefix}_raw_data.xlsx"
    
    with pd.ExcelWriter(excel_filename, engine=excel_engine) as writer:
        # Main sheet with all data
        df.to_excel(writer, sheet_name='All_Data', index=False)
        
        # Separate sheets by data type
        for data_type in df['Data_Type'].unique():
            type_df = df[df['Data_Type'] == data_type]
            sheet_name = data_type.replace(' ', '_')
            type_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Separate sheets by anatomical side
        for side in df['Anatomical_Side'].unique():
            if side != 'Both':
                side_df = df[df['Anatomical_Side'] == side]
                sheet_name = f'{side}_Side'
                side_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Summary statistics sheet
        summary_data = []
        for case in df['Case'].unique():
            case_df = df[df['Case'] == case]
            summary_data.append({
                'Case': case,
                'Total_Parameters': len(case_df),
                'Matrix_Parameters': len(case_df[case_df['Data_Type'] == 'Matrix']),
                'Vector_Parameters': len(case_df[case_df['Data_Type'] == 'Vector']),
                'Scalar_Parameters': len(case_df[case_df['Data_Type'] == 'Scalar']),
                'Left_Side_Parameters': len(case_df[case_df['Anatomical_Side'] == 'Left']),
                'Right_Side_Parameters': len(case_df[case_df['Anatomical_Side'] == 'Right']),
                'Both_Side_Parameters': len(case_df[case_df['Anatomical_Side'] == 'Both'])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Special sheet for femoral anteversion angles (if available)
        anteversion_rows = []
        for result in case_results:
            if result['status'] == 'success' and 'anteversion_angles' in result:
                case_name = result['case_name']
                angles = result['anteversion_angles']
                row = {
                    'Case': case_name,
                    'Right_H001': None,
                    'Right_H002': None,
                    'Right_H003': None,
                    'Left_H001': None,
                    'Left_H002': None,
                    'Left_H003': None,
                }
                right_angles = angles.get('Right', [None, None, None])
                left_angles = angles.get('Left', [None, None, None])
                for idx, tester_label in enumerate(TESTER_IDS):
                    if idx < len(right_angles):
                        row[f'Right_{tester_label}'] = right_angles[idx]
                    if idx < len(left_angles):
                        row[f'Left_{tester_label}'] = left_angles[idx]
                anteversion_rows.append(row)

        anteversion_columns = [
            'Case',
            'Right_H001', 'Right_H002', 'Right_H003',
            'Left_H001', 'Left_H002', 'Left_H003',
        ]
        config_columns = [
            'Case', 'Tester', 'Hip_Config_Index', 'Hip_Config_UID', 'Hip_Config_Name',
            'Config_Source', 'Config_State', 'Requested_Side', 'Configured_Side',
            'Side_Normalized', 'Anteversion_Angle_Deg', 'Stem_UID', 'Stem_Model',
            'Stem_Label', 'Manufacturer', 'RCC_ID', 'Matrix_Value', 'XML_Path', 'Notes'
        ]

        if anteversion_rows or config_anteversion_rows:
            anteversion_df = pd.DataFrame(anteversion_rows, columns=anteversion_columns)
            sheet_name = 'Femoral_Anteversion_Angles'
            anteversion_df.to_excel(writer, sheet_name=sheet_name, index=False)
            summary_height = len(anteversion_df) + 1  # include header row

            if config_anteversion_rows:
                config_df = pd.DataFrame(config_anteversion_rows, columns=config_columns)
                label_row_df = pd.DataFrame([
                    {'Case': 'Per-Configuration View (hipImplantConfig history)'}
                ])
                label_row_index = summary_height + 1
                label_row_df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    header=False,
                    startrow=label_row_index,
                )
                config_start_row = label_row_index + 1
                config_df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    startrow=config_start_row,
                )

        if stem_sheet_rows:
            stems_df = pd.DataFrame(stem_sheet_rows)
            stems_df.to_excel(writer, sheet_name='Stem_Info', index=False)
    
    print(f"Raw data exported to Excel: {excel_filename}")
    return excel_filename

def export_to_excel_detailed(case_results, output_prefix):
    """
    Export detailed planning data with matrices and vectors broken into individual components.
    
    Args:
        case_results: List of case comparison results
        output_prefix: Output filename prefix (without extension)
    
    Returns:
        Excel filename if successful, None if failed
    """
    try:
        import pandas as pd
    except ImportError:
        print("Warning: pandas not available. Install with: pip install pandas")
        print("Detailed Excel export skipped.")
        return None
    
    try:
        import openpyxl
        excel_engine = 'openpyxl'
    except ImportError:
        try:
            import xlsxwriter
            excel_engine = 'xlsxwriter'
        except ImportError:
            print("Warning: Neither openpyxl nor xlsxwriter available.")
            print("Install with: pip install openpyxl  OR  pip install xlsxwriter")
            print("Detailed Excel export skipped.")
            return None
    
    # Prepare detailed data for Excel export
    detailed_rows = []
    stem_sheet_rows = []
    
    def parse_matrix_values(value_string):
        """Parse matrix string into individual components."""
        if not value_string:
            return {}
        
        try:
            values = value_string.strip().split()
            if len(values) == 16:  # 4x4 matrix
                matrix_dict = {}
                for i in range(4):
                    for j in range(4):
                        idx = i * 4 + j
                        matrix_dict[f'M_{i+1}{j+1}'] = float(values[idx])
                # Also extract translation components
                matrix_dict['Translation_X'] = float(values[3])
                matrix_dict['Translation_Y'] = float(values[7])
                matrix_dict['Translation_Z'] = float(values[11])
                return matrix_dict
        except:
            pass
        return {}
    
    def parse_vector_values(value_string):
        """Parse vector string into individual components."""
        if not value_string:
            return {}
        
        try:
            values = value_string.strip().split()
            if len(values) == 3:  # 3D vector
                return {
                    'X': float(values[0]),
                    'Y': float(values[1]),
                    'Z': float(values[2])
                }
        except:
            pass
        return {}
    
    for result in case_results:
        if result['status'] != 'success':
            continue
        
        case_name = result['case_name']
        
        # Extract raw data from each case
        if 'raw_data' in result:
            data1, data2, data3 = result['raw_data']
            common_tags = result['common_tags']
            
            for tag in common_tags:
                # Get values from all three testers
                value1 = data1.get(tag)
                value2 = data2.get(tag)  
                value3 = data3.get(tag)
                
                # Determine data type and anatomical side
                data_type = "Unknown"
                anatomical_side = "Both"
                
                if "matrix" in tag.lower() or "mat" in tag.lower():
                    data_type = "Matrix"
                elif "vector" in tag.lower() or any(x in tag.lower() for x in ['p0', 'p1', 'normal']):
                    data_type = "Vector"
                elif any(x in tag.lower() for x in ['angle', 'length', 'distance', 'radius']):
                    data_type = "Scalar"
                elif value1 and len(str(value1).split()) == 16:
                    data_type = "Matrix" 
                elif value1 and len(str(value1).split()) == 3:
                    data_type = "Vector"
                else:
                    data_type = "Scalar"
                
                if "_R" in tag or "_Right" in tag:
                    anatomical_side = "Right"
                elif "_L" in tag or "_Left" in tag:
                    anatomical_side = "Left"
                
                # Process based on data type
                if data_type == "Matrix":
                    # Break down matrix into components
                    matrix1 = parse_matrix_values(value1)
                    matrix2 = parse_matrix_values(value2)
                    matrix3 = parse_matrix_values(value3)
                    
                    # Create a row for each matrix component
                    all_components = set()
                    if matrix1: all_components.update(matrix1.keys())
                    if matrix2: all_components.update(matrix2.keys())
                    if matrix3: all_components.update(matrix3.keys())
                    
                    for component in sorted(all_components):
                        row = {
                            'Case': case_name,
                            'Parameter': tag,
                            'Component': component,
                            'Data_Type': f"Matrix_{component}",
                            'Anatomical_Side': anatomical_side,
                            'H001_Value': matrix1.get(component),
                            'H002_Value': matrix2.get(component),
                            'H003_Value': matrix3.get(component)
                        }
                        detailed_rows.append(row)
                
                elif data_type == "Vector":
                    # Break down vector into components
                    vector1 = parse_vector_values(value1)
                    vector2 = parse_vector_values(value2)
                    vector3 = parse_vector_values(value3)
                    
                    # Create a row for each vector component
                    for component in ['X', 'Y', 'Z']:
                        row = {
                            'Case': case_name,
                            'Parameter': tag,
                            'Component': component,
                            'Data_Type': f"Vector_{component}",
                            'Anatomical_Side': anatomical_side,
                            'H001_Value': vector1.get(component),
                            'H002_Value': vector2.get(component),
                            'H003_Value': vector3.get(component)
                        }
                        detailed_rows.append(row)
                
                else:  # Scalar
                    # Single value - no breakdown needed
                    try:
                        val1 = float(value1) if value1 else None
                        val2 = float(value2) if value2 else None
                        val3 = float(value3) if value3 else None
                    except:
                        val1, val2, val3 = value1, value2, value3
                    
                    row = {
                        'Case': case_name,
                        'Parameter': tag,
                        'Component': 'Value',
                        'Data_Type': data_type,
                        'Anatomical_Side': anatomical_side,
                        'H001_Value': val1,
                        'H002_Value': val2,
                        'H003_Value': val3
                    }
                    detailed_rows.append(row)

        for stem_entry in result.get('stem_info', []):
            rotation = stem_entry.get('rotation') or {}
            translation = stem_entry.get('translation') or {}
            row = {
                'Case': case_name,
                'Tester': stem_entry.get('tester'),
                'Stem_UID': stem_entry.get('uid'),
                'Manufacturer': stem_entry.get('manufacturer'),
                'Stem_Model': stem_entry.get('stem_enum_name'),
                'Stem_Label': stem_entry.get('stem_friendly_name'),
                'RCC_ID': stem_entry.get('rcc_id'),
                'Requested_Side': stem_entry.get('requested_side'),
                'Configured_Side': stem_entry.get('configured_side'),
                'Config_State': stem_entry.get('state'),
                'Hip_Config_UID': stem_entry.get('hip_config_uid'),
                'Hip_Config_Index': stem_entry.get('hip_config_index'),
                'Hip_Config_Name': stem_entry.get('hip_config_name'),
                'Matrix_Source': stem_entry.get('source'),
                'Matrix_Value': stem_entry.get('matrix_raw'),
                'XML_Path': stem_entry.get('xml_path'),
                'Error': stem_entry.get('error'),
            }

            for key in STEM_ROTATION_KEYS:
                row[f'Rot_{key}'] = rotation.get(key)
            for key in STEM_TRANSLATION_KEYS:
                row[f'Trans_{key}'] = translation.get(key)

            stem_sheet_rows.append(row)
    
    if not detailed_rows:
        print("Warning: No data available for detailed Excel export.")
        return None
    
    # Create DataFrame
    df = pd.DataFrame(detailed_rows)
    
    # Create Excel file with multiple sheets
    excel_filename = f"{output_prefix}_detailed_data.xlsx"
    
    with pd.ExcelWriter(excel_filename, engine=excel_engine) as writer:
        # Main sheet with all detailed data
        df.to_excel(writer, sheet_name='Detailed_Data', index=False)
        
        # Matrices sheet with all matrix components
        matrix_df = df[df['Data_Type'].str.startswith('Matrix_')]
        if not matrix_df.empty:
            # Pivot to create matrix component analysis
            matrix_pivot = matrix_df.pivot_table(
                index=['Case', 'Parameter', 'Anatomical_Side'],
                columns=['Component'],
                values=['H001_Value', 'H002_Value', 'H003_Value'],
                fill_value=None
            )
            matrix_pivot.to_excel(writer, sheet_name='Matrix_Components')
        
        # Vectors sheet with all vector components
        vector_df = df[df['Data_Type'].str.startswith('Vector_')]
        if not vector_df.empty:
            # Pivot to create vector component analysis
            vector_pivot = vector_df.pivot_table(
                index=['Case', 'Parameter', 'Anatomical_Side'],
                columns=['Component'],
                values=['H001_Value', 'H002_Value', 'H003_Value'],
                fill_value=None
            )
            vector_pivot.to_excel(writer, sheet_name='Vector_Components')
        
        # Translation components only (from matrices)
        translation_df = df[df['Component'].isin(['Translation_X', 'Translation_Y', 'Translation_Z'])]
        if not translation_df.empty:
            translation_pivot = translation_df.pivot_table(
                index=['Case', 'Parameter', 'Anatomical_Side'],
                columns=['Component'],
                values=['H001_Value', 'H002_Value', 'H003_Value'],
                fill_value=None
            )
            translation_pivot.to_excel(writer, sheet_name='Translation_Components')
        
        # Scalars sheet
        scalar_df = df[~df['Data_Type'].str.contains('Matrix_|Vector_')]
        if not scalar_df.empty:
            scalar_df.to_excel(writer, sheet_name='Scalar_Values', index=False)
        
        # Summary statistics by component type
        summary_data = []
        for case in df['Case'].unique():
            case_df = df[df['Case'] == case]
            summary_data.append({
                'Case': case,
                'Total_Components': len(case_df),
                'Matrix_Components': len(case_df[case_df['Data_Type'].str.startswith('Matrix_')]),
                'Vector_Components': len(case_df[case_df['Data_Type'].str.startswith('Vector_')]),
                'Scalar_Values': len(case_df[~case_df['Data_Type'].str.contains('Matrix_|Vector_')]),
                'Translation_Components': len(case_df[case_df['Component'].isin(['Translation_X', 'Translation_Y', 'Translation_Z'])]),
                'Rotation_Components': len(case_df[case_df['Component'].str.startswith('M_') & ~case_df['Component'].isin(['Translation_X', 'Translation_Y', 'Translation_Z'])])
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Component_Summary', index=False)

        if stem_sheet_rows:
            stems_df = pd.DataFrame(stem_sheet_rows)
            stems_df.to_excel(writer, sheet_name='Stem_Info', index=False)
    
    print(f"Detailed data (component-wise) exported to Excel: {excel_filename}")
    return excel_filename

if __name__ == "__main__":
    main()