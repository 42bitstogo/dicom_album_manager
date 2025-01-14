# tests/test_query_interface.py
import unittest
import logging
from datetime import datetime
from pathlib import Path
from dicom_manager.models.dicom_data import DicomDataManager
from dicom_manager.models.album import AlbumManager
from dicom_manager.models.query import DicomQuery
from config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class TestDicomQuery(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.dicom_dir = Path("./DICOM")
        if not self.dicom_dir.exists():
            self.skipTest("DICOM directory not found. Please set up test data first.")
        
        # Initialize managers
        self.data_manager = DicomDataManager(str(self.dicom_dir))
        self.query = DicomQuery(self.data_manager)
        
        # Scan directory
        count = self.data_manager.scan_directory(str(self.dicom_dir))
        logger.info(f"Scanned {count} DICOM files")
        
        # Log what we found
        logger.info(f"Found {len(self.data_manager.patients)} patients")
        for patient_id, patient in self.data_manager.patients.items():
            logger.info(f"Patient {patient_id}:")
            logger.info(f"  Studies: {len(patient.studies)}")
            for study_uid, study in patient.studies.items():
                logger.info(f"  Study {study_uid}:")
                logger.info(f"    Series: {len(study.series)}")
    
    def test_query_by_metadata(self):
        """Test metadata-based patient queries"""
        # Query by patient ID
        logger.info("Testing query by patient ID")
        results = self.query.query_by_metadata(patient_id="NOID")  # Using NOID from actual test data
        logger.info(f"Query returned {len(results)} results")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].patient_id, "NOID")

        # Query by patient name if available
        patient = next(iter(self.data_manager.patients.values()))
        if patient.patient_name:
            logger.info(f"Testing query by patient name: {patient.patient_name}")
            results = self.query.query_by_metadata(patient_name=patient.patient_name)
            self.assertEqual(len(results), 1)
            self.assertEqual(results[0].patient_name, patient.patient_name)
    
    def test_query_by_study(self):
        """Test study queries"""
        logger.info("Testing query by study")
        # Get study info from actual data
        known_study_id = "1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.4.0"
        patient = self.data_manager.patients.get("NOID")
        study = patient.studies.get(known_study_id)
        
        # Query by study description
        if study.study_description:
            logger.info(f"Querying for study description: {study.study_description}")
            results = self.query.query_by_study(description=study.study_description)
            self.assertGreater(len(results), 0)
            self.assertEqual(results[0].study_description, study.study_description)
    
    def test_query_by_series(self):
        """Test series queries"""
        logger.info("Testing query by series")
        # Get series info from actual data
        known_series_id = "1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.5.0"
        patient = self.data_manager.patients.get("NOID")
        study = patient.studies.get("1.3.6.1.4.1.5962.99.1.5128099.2103784727.1533308485539.4.0")
        series = study.series.get(known_series_id)
        
        # Query by modality
        if series.modality:
            logger.info(f"Querying for modality: {series.modality}")
            results = self.query.query_by_series(modality=series.modality)
            self.assertGreater(len(results), 0)
            self.assertTrue(any(s.modality == series.modality for s in results))
        
        # Query by series number
        if series.series_number is not None:
            logger.info(f"Querying for series number: {series.series_number}")
            results = self.query.query_by_series(series_number=series.series_number)
            self.assertGreater(len(results), 0)
            self.assertTrue(any(s.series_number == series.series_number for s in results))

if __name__ == '__main__':
    unittest.main(verbosity=2)