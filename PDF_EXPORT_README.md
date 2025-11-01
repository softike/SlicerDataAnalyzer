# PDF Export Feature

This tool now supports exporting reports to PDF format in addition to HTML.

## Installation

To use PDF export functionality, install the required dependencies:

```bash
pip install -r requirements_pdf.txt
```

Or install individually:

```bash
# Recommended: weasyprint (no external dependencies)
pip install weasyprint

# Alternative: pdfkit (requires wkhtmltopdf)
pip install pdfkit
# Plus system package: sudo apt-get install wkhtmltopdf
```

## Usage

Add the `--pdf` flag to any command to also generate a PDF report:

### Single file analysis with PDF export:
```bash
python compareResults_3Studies.py --xml_path planning.xml --pdf
```

### Three-file comparison with PDF export:
```bash
python compareResults_3Studies.py --compare plan1.xml plan2.xml plan3.xml --pdf
```

### Custom output filename with PDF:
```bash
python compareResults_3Studies.py --xml_path planning.xml --output my_analysis --pdf
```

## PDF Export Methods

The tool tries multiple PDF generation methods in order:

1. **weasyprint** (recommended): Pure Python, handles HTML/CSS well
2. **pdfkit**: Requires wkhtmltopdf system package, good HTML rendering
3. **matplotlib fallback**: Creates plot-only PDF if web libraries unavailable

## Output Files

When using `--pdf` flag, you'll get:
- `.html` file: Full interactive report with styling
- `.pdf` file: PDF version of the report
- `.png` file: High-resolution plots

## Troubleshooting

If PDF export fails:

1. Install weasyprint: `pip install weasyprint`
2. Or install pdfkit + wkhtmltopdf: 
   ```bash
   pip install pdfkit
   sudo apt-get install wkhtmltopdf  # Linux
   brew install wkhtmltopdf          # macOS
   ```
3. Fallback to matplotlib plots: The tool will create plot-only PDFs if web libraries are unavailable