import argparse
import os
import sys

import slicer
import slicer.util as su
from vtk import vtkColorTransferFunction

ZONE_DEFS = [
	(-200.0, 100.0, (0.0, 0.0, 1.0), "Loosening"),
	(100.0, 400.0, (1.0, 0.0, 1.0), "MicroMove"),
	(400.0, 1000.0, (0.0, 1.0, 0.0), "Stable"),
	(1000.0, 1500.0, (1.0, 0.0, 0.0), "Cortical"),
]


def _script_argv() -> list[str]:
	if "--" in sys.argv:
		idx = sys.argv.index("--")
		return sys.argv[idx + 1 :]
	return sys.argv[1:]


def _parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(
		description="Create the EZplan HU zone LUT inside Slicer and optionally export it as a .json color file."
	)
	parser.add_argument(
		"--name",
		default="EZplan HU Zones",
		help="Display name for the color node (default: 'EZplan HU Zones')",
	)
	parser.add_argument(
		"--category",
		default="Implant Scalars",
		help="Category label shown in the Colors module (default: 'Implant Scalars')",
	)
	parser.add_argument(
		"--save",
		dest="save_path",
		help="Optional path to save the LUT as a .json file for reuse",
	)
	parser.add_argument(
		"--overwrite",
		action="store_true",
		help="Overwrite existing color node with the same name if it already exists",
	)
	return parser.parse_args(_script_argv())


def _remove_existing(name: str):
	existing_nodes = su.getNodesByClass("vtkMRMLProceduralColorNode")
	for node in existing_nodes.values():
		if node.GetName() == name:
			slicer.mrmlScene.RemoveNode(node)


def _build_color_node(name: str, category: str) -> slicer.vtkMRMLProceduralColorNode:
	node = slicer.vtkMRMLProceduralColorNode()
	node.SetName(name)
	node.SetAttribute("Category", category)
	func = vtkColorTransferFunction()
	for zone_min, zone_max, (r, g, b), _label in ZONE_DEFS:
		func.AddRGBPoint(zone_min, r, g, b)
		func.AddRGBPoint(zone_max, r, g, b)
	node.SetAndObserveColorTransferFunction(func)
	return node


def _save_node(node: slicer.vtkMRMLProceduralColorNode, path: str):
	path = os.path.abspath(path)
	folder = os.path.dirname(path)
	if folder and not os.path.isdir(folder):
		os.makedirs(folder, exist_ok=True)
	if not path.lower().endswith(".json"):
		path = f"{path}.json"
	su.saveNode(node, path)
	print(f"Saved LUT to {path}")


def main():
	args = _parse_args()
	if args.overwrite:
		_remove_existing(args.name)

	color_node = _build_color_node(args.name, args.category)
	added_node = slicer.mrmlScene.AddNode(color_node)
	added_node.SetAttribute("lut.source", "ezplan-lut-labels")
	print(f"Registered '{args.name}' LUT in category '{args.category}'")

	if args.save_path:
		_save_node(added_node, args.save_path)


if __name__ == "__main__":
	main()
