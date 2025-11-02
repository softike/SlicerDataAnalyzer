#!/usr/bin/env python3
"""
Batch comparison script for medical planning data across multiple testers.
This script automatically finds corresponding case folders across H001, H002, H003 directories
and generates a consolidated HTML report with all case comparisons.

Usage:
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --pdf
    python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report --translation-only
"""

import os
import sys
import argparse
import glob
from pathlib import Path
import xml.etree.ElementTree as ET
from datetime import datetime

# Import the main comparison functions from the existing script
from compareResults_3Studies import (
    comparePlanningData, extractPlanningData_plain, 
    calculate_frontal_plane_angle, generate_comparison_stats,
    create_individual_comparison_plots, export_to_pdf,
    extract_patient_side, validate_patient_sides, filter_tags_by_side,
    TAGS_XPATHS
)

def find_case_folders(base_path):
    """
    Find all corresponding case folders across H001, H002, H003 directories.
    
    Args:
        base_path: Base path containing H001, H002, H003 directories
        
    Returns:
        List of tuples (case_name, h001_path, h002_path, h003_path)
    """
    case_sets = []
    
    # Define tester directories
    tester_dirs = ['H001', 'H002', 'H003']
    
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

def generate_case_comparison_data(xml_path1, xml_path2, xml_path3, case_name, output_dir, translation_only=False, side_filter='Both'):
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
                'side_error': f'Auto mode failed: Inconsistent PatientSide values: {sides_list}'
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
                'side_error': f'Inconsistent PatientSide values: {sides_list}'
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
    plot_files = create_individual_comparison_plots(data1, data2, data3, common_tags, case_output_prefix, translation_only, actual_side_filter)
    
    # Generate statistics
    stats_html = generate_comparison_stats(data1, data2, data3, common_tags)
    
    return {
        'case_name': case_name,
        'status': 'success',
        'common_tags': common_tags,
        'plot_files': plot_files,
        'stats_html': stats_html,
        'xml_paths': [xml_path1, xml_path2, xml_path3]
    }

def generate_consolidated_html_report(case_results, output_prefix, export_pdf=False):
    """
    Generate a consolidated HTML report containing all case comparisons.
    """
    
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
            plots_html += f"""
            <div class="plot-item">
                <h4>{plot_info['title']}</h4>
                <img src="{plot_info['filename']}" alt="{plot_info['title']}" class="individual-plot">
            </div>
            """
        
        cases_html += f"""
        <div class="case-section" id="case-{result['case_name']}">
            <h2>Case: {result['case_name']}</h2>
            
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
    html_filename = f"{output_prefix}.html"
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
                       help="Output filename prefix (without extension)")
    parser.add_argument("--pdf", action="store_true", 
                       help="Also export results to PDF format")
    parser.add_argument("--translation-only", action="store_true", 
                       help="Only display translation (positional) data from matrices")
    parser.add_argument("--side", choices=['Left', 'Right', 'Both', 'Auto'], default='Both',
                       help="Filter data by patient side: Left, Right, Both, or Auto (detect from XML) - default: Both")
    
    args = parser.parse_args()
    
    # Validate base path
    if not os.path.exists(args.base_path):
        print(f"Error: Base path {args.base_path} does not exist")
        sys.exit(1)
    
    # Create output directory for individual case plots
    output_dir = f"{args.output}_plots"
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
                args.translation_only, args.side
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
    html_filename = generate_consolidated_html_report(case_results, args.output, args.pdf)
    
    # Print summary
    successful_cases = len([r for r in case_results if r['status'] == 'success'])
    total_plots = sum(len(r['plot_files']) for r in case_results if r['status'] == 'success')
    
    print(f"\nBatch processing complete!")
    print(f"Cases processed: {len(case_results)}")
    print(f"Successful: {successful_cases}")
    print(f"Total plots generated: {total_plots}")
    print(f"Report saved as: {html_filename}")

if __name__ == "__main__":
    main()