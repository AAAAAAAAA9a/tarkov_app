"""
Map management module for the Tarkov Map Assistant.

This module handles loading, displaying and interaction with game maps.
"""
import os
import logging
from typing import Dict, Tuple, Optional
from dataclasses import dataclass

from .config_manager import ConfigManager
from .screenshot_handler import Coordinates

# Configure logger
logger = logging.getLogger(__name__)

@dataclass
class MapPoint:
    """Data class for a point on a map."""
    x: int
    y: int
    color: str = "red"
    radius: int = 5
    
    def get_oval_coords(self) -> Tuple[int, int, int, int]:
        """
        Get coordinates for drawing an oval.
        
        Returns:
            Tuple of (x1, y1, x2, y2) coordinates for oval drawing
        """
        return (
            self.x - self.radius,
            self.y - self.radius,
            self.x + self.radius,
            self.y + self.radius
        )

class MapManager:
    """Manages game maps and coordinate mapping."""
    
    def __init__(self, config_manager: ConfigManager, maps_dir: str):
        """
        Initialize the map manager.
        
        Args:
            config_manager: ConfigManager instance for map configurations
            maps_dir: Directory containing map SVG files
        """
        self.config_manager = config_manager
        self.maps_dir = maps_dir
        self.available_maps = self._find_available_maps()
    
    def _find_available_maps(self) -> list:
        """
        Find available maps from SVG files in the maps directory.
        
        Returns:
            List of available map names
        """
        try:
            maps = []
            for file in os.listdir(self.maps_dir):
                if file.endswith(".svg"):
                    map_name = os.path.splitext(file)[0]
                    maps.append(map_name)
            
            if not maps:
                logger.warning(f"No SVG maps found in {self.maps_dir}")
            
            return maps
        except Exception as e:
            logger.error(f"Error finding available maps: {e}")
            return []
    
    def get_map_path(self, map_name: str) -> str:
        """
        Get the file path for a map SVG.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Absolute path to the map SVG file
            
        Raises:
            ValueError: If the map does not exist
        """
        map_file = f"{map_name}.svg"
        map_path = os.path.join(self.maps_dir, map_file)
        
        if not os.path.exists(map_path):
            raise ValueError(f"Map not found: {map_name}")
        
        return map_path
    
    def game_to_map_coordinates(self, map_name: str, game_coords: Coordinates, canvas_width: int, canvas_height: int) -> MapPoint:
        """
        Convert game coordinates to map coordinates.
        
        Args:
            map_name: Name of the map
            game_coords: Game coordinates to convert
            canvas_width: Width of the canvas
            canvas_height: Height of the canvas
            
        Returns:
            MapPoint with converted coordinates
        """
        map_config = self.config_manager.get_map_config(map_name)
        
        # Calculate map center point
        center_x = (map_config["centerMaxX"] + map_config["centerMinX"]) / 2
        center_y = (map_config["centerMaxY"] + map_config["centerMinY"]) / 2
        
        # Calculate scale factors
        scale_x = canvas_width / (map_config["pointMaxX"] - map_config["pointMinX"])
        scale_y = canvas_height / (map_config["pointMaxY"] - map_config["pointMinY"])
        
        # Convert coordinates
        real_x = canvas_width / 2 - ((game_coords.x - center_x) * scale_x)
        real_y = canvas_height / 2 + ((game_coords.z - center_y) * scale_y)
        
        logger.debug(f"Converted game coords {game_coords} to map point ({int(real_x)}, {int(real_y)})")
        
        return MapPoint(x=int(real_x), y=int(real_y))