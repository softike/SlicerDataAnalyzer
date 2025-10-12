import vtk

# Get the model node
#modelNode = getNode('YourModelNodeName')  # e.g., 'FemurModel'
modelNode = getNode('HU mapped iso ante=24') 
polyData = modelNode.GetPolyData()

# Get scalar array
scalarArray = polyData.GetPointData().GetArray('NRRDImage')
if not scalarArray:
    raise RuntimeError("No scalar array named 'NRRDImage' found.")

# Step 1: Threshold by scalar value (Stable zone: 400–1000)
thresholdFilter = vtk.vtkThreshold()
thresholdFilter.SetInputData(polyData)
thresholdFilter.SetLowerThreshold(400)  # Upper exclusive
thresholdFilter.SetUpperThreshold(999.999)  # Upper exclusive
thresholdFilter.SetInputArrayToProcess(0, 0, 0, vtk.vtkDataObject.FIELD_ASSOCIATION_POINTS, "NRRDImage")

# Convert to unstructured grid for connectivity filter
thresholdFilter.Update()
ugrid = thresholdFilter.GetOutput()

# Step 2: Extract connected components (regions)
connectivityFilter = vtk.vtkConnectivityFilter()
connectivityFilter.SetInputData(ugrid)
connectivityFilter.SetExtractionModeToAllRegions()
connectivityFilter.ColorRegionsOn()
connectivityFilter.Update()

numRegions = connectivityFilter.GetNumberOfExtractedRegions()
print(f"Number of spatially disconnected 'Stable' regions: {numRegions}")
