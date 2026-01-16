"""Regression tests for the AMISTEM tables extracted from the Qt plugin."""

from __future__ import annotations

import math

import pytest

from amedacta_complete import (
    S3UID,
    StemGroup,
    get_head_point,
    get_neck_origin,
    get_shift_vector,
    get_stem_size,
    head_to_stem_offset,
    similar_stem_uid,
    stem_group,
)


def test_group_and_size_mapping():
    uid = S3UID.STEM_STD_3
    assert stem_group(uid) is StemGroup.STD
    assert get_stem_size(uid) == 3


def test_similar_uid_std_to_lat():
    neighbor = similar_stem_uid(S3UID.STEM_STD_5, StemGroup.LAT)
    assert neighbor is S3UID.STEM_LAT_4


def test_shift_vector_std_to_lat():
    shift = get_shift_vector(S3UID.STEM_STD_5, S3UID.STEM_LAT_4)
    assert shift == pytest.approx((0.0, 0.0, 6.55), rel=1e-4)


def _axis_for_stem(uid: S3UID):
    neck = get_neck_origin(uid)
    head = get_head_point(uid)
    delta = (head[0] - neck[0], head[1] - neck[1], head[2] - neck[2])
    length = math.sqrt(delta[0] ** 2 + delta[1] ** 2 + delta[2] ** 2)
    return (delta[0] / length, delta[1] / length, delta[2] / length)


def test_head_offsets_for_std_stem():
    stem_uid = S3UID.STEM_STD_5
    head_point = get_head_point(stem_uid)
    axis = _axis_for_stem(stem_uid)

    offset_p4 = head_to_stem_offset(S3UID.HEAD_P4, stem_uid)
    assert offset_p4 == pytest.approx(head_point, rel=1e-4)

    offset_p12 = head_to_stem_offset(S3UID.HEAD_P12, stem_uid)
    expected = tuple(head_point[i] + axis[i] * 7.071 for i in range(3))
    assert offset_p12 == pytest.approx(expected, rel=1e-3)


def test_lat_head_offset_includes_correction():
    stem_uid = S3UID.STEM_LAT_4
    axis = _axis_for_stem(stem_uid)
    offset = head_to_stem_offset(S3UID.HEAD_P4, stem_uid)
    head_point = get_head_point(stem_uid)

    delta = tuple(offset[i] - head_point[i] for i in range(3))
    expected_mag = 0.9 + 3.5355
    expected = tuple(axis[i] * expected_mag for i in range(3))
    assert delta == pytest.approx(expected, rel=1e-3)
