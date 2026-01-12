"""Tests for the stem extraction helper used by batchCompareStudies."""

from __future__ import annotations

from pathlib import Path
import unittest

from batchCompareStudies import extract_stem_info_from_xml


class ExtractStemInfoTests(unittest.TestCase):
    """Validate that multi-configuration seedplans are parsed correctly."""

    @classmethod
    def setUpClass(cls) -> None:
        repo_root = Path(__file__).resolve().parent.parent
        cls.seedplan_path = repo_root / "planning_multiconfig" / "seedplan.xml"

    def test_multiple_configurations_are_returned(self) -> None:
        """Ensure every hipImplantConfig is surfaced with ordering and metadata."""

        entries = extract_stem_info_from_xml(str(self.seedplan_path))
        self.assertGreater(len(entries), 1)

        indices = [entry.get("hip_config_index") for entry in entries if entry.get("hip_config_index") is not None]
        self.assertEqual(indices, sorted(indices))

        sources = {entry.get("source") for entry in entries if entry.get("source")}
        self.assertIn("active", sources)
        self.assertIn("history", sources)

        names = [entry.get("hip_config_name") or "" for entry in entries]
        self.assertTrue(any("CORAIL KA 135" in name for name in names))

        matrices = [entry for entry in entries if entry.get("matrix_raw")]
        self.assertTrue(matrices)
        self.assertTrue(matrices[0].get("rotation"))
        self.assertIn("Tx", matrices[0].get("translation", {}))

    def test_parse_error_is_reported(self) -> None:
        """Bad input paths should return a single entry with an error message."""

        bogus_path = str(self.seedplan_path.with_name("missing_seedplan.xml"))
        entries = extract_stem_info_from_xml(bogus_path)
        self.assertEqual(len(entries), 1)
        self.assertIn("parse_error", entries[0].get("error", ""))


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
    unittest.main()
