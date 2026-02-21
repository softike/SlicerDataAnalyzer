"""Utilities reconstructed from ``implantcast_ecofit_scheme.h`` for ECOFIT stems."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "ICAST"
PRODUCT_NAME = "ECOFIT STEMLESS"
PRODUCT_RANGE_START_AT = 310_000 + 750 
S3UID_FIRST_OFFSET = 90


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return PRODUCT_RANGE_START_AT + S3UID_FIRST_OFFSET
        return last_values[-1] + 1

    STEM_STD_133_0 = auto()
    STEM_STD_133_1 = auto()
    STEM_STD_133_2 = auto()
    STEM_STD_133_3 = auto()
    STEM_STD_133_4 = auto()
    STEM_STD_133_5 = auto()
    STEM_STD_133_6 = auto()
    STEM_STD_133_7 = auto()
    STEM_STD_133_8 = auto()
    STEM_STD_133_9 = auto()
    STEM_STD_133_10 = auto()
    STEM_STD_133_11 = auto()

    STEM_LAT_133_0 = auto()
    STEM_LAT_133_1 = auto()
    STEM_LAT_133_2 = auto()
    STEM_LAT_133_3 = auto()
    STEM_LAT_133_4 = auto()
    STEM_LAT_133_5 = auto()
    STEM_LAT_133_6 = auto()
    STEM_LAT_133_7 = auto()
    STEM_LAT_133_8 = auto()
    STEM_LAT_133_9 = auto()
    STEM_LAT_133_10 = auto()
    STEM_LAT_133_11 = auto()

    STEM_STD_138_0 = auto()
    STEM_STD_138_1 = auto()
    STEM_STD_138_2 = auto()
    STEM_STD_138_3 = auto()
    STEM_STD_138_4 = auto()
    STEM_STD_138_5 = auto()
    STEM_STD_138_6 = auto()
    STEM_STD_138_7 = auto()
    STEM_STD_138_8 = auto()
    STEM_STD_138_9 = auto()

    STEM_LAT_138_0 = auto()
    STEM_LAT_138_1 = auto()
    STEM_LAT_138_2 = auto()
    STEM_LAT_138_3 = auto()
    STEM_LAT_138_4 = auto()
    STEM_LAT_138_5 = auto()
    STEM_LAT_138_6 = auto()
    STEM_LAT_138_7 = auto()
    STEM_LAT_138_8 = auto()
    STEM_LAT_138_9 = auto()

    STEM_CV_0 = auto()
    STEM_CV_1 = auto()
    STEM_CV_2 = auto()
    STEM_CV_3 = auto()
    STEM_CV_4 = auto()
    STEM_CV_5 = auto()
    STEM_CV_6 = auto()
    STEM_CV_7 = auto()
    STEM_CV_8 = auto()
    STEM_CV_9 = auto()

    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()
    RANGE_CCD_STD_133 = auto()
    RANGE_CCD_LAT_133 = auto()
    RANGE_CCD_STD_138 = auto()
    RANGE_CCD_LAT_138 = auto()
    RANGE_CCD_CV = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_STD_133_0: "30363062_133",
    S3UID.STEM_STD_133_1: "30363075_133",
    S3UID.STEM_STD_133_2: "30363087_133",
    S3UID.STEM_STD_133_3: "30363100_133",
    S3UID.STEM_STD_133_4: "30363112_133",
    S3UID.STEM_STD_133_5: "30363125_133",
    S3UID.STEM_STD_133_6: "30363137_133",
    S3UID.STEM_STD_133_7: "30363150_133",
    S3UID.STEM_STD_133_8: "30363162_133",
    S3UID.STEM_STD_133_9: "30363175_133",
    S3UID.STEM_STD_133_10: "30363187_133",
    S3UID.STEM_STD_133_11: "30363200_133",
    S3UID.STEM_LAT_133_0: "30364062_133Lat",
    S3UID.STEM_LAT_133_1: "30364075_133Lat",
    S3UID.STEM_LAT_133_2: "30364087_133Lat",
    S3UID.STEM_LAT_133_3: "30364100_133Lat",
    S3UID.STEM_LAT_133_4: "30364112_133Lat",
    S3UID.STEM_LAT_133_5: "30364125_133Lat",
    S3UID.STEM_LAT_133_6: "30364137_133Lat",
    S3UID.STEM_LAT_133_7: "30364150_133Lat",
    S3UID.STEM_LAT_133_8: "30364162_133Lat",
    S3UID.STEM_LAT_133_9: "30364175_133Lat",
    S3UID.STEM_LAT_133_10: "30364187_133Lat",
    S3UID.STEM_LAT_133_11: "30364200_133Lat",
    S3UID.STEM_STD_138_0: "30383062_138",
    S3UID.STEM_STD_138_1: "30383075_138",
    S3UID.STEM_STD_138_2: "30383087_138",
    S3UID.STEM_STD_138_3: "30383100_138",
    S3UID.STEM_STD_138_4: "30383112_138",
    S3UID.STEM_STD_138_5: "30383125_138",
    S3UID.STEM_STD_138_6: "30383137_138",
    S3UID.STEM_STD_138_7: "30383150_138",
    S3UID.STEM_STD_138_8: "30383175_138",
    S3UID.STEM_STD_138_9: "30383200_138",
    S3UID.STEM_LAT_138_0: "30384062_138Lat",
    S3UID.STEM_LAT_138_1: "30384075_138Lat",
    S3UID.STEM_LAT_138_2: "30384087_138Lat",
    S3UID.STEM_LAT_138_3: "30384100_138Lat",
    S3UID.STEM_LAT_138_4: "30384112_138Lat",
    S3UID.STEM_LAT_138_5: "30384125_138Lat",
    S3UID.STEM_LAT_138_6: "30384137_138Lat",
    S3UID.STEM_LAT_138_7: "30384150_138Lat",
    S3UID.STEM_LAT_138_8: "30384175_138Lat",
    S3UID.STEM_LAT_138_9: "30384200_138Lat",
    S3UID.STEM_CV_0: "30382062_CV",
    S3UID.STEM_CV_1: "30382075_CV",
    S3UID.STEM_CV_2: "30382087_CV",
    S3UID.STEM_CV_3: "30382100_CV",
    S3UID.STEM_CV_4: "30382112_CV",
    S3UID.STEM_CV_5: "30382125_CV",
    S3UID.STEM_CV_6: "30382137_CV",
    S3UID.STEM_CV_7: "30382150_CV",
    S3UID.STEM_CV_8: "30382175_CV",
    S3UID.STEM_CV_9: "30382200_CV",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided ECOFIT UID."""

    try:
        return RCC_ID_NAME[uid]
    except KeyError as exc:
        raise KeyError(f"No RCC identifier configured for {uid.name}") from exc


class StemGroup(Enum):
    STD_133 = "STD_133"
    LAT_133 = "LAT_133"
    STD_138 = "STD_138"
    LAT_138 = "LAT_138"
    CV = "CV"


def _stem_uids(prefix: str, last_index: int) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(last_index + 1))


GROUP_UIDS: Dict[StemGroup, Tuple[S3UID, ...]] = {
    StemGroup.STD_133: _stem_uids("STEM_STD_133", 11),
    StemGroup.LAT_133: _stem_uids("STEM_LAT_133", 11),
    StemGroup.STD_138: _stem_uids("STEM_STD_138", 9),
    StemGroup.LAT_138: _stem_uids("STEM_LAT_138", 9),
    StemGroup.CV: _stem_uids("STEM_CV", 9),
}

UID_TO_GROUP: Dict[S3UID, StemGroup] = {
    uid: group for group, uids in GROUP_UIDS.items() for uid in uids
}

UID_TO_OFFSET: Dict[S3UID, int] = {
    uid: offset for group, uids in GROUP_UIDS.items() for offset, uid in enumerate(uids)
}

GROUP_RANGE_UID = {
    StemGroup.STD_133: S3UID.RANGE_CCD_STD_133,
    StemGroup.LAT_133: S3UID.RANGE_CCD_LAT_133,
    StemGroup.STD_138: S3UID.RANGE_CCD_STD_138,
    StemGroup.LAT_138: S3UID.RANGE_CCD_LAT_138,
    StemGroup.CV: S3UID.RANGE_CCD_CV,
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

    @property
    def description(self) -> str:
        stats = RANGE_STATS[self.group]
        return f"{stats.description} size {self.offset}"


@dataclass(frozen=True)
class CutPlane:
    origin: Vector3
    normal: Vector3


RANGE_STATS = {
    StemGroup.STD_133: RangeStats(StemGroup.STD_133, 0, 11, S3UID.RANGE_CCD_STD_133, "133 STD", 0, 11),
    StemGroup.LAT_133: RangeStats(StemGroup.LAT_133, 12, 23, S3UID.RANGE_CCD_LAT_133, "133 LAT", 0, 11),
    StemGroup.STD_138: RangeStats(StemGroup.STD_138, 24, 33, S3UID.RANGE_CCD_STD_138, "138 STD", 0, 9),
    StemGroup.LAT_138: RangeStats(StemGroup.LAT_138, 34, 43, S3UID.RANGE_CCD_LAT_138, "138 LAT", 0, 9),
    StemGroup.CV: RangeStats(StemGroup.CV, 44, 53, S3UID.RANGE_CCD_CV, "123 STD", 0, 9),
}

HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8)
RANGE_UIDS = tuple(GROUP_RANGE_UID.values())

VARIANT_LABELS = {
    StemGroup.STD_133: (
        "133 STD 6,25",
        "133 STD 7,5",
        "133 STD 8,75",
        "133 STD 10",
        "133 STD 11,25",
        "133 STD 12,5",
        "133 STD 13,75",
        "133 STD 15",
        "133 STD 16,25",
        "133 STD 17,5",
        "133 STD 18,75",
        "133 STD 20",
    ),
    StemGroup.LAT_133: (
        "133 LAT 6,25",
        "133 LAT 7,5",
        "133 LAT 8,75",
        "133 LAT 10",
        "133 LAT 11,25",
        "133 LAT 12,5",
        "133 LAT 13,75",
        "133 LAT 15",
        "133 LAT 16,25",
        "133 LAT 17.5",
        "133 LAT 18,75",
        "133 LAT 20",
    ),
    StemGroup.STD_138: (
        "138 STD 6,25",
        "138 STD 7,5",
        "138 STD 8,75",
        "138 STD 10",
        "138 STD 11,25",
        "138 STD 12,5",
        "138 STD 13,75",
        "138 STD 15",
        "138 STD 17,5",
        "138 STD 20",
    ),
    StemGroup.LAT_138: (
        "138 LAT 6,25",
        "138 LAT 7,5",
        "138 LAT 8,75",
        "138 LAT 10",
        "138 LAT 11,25",
        "138 LAT 12,5",
        "138 LAT 13,75",
        "138 LAT 15",
        "138 LAT 17,5",
        "138 LAT 20",
    ),
    StemGroup.CV: (
        "123 STD 6,25",
        "123 STD 7,5",
        "123 STD 8,75",
        "123 STD 10",
        "123 STD 11,25",
        "123 STD 12,5",
        "123 STD 13,75",
        "123 STD 15",
        "123 STD 17,5",
        "123 STD 20",
    ),
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
        )


_HEAD_OFFSETS = {
    S3UID.HEAD_M4: -3.53,
    S3UID.HEAD_P0: 0.0,
    S3UID.HEAD_P4: 3.53,
    S3UID.HEAD_P8: 7.1,
}

_REFERENCE_POINT_TABLE = {
    StemGroup.STD_133: (10.69, -9.21, 0.0),
    StemGroup.STD_138: (10.5, -9.45, 0.0),
    StemGroup.CV: (10.27, -9.93, 0.0),
    StemGroup.LAT_133: (6.55, -5.9, 0.0),
    StemGroup.LAT_138: (6.54, -5.89, 0.0),
}

_HEAD_POINT_TABLE = {
    StemGroup.STD_133: (25.09, 23.39, 0.0),
    StemGroup.STD_138: (23.02, 25.56, 0.0),
    StemGroup.CV: (27.12, 17.61, 0.0),
    StemGroup.LAT_133: (29.25, 27.28, 0.0),
    StemGroup.LAT_138: (26.77, 29.74, 0.0),
}


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


def get_stem_size(uid: S3UID) -> int:
    try:
        return UID_TO_OFFSET[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem label") from exc


def iter_stems(group: StemGroup | None = None) -> Iterable[S3UID]:
    if group is None:
        for uids in GROUP_UIDS.values():
            yield from uids
    else:
        yield from GROUP_UIDS[group]


def next_stem_uid(uid: S3UID, forward: bool = True) -> S3UID:
    stats = RANGE_STATS[stem_group(uid)]
    offset = UID_TO_OFFSET[uid] + (1 if forward else -1)
    offset = stats.clamp_size(offset)
    return GROUP_UIDS[stats.group][offset]


def get_ccd_range(uid: S3UID) -> S3UID:
    return GROUP_RANGE_UID[stem_group(uid)]


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    source_group = stem_group(uid)
    source_offset = UID_TO_OFFSET[uid]
    target_stats = RANGE_STATS[target_group]
    target_offset = source_offset
    source_is_133 = source_group in (StemGroup.STD_133, StemGroup.LAT_133)
    target_is_133 = target_group in (StemGroup.STD_133, StemGroup.LAT_133)
    if not source_is_133 and target_is_133:
        if source_offset == 8:
            target_offset = 9
        elif source_offset == 9:
            target_offset = 11
    elif source_is_133 and not target_is_133:
        if source_offset == 9:
            target_offset = 8
        elif source_offset == 11:
            target_offset = 9
    target_offset = target_stats.clamp_size(target_offset)
    return GROUP_UIDS[target_group][target_offset]


def get_neck_origin(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError("uid must reference a stem label")
    return (0.0, 0.0, 0.0)


def get_reference_point(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError("uid must reference a stem label")
    return _REFERENCE_POINT_TABLE[stem_group(uid)]


def get_head_point(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError("uid must reference a stem label")
    return _HEAD_POINT_TABLE[stem_group(uid)]


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    source = get_reference_point(source_uid)
    target = get_reference_point(target_uid)
    return (source[0] - target[0], source[1] - target[1], source[2] - target[2])


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    if not is_head(head_uid):
        raise ValueError("head_uid must reference a head label")
    neck_origin = get_neck_origin(stem_uid)
    head_point = get_head_point(stem_uid)
    neck_axis = _vec_normalize(_vec_sub(head_point, neck_origin))
    offset = _HEAD_OFFSETS.get(head_uid, 0.0)
    return _vec_add(head_point, _vec_scale(neck_axis, offset))


def get_cut_plane(uid: S3UID) -> CutPlane:
    origin = get_neck_origin(uid)
    angle = math.radians(-42.0)
    normal = (math.sin(-angle), math.cos(angle), 0.0)
    return CutPlane(origin=origin, normal=normal)


def _vec_add(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def _vec_sub(a: Vector3, b: Vector3) -> Vector3:
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def _vec_scale(a: Vector3, scale: float) -> Vector3:
    return (a[0] * scale, a[1] * scale, a[2] * scale)


def _vec_norm(a: Vector3) -> float:
    return math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2)


def _vec_normalize(a: Vector3) -> Vector3:
    norm = _vec_norm(a)
    if norm == 0:
        return (0.0, 0.0, 0.0)
    return (a[0] / norm, a[1] / norm, a[2] / norm)


__all__ = [
    "S3UID",
    "StemGroup",
    "RCC_ID_NAME",
    "HEAD_UIDS",
    "RANGE_UIDS",
    "RANGE_STATS",
    "VARIANTS",
    "get_rcc_id",
    "stem_group",
    "get_variant",
    "is_stem",
    "is_head",
    "is_range",
    "get_stem_size",
    "iter_stems",
    "next_stem_uid",
    "get_ccd_range",
    "similar_stem_uid",
    "get_neck_origin",
    "get_reference_point",
    "get_head_point",
    "get_shift_vector",
    "head_to_stem_offset",
    "get_cut_plane",
]
