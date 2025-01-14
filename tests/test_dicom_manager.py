import unittest
import os
import pydicom
import logging,sys
from dicom_manager.models.dicom_data import DicomDataManager
from config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class TestDicomDataManagerRealData(unittest.TestCase):
    def setUp(self):
        self.dicom_dir = "./DICOM"
        logger.info(f"Looking for DICOM files in: {os.path.abspath(self.dicom_dir)}")
        
        self.files = []
        if os.path.exists(self.dicom_dir):
            for root, _, files in os.walk(self.dicom_dir):
                for file in files:
                    if file.startswith('I'):
                        full_path = os.path.join(root, file)
                        self.files.append(full_path)
                        
            logger.info(f"Found {len(self.files)} potential DICOM files")
            
            if self.files:
                try:
                    ds = pydicom.dcmread(self.files[0])
                    logger.debug(
                        f"Successfully read first DICOM file: {self.files[0]}\n"
                        f"DICOM tags found: PatientID={getattr(ds, 'PatientID', 'missing')}, "
                        f"Modality={getattr(ds, 'Modality', 'missing')}"
                    )
                except Exception as e:
                    logger.error(f"Error reading first DICOM file: {e}", exc_info=True)
        else:
            logger.error(f"Directory {self.dicom_dir} does not exist!")
        
        self.manager = DicomDataManager(self.dicom_dir)

    def test_scan_directory(self):
        logger.info("Testing directory scan...")
        processed_count = self.manager.scan_directory(self.dicom_dir)
        
        logger.info(f"Processed {processed_count} DICOM files")
        logger.info(f"Found {len(self.manager.patients)} patients")
        
        if processed_count == 0:
            logger.warning("No files were processed, attempting direct file read")
            if self.files:
                try:
                    file_path = self.files[0]
                    ds = pydicom.dcmread(file_path)
                    logger.debug(
                        f"Direct file read successful: "
                        f"PatientID={getattr(ds, 'PatientID', 'missing')}"
                    )
                except Exception as e:
                    logger.error(f"Error reading file: {e}", exc_info=True)
        
        self.assertGreater(processed_count, 0, "No DICOM files were processed")

    def test_hierarchy_details(self):
        self.manager.scan_directory(self.dicom_dir)
        
        patient = self.manager.patients.get("NOID")
        self.assertIsNotNone(patient, "Should find patient with ID 'NOID'")
        
        # Log patient details
        logger.info("\nPatient Details:")
        logger.info(f"ID: {patient.patient_id}")
        logger.info(f"Number of studies: {len(patient.studies)}")
        
        # Get the study we know exists
        study_id = "1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.4.0"
        study = patient.studies.get(study_id)
        self.assertIsNotNone(study, "Should find the known study")
        
        # Log study details
        logger.info("\nStudy Details:")
        logger.info(f"ID: {study.study_instance_uid}")
        logger.info(f"Number of series: {len(study.series)}")
        
        # Get the series we know exists
        series_id = "1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.5.0"
        series = study.series.get(series_id)
        self.assertIsNotNone(series, "Should find the known series")
        
        # Log series details
        logger.info("\nSeries Details:")
        logger.info(f"ID: {series.series_instance_uid}")
        logger.info(f"Number of images: {len(series.images)}")
        logger.info(f"Modality: {series.modality}")
        
        # Verify image count
        self.assertEqual(len(series.images), 517, 
                        "Should have all images in the series")
        
        # Log sample image paths
        logger.info("\nSample Image Paths:")
        for path in list(series.images)[:5]:
            logger.info(f"- {path}")

    def test_metadata_extraction(self):
        """Test extraction of additional metadata"""
        self.manager.scan_directory(self.dicom_dir)
        
        # Get sample DICOM file
        sample_file = self.files[0]
        ds = pydicom.dcmread(sample_file)
        
        logger.debug("\nAvailable DICOM tags in sample file:")
        for elem in ds:
            if elem.keyword:  # Only log named elements
                logger.debug(f"{elem.keyword}: {elem.value}")

if __name__ == '__main__':
    unittest.main(verbosity=2)