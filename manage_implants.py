"""Python translation of the implant UID table defined in workbench.txt."""

from __future__ import annotations

from enum import IntEnum, auto
from typing import Dict

MYS_RANGE_START_AT = 130_000 + 500


class S3UID(IntEnum):
	"""Integer UIDs mirroring the C++ S3UID enum."""

	def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
		if not last_values:
			return MYS_RANGE_START_AT
		return last_values[-1] + 1

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
	STEM_STD_13 = auto()
	STEM_STD_14 = auto()
	STEM_LAT_1 = auto()
	STEM_LAT_2 = auto()
	STEM_LAT_3 = auto()
	STEM_LAT_4 = auto()
	STEM_LAT_5 = auto()
	STEM_LAT_6 = auto()
	STEM_LAT_7 = auto()
	STEM_LAT_8 = auto()
	STEM_LAT_9 = auto()
	STEM_LAT_10 = auto()
	STEM_LAT_11 = auto()
	STEM_LAT_12 = auto()
	STEM_LAT_13 = auto()
	STEM_LAT_14 = auto()
	CUTPLANE = auto()
	HEAD_M4 = auto()
	HEAD_P0 = auto()
	HEAD_P4 = auto()
	HEAD_P8 = auto()
	RANGE_CCD_STD = auto()
	RANGE_CCD_LAT = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
	S3UID.STEM_STD_1: "52_34_1165_50024772_V02",
	S3UID.STEM_STD_2: "52_34_1166_50028325_V03",
	S3UID.STEM_STD_3: "52_34_0191_10092331_V01",
	S3UID.STEM_STD_4: "52_34_0192_10092332_V01",
	S3UID.STEM_STD_5: "52_34_0193_10092333_V01",
	S3UID.STEM_STD_6: "52_34_0194_10092334_V01",
	S3UID.STEM_STD_7: "52_34_0195_10092335_V01",
	S3UID.STEM_STD_8: "52_34_0196_10092336_V01",
	S3UID.STEM_STD_9: "52_34_0197_10092337_V01",
	S3UID.STEM_STD_10: "52_34_0198_10092338_V01",
	S3UID.STEM_STD_11: "52_34_0199_10092339_V01",
	S3UID.STEM_STD_12: "52_34_0200_10092340_V01",
	S3UID.STEM_STD_13: "52_34_0211_10092351_V03",
	S3UID.STEM_STD_14: "52_34_0212_10092352_V03",
	S3UID.STEM_LAT_1: "52_34_1167_50028427_V02",
	S3UID.STEM_LAT_2: "52_34_1168_50028426_V02",
	S3UID.STEM_LAT_3: "52_34_0201_10092341_V01",
	S3UID.STEM_LAT_4: "52_34_0202_10092342_V01",
	S3UID.STEM_LAT_5: "52_34_0203_10092343_V01",
	S3UID.STEM_LAT_6: "52_34_0204_10092344_V01",
	S3UID.STEM_LAT_7: "52_34_0205_10092345_V01",
	S3UID.STEM_LAT_8: "52_34_0206_10092346_V01",
	S3UID.STEM_LAT_9: "52_34_0207_10092347_V01",
	S3UID.STEM_LAT_10: "52_34_0208_10092348_V01",
	S3UID.STEM_LAT_11: "52_34_0209_10092349_V01",
	S3UID.STEM_LAT_12: "52_34_0210_10092350_V01",
	S3UID.STEM_LAT_13: "52_34_0221_10092361_V03",
	S3UID.STEM_LAT_14: "52_34_0222_10092362_V03",
}


def get_rcc_id(uid: S3UID) -> str:
	"""Return the RCC identifier for the provided UID."""

	return RCC_ID_NAME[uid]


__all__ = ["MYS_RANGE_START_AT", "S3UID", "RCC_ID_NAME", "get_rcc_id"]
