#!/usr/bin/env python3
"""Lightweight VTP viewer that mimics the EZplan LUT from load_nifti_and_stem."""

from __future__ import annotations

import argparse
import os
import sys

import vtk


EZPLAN_ZONE_DEFS = [
	(-200.0, 100.0, (0.0, 0.0, 1.0), "Loosening"),
	(100.0, 400.0, (1.0, 0.0, 1.0), "MicroMove"),
	(400.0, 1000.0, (0.0, 1.0, 0.0), "Stable"),
	(1000.0, 1500.0, (1.0, 0.0, 0.0), "Cortical"),
]
DEFAULT_ARRAY = "VolumeScalars"


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description=(
			"View a VTP stem file with the same EZplan HU LUT used by load_nifti_and_stem."
		)
	)
	parser.add_argument("vtp", help="Path to the .vtp file exported from Slicer")
	parser.add_argument(
		"--array",
		default=DEFAULT_ARRAY,
		help="Point-data scalar array to display (default: %(default)s)",
	)
	parser.add_argument(
		"--wireframe",
		action="store_true",
		help="Render the mesh in wireframe mode to inspect topology",
	)
	return parser.parse_args()


def _load_polydata(path: str) -> vtk.vtkPolyData:
	if not os.path.isfile(path):
		raise FileNotFoundError(path)
	reader = vtk.vtkXMLPolyDataReader()
	reader.SetFileName(path)
	reader.Update()
	poly = reader.GetOutput()
	if not poly or poly.GetNumberOfPoints() == 0:
		raise RuntimeError("VTP file '%s' produced empty polydata" % path)
	return poly


def _build_ezplan_transfer_function() -> vtk.vtkColorTransferFunction:
	tf = vtk.vtkColorTransferFunction()
	for zone_min, zone_max, (r, g, b), _label in EZPLAN_ZONE_DEFS:
		tf.AddRGBPoint(zone_min, r, g, b)
		tf.AddRGBPoint(zone_max, r, g, b)
	return tf


def _configure_mapper(
	poly: vtk.vtkPolyData,
	array_name: str,
) -> tuple[vtk.vtkPolyDataMapper, tuple[float, float]]:
	point_data = poly.GetPointData()
	array = point_data.GetArray(array_name)
	if array is None:
		available = [point_data.GetArrayName(i) for i in range(point_data.GetNumberOfArrays())]
		raise RuntimeError(
			"Scalar array '%s' not found. Available arrays: %s"
			% (array_name, ", ".join(filter(None, available)) or "<none>")
		)
	array_range = array.GetRange()
	mapper = vtk.vtkPolyDataMapper()
	mapper.SetInputData(poly)
	mapper.SetScalarModeToUsePointFieldData()
	mapper.SelectColorArray(array_name)
	mapper.SetColorModeToMapScalars()
	mapper.SetScalarRange(EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1])
	mapper.ScalarVisibilityOn()
	return mapper, array_range


def _build_actor(mapper: vtk.vtkPolyDataMapper, wireframe: bool) -> vtk.vtkActor:
	actor = vtk.vtkActor()
	actor.SetMapper(mapper)
	props = actor.GetProperty()
	props.SetAmbient(0.2)
	props.SetDiffuse(0.8)
	props.SetSpecular(0.3)
	props.SetSpecularPower(20.0)
	props.SetInterpolationToPhong()
	if wireframe:
		props.SetRepresentationToWireframe()
	return actor


def _add_scalar_bar(renderer: vtk.vtkRenderer, transfer_function: vtk.vtkColorTransferFunction):
	scalar_bar = vtk.vtkScalarBarActor()
	scalar_bar.SetLookupTable(transfer_function)
	scalar_bar.SetMaximumNumberOfColors(len(EZPLAN_ZONE_DEFS) * 2)
	scalar_bar.SetTitle("HU (EZplan)")
	scalar_bar.GetLabelTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.GetTitleTextProperty().SetColor(0.1, 0.1, 0.1)
	scalar_bar.SetNumberOfLabels(len(EZPLAN_ZONE_DEFS) + 1)
	renderer.AddActor2D(scalar_bar)


def _attach_lut(mapper: vtk.vtkPolyDataMapper, transfer_function: vtk.vtkColorTransferFunction):
	mapper.SetLookupTable(transfer_function)
	mapper.UseLookupTableScalarRangeOn()


def _print_summary(path: str, array_name: str, array_range: tuple[float, float]):
	print("Loaded '%s'" % path)
	print("Using scalar array '%s' (range %.2f .. %.2f)" % (array_name, array_range[0], array_range[1]))
	print("Color range fixed to %.1f .. %.1f (EZplan zones)" % (
		EZPLAN_ZONE_DEFS[0][0], EZPLAN_ZONE_DEFS[-1][1]
	))


def main() -> int:
	args = _parse_args()
	poly = _load_polydata(args.vtp)
	mapper, array_range = _configure_mapper(poly, args.array)
	transfer_function = _build_ezplan_transfer_function()
	_attach_lut(mapper, transfer_function)
	actor = _build_actor(mapper, args.wireframe)

	renderer = vtk.vtkRenderer()
	renderer.AddActor(actor)
	renderer.SetBackground(1.0, 1.0, 1.0)
	renderer.ResetCamera()
	_add_scalar_bar(renderer, transfer_function)

	render_window = vtk.vtkRenderWindow()
	render_window.SetWindowName("Stem Viewer (EZplan LUT)")
	render_window.AddRenderer(renderer)
	render_window.SetSize(900, 700)

	interactor = vtk.vtkRenderWindowInteractor()
	interactor.SetRenderWindow(render_window)
	style = vtk.vtkInteractorStyleTrackballCamera()
	interactor.SetInteractorStyle(style)

	_print_summary(args.vtp, args.array, array_range)
	interactor.Initialize()
	render_window.Render()
	interactor.Start()
	return 0


if __name__ == "__main__":
	try:
		raise SystemExit(main())
	except RuntimeError as exc:
		print("Error:", exc)
		raise SystemExit(1)
