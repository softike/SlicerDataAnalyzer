#!/usr/bin/env python3
"""
Demo batch comparison script - processes just 2 cases for quick demonstration.
"""

import os
import sys
sys.path.append('/home/developer/Projects/Code/SlicerDataAnalyzer')

from batchCompareStudies import *

def main_demo():
    parser = argparse.ArgumentParser(description="Demo batch comparison (2 cases only).")
    parser.add_argument("--base_path", default="/mnt/localstore3",
                       help="Base path containing H001, H002, H003 directories")
    parser.add_argument("--output", "-o", default="demo_batch_report",
                       help="Output filename prefix (without extension)")
    parser.add_argument("--pdf", action="store_true", 
                       help="Also export results to PDF format")
    parser.add_argument("--translation-only", action="store_true", 
                       help="Only display translation (positional) data from matrices")
    parser.add_argument("--side", choices=['Left', 'Right', 'Both', 'Auto'], default='Both',
                       help="Filter data by patient side: Left, Right, Both, or Auto (detect from XML) - default: Both")
    
    args = parser.parse_args()
    
    # Create output directory for individual case plots
    output_dir = f"{args.output}_plots"
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all case sets but limit to first 2 for demo
    print("Scanning for case folders...")
    all_case_sets = find_case_folders(args.base_path)
    case_sets = all_case_sets[:2]  # Only process first 2 cases
    
    if not case_sets:
        print("No case sets found")
        return
    
    print(f"Demo: Processing first 2 of {len(all_case_sets)} available case sets")
    
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
    
    print(f"\nDemo batch processing complete!")
    print(f"Cases processed: {len(case_results)}")
    print(f"Successful: {successful_cases}")
    print(f"Total plots generated: {total_plots}")
    print(f"Report saved as: {html_filename}")

if __name__ == "__main__":
    main_demo()