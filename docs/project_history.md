# Project History

This document captures the history and evolution of the Tarkov Map Assistant project.

## Origin

The project was originally created as "TarkovProjekt" with the following components:

- **Dokumentacja** - Original project documentation in Polish
- **Mapy** - Map SVG files and screenshots
- **TarkovProjekcik** - Initial Python implementation with tkinter

## Initial Structure

The original implementation had a simple structure:

```
TarkovProjekcik/
├── gui.py           # Basic GUI implementation with Tkinter and CustomTkinter
├── icons/           # Map icon files
├── main.py          # Simple entry point 
├── map_config.json  # Map coordinate configurations
├── mapa/            # SVG map files
├── maps.py          # Map display logic
├── nazwaZrzutu.txt  # Screenshot filename storage
├── ss.py            # Screenshot handling
└── wspolrzedne.txt  # Coordinates storage
```

## Refactoring

The project was refactored into a proper Python package with:

1. Modular code organization with separation of concerns
2. Proper error handling and logging
3. Integration with the tarkovdata repository
4. Enhanced UI with additional features
5. Standard Python project structure

## Features Added During Refactoring

- Comprehensive integration with tarkovdata repository
- Enhanced map viewing experience
- Coordinate history tracking and visualization
- Multiple map viewing options
- Improved UI with modern customtkinter widgets
- Full documentation of code and functionality
- Proper package setup for distribution

## Data Migration

All resources from the original project structure have been preserved:

- Documentation files moved to `/docs/documentation/`
- Map SVGs moved to `/src/tarkov_app/maps/`
- Screenshots moved to `/docs/screenshots/`
- Configuration files moved to `/config/`

## Original Contributors

The original project was created for educational purposes.