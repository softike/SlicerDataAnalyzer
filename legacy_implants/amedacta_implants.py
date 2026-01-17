"""Backward-compatible shim that re-exports :mod:`amedacta_complete` symbols."""

from __future__ import annotations

from amedacta_complete import (  # re-export
    AMISTEM_RANGE_START_AT,
    COMPANY_NAME,
    COMPANY_RANGE_END_AT,
    COMPANY_RANGE_START_AT,
    PRODUCT_OFFSETS,
    RCC_ID_NAME,
    S3UID,
    S3UID_FIRST_OFFSET,
    get_rcc_id,
)

__all__ = [
    "COMPANY_NAME",
    "COMPANY_RANGE_START_AT",
    "COMPANY_RANGE_END_AT",
    "PRODUCT_OFFSETS",
    "AMISTEM_RANGE_START_AT",
    "S3UID_FIRST_OFFSET",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
]
