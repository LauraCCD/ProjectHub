import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

from session_service import SessionService
from pdf_service import PDFService

if TYPE_CHECKING:
    from main_controller import MainController
class SettingsController:
    def __init__(self, main_controller: 'MainController', session_service: SessionService, pdf_service: PDFService):
        self.main_controller = main_controller # Reference to the main controller
        self.session_service = session_service
        self.pdf_service = pdf_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def change_theme(self, value: str) -> None:
        theme_map = {"Oscuro": "dark", "Claro": "light", "Sistema": "system"}
        ctk.set_appearance_mode(theme_map.get(value, "dark"))
        self.session_service.update_activity() # Update activity on interaction

    def export_data(self) -> None:
        # This would typically trigger a service call to export data
        # For now, a placeholder message
        messagebox.showinfo("Exportar Datos", "Funcionalidad de exportación de datos aún no implementada en detalle.")