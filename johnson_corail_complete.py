"""Utilities reconstructed from ``johnson_corail_scheme.h`` for CORAIL stems.

The Johnson & Johnson CORAIL catalog exposes numerous stem families that were
originally encoded inside a Qt plugin.  This module mirrors the UID table from
:mod:`johnson_implants_corail` and layers on top the geometric helpers that were
previously only available in C++.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Mapping, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "JNJ"
PRODUCT_NAME = "CORAIL"
COMPANY_RANGE_START_AT = 160_000
PRODUCT_RANGE_START_AT = COMPANY_RANGE_START_AT
JJ_RANGE_START_AT = PRODUCT_RANGE_START_AT + 90


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return JJ_RANGE_START_AT
        return last_values[-1] + 1

    STEM_KHO_A_135_0 = auto()
    STEM_KHO_A_135_1 = auto()
    STEM_KHO_A_135_2 = auto()
    STEM_KHO_A_135_3 = auto()
    STEM_KHO_A_135_4 = auto()
    STEM_KHO_A_135_5 = auto()
    STEM_KHO_A_135_6 = auto()
    STEM_KHO_A_135_7 = auto()
    STEM_KHO_A_135_8 = auto()
    STEM_KHO_A_135_9 = auto()
    STEM_KS_STD135_0 = auto()
    STEM_KS_STD135_1 = auto()
    STEM_KS_STD135_2 = auto()
    STEM_KS_STD135_3 = auto()
    STEM_KS_STD135_4 = auto()
    STEM_KS_STD135_5 = auto()
    STEM_KS_STD135_6 = auto()
    STEM_KS_STD135_7 = auto()
    STEM_KS_STD135_8 = auto()
    STEM_KS_STD135_9 = auto()
    STEM_KS_STD135_10 = auto()
    STEM_KA_STD135_0 = auto()
    STEM_KA_STD135_1 = auto()
    STEM_KA_STD135_2 = auto()
    STEM_KA_STD135_3 = auto()
    STEM_KA_STD135_4 = auto()
    STEM_KA_STD135_5 = auto()
    STEM_KA_STD135_6 = auto()
    STEM_KA_STD135_7 = auto()
    STEM_KA_STD135_8 = auto()
    STEM_KA_STD135_9 = auto()
    STEM_KA_STD135_10 = auto()
    STEM_KHO_S_135_0 = auto()
    STEM_KHO_S_135_1 = auto()
    STEM_KHO_S_135_2 = auto()
    STEM_KHO_S_135_3 = auto()
    STEM_KHO_S_135_4 = auto()
    STEM_KHO_S_135_5 = auto()
    STEM_KHO_S_135_6 = auto()
    STEM_KHO_S_135_7 = auto()
    STEM_KHO_S_135_8 = auto()
    STEM_KHO_S_135_9 = auto()
    STEM_KLA_125_0 = auto()
    STEM_KLA_125_1 = auto()
    STEM_KLA_125_2 = auto()
    STEM_KLA_125_3 = auto()
    STEM_KLA_125_4 = auto()
    STEM_KLA_125_5 = auto()
    STEM_KLA_125_6 = auto()
    STEM_KLA_125_7 = auto()
    STEM_KLA_125_8 = auto()
    STEM_KLA_125_9 = auto()
    STEM_STD125_S_0 = auto()
    STEM_STD125_S_1 = auto()
    STEM_STD125_S_2 = auto()
    STEM_STD125_S_3 = auto()
    STEM_STD125_A_0 = auto()
    STEM_STD125_A_1 = auto()
    STEM_STD125_A_2 = auto()
    STEM_STD125_A_3 = auto()
    STEM_STD125_A_4 = auto()
    STEM_STD125_A_5 = auto()
    STEM_STD125_A_6 = auto()
    STEM_STD125_A_7 = auto()
    STEM_SN_S_0 = auto()
    STEM_SN_S_1 = auto()
    STEM_SN_S_2 = auto()
    STEM_SN_S_3 = auto()
    STEM_SN_A_0 = auto()
    STEM_SN_A_1 = auto()
    STEM_SN_A_2 = auto()
    STEM_SN_A_3 = auto()
    STEM_SN_A_4 = auto()
    STEM_SN_A_5 = auto()
    STEM_SN_A_6 = auto()
    STEM_SN_A_7 = auto()
    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()
    RANGE_CCD_KS_STD135 = auto()
    RANGE_CCD_KA_STD135 = auto()
    RANGE_CCD_KHO_S_135 = auto()
    RANGE_CCD_KHO_A_135 = auto()
    RANGE_CCD_KLA_125 = auto()
    RANGE_CCD_STD125_S = auto()
    RANGE_CCD_STD125_A = auto()
    RANGE_CCD_SN_S = auto()
    RANGE_CCD_SN_A = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_KS_STD135_0: "103427643_1",
    S3UID.STEM_KS_STD135_1: "103427644_1",
    S3UID.STEM_KS_STD135_2: "103427646_1",
    S3UID.STEM_KS_STD135_3: "103427648_1",
    S3UID.STEM_KS_STD135_4: "103427649_1",
    S3UID.STEM_KS_STD135_5: "103427650_1",
    S3UID.STEM_KS_STD135_6: "103427651_1",
    S3UID.STEM_KS_STD135_7: "103427652_1",
    S3UID.STEM_KS_STD135_8: "103427653_1",
    S3UID.STEM_KS_STD135_9: "103427654_1",
    S3UID.STEM_KS_STD135_10: "103427657_1",
    S3UID.STEM_KA_STD135_0: "103414240_1",
    S3UID.STEM_KA_STD135_1: "103414964_1",
    S3UID.STEM_KA_STD135_2: "103414966_1",
    S3UID.STEM_KA_STD135_3: "103414967_1",
    S3UID.STEM_KA_STD135_4: "103414968_1",
    S3UID.STEM_KA_STD135_5: "103414969_1",
    S3UID.STEM_KA_STD135_6: "103414970_1",
    S3UID.STEM_KA_STD135_7: "103414971_1",
    S3UID.STEM_KA_STD135_8: "103427630_1",
    S3UID.STEM_KA_STD135_9: "103427639_1",
    S3UID.STEM_KA_STD135_10: "103427658_1",
    S3UID.STEM_KHO_S_135_0: "103607083_1",
    S3UID.STEM_KHO_S_135_1: "103607086_1",
    S3UID.STEM_KHO_S_135_2: "103607087_1",
    S3UID.STEM_KHO_S_135_3: "103607088_1",
    S3UID.STEM_KHO_S_135_4: "103607091_1",
    S3UID.STEM_KHO_S_135_5: "103607092_1",
    S3UID.STEM_KHO_S_135_6: "103607093_1",
    S3UID.STEM_KHO_S_135_7: "103607094_1",
    S3UID.STEM_KHO_S_135_8: "103607095_1",
    S3UID.STEM_KHO_S_135_9: "103607099_1",
    S3UID.STEM_KHO_A_135_0: "103550471_1",
    S3UID.STEM_KHO_A_135_1: "103550472_1",
    S3UID.STEM_KHO_A_135_2: "103550473_1",
    S3UID.STEM_KHO_A_135_3: "103550474_1",
    S3UID.STEM_KHO_A_135_4: "103550475_1",
    S3UID.STEM_KHO_A_135_5: "103550476_1",
    S3UID.STEM_KHO_A_135_6: "103550477_1",
    S3UID.STEM_KHO_A_135_7: "103550478_1",
    S3UID.STEM_KHO_A_135_8: "103550481_1",
    S3UID.STEM_KHO_A_135_9: "103550482_1",
    S3UID.STEM_KLA_125_0: "103610427_1",
    S3UID.STEM_KLA_125_1: "103610428_1",
    S3UID.STEM_KLA_125_2: "103610429_1",
    S3UID.STEM_KLA_125_3: "103610430_1",
    S3UID.STEM_KLA_125_4: "103610431_1",
    S3UID.STEM_KLA_125_5: "103610432_1",
    S3UID.STEM_KLA_125_6: "103610433_1",
    S3UID.STEM_KLA_125_7: "103610434_1",
    S3UID.STEM_KLA_125_8: "103610435_1",
    S3UID.STEM_KLA_125_9: "103610436_1",
    S3UID.STEM_STD125_S_0: "103548905_1",
    S3UID.STEM_STD125_S_1: "103550468_1",
    S3UID.STEM_STD125_S_2: "103550469_1",
    S3UID.STEM_STD125_S_3: "103550470_1",
    S3UID.STEM_STD125_A_0: "103548903_1",
    S3UID.STEM_STD125_A_1: "103550462_1",
    S3UID.STEM_STD125_A_2: "103550463_1",
    S3UID.STEM_STD125_A_3: "103550464_1",
    S3UID.STEM_STD125_A_4: "103550908_1",
    S3UID.STEM_STD125_A_5: "103550915_1",
    S3UID.STEM_STD125_A_6: "103550917_1",
    S3UID.STEM_STD125_A_7: "103550918_1",
    S3UID.STEM_SN_S_0: "103548906_1",
    S3UID.STEM_SN_S_1: "103550465_1",
    S3UID.STEM_SN_S_2: "103550466_1",
    S3UID.STEM_SN_S_3: "103550467_1",
    S3UID.STEM_SN_A_0: "103548904_1",
    S3UID.STEM_SN_A_1: "103550459_1",
    S3UID.STEM_SN_A_2: "103550460_1",
    S3UID.STEM_SN_A_3: "103550461_1",
    S3UID.STEM_SN_A_4: "103550919_1",
    S3UID.STEM_SN_A_5: "103550920_1",
    S3UID.STEM_SN_A_6: "103550921_1",
    S3UID.STEM_SN_A_7: "103550922_1",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided UID."""

    try:
        return RCC_ID_NAME[uid]
    except KeyError as exc:
        raise KeyError(f"No RCC identifier configured for {uid.name}") from exc


class StemGroup(Enum):
    """Logical families defined by the CORAIL catalog."""

    KHO_A_135 = "KHO_A_135"
    KS_STD135 = "KS_STD135"
    KA_STD135 = "KA_STD135"
    KHO_S_135 = "KHO_S_135"
    KLA_125 = "KLA_125"
    STD125_S = "STD125_S"
    STD125_A = "STD125_A"
    SN_S = "SN_S"
    SN_A = "SN_A"


COLLAR_GROUPS = {
    StemGroup.KHO_A_135,
    StemGroup.KA_STD135,
    StemGroup.KLA_125,
    StemGroup.STD125_A,
    StemGroup.SN_A,
}


def _stem_uids(prefix: str, last_index: int) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(last_index + 1))


GROUP_UIDS = {
    StemGroup.KHO_A_135: _stem_uids("STEM_KHO_A_135", 9),
    StemGroup.KS_STD135: _stem_uids("STEM_KS_STD135", 10),
    StemGroup.KA_STD135: _stem_uids("STEM_KA_STD135", 10),
    StemGroup.KHO_S_135: _stem_uids("STEM_KHO_S_135", 9),
    StemGroup.KLA_125: _stem_uids("STEM_KLA_125", 9),
    StemGroup.STD125_S: _stem_uids("STEM_STD125_S", 3),
    StemGroup.STD125_A: _stem_uids("STEM_STD125_A", 7),
    StemGroup.SN_S: _stem_uids("STEM_SN_S", 3),
    StemGroup.SN_A: _stem_uids("STEM_SN_A", 7),
}

UID_TO_GROUP: Dict[S3UID, StemGroup] = {
    uid: group for group, uids in GROUP_UIDS.items() for uid in uids
}

UID_TO_OFFSET: Dict[S3UID, int] = {
    uid: offset for group, uids in GROUP_UIDS.items() for offset, uid in enumerate(uids)
}

GROUP_START_INDEX = {
    StemGroup.KHO_A_135: 0,
    StemGroup.KS_STD135: 10,
    StemGroup.KA_STD135: 21,
    StemGroup.KHO_S_135: 32,
    StemGroup.KLA_125: 42,
    StemGroup.STD125_S: 52,
    StemGroup.STD125_A: 56,
    StemGroup.SN_S: 64,
    StemGroup.SN_A: 68,
}

GROUP_RANGE_UID = {
    StemGroup.KHO_A_135: S3UID.RANGE_CCD_KHO_A_135,
    StemGroup.KS_STD135: S3UID.RANGE_CCD_KS_STD135,
    StemGroup.KA_STD135: S3UID.RANGE_CCD_KA_STD135,
    StemGroup.KHO_S_135: S3UID.RANGE_CCD_KHO_S_135,
    StemGroup.KLA_125: S3UID.RANGE_CCD_KLA_125,
    StemGroup.STD125_S: S3UID.RANGE_CCD_STD125_S,
    StemGroup.STD125_A: S3UID.RANGE_CCD_STD125_A,
    StemGroup.SN_S: S3UID.RANGE_CCD_SN_S,
    StemGroup.SN_A: S3UID.RANGE_CCD_SN_A,
}


@dataclass(frozen=True)
class RangeStats:
    group: StemGroup
    catalog_index_min: int
    catalog_index_max: int
    range_uid: S3UID
    description: str
    size_min: int
    size_max: int

    def clamp_size(self, value: int) -> int:
        return max(self.size_min, min(self.size_max, value))


@dataclass(frozen=True)
class StemVariant:
    uid: S3UID
    group: StemGroup
    offset: int
    label: str
    rcc_id: str | None
    has_collar: bool

    @property
    def description(self) -> str:
        stats = RANGE_STATS[self.group]
        return f"{stats.description} offset {self.offset}"


RANGE_STATS = {
    StemGroup.KHO_A_135: RangeStats(
        StemGroup.KHO_A_135, 0, 9, S3UID.RANGE_CCD_KHO_A_135, "135 KHO collar", 0, len(GROUP_UIDS[StemGroup.KHO_A_135]) - 1
    ),
    StemGroup.KS_STD135: RangeStats(
        StemGroup.KS_STD135, 10, 20, S3UID.RANGE_CCD_KS_STD135, "135 STD", 0, len(GROUP_UIDS[StemGroup.KS_STD135]) - 1
    ),
    StemGroup.KA_STD135: RangeStats(
        StemGroup.KA_STD135, 21, 31, S3UID.RANGE_CCD_KA_STD135, "135 STD collar", 0, len(GROUP_UIDS[StemGroup.KA_STD135]) - 1
    ),
    StemGroup.KHO_S_135: RangeStats(
        StemGroup.KHO_S_135, 32, 41, S3UID.RANGE_CCD_KHO_S_135, "135 KHO", 0, len(GROUP_UIDS[StemGroup.KHO_S_135]) - 1
    ),
    StemGroup.KLA_125: RangeStats(
        StemGroup.KLA_125, 42, 51, S3UID.RANGE_CCD_KLA_125, "125 KLA", 0, len(GROUP_UIDS[StemGroup.KLA_125]) - 1
    ),
    StemGroup.STD125_S: RangeStats(
        StemGroup.STD125_S, 52, 55, S3UID.RANGE_CCD_STD125_S, "125 STD", 0, len(GROUP_UIDS[StemGroup.STD125_S]) - 1
    ),
    StemGroup.STD125_A: RangeStats(
        StemGroup.STD125_A, 56, 63, S3UID.RANGE_CCD_STD125_A, "125 STD collar", 0, len(GROUP_UIDS[StemGroup.STD125_A]) - 1
    ),
    StemGroup.SN_S: RangeStats(
        StemGroup.SN_S, 64, 67, S3UID.RANGE_CCD_SN_S, "135 SN", 0, len(GROUP_UIDS[StemGroup.SN_S]) - 1
    ),
    StemGroup.SN_A: RangeStats(
        StemGroup.SN_A, 68, 75, S3UID.RANGE_CCD_SN_A, "135 SN collar", 0, len(GROUP_UIDS[StemGroup.SN_A]) - 1
    ),
}


HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8)
RANGE_UIDS = tuple(GROUP_RANGE_UID.values())


VARIANT_LABELS = {
    StemGroup.KS_STD135: (
        "KS 135 deg 8",
        "KS 135 deg 9",
        "KS 135 deg 10",
        "KS 135 deg 11",
        "KS 135 deg 12",
        "KS 135 deg 13",
        "KS 135 deg 14",
        "KS 135 deg 15",
        "KS 135 deg 16",
        "KS 135 deg 18",
        "KS 135 deg 20",
    ),
    StemGroup.KA_STD135: (
        "KA 135 deg 8",
        "KA 135 deg 9",
        "KA 135 deg 10",
        "KA 135 deg 11",
        "KA 135 deg 12",
        "KA 135 deg 13",
        "KA 135 deg 14",
        "KA 135 deg 15",
        "KA 135 deg 16",
        "KA 135 deg 18",
        "KA 135 deg 20",
    ),
    StemGroup.KHO_S_135: (
        "KHO S 135 deg 9",
        "KHO S 135 deg 10",
        "KHO S 135 deg 11",
        "KHO S 135 deg 12",
        "KHO S 135 deg 13",
        "KHO S 135 deg 14",
        "KHO S 135 deg 15",
        "KHO S 135 deg 16",
        "KHO S 135 deg 18",
        "KHO S 135 deg 20",
    ),
    StemGroup.KHO_A_135: (
        "KHO A 135 deg 9",
        "KHO A 135 deg 10",
        "KHO A 135 deg 11",
        "KHO A 135 deg 12",
        "KHO A 135 deg 13",
        "KHO A 135 deg 14",
        "KHO A 135 deg 15",
        "KHO A 135 deg 16",
        "KHO A 135 deg 18",
        "KHO A 135 deg 20",
    ),
    StemGroup.KLA_125: (
        "KLA 125 deg 9",
        "KLA 125 deg 10",
        "KLA 125 deg 11",
        "KLA 125 deg 12",
        "KLA 125 deg 13",
        "KLA 125 deg 14",
        "KLA 125 deg 15",
        "KLA 125 deg 16",
        "KLA 125 deg 18",
        "KLA 125 deg 20",
    ),
    StemGroup.STD125_S: (
        "STD S 125 deg 7",
        "STD S 125 deg 8",
        "STD S 125 deg 9",
        "STD S 125 deg 10",
    ),
    StemGroup.STD125_A: (
        "STD A 125 deg 7",
        "STD A 125 deg 8",
        "STD A 125 deg 9",
        "STD A 125 deg 10",
        "STD A 125 deg 11",
        "STD A 125 deg 12",
        "STD A 125 deg 13",
        "STD A 125 deg 14",
    ),
    StemGroup.SN_S: (
        "SN S 135 deg 7",
        "SN S 135 deg 8",
        "SN S 135 deg 9",
        "SN S 135 deg 10",
    ),
    StemGroup.SN_A: (
        "SN A 135 deg 7",
        "SN A 135 deg 8",
        "SN A 135 deg 9",
        "SN A 135 deg 10",
        "SN A 135 deg 11",
        "SN A 135 deg 12",
        "SN A 135 deg 13",
        "SN A 135 deg 14",
    ),
}

VARIANTS: Dict[S3UID, StemVariant] = {}
for group, uids in GROUP_UIDS.items():
    labels = VARIANT_LABELS[group]
    if len(labels) != len(uids):  # pragma: no cover - defensive
        raise ValueError(f"Label table mismatch for {group.value}")
    for offset, uid in enumerate(uids):
        VARIANTS[uid] = StemVariant(
            uid=uid,
            group=group,
            offset=offset,
            label=labels[offset],
            rcc_id=RCC_ID_NAME.get(uid),
            has_collar=group in COLLAR_GROUPS,
        )


_HEAD_OFFSETS = {
    S3UID.HEAD_M4: -3.5,
    S3UID.HEAD_P0: 0.0,
    S3UID.HEAD_P4: 3.5,
    S3UID.HEAD_P8: 7.0,
}


def _vec_add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_scale(a: Vector3, factor: float) -> Vector3:
    return (a[0] * factor, a[1] * factor, a[2] * factor)


def _vec_length(a: Vector3) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def _vec_normalize(a: Vector3) -> Vector3:
    length = _vec_length(a)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return _vec_scale(a, 1.0 / length)


_RES01_KS = (
    (-11.07, 0.0, 11.07),
    (-11.57, 0.0, 11.57),
    (-12.32, 0.0, 12.32),
    (-13.07, 0.0, 13.07),
    (-13.8, 0.0, 13.8),
    (-14.44, 0.0, 14.44),
    (-15.07, 0.0, 15.07),
    (-15.82, 0.0, 15.82),
    (-16.57, 0.0, 16.57),
    (-17.57, 0.0, 17.57),
    (-18.57, 0.0, 18.57),
)
_RES01_KHO = (
    (-15.1, 0.0, 15.1),
    (-15.85, 0.0, 15.85),
    (-16.6, 0.0, 16.6),
    (-17.35, 0.0, 17.35),
    (-17.98, 0.0, 17.98),
    (-18.6, 0.0, 18.6),
    (-19.35, 0.0, 19.35),
    (-20.1, 0.0, 20.1),
    (-21.1, 0.0, 21.1),
    (-22.1, 0.0, 22.1),
)
_RES01_KLA = (
    (-12.62, 0.0, 8.84),
    (-13.37, 0.0, 9.36),
    (-14.12, 0.0, 9.89),
    (-14.86, 0.0, 10.4),
    (-15.5, 0.0, 10.85),
    (-16.12, 0.0, 11.29),
    (-16.87, 0.0, 11.81),
    (-17.62, 0.0, 12.34),
    (-18.58, 0.0, 13.01),
    (-19.59, 0.0, 13.72),
)
_RES01_STD125_S = (
    (-8.76, 0.0, 6.13),
    (-9.26, 0.0, 6.48),
    (-9.76, 0.0, 6.83),
    (-10.51, 0.0, 7.36),
)
_RES01_STD125_A = (
    (-8.76, 0.0, 6.13),
    (-9.26, 0.0, 6.48),
    (-9.76, 0.0, 6.83),
    (-10.51, 0.0, 7.36),
    (-11.26, 0.0, 7.88),
    (-12.01, 0.0, 8.41),
    (-12.63, 0.0, 8.84),
    (-13.26, 0.0, 9.28),
)
_RES01_SN_S = (
    (-10.22, 0.0, 10.22),
    (-10.71, 0.0, 10.71),
    (-11.21, 0.0, 11.21),
    (-11.96, 0.0, 11.96),
)
_RES01_SN_A = (
    (-10.21, 0.0, 10.21),
    (-10.71, 0.0, 10.71),
    (-11.21, 0.0, 11.21),
    (-11.96, 0.0, 11.96),
    (-12.71, 0.0, 12.71),
    (-13.46, 0.0, 13.46),
    (-14.09, 0.0, 14.09),
    (-14.71, 0.0, 14.71),
)

_NECK_ORIGIN_TABLE = {
    StemGroup.KS_STD135: _RES01_KS,
    StemGroup.KA_STD135: _RES01_KS,
    StemGroup.KHO_S_135: _RES01_KHO,
    StemGroup.KHO_A_135: _RES01_KHO,
    StemGroup.KLA_125: _RES01_KLA,
    StemGroup.STD125_S: _RES01_STD125_S,
    StemGroup.STD125_A: _RES01_STD125_A,
    StemGroup.SN_S: _RES01_SN_S,
    StemGroup.SN_A: _RES01_SN_A,
}

_RES02_KS = (
    (-19.5, 0.0, 2.64),
    (-20.0, 0.0, 3.14),
    (-20.75, 0.0, 3.89),
    (-21.5, 0.0, 4.64),
    (-22.25, 0.0, 5.36),
    (-22.87, 0.0, 6.01),
    (-23.5, 0.0, 6.64),
    (-24.25, 0.0, 7.39),
    (-25.0, 0.0, 8.14),
    (-26.0, 0.0, 9.14),
    (-27.0, 0.0, 10.14),
)
_RES02_KHO = (
    (-20.0, 0.0, 10.21),
    (-20.75, 0.0, 10.96),
    (-21.5, 0.0, 11.71),
    (-22.25, 0.0, 12.46),
    (-22.87, 0.0, 13.08),
    (-23.5, 0.0, 13.71),
    (-24.25, 0.0, 14.46),
    (-25.0, 0.0, 15.21),
    (-26.0, 0.0, 16.21),
    (-27.0, 0.0, 17.21),
)
_RES02_KLA = (
    (-19.99, 0.0, 1.46),
    (-20.74, 0.0, 1.99),
    (-21.5, 0.0, 2.51),
    (-22.26, 0.0, 3.0),
    (-22.88, 0.0, 3.47),
    (-23.49, 0.0, 3.92),
    (-24.21, 0.0, 4.47),
    (-24.96, 0.0, 5.01),
    (-25.85, 0.0, 5.74),
    (-26.78, 0.0, 6.53),
)
_RES02_STD125_S = (
    (-19.0, 0.0, -4.11),
    (-19.5, 0.0, -3.76),
    (-20.0, 0.0, -3.41),
    (-20.75, 0.0, -2.89),
)
_RES02_STD125_A = (
    (-19.0, 0.0, -4.11),
    (-19.5, 0.0, -3.76),
    (-20.0, 0.0, -3.41),
    (-20.75, 0.0, -2.89),
    (-21.5, 0.0, -2.36),
    (-22.25, 0.0, -1.84),
    (-22.87, 0.0, -1.4),
    (-23.5, 0.0, -0.96),
)
_RES02_SN_S = (
    (-19.0, 0.0, 1.43),
    (-19.5, 0.0, 1.93),
    (-20.0, 0.0, 2.43),
    (-20.75, 0.0, 3.18),
)
_RES02_SN_A = (
    (-19.0, 0.0, 1.43),
    (-19.5, 0.0, 1.93),
    (-20.0, 0.0, 2.43),
    (-20.75, 0.0, 3.18),
    (-21.5, 0.0, 3.93),
    (-22.25, 0.0, 4.68),
    (-22.87, 0.0, 5.3),
    (-23.5, 0.0, 5.93),
)

_REFERENCE_POINT_TABLE = {
    StemGroup.KS_STD135: _RES02_KS,
    StemGroup.KA_STD135: _RES02_KS,
    StemGroup.KHO_S_135: _RES02_KHO,
    StemGroup.KHO_A_135: _RES02_KHO,
    StemGroup.KLA_125: _RES02_KLA,
    StemGroup.STD125_S: _RES02_STD125_S,
    StemGroup.STD125_A: _RES02_STD125_A,
    StemGroup.SN_S: _RES02_SN_S,
    StemGroup.SN_A: _RES02_SN_A,
}

_TPR01_KS = (
    (-38.29, 0.0, 38.29),
    (-38.79, 0.0, 38.79),
    (-39.54, 0.0, 39.54),
    (-40.29, 0.0, 40.29),
    (-41.03, 0.0, 41.03),
    (-41.67, 0.0, 41.67),
    (-42.29, 0.0, 42.29),
    (-43.04, 0.0, 43.04),
    (-43.79, 0.0, 43.79),
    (-44.78, 0.0, 44.78),
    (-45.79, 0.0, 45.79),
)
_TPR01_KHO = (
    (-45.65, 0.0, 45.65),
    (-46.4, 0.0, 46.4),
    (-47.15, 0.0, 47.15),
    (-47.9, 0.0, 47.9),
    (-48.53, 0.0, 48.53),
    (-49.15, 0.0, 49.15),
    (-49.9, 0.0, 49.9),
    (-50.65, 0.0, 50.65),
    (-51.83, 0.0, 51.83),
    (-52.86, 0.0, 52.86),
)
_TPR01_KLA = (
    (-45.59, 0.0, 31.92),
    (-46.35, 0.0, 32.45),
    (-47.09, 0.0, 32.98),
    (-47.83, 0.0, 33.49),
    (-48.46, 0.0, 33.93),
    (-49.08, 0.0, 34.37),
    (-49.83, 0.0, 34.89),
    (-50.58, 0.0, 35.41),
    (-51.78, 0.0, 36.26),
    (-52.79, 0.0, 36.97),
)
_TPR01_STD125_S = (
    (-37.87, 0.0, 26.52),
    (-38.37, 0.0, 26.87),
    (-38.87, 0.0, 27.22),
    (-39.62, 0.0, 27.74),
)
_TPR01_STD125_A = (
    (-37.87, 0.0, 26.52),
    (-38.37, 0.0, 26.87),
    (-38.87, 0.0, 27.22),
    (-39.62, 0.0, 27.74),
    (-40.37, 0.0, 28.27),
    (-41.12, 0.0, 28.79),
    (-41.74, 0.0, 29.23),
    (-42.37, 0.0, 29.67),
)
_TPR01_SN_S = (
    (-32.49, 0.0, 32.49),
    (-32.99, 0.0, 32.99),
    (-33.49, 0.0, 33.49),
    (-34.24, 0.0, 34.24),
)
_TPR01_SN_A = (
    (-32.49, 0.0, 32.49),
    (-32.99, 0.0, 32.99),
    (-33.49, 0.0, 33.49),
    (-34.24, 0.0, 34.24),
    (-34.99, 0.0, 34.99),
    (-35.74, 0.0, 35.74),
    (-36.36, 0.0, 36.36),
    (-36.99, 0.0, 36.99),
)

_HEAD_POINT_TABLE = {
    StemGroup.KS_STD135: _TPR01_KS,
    StemGroup.KA_STD135: _TPR01_KS,
    StemGroup.KHO_S_135: _TPR01_KHO,
    StemGroup.KHO_A_135: _TPR01_KHO,
    StemGroup.KLA_125: _TPR01_KLA,
    StemGroup.STD125_S: _TPR01_STD125_S,
    StemGroup.STD125_A: _TPR01_STD125_A,
    StemGroup.SN_S: _TPR01_SN_S,
    StemGroup.SN_A: _TPR01_SN_A,
}


for table in (_NECK_ORIGIN_TABLE, _REFERENCE_POINT_TABLE, _HEAD_POINT_TABLE):
    for group, coords in table.items():
        if len(coords) != len(GROUP_UIDS[group]):  # pragma: no cover - defensive
            raise ValueError(f"Geometry table mismatch for {group.value}")


def stem_group(uid: S3UID) -> StemGroup:
    try:
        return UID_TO_GROUP[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem label") from exc


def get_variant(uid: S3UID) -> StemVariant:
    try:
        return VARIANTS[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem variant") from exc


def is_stem(uid: S3UID) -> bool:
    return uid in UID_TO_GROUP


def is_head(uid: S3UID) -> bool:
    return uid in HEAD_UIDS


def is_range(uid: S3UID) -> bool:
    return uid in RANGE_UIDS


def has_collar(uid: S3UID) -> bool:
    return is_stem(uid) and stem_group(uid) in COLLAR_GROUPS


def get_stem_size(uid: S3UID) -> int:
    try:
        return UID_TO_OFFSET[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem label") from exc


def iter_stems(group: StemGroup | None = None) -> Iterable[S3UID]:
    if group is None:
        for uids in GROUP_UIDS.values():
            yield from uids
        return
    yield from GROUP_UIDS[group]


def next_stem_uid(uid: S3UID, forward: bool = True) -> S3UID:
    group = stem_group(uid)
    uids = GROUP_UIDS[group]
    idx = uids.index(uid)
    candidate = idx + (1 if forward else -1)
    if 0 <= candidate < len(uids):
        return uids[candidate]
    return uid


def get_range_stats(group: StemGroup) -> RangeStats:
    return RANGE_STATS[group]


def get_ccd_range(uid: S3UID) -> S3UID:
    return GROUP_RANGE_UID[stem_group(uid)]


def get_neck_origin(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    y, z = _NECK_ORIGIN_TABLE[group][offset][1:]
    x = _NECK_ORIGIN_TABLE[group][offset][0]
    return (x, y, z)


def get_reference_point(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    x, y, z = _REFERENCE_POINT_TABLE[group][offset]
    return (x, y, z)


def get_head_point(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    x, y, z = _HEAD_POINT_TABLE[group][offset]
    return (x, y, z)


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    if not (is_stem(source_uid) and is_stem(target_uid)):
        raise ValueError("Both inputs must be stem labels")
    return _vec_sub(get_reference_point(source_uid), get_reference_point(target_uid))


def get_shaft_angle(uid: S3UID) -> float:
    return 55.0 if stem_group(uid) is StemGroup.KLA_125 else 45.0


def _clamp_to_group(value: int, group: StemGroup) -> int:
    stats = RANGE_STATS[group]
    return stats.clamp_size(value)


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")

    source_group = stem_group(uid)
    if target_group == source_group:
        return uid

    offset = get_stem_size(uid)

    def _target_in(*groups: StemGroup) -> bool:
        return target_group in groups

    if source_group in {StemGroup.KS_STD135, StemGroup.KA_STD135}:
        if _target_in(StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125):
            offset = _clamp_to_group(offset - 1, target_group)
        elif _target_in(StemGroup.STD125_S, StemGroup.STD125_A, StemGroup.SN_S, StemGroup.SN_A):
            offset = _clamp_to_group(offset + 1, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    elif source_group in {StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125}:
        if _target_in(StemGroup.KS_STD135, StemGroup.KA_STD135):
            offset = _clamp_to_group(offset + 1, target_group)
        elif _target_in(StemGroup.STD125_S, StemGroup.STD125_A, StemGroup.SN_S, StemGroup.SN_A):
            offset = _clamp_to_group(offset + 2, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    elif source_group is StemGroup.STD125_S:
        if _target_in(StemGroup.KS_STD135, StemGroup.KA_STD135):
            offset = _clamp_to_group(offset - 1, target_group)
        elif _target_in(StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125):
            offset = _clamp_to_group(offset - 2, target_group)
        elif _target_in(StemGroup.STD125_A, StemGroup.SN_A):
            offset = _clamp_to_group(offset, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    elif source_group is StemGroup.STD125_A:
        if _target_in(StemGroup.KS_STD135, StemGroup.KA_STD135):
            offset = _clamp_to_group(offset - 1, target_group)
        elif _target_in(StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125):
            offset = _clamp_to_group(offset - 2, target_group)
        elif _target_in(StemGroup.STD125_S, StemGroup.SN_S):
            offset = _clamp_to_group(offset, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    elif source_group is StemGroup.SN_S:
        if _target_in(StemGroup.KS_STD135, StemGroup.KA_STD135):
            offset = _clamp_to_group(offset - 1, target_group)
        elif _target_in(StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125):
            offset = _clamp_to_group(offset - 2, target_group)
        elif _target_in(StemGroup.STD125_A, StemGroup.SN_A):
            offset = _clamp_to_group(offset, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    elif source_group is StemGroup.SN_A:
        if _target_in(StemGroup.KS_STD135, StemGroup.KA_STD135):
            offset = _clamp_to_group(offset - 1, target_group)
        elif _target_in(StemGroup.KHO_S_135, StemGroup.KHO_A_135, StemGroup.KLA_125):
            offset = _clamp_to_group(offset - 2, target_group)
        elif _target_in(StemGroup.STD125_S, StemGroup.SN_S):
            offset = _clamp_to_group(offset, target_group)
        else:
            offset = _clamp_to_group(offset, target_group)
    else:  # pragma: no cover - defensive
        offset = _clamp_to_group(offset, target_group)

    try:
        return GROUP_UIDS[target_group][offset]
    except IndexError as exc:  # pragma: no cover - defensive
        raise ValueError(f"No similar label for {uid.name} in {target_group.value}") from exc


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    if not is_head(head_uid):
        raise ValueError("head_uid must reference a head label")
    if not is_stem(stem_uid):
        raise ValueError("stem_uid must reference a stem label")

    neck_origin = get_neck_origin(stem_uid)
    head_point = get_head_point(stem_uid)
    neck_axis = _vec_normalize(_vec_sub(head_point, neck_origin))
    offset = _HEAD_OFFSETS.get(head_uid, 0.0)
    return _vec_add(head_point, _vec_scale(neck_axis, offset))


__all__ = [
    "COMPANY_NAME",
    "PRODUCT_NAME",
    "COMPANY_RANGE_START_AT",
    "PRODUCT_RANGE_START_AT",
    "JJ_RANGE_START_AT",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
    "StemGroup",
    "StemVariant",
    "Vector3",
    "GROUP_UIDS",
    "RANGE_STATS",
    "VARIANTS",
    "HEAD_UIDS",
    "RANGE_UIDS",
    "stem_group",
    "get_variant",
    "is_stem",
    "is_head",
    "is_range",
    "has_collar",
    "get_stem_size",
    "iter_stems",
    "next_stem_uid",
    "get_range_stats",
    "get_ccd_range",
    "get_neck_origin",
    "get_reference_point",
    "get_head_point",
    "get_shift_vector",
    "get_shaft_angle",
    "similar_stem_uid",
    "head_to_stem_offset",
]
