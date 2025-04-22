"""
Screenshot handling module for the Tarkov Map Assistant.

This module provides functionality to extract coordinates from screenshot filenames
and manage screenshot data.
"""
import os
import re
import logging
from typing import Tuple, Optional, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class Coordinates:
    """Data class to store extracted coordinates."""
    x: float
    y: float
    z: float
    
    def __str__(self) -> str:
        return f"X: {self.x}, Y: {self.y}, Z: {self.z}"

class ScreenshotHandler:
    """Handles screenshots and coordinate extraction."""
    
    def __init__(self, coord_file_path: str):
        """
        Initialize the screenshot handler.
        
        Args:
            coord_file_path: Path to the file storing coordinates
        """
        self.coord_file_path = coord_file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the coordinates file exists."""
        if not os.path.exists(self.coord_file_path):
            try:
                # Create file and parent directories if they don't exist
                os.makedirs(os.path.dirname(self.coord_file_path), exist_ok=True)
                with open(self.coord_file_path, 'w') as f:
                    f.write("# Tarkov coordinates file - Format: X, Y, Z, Timestamp\n")
                logger.info(f"Created coordinates file: {self.coord_file_path}")
            except Exception as e:
                logger.error(f"Failed to create coordinates file: {e}")
    
    def extract_coordinates(self, filename: str) -> Coordinates:
        """
        Extract coordinates from a screenshot filename.
        
        Args:
            filename: Screenshot filename with embedded coordinates
            
        Returns:
            Coordinates object with extracted values
            
        Raises:
            ValueError: If coordinates cannot be extracted from the filename
        """
        # Regular expression to match coordinates pattern in filenames
        pattern = r"_(-?\d+\.\d+), (-?\d+\.\d+), (-?\d+\.\d+)_"
        match = re.search(pattern, filename)
        
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            z = float(match.group(3))
            return Coordinates(x, y, z)
        else:
            raise ValueError(f"Could not extract coordinates from filename: {filename}")
    
    def save_coordinates(self, coords: Coordinates) -> None:
        """
        Save coordinates to the coordinates file.
        
        Args:
            coords: Coordinates object to save
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.coord_file_path, 'a') as file:
                file.write(f"{coords.x}, {coords.y}, {coords.z}, {timestamp}\n")
            logger.info(f"Saved coordinates: {coords}")
        except Exception as e:
            logger.error(f"Failed to save coordinates: {e}")
    
    def get_latest_coordinates(self) -> Optional[Coordinates]:
        """
        Get the most recently saved coordinates.
        
        Returns:
            The latest coordinates or None if no coordinates are available
        """
        try:
            with open(self.coord_file_path, 'r') as file:
                lines = file.readlines()
                
                # Filter out comment lines and empty lines
                data_lines = [line for line in lines if line.strip() and not line.startswith('#')]
                
                if not data_lines:
                    logger.warning("No coordinates found in file")
                    return None
                
                # Get the last line with coordinates
                last_line = data_lines[-1]
                parts = last_line.strip().split(', ')
                
                # Handle different formats
                if len(parts) >= 3:
                    # Full x, y, z format
                    return Coordinates(
                        x=float(parts[0]),
                        y=float(parts[1]),
                        z=float(parts[2])
                    )
                elif len(parts) == 2:
                    # Old x, z format (where y is missing)
                    return Coordinates(
                        x=float(parts[0]),
                        y=0.0,  # Default Y value (height)
                        z=float(parts[1])
                    )
                else:
                    logger.error(f"Invalid format in coordinates file: {last_line}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading coordinates: {e}")
            return None
    
    def get_all_coordinates(self) -> List[Tuple[Coordinates, str]]:
        """
        Get all saved coordinates with timestamps.
        
        Returns:
            List of tuples containing coordinates and timestamps
        """
        result = []
        try:
            with open(self.coord_file_path, 'r') as file:
                for line in file:
                    if line.strip() and not line.startswith('#'):
                        parts = line.strip().split(', ')
                        
                        # Handle different formats
                        if len(parts) >= 4:
                            # Full x, y, z, timestamp format
                            coords = Coordinates(
                                x=float(parts[0]),
                                y=float(parts[1]),
                                z=float(parts[2])
                            )
                            timestamp = parts[3]
                            result.append((coords, timestamp))
                        elif len(parts) == 2:
                            # Old x, z format with generated timestamp
                            coords = Coordinates(
                                x=float(parts[0]),
                                y=0.0,  # Default Y value
                                z=float(parts[1])
                            )
                            # Use current date as timestamp since original doesn't have one
                            timestamp = "Imported data"
                            result.append((coords, timestamp))
                        elif len(parts) == 3:
                            # x, y, z format without timestamp
                            coords = Coordinates(
                                x=float(parts[0]),
                                y=float(parts[1]),
                                z=float(parts[2])
                            )
                            timestamp = "Imported data"
                            result.append((coords, timestamp))
        except Exception as e:
            logger.error(f"Error reading all coordinates: {e}")
        
        return result