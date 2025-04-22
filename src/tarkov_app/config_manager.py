"""
Configuration management module for the Tarkov Map Assistant.

This module handles loading and accessing configuration data for map coordinates
and other application settings.
"""
import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages application configuration and map coordinate settings."""
    
    def __init__(self, config_path: str):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the configuration JSON file
        """
        self.config_path = config_path
        self.config_data = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file."""
        try:
            with open(self.config_path, 'r') as file:
                self.config_data = json.load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            # Use default configuration
            self.config_data = {"Default": self._get_default_map_config()}
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in configuration file: {self.config_path}")
            self.config_data = {"Default": self._get_default_map_config()}
    
    def get_map_config(self, map_name: str) -> Dict[str, float]:
        """
        Get configuration for a specific map.
        
        Args:
            map_name: Name of the map to get configuration for
            
        Returns:
            Dictionary containing map configuration values
        """
        if map_name in self.config_data:
            return self.config_data[map_name]
        else:
            logger.warning(f"No configuration found for map: {map_name}, using default")
            return self.config_data.get("Default", self._get_default_map_config())
    
    def get_available_maps(self) -> list:
        """
        Get list of available maps from configuration.
        
        Returns:
            List of map names
        """
        # Filter out the Default config
        return [name for name in self.config_data.keys() if name != "Default"]
    
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