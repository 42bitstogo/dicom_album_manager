from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import pydicom
import os
import logging

logger = logging.getLogger(__name__)

@dataclass
class DicomImage:
    file_path: str
    study_id: str
    series_id: str
    metadata: Dict[str, any] = field(default_factory=dict)

@dataclass
class DicomSeries:
    series_instance_uid: str
    series_description: Optional[str] = None
    modality: str = ""
    series_number: Optional[int] = None
    images: List[str] = field(default_factory=list)

@dataclass
class DicomStudy:
    study_instance_uid: str
    study_date: Optional[datetime] = None
    study_description: Optional[str] = None
    series: Dict[str, DicomSeries] = field(default_factory=dict)

@dataclass
class DicomPatient:
    patient_id: str
    patient_name: Optional[str] = None
    studies: Dict[str, DicomStudy] = field(default_factory=dict)

class DicomDataManager:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.patients: Dict[str, DicomPatient] = {}
        logger.info(f"Initialized DicomDataManager with base directory: {base_directory}")
    
    def process_dicom_file(self, file_path: str) -> bool:
        """Process a single DICOM file and add it to the hierarchy"""
        try:
            logger.debug(f"Processing file: {file_path}")
            ds = pydicom.dcmread(file_path)
            
            # Extract required DICOM tags with fallbacks
            patient_id = str(getattr(ds, 'PatientID', 'unknown'))
            logger.debug(f"Found PatientID: {patient_id}")
            
            study_uid = str(getattr(ds, 'StudyInstanceUID', None) or 'study_1')
            series_uid = str(getattr(ds, 'SeriesInstanceUID', None) or 'series_1')
            
            logger.debug(f"Study UID: {study_uid}, Series UID: {series_uid}")
            
            # Create or get patient
            if patient_id not in self.patients:
                logger.info(f"Creating new patient record for ID: {patient_id}")
                self.patients[patient_id] = DicomPatient(
                    patient_id=patient_id,
                    patient_name=str(getattr(ds, 'PatientName', ''))
                )
            patient = self.patients[patient_id]
            
            # Create or get study
            if study_uid not in patient.studies:
                study_date = None
                if hasattr(ds, 'StudyDate'):
                    try:
                        study_date = datetime.strptime(ds.StudyDate, '%Y%m%d')
                    except ValueError:
                        logger.warning(f"Invalid study date format in file: {file_path}")
                
                logger.info(f"Creating new study record for UID: {study_uid}")
                patient.studies[study_uid] = DicomStudy(
                    study_instance_uid=study_uid,
                    study_date=study_date,
                    study_description=str(getattr(ds, 'StudyDescription', ''))
                )
            study = patient.studies[study_uid]
            
            # Create or get series
            if series_uid not in study.series:
                # logger.info(f"Creating new series record for UID: {series_uid}")
                study.series[series_uid] = DicomSeries(
                    series_instance_uid=series_uid,
                    series_description=str(getattr(ds, 'SeriesDescription', '')),
                    modality=str(getattr(ds, 'Modality', '')),
                    series_number=getattr(ds, 'SeriesNumber', None)
                )
            series = study.series[series_uid]
            
            # Add image file path if not already present
            if file_path not in series.images:
                logger.debug(f"Adding new image to series: {file_path}")
                series.images.append(file_path)
            
            return True
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}", exc_info=True)
            return False
    
    def scan_directory(self, directory: str) -> int:
        """Scan directory for DICOM files and process them"""
        processed_count = 0
        
        logger.info(f"Starting directory scan: {directory}")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.startswith('I'):  # Modified to match your file naming
                    file_path = os.path.join(root, file)
                    logger.debug(f"Found potential DICOM file: {file_path}")
                    if self.process_dicom_file(file_path):
                        processed_count += 1
        
        logger.info(f"Directory scan complete. Total processed: {processed_count}")
        return processed_count