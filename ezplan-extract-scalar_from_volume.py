# Get the volume node (replace with your actual volume node name)
#volumeNode = getNode('YourVolumeNodeName')  # e.g., 'MRHead'

volumeNode = getNode('YourVolumeNodeName') 

# Get the image data (vtkImageData)
imageData = volumeNode.GetImageData()

# Get the scalar field (array) – usually at index 0
scalarArray = imageData.GetPointData().GetScalars()

# Check the name
print(f"Scalar name: {scalarArray.GetName()}")

# If you want to rename it to 'NRRDImage', you can do:
scalarArray.SetName('NRRDImage')