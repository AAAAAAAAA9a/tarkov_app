"""
Maps data manager module.

This module provides specialized access to Tarkov maps data and integrates
with both the custom map configuration and the official tarkovdata maps.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional, Tuple

from .tarkov_data import TarkovDataManager

logger = logging.getLogger(__name__)

class MapDataManager:
    """
    Manager for Tarkov map data.
    
    This class combines official tarkovdata map info with custom map configuration
    used by the application for coordinate mapping.
    """
    
    def __init__(self, tarkov_data: Optional[TarkovDataManager], custom_config_path: str, maps_dir: str, additional_config_path: str = None):
        """
        Initialize the map data manager.
        
        Args:
            tarkov_data: TarkovDataManager instance for accessing official map data (optional)
            custom_config_path: Path to the custom map configuration JSON file
            maps_dir: Directory containing map SVG files
            additional_config_path: Path to additional map configurations (optional)
        """
        self.tarkov_data = tarkov_data
        self.custom_config_path = custom_config_path
        self.additional_config_path = additional_config_path
        self.maps_dir = maps_dir
        self.custom_config = {}
        self.additional_config = {}
        self.load_custom_config()
    
    def load_custom_config(self) -> None:
        """Load custom map configuration from JSON files."""
        # Load primary config
        try:
            with open(self.custom_config_path, 'r') as file:
                self.custom_config = json.load(file)
                logger.info(f"Custom map configuration loaded from {self.custom_config_path}")
        except FileNotFoundError:
            logger.error(f"Custom map configuration file not found: {self.custom_config_path}")
            self.custom_config = {"Default": self._get_default_map_config()}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in custom map configuration file: {self.custom_config_path}")
            self.custom_config = {"Default": self._get_default_map_config()}
            
        # Load additional config if available
        if self.additional_config_path:
            try:
                with open(self.additional_config_path, 'r') as file:
                    self.additional_config = json.load(file)
                    logger.info(f"Additional map configuration loaded from {self.additional_config_path}")
                    # Merge additional config with primary config
                    self.custom_config.update(self.additional_config)
            except FileNotFoundError:
                logger.warning(f"Additional map configuration file not found: {self.additional_config_path}")
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON in additional map configuration file: {self.additional_config_path}")
    
    def get_available_maps(self) -> List[str]:
        """
        Get list of available maps from both sources.
        
        Returns:
            List of map names
        """
        available_maps = set()
        
        # Add maps from custom config
        available_maps.update([name for name in self.custom_config.keys() if name != "Default"])
        
        # Add maps from tarkovdata if available
        if self.tarkov_data and self.tarkov_data.is_available():
            try:
                maps_data = self.tarkov_data.get_data("maps")
                for map_key, map_info in maps_data.items():
                    if "locale" in map_info and "en" in map_info["locale"]:
                        available_maps.add(map_info["locale"]["en"])
            except Exception as e:
                logger.warning(f"Could not retrieve maps from tarkovdata: {e}")
            
        # Check which maps have SVG files (this is the most important source)
        if os.path.exists(self.maps_dir):
            for file in os.listdir(self.maps_dir):
                if file.endswith(".svg"):
                    map_name = os.path.splitext(file)[0]
                    available_maps.add(map_name)
        
        return sorted(list(available_maps))
    
    def get_map_config(self, map_name: str) -> Dict[str, float]:
        """
        Get configuration for a specific map.
        
        Args:
            map_name: Name of the map to get configuration for
            
        Returns:
            Dictionary containing map configuration values
        """
        # First check custom config (highest priority)
        if map_name in self.custom_config:
            return self.custom_config[map_name]
        
        # Try to get info from tarkovdata if available
        if self.tarkov_data and self.tarkov_data.is_available():
            official_map_info = self._get_official_map_info(map_name)
            if official_map_info:
                # Convert official bounds to our format
                try:
                    bounds = official_map_info["svg"]["bounds"]
                    rotation = official_map_info["svg"]["coordinateRotation"]
                    
                    # Adjust for rotation
                    if rotation == 180:
                        return {
                            "centerMinX": bounds[1][0],
                            "centerMaxX": bounds[0][0],
                            "centerMinY": bounds[0][1],
                            "centerMaxY": bounds[1][1],
                            "pointMinX": bounds[1][0],
                            "pointMaxX": bounds[0][0],
                            "pointMinY": bounds[0][1],
                            "pointMaxY": bounds[1][1]
                        }
                    else:
                        logger.warning(f"Unsupported coordinate rotation for {map_name}: {rotation}")
                except (KeyError, IndexError):
                    logger.warning(f"Could not extract bounds from official map info for {map_name}")
        
        logger.warning(f"No configuration found for map: {map_name}, using default")
        return self.custom_config.get("Default", self._get_default_map_config())
    
    def get_map_file_path(self, map_name: str) -> str:
        """
        Get the path to the SVG file for a map.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Path to the SVG file
            
        Raises:
            FileNotFoundError: If the map file doesn't exist
        """
        # Handle special cases first
        map_name_mapping = {
            "The Lab": "Labs",
            "Lab": "Labs",
            "Streets of Tarkov": "StreetsOfTarkov"
        }
        
        # Apply mapping if available
        search_name = map_name_mapping.get(map_name, map_name)
        
        # Try direct match (most common case)
        map_file = f"{search_name}.svg"
        map_path = os.path.join(self.maps_dir, map_file)
        
        if os.path.exists(map_path):
            return map_path
        
        # Try alternative case variations
        for file in os.listdir(self.maps_dir):
            file_base = os.path.splitext(file)[0]
            if file_base.lower() == search_name.lower() or file_base.lower() == map_name.lower():
                return os.path.join(self.maps_dir, file)
        
        # Try removing spaces
        no_space_name = search_name.replace(" ", "")
        map_file = f"{no_space_name}.svg"
        map_path = os.path.join(self.maps_dir, map_file)
        if os.path.exists(map_path):
            return map_path
        
        # Try to find official name if tarkovdata is available
        if self.tarkov_data and self.tarkov_data.is_available():
            official_map_info = self._get_official_map_info(map_name)
            if official_map_info and "svg" in official_map_info and "file" in official_map_info["svg"]:
                official_file = official_map_info["svg"]["file"]
                official_path = os.path.join(self.maps_dir, official_file)
                if os.path.exists(official_path):
                    return official_path
        
        # If we still can't find the map, try searching for similar filenames
        for file in os.listdir(self.maps_dir):
            if file.endswith(".svg"):
                file_base = os.path.splitext(file)[0]
                # Check for substring matches or similar names
                if (search_name.lower() in file_base.lower() or 
                    file_base.lower() in search_name.lower() or
                    map_name.lower() in file_base.lower() or
                    file_base.lower() in map_name.lower()):
                    logger.info(f"Found similar map file for '{map_name}': {file}")
                    return os.path.join(self.maps_dir, file)
                
        raise FileNotFoundError(f"Map file not found for {map_name}")
    
    def get_map_enemies(self, map_name: str) -> List[str]:
        """
        Get list of enemies that can be found on a map.
        
        Args:
            map_name: Name of the map
            
        Returns:
            List of enemy types
        """
        if not self.tarkov_data or not self.tarkov_data.is_available():
            return []
            
        official_map_info = self._get_official_map_info(map_name)
        if official_map_info and "enemies" in official_map_info:
            return official_map_info["enemies"]
        return []
    
    def get_map_raid_duration(self, map_name: str) -> Dict[str, int]:
        """
        Get raid duration for a map.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Dictionary with day and night raid durations in minutes
        """
        if not self.tarkov_data or not self.tarkov_data.is_available():
            return {"day": 0, "night": 0}
            
        official_map_info = self._get_official_map_info(map_name)
        if official_map_info and "raidDuration" in official_map_info:
            return official_map_info["raidDuration"]
        return {"day": 0, "night": 0}
    
    def get_map_description(self, map_name: str) -> str:
        """
        Get description for a map.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Map description or empty string if not available
        """
        if not self.tarkov_data or not self.tarkov_data.is_available():
            return ""
            
        official_map_info = self._get_official_map_info(map_name)
        if official_map_info and "description" in official_map_info:
            return official_map_info["description"]
        return ""
    
    def get_map_wiki_url(self, map_name: str) -> Optional[str]:
        """
        Get wiki URL for a map.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Map wiki URL or None if not available
        """
        if not self.tarkov_data or not self.tarkov_data.is_available():
            return None
            
        official_map_info = self._get_official_map_info(map_name)
        if official_map_info and "wiki" in official_map_info:
            return official_map_info["wiki"]
        return None
    
    def _get_official_map_info(self, map_name: str) -> Optional[Dict[str, Any]]:
        """
        Get official map information from tarkovdata.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Dictionary with map information or None if not found
        """
        if not self.tarkov_data or not self.tarkov_data.is_available():
            return None
            
        try:
            maps_data = self.tarkov_data.get_data("maps")
            
            # First try direct key match
            if map_name.lower() in maps_data:
                return maps_data[map_name.lower()]
            
            # Try to match by locale name
            for key, map_info in maps_data.items():
                if "locale" in map_info and "en" in map_info["locale"]:
                    if map_info["locale"]["en"].lower() == map_name.lower():
                        return map_info
            
            return None
        except Exception:
            return None
    
    @staticmethod
    def _get_default_map_config() -> Dict[str, float]:
        """
        Get default map configuration.
        
        Returns:
            Dictionary with default map configuration values
        """
        return {
            "centerMinX": -300,
            "centerMaxX": 300,
            "centerMinY": -300,
            "centerMaxY": 300,
            "pointMinX": -300,
            "pointMaxX": 300,
            "pointMinY": -300,
            "pointMaxY": 300
        }