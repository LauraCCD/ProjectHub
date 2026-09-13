import customtkinter as ctk
from main_controller import MainController

if __name__ == "__main__":
    # Set appearance mode and default color theme
    ctk.set_appearance_mode("dark")  # Modes: "System" (default), "Dark", "Light"
    ctk.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    # Initialize the main controller, which sets up the MVC architecture
    app_controller = MainController()

    # Start the application
    app_controller.start()