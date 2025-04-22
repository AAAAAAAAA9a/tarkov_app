"""
GUI module for the Tarkov Map Assistant.

This module provides the graphical user interface for the application.
"""
import os
import logging
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image
from tksvg import SvgImage  # Changed from tkSvg to tksvg (lowercase 's')

from .screenshot_handler import ScreenshotHandler, Coordinates
from .data_manager import MapDataManager

# Configure logger
logger = logging.getLogger(__name__)

class TarkovMapApp:
    """Main application class for the Tarkov Map Assistant GUI."""
    
    def __init__(self, screenshot_handler, map_data, icons_dir):
        """
        Initialize the application.
        
        Args:
            screenshot_handler: ScreenshotHandler instance
            map_data: MapDataManager instance
            icons_dir: Directory containing map icons
        """
        self.screenshot_handler = screenshot_handler
        self.map_data = map_data
        self.icons_dir = icons_dir
        
        self.root = None
        self.icons = {}
        self.status_bar = None
        self.position_label = None
        
        # Set customtkinter appearance mode
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
    
    def run(self):
        """Start the application."""
        self.root = ctk.CTk()
        self.root.title("Tarkov Map Assistant")
        self.root.geometry("500x700")
        self.root.resizable(True, True)
        
        self._setup_menu()
        self._create_main_interface()
        
        self.root.mainloop()
    
    def _setup_menu(self):
        """Set up the application menu."""
        menu_bar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Load Screenshot", command=self._load_screenshot)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menu_bar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menu_bar, tearoff=0)
        view_menu.add_command(label="Coordinate History", command=self._show_coord_history)
        menu_bar.add_cascade(label="View", menu=view_menu)
        
        # Maps menu
        maps_menu = tk.Menu(menu_bar, tearoff=0)
        
        # Add maps from our data manager with special handling for variants
        available_maps = sorted(self.map_data.get_available_maps())
        
        # Filter out duplicate maps with different naming variations
        filtered_maps = []
        skip_maps = ["Lab", "The Lab"]  # Prefer "Labs" over these variations
        
        for map_name in available_maps:
            # Skip certain variations if we have the preferred name
            if "Labs" in available_maps and map_name in skip_maps:
                continue
            if "StreetsOfTarkov" in available_maps and map_name == "Streets of Tarkov":
                continue
            filtered_maps.append(map_name)
        
        # Add maps to menu
        for map_name in filtered_maps:
            maps_menu.add_command(
                label=map_name,
                command=lambda m=map_name: self._show_map(m)
            )
        
        menu_bar.add_cascade(label="Maps", menu=maps_menu)
        
        # Settings menu
        settings_menu = tk.Menu(menu_bar, tearoff=0)
        settings_menu.add_command(label="Settings", command=self._open_settings)
        menu_bar.add_cascade(label="Options", menu=settings_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="Wiki", command=self._open_wiki)
        help_menu.add_separator()
        help_menu.add_command(label="About", command=self._show_about)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menu_bar)
    
    def _create_main_interface(self):
        """Create the main application interface."""
        # Main frame
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Screenshot button
        upload_button = ctk.CTkButton(
            main_frame, 
            text="Load Screenshot", 
            command=self._load_screenshot
        )
        upload_button.pack(pady=10)
        
        # Coordinates display
        coords_frame = ctk.CTkFrame(main_frame)
        coords_frame.pack(fill="x", padx=5, pady=5)
        
        coords_label = ctk.CTkLabel(
            coords_frame, 
            text="Current Position:", 
            font=ctk.CTkFont(size=14, weight="bold")
        )
        coords_label.pack(pady=5)
        
        self.position_label = ctk.CTkLabel(
            coords_frame, 
            text="No coordinates loaded",
            font=ctk.CTkFont(size=12)
        )
        self.position_label.pack(pady=5)
        
        # Maps section
        maps_label = ctk.CTkLabel(
            main_frame, 
            text="Select Map:", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        maps_label.pack(pady=(20, 10))
        
        # Create scrollable frame for maps
        maps_scroll_frame = ctk.CTkScrollableFrame(main_frame)
        maps_scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Load map icons
        self._load_map_icons()
        
        # Create map buttons
        available_maps = self.map_data.get_available_maps()
        
        # Create map category frames
        official_maps_frame = ctk.CTkFrame(maps_scroll_frame)
        official_maps_frame.pack(fill="x", padx=5, pady=5)
        
        ctk.CTkLabel(
            official_maps_frame, 
            text="Official Maps", 
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", pady=5)
        
        maps_grid = ctk.CTkFrame(official_maps_frame)
        maps_grid.pack(fill="x", padx=5, pady=5)
        
        # Create buttons for each map
        button_count = 0
        col_count = 2  # Number of columns in the grid
        
        # Filter out duplicate maps to avoid clutter
        filtered_maps = []
        skip_maps = ["Lab", "The Lab"]  # Prefer "Labs" over these variations
        
        for map_name in sorted(available_maps):
            # Skip certain variations if we have the preferred name
            if "Labs" in available_maps and map_name in skip_maps:
                continue
            if "StreetsOfTarkov" in available_maps and map_name == "Streets of Tarkov":
                continue
            filtered_maps.append(map_name)
        
        for index, map_name in enumerate(filtered_maps):
            # Create a button frame for each map button
            button_frame = ctk.CTkFrame(maps_grid)
            button_frame.grid(
                row=button_count // col_count, 
                column=button_count % col_count, 
                padx=5, pady=5, 
                sticky="ew"
            )
            
            # Map button
            button = ctk.CTkButton(
                button_frame,
                text=map_name,
                image=self.icons.get(map_name),
                compound="left",
                command=lambda mn=map_name: self._show_map(mn),
                width=200,
                height=40
            )
            button.pack(fill="x", padx=5, pady=5)
            
            # Get map info for the tooltip
            map_info = self._get_map_tooltip(map_name)
            if map_info:
                # Create tooltip label
                tooltip_label = ctk.CTkLabel(
                    button_frame,
                    text=map_info,
                    font=ctk.CTkFont(size=10),
                    justify="left",
                    wraplength=190
                )
                tooltip_label.pack(padx=5, pady=(0, 5), anchor="w")
            
            # Increment count
            button_count += 1
        
        # Make columns responsive
        for i in range(col_count):
            maps_grid.columnconfigure(i, weight=1)
        
        # Status bar
        status_bar = ctk.CTkLabel(self.root, text="Ready", anchor="w")
        status_bar.pack(side="bottom", fill="x", padx=5, pady=2)
        self.status_bar = status_bar
        
        # Update coordinates display if available
        self._update_coordinates_display()
    
    def _get_map_tooltip(self, map_name):
        """
        Create a tooltip text for a map button.
        
        Args:
            map_name: Name of the map
            
        Returns:
            Tooltip text with map info
        """
        tooltip_parts = []
        
        # Get raid duration if available
        raid_duration = self.map_data.get_map_raid_duration(map_name)
        if raid_duration and (raid_duration["day"] > 0 or raid_duration["night"] > 0):
            tooltip_parts.append(f"Duration: {raid_duration['day']}min (day) / {raid_duration['night']}min (night)")
        
        # Get enemies if available
        enemies = self.map_data.get_map_enemies(map_name)
        if enemies:
            enemies_text = ", ".join(enemies)
            tooltip_parts.append(f"Enemies: {enemies_text}")
        
        # Return tooltip if we have any info, otherwise None
        if tooltip_parts:
            return "\n".join(tooltip_parts)
        return None
    
    def _load_map_icons(self):
        """Load map icons from the icons directory."""
        self.icons = {}
        for map_name in self.map_data.get_available_maps():
            # Try a few potential file names
            icon_paths = [
                os.path.join(self.icons_dir, f"{map_name}.png"),
                os.path.join(self.icons_dir, f"{map_name.lower()}.png"),
                os.path.join(self.icons_dir, f"{map_name.replace(' ', '')}.png")
            ]
            
            for icon_path in icon_paths:
                if os.path.exists(icon_path):
                    try:
                        icon_image = ctk.CTkImage(Image.open(icon_path), size=(24, 24))
                        self.icons[map_name] = icon_image
                        break
                    except Exception as e:
                        logger.error(f"Error loading icon for {map_name}: {e}")
    
    def _update_coordinates_display(self):
        """Update the coordinates display with the latest coordinates."""
        coords = self.screenshot_handler.get_latest_coordinates()
        if coords:
            self.position_label.configure(text=f"X: {coords.x:.1f}, Y: {coords.y:.1f}, Z: {coords.z:.1f}")
        else:
            self.position_label.configure(text="No coordinates loaded")
    
    def _load_screenshot(self):
        """Load a screenshot file and extract coordinates."""
        file_path = filedialog.askopenfilename(
            filetypes=[("PNG Files", "*.png"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            file_name = os.path.basename(file_path)
            coords = self.screenshot_handler.extract_coordinates(file_name)
            self.screenshot_handler.save_coordinates(coords)
            
            self._update_coordinates_display()
            self._set_status(f"Loaded screenshot: {file_name}")
            
            messagebox.showinfo(
                "Success", 
                f"Screenshot loaded successfully.\nExtracted coordinates: {coords}"
            )
        except ValueError as e:
            logger.error(f"Error processing screenshot: {e}")
            messagebox.showerror("Error", str(e))
    
    def _show_map(self, map_name):
        """
        Display a map in a new window.
        
        Args:
            map_name: Name of the map to display
        """
        try:
            # Get latest coordinates
            coords = self.screenshot_handler.get_latest_coordinates()
            if not coords:
                messagebox.showwarning(
                    "No Coordinates", 
                    "No coordinates available. Load a screenshot first."
                )
                return
            
            # Get map file path
            try:
                map_path = self.map_data.get_map_file_path(map_name)
            except FileNotFoundError as e:
                messagebox.showerror("Error", f"Could not find map file: {e}")
                return
            
            # Create map window
            map_window = ctk.CTkToplevel(self.root)
            map_window.title(f"Map: {map_name}")
            map_window.geometry("1000x800")
            map_window.resizable(True, True)
            
            # Create toolbar frame
            toolbar = ctk.CTkFrame(map_window)
            toolbar.pack(side="top", fill="x")
            
            # Map description
            description = self.map_data.get_map_description(map_name)
            if description:
                desc_label = ctk.CTkLabel(
                    toolbar, 
                    text=description,
                    wraplength=800,
                    justify="left"
                )
                desc_label.pack(padx=10, pady=5, anchor="w")
            
            # Wiki button
            wiki_url = self.map_data.get_map_wiki_url(map_name)
            if wiki_url:
                wiki_button = ctk.CTkButton(
                    toolbar,
                    text="Open Wiki",
                    command=lambda: webbrowser.open(wiki_url)
                )
                wiki_button.pack(side="right", padx=10, pady=5)
            
            # Player position label
            position_text = f"Player Position: X: {coords.x:.1f}, Y: {coords.y:.1f}, Z: {coords.z:.1f}"
            position_label = ctk.CTkLabel(
                toolbar,
                text=position_text
            )
            position_label.pack(side="left", padx=10, pady=5)
            
            # Create canvas for the map
            canvas_frame = ctk.CTkFrame(map_window)
            canvas_frame.pack(fill="both", expand=True)
            
            canvas = tk.Canvas(canvas_frame, width=1000, height=700, bg="#333333")
            canvas.pack(fill="both", expand=True)
            
            # Load SVG map
            try:
                svg_image = SvgImage(master=canvas, file=map_path)
                svg_id = canvas.create_image(0, 0, anchor='nw', image=svg_image)
                
                # Get SVG dimensions
                svg_width = svg_image.width()
                svg_height = svg_image.height()
                
                # Get map config and calculate point position
                map_config = self.map_data.get_map_config(map_name)
                
                # Calculate center point
                center_x = (map_config["centerMaxX"] + map_config["centerMinX"]) / 2
                center_y = (map_config["centerMaxY"] + map_config["centerMinY"]) / 2
                
                # Calculate scale factors
                scale_x = svg_width / (map_config["pointMaxX"] - map_config["pointMinX"])
                scale_y = svg_height / (map_config["pointMaxY"] - map_config["pointMinY"])
                
                # Convert game coordinates to map coordinates
                real_x = svg_width / 2 - ((coords.x - center_x) * scale_x)
                real_y = svg_height / 2 + ((coords.z - center_y) * scale_y)
                
                # Draw player position marker
                marker_size = 8
                canvas.create_oval(
                    real_x - marker_size, real_y - marker_size,
                    real_x + marker_size, real_y + marker_size,
                    fill="red", outline="white", width=2, tags=("player_position",)
                )
                
                # Add a pulsing effect circle
                for i in range(3):
                    size = marker_size + (i+1) * 5
                    canvas.create_oval(
                        real_x - size, real_y - size,
                        real_x + size, real_y + size,
                        outline="red", width=2, tags=("player_effect",)
                    )
                
                # Pulse animation
                def pulse_effect():
                    alpha = 0.8
                    fade_step = 0.05
                    
                    def fade_out():
                        nonlocal alpha
                        if alpha > 0:
                            for item in canvas.find_withtag("player_effect"):
                                canvas.itemconfig(item, outline=f"#{int(255*alpha):02x}0000")
                            alpha -= fade_step
                            canvas.after(50, fade_out)
                        else:
                            alpha = 0.8
                            for item in canvas.find_withtag("player_effect"):
                                canvas.itemconfig(item, outline="red")
                            canvas.after(1000, fade_out)
                    
                    fade_out()
                
                pulse_effect()
                
                # Add pan functionality (no zoom)
                self._add_canvas_controls(canvas)
                
                # Store reference to prevent garbage collection
                canvas.svg_image = svg_image
                
            except Exception as e:
                logger.error(f"Error rendering map {map_name}: {e}")
                messagebox.showerror("Error", f"Could not render map: {e}")
                
        except Exception as e:
            logger.error(f"Error showing map {map_name}: {e}")
            messagebox.showerror("Error", f"Could not load map: {e}")
    
    def _add_canvas_controls(self, canvas):
        """
        Add pan controls to a canvas.
        
        Args:
            canvas: The canvas to add controls to
        """
        # Initialize variables for tracking mouse movement
        prev_x = None
        prev_y = None
        
        # Pan start handler
        def move_start(event):
            nonlocal prev_x, prev_y
            prev_x = event.x
            prev_y = event.y
            canvas.config(cursor="fleur")
        
        # Pan movement handler
        def move_move(event):
            nonlocal prev_x, prev_y
            if prev_x is not None and prev_y is not None:
                dx = event.x - prev_x
                dy = event.y - prev_y
                prev_x = event.x
                prev_y = event.y
                canvas.move("all", dx, dy)
        
        # Pan end handler
        def move_end(_event):
            nonlocal prev_x, prev_y
            prev_x = None
            prev_y = None
            canvas.config(cursor="")
        
        # Bind pan controls
        canvas.bind("<ButtonPress-1>", move_start)
        canvas.bind("<B1-Motion>", move_move)
        canvas.bind("<ButtonRelease-1>", move_end)
    
    def _open_settings(self):
        """Open the settings dialog."""
        settings_window = ctk.CTkToplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("400x300")
        settings_window.resizable(False, False)
        
        # Create a notebook/tab control
        tab_view = ctk.CTkTabview(settings_window)
        tab_view.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Appearance tab
        appearance_tab = tab_view.add("Appearance")
        
        # Theme settings
        theme_label = ctk.CTkLabel(
            appearance_tab, 
            text="Theme:", 
            font=ctk.CTkFont(weight="bold")
        )
        theme_label.pack(anchor="w", pady=(10, 5))
        
        # Theme radio buttons
        theme_var = ctk.StringVar(value=ctk.get_appearance_mode())
        
        def change_theme():
            ctk.set_appearance_mode(theme_var.get())
        
        light_theme = ctk.CTkRadioButton(
            appearance_tab, 
            text="Light", 
            variable=theme_var, 
            value="Light", 
            command=change_theme
        )
        light_theme.pack(anchor="w", padx=20, pady=2)
        
        dark_theme = ctk.CTkRadioButton(
            appearance_tab, 
            text="Dark", 
            variable=theme_var, 
            value="Dark", 
            command=change_theme
        )
        dark_theme.pack(anchor="w", padx=20, pady=2)
        
        system_theme = ctk.CTkRadioButton(
            appearance_tab, 
            text="System", 
            variable=theme_var, 
            value="System", 
            command=change_theme
        )
        system_theme.pack(anchor="w", padx=20, pady=2)
        
        # Maps tab
        maps_tab = tab_view.add("Maps")
        
        ctk.CTkLabel(
            maps_tab,
            text="Available Maps:",
            font=ctk.CTkFont(weight="bold")
        ).pack(anchor="w", pady=(10, 5))
        
        # Create a scrollable frame for maps list
        maps_list_frame = ctk.CTkScrollableFrame(maps_tab)
        maps_list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Add available maps with checkboxes
        for map_name in sorted(self.map_data.get_available_maps()):
            map_row = ctk.CTkFrame(maps_list_frame)
            map_row.pack(fill="x", pady=2)
            
            enabled_var = ctk.BooleanVar(value=True)
            ctk.CTkCheckBox(
                map_row,
                text=map_name,
                variable=enabled_var,
                onvalue=True,
                offvalue=False
            ).pack(side="left", padx=5)
            
            # Add view button
            ctk.CTkButton(
                map_row,
                text="View",
                width=60,
                command=lambda m=map_name: self._show_map(m)
            ).pack(side="right", padx=5)
    
    def _show_coord_history(self):
        """Display coordinate history."""
        history = self.screenshot_handler.get_all_coordinates()
        
        if not history:
            messagebox.showinfo("Coordinate History", "No coordinates history available")
            return
        
        history_window = ctk.CTkToplevel(self.root)
        history_window.title("Coordinate History")
        history_window.geometry("500x400")
        history_window.resizable(True, True)
        
        # Create a scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(history_window)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add headers
        header_frame = ctk.CTkFrame(scroll_frame)
        header_frame.pack(fill="x", pady=(0, 5))
        
        ctk.CTkLabel(
            header_frame, 
            text="Coordinates", 
            font=ctk.CTkFont(weight="bold")
        ).pack(side="left", padx=5)
        
        ctk.CTkLabel(
            header_frame, 
            text="Timestamp", 
            font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=5)
        
        # Add button to view coordinates on map
        ctk.CTkLabel(
            header_frame,
            text="Actions",
            font=ctk.CTkFont(weight="bold")
        ).pack(side="right", padx=25)
        
        # Add history items
        for i, (coords, timestamp) in enumerate(history):
            item_frame = ctk.CTkFrame(scroll_frame)
            item_frame.pack(fill="x", pady=2)
            
            coord_text = f"X: {coords.x:.1f}, Y: {coords.y:.1f}, Z: {coords.z:.1f}"
            ctk.CTkLabel(
                item_frame, 
                text=coord_text
            ).pack(side="left", padx=5)
            
            ctk.CTkLabel(
                item_frame, 
                text=timestamp
            ).pack(side="right", padx=5)
            
            # Add button to view on map
            maps_menu_button = ctk.CTkButton(
                item_frame,
                text="View on Map",
                width=100,
                command=lambda c=coords: self._show_coord_on_map(c)
            )
            maps_menu_button.pack(side="right", padx=5)
    
    def _show_coord_on_map(self, coords):
        """
        Show a map selection dialog to view coordinates.
        
        Args:
            coords: Coordinates to show on the map
        """
        map_select = ctk.CTkToplevel(self.root)
        map_select.title("Select Map")
        map_select.geometry("300x400")
        map_select.resizable(False, False)
        
        ctk.CTkLabel(
            map_select,
            text="Select a map to view coordinates:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Create scrollable frame for maps
        maps_frame = ctk.CTkScrollableFrame(map_select)
        maps_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Add buttons for each map
        for map_name in sorted(self.map_data.get_available_maps()):
            map_button = ctk.CTkButton(
                maps_frame,
                text=map_name,
                command=lambda m=map_name: self._show_selected_map_with_coords(m, coords, map_select)
            )
            map_button.pack(fill="x", pady=5)
    
    def _show_selected_map_with_coords(self, map_name, coords, dialog=None):
        """
        Show a map with specific coordinates.
        
        Args:
            map_name: Name of the map to display
            coords: Coordinates to show on the map
            dialog: Optional dialog to close after selection
        """
        # Close the dialog if provided
        if dialog:
            dialog.destroy()
        
        # Temporarily override the latest coordinates
        original_get_latest = self.screenshot_handler.get_latest_coordinates
        self.screenshot_handler.get_latest_coordinates = lambda: coords
        
        # Show the map
        self._show_map(map_name)
        
        # Restore the original method
        self.screenshot_handler.get_latest_coordinates = original_get_latest
    
    def _open_wiki(self):
        """Open the official Escape from Tarkov wiki."""
        wiki_url = "https://escapefromtarkov.fandom.com/wiki/Escape_from_Tarkov_Wiki"
        webbrowser.open(wiki_url)
    
    def _show_about(self):
        """Show about dialog."""
        about_window = ctk.CTkToplevel(self.root)
        about_window.title("About Tarkov Map Assistant")
        about_window.geometry("500x300")
        about_window.resizable(False, False)
        
        # App info
        ctk.CTkLabel(
            about_window, 
            text="Tarkov Map Assistant",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(20, 5))
        
        ctk.CTkLabel(
            about_window, 
            text="Version 1.0.0"
        ).pack(pady=5)
        
        ctk.CTkLabel(
            about_window, 
            text="A tool for translating Escape from Tarkov game coordinates\n"
                 "to positions on map images."
        ).pack(pady=10)
        
        # Credits
        credits_frame = ctk.CTkFrame(about_window)
        credits_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(
            credits_frame, 
            text="Maps and data sourced from the tarkovdata project",
            font=ctk.CTkFont(size=12)
        ).pack(pady=5)
        
        # GitHub link
        github_button = ctk.CTkButton(
            about_window,
            text="Visit tarkovdata on GitHub",
            command=lambda: webbrowser.open("https://github.com/the-hideout/tarkov-data")
        )
        github_button.pack(pady=10)
        
        # Close button
        ctk.CTkButton(
            about_window, 
            text="Close", 
            command=about_window.destroy
        ).pack(pady=15)
    
    def _set_status(self, message):
        """Update the status bar with a message."""
        self.status_bar.configure(text=message)