"""
Main entry point for the Tarkov Map Assistant application.

This module initializes the application and starts the GUI.
"""
import os
import sys
import logging
import logging.handlers
from pathlib import Path

from .gui import TarkovMapApp
from .screenshot_handler import ScreenshotHandler
from .data_manager import TarkovDataManager, MapDataManager

def setup_logging():
    """Configure application logging."""
    # Create logs directory if it doesn't exist
    logs_dir = Path.home() / ".tarkov_assistant" / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up logging
    log_file = logs_dir / "tarkov_assistant.log"
    
    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # File handler with rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=1048576, backupCount=5
    )
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_format)
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_format = logging.Formatter("%(levelname)s: %(message)s")
    console_handler.setFormatter(console_format)
    console_handler.setLevel(logging.WARNING)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_application_paths():
    """
    Get paths for application resources.
    
    Returns:
        Dictionary containing paths for various application resources
    """
    # Determine the base path for the application
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    app_dir = os.path.join(base_dir, "tarkov_app")
    
    # Check if we're running from a bundled application
    if getattr(sys, 'frozen', False):
        # Running in a bundle
        base_dir = os.path.dirname(sys.executable)
        app_dir = base_dir
    
    # Set up paths
    config_path = os.path.join(os.path.dirname(base_dir), "config", "map_config.json")
    maps_dir = os.path.join(app_dir, "maps")
    icons_dir = os.path.join(app_dir, "icons")
    
    # Create user data directory
    user_data_dir = os.path.join(Path.home(), ".tarkov_assistant", "data")
    os.makedirs(user_data_dir, exist_ok=True)
    
    # Path for coordinates file
    coords_file = os.path.join(user_data_dir, "coordinates.txt")
    
    # Create result paths
    paths = {
        "config_path": config_path,
        "maps_dir": maps_dir,
        "icons_dir": icons_dir,
        "coords_file": coords_file,
    }
    
    # Check for tarkovdata (optional)
    # Try multiple potential locations
    tarkov_data_locations = [
        os.path.join(os.path.dirname(base_dir), "data", "tarkovdata"),  # Standard location
        os.path.join(os.path.dirname(base_dir), "tarkovdata-master"),   # Direct repo location
        os.path.join(base_dir, "data", "tarkovdata"),                  # Alternate location
    ]
    
    for location in tarkov_data_locations:
        if os.path.exists(location):
            paths["tarkov_data_dir"] = location
            break
    
    return paths

def main():
    """Main entry point for the application."""
    # Set up logging
    logger = setup_logging()
    logger.info("Application starting")
    
    try:
        # Get application paths
        paths = get_application_paths()
        logger.info(f"Using config path: {paths['config_path']}")
        logger.info(f"Using maps directory: {paths['maps_dir']}")
        
        # Set up tarkov data manager if available
        tarkov_data = None
        if 'tarkov_data_dir' in paths and os.path.exists(paths['tarkov_data_dir']):
            logger.info(f"Using tarkov data directory: {paths['tarkov_data_dir']}")
            tarkov_data = TarkovDataManager(paths["tarkov_data_dir"])
        else:
            logger.warning("Tarkov data directory not found. Extended game information will not be available.")
        
        # Set up map data manager
        additional_config_path = os.path.join(os.path.dirname(paths["config_path"]), "additional_maps.json")
        map_data = MapDataManager(
            tarkov_data=tarkov_data,
            custom_config_path=paths["config_path"],
            maps_dir=paths["maps_dir"],
            additional_config_path=additional_config_path if os.path.exists(additional_config_path) else None
        )
        
        # Set up screenshot handler
        screenshot_handler = ScreenshotHandler(paths["coords_file"])
        
        # Create and run the application
        app = TarkovMapApp(
            screenshot_handler=screenshot_handler,
            map_data=map_data,
            icons_dir=paths["icons_dir"]
        )
        
        logger.info("Starting GUI")
        app.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return 1
    
    logger.info("Application exiting normally")
    return 0

if __name__ == "__main__":
    sys.exit(main())