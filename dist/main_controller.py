import customtkinter as ctk
from tkinter import messagebox

# Services
from session_service import SessionService
from auth_service import AuthService
from user_service import UserService
from project_service import ProjectService
from task_service import TaskService
from milestone_service import MilestoneService
from category_service import CategoryService
from permission_service import PermissionService
from pdf_service import PDFService
from notification_service import NotificationService
from comment_service import CommentService
from audit_service import AuditService
from dashboard_service import DashboardService
from team_service import TeamService
from report_service import ReportService

# Repositories
from user_repository import UserRepository
from project_repository import ProjectRepository
from task_repository import TaskRepository
from milestone_repository import MilestoneRepository
from category_repository import CategoryRepository
from project_user_repository import ProjectUserRepository
from audit_repository import AuditRepository
from comment_repository import CommentRepository
from team_repository import TeamRepository

# Database connection
from db_connection import DBConnection

# Views and Controllers
from main_view import MainView
from auth_controller import AuthController
from project_controller import ProjectController
from task_controller import TaskController
from resource_controller import ResourceController
from settings_controller import SettingsController
from milestone_controller import MilestoneController
from team_controller import TeamController

class MainController:
    def __init__(self):
        self.db_connection = DBConnection()

        # Initialize Repositories
        self.user_repo = UserRepository(self.db_connection)
        self.project_repo = ProjectRepository(self.db_connection)
        self.task_repo = TaskRepository(self.db_connection)
        self.milestone_repo = MilestoneRepository(self.db_connection)
        self.category_repo = CategoryRepository(self.db_connection)
        self.project_user_repo = ProjectUserRepository(self.db_connection)
        self.audit_repo = AuditRepository(self.db_connection)
        self.comment_repo = CommentRepository(self.db_connection)
        self.team_repo = TeamRepository(self.db_connection)

        # Initialize Services
        self.audit_service = AuditService(self.audit_repo)
        self.session_service = SessionService()
        self.auth_service = AuthService(self.user_repo, self.audit_service)
        self.user_service = UserService(self.user_repo, self.task_repo, self.auth_service)
        self.permission_service = PermissionService(self.project_repo, self.project_user_repo, self.task_repo, self.team_repo)
        self.category_service = CategoryService(self.category_repo)
        self.project_service = ProjectService(self.project_repo, self.user_repo, self.task_repo, self.category_repo, self.permission_service)
        self.task_service = TaskService(self.task_repo, self.project_repo, self.user_repo, self.project_user_repo, self.permission_service)
        self.milestone_service = MilestoneService(self.milestone_repo, self.project_repo)
        self.team_service = TeamService(self.team_repo, self.user_repo, self.permission_service)
        self.pdf_service = PDFService()
        self.dashboard_service = DashboardService(self.project_repo, self.user_repo, self.task_repo, self.permission_service)
        self.notification_service = NotificationService(self.task_repo, self.milestone_repo)
        self.comment_service = CommentService(self.comment_repo, self.task_repo, self.project_user_repo, self.permission_service)
        self.report_service = ReportService(self.project_repo, self.task_repo, self.milestone_repo, self.user_repo, self.permission_service)

        # Initialize Sub-Controllers
        self.auth_controller = AuthController(self, self.auth_service, self.session_service)
        self.project_controller = ProjectController(self, self.project_service, self.session_service, self.permission_service, self.user_service, self.category_service)
        self.task_controller = TaskController(self, self.task_service, self.session_service, self.permission_service, self.project_service, self.user_service)
        self.resource_controller = ResourceController(self, self.user_service, self.session_service, self.permission_service)
        self.settings_controller = SettingsController(self, self.session_service, self.pdf_service)
        self.milestone_controller = MilestoneController(self, self.milestone_service, self.session_service, self.permission_service)
        self.team_controller = TeamController(self, self.team_service, self.session_service, self.permission_service)

        self.main_view = MainView(self)
        self._initial_setup_check()

    def start(self):
        self.main_view.mainloop()

    def _initial_setup_check(self):
        if self.user_repo.count_active_admins() == 0:
            self.main_view.show_initial_setup()
        else:
            self.main_view.show_login()

    def logout(self):
        self.session_service.end_session()
        messagebox.showinfo("Sesión", "Ha cerrado sesión exitosamente.")
        self.main_view.destroy()

    def show_dashboard(self):
        self.main_view.show_dashboard()

    def show_projects(self):
        self.main_view.show_projects()

    def show_tasks(self):
        self.main_view.show_tasks()

    def show_resources(self):
        self.main_view.show_resources()

    def show_milestones(self):
        self.main_view.show_milestones()

    def show_reports(self):
        self.main_view.show_reports()

    def show_settings(self):
        self.main_view.show_settings()