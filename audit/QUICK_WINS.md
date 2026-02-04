# Quick Wins - Immediate Improvements

This document contains actionable improvements that can be implemented immediately with minimal risk.

---

## 1. Add .gitignore (5 minutes)

Create `.gitignore` at project root:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/
*.egg
.pytest_cache/
.mypy_cache/
.ruff_cache/
.hypothesis/
.coverage
*.cover
*.py,cover
.tox/
.nox/

# IDEs
.vscode/settings.json
.vscode/*.log
.idea/
*.swp
*.swo
*~
.DS_Store

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Project-specific outputs
*.tar.gz
*.nii.gz
*.vtp
*.vtu
*.mrb
*.mrml
*.png
*.jpg
*.jpeg
*.pdf
*.xlsx
*.ods

# Generated directories
CurrentReports/*
!CurrentReports/.gitkeep
Slicer-exports/
excel_export/*.xlsx
excel_export/*.ods

# Logs
*.log

# Local configuration
local_config.py
local_settings.py
```

Then remove cached files:
```bash
git rm -r --cached __pycache__ .pytest_cache
```

---

## 2. Add Requirements Files (10 minutes)

### requirements.txt
```
numpy>=1.24.0,<2.0.0
matplotlib>=3.7.0
scipy>=1.10.0
vtk>=9.2.0
pandas>=2.0.0
openpyxl>=3.1.0
pillow>=10.0.0
```

### requirements-pdf.txt
```
-r requirements.txt
weasyprint>=59.0
```

### requirements-dev.txt
```
-r requirements.txt
pytest>=7.4.0
pytest-cov>=4.1.0
mypy>=1.5.0
ruff>=0.1.0
black>=23.0.0
pre-commit>=3.4.0
```

---

## 3. Add Pre-commit Hooks (15 minutes)

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
        args: ['--maxkb=1000']
      - id: check-merge-conflict
      - id: debug-statements

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.10

  - repo: https://github.com/charliermarsh/ruff-pre-commit
    rev: v0.1.8
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.1
    hooks:
      - id: mypy
        additional_dependencies: [types-all]
```

Install:
```bash
pip install pre-commit
pre-commit install
```

---

## 4. Add Structured Logging (20 minutes)

Create `logging_config.py`:

```python
import logging
import sys
from pathlib import Path
from datetime import datetime

def setup_logging(log_dir: Path = Path("logs"), level: int = logging.INFO) -> None:
    """Configure structured logging for the application."""
    log_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"slicer_analyzer_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Reduce noise from third-party libraries
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)

# Usage in scripts:
# from logging_config import setup_logging
# setup_logging()
# logger = logging.getLogger(__name__)
# logger.info("Processing case: %s", case_id)
```

---

## 5. Create a Makefile (10 minutes)

Create `Makefile`:

```makefile
.PHONY: help install install-dev test lint format clean setup

help:
	@echo "Available targets:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and ruff"
	@echo "  clean        - Remove cache files and build artifacts"
	@echo "  setup        - Setup development environment"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements-dev.txt
	pre-commit install

test:
	pytest tests/ -v

test-cov:
	pytest tests/ -v --cov=. --cov-report=term-missing --cov-report=html

lint:
	ruff check .
	mypy . --ignore-missing-imports

format:
	black . --line-length 100
	ruff check . --fix

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/

setup: install-dev
	@echo "Development environment setup complete!"
```

---

## 6. Add Type Hints to Critical Functions (30 minutes)

Start with the most critical functions in `implant_registry.py`:

```python
"""Lookup utilities for implant stems across supported vendors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol, runtime_checkable
from enum import Enum

# Define protocol for implant modules
@runtime_checkable
class ImplantModule(Protocol):
    class S3UID(Enum):
        pass
    
    @staticmethod
    def get_rcc_id(uid) -> Optional[str]:
        ...


@dataclass(frozen=True)
class StemLookupResult:
    """Structured metadata for a resolved implant stem UID."""
    uid: int
    manufacturer: str
    enum_name: str
    friendly_name: str
    rcc_id: Optional[str]


def _friendly_enum_name(enum_name: str) -> str:
    """Convert an internal enum constant to a readable label."""
    return enum_name.replace("_", " ").strip()


def resolve_stem_uid(uid: Optional[int]) -> Optional[StemLookupResult]:
    """Return vendor metadata for the provided implant stem UID, if known.
    
    Args:
        uid: The implant stem UID to look up
        
    Returns:
        StemLookupResult with metadata, or None if not found
        
    Example:
        >>> result = resolve_stem_uid(130506)
        >>> if result:
        ...     print(f"Found: {result.manufacturer} - {result.friendly_name}")
    """
    if uid is None:
        return None
    
    lookup_table: tuple[tuple[str, type, callable], ...] = (
        ("Medacta (AMISTEM)", mdca_amistem_implants.S3UID, mdca_amistem_implants.get_rcc_id),
        ("Mathys", mys_implants.S3UID, mys_implants.get_rcc_id),
        ("Johnson & Johnson (Corail)", jj_corail_implants.S3UID, jj_corail_implants.get_rcc_id),
        ("Johnson & Johnson (Actis)", jj_actis_implants.S3UID, jj_actis_implants.get_rcc_id),
        ("Implantcast (Ecofit)", icast_ecofit_implants.S3UID, icast_ecofit_implants.get_rcc_id),
        ("Lima (FIT)", lima_fit_implants.S3UID, lima_fit_implants.get_rcc_id),
    )
    
    for manufacturer, enum_cls, get_rcc in lookup_table:
        try:
            enum_member = enum_cls(uid)
        except ValueError:
            continue
        
        rcc_id: Optional[str] = None
        try:
            rcc_id = get_rcc(enum_member)
        except (KeyError, AttributeError):
            rcc_id = None
        
        return StemLookupResult(
            uid=uid,
            manufacturer=manufacturer,
            enum_name=enum_member.name,
            friendly_name=_friendly_enum_name(enum_member.name),
            rcc_id=rcc_id,
        )
    
    return None
```

---

## 7. Add a Simple Test (15 minutes)

Create `tests/unit/test_implant_registry.py`:

```python
"""Tests for implant registry functionality."""

import pytest
from implant_registry import resolve_stem_uid, StemLookupResult


class TestResolveStemUid:
    """Test cases for resolve_stem_uid function."""
    
    def test_returns_none_for_none_input(self):
        """Should return None when uid is None."""
        result = resolve_stem_uid(None)
        assert result is None
    
    def test_returns_none_for_invalid_uid(self):
        """Should return None for unknown UID."""
        result = resolve_stem_uid(999999)
        assert result is None
    
    def test_returns_result_for_valid_mathys_uid(self):
        """Should return correct metadata for Mathys UID."""
        result = resolve_stem_uid(130506)  # STEM_STD_1
        
        assert result is not None
        assert result.uid == 130506
        assert "Mathys" in result.manufacturer
        assert result.enum_name == "STEM_STD_1"
        assert result.friendly_name == "STEM STD 1"
    
    def test_returns_result_for_valid_medacta_uid(self):
        """Should return correct metadata for Medacta AMISTEM UID."""
        result = resolve_stem_uid(190001)  # Example AMISTEM UID
        
        assert result is not None
        assert "Medacta" in result.manufacturer
        assert "AMISTEM" in result.manufacturer
    
    def test_result_is_frozen_dataclass(self):
        """Result should be immutable."""
        result = resolve_stem_uid(130506)
        
        with pytest.raises(AttributeError):
            result.uid = 123456


class TestStemLookupResult:
    """Test StemLookupResult dataclass."""
    
    def test_creation(self):
        """Should create instance with all fields."""
        result = StemLookupResult(
            uid=123,
            manufacturer="Test",
            enum_name="TEST_ENUM",
            friendly_name="Test Enum",
            rcc_id="RCC123"
        )
        
        assert result.uid == 123
        assert result.rcc_id == "RCC123"
    
    def test_creation_with_optional_none(self):
        """Should create instance with optional fields as None."""
        result = StemLookupResult(
            uid=123,
            manufacturer="Test",
            enum_name="TEST_ENUM",
            friendly_name="Test Enum",
            rcc_id=None
        )
        
        assert result.rcc_id is None
```

Add `tests/conftest.py`:

```python
"""pytest configuration and fixtures."""

import pytest
from pathlib import Path

# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / 'fixtures'


@pytest.fixture
def sample_seedplan_path() -> Path:
    """Return path to sample seedplan XML."""
    return FIXTURES_DIR / 'sample_seedplan.xml'


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to fixtures directory."""
    return FIXTURES_DIR
```

Run the test:
```bash
pytest tests/unit/test_implant_registry.py -v
```

---

## 8. Add a README Badge (5 minutes)

Add to `README.md` at the top:

```markdown
# Slicer Data Analyzer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Setup for Slicer related development with Python...
```

---

## 9. Create a CHANGELOG (10 minutes)

Create `CHANGELOG.md`:

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Structured logging configuration
- Pre-commit hooks for code quality
- Type hints for critical functions
- Unit tests for implant registry

### Changed
- Updated .gitignore to exclude generated files
- Added requirements files with version constraints

## [0.1.0] - 2024-XX-XX

### Added
- Initial release with core functionality
- Support for multiple implant manufacturers (Mathys, Johnson & Johnson, Medacta, Implantcast, Lima)
- Batch comparison across H001/H002/H003 operators
- HTML and PDF report generation
- Excel export with detailed component breakdown
- Femoral anteversion angle calculation
- Slicer integration for NIfTI loading and stem visualization
```

---

## 10. Add a Simple CI Configuration (15 minutes)

Create `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements-dev.txt
    
    - name: Lint with ruff
      run: ruff check . --output-format=github
    
    - name: Type check with mypy
      run: mypy . --ignore-missing-imports || true
    
    - name: Test with pytest
      run: pytest tests/ -v --cov=. --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: false
```

---

## Summary

These 10 quick wins can be implemented in about 2-3 hours total:

| Task | Time | Priority |
|------|------|----------|
| 1. Add .gitignore | 5 min | Critical |
| 2. Add requirements files | 10 min | High |
| 3. Add pre-commit hooks | 15 min | High |
| 4. Add structured logging | 20 min | Medium |
| 5. Create Makefile | 10 min | Low |
| 6. Add type hints | 30 min | High |
| 7. Add a simple test | 15 min | Critical |
| 8. Add README badge | 5 min | Low |
| 9. Create CHANGELOG | 10 min | Medium |
| 10. Add CI configuration | 15 min | Medium |

**Total: ~2.5 hours**

These changes will:
- ✅ Improve code quality immediately
- ✅ Prevent cache files from being committed
- ✅ Enable automated testing
- ✅ Provide better debugging with structured logging
- ✅ Catch type errors early
- ✅ Establish a foundation for further improvements
