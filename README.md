# Slicer Data Analyzer

Setup for Slicer related development with Python, featuring individual plot generation and PDF export capabilities.

## Features

- **Individual Plot Generation**: Each measure (matrix rotations, translations, vectors, scalars) is now saved as a separate high-quality image
- **HTML Reports**: Interactive reports with grid layout showing all individual plots
- **PDF Export**: Full-featured PDF reports with embedded plots and statistics
- **Excel Export**: Raw data export to Excel spreadsheets for statistical analysis
- **Batch Processing**: Process multiple case folders automatically
- **Three Comparison Methods**: Support for single file analysis and three-file comparisons
- **Implant STL Viewer**: Locate Mathys or Johnson STL files by S3UID and preview them interactively

## Implant STL Viewer

Use `view_implant.py` to resolve a Mathys or Johnson implant S3UID to its RCC identifier, locate the matching STL in one or more folders, and render it with VTK. You can pass either the enum name (`STEM_STD_1`) or the numeric UID value (`130506`).

1. Install VTK once per environment:

   ```shell
   pip install vtk
   ```

2. Launch the viewer (example scans two folders for a Mathys implant and prints verbose details):

   ```shell
   python view_implant.py STEM_STD_1 D:\implants\mathys E:\archives --manufacturer mathys --verbose
   ```

   Or by numeric value (manufacturer becomes optional if the value is unique):

   ```shell
   python view_implant.py 130506 D:\implants\mathys E:\archives --verbose
   ```

   Omit `--manufacturer` to try every known implant module (`mathys_implants`, `johnson_implants_corail`, `johnson_implants_actis`). The script first searches for an STL whose filename matches the RCC identifier, then falls back to substrings of the S3UID name.

3. An interactive VTK window opens so you can inspect the geometry. Close the window to exit the script.

> Tip: Run `python view_implant.py --help` for the full CLI reference.

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
- **Femoral_Anteversion_Angles**: Angle between the projected femoral-neck vector (FemurFrame→FemoralSphere) and the transformed BCP line (planner p0/p1)

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

5. **Femoral_Anteversion_Angles**: Angle between the projected femoral-neck vector and the transformed BCP line
   - Direct comparison values for inter-rater analysis

This format enables advanced statistical analysis in Excel, R, SPSS, or other statistical software while preserving the complete raw dataset without any statistical processing or summarization.

### Femoral Anteversion Calculation

The anteversion worksheet/plots now mirror the projected-vector workflow validated with the planning team:

1. Form the femoral-neck vector by connecting the femur-frame origin to the femoral-sphere center, then project it onto the anatomical XY plane. The resulting azimuth defines the femoral-neck angle (Left sides are shifted by 180° for continuity).
2. Transform the planner-provided BCP measurement points (`p0`, `p1`): zero their Z components, rotate them by `Rᵀ` of the BCP matrix, translate into world coordinates, and take the directed difference (`p0 - p1` for Right, `p1 - p0` for Left). Project this direction onto the XY plane to obtain the BCP azimuth, again applying the left-side adjustment.
3. Report anteversion as the shortest unsigned difference between the neck and BCP angles, preserving the +21°/−21° conventions established during manual validation.

This approach encodes the same calculation sequence used during manual verification (case 008), ensuring planner outputs, plots, and Excel exports all reflect the trusted anatomy-driven reference frame.

### Excel Export Examples

**Standard Format** (`--excel`): Raw values preserved as strings

```text
Case      | Parameter           | Data_Type | H001_Value                              | H002_Value
----------|--------------------|-----------|-----------------------------------------|------------
test_case | S3BCP_R_matrix     | Matrix    | "1.0 0.0 0.0 125.5 0.0 1.0 0.0 89.2..." | "0.99 0.01..."
test_case | S3BCP_R_p0_vector  | Vector    | "125.5 89.2 -15.8"                     | "126.1 88.9..."
```

**Detailed Format** (`--excel-detailed`): Individual components in separate columns

```text
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


### 

Load image and stem in Slicer from seedplan.xml 

Here is a Mathys case

``` shell
python ./load_nifti_and_stem.py --nifti /home/developer/Projects/Code/AZDiffRadio/outputs/classif_2/001-M-30/Dataset/series_by_id/1.2.840.114356.270937472228232525423838658850315419768/nifti/1.2.840.114356.270937472228232525423838658850315419768.nii.gz --seedplan /mnt/localstore1/H001/001-M-30/Mediplan3D/seedplan.xml --stl-folder /mnt/localstore1/Implants4EZplan --no-splash  --post-rotate-z-180
```

Here is a Corail case

```shell
python ./load_nifti_and_stem.py --nifti /home/developer/Projects/Code/AZDiffRadio/outputs/classif_2/007-F-87/Dataset/series_by_id/1.3.46.670589.33.1.63837029670551863400001.4767352654215964939/nifti/1.3.46.670589.33.1.63837029670551863400001.4767352654215964939.nii.gz --seedplan /mnt/localstore1/H001/007-F-87/Mediplan3D/seedplan.xml --stl-folder /mnt/localstore1/Implants4EZplan  --no-splash --pre-rotate-z-180 --post-rotate-z-180
```

Here is an Actis case

```shell
python ./load_nifti_and_stem.py --nifti /home/developer/Projects/Code/AZDiffRadio/outputs/classif_2/011-F-54/Dataset/series_by_id/1.2.840.113619.2.416.154329578107230525325724120376429504045/stacks/stack_03/nifti/1.2.840.113619.2.416.154329578107230525325724120376429504045_stack_03.nii.gz --seedplan /mnt/localstore1/H003/011-F-54/Mediplan3D/seedplan.xml --stl-folder /mnt/localstore1/Implants4EZplan  --no-splash --pre-rotate-z-180 --post-rotate-z-180
```

`load_nifti_and_stem.py` automatically applies the correct Z-rotations: Mathys stems receive `--post-rotate-z-180`, while Johnson Corail/Actis stems get both `--pre-rotate-z-180` and `--post-rotate-z-180`. Pass `--rotation-mode mathys|johnson|none` to override.

Add the `--compute-stem-scalars` flag to probe the image volume onto the hardened stem clone and print the HU distribution, and tack on `--export-stem-screenshots` to automatically capture AP/Sagittal PNGs with the EZplan LUT. Screenshots land in a `Slicer-exports/` folder next to each case's `seedplan.xml` and are overwritten on every run.

> **Note:** Screenshot export requires a GUI-capable Slicer run (e.g., omit `--no-main-window`); headless sessions cannot capture 3D views and will raise an explicit error.

Add `--exit-after-run` if you need the launched Slicer GUI to close itself automatically when processing finishes (useful when running several cases back-to-back without manual interaction).

Whenever stem scalars are computed, the script also writes the original (non-hardened) stem geometry—with the sampled scalar array attached—to `Slicer-exports/<volume>_stem_original.vtp`, so you can reload the untouched implant in future sessions without re-running the sampling step.

In the same `Slicer-exports/` directory you now also get a machine-friendly `*_stem_metrics.xml`. Each XML captures the case/user identifiers (H001/H002/H003), the detected stem metadata, scalar range, and the EZplan zone distribution (counts + percentages). This makes it trivial to audit which implant model was used and how its fixation zones scored without re-opening Slicer.

Once a batch run has produced those XML files, aggregate everything into a workbook with:

```shell
python export_stem_metrics_excel.py --root /mnt/localstore1 --output stem_metrics.xlsx
```

The exporter auto-discovers every `*_stem_metrics.xml` beneath the provided root, populates a `Cases` sheet (one row per case with all stem metadata and zone stats), and a `Users` sheet that summarizes zone totals per planner folder (H001/H002/H003). Install `openpyxl` via `pip install -r requirements_excel.txt` if the script asks for it.

### Batch stem screenshots

Use `batch_stem_screenshots.py` to iterate over every `seedplan.xml` in a planning root, locate the matching per-case NIfTI under an image root, and call `load_nifti_and_stem.py` headlessly for each case:

```shell
python batch_stem_screenshots.py \
   --image-root /home/developer/Projects/Code/AZDiffRadio/outputs/classif_2 \
   --planning-root /mnt/localstore1/H001 \
   --stl-folder /mnt/localstore1/Implants4EZplan \
   --case 001-M-30 --case 007-F-87 --case 011-F-54 --slicer-extra-arg=--qt-disable-translate
```

Key options:

- `--case` / `--cases-file`: restrict which case IDs to process (otherwise every seedplan under the planning root is included).
- `--slicer-extra-arg`: forward additional flags to Slicer (defaults to `--no-main-window`; drop it if you need screenshots).
- `--dry-run`: print the resolved commands without launching Slicer. Every invocation automatically enables `--compute-stem-scalars` and `--export-stem-screenshots` on the loader.
- Implant-specific rotations are applied automatically: detected Mathys stems get `--post-rotate-z-180`, while Johnson Corail/Actis stems get both `--pre-rotate-z-180` and `--post-rotate-z-180` so the loader receives the same arguments you would pass manually.
- `--exit-after-run`: close each Slicer instance automatically after its screenshots finish (handy when a GUI window would otherwise block the batch).
