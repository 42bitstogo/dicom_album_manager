from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
import json
import os
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

@dataclass
class DicomAlbum:
    album_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: datetime = field(default_factory=datetime.now)
    creator: str = "system"
    images: List[str] = field(default_factory=list)  # List of DICOM file paths
    metadata: Dict[str, any] = field(default_factory=dict)
    sharing_url: Optional[str] = None
    
class AlbumManager:
    def __init__(self, base_directory: str):
        self.base_directory = base_directory
        self.albums_directory = os.path.join(base_directory, "albums")
        self.albums: Dict[str, DicomAlbum] = {}
        self._ensure_directory_exists()
        self._load_existing_albums()
        
    def _ensure_directory_exists(self):
        """Create albums directory if it doesn't exist"""
        os.makedirs(self.albums_directory, exist_ok=True)
        logger.info(f"Albums directory ensured at: {self.albums_directory}")
        
    def _load_existing_albums(self):
        """Load existing albums from disk"""
        if not os.path.exists(self.albums_directory):
            return
            
        for filename in os.listdir(self.albums_directory):
            if filename.endswith('.json'):
                try:
                    with open(os.path.join(self.albums_directory, filename), 'r') as f:
                        data = json.load(f)
                        album = DicomAlbum(
                            album_id=data['album_id'],
                            name=data['name'],
                            description=data.get('description'),
                            created_at=datetime.fromisoformat(data['created_at']),
                            modified_at=datetime.fromisoformat(data['modified_at']),
                            creator=data.get('creator', 'system'),
                            images=data.get('images', []),
                            metadata=data.get('metadata', {}),
                            sharing_url=data.get('sharing_url')
                        )
                        self.albums[album.album_id] = album
                        logger.info(f"Loaded album: {album.name} ({album.album_id})")
                except Exception as e:
                    logger.error(f"Error loading album {filename}: {e}")
    
    def create_album(self, name: str, description: Optional[str] = None, 
                    creator: str = "system") -> DicomAlbum:
        """Create a new album"""
        album_id = str(uuid4())
        album = DicomAlbum(
            album_id=album_id,
            name=name,
            description=description,
            creator=creator
        )
        self.albums[album_id] = album
        self._save_album(album)
        logger.info(f"Created new album: {name} ({album_id})")
        return album
    
    def add_images_to_album(self, album_id: str, image_paths: List[str]) -> bool:
        """Add images to an existing album"""
        if album_id not in self.albums:
            logger.error(f"Album {album_id} not found")
            return False
            
        album = self.albums[album_id]
        for path in image_paths:
            if path not in album.images and os.path.exists(path):
                album.images.append(path)
                
        album.modified_at = datetime.now()
        self._save_album(album)
        logger.info(f"Added {len(image_paths)} images to album {album_id}")
        return True
    
    def remove_images_from_album(self, album_id: str, image_paths: List[str]) -> bool:
        """Remove images from an album"""
        if album_id not in self.albums:
            logger.error(f"Album {album_id} not found")
            return False
            
        album = self.albums[album_id]
        for path in image_paths:
            if path in album.images:
                album.images.remove(path)
                
        album.modified_at = datetime.now()
        self._save_album(album)
        logger.info(f"Removed {len(image_paths)} images from album {album_id}")
        return True
    
    def _save_album(self, album: DicomAlbum):
        """Save album to disk"""
        album_data = {
            'album_id': album.album_id,
            'name': album.name,
            'description': album.description,
            'created_at': album.created_at.isoformat(),
            'modified_at': album.modified_at.isoformat(),
            'creator': album.creator,
            'images': album.images,
            'metadata': album.metadata,
            'sharing_url': album.sharing_url
        }
        
        filepath = os.path.join(self.albums_directory, f"{album.album_id}.json")
        with open(filepath, 'w') as f:
            json.dump(album_data, f, indent=2)
        logger.debug(f"Saved album to disk: {filepath}")
    
    def delete_album(self, album_id: str) -> bool:
        """Delete an album"""
        if album_id not in self.albums:
            logger.error(f"Album {album_id} not found")
            return False
            
        filepath = os.path.join(self.albums_directory, f"{album_id}.json")
        if os.path.exists(filepath):
            os.remove(filepath)
            
        del self.albums[album_id]
        logger.info(f"Deleted album {album_id}")
        return True
    
    def get_album(self, album_id: str) -> Optional[DicomAlbum]:
        """Get album by ID"""
        return self.albums.get(album_id)
    
    def list_albums(self) -> List[DicomAlbum]:
        """List all albums"""
        return list(self.albums.values())