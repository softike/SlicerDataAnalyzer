# Slicer Data Analyzer

Setup for Slicer related development with Python, featuring individual plot generation and PDF export capabilities.

## Features

- **Individual Plot Generation**: Each measure (matrix rotations, translations, vectors, scalars) is now saved as a separate high-quality image
- **HTML Reports**: Interactive reports with grid layout showing all individual plots
- **PDF Export**: Full-featured PDF reports with embedded plots and statistics
- **Three Comparison Methods**: Support for single file analysis and three-file comparisons

## Conda Environment

We use Python 3.10, create a conda environment:

```shell
conda create -n slicer-env-py310 python=3.10
```

Install required packages:

```shell
pip install numpy matplotlib weasyprint
```

## Usage Examples

### Basic Comparison Analysis

The script can achieve a comparison analysis using seedplan files as inputs:

```shell
# Three-file comparison with individual plots
python compareResults_3Studies.py --compare /mnt/localstore3/H001/001-M-30/Mediplan3D/seedplan.xml /mnt/localstore3/H002/001-M-30/Mediplan3D/seedplan.xml  /mnt/localstore3/H003/001-M-30/Mediplan3D/seedplan.xml 

# With custom output prefix
python compareResults_3Studies.py --compare /mnt/localstore3/H001/002-F-36/Mediplan3D/seedplan.xml /mnt/localstore3/H002/002-F-36/Mediplan3D/seedplan.xml  /mnt/localstore3/H003/002-F-36/Mediplan3D/seedplan.xml --output Patient002

# Single file analysis
python compareResults_3Studies.py --xml_path /path/to/planning.xml --output MyAnalysis
```

### PDF Export

Add the `--pdf` flag to any command to also generate PDF reports:

```shell
# Comparison with PDF export
python compareResults_3Studies.py --compare file1.xml file2.xml file3.xml --pdf

# Single file with PDF export
python compareResults_3Studies.py --xml_path planning.xml --pdf --output MyReport
```

## Output Files

### Individual Plots Generated

**For single file analysis:**
- `{prefix}_{tag}_rotation.png` - Matrix rotation heatmaps
- `{prefix}_{tag}_translation.png` - Translation bar charts
- `{prefix}_{tag}_vector.png` - Vector component charts
- `{prefix}_{tag}_scalar.png` - Scalar value displays

**For three-file comparison:**
- `{prefix}_{tag}_rotation_deviation.png` - Rotation deviation heatmaps
- `{prefix}_{tag}_translation_comparison.png` - Translation comparison charts
- `{prefix}_{tag}_vector_comparison.png` - Vector comparison charts
- `{prefix}_{tag}_scalar_comparison.png` - Scalar comparison with deviation info

### Reports
- `{prefix}_report.html` - Interactive HTML report with all plots
- `{prefix}_report.pdf` - PDF version (when using --pdf flag)

## Installation for PDF Export

For full PDF functionality, install weasyprint:

```shell
pip install weasyprint
```

For alternative PDF generation:
```shell
pip install pdfkit
sudo apt-get install wkhtmltopdf  # Linux
```

See `PDF_EXPORT_README.md` for detailed PDF export documentation.


