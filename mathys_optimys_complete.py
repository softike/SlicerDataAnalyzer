"""Utilities reconstructed from ``mathys_optimys_scheme.h`` for OPTIMYS stems."""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "MYS"
PRODUCT_NAME = "MYS OPTIMYS"
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


class StemGroup(Enum):
    STD = "STD"
    LAT = "LAT"


COLLAR_GROUPS = {StemGroup.STD, StemGroup.LAT}


def _stem_uids(prefix: str) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(1, 15))


GROUP_UIDS = {
    StemGroup.STD: _stem_uids("STEM_STD"),
    StemGroup.LAT: _stem_uids("STEM_LAT"),
}

UID_TO_GROUP = {uid: group for group, uids in GROUP_UIDS.items() for uid in uids}
UID_TO_OFFSET = {uid: idx for group, uids in GROUP_UIDS.items() for idx, uid in enumerate(uids)}

GROUP_RANGE_UID = {
    StemGroup.STD: S3UID.RANGE_CCD_STD,
    StemGroup.LAT: S3UID.RANGE_CCD_LAT,
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
    StemGroup.STD: RangeStats(StemGroup.STD, 0, 13, S3UID.RANGE_CCD_STD, "Standard CCD", 0, len(GROUP_UIDS[StemGroup.STD]) - 1),
    StemGroup.LAT: RangeStats(StemGroup.LAT, 14, 27, S3UID.RANGE_CCD_LAT, "Lateralized CCD", 0, len(GROUP_UIDS[StemGroup.LAT]) - 1),
}

HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8)
RANGE_UIDS = tuple(GROUP_RANGE_UID.values())

VARIANT_LABELS = {
    StemGroup.STD: ("STD XS", "STD 0", "STD 1", "STD 2", "STD 3", "STD 4", "STD 5", "STD 6", "STD 7", "STD 8", "STD 9", "STD 10", "STD 11", "STD 12"),
    StemGroup.LAT: ("LAT XS", "LAT 0", "LAT 1", "LAT 2", "LAT 3", "LAT 4", "LAT 5", "LAT 6", "LAT 7", "LAT 8", "LAT 9", "LAT 10", "LAT 11", "LAT 12"),
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


_HEAD_TOP_STD = (
    27.0,
    28.05,
    29.1,
    30.15,
    31.2,
    32.25,
    33.9,
    35.05,
    36.2,
    38.25,
    39.5,
    40.75,
    42.0,
    43.25,
)

_HEAD_TOP_LAT = (
    31.0,
    32.05,
    33.1,
    34.15,
    35.2,
    36.25,
    37.9,
    39.05,
    40.2,
    42.25,
    43.5,
    44.75,
    46.0,
    47.25,
)

_TRANSLATION_X = {
    StemGroup.STD: -12.5,
    StemGroup.LAT: -8.5,
}

_HEAD_OFFSETS = {
    S3UID.HEAD_M4: -8.0,
    S3UID.HEAD_P0: -4.0,
    S3UID.HEAD_P4: 0.0,
    S3UID.HEAD_P8: 4.0,
}

_COS = math.cos(math.radians(-45.0))
_SIN = math.sin(math.radians(-45.0))


def _rotate_z(vec: Vector3) -> Vector3:
    x, y, z = vec
    return (x * _COS - y * _SIN, x * _SIN + y * _COS, z)


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


def _head_top(uid: S3UID) -> float:
    table = _HEAD_TOP_STD if stem_group(uid) is StemGroup.STD else _HEAD_TOP_LAT
    return table[get_stem_size(uid)]


def _translation_x(uid: S3UID) -> float:
    return _TRANSLATION_X[stem_group(uid)]


def get_neck_origin(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    return _rotate_z((_translation_x(uid), 0.0, 0.0))


def get_head_point(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    return _rotate_z((_translation_x(uid), _head_top(uid), 0.0))


def get_reference_point(uid: S3UID) -> Vector3:
    return get_head_point(uid)


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    if not (is_stem(source_uid) and is_stem(target_uid)):
        raise ValueError("Both inputs must be stem labels")
    ref_source = get_reference_point(source_uid)
    ref_target = get_reference_point(target_uid)
    return (ref_source[0] - ref_target[0], ref_source[1] - ref_target[1], ref_source[2] - ref_target[2])


def get_shaft_angle(uid: S3UID) -> float:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")
    return 45.0


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")

    offset = get_stem_size(uid)
    clamped = RANGE_STATS[target_group].clamp_size(offset)
    return GROUP_UIDS[target_group][clamped]


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    if not is_head(head_uid):
        raise ValueError("head_uid must reference a head label")
    if not is_stem(stem_uid):
        raise ValueError("stem_uid must reference a stem label")

    head_top = _head_top(stem_uid) + _HEAD_OFFSETS.get(head_uid, 0.0)
    return _rotate_z((_translation_x(stem_uid), head_top, 0.0))


__all__ = [
    "COMPANY_NAME",
    "PRODUCT_NAME",
    "MYS_RANGE_START_AT",
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
