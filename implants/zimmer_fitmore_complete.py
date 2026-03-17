"""Utilities reconstructed from ``zimmer_fitmore_complete.h`` for Zimmer Biomet FITMORE stems.

The Zimmer Biomet FITMORE catalog exposes four stem families (A, B, Bext, C)
that were originally encoded inside a Qt plugin.  This module mirrors the UID
table and layers on top the geometric helpers that were previously only
available in C++.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "ZB"
PRODUCT_NAME = "ZB FITMORE"

# From SboPluginDefs.h: namespace ZB { companyRangeStartsAt = 190000L }
# FITMORE product offset = +1500L  →  PRODUCT_RANGE_START_AT = 191_500
ZB_RANGE_START_AT = 190_000
PRODUCT_RANGE_START_AT = ZB_RANGE_START_AT + 1_500
S3UID_FIRST_OFFSET = 90  # STEM_A_0 = 191_590


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum for Zimmer Biomet FITMORE."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return PRODUCT_RANGE_START_AT + S3UID_FIRST_OFFSET
        return last_values[-1] + 1

    STEM_A_0 = auto()
    STEM_A_1 = auto()
    STEM_A_2 = auto()
    STEM_A_3 = auto()
    STEM_A_4 = auto()
    STEM_A_5 = auto()
    STEM_A_6 = auto()
    STEM_A_7 = auto()
    STEM_A_8 = auto()
    STEM_A_9 = auto()
    STEM_A_10 = auto()
    STEM_A_11 = auto()
    STEM_A_12 = auto()
    STEM_A_13 = auto()

    STEM_B_0 = auto()
    STEM_B_1 = auto()
    STEM_B_2 = auto()
    STEM_B_3 = auto()
    STEM_B_4 = auto()
    STEM_B_5 = auto()
    STEM_B_6 = auto()
    STEM_B_7 = auto()
    STEM_B_8 = auto()
    STEM_B_9 = auto()
    STEM_B_10 = auto()
    STEM_B_11 = auto()
    STEM_B_12 = auto()
    STEM_B_13 = auto()

    STEM_BEX_0 = auto()
    STEM_BEX_1 = auto()
    STEM_BEX_2 = auto()
    STEM_BEX_3 = auto()
    STEM_BEX_4 = auto()
    STEM_BEX_5 = auto()
    STEM_BEX_6 = auto()
    STEM_BEX_7 = auto()
    STEM_BEX_8 = auto()
    STEM_BEX_9 = auto()
    STEM_BEX_10 = auto()
    STEM_BEX_11 = auto()
    STEM_BEX_12 = auto()
    STEM_BEX_13 = auto()

    STEM_C_0 = auto()
    STEM_C_1 = auto()
    STEM_C_2 = auto()
    STEM_C_3 = auto()
    STEM_C_4 = auto()
    STEM_C_5 = auto()
    STEM_C_6 = auto()
    STEM_C_7 = auto()
    STEM_C_8 = auto()
    STEM_C_9 = auto()
    STEM_C_10 = auto()
    STEM_C_11 = auto()
    STEM_C_12 = auto()
    STEM_C_13 = auto()

    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()
    HEAD_P10 = auto()

    RANGE_CCD_A = auto()
    RANGE_CCD_B = auto()
    RANGE_CCD_BEX = auto()
    RANGE_CCD_C = auto()


# RCC IDs from meshInfoRCList() in zimmer_fitmore_complete.h
# Pattern: "063.287.411_C_M##_R00", M01-M14 → A, M15-M28 → B, M29-M42 → BEX, M43-M56 → C
RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_A_0:   "063.287.411_C_M01_R00",
    S3UID.STEM_A_1:   "063.287.411_C_M02_R00",
    S3UID.STEM_A_2:   "063.287.411_C_M03_R00",
    S3UID.STEM_A_3:   "063.287.411_C_M04_R00",
    S3UID.STEM_A_4:   "063.287.411_C_M05_R00",
    S3UID.STEM_A_5:   "063.287.411_C_M06_R00",
    S3UID.STEM_A_6:   "063.287.411_C_M07_R00",
    S3UID.STEM_A_7:   "063.287.411_C_M08_R00",
    S3UID.STEM_A_8:   "063.287.411_C_M09_R00",
    S3UID.STEM_A_9:   "063.287.411_C_M10_R00",
    S3UID.STEM_A_10:  "063.287.411_C_M11_R00",
    S3UID.STEM_A_11:  "063.287.411_C_M12_R00",
    S3UID.STEM_A_12:  "063.287.411_C_M13_R00",
    S3UID.STEM_A_13:  "063.287.411_C_M14_R00",
    S3UID.STEM_B_0:   "063.287.411_C_M15_R00",
    S3UID.STEM_B_1:   "063.287.411_C_M16_R00",
    S3UID.STEM_B_2:   "063.287.411_C_M17_R00",
    S3UID.STEM_B_3:   "063.287.411_C_M18_R00",
    S3UID.STEM_B_4:   "063.287.411_C_M19_R00",
    S3UID.STEM_B_5:   "063.287.411_C_M20_R00",
    S3UID.STEM_B_6:   "063.287.411_C_M21_R00",
    S3UID.STEM_B_7:   "063.287.411_C_M22_R00",
    S3UID.STEM_B_8:   "063.287.411_C_M23_R00",
    S3UID.STEM_B_9:   "063.287.411_C_M24_R00",
    S3UID.STEM_B_10:  "063.287.411_C_M25_R00",
    S3UID.STEM_B_11:  "063.287.411_C_M26_R00",
    S3UID.STEM_B_12:  "063.287.411_C_M27_R00",
    S3UID.STEM_B_13:  "063.287.411_C_M28_R00",
    S3UID.STEM_BEX_0:  "063.287.411_C_M29_R00",
    S3UID.STEM_BEX_1:  "063.287.411_C_M30_R00",
    S3UID.STEM_BEX_2:  "063.287.411_C_M31_R00",
    S3UID.STEM_BEX_3:  "063.287.411_C_M32_R00",
    S3UID.STEM_BEX_4:  "063.287.411_C_M33_R00",
    S3UID.STEM_BEX_5:  "063.287.411_C_M34_R00",
    S3UID.STEM_BEX_6:  "063.287.411_C_M35_R00",
    S3UID.STEM_BEX_7:  "063.287.411_C_M36_R00",
    S3UID.STEM_BEX_8:  "063.287.411_C_M37_R00",
    S3UID.STEM_BEX_9:  "063.287.411_C_M38_R00",
    S3UID.STEM_BEX_10: "063.287.411_C_M39_R00",
    S3UID.STEM_BEX_11: "063.287.411_C_M40_R00",
    S3UID.STEM_BEX_12: "063.287.411_C_M41_R00",
    S3UID.STEM_BEX_13: "063.287.411_C_M42_R00",
    S3UID.STEM_C_0:   "063.287.411_C_M43_R00",
    S3UID.STEM_C_1:   "063.287.411_C_M44_R00",
    S3UID.STEM_C_2:   "063.287.411_C_M45_R00",
    S3UID.STEM_C_3:   "063.287.411_C_M46_R00",
    S3UID.STEM_C_4:   "063.287.411_C_M47_R00",
    S3UID.STEM_C_5:   "063.287.411_C_M48_R00",
    S3UID.STEM_C_6:   "063.287.411_C_M49_R00",
    S3UID.STEM_C_7:   "063.287.411_C_M50_R00",
    S3UID.STEM_C_8:   "063.287.411_C_M51_R00",
    S3UID.STEM_C_9:   "063.287.411_C_M52_R00",
    S3UID.STEM_C_10:  "063.287.411_C_M53_R00",
    S3UID.STEM_C_11:  "063.287.411_C_M54_R00",
    S3UID.STEM_C_12:  "063.287.411_C_M55_R00",
    S3UID.STEM_C_13:  "063.287.411_C_M56_R00",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided UID."""
    try:
        return RCC_ID_NAME[uid]
    except KeyError as exc:
        raise KeyError(f"No RCC identifier configured for {uid.name}") from exc


class StemGroup(Enum):
    """Logical families defined by the FITMORE catalog."""
    A = "A"
    B = "B"
    BEX = "BEX"
    C = "C"


# No collar for any FITMORE group (cutPlane() in C++ has no collar offset logic)
COLLAR_GROUPS: set = set()


def _stem_uids(prefix: str, last_index: int) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(last_index + 1))


GROUP_UIDS = {
    StemGroup.A:   _stem_uids("STEM_A", 13),
    StemGroup.B:   _stem_uids("STEM_B", 13),
    StemGroup.BEX: _stem_uids("STEM_BEX", 13),
    StemGroup.C:   _stem_uids("STEM_C", 13),
}

UID_TO_GROUP: Dict[S3UID, StemGroup] = {
    uid: group for group, uids in GROUP_UIDS.items() for uid in uids
}

UID_TO_OFFSET: Dict[S3UID, int] = {
    uid: offset for group, uids in GROUP_UIDS.items() for offset, uid in enumerate(uids)
}

GROUP_RANGE_UID = {
    StemGroup.A:   S3UID.RANGE_CCD_A,
    StemGroup.B:   S3UID.RANGE_CCD_B,
    StemGroup.BEX: S3UID.RANGE_CCD_BEX,
    StemGroup.C:   S3UID.RANGE_CCD_C,
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


@dataclass(frozen=True)
class CutPlane:
    origin: Vector3
    normal: Vector3


RANGE_STATS = {
    StemGroup.A: RangeStats(
        StemGroup.A, 0, 13, S3UID.RANGE_CCD_A, "A", 0, len(GROUP_UIDS[StemGroup.A]) - 1
    ),
    StemGroup.B: RangeStats(
        StemGroup.B, 14, 27, S3UID.RANGE_CCD_B, "B", 0, len(GROUP_UIDS[StemGroup.B]) - 1
    ),
    StemGroup.BEX: RangeStats(
        StemGroup.BEX, 28, 41, S3UID.RANGE_CCD_BEX, "Bext", 0, len(GROUP_UIDS[StemGroup.BEX]) - 1
    ),
    StemGroup.C: RangeStats(
        StemGroup.C, 42, 55, S3UID.RANGE_CCD_C, "C", 0, len(GROUP_UIDS[StemGroup.C]) - 1
    ),
}

HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8, S3UID.HEAD_P10)
RANGE_UIDS = tuple(GROUP_RANGE_UID.values())

# Catalog labels from parts() in zimmer_fitmore_complete.h
VARIANT_LABELS = {
    StemGroup.A:   ("A1", "A2", "A3", "A4", "A5", "A6", "A7", "A8", "A9", "A10", "A11", "A12", "A13", "A14"),
    StemGroup.B:   ("B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14"),
    StemGroup.BEX: ("Bext1", "Bext2", "Bext3", "Bext4", "Bext5", "Bext6", "Bext7",
                    "Bext8", "Bext9", "Bext10", "Bext11", "Bext12", "Bext13", "Bext14"),
    StemGroup.C:   ("C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11", "C12", "C13", "C14"),
}

VARIANTS: Dict[S3UID, StemVariant] = {}
for _group, _uids in GROUP_UIDS.items():
    _labels = VARIANT_LABELS[_group]
    if len(_labels) != len(_uids):  # pragma: no cover - defensive
        raise ValueError(f"Label table mismatch for {_group.value}")
    for _offset, _uid in enumerate(_uids):
        VARIANTS[_uid] = StemVariant(
            uid=_uid,
            group=_group,
            offset=_offset,
            label=_labels[_offset],
            rcc_id=RCC_ID_NAME.get(_uid),
            has_collar=False,
        )

# Offsets applied to head_point along the neck axis (from headToStemMatrix() in .h)
_HEAD_OFFSETS = {
    S3UID.HEAD_M4:  -3.5,
    S3UID.HEAD_P0:   0.0,
    S3UID.HEAD_P4:   3.5,
    S3UID.HEAD_P8:   7.0,
    S3UID.HEAD_P10: 10.5,
}

# ---------------------------------------------------------------------------
# Vector helpers
# ---------------------------------------------------------------------------

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


def _rotate_x(vec: Vector3, degrees: float) -> Vector3:
    rad = math.radians(degrees)
    c = math.cos(rad)
    s = math.sin(rad)
    x, y, z = vec
    return (x, y * c - z * s, y * s + z * c)


def _rotate_y(vec: Vector3, degrees: float) -> Vector3:
    rad = math.radians(degrees)
    c = math.cos(rad)
    s = math.sin(rad)
    x, y, z = vec
    return (x * c + z * s, y, -x * s + z * c)


# ---------------------------------------------------------------------------
# Geometry tables — transcribed from cRes01_* (neck origin / PLANE_ORIGIN)
# and cTpr01_* (head rotation point) arrays in zimmer_fitmore_complete.h
# ---------------------------------------------------------------------------

# cRes01_A[14][3] — PLANE_ORIGIN for group A
_NECK_ORIGIN_A = (
    (16.053, 0.0, 19.132),
    (16.553, 0.0, 19.728),
    (17.053, 0.0, 20.323),
    (17.553, 0.0, 20.919),
    (18.053, 0.0, 21.515),
    (18.678, 0.0, 22.260),
    (19.303, 0.0, 23.005),
    (19.928, 0.0, 23.750),
    (20.553, 0.0, 24.495),
    (21.303, 0.0, 25.388),
    (22.053, 0.0, 26.282),
    (22.803, 0.0, 27.176),
    (23.553, 0.0, 28.070),
    (24.303, 0.0, 28.964),
)

# cRes01_B[14][3] — PLANE_ORIGIN for group B
_NECK_ORIGIN_B = (
    (18.297, 0.0, 19.621),
    (18.797, 0.0, 20.157),
    (19.297, 0.0, 20.694),
    (19.797, 0.0, 21.230),
    (20.297, 0.0, 21.766),
    (20.922, 0.0, 22.436),
    (21.547, 0.0, 23.106),
    (22.172, 0.0, 23.777),
    (22.797, 0.0, 24.447),
    (23.547, 0.0, 25.251),
    (24.297, 0.0, 26.055),
    (25.047, 0.0, 26.860),
    (25.797, 0.0, 27.664),
    (26.547, 0.0, 28.468),
)

# cRes01_BEX[14][3] — PLANE_ORIGIN for group BEX
_NECK_ORIGIN_BEX = (
    (18.716, 0.0, 15.156),
    (19.216, 0.0, 15.560),
    (19.716, 0.0, 15.965),
    (20.216, 0.0, 16.370),
    (20.716, 0.0, 16.775),
    (21.341, 0.0, 17.281),
    (21.966, 0.0, 17.787),
    (22.591, 0.0, 18.293),
    (23.216, 0.0, 18.800),
    (23.966, 0.0, 19.407),
    (24.716, 0.0, 20.014),
    (25.466, 0.0, 20.622),
    (26.216, 0.0, 21.229),
    (26.966, 0.0, 21.836),
)

# cRes01_C[14][3] — PLANE_ORIGIN for group C
_NECK_ORIGIN_C = (
    (20.913, 0.0, 15.759),
    (21.413, 0.0, 16.136),
    (21.913, 0.0, 16.513),
    (22.413, 0.0, 16.889),
    (22.913, 0.0, 17.266),
    (23.538, 0.0, 17.737),
    (24.163, 0.0, 18.208),
    (24.788, 0.0, 18.679),
    (25.413, 0.0, 19.150),
    (26.163, 0.0, 19.715),
    (26.913, 0.0, 20.280),
    (27.663, 0.0, 20.845),
    (28.413, 0.0, 21.411),
    (29.163, 0.0, 21.976),
)

_NECK_ORIGIN_TABLE = {
    StemGroup.A:   _NECK_ORIGIN_A,
    StemGroup.B:   _NECK_ORIGIN_B,
    StemGroup.BEX: _NECK_ORIGIN_BEX,
    StemGroup.C:   _NECK_ORIGIN_C,
}

# cTpr01_A[14][3] — HEAD_ROTATION_POINT for group A
_HEAD_POINT_A = (
    (31.000, 0.0, 36.944),
    (31.500, 0.0, 37.540),
    (32.000, 0.0, 38.136),
    (32.500, 0.0, 38.732),
    (33.000, 0.0, 39.328),
    (33.625, 0.0, 40.073),
    (34.250, 0.0, 40.818),
    (34.875, 0.0, 41.562),
    (35.500, 0.0, 42.307),
    (36.250, 0.0, 43.201),
    (37.000, 0.0, 44.095),
    (37.750, 0.0, 44.989),
    (38.500, 0.0, 45.883),
    (39.250, 0.0, 46.776),
)

# cTpr01_B[14][3] — HEAD_ROTATION_POINT for group B
_HEAD_POINT_B = (
    (37.000, 0.0, 39.678),
    (37.500, 0.0, 40.214),
    (38.000, 0.0, 40.750),
    (38.500, 0.0, 41.286),
    (39.000, 0.0, 41.822),
    (39.625, 0.0, 42.493),
    (40.250, 0.0, 43.163),
    (40.875, 0.0, 43.833),
    (41.500, 0.0, 44.503),
    (42.250, 0.0, 45.308),
    (43.000, 0.0, 46.112),
    (43.750, 0.0, 46.916),
    (44.500, 0.0, 47.720),
    (45.250, 0.0, 48.525),
)

# cTpr01_BEX[14][3] — HEAD_ROTATION_POINT for group BEX
_HEAD_POINT_BEX = (
    (44.000, 0.0, 35.630),
    (44.500, 0.0, 36.035),
    (45.000, 0.0, 36.440),
    (45.500, 0.0, 36.845),
    (46.000, 0.0, 37.250),
    (46.625, 0.0, 37.756),
    (47.250, 0.0, 38.262),
    (47.875, 0.0, 38.768),
    (48.500, 0.0, 39.275),
    (49.250, 0.0, 39.882),
    (50.000, 0.0, 40.489),
    (50.750, 0.0, 41.097),
    (51.500, 0.0, 41.704),
    (52.250, 0.0, 42.311),
)

# cTpr01_C[14][3] — HEAD_ROTATION_POINT for group C
_HEAD_POINT_C = (
    (51.000, 0.0, 38.431),
    (51.500, 0.0, 38.808),
    (52.000, 0.0, 39.185),
    (52.500, 0.0, 39.562),
    (53.000, 0.0, 39.938),
    (53.625, 0.0, 40.409),
    (54.250, 0.0, 40.880),
    (54.875, 0.0, 41.351),
    (55.500, 0.0, 41.822),
    (56.250, 0.0, 42.387),
    (57.000, 0.0, 42.953),
    (57.750, 0.0, 43.518),
    (58.500, 0.0, 44.083),
    (59.250, 0.0, 44.648),
)

_HEAD_POINT_TABLE = {
    StemGroup.A:   _HEAD_POINT_A,
    StemGroup.B:   _HEAD_POINT_B,
    StemGroup.BEX: _HEAD_POINT_BEX,
    StemGroup.C:   _HEAD_POINT_C,
}

# Per-group diagonal offset d used in getRES_02():
#   reference_point = (neck_x + d, neck_y, neck_z - d)
_RES02_OFFSET = {
    StemGroup.A:   6.55,
    StemGroup.B:   6.90,
    StemGroup.BEX: 6.50,
    StemGroup.C:   6.95,
}

for _table in (_NECK_ORIGIN_TABLE, _HEAD_POINT_TABLE):
    for _group, _coords in _table.items():
        if len(_coords) != len(GROUP_UIDS[_group]):  # pragma: no cover - defensive
            raise ValueError(f"Geometry table mismatch for {_group.value}")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

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
    return False


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
    x, y, z = _NECK_ORIGIN_TABLE[group][offset]
    return (x, y, z)


def get_reference_point(uid: S3UID) -> Vector3:
    """Mirror of getRES_02() in C++: neck_origin offset by (d, 0, -d) per group."""
    group = stem_group(uid)
    offset = get_stem_size(uid)
    x, y, z = _NECK_ORIGIN_TABLE[group][offset]
    d = _RES02_OFFSET[group]
    return (x + d, y, z - d)


def get_head_point(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    x, y, z = _HEAD_POINT_TABLE[group][offset]
    return (x, y, z)


def get_cut_plane(uid: S3UID) -> CutPlane:
    """Mirror of cutPlane() in C++: origin at neck, normal via rotX(90°) then rotY(+45°)."""
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    origin = get_neck_origin(uid)
    normal = _rotate_y(_rotate_x((0.0, 1.0, 0.0), 90.0), 45.0)
    return CutPlane(origin=origin, normal=_vec_normalize(normal))


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    if not (is_stem(source_uid) and is_stem(target_uid)):
        raise ValueError("Both inputs must be stem labels")
    return _vec_sub(get_reference_point(source_uid), get_reference_point(target_uid))


def get_shaft_angle(uid: S3UID) -> float:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    return 45.0


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    """Return the stem in target_group whose size most closely matches uid's.

    Mirrors getSimilarLabel() in C++, which simply transfers the size index,
    clamping to the target group's valid range.
    """
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    if target_group == stem_group(uid):
        return uid
    offset = get_stem_size(uid)
    clamped = RANGE_STATS[target_group].clamp_size(offset)
    return GROUP_UIDS[target_group][clamped]


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    """Mirror of headToStemMatrix() in C++: head_point + neck_axis * l."""
    if not is_head(head_uid):
        raise ValueError("head_uid must reference a head label")
    if not is_stem(stem_uid):
        raise ValueError("stem_uid must reference a stem label")
    neck_o = get_neck_origin(stem_uid)
    head_o = get_head_point(stem_uid)
    neck_axis = _vec_normalize(_vec_sub(head_o, neck_o))
    l = _HEAD_OFFSETS.get(head_uid, 0.0)
    return _vec_add(head_o, _vec_scale(neck_axis, l))


__all__ = [
    "COMPANY_NAME",
    "PRODUCT_NAME",
    "ZB_RANGE_START_AT",
    "PRODUCT_RANGE_START_AT",
    "S3UID_FIRST_OFFSET",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
    "StemGroup",
    "COLLAR_GROUPS",
    "StemVariant",
    "CutPlane",
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
    "get_cut_plane",
    "get_shift_vector",
    "get_shaft_angle",
    "similar_stem_uid",
    "head_to_stem_offset",
]
