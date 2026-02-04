# Recommended Project Structure

This document proposes a refactored directory structure for the SlicerDataAnalyzer project.

## Proposed Structure

```
SlicerDataAnalyzer/
├── pyproject.toml              # Modern Python packaging
├── README.md                   # User-facing documentation
├── LICENSE                     # License file (if not present)
├── .gitignore                  # Comprehensive gitignore
├── .gitattributes              # Git attributes for line endings
├── .pre-commit-config.yaml     # Pre-commit hooks configuration
├── Makefile                    # Common development tasks
├── docker-compose.yml          # Optional: containerized setup
│
├── src/
│   └── slicer_analyzer/        # Main package (src-layout)
│       ├── __init__.py
│       ├── __version__.py      # Version info
│       ├── config.py           # Configuration management
│       ├── logging_config.py   # Structured logging setup
│       │
│       ├── core/               # Core business logic
│       │   ├── __init__.py
│       │   ├── xml_parser.py   # XML parsing utilities
│       │   ├── matrix_utils.py # Matrix/vector operations
│       │   ├── geometry.py     # 3D geometry calculations
│       │   ├── data_models.py  # Dataclasses for planning data
│       │   └── validation.py   # Input validation
│       │
│       ├── implants/           # Implant-related modules
│       │   ├── __init__.py
│       │   ├── registry.py     # Implant registry (from implant_registry.py)
│       │   ├── loader.py       # Stem loading logic
│       │   ├── manufacturers/  # Per-manufacturer modules
│       │   │   ├── __init__.py
│       │   │   ├── mathys.py   # Was: mathys_optimys_complete.py
│       │   │   ├── johnson.py  # Was: johnson_corail_complete.py
│       │   │   ├── medacta.py  # Was: amedacta_complete.py
│       │   │   ├── implantcast.py
│       │   │   └── lima.py
│       │   └── schemas/        # Data schemas
│       │       ├── __init__.py
│       │       └── stem.py     # Stem dataclass definitions
│       │
│       ├── comparison/         # Data comparison logic
│       │   ├── __init__.py
│       │   ├── engine.py       # Comparison algorithms
│       │   ├── batch.py        # Batch processing
│       │   ├── inter_rater.py  # Inter-rater reliability
│       │   └── stats.py        # Statistical calculations
│       │
│       ├── slicer/             # 3D Slicer integration
│       │   ├── __init__.py
│       │   ├── launcher.py     # Slicer process management
│       │   ├── scripts/        # Embedded Slicer scripts
│       │   │   ├── __init__.py
│       │   │   └── load_stem.py  # Template for load_nifti_and_stem.py
│       │   └── io/             # File I/O
│       │       ├── __init__.py
│       │       ├── nifti.py    # NIfTI handling
│       │       └── stl.py      # STL mesh handling
│       │
│       ├── export/             # Output generation
│       │   ├── __init__.py
│       │   ├── base.py         # Export base classes
│       │   ├── html.py         # HTML report generation
│       │   ├── pdf.py          # PDF export
│       │   ├── excel.py        # Excel export
│       │   └── plots.py        # Matplotlib plot generation
│       │
│       └── cli/                # Command-line interfaces
│           ├── __init__.py
│           ├── compare.py      # compareResults_3Studies.py logic
│           ├── batch_compare.py # batchCompareStudies.py logic
│           ├── load_stem.py    # load_nifti_and_stem.py logic
│           ├── view_implant.py # view_implant.py logic
│           └── batch_stem.py   # batch_stem_analysis.py logic
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── unit/
│   │   ├── test_matrix_utils.py
│   │   ├── test_xml_parser.py
│   │   ├── test_anteversion.py
│   │   ├── test_implant_registry.py
│   │   └── test_validation.py
│   ├── integration/
│   │   ├── test_batch_processing.py
│   │   ├── test_comparison.py
│   │   └── test_exports.py
│   ├── fixtures/
│   │   ├── sample_seedplan.xml
│   │   ├── sample_nifti.nii.gz
│   │   └── sample_stem.stl
│   └── e2e/
│       └── test_full_pipeline.py
│
├── docs/
│   ├── index.md
│   ├── architecture.md
│   ├── development.md
│   ├── clinical-validation.md
│   ├── api/
│   │   └── (auto-generated)
│   ├── examples/
│   │   ├── basic-usage.md
│   │   ├── batch-processing.md
│   │   └── custom-analysis.md
│   └── changelog.md
│
├── scripts/
│   ├── setup_dev_env.sh        # Development environment setup
│   └── run_tests.sh            # Test runner script
│
├── config/
│   ├── default.yaml            # Default configuration
│   └── logging.yaml            # Logging configuration
│
└── data/                       # Sample/test data (not in git)
    ├── examples/               # Small example files
    └── tests/                  # Test fixtures (if large)
```

## Migration Strategy

### Phase 1: Setup (Week 1)

1. **Create new structure:**
```bash
mkdir -p src/slicer_analyzer/{core,implants,comparison,slicer,export,cli}
mkdir -p tests/{unit,integration,e2e,fixtures}
mkdir -p docs/{api,examples}
```

2. **Move files incrementally:**
```bash
# Move implant registry (clean, well-structured)
cp implant_registry.py src/slicer_analyzer/implants/registry.py

# Move manufacturer modules
cp mathys_optimys_complete.py src/slicer_analyzer/implants/manufacturers/mathys.py
cp johnson_corail_complete.py src/slicer_analyzer/implants/manufacturers/johnson.py
# ... etc
```

3. **Update imports:**
```python
# Old
import implant_registry

# New
from slicer_analyzer.implants import registry as implant_registry
```

### Phase 2: Extract Core Logic (Week 2-3)

Break down monolithic scripts into modules:

**From `compareResults_3Studies.py`:**
- Extract XML parsing → `core/xml_parser.py`
- Extract matrix operations → `core/matrix_utils.py`
- Extract plot generation → `export/plots.py`
- Extract HTML generation → `export/html.py`
- Keep CLI logic in `cli/compare.py`

**Example extraction:**
```python
# core/xml_parser.py
from dataclasses import dataclass
from typing import Dict, Optional, List
import xml.etree.ElementTree as ET
from pathlib import Path

@dataclass
class PlanningData:
    matrices: Dict[str, str]
    vectors: Dict[str, str]
    scalars: Dict[str, str]
    patient_side: Optional[str] = None

class SeedplanParser:
    TAGS_XPATHS: List[tuple] = [
        ("S3FemoralSphere_R_matrix", ".//s3Shape[@name='S3FemoralSphere_R']/matrix4[@name='mat']"),
        # ... other tags
    ]
    
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.tree = ET.parse(file_path)
        self.root = self.tree.getroot()
    
    def parse(self) -> PlanningData:
        data = PlanningData(matrices={}, vectors={}, scalars={})
        
        for tag, xpath in self.TAGS_XPATHS:
            elem = self.root.find(xpath)
            if elem is not None and 'value' in elem.attrib:
                value = elem.attrib['value']
                if tag.endswith('_matrix'):
                    data.matrices[tag] = value
                elif tag.endswith(('_p0', '_p1')):
                    data.vectors[tag] = value
                elif tag.endswith('_diameter'):
                    data.scalars[tag] = value
        
        return data
    
    def get_patient_side(self) -> Optional[str]:
        side_elem = self.root.find(".//PatientSide")
        if side_elem is not None and side_elem.text:
            side = side_elem.text.strip().lower()
            if side in ['left', 'l']:
                return 'Left'
            elif side in ['right', 'r']:
                return 'Right'
        return None
```

### Phase 3: Testing (Week 4-5)

Add tests as you refactor:

```python
# tests/unit/test_xml_parser.py
import pytest
from pathlib import Path
from slicer_analyzer.core.xml_parser import SeedplanParser

FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures'

class TestSeedplanParser:
    def test_parse_valid_seedplan(self):
        parser = SeedplanParser(FIXTURES_DIR / 'sample_seedplan.xml')
        data = parser.parse()
        
        assert 'S3FemoralSphere_R_matrix' in data.matrices
        assert len(data.matrices) > 0
    
    def test_get_patient_side_right(self):
        # Create temp XML with Right side
        # ...
        parser = SeedplanParser(temp_path)
        assert parser.get_patient_side() == 'Right'
    
    def test_parse_missing_file(self):
        with pytest.raises(FileNotFoundError):
            SeedplanParser(Path('/nonexistent/file.xml'))
```

## Benefits of New Structure

1. **Separation of concerns:** CLI, core logic, and exports are distinct
2. **Testability:** Each module can be tested independently
3. **Reusability:** Core modules can be imported without CLI overhead
4. **Maintainability:** Smaller, focused files are easier to understand
5. **Discoverability:** Clear organization helps new developers
6. **Packaging:** Proper `src/` layout enables proper Python packaging

## Configuration with pyproject.toml

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "slicer-analyzer"
dynamic = ["version"]
description = "Medical imaging analysis tool for hip implant planning"
readme = "README.md"
license = {text = "MIT"}  # Or appropriate license
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "your.email@example.com"}
]
keywords = ["medical", "imaging", "hip", "implant", "slicer"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Science/Research",
    "Topic :: Scientific/Engineering :: Medical Science Apps.",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "numpy>=1.24.0",
    "matplotlib>=3.7.0",
    "scipy>=1.10.0",
    "vtk>=9.2.0",
    "pandas>=2.0.0",
    "openpyxl>=3.1.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    "structlog>=23.0.0",
    "rich>=13.0.0",  # For CLI output
]

[project.optional-dependencies]
pdf = ["weasyprint>=59.0"]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-mock>=3.11.0",
    "mypy>=1.5.0",
    "ruff>=0.1.0",
    "black>=23.0.0",
    "pre-commit>=3.4.0",
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
    "mkdocstrings[python]>=0.22.0",
]

[project.scripts]
slicer-compare = "slicer_analyzer.cli.compare:main"
slicer-batch = "slicer_analyzer.cli.batch_compare:main"
slicer-load-stem = "slicer_analyzer.cli.load_stem:main"
slicer-view-implant = "slicer_analyzer.cli.view_implant:main"

[project.urls]
Homepage = "https://github.com/yourorg/slicer-analyzer"
Documentation = "https://slicer-analyzer.readthedocs.io"
Repository = "https://github.com/yourorg/slicer-analyzer"
Issues = "https://github.com/yourorg/slicer-analyzer/issues"

[tool.hatch.version]
path = "src/slicer_analyzer/__version__.py"

[tool.hatch.build.targets.wheel]
packages = ["src/slicer_analyzer"]

[tool.black]
line-length = 100
target-version = ['py310']

[tool.ruff]
line-length = 100
target-version = "py310"
select = ["E", "F", "I", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --cov=slicer_analyzer --cov-report=term-missing"
```

## Migration Checklist

- [ ] Create new directory structure
- [ ] Set up `pyproject.toml`
- [ ] Move `implant_registry.py` → `implants/registry.py`
- [ ] Move manufacturer modules → `implants/manufacturers/`
- [ ] Extract XML parsing → `core/xml_parser.py`
- [ ] Extract matrix utilities → `core/matrix_utils.py`
- [ ] Extract plot generation → `export/plots.py`
- [ ] Extract HTML generation → `export/html.py`
- [ ] Extract Excel export → `export/excel.py`
- [ ] Move CLI logic → `cli/` modules
- [ ] Update all imports
- [ ] Add `__init__.py` files with exports
- [ ] Set up pytest configuration
- [ ] Write tests for core modules
- [ ] Update README with new usage
- [ ] Verify all scripts still work
- [ ] Remove old files
- [ ] Update `.gitignore`
- [ ] Set up pre-commit hooks

## Notes

- Keep old files until new structure is fully tested
- Use `git mv` when moving files to preserve history
- Consider using `traitlets` or similar for configuration if needed
- Document breaking changes in CHANGELOG.md
