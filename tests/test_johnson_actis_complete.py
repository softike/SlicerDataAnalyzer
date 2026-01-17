"""Regression tests for the Johnson & Johnson ACTIS geometry tables."""

from __future__ import annotations

import math

import pytest

from johnson_actis_complete import (
    S3UID,
    StemGroup,
    get_cut_plane,
    get_head_point,
    get_neck_origin,
    get_reference_point,
    get_shift_vector,
    get_stem_size,
    has_collar,
    head_to_stem_offset,
    similar_stem_uid,
    stem_group,
)


def _normalized_axis(stem_uid: S3UID):
    neck = get_neck_origin(stem_uid)
    head = get_head_point(stem_uid)
    delta = (head[0] - neck[0], head[1] - neck[1], head[2] - neck[2])
    length = math.sqrt(delta[0] ** 2 + delta[1] ** 2 + delta[2] ** 2)
    return (delta[0] / length, delta[1] / length, delta[2] / length)


def test_group_and_size_mapping():
    uid = S3UID.STEM_STD_4
    assert stem_group(uid) is StemGroup.STD
    assert get_stem_size(uid) == 4


def test_similar_uid_between_ranges():
    neighbor = similar_stem_uid(S3UID.STEM_STD_6, StemGroup.HO)
    assert neighbor is S3UID.STEM_HO_6


def test_shift_vector_matches_reference_points():
    source = S3UID.STEM_STD_2
    target = S3UID.STEM_STD_1
    shift = get_shift_vector(source, target)
    ref_source = get_reference_point(source)
    ref_target = get_reference_point(target)
    expected = (
        ref_source[0] - ref_target[0],
        ref_source[1] - ref_target[1],
        ref_source[2] - ref_target[2],
    )
    assert shift == pytest.approx(expected, rel=1e-5)


def test_head_offset_uses_axis_direction():
    stem_uid = S3UID.STEM_HO_3
    offset = head_to_stem_offset(S3UID.HEAD_P8, stem_uid)
    axis = _normalized_axis(stem_uid)
    head_point = get_head_point(stem_uid)
    expected = (
        head_point[0] + axis[0] * 7.0,
        head_point[1] + axis[1] * 7.0,
        head_point[2] + axis[2] * 7.0,
    )
    assert offset == pytest.approx(expected, rel=1e-4)


def test_all_stems_have_collar():
    assert has_collar(S3UID.STEM_STD_0)
    assert has_collar(S3UID.STEM_HO_0)


def test_cut_plane_orientation_matches_cpp_logic():
    uid = S3UID.STEM_STD_2
    plane = get_cut_plane(uid)
    assert plane.origin == pytest.approx(get_neck_origin(uid), rel=1e-6)
    expected = (
        math.sin(math.radians(40.0)),
        0.0,
        math.cos(math.radians(40.0)),
    )
    assert plane.normal == pytest.approx(expected, rel=1e-6)

