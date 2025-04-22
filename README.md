# Tarkov Map Assistant

A tool for translating Escape from Tarkov game coordinates to positions on map images.

## Features

- Load screenshots with embedded coordinates from Escape from Tarkov
- Display player positions on interactive SVG maps with animated indicators
- Support for all official Tarkov maps (Customs, Factory, Woods, Shoreline, Interchange, Reserve, Labs, Lighthouse, Streets of Tarkov)
- Pan and zoom functionality with smooth animations and reset view option
- Coordinate history tracking with timestamp logging
- Dark and light theme support
- Modern UI with customtkinter

## Installation

### Prerequisites

- Python 3.8 or higher
- Required packages:
  - tkinter (usually comes with Python)
  - customtkinter
  - Pillow (PIL)
  - tkSvg

### Setup

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/tarkov-app.git
   cd tarkov-app
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Install the package in development mode:
   ```
   pip install -e .
   ```

## Usage

### Running the application

```
# Using the quick run script
./run.py

# As a Python module
python -m tarkov_app

# Using the entry point after installation
tarkov-assistant
```

### How to use

1. **Load a Screenshot**:
   - Click "Load Screenshot" or use File → Load Screenshot
   - Select a screenshot from Escape from Tarkov with embedded coordinates
   - The application extracts coordinates from the filename

2. **View Your Position**:
   - Select a map from the available maps in the main window or Maps menu
   - Your position is displayed on the map with a red pulsing indicator
   - Map information (raid duration, enemies) is shown when available

3. **Navigate Maps**:
   - **Zoom**: Use mouse wheel to zoom in/out
   - **Pan**: Click and drag to move around the map
   - **Reset View**: Press 'R' key to reset to the original view

4. **View Coordinate History**:
   - Go to View → Coordinate History
   - See all previously loaded coordinates with timestamps
   - Click "View on Map" to see any historical position on any map

5. **Settings**:
   - Access Options → Settings to change theme (Light/Dark/System)
   - Manage available maps and view options

### Supported Maps

The application supports all Escape from Tarkov maps:
- Customs
- Factory
- Woods
- Shoreline
- Interchange
- Reserve
- Labs
- Lighthouse
- Streets of Tarkov
- Ground Zero

### Screenshot Format

The application extracts coordinates from screenshot filenames in the format:

```
YYYY-MM-DD[HH-MM]_X.X, Y.Y, Z.Z_...
```

For example: `2024-03-16[02-20]_-9.1, 33.6, 166.4_0.0, -1.0, 0.2, 0.1_12.33 (0).png`

The application uses the X and Z coordinates to position the player marker on the 2D map.

## Project Structure

```
tarkov_app/
├── config/                    # Configuration files
│   ├── map_config.json        # Primary map configurations
│   └── additional_maps.json   # Additional map configurations
├── data/                      # Game data files
│   ├── maps.json              # Map information data
│   └── coordinates/           # Coordinate storage
├── src/                       # Source code
│   └── tarkov_app/            # Main package
│       ├── __init__.py        # Package initialization
│       ├── __main__.py        # Entry point
│       ├── main.py            # Application initialization
│       ├── gui.py             # GUI components
│       ├── screenshot_handler.py  # Screenshot handling
│       ├── data_manager/      # Data management modules
│       │   ├── __init__.py    # Package initialization
│       │   ├── maps_data.py   # Maps data handler
│       │   └── tarkov_data.py # Tarkov game data handler
│       ├── icons/             # Map icons
│       └── maps/              # SVG maps
├── tests/                     # Test files
├── docs/                      # Documentation
├── run.py                     # Quick launch script
├── README.md                  # This file
├── requirements.txt           # Dependencies
├── setup.py                   # Package setup script
└── MANIFEST.in                # Packaging manifest
```

## Key Features

### Enhanced Map Viewing

- **Interactive Maps**: Smooth pan and zoom controls
- **Animated Player Marker**: Visual pulsing effect to easily spot your position
- **Map Information**: Details about raid duration and enemies when available
- **Multiple Map Formats**: Support for all official Tarkov map formats

### Coordinate Management

- **Screenshot Parsing**: Automatically extracts coordinates from screenshot filenames
- **Coordinate History**: Maintains a log of all loaded coordinates with timestamps
- **Historical Viewing**: View any past position on any map
- **Position Tracking**: Keep track of player movements across game sessions

### User Interface

- **Modern Design**: Clean, modern interface with customtkinter
- **Theme Support**: Light and dark mode options
- **Responsive Layout**: Adapts to different window sizes
- **Menu System**: Easy access to all features through a traditional menu system

## Troubleshooting

- **Missing Dependencies**: Make sure all required packages are installed
- **Screenshot Format**: Ensure screenshots follow the expected naming format
- **Map Files**: Verify that SVG map files are present in the maps directory
- **Coordinate Extraction**: Check the coordinate extraction from screenshot filenames

## License

MIT License

## Credits

Map SVGs based on files from the Escape from Tarkov community and tarkovdata project.