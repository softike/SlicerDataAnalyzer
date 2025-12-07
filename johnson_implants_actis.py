"""Johnson & Johnson ACTIS implant UID table translated from workbench_jnjds_actis.txt."""

from __future__ import annotations

from enum import IntEnum, auto
from typing import Dict

COMPANY_RANGE_START_AT = 160_000
PRODUCT_RANGE_START_AT = COMPANY_RANGE_START_AT + 1_250  # ACTIS product family offset
JJ_RANGE_START_AT = PRODUCT_RANGE_START_AT + 90  # per workbench offset


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum for ACTIS."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return JJ_RANGE_START_AT
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
    STEM_STD_11 = auto()
    STEM_STD_12 = auto()

    STEM_HO_0 = auto()
    STEM_HO_1 = auto()
    STEM_HO_2 = auto()
    STEM_HO_3 = auto()
    STEM_HO_4 = auto()
    STEM_HO_5 = auto()
    STEM_HO_6 = auto()
    STEM_HO_7 = auto()
    STEM_HO_8 = auto()
    STEM_HO_9 = auto()
    STEM_HO_10 = auto()
    STEM_HO_11 = auto()
    STEM_HO_12 = auto()

    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()
    RANGE_CCD_STD = auto()
    RANGE_CCD_HO = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_STD_0: "103794036_1",
    S3UID.STEM_STD_1: "103533729_1",
    S3UID.STEM_STD_2: "103534115_1",
    S3UID.STEM_STD_3: "103534118_1",
    S3UID.STEM_STD_4: "103534120_1",
    S3UID.STEM_STD_5: "103534121_1",
    S3UID.STEM_STD_6: "103534123_1",
    S3UID.STEM_STD_7: "103534124_1",
    S3UID.STEM_STD_8: "103534125_1",
    S3UID.STEM_STD_9: "103534127_1",
    S3UID.STEM_STD_10: "103534129_1",
    S3UID.STEM_STD_11: "103534132_1",
    S3UID.STEM_STD_12: "103534133_1",
    S3UID.STEM_HO_0: "103794037_1",
    S3UID.STEM_HO_1: "103534134_1",
    S3UID.STEM_HO_2: "103534135_1",
    S3UID.STEM_HO_3: "103534138_1",
    S3UID.STEM_HO_4: "103534139_1",
    S3UID.STEM_HO_5: "103534144_1",
    S3UID.STEM_HO_6: "103534146_1",
    S3UID.STEM_HO_7: "103534147_1",
    S3UID.STEM_HO_8: "103534972_1",
    S3UID.STEM_HO_9: "103534973_1",
    S3UID.STEM_HO_10: "103534974_1",
    S3UID.STEM_HO_11: "103534976_1",
    S3UID.STEM_HO_12: "103534977_1",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided ACTIS UID."""

    return RCC_ID_NAME[uid]


__all__ = [
    "COMPANY_RANGE_START_AT",
    "PRODUCT_RANGE_START_AT",
    "JJ_RANGE_START_AT",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
]
