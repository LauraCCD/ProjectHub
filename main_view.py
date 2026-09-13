import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

from dashboard_view import DashboardView
from initial_setup_view import InitialSetupView
from login_view import LoginView
from project_view import ProjectView
from task_view import TaskView
from resource_view import ResourceView
from settings_view import SettingsView
from milestone_view import MilestoneView
from reports_view import ReportsView

if TYPE_CHECKING:
    from main_controller import MainController

class MainView(ctk.CTk):
    def __init__(self, controller: 'MainController'):
        super().__init__()
        self.controller = controller

        self.title("ProjectHub - Gestión de Proyectos")
        self.geometry("1200x700")
        self.minsize(900, 600)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- Frame de Navegación ---
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(8, weight=1)

        ctk.CTkLabel(self.navigation_frame, text="ProjectHub", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        self.dashboard_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Dashboard",
                                              fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                              anchor="w", command=self.show_dashboard)
        self.dashboard_button.grid(row=1, column=0, sticky="ew", pady=(0, 5))

        self.project_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Proyectos",
                                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                            anchor="w", command=self.show_projects)
        self.project_button.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        self.task_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Tareas",
                                         fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                         anchor="w", command=self.show_tasks)
        self.task_button.grid(row=3, column=0, sticky="ew", pady=(0, 5))

        self.resource_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Recursos",
                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                             anchor="w", command=self.show_resources)
        self.resource_button.grid(row=4, column=0, sticky="ew", pady=(0, 5))

        self.milestone_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Hitos",
                                              fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                              anchor="w", command=self.show_milestones)
        self.milestone_button.grid(row=5, column=0, sticky="ew", pady=(0, 5))

        self.reports_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Reportes",
                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                             anchor="w", command=self.show_reports)
        self.reports_button.grid(row=6, column=0, sticky="ew", pady=(0, 5))

        self.settings_button = ctk.CTkButton(self.navigation_frame, corner_radius=0, height=40, border_spacing=10, text="Configuración",
                                             fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                                             anchor="w", command=self.show_settings)
        self.settings_button.grid(row=7, column=0, sticky="ew", pady=(0, 5))

        self.logout_button = ctk.CTkButton(self.navigation_frame, text="Cerrar Sesión", command=self.controller.logout)
        self.logout_button.grid(row=8, column=0, padx=20, pady=20, sticky="s")

        # --- Frame Principal de Contenido ---
        self.main_content_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        self.main_content_frame.grid_columnconfigure(0, weight=1)
        self.main_content_frame.grid_rowconfigure(0, weight=1)

        # Inicializar vistas
        self.initial_setup_view = InitialSetupView(self.main_content_frame, self.controller)
        self.login_view = LoginView(self.main_content_frame, self.controller)
        self.dashboard_view = DashboardView(self.main_content_frame, self.controller, self.controller.dashboard_service)
        self.project_view = ProjectView(self.main_content_frame, self.controller, self.controller.project_service, self.controller.category_service, self.controller.user_service, self.controller.project_controller, self.controller.milestone_controller)
        self.task_view = TaskView(self.main_content_frame, self.controller, self.controller.task_service, self.controller.session_service, self.controller.permission_service, self.controller.project_service, self.controller.user_service, self.controller.task_controller, self.controller.comment_service)
        self.resource_view = ResourceView(self.main_content_frame, self.controller, self.controller.user_service, self.controller.resource_controller, self.controller.team_controller)
        self.settings_view = SettingsView(self.main_content_frame, self.controller, self.controller.session_service, self.controller.pdf_service, self.controller.settings_controller)
        self.milestone_view = MilestoneView(self.main_content_frame, self.controller)
        self.reports_view = ReportsView(self.main_content_frame, self.controller)

        self.current_active_view = None

    def select_frame_by_name(self, name: str):
        self.dashboard_button.configure(fg_color=("gray75", "gray25") if name == "dashboard" else "transparent")
        self.project_button.configure(fg_color=("gray75", "gray25") if name == "projects" else "transparent")
        self.task_button.configure(fg_color=("gray75", "gray25") if name == "tasks" else "transparent")
        self.resource_button.configure(fg_color=("gray75", "gray25") if name == "resources" else "transparent")
        self.milestone_button.configure(fg_color=("gray75", "gray25") if name == "milestones" else "transparent")
        self.reports_button.configure(fg_color=("gray75", "gray25") if name == "reports" else "transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25") if name == "settings" else "transparent")

        if self.current_active_view:
            self.current_active_view.grid_forget()

        if name == "initial_setup":
            self.initial_setup_view.grid(row=0, column=0, sticky="nsew")
            self.current_active_view = self.initial_setup_view
        elif name == "login":
            self.login_view.grid(row=0, column=0, sticky="nsew")
            self.current_active_view = self.login_view
        elif name == "dashboard":
            self.dashboard_view.grid(row=0, column=0, sticky="nsew")
            self.dashboard_view.load_dashboard_data()
            self.current_active_view = self.dashboard_view
        elif name == "projects":
            self.project_view.grid(row=0, column=0, sticky="nsew")
            self.project_view.load_data()
            self.current_active_view = self.project_view
        elif name == "tasks":
            self.task_view.grid(row=0, column=0, sticky="nsew")
            self.task_view.load_data()
            self.current_active_view = self.task_view
        elif name == "resources":
            self.resource_view.grid(row=0, column=0, sticky="nsew")
            self.resource_view.load_data()
            self.current_active_view = self.resource_view
        elif name == "milestones":
            self.milestone_view.grid(row=0, column=0, sticky="nsew")
            self.milestone_view.load_data()
            self.current_active_view = self.milestone_view
        elif name == "reports":
            self.reports_view.grid(row=0, column=0, sticky="nsew")
            self.reports_view.load_data()
            self.current_active_view = self.reports_view
        elif name == "settings":
            self.settings_view.grid(row=0, column=0, sticky="nsew")
            self.settings_view.load_data()
            self.current_active_view = self.settings_view

    def show_initial_setup(self):
        self.select_frame_by_name("initial_setup")

    def show_login(self):
        self.select_frame_by_name("login")

    def show_dashboard(self):
        self.select_frame_by_name("dashboard")

    def show_projects(self):
        self.select_frame_by_name("projects")

    def show_tasks(self):
        self.select_frame_by_name("tasks")

    def show_resources(self):
        self.select_frame_by_name("resources")

    def show_milestones(self):
        self.select_frame_by_name("milestones")

    def show_reports(self):
        self.select_frame_by_name("reports")

    def show_settings(self):
        self.select_frame_by_name("settings")