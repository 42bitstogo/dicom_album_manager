# tests/test_album.py
import unittest
import os
import shutil
from pathlib import Path
import logging
from dicom_manager.models.album import AlbumManager
from config.logging import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

class TestAlbumManager(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.test_dir = Path("./test_data")
        self.albums_dir = self.test_dir / "albums"
        
        # Create test directories
        self.test_dir.mkdir(exist_ok=True)
        self.albums_dir.mkdir(exist_ok=True)
        
        # Initialize manager
        self.album_manager = AlbumManager(str(self.test_dir))
        
    def tearDown(self):
        """Clean up test environment"""
        if self.test_dir.exists():
            shutil.rmtree(str(self.test_dir))
    
    def test_create_album(self):
        """Test album creation"""
        album = self.album_manager.create_album(
            name="Test Album",
            description="Test Description",
            creator="test_user"
        )
        
        self.assertIsNotNone(album)
        self.assertEqual(album.name, "Test Album")
        self.assertEqual(album.description, "Test Description")
        self.assertEqual(album.creator, "test_user")
        
        # Verify album was saved to disk
        album_file = self.albums_dir / f"{album.album_id}.json"
        self.assertTrue(album_file.exists())
    
    def test_add_remove_images(self):
        """Test adding and removing images from album"""
        album = self.album_manager.create_album("Test Album")
        
        # Create dummy image paths
        test_images = [
            str(self.test_dir / "image1.dcm"),
            str(self.test_dir / "image2.dcm")
        ]
        
        # Create empty files
        for img_path in test_images:
            Path(img_path).touch()
        
        # Add images
        success = self.album_manager.add_images_to_album(album.album_id, test_images)
        self.assertTrue(success)
        self.assertEqual(len(album.images), 2)
        
        # Remove images
        success = self.album_manager.remove_images_from_album(album.album_id, [test_images[0]])
        self.assertTrue(success)
        self.assertEqual(len(album.images), 1)
    
    def test_delete_album(self):
        """Test album deletion"""
        album = self.album_manager.create_album("Test Album")
        album_id = album.album_id
        
        success = self.album_manager.delete_album(album_id)
        self.assertTrue(success)
        
        # Verify album file was deleted
        album_file = self.albums_dir / f"{album_id}.json"
        self.assertFalse(album_file.exists())

if __name__ == '__main__':
    unittest.main(verbosity=2)