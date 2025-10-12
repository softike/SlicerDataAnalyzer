# Get the model node (replace with your actual model name)
#modelNode = getNode('YourModelNodeName')  # e.g., 'FemurModel'
modelNode = getNode('HU mapped iso ante=24') 

# Get the polydata (geometry and associated data)
polyData = modelNode.GetPolyData()

# Check in point data first
pointDataArray = polyData.GetPointData().GetArray('NRRDImage')

if pointDataArray:
    print("Found 'NRRDImage' in point data.")
else:
    # Try cell data if not in point data
    cellDataArray = polyData.GetCellData().GetArray('NRRDImage')
    if cellDataArray:
        print("Found 'NRRDImage' in cell data.")
    else:
        print("Scalar field 'NRRDImage' not found.")

scalarArray = polyData.GetPointData().GetArray('NRRDImage')

if not scalarArray:
    print("No scalar field named 'NRRDImage' found in point data.")
else:
    numPoints = polyData.GetNumberOfPoints()
    print(f"Scalar values for {numPoints} points:")
    for i in range(numPoints):
        value = scalarArray.GetTuple1(i)
        point = polyData.GetPoint(i)
        print(f"Point {i}: {point} → NRRDImage = {value}")