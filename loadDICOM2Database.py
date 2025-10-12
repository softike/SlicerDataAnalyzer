import slicer
from DICOMLib import DICOMUtils

dcm_path = r"C:\\Users\\Coder\\Desktop\\001-M-30\\001-M-30\\Dataset"

##
def loadDICOMToDatabase(dcm_path):
    """
    Load DICOM files from a specified path into the Slicer DICOM database.
    """
    # instantiate a new DICOM browser
    slicer.util.selectModule("DICOM")
    dicomBrowser = slicer.modules.DICOMWidget.browserWidget.dicomBrowser
    # use dicomBrowser.ImportDirectoryCopy to make a copy of the files (useful for importing data from removable storage)
    dicomBrowser.importDirectory(dcm_path, dicomBrowser.ImportDirectoryAddLink)
    # wait for import to finish before proceeding (optional, if removed then import runs in the background)
    dicomBrowser.waitForImportFinished()

    dicomDatabase = slicer.dicomDatabase
    patientUIDs = dicomDatabase.patients()

    for patientUID in patientUIDs:
        studies = dicomDatabase.studiesForPatient(patientUID)
        for studyUID in studies:
            seriesUIDs = dicomDatabase.seriesForStudy(studyUID)
            for seriesUID in seriesUIDs:
                print("Found series:", seriesUID)