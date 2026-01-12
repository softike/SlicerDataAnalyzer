"""Tests for amedacta_implants module."""

from __future__ import annotations

import unittest

import amedacta_implants
from amedacta_implants import (
    AMISTEM_RANGE_START_AT,
    RCC_ID_NAME,
    S3UID,
    S3UID_FIRST_OFFSET,
    get_rcc_id,
)


class MedactaAmistemImplantsTests(unittest.TestCase):
    """Unit tests ensuring the Medacta AMISTEM table matches the workbench source."""

    def test_s3uid_values_are_contiguous(self) -> None:
        """Enum members should form a contiguous increasing block starting from the first offset."""

        members = list(S3UID)
        first_value = AMISTEM_RANGE_START_AT + S3UID_FIRST_OFFSET
        self.assertEqual(members[0].value, first_value)
        expected_values = list(range(first_value, first_value + len(members)))
        self.assertEqual([member.value for member in members], expected_values)

    def test_get_rcc_id_matches_reference_table(self) -> None:
        """Every mapped UID should return the RCC identifier from the reference table."""

        for uid, expected_rcc in RCC_ID_NAME.items():
            self.assertEqual(get_rcc_id(uid), expected_rcc)

    def test_get_rcc_id_missing_uid_raises_key_error(self) -> None:
        """Calling get_rcc_id on unmapped enums should raise KeyError for visibility."""

        with self.assertRaises(KeyError):
            get_rcc_id(S3UID.CUTPLANE)

    def test_public_api_contract(self) -> None:
        """__all__ must advertise the supported surface for downstream consumers."""

        self.assertEqual(
            set(amedacta_implants.__all__),
            {
                "COMPANY_NAME",
                "COMPANY_RANGE_START_AT",
                "COMPANY_RANGE_END_AT",
                "PRODUCT_OFFSETS",
                "AMISTEM_RANGE_START_AT",
                "S3UID_FIRST_OFFSET",
                "S3UID",
                "RCC_ID_NAME",
                "get_rcc_id",
            },
        )


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
    unittest.main()
