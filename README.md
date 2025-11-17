# Slicer Data Analyzer

Setup for Slicer related development with Python, featuring individual plot generation and PDF export capabilities.

## Features

- **Individual Plot Generation**: Each measure (matrix rotations, translations, vectors, scalars) is now saved as a separate high-quality image
- **HTML Reports**: Interactive reports with grid layout showing all individual plots
- **PDF Export**: Full-featured PDF reports with embedded plots and statistics
- **Excel Export**: Raw data export to Excel spreadsheets for statistical analysis
- **Batch Processing**: Process multiple case folders automatically
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

### Excel Export

Add the `--excel` flag to export raw data to Excel spreadsheets for further statistical analysis:

```shell
# Export raw data to Excel
python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_report --excel

# Export detailed component-wise data
python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_report --excel-detailed

# Combine with other export formats
python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_report --pdf --excel --excel-detailed
```

**Standard Excel Export (`--excel`)** creates a comprehensive workbook with:
- **All_Data**: Complete dataset with all cases and parameters
- **Matrix/Vector/Scalar**: Separate sheets by data type
- **Left_Side/Right_Side**: Anatomical side-specific data
- **Summary**: Statistics summary by case
- **Femoral_Anteversion_Angles**: Calculated anteversion angles for analysis

**Detailed Excel Export (`--excel-detailed`)** breaks down complex data into individual components:
- **Matrices**: Each 4x4 matrix element in separate columns (M_11, M_12, ... M_44, Translation_X/Y/Z)
- **Vectors**: Individual X, Y, Z components in separate columns
- **Component Analysis**: Pivot tables for easier statistical analysis
- **Translation Components**: Dedicated sheet for positional data
- **Rotation Components**: Dedicated sheet for rotational matrix elements

### Batch Processing

Process multiple cases across H001, H002, H003 directories:

```shell
# Basic batch processing
python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_comparison_report

# With side filtering
python batchCompareStudies.py --base_path /mnt/localstore3 --output batch_report --side Left

# Auto-detect sides and export everything
python batchCompareStudies.py --base_path /mnt/localstore3 --output comprehensive_report --side Auto --pdf --excel
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
- `{prefix}_raw_data.xlsx` - Excel workbook with raw data (when using --excel flag)
- `{prefix}_detailed_data.xlsx` - Excel workbook with component-wise data (when using --excel-detailed flag)

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

## Installation for Excel Export

For Excel export functionality, install pandas and openpyxl:

```shell
pip install -r requirements_excel.txt
```

Or manually:
```shell
pip install pandas openpyxl
```

Alternative Excel engine:
```shell
pip install xlsxwriter  # Alternative to openpyxl
```

## Excel Export Format

The Excel export (`--excel` flag) generates a comprehensive `.xlsx` workbook with the following structure:

### Worksheet Organization

1. **All_Data**: Complete dataset with all cases and parameters
   - Columns: Case, Parameter, Data_Type, Anatomical_Side, H001_Value, H002_Value, H003_Value

2. **Matrix/Vector/Scalar**: Data separated by type for focused analysis
   - Matrix data: 4x4 transformation matrices  
   - Vector data: 3D coordinate vectors
   - Scalar data: Single numerical values

3. **Left_Side/Right_Side**: Anatomical side-specific data
   - Facilitates bilateral comparison studies

4. **Summary**: Case-by-case statistics
   - Parameter counts by data type and anatomical side

5. **Femoral_Anteversion_Angles**: Calculated clinical angles
   - Direct comparison values for inter-rater analysis

This format enables advanced statistical analysis in Excel, R, SPSS, or other statistical software while preserving the complete raw dataset without any statistical processing or summarization.

### Excel Export Examples

**Standard Format** (`--excel`): Raw values preserved as strings
```
Case      | Parameter           | Data_Type | H001_Value                              | H002_Value
----------|--------------------|-----------|-----------------------------------------|------------
test_case | S3BCP_R_matrix     | Matrix    | "1.0 0.0 0.0 125.5 0.0 1.0 0.0 89.2..." | "0.99 0.01..."
test_case | S3BCP_R_p0_vector  | Vector    | "125.5 89.2 -15.8"                     | "126.1 88.9..."
```

**Detailed Format** (`--excel-detailed`): Individual components in separate columns
```
Case      | Parameter         | Component     | Data_Type    | H001_Value | H002_Value | H003_Value
----------|-------------------|---------------|--------------|------------|------------|------------
test_case | S3BCP_R_matrix    | M_11         | Matrix_M_11  | 1.0        | 0.99       | 0.98
test_case | S3BCP_R_matrix    | M_12         | Matrix_M_12  | 0.0        | 0.01       | 0.02  
test_case | S3BCP_R_matrix    | Translation_X | Matrix_Trans | 125.5      | 126.1      | 124.8
test_case | S3BCP_R_p0_vector | X            | Vector_X     | 125.5      | 126.1      | 124.8
test_case | S3BCP_R_p0_vector | Y            | Vector_Y     | 89.2       | 88.9       | 89.5
```

This detailed format is ideal for:
- Statistical analysis of individual matrix/vector components
- ICC calculations for specific measurements  
- Component-wise correlation analysis
- Precision assessment of translation vs rotation measurements


