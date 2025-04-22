"""
Unit tests for the screenshot handler module.
"""
import os
import unittest
from unittest.mock import patch, mock_open
import tempfile

from tarkov_app.screenshot_handler import ScreenshotHandler, Coordinates


class TestScreenshotHandler(unittest.TestCase):
    """Test cases for the ScreenshotHandler class."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.handler = ScreenshotHandler(self.temp_file.name)
    
    def tearDown(self):
        """Clean up test environment."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_extract_coordinates_valid(self):
        """Test extracting coordinates from a valid filename."""
        filename = "2024-03-16[02-20]_-9.1, 33.6, 166.4_0.0, -1.0, 0.2, 0.1_12.33 (0).png"
        coords = self.handler.extract_coordinates(filename)
        
        self.assertEqual(coords.x, -9.1)
        self.assertEqual(coords.y, 33.6)
        self.assertEqual(coords.z, 166.4)
    
    def test_extract_coordinates_invalid(self):
        """Test extracting coordinates from an invalid filename."""
        filename = "invalid_filename.png"
        
        with self.assertRaises(ValueError):
            self.handler.extract_coordinates(filename)
    
    def test_save_coordinates(self):
        """Test saving coordinates to file."""
        coords = Coordinates(x=10.5, y=20.5, z=30.5)
        
        with patch('builtins.open', mock_open()) as mocked_file:
            self.handler.save_coordinates(coords)
            mocked_file.assert_called_once_with(self.temp_file.name, 'a')
            mocked_file().write.assert_called_once()
            # Check that coordinates are in the written data
            args, _ = mocked_file().write.call_args
            self.assertIn("10.5", args[0])
            self.assertIn("20.5", args[0])
            self.assertIn("30.5", args[0])
    
    def test_get_latest_coordinates_empty_file(self):
        """Test getting latest coordinates from an empty file."""
        # Just create the file with no content
        with open(self.temp_file.name, 'w') as f:
            pass
            
        coords = self.handler.get_latest_coordinates()
        self.assertIsNone(coords)
    
    def test_get_latest_coordinates(self):
        """Test getting latest coordinates from file with data."""
        # Write test data to the file
        with open(self.temp_file.name, 'w') as f:
            f.write("# Comment line\n")
            f.write("1.1, 2.2, 3.3, 2024-01-01 12:00:00\n")
            f.write("4.4, 5.5, 6.6, 2024-01-02 12:00:00\n")
        
        coords = self.handler.get_latest_coordinates()
        self.assertIsNotNone(coords)
        self.assertEqual(coords.x, 4.4)
        self.assertEqual(coords.y, 5.5)
        self.assertEqual(coords.z, 6.6)
    
    def test_get_all_coordinates(self):
        """Test getting all coordinates from file."""
        # Write test data to the file
        with open(self.temp_file.name, 'w') as f:
            f.write("# Comment line\n")
            f.write("1.1, 2.2, 3.3, 2024-01-01 12:00:00\n")
            f.write("4.4, 5.5, 6.6, 2024-01-02 12:00:00\n")
        
        coords_list = self.handler.get_all_coordinates()
        self.assertEqual(len(coords_list), 2)
        
        # Check first entry
        coords1, timestamp1 = coords_list[0]
        self.assertEqual(coords1.x, 1.1)
        self.assertEqual(coords1.y, 2.2)
        self.assertEqual(coords1.z, 3.3)
        self.assertEqual(timestamp1, "2024-01-01 12:00:00")
        
        # Check second entry
        coords2, timestamp2 = coords_list[1]
        self.assertEqual(coords2.x, 4.4)
        self.assertEqual(coords2.y, 5.5)
        self.assertEqual(coords2.z, 6.6)
        self.assertEqual(timestamp2, "2024-01-02 12:00:00")


if __name__ == '__main__':
    unittest.main()