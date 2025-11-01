import os
import xml.etree.ElementTree as ET

import numpy as np
import argparse
from pathlib import Path

dcm_path = r"C:\\Users\\Coder\\Desktop\\001-M-30\\001-M-30\\Dataset"

##
def export_to_pdf(html_content, plot_filename, output_prefix, title="Planning Data Report"):
    """
    Export HTML content and plots to PDF using weasyprint or pdfkit.
    Falls back to matplotlib PDF if web-based libraries are not available.
    """
    pdf_filename = f"{output_prefix}.pdf"
    
    # Try different PDF generation methods
    success = False
    
    # Method 1: Try weasyprint (recommended for HTML to PDF)
    try:
        from weasyprint import HTML, CSS
        from weasyprint.css import get_all_computed_styles
        
        # Create a complete HTML document with embedded plot
        if os.path.exists(plot_filename):
            import base64
            with open(plot_filename, 'rb') as img_file:
                img_data = base64.b64encode(img_file.read()).decode()
                img_tag = f'<img src="data:image/png;base64,{img_data}" style="max-width: 100%; height: auto;">'
        else:
            img_tag = f'<p>Plot file not found: {plot_filename}</p>'
        
        # Replace the image src in HTML with base64 data
        html_for_pdf = html_content.replace(f'src="{plot_filename}"', f'src="data:image/png;base64,{img_data}"')
        
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
            
            # Create temporary HTML file with absolute paths
            temp_html = f"{output_prefix}_temp.html"
            
            # Convert relative image path to absolute
            abs_plot_path = os.path.abspath(plot_filename)
            html_for_pdf = html_content.replace(f'src="{plot_filename}"', f'src="file://{abs_plot_path}"')
            
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
                
                # Add the main plot if it exists
                if os.path.exists(plot_filename):
                    fig = plt.figure(figsize=(11, 8.5))
                    img = plt.imread(plot_filename)
                    plt.imshow(img)
                    plt.axis('off')
                    plt.title(title, fontsize=16, pad=20)
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

##
def create_individual_plots(matrix_data, vector_data, scalar_data, output_prefix):
    """
    Create individual plots for each measure and save them as separate image files.
    Returns a list of dictionaries containing plot information.
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
    plot_files = []
    
    # Create plots for matrices (rotation and translation parts separately)
    for tag, value in matrix_data:
        # Parse the 4x4 matrix
        mat = np.array([float(x) for x in value.split()]).reshape((4, 4))
        
        # Extract rotation (3x3) and translation (3x1) parts
        rotation_part = mat[:3, :3]
        translation_part = mat[3, :3]
        
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
        
        # Plot translation part as bar chart
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
    
    return plot_files

##
def create_individual_comparison_plots(data1, data2, data3, common_tags, output_prefix):
    """
    Create individual comparison plots for each measure from three datasets.
    Returns a list of dictionaries containing plot information.
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
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
        
        # Extract translation parts
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
def extractPlanningData(xml_path, output_prefix="planning_data", export_pdf=False):
    """
    Read the planning configuration from a file.
    """
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Create a dictionary to store tag-value pairs
    planning_data = {}

    # Helper function to extract value from an element
    def get_elem_value(elem):
        if elem is not None and 'value' in elem.attrib:
            return elem.attrib['value']
        return None

    # List of (tag, xpath) pairs to extract
    tags_xpaths = [
        #("S3FemoralSphere_R_matrix", ".//s3Shape[@name='S3FemoralSphere_R']/matrix4[@name='mat']"),
        ("S3FemoralSphere_R_diameter", ".//s3Shape[@name='S3FemoralSphere_R']/scalar[@name='diameter']"),
        #("S3AcetabularHSphere_R_matrix", ".//s3Shape[@name='S3AcetabularHSphere_R']/matrix4[@name='mat']"),
        #("S3AcetabularHSphere_R_diameter", ".//s3Shape[@name='S3AcetabularHSphere_R']/scalar[@name='diameter']"),
        #("S3FemoralSphere_L_matrix", ".//s3Shape[@name='S3FemoralSphere_L']/matrix4[@name='mat']"),
        ("S3FemoralSphere_L_diameter", ".//s3Shape[@name='S3FemoralSphere_L']/scalar[@name='diameter']"),
        #("S3AcetabularHSphere_L_matrix", ".//s3Shape[@name='S3AcetabularHSphere_L']/matrix4[@name='mat']"),
        #("S3AcetabularHSphere_L_diameter", ".//s3Shape[@name='S3AcetabularHSphere_L']/scalar[@name='diameter']"),
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
    plot_files = create_individual_plots(matrix_data, vector_data, scalar_data, output_prefix)
    
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
        # For PDF export, we'll use the first plot as the main image, or create a summary plot
        main_plot_filename = plot_files[0]['filename'] if plot_files else None
        success, pdf_filename = export_to_pdf(html_content, main_plot_filename, f"{output_prefix}_report", 
                                            title="Planning Data Visualization")
        if success:
            print(f"PDF report generated: {pdf_filename}")
    
    # Optionally still show the plot
    #plt.show()


def comparePlanningData(xml_path1, xml_path2, xml_path3, output_prefix="planning_data_comparison", export_pdf=False):
    """
    Read and compare planning configuration from three XML files.
    Shows deviations between the three datasets.
    """
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend for HTML generation
    
    # Helper function to extract data from a single XML file
    def extract_data_from_xml(xml_path):
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        planning_data = {}
        
        def get_elem_value(elem):
            if elem is not None and 'value' in elem.attrib:
                return elem.attrib['value']
            return None
        
        tags_xpaths = [
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
            ("S3AppFrame_matrix", ".//s3Shape[@name='S3AppFrame']/matrix4[@name='mat']"),
            ("S3FemurFrame_R_matrix", ".//s3Shape[@name='S3FemurFrame_R']/matrix4[@name='mat']"),
            ("S3FemurFrame_L_matrix", ".//s3Shape[@name='S3FemurFrame_L']/matrix4[@name='mat']"),
        ]
        
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
    plot_files = create_individual_comparison_plots(data1, data2, data3, common_tags, output_prefix)
    
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
        # For PDF export, we'll use the first plot as the main image, or create a summary plot
        main_plot_filename = plot_files[0]['filename'] if plot_files else None
        success, pdf_filename = export_to_pdf(html_content, main_plot_filename, f"{output_prefix}_report", 
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
    args = parser.parse_args()

    if args.compare:
        # Compare three XML files
        output_prefix = args.output if args.output else "planning_data_comparison"
        comparePlanningData(args.compare[0], args.compare[1], args.compare[2], output_prefix, export_pdf=args.pdf)
    elif args.xml_path:
        # Single file analysis
        output_prefix = args.output if args.output else "planning_data"
        extractPlanningData(args.xml_path, output_prefix, export_pdf=args.pdf)
    else:
        print("Please provide either --xml_path for single file analysis or --compare with three XML file paths")
        print("Examples:")
        print("  python excerpts.py --xml_path planning.xml")
        print("  python excerpts.py --xml_path planning.xml --output my_analysis")
        print("  python excerpts.py --xml_path planning.xml --pdf")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml --output comparison_study --pdf")
