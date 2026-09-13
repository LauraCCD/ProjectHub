import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from typing import TYPE_CHECKING, Dict, Any, List

if TYPE_CHECKING:
    from dashboard_service import DashboardService
    from main_controller import MainController

class DashboardView(ctk.CTkFrame):
    def __init__(self, parent_frame: ctk.CTkFrame, controller: 'MainController', dashboard_service: 'DashboardService'):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.dashboard_service = dashboard_service

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Dashboard", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkLabel(header, text=datetime.now().strftime("%d de %B, %Y"), font=ctk.CTkFont(size=14), text_color="#a0a0a0").pack(side="right")

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=10)

        self.bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bottom_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=20)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(1, weight=1)
        self.bottom_frame.grid_rowconfigure(0, weight=1)

        self.projects_card = ctk.CTkFrame(self.bottom_frame, fg_color="#16213e", corner_radius=15)
        self.projects_card.grid(row=0, column=0, sticky="nsew", padx=(0, 10))
        ctk.CTkLabel(self.projects_card, text="Proyectos Recientes", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(padx=20, pady=15, anchor="w")
        self.recent_projects_container = ctk.CTkFrame(self.projects_card, fg_color="transparent")
        self.recent_projects_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.resources_card = ctk.CTkFrame(self.bottom_frame, fg_color="#16213e", corner_radius=15)
        self.resources_card.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(self.resources_card, text="Disponibilidad de Recursos", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(padx=20, pady=15, anchor="w")
        self.resource_availability_container = ctk.CTkFrame(self.resources_card, fg_color="transparent")
        self.resource_availability_container.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def load_data(self) -> None:
        current_user = self.controller.session_service.current_user
        if not current_user:
            return

        try:
            summary = self.dashboard_service.get_dashboard_summary(current_user)
            recent_projects = self.dashboard_service.get_recent_projects(current_user)
            resource_availability = self.dashboard_service.get_resource_availability_summary(current_user)

            self._update_stats_cards(summary)
            self._update_recent_projects(recent_projects)
            self._update_resource_availability(resource_availability)

            # RN-NT-01/02/03/04/05: Mostrar alertas de notificaciones
            alerts = self.controller.notification_service.get_pending_alerts()
            if alerts:
                alert_text = "\n".join(alerts[:5])
                messagebox.showwarning("Notificaciones", alert_text)
                self.controller.notification_service.limpiar_notificaciones()

        except Exception as e:
            print(f"Error cargando dashboard: {e}")

    def _update_stats_cards(self, summary: Dict[str, Any]) -> None:
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        stats_data = [
            ("Proyectos Totales", str(summary["total_projects"]), "#4ecca3"),
            ("Proyectos Activos", str(summary["active_projects"]), "#3498db"),
            ("Recursos Activos", str(summary["total_resources"]), "#f39c12"),
            ("Tareas Pendientes", str(summary["pending_tasks"]), "#e74c3c"),
            ("Progreso General", f"{summary['overall_progress']}%", "#4ecca3"),
        ]

        for title, value, color in stats_data:
            card = ctk.CTkFrame(self.stats_frame, fg_color="#16213e", corner_radius=15, height=120)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(padx=20, pady=(15, 5), anchor="w")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=32, weight="bold"), text_color=color).pack(padx=20, anchor="w")

    def _update_recent_projects(self, projects: List[Dict[str, Any]]) -> None:
        for widget in self.recent_projects_container.winfo_children():
            widget.destroy()
        if not projects:
            ctk.CTkLabel(self.recent_projects_container, text="No hay proyectos recientes.", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(pady=20)
            return
        for project in projects:
            self._create_project_mini_card(self.recent_projects_container, project)

    def _create_project_mini_card(self, parent, project_data: Dict[str, Any]) -> None:
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=10, height=70)
        card.pack(fill="x", padx=5, pady=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=project_data["name"], font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff").pack(side="left", padx=10, pady=5)
        status_colors = {"En Curso": "#f39c12", "Planificado": "#3498db", "Finalizado": "#4ecca3", "Cancelado": "#6c757d"}
        ctk.CTkLabel(card, text=project_data["status"], font=ctk.CTkFont(size=11), text_color=status_colors.get(project_data["status"], "#a0a0a0")).pack(side="right", padx=(5, 5), pady=5)
        ctk.CTkLabel(card, text=f"{project_data['progress']}%", font=ctk.CTkFont(size=11), text_color="#4ecca3").pack(side="right", padx=(10, 0), pady=5)

    def _update_resource_availability(self, resources: List[Dict[str, Any]]) -> None:
        for widget in self.resource_availability_container.winfo_children():
            widget.destroy()
        if not resources:
            ctk.CTkLabel(self.resource_availability_container, text="No hay recursos disponibles.", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(pady=20)
            return
        for resource in resources:
            self._create_resource_mini_card(self.resource_availability_container, resource)

    def _create_resource_mini_card(self, parent, resource_data: Dict[str, Any]) -> None:
        card = ctk.CTkFrame(parent, fg_color="#1a1a2e", corner_radius=10, height=60)
        card.pack(fill="x", padx=5, pady=5)
        card.pack_propagate(False)
        ctk.CTkLabel(card, text=resource_data["name"], font=ctk.CTkFont(size=12, weight="bold"), text_color="#ffffff").pack(side="left", padx=10, pady=5)
        ctk.CTkLabel(card, text=resource_data["role"], font=ctk.CTkFont(size=11), text_color="#a0a0a0").pack(side="left", padx=5, pady=5)
        avail_color = "#4ecca3" if resource_data["availability"] >= 70 else "#f39c12" if resource_data["availability"] >= 40 else "#e74c3c"
        ctk.CTkLabel(card, text=f"{resource_data['availability']}%", font=ctk.CTkFont(size=14, weight="bold"), text_color=avail_color).pack(side="right", padx=10, pady=5)

    def load_dashboard_data(self) -> None:
        self.load_data()