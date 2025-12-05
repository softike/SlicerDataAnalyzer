import math

import pytest

from compareResults_3Studies import calculate_femoral_anteversion

TOL = 1e-4


def _matrix_string(translation):
	"""Return a flattened 4x4 transform with identity rotation and the given translation."""
	tx, ty, tz = translation
	rows = [
		[1.0, 0.0, 0.0, 0.0],
		[0.0, 1.0, 0.0, 0.0],
		[0.0, 0.0, 1.0, 0.0],
		[tx, ty, tz, 1.0],
	]
	return " ".join(f"{value:.6f}" for row in rows for value in row)


def _vector_string(x, y, z):
	return f"{x:.6f} {y:.6f} {z:.6f}"


def _sphere_matrix(angle_deg, radius=50.0):
	rad = math.radians(angle_deg)
	return _matrix_string((radius * math.cos(rad), radius * math.sin(rad), 0.0))


def _bcp_points(angle_deg, side):
	rad = math.radians(angle_deg)
	direction = (math.cos(rad), math.sin(rad), 0.0)
	if side == 'Right':
		p0 = direction
		p1 = (0.0, 0.0, 0.0)
	else:
		p0 = (0.0, 0.0, 0.0)
		p1 = direction
	return _vector_string(*p0), _vector_string(*p1)


def _expected_difference(angle_a, angle_b):
	diff = (angle_a - angle_b) % 360.0
	return 360.0 - diff if diff > 180.0 else diff


def _fold_within_90(angle):
	normalized = ((angle + 180.0) % 360.0) - 180.0
	if normalized > 90.0:
		normalized = 180.0 - normalized
	elif normalized < -90.0:
		normalized = -180.0 - normalized
	return normalized

def test_zero_anteversion_when_vectors_align_right_side():
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(0.0)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(0.0, side='Right')

	angle, neck, bcp_angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
		return_components=True,
	)

	assert angle == pytest.approx(0.0, abs=TOL)
	assert neck == pytest.approx(0.0, abs=TOL)
	assert bcp_angle == pytest.approx(0.0, abs=TOL)


def test_known_offset_matches_shortest_difference():
	neck_angle = 35.0
	bcp_angle = 0.0
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Right')

	angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
	)

	expected = _expected_difference(neck_angle, bcp_angle)
	assert angle == pytest.approx(expected, abs=TOL)


def test_wraparound_uses_shortest_distance():
	neck_angle = 355.0
	bcp_angle = 5.0
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Right')

	angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
	)

	expected = _expected_difference(neck_angle, bcp_angle)
	assert angle == pytest.approx(expected, abs=TOL)


def test_right_side_uses_supplementary_when_difference_large():
	neck_angle = 358.71157899648233
	bcp_angle = 199.98084733141582
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Right')

	angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
	)

	raw_diff = _expected_difference(neck_angle, bcp_angle)
	assert raw_diff > 90.0
	expected = 180.0 - raw_diff
	assert angle == pytest.approx(expected, abs=TOL)


def test_left_side_also_limits_large_differences():
	neck_angle = 210.0  # becomes 30° after left-side adjustment
	bcp_angle = 162.0
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Left')

	angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
		side='Left',
	)

	raw_diff = _expected_difference(30.0, bcp_angle)
	assert raw_diff > 90.0
	expected = 180.0 - raw_diff
	assert angle == pytest.approx(expected, abs=TOL)


def test_returned_components_are_folded_within_90():
	neck_angle = 358.71157899648233
	bcp_angle = 199.98084733141582
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Right')

	anteversion, neck, bcp_dir = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
		return_components=True,
	)

	assert anteversion == pytest.approx(21.269268334933486, abs=TOL)
	assert abs(neck) <= 90.0
	assert abs(bcp_dir) <= 90.0
	assert neck == pytest.approx(_fold_within_90(neck_angle), abs=TOL)
	assert bcp_dir == pytest.approx(_fold_within_90(bcp_angle), abs=TOL)

def test_left_side_uses_reoriented_bcp_direction():
	neck_angle = 210.0  # Maps to 30° after left-side adjustment
	bcp_angle = 0.0
	femur = _matrix_string((0.0, 0.0, 0.0))
	sphere = _sphere_matrix(neck_angle)
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(bcp_angle, side='Left')

	angle = calculate_femoral_anteversion(
		femur,
		bcp,
		femoral_sphere_matrix_str=sphere,
		bcp_p0_str=p0,
		bcp_p1_str=p1,
		side='Left',
	)

	expected = _expected_difference(30.0, 0.0)
	assert angle == pytest.approx(expected, abs=TOL)


def test_invalid_matrices_raise_value_error():
	femur = _matrix_string((0.0, 0.0, 0.0))
	bcp = _matrix_string((0.0, 0.0, 0.0))
	p0, p1 = _bcp_points(0.0, side='Right')

	with pytest.raises(ValueError):
		calculate_femoral_anteversion(
			femur,
			bcp,
			femoral_sphere_matrix_str="",
			bcp_p0_str=p0,
			bcp_p1_str=p1,
		)
