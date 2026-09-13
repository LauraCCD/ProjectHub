import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_controller import MainController

class ReportsView(ctk.CTkFrame):
    def __init__(self, parent_frame: ctk.CTkFrame, controller: 'MainController'):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Reportes", font=ctk.CTkFont(size=28, weight="bold"),
                     text_color="#ffffff").pack(side="left")

        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))

        ctk.CTkLabel(selector_frame, text="Tipo de reporte:", text_color="#a0a0a0").pack(side="left", padx=(0, 10))

        self.report_combo = ctk.CTkComboBox(
            selector_frame,
            values=["Proyectos", "Tareas", "Hitos", "Recursos"],
            width=250,
            command=self._on_report_change
        )
        self.report_combo.set("Proyectos")
        self.report_combo.pack(side="left", padx=(0, 10))

        ctk.CTkButton(selector_frame, text="Generar", width=100, fg_color="#4ecca3",
                      text_color="#1a1a2e", hover_color="#3db892", corner_radius=8,
                      command=self.load_data).pack(side="left", padx=(0, 10))

        ctk.CTkButton(selector_frame, text="Exportar PDF", width=120, fg_color="#3498db",
                      hover_color="#2980b9", corner_radius=8,
                      command=self._export_pdf).pack(side="left")

        self.scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

    def _on_report_change(self, _):
        self.load_data()

    def load_data(self) -> None:
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        current_user = self.controller.session_service.current_user
        if not current_user:
            return

        selected = self.report_combo.get()

        # Validar permisos por rol
        if selected == "Recursos" and current_user.role == "Colaborador":
            ctk.CTkLabel(self.scroll_frame, text="No tiene permisos para ver este reporte.",
                         text_color="#e74c3c", font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=30)
            return

        try:
            if selected == "Proyectos":
                data = self.controller.report_service.get_projects_report(current_user)
            elif selected == "Tareas":
                data = self.controller.report_service.get_tasks_report(current_user)
            elif selected == "Hitos":
                data = self.controller.report_service.get_milestones_report(current_user)
            elif selected == "Recursos":
                data = self.controller.report_service.get_resources_report(current_user)
            else:
                data = []

            if not data:
                ctk.CTkLabel(self.scroll_frame, text="No hay datos para mostrar.",
                             text_color="gray", font=ctk.CTkFont(size=14)).grid(row=0, column=0, pady=30)
                return

            headers = list(data[0].keys())
            for col, h in enumerate(headers):
                ctk.CTkLabel(self.scroll_frame, text=h, font=ctk.CTkFont(weight="bold"),
                             text_color="#4ecca3").grid(row=0, column=col, padx=10, pady=5, sticky="w")

            for row_idx, item in enumerate(data, start=1):
                bg = "#16213e" if row_idx % 2 == 0 else "#1a1a2e"
                for col, key in enumerate(headers):
                    ctk.CTkLabel(self.scroll_frame, text=str(item[key]),
                                 text_color="#ffffff", fg_color=bg,
                                 corner_radius=4).grid(row=row_idx, column=col, padx=10, pady=2, sticky="w")

        except PermissionError as e:
            messagebox.showerror("Acceso Denegado", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar reporte: {e}")

    def _export_pdf(self) -> None:
        current_user = self.controller.session_service.current_user
        if not current_user:
            return
        selected = self.report_combo.get()

        if selected == "Recursos" and current_user.role == "Colaborador":
            messagebox.showerror("Acceso Denegado", "No tiene permisos para exportar este reporte.")
            return

        try:
            if selected == "Proyectos":
                data = self.controller.report_service.get_projects_report(current_user)
            elif selected == "Tareas":
                data = self.controller.report_service.get_tasks_report(current_user)
            elif selected == "Hitos":
                data = self.controller.report_service.get_milestones_report(current_user)
            elif selected == "Recursos":
                data = self.controller.report_service.get_resources_report(current_user)
            else:
                data = []

            filename = self.controller.pdf_service.exportar(selected, data, current_user.name)
            messagebox.showinfo("PDF Generado", f"Archivo generado: {filename}")
        except PermissionError as e:
            messagebox.showerror("Acceso Denegado", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {e}")