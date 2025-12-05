import os
import xml.etree.ElementTree as ET

import numpy as np
import argparse
from pathlib import Path

dcm_path = r"C:\\Users\\Coder\\Desktop\\001-M-30\\001-M-30\\Dataset"

# Basis vectors for anatomical reference frame
X_UNIT = np.array([1.0, 0.0, 0.0])  # Right ➜ Left
Y_UNIT = np.array([0.0, 1.0, 0.0])  # Front ➜ Back
Z_UNIT = np.cross(X_UNIT, Y_UNIT)
Z_UNIT = Z_UNIT / np.linalg.norm(Z_UNIT)  # Headward direction (X × Y)

# Centralized definition of XML tags and XPath expressions to extract
TAGS_XPATHS = [
    ("S3FemoralSphere_R_matrix", ".//s3Shape[@name='S3FemoralSphere_R']/matrix4[@name='mat']"),
    ("S3FemoralSphere_R_diameter", ".//s3Shape[@name='S3FemoralSphere_R']/scalar[@name='diameter']"),
    ("S3AcetabularHSphere_R_matrix", ".//s3Shape[@name='S3AcetabularHSphere_R']/matrix4[@name='mat']"),
    ("S3AcetabularHSphere_R_diameter", ".//s3Shape[@name='S3AcetabularHSphere_R']/scalar[@name='diameter']"),
    ("S3FemoralSphere_L_matrix", ".//s3Shape[@name='S3FemoralSphere_L']/matrix4[@name='mat']"),
    ("S3FemoralSphere_L_diameter", ".//s3Shape[@name='S3FemoralSphere_L']/scalar[@name='diameter']"),
    ("S3AcetabularHSphere_L_matrix", ".//s3Shape[@name='S3AcetabularHSphere_L']/matrix4[@name='mat']"),
    ("S3AcetabularHSphere_L_diameter", ".//s3Shape[@name='S3AcetabularHSphere_L']/scalar[@name='diameter']"),
    ("S3GreaterTroch_R_matrix", ".//s3Shape[@name='S3GreaterTroch_R']/matrix4[@name='mat']"),
    ("S3GreaterTroch_L_matrix", ".//s3Shape[@name='S3GreaterTroch_L']/matrix4[@name='mat']"),
    ("S3TopLesserTroch_R_matrix", ".//s3Shape[@name='S3TopLesserTroch_R']/matrix4[@name='mat']"),
    ("S3TopLesserTroch_L_matrix", ".//s3Shape[@name='S3TopLesserTroch_L']/matrix4[@name='mat']"),
    ("S3BCP_R_matrix", ".//s3Shape[@name='S3BCP_R']/matrix4[@name='mat']"),
    ("S3BCP_R_p0", ".//s3Shape[@name='S3BCP_R']/vector3[@name='p0']"),
    ("S3BCP_R_p1", ".//s3Shape[@name='S3BCP_R']/vector3[@name='p1']"),
    ("S3BCP_L_matrix", ".//s3Shape[@name='S3BCP_L']/matrix4[@name='mat']"),
    ("S3BCP_L_p0", ".//s3Shape[@name='S3BCP_L']/vector3[@name='p0']"),
    ("S3BCP_L_p1", ".//s3Shape[@name='S3BCP_L']/vector3[@name='p1']"),
    #("S3AppFrame_matrix", ".//s3Shape[@name='S3AppFrame']/matrix4[@name='mat']"),
    ("S3FemurFrame_R_matrix", ".//s3Shape[@name='S3FemurFrame_R']/matrix4[@name='mat']"),
    ("S3FemurFrame_L_matrix", ".//s3Shape[@name='S3FemurFrame_L']/matrix4[@name='mat']"),
]

# Filtered version for extractPlanningData function (only enabled elements)
TAGS_XPATHS_EXTRACT_ONLY = [
    ("S3FemoralSphere_R_matrix", ".//s3Shape[@name='S3FemoralSphere_R']/matrix4[@name='mat']"),
    ("S3FemoralSphere_L_matrix", ".//s3Shape[@name='S3FemoralSphere_L']/matrix4[@name='mat']"),
    ("S3FemoralSphere_R_diameter", ".//s3Shape[@name='S3FemoralSphere_R']/scalar[@name='diameter']"),
    ("S3FemoralSphere_L_diameter", ".//s3Shape[@name='S3FemoralSphere_L']/scalar[@name='diameter']"),
    ("S3GreaterTroch_R_matrix", ".//s3Shape[@name='S3GreaterTroch_R']/matrix4[@name='mat']"),
    ("S3GreaterTroch_L_matrix", ".//s3Shape[@name='S3GreaterTroch_L']/matrix4[@name='mat']"),
    ("S3TopLesserTroch_R_matrix", ".//s3Shape[@name='S3TopLesserTroch_R']/matrix4[@name='mat']"),
    ("S3TopLesserTroch_L_matrix", ".//s3Shape[@name='S3TopLesserTroch_L']/matrix4[@name='mat']"),
    ("S3BCP_R_matrix", ".//s3Shape[@name='S3BCP_R']/matrix4[@name='mat']"),
    ("S3BCP_R_p0", ".//s3Shape[@name='S3BCP_R']/vector3[@name='p0']"),
    ("S3BCP_R_p1", ".//s3Shape[@name='S3BCP_R']/vector3[@name='p1']"),
    ("S3BCP_L_matrix", ".//s3Shape[@name='S3BCP_L']/matrix4[@name='mat']"),
    ("S3BCP_L_p0", ".//s3Shape[@name='S3BCP_L']/vector3[@name='p0']"),
    ("S3BCP_L_p1", ".//s3Shape[@name='S3BCP_L']/vector3[@name='p1']"),
    ("S3FemurFrame_R_matrix", ".//s3Shape[@name='S3FemurFrame_R']/matrix4[@name='mat']"),
    ("S3FemurFrame_L_matrix", ".//s3Shape[@name='S3FemurFrame_L']/matrix4[@name='mat']"),
]

##
def _matrix_from_string(matrix_str):
    values = [float(x) for x in matrix_str.split()]
    if len(values) != 16:
        raise ValueError("Matrix entries must contain 16 floats")
    return np.array(values).reshape((4, 4))


def _vector_from_string(vector_str):
    values = [float(x) for x in vector_str.split()]
    if len(values) != 3:
        raise ValueError("Vector entries must contain 3 floats")
    return np.array(values)


def _project_onto_xy_plane(vector):
    projection = vector - np.dot(vector, Z_UNIT) * Z_UNIT
    norm = np.linalg.norm(projection)
    if norm < 1e-8:
        raise ValueError("Projection onto XY plane is undefined (vector near +Z)")
    return projection / norm


def _vector_angle_deg(vector, side, test_angle_sign=False):
    # Calculate angle using dot product with X_UNIT (pointing Right/+X)
    # First normalize the vector
    norm = np.linalg.norm(vector)
    if norm < 1e-8:
        raise ValueError("Vector magnitude too small for angle calculation")
    unit_vec = vector / norm
    
    # Get angle from X_UNIT using arccos of dot product
    cos_angle = np.dot(unit_vec, X_UNIT)
    if side == 'Left':
        cos_angle = np.dot(unit_vec, -X_UNIT) 
    # Clamp to [-1, 1] to avoid numerical errors with arccos
    cos_angle = np.clip(cos_angle, -1.0, 1.0)
    angle = np.degrees(np.arccos(cos_angle))

    if test_angle_sign:
        test_angle = np.dot(unit_vec, Y_UNIT)
        if test_angle > 0:
            angle = -angle

    return angle


def _femoral_neck_angle(femur_frame_matrix_str, femoral_sphere_matrix_str, side):
    frame_mat = _matrix_from_string(femur_frame_matrix_str)
    sphere_mat = _matrix_from_string(femoral_sphere_matrix_str)
    frame_origin = frame_mat[3, :3]
    sphere_center = sphere_mat[3, :3]
    direction = sphere_center - frame_origin
    neck_proj = _project_onto_xy_plane(direction)
    angle = _vector_angle_deg(neck_proj, side, True)



    return angle


def _bcp_direction_angle(bcp_matrix_str, p0_str, p1_str, side):
    mat = _matrix_from_string(bcp_matrix_str)
    rot = mat[:3, :3]
    translation = mat[3, :3]

    if not (p0_str and p1_str):
        axis = mat[:3, 0]
        direction = axis if side == 'Left' else -axis
    else:
        p0 = _vector_from_string(p0_str)
        p1 = _vector_from_string(p1_str)
        p0_xy = p0.copy()
        p1_xy = p1.copy()
        p0_xy[2] = 0.0
        p1_xy[2] = 0.0
        rot_T = rot.T
        tp0 = rot_T @ p0_xy + translation
        tp1 = rot_T @ p1_xy + translation
        direction = tp0 - tp1 if side == 'Left' else tp1 - tp0

    bcp_proj = _project_onto_xy_plane(direction)
    angle = _vector_angle_deg(bcp_proj, side, True)

    return angle


def calculate_femoral_anteversion(
    femur_matrix_str,
    bcp_matrix_str,
    *,
    femoral_sphere_matrix_str,
    bcp_p0_str,
    bcp_p1_str,
    side='Right',
    return_components=False,
):
    """Compute anteversion using femoral neck-to-sphere and BCP projected vectors."""

    neck_angle = _femoral_neck_angle(femur_matrix_str, femoral_sphere_matrix_str, side)
    #print ("TEST : " + neck_angle.__str__())
    bcp_angle = _bcp_direction_angle(bcp_matrix_str, bcp_p0_str, bcp_p1_str, side)
    #print ("TEST : " + bcp_angle.__str__()) 
    anteversion = neck_angle - bcp_angle
    #print ("ANTEVERSION: " + anteversion.__str__())
    if return_components:
        return anteversion, neck_angle, bcp_angle
    return anteversion


def calculate_femoral_anteversion_from_dict(data, side):
    """Convenience helper for callers that operate on planning data dictionaries."""
    suffix = 'R' if side == 'Right' else 'L'
    femur_key = f'S3FemurFrame_{suffix}_matrix'
    sphere_key = f'S3FemoralSphere_{suffix}_matrix'
    bcp_key = f'S3BCP_{suffix}_matrix'
    p0_key = f'S3BCP_{suffix}_p0'
    p1_key = f'S3BCP_{suffix}_p1'

    required = [femur_key, sphere_key, bcp_key, p0_key, p1_key]
    missing = [key for key in required if not data.get(key)]
    if missing:
        raise ValueError(f"Missing anteversion inputs: {', '.join(missing)}")

    return calculate_femoral_anteversion(
        data[femur_key],
        data[bcp_key],
        femoral_sphere_matrix_str=data[sphere_key],
        bcp_p0_str=data[p0_key],
        bcp_p1_str=data[p1_key],
        side=side,
    )

##
def extract_patient_side(xml_path):
    """
    Extract PatientSide information from XML file.
    
    Args:
        xml_path: Path to the XML file
        
    Returns:
        String: 'Left', 'Right', or None if not found
    """
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Look for PatientSide tag - it might be in different locations
        side_elem = root.find(".//PatientSide")
        if side_elem is not None and side_elem.text:
            side = side_elem.text.strip()
            # Normalize the side value
            if side.lower() in ['left', 'l']:
                return 'Left'
            elif side.lower() in ['right', 'r']:
                return 'Right'
        
        # Alternative search patterns if the first doesn't work
        for elem in root.iter():
            if 'patientside' in elem.tag.lower() and elem.text:
                side = elem.text.strip()
                if side.lower() in ['left', 'l']:
                    return 'Left'
                elif side.lower() in ['right', 'r']:
                    return 'Right'
                    
        return None
    except Exception as e:
        print(f"Warning: Could not extract PatientSide from {xml_path}: {e}")
        return None

##
def validate_patient_sides(xml_paths, case_name=None):
    """
    Validate that all XML files have the same PatientSide.
    
    Args:
        xml_paths: List of XML file paths
        case_name: Optional case name for error reporting
        
    Returns:
        Tuple: (is_consistent, patient_side, sides_list)
    """
    sides = []
    for xml_path in xml_paths:
        side = extract_patient_side(xml_path)
        sides.append(side)
    
    # Check consistency
    non_none_sides = [s for s in sides if s is not None]
    if not non_none_sides:
        return False, None, sides
    
    first_side = non_none_sides[0]
    is_consistent = all(s == first_side for s in non_none_sides)
    
    if not is_consistent and case_name:
        print(f"Warning: Inconsistent PatientSide values for case {case_name}: {sides}")
    
    return is_consistent, first_side if is_consistent else None, sides

##
def filter_tags_by_side(tags, target_side):
    """
    Filter a list of tags based on the target side (Left/Right).
    Tags ending with '_L' are Left side, tags ending with '_R' are Right side.
    
    Args:
        tags: List of tag names
        target_side: 'Left', 'Right', or 'Both'
        
    Returns:
        List of filtered tags
    """
    if target_side == 'Both' or target_side is None:
        return tags
    
    filtered_tags = []
    for tag in tags:
        if target_side == 'Left' and (tag.endswith('_L') or '_L_' in tag):
            filtered_tags.append(tag)
        elif target_side == 'Right' and (tag.endswith('_R') or '_R_' in tag):
            filtered_tags.append(tag)
        elif not (tag.endswith('_L') or tag.endswith('_R') or '_L_' in tag or '_R_' in tag):
            # Include tags that don't have side indicators (like diameter measurements without L/R)
            filtered_tags.append(tag)
    
    return filtered_tags

##
def export_to_pdf(html_content, plot_files, output_prefix, title="Planning Data Report"):
    """
    Export HTML content and plots to PDF using weasyprint or pdfkit.
    plot_files can be a single filename string or a list of plot info dictionaries.
    Falls back to matplotlib PDF if web-based libraries are not available.
    """
    pdf_filename = f"{output_prefix}.pdf"
    
    # Try different PDF generation methods
    success = False
    
    # Method 1: Try weasyprint (recommended for HTML to PDF)
    try:
        from weasyprint import HTML, CSS
        import base64
        import re

        # Build a PDF-specific HTML that places 2 plots per page and summary on separate page
        pdf_css = """
        @page { size: A4; margin: 0.75in; }
        body { font-family: Arial, sans-serif; color: #333; }
        .pdf-page { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 0.5in; page-break-after: always; }
        .pdf-plot { width: 49%; }
        .pdf-plot img { width: 100%; height: auto; display: block; }
        .summary-page { page-break-before: always; }
        .summary-card { background: #f8f9fa; padding: 12px; border-radius: 6px; border:1px solid #ddd; }
        """

        # Try extracting any existing stats/summary section from html_content
        summary_html = None
        m = re.search(r'<div class="stats-section">(.*?)</div>', html_content, re.S)
        if not m:
            m = re.search(r'<div class="data-summary">(.*?)</div>', html_content, re.S)
        if m:
            summary_html = m.group(1)

        # Construct body with 2 plots per page
        body_parts = []
        if isinstance(plot_files, str):
            plot_list = [{'filename': plot_files, 'title': ''}]
        else:
            plot_list = plot_files

        # embed images as base64
        def img_tag_from_file(path, alt="plot"):
            if not os.path.exists(path):
                return f'<div class="pdf-plot"><p>Missing file: {path}</p></div>'
            with open(path, 'rb') as f:
                data = base64.b64encode(f.read()).decode()
            return f'<div class="pdf-plot"><img src="data:image/png;base64,{data}" alt="{alt}"></div>'

        for i in range(0, len(plot_list), 2):
            left = plot_list[i]
            right = plot_list[i+1] if i+1 < len(plot_list) else None
            left_tag = img_tag_from_file(left['filename'], left.get('title',''))
            right_tag = img_tag_from_file(right['filename'], right.get('title','')) if right else ''
            page_html = f'<div class="pdf-page">{left_tag}{right_tag}</div>'
            body_parts.append(page_html)

        # summary page
        if summary_html:
            summary_block = f'<div class="summary-page"><div class="summary-card">{summary_html}</div></div>'
        else:
            # fallback: simple filenames list
            items = ''.join([f'<li>{p["filename"]}</li>' for p in plot_list])
            summary_block = f'<div class="summary-page"><div class="summary-card"><h2>Generated Plots</h2><ul>{items}</ul></div></div>'

        html_for_pdf = f'<!doctype html><html><head><meta charset="utf-8"><style>{pdf_css}</style></head><body>' + '\n'.join(body_parts) + summary_block + '</body></html>'

        HTML(string=html_for_pdf).write_pdf(pdf_filename)
        print(f"PDF exported using weasyprint: {pdf_filename}")
        success = True

    except ImportError:
        print("weasyprint not available, trying pdfkit...")
    except Exception as e:
        print(f"weasyprint failed: {e}, trying pdfkit...")
    
    # Method 2: Try pdfkit (requires wkhtmltopdf)
    if not success:
        try:
            import pdfkit

            # Build similar PDF-specific HTML as for weasyprint but using file:// paths
            pdf_css = """
            @page { size: A4; margin: 0.75in; }
            body { font-family: Arial, sans-serif; color: #333; }
            .pdf-page { display: flex; justify-content: space-between; gap: 10px; margin-bottom: 0.5in; page-break-after: always; }
            .pdf-plot { width: 49%; }
            .pdf-plot img { width: 100%; height: auto; display: block; }
            .summary-page { page-break-before: always; }
            .summary-card { background: #f8f9fa; padding: 12px; border-radius: 6px; border:1px solid #ddd; }
            """

            if isinstance(plot_files, str):
                plot_list = [{'filename': plot_files, 'title': ''}]
            else:
                plot_list = plot_files

            body_parts = []
            for i in range(0, len(plot_list), 2):
                left = plot_list[i]
                right = plot_list[i+1] if i+1 < len(plot_list) else None
                left_path = os.path.abspath(left['filename'])
                left_tag = f'<div class="pdf-plot"><img src="file://{left_path}" alt="{left.get("title","")}"></div>'
                right_tag = ''
                if right:
                    right_path = os.path.abspath(right['filename'])
                    right_tag = f'<div class="pdf-plot"><img src="file://{right_path}" alt="{right.get("title","")}"></div>'
                page_html = f'<div class="pdf-page">{left_tag}{right_tag}</div>'
                body_parts.append(page_html)

            # try extracting summary from html_content
            import re
            summary_html = None
            m = re.search(r'<div class="stats-section">(.*?)</div>', html_content, re.S)
            if not m:
                m = re.search(r'<div class="data-summary">(.*?)</div>', html_content, re.S)
            if m:
                summary_html = m.group(1)

            if summary_html:
                summary_block = f'<div class="summary-page"><div class="summary-card">{summary_html}</div></div>'
            else:
                items = ''.join([f'<li>{p["filename"]}</li>' for p in plot_list])
                summary_block = f'<div class="summary-page"><div class="summary-card"><h2>Generated Plots</h2><ul>{items}</ul></div></div>'

            html_for_pdf = f'<!doctype html><html><head><meta charset="utf-8"><style>{pdf_css}</style></head><body>' + '\n'.join(body_parts) + summary_block + '</body></html>'

            temp_html = f"{output_prefix}_temp.html"
            with open(temp_html, 'w') as f:
                f.write(html_for_pdf)

            options = {
                'page-size': 'A4',
                'margin-top': '0.75in',
                'margin-right': '0.75in',
                'margin-bottom': '0.75in',
                'margin-left': '0.75in',
                'encoding': "UTF-8",
                'no-outline': None,
                'enable-local-file-access': None
            }

            pdfkit.from_file(temp_html, pdf_filename, options=options)

            # Clean up temporary file
            os.remove(temp_html)

            print(f"PDF exported using pdfkit: {pdf_filename}")
            success = True

        except ImportError:
            print("pdfkit not available, trying matplotlib PDF...")
        except Exception as e:
            print(f"pdfkit failed: {e}, trying matplotlib PDF...")
    
    # Method 3: Fallback to matplotlib PDF (plot only, no HTML)
    if not success:
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_pdf import PdfPages
            from datetime import datetime
            
            with PdfPages(pdf_filename) as pdf:
                # Add title page
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.text(0.5, 0.8, title, fontsize=20, ha='center', va='center', weight='bold')
                ax.text(0.5, 0.7, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                       fontsize=12, ha='center', va='center')
                ax.text(0.5, 0.3, "Note: This PDF contains plots only.\nFor full report with statistics,\ninstall 'weasyprint' or 'pdfkit'.", 
                       fontsize=10, ha='center', va='center', style='italic')
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)
                
                # Add individual plots two per page
                if isinstance(plot_files, str):
                    plot_list = [{'filename': plot_files, 'title': ''}]
                else:
                    plot_list = plot_files

                # pages with 2 plots each
                for i in range(0, len(plot_list), 2):
                    left = plot_list[i]
                    right = plot_list[i+1] if i+1 < len(plot_list) else None
                    fig, axes = plt.subplots(1, 2, figsize=(11, 8.5))
                    # left
                    left_ax = axes[0]
                    if os.path.exists(left['filename']):
                        img = plt.imread(left['filename'])
                        left_ax.imshow(img)
                        left_ax.set_title(left.get('title',''))
                    else:
                        left_ax.text(0.5, 0.5, f"Missing: {left['filename']}", ha='center')
                    left_ax.axis('off')

                    # right
                    if right:
                        right_ax = axes[1]
                        if os.path.exists(right['filename']):
                            img = plt.imread(right['filename'])
                            right_ax.imshow(img)
                            right_ax.set_title(right.get('title',''))
                        else:
                            right_ax.text(0.5, 0.5, f"Missing: {right['filename']}", ha='center')
                        right_ax.axis('off')
                    else:
                        # hide second axis
                        axes[1].axis('off')

                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)

                # Add a summary page (text extracted from HTML if possible)
                import re
                summary_html = None
                m = re.search(r'<div class="stats-section">(.*?)</div>', html_content, re.S)
                if not m:
                    m = re.search(r'<div class="data-summary">(.*?)</div>', html_content, re.S)
                if m:
                    summary_html = m.group(1)

                # convert HTML to plain text for matplotlib rendering
                def html_to_text(h):
                    # naive tag stripper
                    import re
                    text = re.sub(r'<script.*?>.*?</script>', '', h, flags=re.S)
                    text = re.sub(r'<[^>]+>', '', text)
                    # normalize whitespace
                    text = re.sub(r'\s+', ' ', text).strip()
                    return text

                if summary_html:
                    text = html_to_text(summary_html)
                    fig, ax = plt.subplots(figsize=(8.5, 11))
                    ax.text(0.01, 0.99, text, va='top', ha='left', wrap=True, fontsize=9)
                    ax.axis('off')
                    pdf.savefig(fig, bbox_inches='tight')
                    plt.close(fig)
            
            print(f"PDF exported using matplotlib (plots only): {pdf_filename}")
            print("For full HTML content in PDF, install: pip install weasyprint")
            success = True
            
        except Exception as e:
            print(f"matplotlib PDF export failed: {e}")
    
    if not success:
        print("PDF export failed. Please install weasyprint or pdfkit:")
        print("  pip install weasyprint")
        print("  # or")
        print("  pip install pdfkit")
        print("  # Note: pdfkit also requires wkhtmltopdf system package")
        
    return success, pdf_filename if success else None

def is_landmark_matrix(tag):
    """
    Check if a matrix tag corresponds to an anatomical landmark that should skip rotation analysis.
    
    Args:
        tag: Matrix tag name (e.g., 'S3GreaterTroch_R_matrix')
        
    Returns:
        bool: True if this is a landmark matrix that should skip rotation analysis
    """
    landmark_patterns = [
        'S3GreaterTroch_',
        'S3TopLesserTroch_', 
        'S3FemoralSphere_'
    ]
    return any(pattern in tag for pattern in landmark_patterns)

##
def create_individual_plots(matrix_data, vector_data, scalar_data, output_prefix, translation_only=False, side_filter='Both', no_landmark_rotation=False):
    """
    Create individual plots for each measure and save them as separate image files.
    Returns a list of dictionaries containing plot information.
    
    Args:
        translation_only: If True, only create translation plots from matrices (skip rotation, vectors, scalars)
        side_filter: 'Left', 'Right', or 'Both' - filter data by patient side
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
    # Apply side filtering to the data
    if side_filter != 'Both':
        matrix_tags = [tag for tag, _ in matrix_data]
        vector_tags = [tag for tag, _ in vector_data]
        scalar_tags = [tag for tag, _ in scalar_data]
        
        matrix_tags_filtered = filter_tags_by_side(matrix_tags, side_filter)
        vector_tags_filtered = filter_tags_by_side(vector_tags, side_filter)
        scalar_tags_filtered = filter_tags_by_side(scalar_tags, side_filter)
        
        matrix_data = [(tag, value) for tag, value in matrix_data if tag in matrix_tags_filtered]
        vector_data = [(tag, value) for tag, value in vector_data if tag in vector_tags_filtered]
        scalar_data = [(tag, value) for tag, value in scalar_data if tag in scalar_tags_filtered]
    
    plot_files = []
    
    # Create plots for matrices (rotation and translation parts separately)
    for tag, value in matrix_data:
        # Parse the 4x4 matrix
        mat = np.array([float(x) for x in value.split()]).reshape((4, 4))
        
        # Extract rotation (3x3) and translation (3x1) parts
        rotation_part = mat[:3, :3]
        translation_part = mat[3, :3]
        
        # Only create rotation plots if not translation_only mode and not excluded landmark
        if not translation_only and not (no_landmark_rotation and is_landmark_matrix(tag)):
            # Plot rotation part as heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(rotation_part, cmap='viridis', interpolation='nearest')
            ax.set_title(f"{tag} (Rotation 3x3)", fontsize=14, pad=20)
            ax.set_xlabel("Column")
            ax.set_ylabel("Row")
            plt.colorbar(im, ax=ax)
            
            # Add value annotations
            for i in range(3):
                for j in range(3):
                    ax.text(j, i, f'{rotation_part[i, j]:.3f}', 
                           ha='center', va='center', color='white' if rotation_part[i, j] < rotation_part.mean() else 'black')
            
            rotation_filename = f"{output_prefix}_{tag}_rotation.png"
            plt.savefig(rotation_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': rotation_filename,
                'title': f"{tag} (Rotation)",
                'type': 'matrix_rotation',
                'tag': tag
            })
        
        # Plot translation part as bar chart (always included, this is the positional data)
        fig, ax = plt.subplots(figsize=(8, 6))
        bars = ax.bar(['X', 'Y', 'Z'], translation_part, color=['#ff7f7f', '#7fff7f', '#7f7fff'], alpha=0.8)
        ax.set_title(f"{tag} (Translation)", fontsize=14, pad=20)
        ax.set_ylabel("Value")
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars, translation_part):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + abs(max(translation_part))*0.01,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=10)
        
        translation_filename = f"{output_prefix}_{tag}_translation.png"
        plt.savefig(translation_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append({
            'filename': translation_filename,
            'title': f"{tag} (Translation)",
            'type': 'matrix_translation',
            'tag': tag
        })

    # Skip vectors and scalars in translation_only mode (only matrix translations are positional)
    if not translation_only:
        # Create plots for vectors
        for tag, value in vector_data:
            vec = np.array([float(x) for x in value.split()])
            
            fig, ax = plt.subplots(figsize=(8, 6))
            bars = ax.bar(range(len(vec)), vec, color='skyblue', alpha=0.8)
            ax.set_title(f"{tag} (Vector)", fontsize=14, pad=20)
            ax.set_xlabel("Component Index")
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for i, (bar, val) in enumerate(zip(bars, vec)):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + abs(max(vec))*0.01,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=10)
            
            vector_filename = f"{output_prefix}_{tag}_vector.png"
            plt.savefig(vector_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': vector_filename,
                'title': f"{tag} (Vector)",
                'type': 'vector',
                'tag': tag
            })

        # Create plots for scalars
        for tag, value in scalar_data:
            val = float(value)
            
            fig, ax = plt.subplots(figsize=(6, 6))
            bar = ax.bar([tag.split('_')[-2]], [val], color='lightcoral', alpha=0.8, width=0.5)
            ax.set_title(f"{tag} (Scalar)", fontsize=14, pad=20)
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
        
        # Add value label on bar
        ax.text(bar[0].get_x() + bar[0].get_width()/2, bar[0].get_height() + abs(val)*0.01,
               f'{val:.3f}', ha='center', va='bottom', fontsize=12, weight='bold')
        
        # Remove x-tick labels for cleaner look
        ax.set_xticklabels([])
        
        scalar_filename = f"{output_prefix}_{tag}_scalar.png"
        plt.savefig(scalar_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append({
            'filename': scalar_filename,
            'title': f"{tag} (Scalar)",
            'type': 'scalar',
            'tag': tag
        })
    
    # Calculate and plot femoral anteversion based on femoral neck vs BCP projection
    matrix_dict = {tag: value for tag, value in matrix_data}
    vector_dict = {tag: value for tag, value in vector_data}
    planning_values = {**matrix_dict, **vector_dict}
    
    side_labels = [('Right', 'R'), ('Left', 'L')]
    for side, suffix in side_labels:
        title = f"{side} Femoral Anteversion Angle"
        femur_key = f'S3FemurFrame_{suffix}_matrix'
        sphere_key = f'S3FemoralSphere_{suffix}_matrix'
        bcp_key = f'S3BCP_{suffix}_matrix'
        p0_key = f'S3BCP_{suffix}_p0'
        p1_key = f'S3BCP_{suffix}_p1'
        requirements = [femur_key, sphere_key, bcp_key, p0_key, p1_key]
        if all(planning_values.get(key) for key in requirements):
            try:
                angle = calculate_femoral_anteversion(
                    planning_values[femur_key],
                    planning_values[bcp_key],
                    femoral_sphere_matrix_str=planning_values[sphere_key],
                    bcp_p0_str=planning_values[p0_key],
                    bcp_p1_str=planning_values[p1_key],
                    side=side,
                )
            except ValueError:
                continue
            
            label = f'{femur_key}\nvs\n{bcp_key}'

            # Create angle visualization plot
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Create a simple bar chart showing the angle
            bar = ax.bar([label], [angle], color='orange', alpha=0.8, width=0.6)
            ax.set_title(f"{title}", fontsize=14, pad=20)
            ax.set_ylabel("Angle (degrees)")
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, max(90, angle * 1.2))
            
            # Add value label on bar
            ax.text(bar[0].get_x() + bar[0].get_width()/2, bar[0].get_height() + angle*0.02,
                   f'{angle:.2f}°', ha='center', va='bottom', fontsize=14, weight='bold')
            
            # Add interpretation text
            if angle < 10:
                interpretation = "Very Small Angle"
                color = 'green'
            elif angle < 30:
                interpretation = "Small Angle"
                color = 'yellow'
            elif angle < 60:
                interpretation = "Moderate Angle"
                color = 'orange'
            else:
                interpretation = "Large Angle"
                color = 'red'
                
            ax.text(0.02, 0.98, f'Interpretation: {interpretation}', 
                   transform=ax.transAxes, va='top', ha='left',
                   bbox=dict(boxstyle='round', facecolor=color, alpha=0.7))
            
            # Remove x-tick labels for cleaner look
            ax.set_xticklabels([])
            
            angle_filename = f"{output_prefix}_{femur_key}_{bcp_key}_angle.png"
            plt.savefig(angle_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': angle_filename,
                'title': title,
                'type': 'femoral_anteversion',
                'tag': f"{femur_key}_{bcp_key}",
                'angle': angle
            })
    
    return plot_files

##
def create_individual_comparison_plots(data1, data2, data3, common_tags, output_prefix, translation_only=False, side_filter='Both', no_landmark_rotation=False):
    """
    Create individual comparison plots for each measure from three datasets.
    Returns a list of dictionaries containing plot information.
    
    Args:
        translation_only: If True, only create translation comparison plots from matrices
        side_filter: 'Left', 'Right', or 'Both' - filter data by patient side
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
    # Apply side filtering to common_tags
    if side_filter != 'Both':
        common_tags = filter_tags_by_side(common_tags, side_filter)
    
    plot_files = []
    
    # Separate tags by type
    matrix_tags = [tag for tag in common_tags if tag.endswith("_matrix")]
    vector_tags = [tag for tag in common_tags if tag.endswith("_p0") or tag.endswith("_p1")]
    scalar_tags = [tag for tag in common_tags if tag.endswith("_diameter")]
    
    # Compare matrices (rotation and translation parts separately)
    for tag in matrix_tags:
        # Parse matrices from all three files
        mat1 = np.array([float(x) for x in data1[tag].split()]).reshape((4, 4))
        mat2 = np.array([float(x) for x in data2[tag].split()]).reshape((4, 4))
        mat3 = np.array([float(x) for x in data3[tag].split()]).reshape((4, 4))
        
        # Only create rotation plots if not translation_only mode and not excluded landmark
        if not translation_only and not (no_landmark_rotation and is_landmark_matrix(tag)):
            # Extract rotation parts (3x3)
            rot1, rot2, rot3 = mat1[:3, :3], mat2[:3, :3], mat3[:3, :3]
            
            # Calculate rotation deviations
            rot_dev12 = np.abs(rot1 - rot2)
            rot_dev13 = np.abs(rot1 - rot3)
            rot_dev23 = np.abs(rot2 - rot3)
            max_rot_dev = np.maximum(np.maximum(rot_dev12, rot_dev13), rot_dev23)
            
            # Plot rotation deviation heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(max_rot_dev, cmap='Reds', interpolation='nearest')
            ax.set_title(f"{tag} (Rotation Deviation)", fontsize=14, pad=20)
            ax.set_xlabel("Column")
            ax.set_ylabel("Row")
            plt.colorbar(im, ax=ax, label='Max Deviation')
            
            # Add value annotations
            for i in range(3):
                for j in range(3):
                    ax.text(j, i, f'{max_rot_dev[i, j]:.4f}', 
                           ha='center', va='center', color='white' if max_rot_dev[i, j] > max_rot_dev.mean() else 'black')
            
            rotation_dev_filename = f"{output_prefix}_{tag}_rotation_deviation.png"
            plt.savefig(rotation_dev_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': rotation_dev_filename,
                'title': f"{tag} (Rotation Deviation)",
                'type': 'matrix_rotation_comparison',
                'tag': tag
            })
        
        # Extract translation parts (always included in comparison)
        trans1, trans2, trans3 = mat1[3, :3], mat2[3, :3], mat3[3, :3]
        
        # Plot translation comparison
        fig, ax = plt.subplots(figsize=(10, 6))
        
        x_pos = np.arange(3)
        width = 0.25
        
        bars1 = ax.bar(x_pos - width, trans1, width, label='File 1', alpha=0.8, color='#ff7f7f')
        bars2 = ax.bar(x_pos, trans2, width, label='File 2', alpha=0.8, color='#7fff7f')
        bars3 = ax.bar(x_pos + width, trans3, width, label='File 3', alpha=0.8, color='#7f7fff')
        
        ax.set_title(f"{tag} (Translation Comparison)", fontsize=14, pad=20)
        ax.set_ylabel("Value")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(['X', 'Y', 'Z'])
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Add value labels
        for bars, values in zip([bars1, bars2, bars3], [trans1, trans2, trans3]):
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + abs(max(trans1.max(), trans2.max(), trans3.max()))*0.01,
                       f'{val:.3f}', ha='center', va='bottom', fontsize=8)
        
        translation_comp_filename = f"{output_prefix}_{tag}_translation_comparison.png"
        plt.savefig(translation_comp_filename, dpi=300, bbox_inches='tight')
        plt.close()
        
        plot_files.append({
            'filename': translation_comp_filename,
            'title': f"{tag} (Translation Comparison)",
            'type': 'matrix_translation_comparison',
            'tag': tag
        })
    
    # Skip vectors and scalars in translation_only mode (only matrix translations are positional)
    if not translation_only:
        # Compare vectors
        for tag in vector_tags:
            vec1 = np.array([float(x) for x in data1[tag].split()])
            vec2 = np.array([float(x) for x in data2[tag].split()])
            vec3 = np.array([float(x) for x in data3[tag].split()])
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            x_pos = np.arange(len(vec1))
            width = 0.25
            
            bars1 = ax.bar(x_pos - width, vec1, width, label='File 1', alpha=0.8, color='#ff9999')
            bars2 = ax.bar(x_pos, vec2, width, label='File 2', alpha=0.8, color='#99ff99')
            bars3 = ax.bar(x_pos + width, vec3, width, label='File 3', alpha=0.8, color='#9999ff')
            
            ax.set_title(f"{tag} (Vector Comparison)", fontsize=14, pad=20)
            ax.set_xlabel("Component")
            ax.set_ylabel("Value")
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            # Add value labels
            for bars, values in zip([bars1, bars2, bars3], [vec1, vec2, vec3]):
                for bar, val in zip(bars, values):
                    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + abs(max(vec1.max(), vec2.max(), vec3.max()))*0.01,
                           f'{val:.3f}', ha='center', va='bottom', fontsize=8)
            
            vector_comp_filename = f"{output_prefix}_{tag}_vector_comparison.png"
            plt.savefig(vector_comp_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': vector_comp_filename,
                'title': f"{tag} (Vector Comparison)",
                'type': 'vector_comparison',
                'tag': tag
            })
        
        # Compare scalars
        for tag in scalar_tags:
            val1 = float(data1[tag])
            val2 = float(data2[tag])
            val3 = float(data3[tag])
            
            fig, ax = plt.subplots(figsize=(8, 6))
            
            values = [val1, val2, val3]
            labels = ['File 1', 'File 2', 'File 3']
            colors = ['#ffcccc', '#ccffcc', '#ccccff']
            
            bars = ax.bar(labels, values, color=colors, alpha=0.8)
            ax.set_title(f"{tag} (Scalar Comparison)", fontsize=14, pad=20)
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
            
            # Add value labels on bars
            for bar, val in zip(bars, values):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                       f'{val:.4f}', ha='center', va='bottom', fontsize=10, weight='bold')
            
            # Add deviation information
            max_dev = max(abs(val1-val2), abs(val1-val3), abs(val2-val3))
            ax.text(0.02, 0.98, f'Max Deviation: {max_dev:.4f}', 
                   transform=ax.transAxes, va='top', ha='left',
                   bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
            
            scalar_comp_filename = f"{output_prefix}_{tag}_scalar_comparison.png"
            plt.savefig(scalar_comp_filename, dpi=300, bbox_inches='tight')
            plt.close()
            
            plot_files.append({
                'filename': scalar_comp_filename,
                'title': f"{tag} (Scalar Comparison)",
                'type': 'scalar_comparison',
                'tag': tag
            })
    
    # Calculate and compare femoral anteversion angles across the three planners
    for side, suffix in [('Right', 'R'), ('Left', 'L')]:
        femur_key = f'S3FemurFrame_{suffix}_matrix'
        sphere_key = f'S3FemoralSphere_{suffix}_matrix'
        bcp_key = f'S3BCP_{suffix}_matrix'
        p0_key = f'S3BCP_{suffix}_p0'
        p1_key = f'S3BCP_{suffix}_p1'
        requirements = [femur_key, sphere_key, bcp_key, p0_key, p1_key]

        if not all(key in common_tags for key in requirements):
            continue

        try:
            angle1 = calculate_femoral_anteversion(
                data1[femur_key],
                data1[bcp_key],
                femoral_sphere_matrix_str=data1[sphere_key],
                bcp_p0_str=data1[p0_key],
                bcp_p1_str=data1[p1_key],
                side=side,
            )
            angle2 = calculate_femoral_anteversion(
                data2[femur_key],
                data2[bcp_key],
                femoral_sphere_matrix_str=data2[sphere_key],
                bcp_p0_str=data2[p0_key],
                bcp_p1_str=data2[p1_key],
                side=side,
            )
            angle3 = calculate_femoral_anteversion(
                data3[femur_key],
                data3[bcp_key],
                femoral_sphere_matrix_str=data3[sphere_key],
                bcp_p0_str=data3[p0_key],
                bcp_p1_str=data3[p1_key],
                side=side,
            )
        except (KeyError, ValueError):
            continue

        title = f"{side} Femoral Anteversion Angle"
        angles = [angle1, angle2, angle3]
        labels = ['File 1', 'File 2', 'File 3']
        colors = ['#ffcccc', '#ccffcc', '#ccccff']

        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(labels, angles, color=colors, alpha=0.8)
        ax.set_title(f"{title} Comparison", fontsize=14, pad=20)
        ax.set_ylabel("Angle (degrees)")
        ax.grid(True, alpha=0.3)

        for bar, angle in zip(bars, angles):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(angles)*0.01,
                   f'{angle:.2f}°', ha='center', va='bottom', fontsize=10, weight='bold')

        max_dev = max(abs(angle1-angle2), abs(angle1-angle3), abs(angle2-angle3))
        mean_angle = np.mean(angles)
        ax.text(0.02, 0.98, f'Max Deviation: {max_dev:.2f}°\nMean Angle: {mean_angle:.2f}°',
               transform=ax.transAxes, va='top', ha='left',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))

        angle_comp_filename = f"{output_prefix}_{femur_key}_{bcp_key}_angle_comparison.png"
        plt.savefig(angle_comp_filename, dpi=300, bbox_inches='tight')
        plt.close()

        plot_files.append({
            'filename': angle_comp_filename,
            'title': f"{title} Comparison",
            'type': 'femoral_anteversion_comparison',
            'tag': f"{femur_key}_{bcp_key}",
            'angles': angles,
            'deviation': max_dev
        })
    
    return plot_files

##
def loadDICOMToDatabase(dcm_path):
    """
    Load DICOM files from a specified path into the Slicer DICOM database.
    """
    # instantiate a new DICOM browser
    slicer.util.selectModule("DICOM")
    dicomBrowser = slicer.modules.DICOMWidget.browserWidget.dicomBrowser
    # use dicomBrowser.ImportDirectoryCopy to make a copy of the files (useful for importing data from removable storage)
    dicomBrowser.importDirectory(dcm_path, dicomBrowser.ImportDirectoryAddLink)
    # wait for import to finish before proceeding (optional, if removed then import runs in the background)
    dicomBrowser.waitForImportFinished()

    dicomDatabase = slicer.dicomDatabase
    patientUIDs = dicomDatabase.patients()

    for patientUID in patientUIDs:
        studies = dicomDatabase.studiesForPatient(patientUID)
        for studyUID in studies:
            seriesUIDs = dicomDatabase.seriesForStudy(studyUID)
            for seriesUID in seriesUIDs:
                print("Found series:", seriesUID)

##
def extractPlanningData(xml_path, output_prefix="planning_data", export_pdf=False, translation_only=False, side_filter='Both', no_landmark_rotation=False):
    """
    Read the planning configuration from a file.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Extract and validate patient side if filtering is requested
    actual_side_filter = side_filter
    if side_filter == 'Auto':
        patient_side = extract_patient_side(xml_path)
        if patient_side is None:
            print(f"Warning: Could not determine PatientSide from {xml_path}. Using 'Both' mode.")
            actual_side_filter = 'Both'
        else:
            actual_side_filter = patient_side
            print(f"Info: Auto-detected PatientSide '{patient_side}' from {xml_path}. Filtering data accordingly.")
    elif side_filter != 'Both':
        patient_side = extract_patient_side(xml_path)
        if patient_side is None:
            print(f"Warning: Could not determine PatientSide from {xml_path}. Proceeding with all data.")
        elif patient_side != side_filter:
            print(f"Info: File {xml_path} has PatientSide '{patient_side}', but filtering for '{side_filter}'. Data will be filtered accordingly.")

    # Create a dictionary to store tag-value pairs
    planning_data = {}

    # Helper function to extract value from an element
    def get_elem_value(elem):
        if elem is not None and 'value' in elem.attrib:
            return elem.attrib['value']
        return None

    # Use centralized definition of tags and XPaths (filtered for extract function)
    tags_xpaths = TAGS_XPATHS_EXTRACT_ONLY

    # Populate the dictionary
    for tag, xpath in tags_xpaths:
        elem = root.find(xpath)
        planning_data[tag] = get_elem_value(elem)

    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation

    # Separate tags by type
    matrix_tags = [tag for tag in planning_data if tag.endswith("_matrix")]
    vector_tags = [tag for tag in planning_data if tag.endswith("_p0") or tag.endswith("_p1")]
    scalar_tags = [tag for tag in planning_data if tag.endswith("_diameter")]
    
    # Filter out None values
    matrix_data = [(tag, planning_data[tag]) for tag in matrix_tags if planning_data[tag]]
    vector_data = [(tag, planning_data[tag]) for tag in vector_tags if planning_data[tag]]
    scalar_data = [(tag, planning_data[tag]) for tag in scalar_tags if planning_data[tag]]
    
    total_plots = (len(matrix_data) * 2) + len(vector_data) + len(scalar_data)  # Each matrix creates 2 plots
    
    if total_plots == 0:
        print("No valid data found to plot.")
        return
    
    # Create individual plots for each measure
    plot_files = create_individual_plots(matrix_data, vector_data, scalar_data, output_prefix, translation_only, actual_side_filter, no_landmark_rotation)
    
    # Generate HTML content with individual plots
    plots_html = ""
    for plot_info in plot_files:
        plots_html += f"""
        <div class="plot-item">
            <h3>{plot_info['title']}</h3>
            <img src="{plot_info['filename']}" alt="{plot_info['title']}" class="individual-plot">
        </div>
        """
    
    # Generate HTML file
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Planning Data Visualization</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
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
        .plot-item h3 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .individual-plot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .data-summary {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
        .data-item {{
            margin: 10px 0;
            padding: 10px;
            background-color: white;
            border-left: 4px solid #007bff;
        }}
        .data-type {{
            font-weight: bold;
            color: #007bff;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Planning Data Visualization</h1>
        
        <div class="plots-grid">
            {plots_html}
        </div>
        
        <div class="data-summary">
            <h2>Data Summary</h2>
            <div class="data-item">
                <span class="data-type">Matrix Data:</span> {len(matrix_data)} items
                <ul>
                    {"".join([f"<li>{tag}</li>" for tag, _ in matrix_data])}
                </ul>
            </div>
            <div class="data-item">
                <span class="data-type">Vector Data:</span> {len(vector_data)} items
                <ul>
                    {"".join([f"<li>{tag}</li>" for tag, _ in vector_data])}
                </ul>
            </div>
            <div class="data-item">
                <span class="data-type">Scalar Data:</span> {len(scalar_data)} items
                <ul>
                    {"".join([f"<li>{tag}</li>" for tag, _ in scalar_data])}
                </ul>
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    html_filename = f"{output_prefix}_report.html"
    with open(html_filename, 'w') as f:
        f.write(html_content)
    
    print(f"Individual plots saved: {len(plot_files)} files")
    for plot_info in plot_files:
        print(f"  - {plot_info['filename']}")
    print(f"HTML report generated: {html_filename}")
    
    # Export to PDF if requested
    if export_pdf:
        # Pass all plot files to PDF export
        success, pdf_filename = export_to_pdf(html_content, plot_files, f"{output_prefix}_report", 
                                            title="Planning Data Visualization")
        if success:
            print(f"PDF report generated: {pdf_filename}")
    
    # Optionally still show the plot
    #plt.show()


def comparePlanningData(xml_path1, xml_path2, xml_path3, output_prefix="planning_data_comparison", export_pdf=False, translation_only=False, side_filter='Both', no_landmark_rotation=False):
    """
    Read and compare planning configuration from three XML files.
    Shows deviations between the three datasets.
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
    # Determine actual side filter based on mode
    actual_side_filter = side_filter
    if side_filter == 'Auto':
        xml_paths = [xml_path1, xml_path2, xml_path3]
        is_consistent, detected_side, sides_list = validate_patient_sides(xml_paths, output_prefix)
        
        if not is_consistent:
            print(f"Error: Auto mode requires consistent PatientSide across all files.")
            print(f"Found inconsistent sides: {sides_list}")
            print(f"Files: {xml_paths}")
            print(f"Falling back to 'Both' mode.")
            actual_side_filter = 'Both'
        elif detected_side is None:
            print(f"Warning: Could not determine PatientSide from any file. Using 'Both' mode.")
            actual_side_filter = 'Both'
        else:
            actual_side_filter = detected_side
            print(f"Info: Auto-detected consistent PatientSide '{detected_side}' across all files. Filtering data accordingly.")
    
    # Validate patient sides consistency across files
    elif side_filter != 'Both':
        xml_paths = [xml_path1, xml_path2, xml_path3]
        is_consistent, detected_side, sides_list = validate_patient_sides(xml_paths, output_prefix)
        
        if not is_consistent:
            print(f"Warning: Inconsistent PatientSide values across files: {sides_list}")
            print(f"Files: {xml_paths}")
        else:
            if detected_side and detected_side != side_filter:
                print(f"Info: Detected PatientSide '{detected_side}' in files, but filtering for '{side_filter}'. Data will be filtered accordingly.")
            elif detected_side:
                print(f"Info: Confirmed PatientSide '{detected_side}' across all files matches filter '{side_filter}'.")
    
    # Helper function to extract data from a single XML file
    def extract_data_from_xml(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        planning_data = {}
        
        def get_elem_value(elem):
            if elem is not None and 'value' in elem.attrib:
                return elem.attrib['value']
            return None
        
        # Use centralized definition of tags and XPaths (full list for comparison)
        tags_xpaths = TAGS_XPATHS
        
        for tag, xpath in tags_xpaths:
            elem = root.find(xpath)
            planning_data[tag] = get_elem_value(elem)
        
        return planning_data
    
    # Extract data from all three XML files
    data1 = extract_data_from_xml(xml_path1)
    data2 = extract_data_from_xml(xml_path2)
    data3 = extract_data_from_xml(xml_path3)
    
    # Get all common tags that exist in all three files
    common_tags = set(data1.keys()) & set(data2.keys()) & set(data3.keys())
    common_tags = [tag for tag in common_tags if data1[tag] and data2[tag] and data3[tag]]
    
    if not common_tags:
        print("No common data found across all three XML files.")
        return
    
    # Separate tags by type
    matrix_tags = [tag for tag in common_tags if tag.endswith("_matrix")]
    vector_tags = [tag for tag in common_tags if tag.endswith("_p0") or tag.endswith("_p1")]
    scalar_tags = [tag for tag in common_tags if tag.endswith("_diameter")]
    
    # Calculate total plots (matrices create 2 plots each: rotation + translation)
    total_plots = (len(matrix_tags) * 2) + len(vector_tags) + len(scalar_tags)
    
    if total_plots == 0:
        print("No valid comparison data found.")
        return
    
    # Create individual comparison plots for each measure
    plot_files = create_individual_comparison_plots(data1, data2, data3, common_tags, output_prefix, translation_only, actual_side_filter, no_landmark_rotation)
    
    # Generate HTML content with individual plots
    plots_html = ""
    for plot_info in plot_files:
        plots_html += f"""
        <div class="plot-item">
            <h3>{plot_info['title']}</h3>
            <img src="{plot_info['filename']}" alt="{plot_info['title']}" class="individual-plot">
        </div>
        """
    
    # Generate comparison statistics
    stats_html = generate_comparison_stats(data1, data2, data3, common_tags)
    
    # Generate HTML report for comparison
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Planning Data Comparison</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 30px;
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
        .plot-item h3 {{
            color: #495057;
            margin-bottom: 15px;
            font-size: 16px;
        }}
        .individual-plot {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .file-info {{
            margin: 20px 0;
            padding: 15px;
            background-color: #e3f2fd;
            border-radius: 5px;
        }}
        .stats-section {{
            margin: 20px 0;
            padding: 15px;
            background-color: #f8f9fa;
            border-radius: 5px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Planning Data Comparison Report</h1>
        
        <div class="file-info">
            <h3>Compared Files:</h3>
            <ul>
                <li><strong>File 1:</strong> {xml_path1}</li>
                <li><strong>File 2:</strong> {xml_path2}</li>
                <li><strong>File 3:</strong> {xml_path3}</li>
            </ul>
            <p><strong>Common data elements:</strong> {len(common_tags)}</p>
        </div>
        
        <div class="plots-grid">
            {plots_html}
        </div>
        
        <div class="stats-section">
            <h2>Comparison Statistics</h2>
            {stats_html}
        </div>
    </div>
</body>
</html>
"""
    
    comparison_html_filename = f"{output_prefix}_report.html"
    with open(comparison_html_filename, 'w') as f:
        f.write(html_content)
    
    print(f"Individual comparison plots saved: {len(plot_files)} files")
    for plot_info in plot_files:
        print(f"  - {plot_info['filename']}")
    print(f"Comparison HTML report generated: {comparison_html_filename}")
    print(f"Found {len(common_tags)} common data elements across all three files")
    
    # Export to PDF if requested
    if export_pdf:
        # Pass all plot files to PDF export
        success, pdf_filename = export_to_pdf(html_content, plot_files, f"{output_prefix}_report", 
                                            title="Planning Data Comparison Report")
        if success:
            print(f"PDF report generated: {pdf_filename}")


def generate_comparison_stats(data1, data2, data3, common_tags):
    """Generate statistical comparison between the three datasets."""
    stats_html = "<table border='1' style='width:100%; border-collapse: collapse;'>"
    stats_html += "<tr><th>Parameter</th><th>File 1</th><th>File 2</th><th>File 3</th><th>Max Deviation</th></tr>"
    
    for tag in common_tags:
        if tag.endswith("_diameter"):
            # Scalar comparison
            val1 = float(data1[tag])
            val2 = float(data2[tag])
            val3 = float(data3[tag])
            
            max_dev = max(abs(val1-val2), abs(val1-val3), abs(val2-val3))
            
            stats_html += f"<tr><td>{tag}</td><td>{val1:.4f}</td><td>{val2:.4f}</td><td>{val3:.4f}</td><td>{max_dev:.4f}</td></tr>"
        
        elif tag.endswith(("_p0", "_p1")):
            # Vector comparison
            vec1 = np.array([float(x) for x in data1[tag].split()])
            vec2 = np.array([float(x) for x in data2[tag].split()])
            vec3 = np.array([float(x) for x in data3[tag].split()])
            
            # Calculate Euclidean distance deviations
            dev12 = np.linalg.norm(vec1 - vec2)
            dev13 = np.linalg.norm(vec1 - vec3)
            dev23 = np.linalg.norm(vec2 - vec3)
            max_dev = max(dev12, dev13, dev23)
            
            stats_html += f"<tr><td>{tag}</td><td>{np.array_str(vec1, precision=3)}</td><td>{np.array_str(vec2, precision=3)}</td><td>{np.array_str(vec3, precision=3)}</td><td>{max_dev:.4f}</td></tr>"
        
        elif tag.endswith("_matrix"):
            # Matrix comparison - show Frobenius norm deviation
            mat1 = np.array([float(x) for x in data1[tag].split()]).reshape((4, 4))
            mat2 = np.array([float(x) for x in data2[tag].split()]).reshape((4, 4))
            mat3 = np.array([float(x) for x in data3[tag].split()]).reshape((4, 4))
            
            # Calculate Frobenius norm deviations
            dev12 = np.linalg.norm(mat1 - mat2, 'fro')
            dev13 = np.linalg.norm(mat1 - mat3, 'fro')
            dev23 = np.linalg.norm(mat2 - mat3, 'fro')
            max_dev = max(dev12, dev13, dev23)
            
            stats_html += f"<tr><td>{tag}</td><td>4x4 Matrix</td><td>4x4 Matrix</td><td>4x4 Matrix</td><td>{max_dev:.4f}</td></tr>"
    
    # Add femoral anteversion comparisons
    for side, suffix in [('Right', 'R'), ('Left', 'L')]:
        femur_key = f'S3FemurFrame_{suffix}_matrix'
        sphere_key = f'S3FemoralSphere_{suffix}_matrix'
        bcp_key = f'S3BCP_{suffix}_matrix'
        p0_key = f'S3BCP_{suffix}_p0'
        p1_key = f'S3BCP_{suffix}_p1'
        requirements = [femur_key, sphere_key, bcp_key, p0_key, p1_key]

        if not all(key in common_tags for key in requirements):
            continue

        try:
            angle1 = calculate_femoral_anteversion(
                data1[femur_key],
                data1[bcp_key],
                femoral_sphere_matrix_str=data1[sphere_key],
                bcp_p0_str=data1[p0_key],
                bcp_p1_str=data1[p1_key],
                side=side,
            )
            angle2 = calculate_femoral_anteversion(
                data2[femur_key],
                data2[bcp_key],
                femoral_sphere_matrix_str=data2[sphere_key],
                bcp_p0_str=data2[p0_key],
                bcp_p1_str=data2[p1_key],
                side=side,
            )
            angle3 = calculate_femoral_anteversion(
                data3[femur_key],
                data3[bcp_key],
                femoral_sphere_matrix_str=data3[sphere_key],
                bcp_p0_str=data3[p0_key],
                bcp_p1_str=data3[p1_key],
                side=side,
            )
        except (KeyError, ValueError):
            continue

        max_dev = max(abs(angle1-angle2), abs(angle1-angle3), abs(angle2-angle3))
        title = f"{side} Femoral Anteversion Angle"
        stats_html += (
            f"<tr><td>{title}</td><td>{angle1:.2f}°</td><td>{angle2:.2f}°</td>"
            f"<td>{angle3:.2f}°</td><td>{max_dev:.2f}°</td></tr>"
        )
    
    stats_html += "</table>"
    return stats_html



def extractPlanningData_plain(xml_path):

    tree = ET.parse(xml_path)
    root = tree.getroot()

    # FemoralSphere_R matrix
    print("Searching S3FemoralSphere_R matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemoralSphere_R']/matrix4[@name='mat']")
    if elem is not None:       
        print("Found S3FemoralSphere_R matrix in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3FemoralSphere_R matrix not found in the XML file.")

    # FemoralSphere_R diameter
    print("Searching S3FemoralSphere_R diameter in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemoralSphere_R']/scalar[@name='diameter']")
    if elem is not None:       
        print("Found S3FemoralSphere_R diameter in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3FemoralSphere_R diameter not found in the XML file.")
            
    # AcetabularHSphere_R matrix
    print("Searching S3AcetabularHSphere_R matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3AcetabularHSphere_R']/matrix4[@name='mat']")
    if elem is not None:   
        print("Found S3AcetabularHSphere_R matrix in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3AcetabularHSphere_R matrix not found in the XML file.")

    # AcetabularHSphere_R diameter
    print("Searching S3AcetabularHSphere_R diameter in the XML file.")
    elem = root.find(".//s3Shape[@name='S3AcetabularHSphere_R']/scalar[@name='diameter']")
    if elem is not None:   
        print("Found S3AcetabularHSphere_R diameter in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3AcetabularHSphere_R diameter not found in the XML file.")

    # FemoralSphere_L matrix
    print("Searching S3FemoralSphere_L matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemoralSphere_L']/matrix4[@name='mat']")
    if elem is not None:       
        print("Found S3FemoralSphere_L matrix in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3FemoralSphere_L matrix not found in the XML file.")

    # FemoralSphere_L diameter
    print("Searching S3FemoralSphere_L diameter in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemoralSphere_L']/scalar[@name='diameter']")
    if elem is not None:       
        print("Found S3FemoralSphere_L diameter in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3FemoralSphere_L diameter not found in the XML file.")
            
    # AcetabularHSphere_L matrix
    print("Searching S3AcetabularHSphere_L matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3AcetabularHSphere_L']/matrix4[@name='mat']")
    if elem is not None:   
        print("Found S3AcetabularHSphere_L matrix in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3AcetabularHSphere_L matrix not found in the XML file.")    

    # AcetabularHSphere_L diameter
    print("Searching S3AcetabularHSphere_L diameter in the XML file.")
    elem = root.find(".//s3Shape[@name='S3AcetabularHSphere_L']/scalar[@name='diameter']")
    if elem is not None:   
        print("Found S3AcetabularHSphere_L diameter in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3AcetabularHSphere_L diameter not found in the XML file.")  

    # S3GreaterTroch_R
    print("Searching S3GreaterTroch_R in the XML file.")
    elem = root.find(".//s3Shape[@name='S3GreaterTroch_R']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3GreaterTroch_R in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3GreaterTroch_R not found in the XML file.")

    # S3GreaterTroch_L
    print("Searching S3GreaterTroch_L in the XML file.")
    elem = root.find(".//s3Shape[@name='S3GreaterTroch_L']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3GreaterTroch_L in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3GreaterTroch_L not found in the XML file.")

    # S3TopLesserTroch_R
    print("Searching S3TopLesserTroch_R in the XML file.")
    elem = root.find(".//s3Shape[@name='S3TopLesserTroch_R']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3TopLesserTroch_R in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3TopLesserTroch_R not found in the XML file.")

    # S3TopLesserTroch_L
    print("Searching S3TopLesserTroch_L in the XML file.")
    elem = root.find(".//s3Shape[@name='S3TopLesserTroch_L']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3TopLesserTroch_L in the XML file.")
        values = elem.attrib['value'].split()
    else:
        print("S3TopLesserTroch_L not found in the XML file.")


    # S3BCP_R matrix
    print("Searching S3BCP_R matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_R']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3BCP_R matrix in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_R matrix not found in the XML file.")

    # S3BCP_R vector p0
    print("Searching S3BCP_R vector in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_R']/vector3[@name='p0']")
    if elem is not None:
        print("Found S3BCP_R vector in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_R vector not found in the XML file.")

    # S3BCP_R vector p1
    print("Searching S3BCP_R vector in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_R']/vector3[@name='p1']")
    if elem is not None:
        print("Found S3BCP_R vector in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_R vector not found in the XML file.")

    # S3BCP_L matrix 
    print("Searching S3BCP_L matrix in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_L']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3BCP_L matrix in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_L matrix not found in the XML file.")

    # S3BCP_L vector p0
    print("Searching S3BCP_L vector in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_L']/vector3[@name='p0']")
    if elem is not None:
        print("Found S3BCP_L vector in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_L vector not found in the XML file.")

    # S3BCP_L vector p1
    print("Searching S3BCP_L vector in the XML file.")
    elem = root.find(".//s3Shape[@name='S3BCP_L']/vector3[@name='p1']")
    if elem is not None:
        print("Found S3BCP_L vector in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3BCP_L vector not found in the XML file.")

    # S3AppFrame
    print("Searching S3AppFrame in the XML file.")
    elem = root.find(".//s3Shape[@name='S3AppFrame']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3AppFrame in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3AppFrame not found in the XML file.")

    # S3FemurFrame_R
    print("Searching S3FemurFrame_R in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemurFrame_R']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3FemurFrame_R in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3FemurFrame_R not found in the XML file.")

    # S3FemurFrame_L
    print("Searching S3FemurFrame_L in the XML file.")
    elem = root.find(".//s3Shape[@name='S3FemurFrame_L']/matrix4[@name='mat']")
    if elem is not None:
        print("Found S3FemurFrame_L in the XML file.")
        original_matrix = elem.attrib['value']
    else:
        print("S3FemurFrame_L not found in the XML file.")



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Extract and plot planning data from XML file(s).")
    parser.add_argument("--xml_path", help="Path to the planning XML file (for single file analysis)")
    parser.add_argument("--compare", nargs=3, metavar=('XML1', 'XML2', 'XML3'), 
                       help="Compare three XML files (provide paths to all three files)")
    parser.add_argument("--output", "-o", help="Output filename prefix (without extension)")
    parser.add_argument("--pdf", action="store_true", help="Also export results to PDF format")
    parser.add_argument("--translation-only", action="store_true", 
                       help="Only display translation (positional) data from matrices, skip rotation and other measurements")
    parser.add_argument("--no-landmark-rotation", action="store_true",
                       help="Exclude rotation analysis for anatomical landmarks (S3GreaterTroch, S3TopLesserTroch, S3FemoralSphere)")
    parser.add_argument("--side", choices=['Left', 'Right', 'Both', 'Auto'], default='Both',
                       help="Filter data by patient side: Left, Right, Both, or Auto (detect from XML) - default: Both")
    args = parser.parse_args()

    if args.compare:
        # Compare three XML files
        output_prefix = args.output if args.output else "planning_data_comparison"
        comparePlanningData(args.compare[0], args.compare[1], args.compare[2], output_prefix, 
                          export_pdf=args.pdf, translation_only=args.translation_only, side_filter=args.side, no_landmark_rotation=args.no_landmark_rotation)
    elif args.xml_path:
        # Single file analysis
        output_prefix = args.output if args.output else "planning_data"
        extractPlanningData(args.xml_path, output_prefix, export_pdf=args.pdf, 
                          translation_only=args.translation_only, side_filter=args.side, no_landmark_rotation=args.no_landmark_rotation)
    else:
        print("Please provide either --xml_path for single file analysis or --compare with three XML file paths")
        print("Examples:")
        print("  python excerpts.py --xml_path planning.xml")
        print("  python excerpts.py --xml_path planning.xml --output my_analysis")
        print("  python excerpts.py --xml_path planning.xml --pdf")
        print("  python excerpts.py --xml_path planning.xml --translation-only")
        print("  python excerpts.py --xml_path planning.xml --side Left")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml --output comparison_study --pdf")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml --translation-only")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml --side Right")
