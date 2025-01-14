# dicom_manager/models/query.py
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
from dicom_manager.models.dicom_data import DicomDataManager, DicomPatient, DicomStudy, DicomSeries

logger = logging.getLogger(__name__)

class DicomQuery:
    def __init__(self, data_manager: DicomDataManager):
        self.data_manager = data_manager
    
    def _date_matches(self, study_date: Optional[datetime], 
                     date_from: Optional[datetime], 
                     date_to: Optional[datetime]) -> bool:
        """Helper to check if a date falls within a range"""
        if study_date is None:
            return False
        if date_from and study_date < date_from:
            return False
        if date_to and study_date > date_to:
            return False
        return True
    
    def query_by_metadata(self, 
                        patient_id: Optional[str] = None,
                        patient_name: Optional[str] = None) -> List[DicomPatient]:
        """Query patients based on ID or name"""
        results = []
        logger.debug(f"Querying patients with ID={patient_id}, name={patient_name}")
        logger.debug(f"Total patients in database: {len(self.data_manager.patients)}")
        
        for patient in self.data_manager.patients.values():
            logger.debug(f"Checking patient {patient.patient_id} ({patient.patient_name})")
            
            if patient_id and patient.patient_id != patient_id:
                logger.debug(f"Patient ID mismatch: {patient.patient_id} != {patient_id}")
                continue
            if patient_name and patient.patient_name != patient_name:
                logger.debug(f"Patient name mismatch: {patient.patient_name} != {patient_name}")
                continue
                
            logger.debug(f"Found matching patient: {patient.patient_id}")
            results.append(patient)
            
        logger.debug(f"Found {len(results)} matching patients")
        return results
    
    def query_by_study(self,
                      study_date_from: Optional[datetime] = None,
                      study_date_to: Optional[datetime] = None,
                      description: Optional[str] = None) -> List[DicomStudy]:
        """Query studies based on date range and description"""
        results = []
        logger.debug(f"Querying studies with date_from={study_date_from}, date_to={study_date_to}, description={description}")
        
        for patient in self.data_manager.patients.values():
            logger.debug(f"Checking studies for patient {patient.patient_id}")
            for study in patient.studies.values():
                logger.debug(f"Checking study {study.study_instance_uid}")
                
                if not self._date_matches(study.study_date, study_date_from, study_date_to):
                    logger.debug("Date mismatch")
                    continue
                    
                if description and description.lower() not in (study.study_description or "").lower():
                    logger.debug("Description mismatch")
                    continue
                    
                logger.debug("Found matching study")
                results.append(study)
                
        logger.debug(f"Found {len(results)} matching studies")
        return results
    
    def query_by_series(self,
                       modality: Optional[str] = None,
                       series_number: Optional[int] = None,
                       description: Optional[str] = None) -> List[DicomSeries]:
        """Query series based on modality, number, and description"""
        results = []
        logger.debug(f"Querying series with modality={modality}, number={series_number}, description={description}")
        
        for patient in self.data_manager.patients.values():
            logger.debug(f"Checking series for patient {patient.patient_id}")
            for study in patient.studies.values():
                logger.debug(f"Checking study {study.study_instance_uid}")
                for series in study.series.values():
                    logger.debug(f"Checking series {series.series_instance_uid}")
                    
                    if modality and series.modality != modality:
                        logger.debug(f"Modality mismatch: {series.modality} != {modality}")
                        continue
                    if series_number is not None and series.series_number != series_number:
                        logger.debug(f"Series number mismatch: {series.series_number} != {series_number}")
                        continue
                    if description and description.lower() not in (series.series_description or "").lower():
                        logger.debug("Description mismatch")
                        continue
                        
                    logger.debug("Found matching series")
                    results.append(series)
                    
        logger.debug(f"Found {len(results)} matching series")
        return results

__all__ = ['DicomQuery']