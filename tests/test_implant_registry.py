"""Tests for implant_registry helper module."""

from __future__ import annotations

import unittest

import amedacta_complete as amedacta_implants
import johnson_actis_complete as johnson_actis_implants
import johnson_corail_complete as johnson_corail_implants
import mathys_implants
from implant_registry import resolve_stem_uid


class ImplantRegistryTests(unittest.TestCase):
    """Ensure implant UID lookups return consistent metadata across vendors."""

    def test_mathys_uid_is_resolved(self) -> None:
        """A Mathys stem UID should resolve to the correct metadata payload."""

        uid = mathys_implants.S3UID.STEM_STD_3.value
        lookup = resolve_stem_uid(uid)
        self.assertIsNotNone(lookup)
        assert lookup  # help type checkers
        self.assertEqual(lookup.manufacturer, "Mathys")
        self.assertEqual(lookup.enum_name, mathys_implants.S3UID.STEM_STD_3.name)
        self.assertEqual(lookup.friendly_name, lookup.enum_name.replace("_", " "))
        self.assertEqual(lookup.rcc_id, mathys_implants.get_rcc_id(mathys_implants.S3UID.STEM_STD_3))

    def test_johnson_corail_uid_is_resolved(self) -> None:
        """A Johnson & Johnson CORAIL stem UID should resolve to the correct metadata payload."""

        uid = johnson_corail_implants.S3UID.STEM_KHO_A_135_2.value
        lookup = resolve_stem_uid(uid)
        self.assertIsNotNone(lookup)
        assert lookup
        self.assertEqual(lookup.manufacturer, "Johnson & Johnson (Corail)")
        self.assertEqual(lookup.enum_name, johnson_corail_implants.S3UID.STEM_KHO_A_135_2.name)
        self.assertEqual(lookup.friendly_name, lookup.enum_name.replace("_", " "))
        self.assertEqual(
            lookup.rcc_id,
            johnson_corail_implants.get_rcc_id(johnson_corail_implants.S3UID.STEM_KHO_A_135_2),
        )

    def test_johnson_actis_uid_is_resolved(self) -> None:
        """A Johnson & Johnson ACTIS stem UID should resolve to the correct metadata payload."""

        uid = johnson_actis_implants.S3UID.STEM_STD_3.value
        lookup = resolve_stem_uid(uid)
        self.assertIsNotNone(lookup)
        assert lookup
        self.assertEqual(lookup.manufacturer, "Johnson & Johnson (Actis)")
        self.assertEqual(lookup.enum_name, johnson_actis_implants.S3UID.STEM_STD_3.name)
        self.assertEqual(lookup.friendly_name, lookup.enum_name.replace("_", " "))
        self.assertEqual(
            lookup.rcc_id,
            johnson_actis_implants.get_rcc_id(johnson_actis_implants.S3UID.STEM_STD_3),
        )

    def test_medacta_amistem_uid_is_resolved(self) -> None:
        """A Medacta AMISTEM stem UID should resolve to the correct metadata payload."""

        uid = amedacta_implants.S3UID.STEM_STD_3.value
        lookup = resolve_stem_uid(uid)
        self.assertIsNotNone(lookup)
        assert lookup
        self.assertEqual(lookup.manufacturer, "Medacta (AMISTEM)")
        self.assertEqual(lookup.enum_name, amedacta_implants.S3UID.STEM_STD_3.name)
        self.assertEqual(lookup.friendly_name, lookup.enum_name.replace("_", " "))
        self.assertEqual(
            lookup.rcc_id,
            amedacta_implants.get_rcc_id(amedacta_implants.S3UID.STEM_STD_3),
        )

    def test_unknown_uid_returns_none(self) -> None:
        """UIDs outside the managed ranges return None rather than raising."""

        self.assertIsNone(resolve_stem_uid(42))


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
    unittest.main()
