import os
import xml.etree.ElementTree as ET

import numpy as np
import argparse

# Import centralized tag definitions
from compareResults_3Studies import TAGS_XPATHS

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
def extractPlanningData(xml_path):
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

    # Use centralized definition of tags and XPaths
    tags_xpaths = TAGS_XPATHS

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
    plot_filename = "planning_data_plots.png"
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
    
    html_filename = "planning_data_report.html"
    with open(html_filename, 'w') as f:
        f.write(html_content)
    
    print(f"Combined plot saved as: {plot_filename}")
    print(f"HTML report generated: {html_filename}")
    
    # Optionally still show the plot
    #plt.show()




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

    parser = argparse.ArgumentParser(description="Extract and plot planning data from an XML file.")
    parser.add_argument("--xml_path", help="Path to the planning XML file")
    args = parser.parse_args()

    extractPlanningData(args.xml_path)

    