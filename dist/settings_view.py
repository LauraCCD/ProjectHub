import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_controller import MainController
    from session_service import SessionService
    from pdf_service import PDFService
    from settings_controller import SettingsController

class SettingsView(ctk.CTkFrame):
    def __init__(self, parent_frame: ctk.CTkFrame, controller: 'MainController', session_service: 'SessionService', pdf_service: 'PDFService', settings_controller: 'SettingsController'):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.session_service = session_service
        self.pdf_service = pdf_service
        self.settings_controller = settings_controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Configuración", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").pack(side="left")

        settings_scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        settings_scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)

        # Apariencia
        appearance_card = ctk.CTkFrame(settings_scroll, fg_color="#16213e", corner_radius=15)
        appearance_card.pack(fill="x", pady=10)
        ctk.CTkLabel(appearance_card, text="Apariencia", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(padx=20, pady=15, anchor="w")

        theme_frame = ctk.CTkFrame(appearance_card, fg_color="transparent")
        theme_frame.pack(fill="x", padx=20, pady=(0, 15))
        ctk.CTkLabel(theme_frame, text="Tema de la aplicación:", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(side="left")
        theme_selector = ctk.CTkSegmentedButton(theme_frame, values=["Oscuro", "Claro", "Sistema"], font=ctk.CTkFont(size=12), command=self.settings_controller.change_theme)
        theme_selector.pack(side="right")
        theme_selector.set(ctk.get_appearance_mode().capitalize())

        # Notificaciones (Placeholder)
        notif_card = ctk.CTkFrame(settings_scroll, fg_color="#16213e", corner_radius=15)
        notif_card.pack(fill="x", pady=10)
        ctk.CTkLabel(notif_card, text="Notificaciones", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(padx=20, pady=15, anchor="w")

        notifications = [("Notificaciones por email", True), ("Recordatorios de tareas", True), ("Alertas de proyectos", False), ("Resumen semanal", True)]

        for notif_text, default_val in notifications:
            notif_frame = ctk.CTkFrame(notif_card, fg_color="transparent")
            notif_frame.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(notif_frame, text=notif_text, font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(side="left")
            switch = ctk.CTkSwitch(notif_frame, text="", onvalue=True, offvalue=False)
            switch.pack(side="right")
            if default_val:
                switch.select()

        # Datos (Placeholder)
        data_card = ctk.CTkFrame(settings_scroll, fg_color="#16213e", corner_radius=15)
        data_card.pack(fill="x", pady=10)
        ctk.CTkLabel(data_card, text="Gestión de Datos", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(padx=20, pady=15, anchor="w")

        buttons_frame = ctk.CTkFrame(data_card, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 20))
        ctk.CTkButton(buttons_frame, text="Exportar Datos", font=ctk.CTkFont(size=13), fg_color="#3498db", hover_color="#2980b9", corner_radius=8, height=40, width=150, command=self.controller.settings_controller.export_data).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Importar Datos", font=ctk.CTkFont(size=13), fg_color="#2d4263", hover_color="#3d5273", corner_radius=8, height=40, width=150).pack(side="left", padx=5)
        ctk.CTkButton(buttons_frame, text="Crear Respaldo", font=ctk.CTkFont(size=13), fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8, height=40, width=150).pack(side="left", padx=5)

    def load_data(self) -> None:
        """Method to refresh data in the settings view if needed."""
        pass