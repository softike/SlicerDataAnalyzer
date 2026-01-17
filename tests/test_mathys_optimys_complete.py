"""Regression tests for the Mathys OPTIMYS geometry helpers."""

from __future__ import annotations

import math

import pytest

from mathys_optimys_complete import (
    S3UID,
    StemGroup,
    get_cut_plane,
    get_head_point,
    get_neck_origin,
    get_reference_point,
    get_shift_vector,
    get_stem_size,
    get_variant,
    head_to_stem_offset,
    similar_stem_uid,
    stem_group,
)


def _rotate_expected(x: float, y: float) -> tuple[float, float, float]:
    angle = math.radians(-45.0)
    c = math.cos(angle)
    s = math.sin(angle)
    return (x * c - y * s, x * s + y * c, 0.0)


def test_variant_metadata():
    variant = get_variant(S3UID.STEM_STD_1)
    assert variant.label == "STD XS"
    assert variant.group is StemGroup.STD
    assert variant.has_collar


def test_group_and_size_mapping():
    uid = S3UID.STEM_LAT_4
    assert stem_group(uid) is StemGroup.LAT
    assert get_stem_size(uid) == 3


def test_neck_origin_matches_cpp_transform():
    origin = get_neck_origin(S3UID.STEM_STD_1)
    expected = _rotate_expected(-12.5, 0.0)
    assert origin == pytest.approx(expected, rel=1e-6)


def test_head_point_uses_precomputed_offsets():
    head_point = get_head_point(S3UID.STEM_STD_1)
    expected = _rotate_expected(-12.5, 27.0)
    assert head_point == pytest.approx(expected, rel=1e-6)


def test_head_offset_varies_with_head_uid():
    offset = head_to_stem_offset(S3UID.HEAD_P8, S3UID.STEM_STD_1)
    expected = _rotate_expected(-12.5, 31.0)
    assert offset == pytest.approx(expected, rel=1e-6)


def test_shift_vector_uses_reference_points():
    source = S3UID.STEM_STD_4
    target = S3UID.STEM_STD_3
    shift = get_shift_vector(source, target)
    ref_source = get_reference_point(source)
    ref_target = get_reference_point(target)
    expected = (ref_source[0] - ref_target[0], ref_source[1] - ref_target[1], ref_source[2] - ref_target[2])
    assert shift == pytest.approx(expected, rel=1e-6)


def test_similar_uid_between_ranges():
    neighbor = similar_stem_uid(S3UID.STEM_STD_5, StemGroup.LAT)
    assert neighbor is S3UID.STEM_LAT_5


def test_cut_plane_matches_reference_transform():
    uid = S3UID.STEM_STD_1
    plane = get_cut_plane(uid)
    assert plane.origin == pytest.approx(get_neck_origin(uid), rel=1e-6)
    expected_normal = _rotate_expected(0.0, 1.0)
    assert plane.normal == pytest.approx(expected_normal, rel=1e-6)

