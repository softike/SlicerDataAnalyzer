"""Tests for mathys_implants module."""

from __future__ import annotations

import unittest

import mathys_implants
from mathys_implants import (
	MYS_RANGE_START_AT,
	RCC_ID_NAME,
	S3UID,
	get_rcc_id,
)


class MathysImplantsTests(unittest.TestCase):
	"""Unit tests that mirror the original C++ table semantics."""

	def test_s3uid_values_are_contiguous(self) -> None:
		"""All enum members should be numbered sequentially from the base value."""

		members = list(S3UID)
		self.assertEqual(members[0].value, MYS_RANGE_START_AT)
		expected_values = list(range(MYS_RANGE_START_AT, MYS_RANGE_START_AT + len(members)))
		self.assertEqual([member.value for member in members], expected_values)

	def test_get_rcc_id_matches_reference_table(self) -> None:
		"""The helper must mirror the C++ lookup table for every known UID."""

		for uid, expected_rcc in RCC_ID_NAME.items():
			self.assertEqual(get_rcc_id(uid), expected_rcc)

	def test_get_rcc_id_missing_uid_raises_key_error(self) -> None:
		"""Querying an unmapped UID should propagate the dict KeyError."""

		with self.assertRaises(KeyError):
			get_rcc_id(S3UID.CUTPLANE)

	def test_public_api_contract(self) -> None:
		"""__all__ should expose the curated surface of the module."""

		required = {"MYS_RANGE_START_AT", "S3UID", "RCC_ID_NAME", "get_rcc_id"}
		self.assertTrue(required.issubset(set(mathys_implants.__all__)))


if __name__ == "__main__":  # pragma: no cover - convenience for direct execution
	unittest.main()
