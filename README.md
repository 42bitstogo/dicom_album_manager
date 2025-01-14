# DICOM Album Creator

A Python-based utility for creating and managing shareable albums from locally stored DICOM images.

## Project Overview

With this album creator and manager we aim to solve the challenge of sharing specific subsets of DICOM images from local envs with researched. The traditional PACS envs and manual sharing methdos are cumbersome and time-consuming. We provide a streamlined approach to organise and share DICOM data.

### Key Features

#### Implemented
- complete DICOM hierarchy management (Patient → Study → Series → Image)
- metadata extraction and storage
- query interface for searching DICOM data
- album creation and management
- logging
- command-line interface for all operations
- persistent storage of albums and metadata -> simple jsons are used for this
- some unit tests with real DICOM data support

#### Planned
- integration with Kheops for image viewing
- OHIF Viewer integration for web-based image viewing
- URLs sharing functionality
- web interface for album management
- PACS environment integration
- authentication and authorization 
- support for different sharing modes and permissions

## Prerequisites

- Python 3.9+
- Virtual environment (recommended)
- Required Python packages:
  - pydicom >= 2.4.0
  - python-dateutil >= 2.8.2
  - pytest >= 7.4.0
  - logging >= 0.4.9.6

## Installation

1. Clone the repository:
```bash
git clone https://github.com/42bitstogo/dicom_album_manager
cd dicom_album_manager
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Project Structure

```
dicom_album_manager/
├── config/
│   ├── __init__.py
│   └── logging.py          # Logging configuration
├── dicom_manager/
│   ├── __init__.py
│   └── models/
│       ├── __init__.py
│       ├── dicom_data.py   # Core DICOM data structures
│       ├── query.py        # DICOM query interface
│       └── album.py        # Album management
├── tests/
│   ├── __init__.py
│   ├── test_dicom_manager.py
│   ├── test_query_interface.py
│   └── test_album_manager.py
├── cli.py                  # Command-line interface
└── DICOM/                  # Place DICOM files here
```

## Usage

### Command Line Interface

The project provides a comprehensive CLI for all operations:

1. Scanning DICOM directories:
```bash
python cli.py scan ./path/to/dicom/files
```

2. Creating albums:
```bash
python cli.py create-album --name "My Album" --description "Description"
```

3. Adding images to albums:
```bash
python cli.py add-images ALBUM_ID /path/to/image1.dcm /path/to/image2.dcm
```

4. Querying DICOM data:
```bash
# Query by patient
python cli.py query by-patient --patient-id "123"

# Query by study
python cli.py query by-study --date-from "2024-01-01" --description "CT Scan"

# Query by series
python cli.py query by-series --modality "CT" --series-number 1
```

5. Creating albums from query results:
```bash
python cli.py create-from-query --album-name "CT Scans" --query-type series --modality "CT"
```

### Programmatic Usage

```python
from dicom_manager.models.dicom_data import DicomDataManager
from dicom_manager.models.album import AlbumManager
from dicom_manager.models.query import DicomQuery

# Initialize managers
data_manager = DicomDataManager("./DICOM")
album_manager = AlbumManager("./DICOM")
query = DicomQuery(data_manager)

# Scan for DICOM files
data_manager.scan_directory("./DICOM")

# Create an album
album = album_manager.create_album("My Album", "Description")

# Query for specific images
results = query.query_by_series(modality="CT")

# Add images to album
album_manager.add_images_to_album(album.album_id, [image.file_path for image in results])
```

## Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m unittest tests/test_dicom_manager.py

# Run with verbose output
python -m pytest -v tests/
```

## Roadmap

1. **Phase 1 - Core Functionality** ✅
   - DICOM data management
   - Query interface
   - Album management
   - CLI implementation

2. **Phase 2 - Integration** (In Progress)
   - Kheops integration
   - OHIF Viewer integration
   - URL-based sharing system

3. **Phase 3 - Web Interface**
   - User interface development
   - Authentication system
   - Access control implementation

4. **Phase 4 - Advanced Features**
   - PACS integration
   - Automated album creation
   - Batch processing capabilities

## Acknowledgments

- Mentors: Ananth Reddy and Pradeeban Kathiravelu
- KathiraveluLab team