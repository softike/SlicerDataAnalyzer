import os
import xml.etree.ElementTree as ET

import numpy as np
import argparse

dcm_path = r"C:\\Users\\Coder\\Desktop\\001-M-30\\001-M-30\\Dataset"

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
def extractPlanningData(xml_path, output_prefix="planning_data"):
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
    
    # Calculate grid dimensions
    cols = 3
    rows = (total_plots + cols - 1) // cols
    
    # Create figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(15, 5 * rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    elif total_plots == 1:
        axes = axes.reshape(1, 1)
    
    plot_idx = 0
    
    # Plot matrices as separate rotation and translation plots
    for tag, value in matrix_data:
        # Parse the 4x4 matrix
        mat = np.array([float(x) for x in value.split()]).reshape((4, 4))
        
        # Extract rotation (3x3) and translation (3x1) parts
        rotation_part = mat[:3, :3]
        translation_part = mat[3, :3]
        
        # Plot rotation part as heatmap
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        im = ax.imshow(rotation_part, cmap='viridis', interpolation='nearest')
        ax.set_title(f"{tag} (Rotation 3x3)", fontsize=9)
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        plt.colorbar(im, ax=ax)
        plot_idx += 1
        
        # Plot translation part as bar chart
        if plot_idx < rows * cols:  # Check if we have space for another plot
            row, col = plot_idx // cols, plot_idx % cols
            ax = axes[row, col]
            ax.bar(['X', 'Y', 'Z'], translation_part)
            ax.set_title(f"{tag} (Translation)", fontsize=9)
            ax.set_ylabel("Value")
            ax.grid(True, alpha=0.3)
            plot_idx += 1

    # Plot vectors as bar plots
    for tag, value in vector_data:
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        
        vec = np.array([float(x) for x in value.split()])
        ax.bar(range(len(vec)), vec)
        ax.set_title(f"{tag} (vector)", fontsize=10)
        ax.set_xlabel("Index")
        ax.set_ylabel("Value")
        plot_idx += 1

    # Plot scalars as single-value bar plots
    for tag, value in scalar_data:
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        
        val = float(value)
        ax.bar([0], [val])
        ax.set_title(f"{tag} (scalar)", fontsize=10)
        ax.set_ylabel("Value")
        ax.set_xticks([])
        plot_idx += 1
    
    # Hide unused subplots
    for i in range(plot_idx, rows * cols):
        row, col = i // cols, i % cols
        axes[row, col].set_visible(False)
    
    plt.tight_layout()
    
    # Save as PNG for HTML embedding
    plot_filename = f"{output_prefix}_plots.png"
    plt.savefig(plot_filename, dpi=300, bbox_inches='tight')
    
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
            max-width: 1200px;
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
        .plot-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .plot-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
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
        
        <div class="plot-container">
            <img src="{plot_filename}" alt="Planning Data Plots">
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
    
    print(f"Combined plot saved as: {plot_filename}")
    print(f"HTML report generated: {html_filename}")
    
    # Optionally still show the plot
    #plt.show()


def comparePlanningData(xml_path1, xml_path2, xml_path3, output_prefix="planning_data_comparison"):
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
    
    # Calculate grid dimensions
    cols = 3
    rows = (total_plots + cols - 1) // cols
    
    # Create figure with subplots
    fig, axes = plt.subplots(rows, cols, figsize=(18, 6 * rows))
    if rows == 1:
        axes = axes.reshape(1, -1)
    elif total_plots == 1:
        axes = axes.reshape(1, 1)
    
    plot_idx = 0
    
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
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        im = ax.imshow(max_rot_dev, cmap='Reds', interpolation='nearest')
        ax.set_title(f"{tag} (Rotation Deviation)", fontsize=9)
        ax.set_xlabel("Column")
        ax.set_ylabel("Row")
        plt.colorbar(im, ax=ax, label='Max Deviation')
        plot_idx += 1
        
        # Extract translation parts
        trans1, trans2, trans3 = mat1[3, :3], mat2[3, :3], mat3[3, :3]
        
        # Plot translation comparison
        if plot_idx < rows * cols:
            row, col = plot_idx // cols, plot_idx % cols
            ax = axes[row, col]
            
            x_pos = np.arange(3)
            width = 0.25
            
            ax.bar(x_pos - width, trans1, width, label='File 1', alpha=0.8)
            ax.bar(x_pos, trans2, width, label='File 2', alpha=0.8)
            ax.bar(x_pos + width, trans3, width, label='File 3', alpha=0.8)
            
            ax.set_title(f"{tag} (Translation Comparison)", fontsize=9)
            ax.set_ylabel("Value")
            ax.set_xticks(x_pos)
            ax.set_xticklabels(['X', 'Y', 'Z'])
            ax.legend(fontsize=8)
            ax.grid(True, alpha=0.3)
            plot_idx += 1
    
    # Compare vectors
    for tag in vector_tags:
        vec1 = np.array([float(x) for x in data1[tag].split()])
        vec2 = np.array([float(x) for x in data2[tag].split()])
        vec3 = np.array([float(x) for x in data3[tag].split()])
        
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        
        x_pos = np.arange(len(vec1))
        width = 0.25
        
        ax.bar(x_pos - width, vec1, width, label='File 1', alpha=0.8)
        ax.bar(x_pos, vec2, width, label='File 2', alpha=0.8)
        ax.bar(x_pos + width, vec3, width, label='File 3', alpha=0.8)
        
        ax.set_title(f"{tag} (Vector Comparison)", fontsize=9)
        ax.set_xlabel("Component")
        ax.set_ylabel("Value")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        plot_idx += 1
    
    # Compare scalars
    for tag in scalar_tags:
        val1 = float(data1[tag])
        val2 = float(data2[tag])
        val3 = float(data3[tag])
        
        row, col = plot_idx // cols, plot_idx % cols
        ax = axes[row, col]
        
        values = [val1, val2, val3]
        labels = ['File 1', 'File 2', 'File 3']
        colors = ['skyblue', 'lightcoral', 'lightgreen']
        
        bars = ax.bar(labels, values, color=colors, alpha=0.8)
        ax.set_title(f"{tag} (Scalar Comparison)", fontsize=9)
        ax.set_ylabel("Value")
        ax.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, val in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values)*0.01,
                   f'{val:.3f}', ha='center', va='bottom', fontsize=8)
        plot_idx += 1
    
    # Hide unused subplots
    for i in range(plot_idx, rows * cols):
        row, col = i // cols, i % cols
        axes[row, col].set_visible(False)
    
    plt.tight_layout()
    
    # Save comparison plot
    comparison_plot_filename = f"{output_prefix}.png"
    plt.savefig(comparison_plot_filename, dpi=300, bbox_inches='tight')
    
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
        .plot-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .plot-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #ddd;
            border-radius: 5px;
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
        
        <div class="plot-container">
            <img src="{comparison_plot_filename}" alt="Planning Data Comparison">
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
    
    print(f"Comparison plot saved as: {comparison_plot_filename}")
    print(f"Comparison HTML report generated: {comparison_html_filename}")
    print(f"Found {len(common_tags)} common data elements across all three files")


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
    args = parser.parse_args()

    if args.compare:
        # Compare three XML files
        output_prefix = args.output if args.output else "planning_data_comparison"
        comparePlanningData(args.compare[0], args.compare[1], args.compare[2], output_prefix)
    elif args.xml_path:
        # Single file analysis
        output_prefix = args.output if args.output else "planning_data"
        extractPlanningData(args.xml_path, output_prefix)
    else:
        print("Please provide either --xml_path for single file analysis or --compare with three XML file paths")
        print("Examples:")
        print("  python excerpts.py --xml_path planning.xml")
        print("  python excerpts.py --xml_path planning.xml --output my_analysis")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml")
        print("  python excerpts.py --compare plan1.xml plan2.xml plan3.xml --output comparison_study")
