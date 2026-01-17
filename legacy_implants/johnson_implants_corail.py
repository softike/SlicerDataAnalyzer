"""Backward-compatible shim that re-exports :mod:`johnson_corail_complete`."""

from __future__ import annotations

from johnson_corail_complete import (  # re-export
    COMPANY_RANGE_START_AT,
    JJ_RANGE_START_AT,
    PRODUCT_RANGE_START_AT,
    RCC_ID_NAME,
    S3UID,
    get_rcc_id,
)

__all__ = [
    "COMPANY_RANGE_START_AT",
    "PRODUCT_RANGE_START_AT",
    "JJ_RANGE_START_AT",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
]
