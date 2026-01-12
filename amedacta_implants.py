"""Medacta AMISTEM implant UID table translated from workbench_medacta_amistem.txt."""

from __future__ import annotations

from enum import IntEnum, auto
from typing import Dict

COMPANY_NAME = "MDCA"
COMPANY_RANGE_START_AT = 100_000
COMPANY_RANGE_END_AT = 130_000
PRODUCT_OFFSETS = {
    "QUADRA": 0,
    "VERSAFITCUPCCTRIO": 500,
    "AMISTEM": 750,
    "MINIMAX": 1_250,
}
AMISTEM_RANGE_START_AT = COMPANY_RANGE_START_AT + PRODUCT_OFFSETS["AMISTEM"]
S3UID_FIRST_OFFSET = 50


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum for AMISTEM."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return AMISTEM_RANGE_START_AT + S3UID_FIRST_OFFSET
        return last_values[-1] + 1

    STEM_STD_0 = auto()
    STEM_STD_1 = auto()
    STEM_STD_2 = auto()
    STEM_STD_3 = auto()
    STEM_STD_4 = auto()
    STEM_STD_5 = auto()
    STEM_STD_6 = auto()
    STEM_STD_7 = auto()
    STEM_STD_8 = auto()
    STEM_STD_9 = auto()
    STEM_STD_10 = auto()

    STEM_LAT_0 = auto()
    STEM_LAT_1 = auto()
    STEM_LAT_2 = auto()
    STEM_LAT_3 = auto()
    STEM_LAT_4 = auto()
    STEM_LAT_5 = auto()
    STEM_LAT_6 = auto()
    STEM_LAT_7 = auto()
    STEM_LAT_8 = auto()

    STEM_STD_SN_0 = auto()
    STEM_STD_SN_1 = auto()
    STEM_STD_SN_2 = auto()
    STEM_STD_SN_3 = auto()
    STEM_STD_SN_4 = auto()
    STEM_STD_SN_5 = auto()
    STEM_STD_SN_6 = auto()
    STEM_STD_SN_7 = auto()
    STEM_STD_SN_8 = auto()
    STEM_STD_SN_9 = auto()
    STEM_STD_SN_10 = auto()

    STEM_LAT_SN_0 = auto()
    STEM_LAT_SN_1 = auto()
    STEM_LAT_SN_2 = auto()
    STEM_LAT_SN_3 = auto()
    STEM_LAT_SN_4 = auto()
    STEM_LAT_SN_5 = auto()
    STEM_LAT_SN_6 = auto()
    STEM_LAT_SN_7 = auto()
    STEM_LAT_SN_8 = auto()

    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()
    HEAD_P12 = auto()
    RANGE_CCD_STD = auto()
    RANGE_CCD_LAT = auto()
    RANGE_CCD_STD_SN = auto()
    RANGE_CCD_LAT_SN = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_STD_0: "01_18_399",
    S3UID.STEM_STD_1: "01_18_400",
    S3UID.STEM_STD_2: "01_18_401",
    S3UID.STEM_STD_3: "01_18_402",
    S3UID.STEM_STD_4: "01_18_403",
    S3UID.STEM_STD_5: "01_18_404",
    S3UID.STEM_STD_6: "01_18_405",
    S3UID.STEM_STD_7: "01_18_406",
    S3UID.STEM_STD_8: "01_18_407",
    S3UID.STEM_STD_9: "01_18_408",
    S3UID.STEM_STD_10: "01_18_409",
    S3UID.STEM_LAT_0: "01_18_410",
    S3UID.STEM_LAT_1: "01_18_411",
    S3UID.STEM_LAT_2: "01_18_412",
    S3UID.STEM_LAT_3: "01_18_413",
    S3UID.STEM_LAT_4: "01_18_414",
    S3UID.STEM_LAT_5: "01_18_415",
    S3UID.STEM_LAT_6: "01_18_416",
    S3UID.STEM_LAT_7: "01_18_417",
    S3UID.STEM_LAT_8: "01_18_418",
    S3UID.STEM_STD_SN_0: "01_18_459",
    S3UID.STEM_STD_SN_1: "01_18_460",
    S3UID.STEM_STD_SN_2: "01_18_461",
    S3UID.STEM_STD_SN_3: "01_18_462",
    S3UID.STEM_STD_SN_4: "01_18_463",
    S3UID.STEM_STD_SN_5: "01_18_464",
    S3UID.STEM_STD_SN_6: "01_18_465",
    S3UID.STEM_STD_SN_7: "01_18_466",
    S3UID.STEM_STD_SN_8: "01_18_467",
    S3UID.STEM_STD_SN_9: "01_18_468",
    S3UID.STEM_STD_SN_10: "01_18_469",
    S3UID.STEM_LAT_SN_0: "01_18_470",
    S3UID.STEM_LAT_SN_1: "01_18_471",
    S3UID.STEM_LAT_SN_2: "01_18_472",
    S3UID.STEM_LAT_SN_3: "01_18_473",
    S3UID.STEM_LAT_SN_4: "01_18_474",
    S3UID.STEM_LAT_SN_5: "01_18_475",
    S3UID.STEM_LAT_SN_6: "01_18_476",
    S3UID.STEM_LAT_SN_7: "01_18_477",
    S3UID.STEM_LAT_SN_8: "01_18_478",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided AMISTEM UID."""

    try:
        return RCC_ID_NAME[uid]
    except KeyError as exc:
        raise KeyError(f"No RCC identifier configured for {uid.name}") from exc


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
