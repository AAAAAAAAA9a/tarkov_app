"""
General Tarkov data manager.

This module provides access to various Tarkov game data from the tarkovdata project.
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class TarkovDataManager:
    """
    Manager for accessing Tarkov game data.
    
    This class provides methods to access various game data such as items,
    ammunition, quests, traders, etc.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the Tarkov data manager.
        
        Args:
            data_dir: Directory containing Tarkov data files (optional)
        """
        self.data_dir = data_dir
        self.cache = {}
        self.available = data_dir is not None and os.path.exists(data_dir)
        
        if not self.available:
            logger.warning("Tarkov data directory not found. Extended game data will not be available.")
    
    def get_data(self, data_type: str) -> Dict[str, Any]:
        """
        Get data of a specific type.
        
        Args:
            data_type: Type of data to get (e.g., 'items', 'ammunition', 'maps')
            
        Returns:
            Dictionary containing the requested data
            
        Raises:
            FileNotFoundError: If the data file doesn't exist
        """
        # Check if tarkovdata is available
        if not self.available:
            return {}
            
        # Check cache first
        if data_type in self.cache:
            return self.cache[data_type]
        
        # Determine file path
        file_name = f"{data_type}.json"
        if data_type == "items":
            file_name = "items.en.json"  # Special case for items
            
        file_path = os.path.join(self.data_dir, file_name)
        
        # Try to load from data directory
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.cache[data_type] = data
                logger.info(f"Loaded {data_type} data from {file_path}")
                return data
        except FileNotFoundError:
            # Try alternate location
            alternate_path = os.path.join(self.data_dir, "Data", file_name)
            try:
                with open(alternate_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    self.cache[data_type] = data
                    logger.info(f"Loaded {data_type} data from {alternate_path}")
                    return data
            except FileNotFoundError:
                logger.warning(f"Data file not found: {file_name}")
                self.cache[data_type] = {}  # Cache empty result to avoid repeated attempts
                return {}
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Get an item by its ID.
        
        Args:
            item_id: The ID of the item to get
            
        Returns:
            Dictionary containing item data, or None if not found
        """
        if not self.available:
            return None
            
        try:
            items = self.get_data("items")
            return items.get(item_id)
        except Exception:
            logger.warning(f"Could not find item with ID {item_id}")
            return None
    
    def get_ammo_types(self) -> List[Dict[str, Any]]:
        """
        Get all ammunition types.
        
        Returns:
            List of ammunition type data
        """
        if not self.available:
            return []
            
        try:
            ammo_data = self.get_data("ammunition")
            return list(ammo_data.values())
        except Exception:
            logger.warning("Could not load ammunition data")
            return []
    
    def get_maps_list(self) -> List[str]:
        """
        Get a list of all available maps.
        
        Returns:
            List of map names
        """
        if not self.available:
            return []
            
        try:
            maps_data = self.get_data("maps")
            return list(maps_data.keys())
        except Exception:
            logger.warning("Could not load maps data")
            return []
    
    def get_map_info(self, map_name: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a specific map.
        
        Args:
            map_name: Name of the map (e.g., 'factory', 'customs')
            
        Returns:
            Dictionary containing map information, or None if not found
        """
        if not self.available:
            return None
            
        try:
            maps_data = self.get_data("maps")
            return maps_data.get(map_name.lower())
        except Exception:
            logger.warning(f"Could not find map info for {map_name}")
            return None
            
    def is_available(self) -> bool:
        """
        Check if tarkovdata is available.
        
        Returns:
            True if tarkovdata is available, False otherwise
        """
        return self.available