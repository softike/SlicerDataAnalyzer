"""Utilities reconstructed from ``lima_fit_scheme.h`` for FIT stems."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from typing import Dict, Iterable, Tuple

Vector3 = Tuple[float, float, float]

COMPANY_NAME = "LC"
PRODUCT_NAME = "LC FIT"
PRODUCT_RANGE_START_AT = 60_000 + 750


class S3UID(IntEnum):
    """Integer UIDs mirroring the C++ S3UID enum."""

    def _generate_next_value_(name, start, count, last_values):  # type: ignore[override]
        if not last_values:
            return PRODUCT_RANGE_START_AT
        return last_values[-1] + 1

    STEM_1_R = auto()
    STEM_2_R = auto()
    STEM_3_R = auto()
    STEM_4_R = auto()
    STEM_5_R = auto()
    STEM_6_R = auto()
    STEM_7_R = auto()
    STEM_1_L = auto()
    STEM_2_L = auto()
    STEM_3_L = auto()
    STEM_4_L = auto()
    STEM_5_L = auto()
    STEM_6_L = auto()
    STEM_7_L = auto()
    CUTPLANE = auto()
    HEAD_M4 = auto()
    HEAD_P0 = auto()
    HEAD_P4 = auto()
    HEAD_P8 = auto()


RCC_ID_NAME: Dict[S3UID, str] = {
    S3UID.STEM_1_R: "4211_25_110",
    S3UID.STEM_2_R: "4211_25_120",
    S3UID.STEM_3_R: "4211_25_130",
    S3UID.STEM_4_R: "4211_25_140",
    S3UID.STEM_5_R: "4211_25_150",
    S3UID.STEM_6_R: "4211_25_160",
    S3UID.STEM_7_R: "4211_25_170",
    S3UID.STEM_1_L: "4211_25_010",
    S3UID.STEM_2_L: "4211_25_020",
    S3UID.STEM_3_L: "4211_25_030",
    S3UID.STEM_4_L: "4211_25_040",
    S3UID.STEM_5_L: "4211_25_050",
    S3UID.STEM_6_L: "4211_25_060",
    S3UID.STEM_7_L: "4211_25_070",
}


def get_rcc_id(uid: S3UID) -> str:
    """Return the RCC identifier for the provided FIT UID."""

    try:
        return RCC_ID_NAME[uid]
    except KeyError as exc:
        raise KeyError(f"No RCC identifier configured for {uid.name}") from exc


class StemSide(Enum):
    RIGHT = "R"
    LEFT = "L"


HEAD_UIDS = (S3UID.HEAD_M4, S3UID.HEAD_P0, S3UID.HEAD_P4, S3UID.HEAD_P8)


@dataclass(frozen=True)
class CutPlane:
    origin: Vector3
    normal: Vector3


UID_TO_SIDE: Dict[S3UID, StemSide] = {
    **{uid: StemSide.RIGHT for uid in (
        S3UID.STEM_1_R,
        S3UID.STEM_2_R,
        S3UID.STEM_3_R,
        S3UID.STEM_4_R,
        S3UID.STEM_5_R,
        S3UID.STEM_6_R,
        S3UID.STEM_7_R,
    )},
    **{uid: StemSide.LEFT for uid in (
        S3UID.STEM_1_L,
        S3UID.STEM_2_L,
        S3UID.STEM_3_L,
        S3UID.STEM_4_L,
        S3UID.STEM_5_L,
        S3UID.STEM_6_L,
        S3UID.STEM_7_L,
    )},
}

UID_TO_SIZE: Dict[S3UID, int] = {
    S3UID.STEM_1_R: 1,
    S3UID.STEM_2_R: 2,
    S3UID.STEM_3_R: 3,
    S3UID.STEM_4_R: 4,
    S3UID.STEM_5_R: 5,
    S3UID.STEM_6_R: 6,
    S3UID.STEM_7_R: 7,
    S3UID.STEM_1_L: 1,
    S3UID.STEM_2_L: 2,
    S3UID.STEM_3_L: 3,
    S3UID.STEM_4_L: 4,
    S3UID.STEM_5_L: 5,
    S3UID.STEM_6_L: 6,
    S3UID.STEM_7_L: 7,
}


_HEAD_OFFSETS = {
    S3UID.HEAD_M4: -8.0,
    S3UID.HEAD_P0: -4.0,
    S3UID.HEAD_P4: 0.0,
    S3UID.HEAD_P8: 4.3,
}


def is_stem(uid: S3UID) -> bool:
    return uid in UID_TO_SIDE


def is_head(uid: S3UID) -> bool:
    return uid in HEAD_UIDS


def stem_side(uid: S3UID) -> StemSide:
    try:
        return UID_TO_SIDE[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem label") from exc


def get_stem_size(uid: S3UID) -> int:
    try:
        return UID_TO_SIZE[uid]
    except KeyError as exc:
        raise ValueError(f"{uid.name} is not a stem label") from exc


def iter_stems(side: StemSide | None = None) -> Iterable[S3UID]:
    for uid in UID_TO_SIDE:
        if side is None or UID_TO_SIDE[uid] is side:
            yield uid


def get_neck_origin(uid: S3UID) -> Vector3:
    if not is_stem(uid):
        raise ValueError("uid must reference a stem label")
    return (0.0, 0.0, 0.0)


def head_to_stem_offset(head_uid: S3UID, stem_uid: S3UID) -> Vector3:
    if not is_head(head_uid):
        raise ValueError("head_uid must reference a head label")
    if not is_stem(stem_uid):
        raise ValueError("stem_uid must reference a stem label")
    return (_HEAD_OFFSETS.get(head_uid, 0.0), 0.0, 0.0)


def get_cut_plane(uid: S3UID) -> CutPlane:
    if not is_stem(uid):
        raise ValueError("uid must reference a stem label")
    size = get_stem_size(uid)
    l = -34.4
    if size == 2:
        l = -36.5
    elif size == 3:
        l = -38.0
    elif size == 4:
        l = -39.5
    elif size == 5:
        l = -41.5
    elif size == 6:
        l = -43.4
    elif size == 7:
        l = -45.6
    return CutPlane(origin=(l, 0.0, 0.0), normal=(1.0, 0.0, 0.0))


__all__ = [
    "S3UID",
    "StemSide",
    "HEAD_UIDS",
    "RCC_ID_NAME",
    "get_rcc_id",
    "is_stem",
    "is_head",
    "stem_side",
    "get_stem_size",
    "iter_stems",
    "get_neck_origin",
    "head_to_stem_offset",
    "get_cut_plane",
]
