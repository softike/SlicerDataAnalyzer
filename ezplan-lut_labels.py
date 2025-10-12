import slicer
from vtk import vtkColorTransferFunction

# Create procedural color node
colorNode = slicer.vtkMRMLProceduralColorNode()
colorNode.SetName("EZplanHUZones")
colorFunction = vtkColorTransferFunction()

# Zone 1 : loosening
# Zone 2 : micro-movement
# Zone 3 : stable
# Zone 4 : cortical 

# Define the 4 ranges with desired colors
#colorNode.SetAttribute("Category", "Loosening")  # Set the name of the zone for UI display
colorFunction.AddRGBPoint(-200, 1, 0.5, 0)   # Zone 1 Start (Loosening - Orange)
colorFunction.AddRGBPoint(100, 1, 0.5, 0)    # Zone 1 End

#colorNode.SetAttribute("Category", "MicroMove")  # Set the name of the zone for UI display
colorFunction.AddRGBPoint(100.1, 1, 1, 0)  # Zone 2 Start (Yellow)
colorFunction.AddRGBPoint(400, 1, 1, 0)    # Zone 2 End

#colorNode.SetAttribute("Category", "Stable")  # Set the name of the zone for UI display
colorFunction.AddRGBPoint(400.1, 0, 1, 0)  # Zone 3 Start (Green)
colorFunction.AddRGBPoint(1000, 0, 1, 0)   # Zone 3 End

#colorNode.SetAttribute("Category", "Cortical")  # Set the name of the zone for UI display
colorFunction.AddRGBPoint(1000.1, 1, 0, 0) # Zone 4 Start (Red)
colorFunction.AddRGBPoint(1500, 1, 0, 0)   # Zone 4 End

colorNode.SetAndObserveColorTransferFunction(colorFunction)
slicer.mrmlScene.AddNode(colorNode)
