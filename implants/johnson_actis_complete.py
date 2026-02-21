"""Utilities reconstructed from ``johnson_actis_scheme.h`` for ACTIS stems.

The Johnson & Johnson ACTIS catalog exposes two CCD ranges (standard and high
offset).  This module mirrors the UID table from :mod:`johnson_implants_actis`
and layers on top the geometric helpers that previously only existed in C++.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "JNJ"
PRODUCT_NAME = "ACTIS"
COMPANY_RANGE_START_AT = 160_000
PRODUCT_RANGE_START_AT = COMPANY_RANGE_START_AT + 1_250
JJ_RANGE_START_AT = PRODUCT_RANGE_START_AT + 90


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum."""

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
    S3UID.STEM_STD_0: "103794036 Rev 1",
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
    S3UID.STEM_HO_0: "103794037 Rev 1",
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
    """Return the RCC identifier for the provided UID."""

    return RCC_ID_NAME[uid]


class StemGroup(Enum):
    """Logical CCD ranges offered by the ACTIS catalog."""

    STD = "STD"
    HO = "HIGH"


COLLAR_GROUPS = {StemGroup.STD, StemGroup.HO}


def _stem_uids(prefix: str, last_index: int) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(last_index + 1))


GROUP_UIDS = {
    StemGroup.STD: _stem_uids("STEM_STD", 12),
    StemGroup.HO: _stem_uids("STEM_HO", 12),
}

UID_TO_GROUP = {uid: group for group, uids in GROUP_UIDS.items() for uid in uids}
UID_TO_OFFSET = {uid: offset for group, uids in GROUP_UIDS.items() for offset, uid in enumerate(uids)}

GROUP_RANGE_UID = {
    StemGroup.STD: S3UID.RANGE_CCD_STD,
    StemGroup.HO: S3UID.RANGE_CCD_HO,
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
    StemGroup.STD: RangeStats(
        StemGroup.STD,
        0,
        12,
        S3UID.RANGE_CCD_STD,
        "Standard collared",
        0,
        len(GROUP_UIDS[StemGroup.STD]) - 1,
    ),
    StemGroup.HO: RangeStats(
        StemGroup.HO,
        13,
        25,
        S3UID.RANGE_CCD_HO,
        "High-offset collared",
        0,
        len(GROUP_UIDS[StemGroup.HO]) - 1,
    ),
}

HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8)


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
RANGE_UIDS = tuple(GROUP_RANGE_UID.values())

VARIANT_LABELS = {
    StemGroup.STD: tuple(f"COLLARED STD {idx}" for idx in range(len(GROUP_UIDS[StemGroup.STD]))),
    StemGroup.HO: tuple(f"COLLARED HIGH {idx}" for idx in range(len(GROUP_UIDS[StemGroup.HO]))),
}


VARIANTS: Dict[S3UID, StemVariant] = {}
for group, uids in GROUP_UIDS.items():
    labels = VARIANT_LABELS[group]
    for offset, uid in enumerate(uids):
        VARIANTS[uid] = StemVariant(
            uid=uid,
            group=group,
            offset=offset,
            label=labels[offset],
            rcc_id=RCC_ID_NAME.get(uid),
            has_collar=True,
        )


_HEAD_OFFSETS = {
    S3UID.HEAD_M4: -3.5,
    S3UID.HEAD_P0: 0.0,
    S3UID.HEAD_P4: 3.5,
    S3UID.HEAD_P8: 7.0,
}

_NECK_ORIGIN_STD = (
    (11.94, 0.0, 10.02),
    (12.47, 0.0, 10.46),
    (13.27, 0.0, 11.14),
    (13.05, 0.0, 10.95),
    (13.56, 0.0, 11.38),
    (13.58, 0.0, 11.40),
    (14.12, 0.0, 11.85),
    (14.14, 0.0, 11.87),
    (14.68, 0.0, 12.32),
    (14.70, 0.0, 12.34),
    (15.29, 0.0, 12.83),
    (15.64, 0.0, 13.12),
    (16.04, 0.0, 13.46),
)

_NECK_ORIGIN_HO = (
    (15.10, 0.0, 12.67),
    (15.47, 0.0, 12.98),
    (16.27, 0.0, 13.65),
    (16.05, 0.0, 13.46),
    (17.57, 0.0, 14.74),
    (17.58, 0.0, 14.76),
    (18.12, 0.0, 15.21),
    (18.14, 0.0, 15.22),
    (18.68, 0.0, 15.68),
    (18.70, 0.0, 15.69),
    (19.29, 0.0, 16.19),
    (19.64, 0.0, 16.48),
    (20.04, 0.0, 16.82),
)

_REFERENCE_POINT_STD = (
    (20.01, 0.0, 3.17),
    (21.01, 0.0, 3.30),
    (21.81, 0.0, 3.98),
    (22.51, 0.0, 3.01),
    (23.30, 0.0, 3.21),
    (24.10, 0.0, 2.57),
    (24.81, 0.0, 2.89),
    (25.61, 0.0, 2.25),
    (26.31, 0.0, 2.57),
    (27.11, 0.0, 1.93),
    (27.91, 0.0, 2.24),
    (28.61, 0.0, 2.24),
    (29.41, 0.0, 2.24),
)

_REFERENCE_POINT_HO = (
    (20.21, 0.0, 8.39),
    (21.01, 0.0, 8.33),
    (21.81, 0.0, 9.01),
    (22.51, 0.0, 8.04),
    (23.31, 0.0, 9.92),
    (24.11, 0.0, 9.28),
    (24.82, 0.0, 9.59),
    (25.61, 0.0, 8.96),
    (26.31, 0.0, 9.28),
    (27.11, 0.0, 8.64),
    (27.91, 0.0, 8.96),
    (28.61, 0.0, 8.96),
    (29.41, 0.0, 8.96),
)

_HEAD_POINT_STD = (
    (36.29, 0.0, 30.45),
    (36.44, 0.0, 30.58),
    (38.44, 0.0, 32.26),
    (38.24, 0.0, 32.09),
    (39.85, 0.0, 33.44),
    (39.66, 0.0, 33.28),
    (41.66, 0.0, 34.96),
    (41.66, 0.0, 34.96),
    (43.66, 0.0, 36.64),
    (43.66, 0.0, 36.64),
    (45.66, 0.0, 38.32),
    (45.66, 0.0, 38.32),
    (45.66, 0.0, 38.32),
)

_HEAD_POINT_HO = (
    (42.44, 0.0, 35.61),
    (42.44, 0.0, 35.61),
    (44.44, 0.0, 37.29),
    (44.24, 0.0, 37.12),
    (47.85, 0.0, 40.15),
    (47.66, 0.0, 39.99),
    (49.66, 0.0, 41.67),
    (49.66, 0.0, 41.67),
    (51.66, 0.0, 43.35),
    (51.66, 0.0, 43.35),
    (53.66, 0.0, 45.03),
    (53.66, 0.0, 45.03),
    (53.66, 0.0, 45.03),
)

_NECK_ORIGIN_TABLE = {
    StemGroup.STD: _NECK_ORIGIN_STD,
    StemGroup.HO: _NECK_ORIGIN_HO,
}

_REFERENCE_POINT_TABLE = {
    StemGroup.STD: _REFERENCE_POINT_STD,
    StemGroup.HO: _REFERENCE_POINT_HO,
}

_HEAD_POINT_TABLE = {
    StemGroup.STD: _HEAD_POINT_STD,
    StemGroup.HO: _HEAD_POINT_HO,
}


for table in (_NECK_ORIGIN_TABLE, _REFERENCE_POINT_TABLE, _HEAD_POINT_TABLE):
    for group, coords in table.items():
        if len(coords) != len(GROUP_UIDS[group]):  # pragma: no cover - defensive
            raise ValueError(f"Geometry table mismatch for {group.value}")


def _vec_sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_scale(a: Vector3, factor: float) -> Vector3:
    return (a[0] * factor, a[1] * factor, a[2] * factor)


def _vec_length(a: Vector3) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def _vec_normalize(a: Vector3) -> Vector3:
    length = _vec_length(a)
    if length == 0:
        return (0.0, 0.0, 0.0)
    return _vec_scale(a, 1.0 / length)


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
    return is_stem(uid)


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
    return _NECK_ORIGIN_TABLE[group][offset]


def get_reference_point(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    return _REFERENCE_POINT_TABLE[group][offset]


def get_head_point(uid: S3UID) -> Vector3:
    group = stem_group(uid)
    offset = get_stem_size(uid)
    return _HEAD_POINT_TABLE[group][offset]


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    if not (is_stem(source_uid) and is_stem(target_uid)):
        raise ValueError("Both inputs must be stem labels")
    return _vec_sub(get_reference_point(source_uid), get_reference_point(target_uid))


def get_shaft_angle(uid: S3UID) -> float:
    return 45.0


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")

    source_group = stem_group(uid)
    if source_group is target_group:
        return uid

    offset = get_stem_size(uid)
    offset = RANGE_STATS[target_group].clamp_size(offset)
    return GROUP_UIDS[target_group][offset]


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


def get_cut_plane(uid: S3UID) -> CutPlane:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")

    origin = get_neck_origin(uid)
    normal = _rotate_y(_rotate_x((0.0, 1.0, 0.0), 90.0), 40.0)
    return CutPlane(origin=origin, normal=_vec_normalize(normal))


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
    "get_shift_vector",
    "get_shaft_angle",
    "similar_stem_uid",
    "head_to_stem_offset",
    "get_cut_plane",
]
