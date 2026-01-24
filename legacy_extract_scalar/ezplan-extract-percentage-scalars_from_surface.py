# Get the model node
#modelNode = getNode('YourModelNodeName')  # e.g., 'FemurModel'
modelNode = getNode('HU mapped iso ante=24') 

# Get the polydata
polyData = modelNode.GetPolyData()

# Get the scalar array from point data
scalarArray = polyData.GetPointData().GetArray('NRRDImage')

if not scalarArray:
    print("No scalar field named 'NRRDImage' found in point data.")
else:
    numPoints = polyData.GetNumberOfPoints()
    
    # Zone definitions
    zones = {
        'Loosening': {'range': (-200, 100), 'count': 0},
        'MicroMove': {'range': (100, 400), 'count': 0},
        'Stable': {'range': (400, 1000), 'count': 0},
        'Cortical': {'range': (1000, 2000), 'count': 0}
    }

    # Classify each scalar value into the correct zone
    for i in range(numPoints):
        value = scalarArray.GetTuple1(i)
        for name, zone in zones.items():
            rmin, rmax = zone['range']
            if rmin <= value < rmax:
                zone['count'] += 1
                break  # Assuming non-overlapping ranges

    # Compute and print percentages
    print("Zone distribution (based on NRRDImage scalar field):")
    for name, zone in zones.items():
        percentage = (zone['count'] / numPoints) * 100 if numPoints > 0 else 0
        print(f"  {name}: {zone['count']} points ({percentage:.2f}%)")
