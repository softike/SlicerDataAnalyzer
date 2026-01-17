"""Regression tests for the Johnson & Johnson CORAIL geometry tables."""

from __future__ import annotations

import math

import pytest

from johnson_corail_complete import (
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
    uid = S3UID.STEM_KA_STD135_2
    assert stem_group(uid) is StemGroup.KA_STD135
    assert get_stem_size(uid) == 2


def test_similar_uid_from_ks_to_kho():
    neighbor = similar_stem_uid(S3UID.STEM_KS_STD135_5, StemGroup.KHO_S_135)
    assert neighbor is S3UID.STEM_KHO_S_135_4


def test_similar_uid_from_kho_to_std125_a():
    neighbor = similar_stem_uid(S3UID.STEM_KHO_S_135_4, StemGroup.STD125_A)
    assert neighbor is S3UID.STEM_STD125_A_6


def test_shift_vector_matches_reference_points():
    source = S3UID.STEM_KA_STD135_1
    target = S3UID.STEM_KA_STD135_0
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
    stem_uid = S3UID.STEM_KA_STD135_3
    offset = head_to_stem_offset(S3UID.HEAD_P8, stem_uid)
    axis = _normalized_axis(stem_uid)
    head_point = get_head_point(stem_uid)
    expected = (
        head_point[0] + axis[0] * 7.0,
        head_point[1] + axis[1] * 7.0,
        head_point[2] + axis[2] * 7.0,
    )
    assert offset == pytest.approx(expected, rel=1e-4)


def test_has_collar_detection():
    assert has_collar(S3UID.STEM_KA_STD135_0)
    assert not has_collar(S3UID.STEM_KS_STD135_0)


def test_cut_plane_orientation_matches_cpp_expectations():
    uid = S3UID.STEM_KS_STD135_2
    plane = get_cut_plane(uid)
    assert plane.origin == pytest.approx(get_neck_origin(uid), rel=1e-6)
    expected = (
        -math.sin(math.radians(45.0)),
        0.0,
        math.cos(math.radians(45.0)),
    )
    assert plane.normal == pytest.approx(expected, rel=1e-6)


def test_cut_plane_collar_offset_is_applied():
    uid = S3UID.STEM_KA_STD135_2
    plane = get_cut_plane(uid)
    neck = get_neck_origin(uid)
    expected_origin = tuple(neck[i] + plane.normal[i] * -0.1 for i in range(3))
    assert plane.origin == pytest.approx(expected_origin, rel=1e-6)
