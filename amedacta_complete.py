"""Utilities derived from the legacy ``amistem_scheme.h`` header.

This module mirrors and extends the historical :mod:`amedacta_implants` module.
It now hosts both the UID tables (so legacy imports keep working) *and* the
extras reconstructed from the Qt plugin, allowing the new helpers to replace the
previous script seamlessly.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Mapping, Tuple

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

Vector3 = Tuple[float, float, float]


class StemGroup(str, Enum):
    """High-level families used by the AMISTEM catalog."""

    STD = "STD"
    LAT = "LAT"
    STD_SN = "STD_SN"
    LAT_SN = "LAT_SN"


def _stem_uids(prefix: str, count: int) -> Tuple[S3UID, ...]:
    return tuple(getattr(S3UID, f"{prefix}_{idx}") for idx in range(count))


GROUP_UIDS: Dict[StemGroup, Tuple[S3UID, ...]] = {
    StemGroup.STD: _stem_uids("STEM_STD", 11),
    StemGroup.LAT: _stem_uids("STEM_LAT", 9),
    StemGroup.STD_SN: _stem_uids("STEM_STD_SN", 11),
    StemGroup.LAT_SN: _stem_uids("STEM_LAT_SN", 9),
}

UID_TO_GROUP: Dict[S3UID, StemGroup] = {
    uid: group for group, uids in GROUP_UIDS.items() for uid in uids
}

UID_TO_SIZE: Dict[S3UID, int] = {
    uid: size for group, uids in GROUP_UIDS.items() for size, uid in enumerate(uids)
}

GROUP_SIZE_TO_UID: Dict[StemGroup, Dict[int, S3UID]] = {
    group: {size: uid for size, uid in enumerate(uids)}
    for group, uids in GROUP_UIDS.items()
}


@dataclass(frozen=True)
class RangeStats:
    group: StemGroup
    size_min: int
    size_max: int
    catalog_index_min: int
    catalog_index_max: int
    description: str

    def clamp_size(self, value: int) -> int:
        """Clamp ``value`` to the valid size window for the range."""

        return max(self.size_min, min(self.size_max, value))


RANGE_STATS: Dict[StemGroup, RangeStats] = {
    StemGroup.STD: RangeStats(StemGroup.STD, 0, 10, 0, 10, "STD (135 deg)"),
    StemGroup.LAT: RangeStats(StemGroup.LAT, 0, 8, 11, 19, "LAT (127 deg)"),
    StemGroup.STD_SN: RangeStats(
        StemGroup.STD_SN, 0, 10, 20, 30, "SN STD (135 deg)"
    ),
    StemGroup.LAT_SN: RangeStats(
        StemGroup.LAT_SN, 0, 8, 31, 39, "SN LAT (127 deg)"
    ),
}


@dataclass(frozen=True)
class StemVariant:
    uid: S3UID
    group: StemGroup
    size: int
    label: str
    rcc_id: str | None

    @property
    def description(self) -> str:
        stats = RANGE_STATS[self.group]
        return f"{stats.description} size {self.size}"


@dataclass(frozen=True)
class CutPlane:
    origin: "Vector3"
    normal: "Vector3"


def _variant_label(group: StemGroup, size: int) -> str:
    if group is StemGroup.STD:
        return "STD 00" if size == 0 else f"STD {size - 1}"
    if group is StemGroup.STD_SN:
        return "SN STD 00" if size == 0 else f"SN STD {size - 1}"
    if group is StemGroup.LAT:
        return f"LAT {size}"
    if group is StemGroup.LAT_SN:
        return f"SN LAT {size}"
    raise ValueError(f"Unknown group {group}")


VARIANTS: Dict[S3UID, StemVariant] = {
    uid: StemVariant(uid, group, size, _variant_label(group, size), RCC_ID_NAME.get(uid))
    for group, uids in GROUP_UIDS.items()
    for size, uid in enumerate(uids)
}

HEAD_UIDS: Tuple[S3UID, ...] = (
    S3UID.HEAD_M4,
    S3UID.HEAD_P0,
    S3UID.HEAD_P4,
    S3UID.HEAD_P8,
    S3UID.HEAD_P12,
)

RANGE_UIDS: Tuple[S3UID, ...] = (
    S3UID.RANGE_CCD_STD,
    S3UID.RANGE_CCD_LAT,
    S3UID.RANGE_CCD_STD_SN,
    S3UID.RANGE_CCD_LAT_SN,
)


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


def is_ccd_std(uid: S3UID) -> bool:
    return is_stem(uid) and stem_group(uid) is StemGroup.STD


def is_ccd_lat(uid: S3UID) -> bool:
    return is_stem(uid) and stem_group(uid) is StemGroup.LAT


def is_ccd_std_sn(uid: S3UID) -> bool:
    return is_stem(uid) and stem_group(uid) is StemGroup.STD_SN


def is_ccd_lat_sn(uid: S3UID) -> bool:
    return is_stem(uid) and stem_group(uid) is StemGroup.LAT_SN


def is_std(uid: S3UID) -> bool:
    return is_ccd_std(uid) or is_ccd_std_sn(uid)


def is_lat(uid: S3UID) -> bool:
    return is_ccd_lat(uid) or is_ccd_lat_sn(uid)


def is_head(uid: S3UID) -> bool:
    return uid in HEAD_UIDS


def is_range(uid: S3UID) -> bool:
    return uid in RANGE_UIDS


def get_stem_size(uid: S3UID) -> int:
    try:
        return UID_TO_SIZE[uid]
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


_NECK_ORIGIN_MERIDIAN: Mapping[StemGroup, Tuple[Tuple[float, float], ...]] = {
    StemGroup.STD: (
        (14.52, 14.52),
        (14.78, 14.78),
        (15.49, 15.49),
        (16.19, 16.19),
        (16.9, 16.9),
        (17.54, 17.54),
        (18.17, 18.17),
        (18.8, 18.8),
        (19.37, 19.37),
        (20.07, 20.07),
        (20.78, 20.78),
    ),
    StemGroup.LAT: (
        (13.99, 10.54),
        (14.7, 11.08),
        (15.4, 11.61),
        (16.35, 12.32),
        (16.76, 12.63),
        (17.38, 13.1),
        (17.88, 13.55),
        (18.59, 14.01),
        (19.2, 14.47),
    ),
    StemGroup.STD_SN: (
        (14.51, 14.51),
        (14.77, 14.77),
        (15.48, 15.48),
        (16.19, 16.19),
        (16.9, 16.9),
        (17.53, 17.53),
        (18.17, 18.17),
        (18.8, 18.8),
        (19.36, 19.36),
        (20.07, 20.07),
        (20.78, 20.78),
    ),
    StemGroup.LAT_SN: (
        (13.99, 10.54),
        (14.7, 11.08),
        (15.4, 11.61),
        (16.35, 12.32),
        (16.76, 12.63),
        (17.38, 13.1),
        (17.98, 13.55),
        (18.59, 14.01),
        (19.2, 14.47),
    ),
}

_HEAD_POINT_MERIDIAN: Mapping[StemGroup, Tuple[Tuple[float, float], ...]] = {
    StemGroup.STD: (
        (41.5, 41.5),
        (41.95, 41.95),
        (43.19, 43.19),
        (44.44, 44.44),
        (45.7, 45.7),
        (46.84, 46.84),
        (48.0, 48.0),
        (49.18, 49.18),
        (50.25, 50.25),
        (51.48, 51.48),
        (52.87, 52.87),
    ),
    StemGroup.LAT: (
        (43.73, 32.96),
        (45.13, 34.01),
        (46.54, 35.07),
        (47.94, 36.13),
        (49.3, 37.15),
        (50.61, 38.14),
        (51.91, 39.12),
        (53.26, 40.13),
        (54.41, 41.0),
    ),
    StemGroup.STD_SN: (
        (37.96, 37.96),
        (38.42, 38.42),
        (39.65, 39.65),
        (40.91, 40.91),
        (42.16, 42.16),
        (43.3, 43.3),
        (44.46, 44.46),
        (45.64, 45.64),
        (46.72, 46.72),
        (47.94, 47.94),
        (49.33, 49.33),
    ),
    StemGroup.LAT_SN: (
        (43.73, 32.96),
        (45.13, 34.01),
        (45.64, 35.07),
        (47.94, 36.13),
        (49.3, 37.15),
        (50.61, 38.14),
        (51.91, 39.12),
        (53.26, 40.13),
        (54.41, 41.0),
    ),
}


def _vec(x: float, y: float, z: float) -> Vector3:
    return (float(x), float(y), float(z))


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


def get_neck_origin(uid: S3UID) -> Vector3:
    stats = stem_group(uid)
    size = get_stem_size(uid)
    try:
        y, z = _NECK_ORIGIN_MERIDIAN[stats][size]
    except (KeyError, IndexError) as exc:
        raise ValueError(f"No neck origin data for {uid.name}") from exc
    return _vec(0.0, y, z)


def get_head_point(uid: S3UID) -> Vector3:
    stats = stem_group(uid)
    size = get_stem_size(uid)
    try:
        y, z = _HEAD_POINT_MERIDIAN[stats][size]
    except (KeyError, IndexError) as exc:
        raise ValueError(f"No head point data for {uid.name}") from exc
    return _vec(0.0, y, z)


_STD_TO_LAT_SHIFT = {
    1: 5.89,
    2: 6.03,
    3: 6.22,
    4: 6.39,
    5: 6.55,
    6: 6.71,
    7: 6.85,
    8: 7.0,
    9: 7.26,
}

_LAT_TO_STD_SHIFT = {
    0: 5.89,
    1: 6.03,
    2: 6.22,
    3: 6.39,
    4: 6.55,
    5: 6.71,
    6: 6.85,
    7: 7.0,
    8: 7.26,
}

_STD_SN_TO_LAT_SN_SHIFT = {
    1: 5.01,
    2: 5.19,
    3: 5.38,
    4: 5.58,
    5: 5.69,
    6: 5.87,
    7: 6.07,
    8: 6.13,
    9: 6.48,
}

_LAT_SN_TO_STD_SN_SHIFT = {
    0: 5.01,
    1: 5.19,
    2: 5.38,
    3: 5.58,
    4: 5.69,
    5: 5.87,
    6: 6.07,
    7: 6.13,
    8: 6.48,
}


def get_shift_vector(source_uid: S3UID, target_uid: S3UID) -> Vector3:
    if not (is_stem(source_uid) and is_stem(target_uid)):
        raise ValueError("Both labels must be stem variants")

    if source_uid == target_uid:
        return (0.0, 0.0, 0.0)

    source_neck = get_neck_origin(source_uid)
    target_neck = get_neck_origin(target_uid)

    if is_std(source_uid) and is_std(target_uid):
        return _vec_sub(source_neck, target_neck)

    if is_ccd_lat(source_uid) and is_ccd_lat(target_uid):
        return _vec_sub(source_neck, target_neck)

    if is_ccd_lat_sn(source_uid) and is_ccd_lat_sn(target_uid):
        return _vec_sub(source_neck, target_neck)

    size = get_stem_size(source_uid)

    if is_ccd_std(source_uid) and is_ccd_lat(target_uid):
        shift = _STD_TO_LAT_SHIFT.get(size, 0.0)
        return _vec(0.0, 0.0, shift)

    if is_ccd_lat(source_uid) and is_ccd_std(target_uid):
        shift = _LAT_TO_STD_SHIFT.get(size, 0.0)
        return _vec(0.0, 0.0, -shift)

    if is_ccd_std_sn(source_uid) and is_ccd_lat_sn(target_uid):
        shift = _STD_SN_TO_LAT_SN_SHIFT.get(size, 0.0)
        return _vec(0.0, 0.0, shift)

    if is_ccd_lat_sn(source_uid) and is_ccd_std_sn(target_uid):
        shift = _LAT_SN_TO_STD_SN_SHIFT.get(size, 0.0)
        return _vec(0.0, 0.0, -shift)

    return _vec_sub(source_neck, target_neck)


def similar_stem_uid(uid: S3UID, target_group: StemGroup) -> S3UID:
    if not is_stem(uid):
        raise ValueError(f"{uid.name} is not a stem label")

    source_group = stem_group(uid)
    if target_group == source_group:
        return uid

    stats = RANGE_STATS[target_group]
    size = get_stem_size(uid)
    translated_size = size

    if source_group is StemGroup.STD:
        if target_group is StemGroup.STD_SN:
            translated_size = stats.clamp_size(size)
        elif target_group in {StemGroup.LAT, StemGroup.LAT_SN}:
            if size in (0, RANGE_STATS[source_group].size_max):
                return uid
            translated_size = stats.clamp_size(size - 1)
    elif source_group is StemGroup.LAT:
        if target_group in {StemGroup.STD, StemGroup.STD_SN}:
            translated_size = stats.clamp_size(size + 1)
    elif source_group is StemGroup.STD_SN:
        if target_group is StemGroup.STD:
            translated_size = stats.clamp_size(size)
        elif target_group in {StemGroup.LAT, StemGroup.LAT_SN}:
            if size in (0, RANGE_STATS[source_group].size_max):
                return uid
            translated_size = stats.clamp_size(size - 1)
    elif source_group is StemGroup.LAT_SN:
        if target_group in {StemGroup.STD, StemGroup.STD_SN}:
            translated_size = stats.clamp_size(size + 1)

    try:
        return GROUP_SIZE_TO_UID[target_group][translated_size]
    except KeyError as exc:
        raise ValueError(
            f"No similar label for {uid.name} in {target_group.value}"
        ) from exc


_HEAD_OFFSET_BASE = 3.5355
_LAT_CORRECTION = 0.9 + _HEAD_OFFSET_BASE


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    if not is_head(head_uid):
        raise ValueError("Head label expected")
    if not is_stem(stem_uid):
        raise ValueError("Stem label expected")

    neck_origin = get_neck_origin(stem_uid)
    head_point = get_head_point(stem_uid)
    neck_axis = _vec_normalize(_vec_sub(head_point, neck_origin))

    offset_factor = _HEAD_OFFSET_BASE
    if head_uid is S3UID.HEAD_M4:
        offset_factor *= -2.0
    elif head_uid is S3UID.HEAD_P0:
        offset_factor *= -1.0
    elif head_uid is S3UID.HEAD_P4:
        offset_factor = 0.0
    elif head_uid is S3UID.HEAD_P12:
        offset_factor *= 2.0

    if is_ccd_lat(stem_uid):
        offset_factor += _LAT_CORRECTION

    delta = _vec_scale(neck_axis, offset_factor)
    return _vec_add(head_point, delta)


def get_cut_plane(uid: S3UID) -> CutPlane:
    if not is_stem(uid):
        raise ValueError("Stem label expected")

    origin = get_neck_origin(uid)
    angle = math.radians(45.0)
    normal = _vec(0.0, math.cos(angle), math.sin(angle))
    normal = _vec_normalize(normal)
    return CutPlane(origin=origin, normal=normal)


__all__ = [
    # Backwards-compatible surface that used to live in amedacta_implants
    "COMPANY_NAME",
    "COMPANY_RANGE_START_AT",
    "COMPANY_RANGE_END_AT",
    "PRODUCT_OFFSETS",
    "AMISTEM_RANGE_START_AT",
    "S3UID_FIRST_OFFSET",
    "S3UID",
    "RCC_ID_NAME",
    "get_rcc_id",
    # Extended helpers derived from amistem_scheme.h
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
    "is_ccd_std",
    "is_ccd_lat",
    "is_ccd_std_sn",
    "is_ccd_lat_sn",
    "is_std",
    "is_lat",
    "is_head",
    "is_range",
    "get_stem_size",
    "iter_stems",
    "next_stem_uid",
    "get_range_stats",
    "get_neck_origin",
    "get_head_point",
    "get_shift_vector",
    "similar_stem_uid",
    "head_to_stem_offset",
    "get_cut_plane",
]
