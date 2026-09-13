import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, Optional
from uuid import UUID
from datetime import date
from project_service import ProjectService
from session_service import SessionService
from user_service import UserService
from category_service import CategoryService
from permission_service import PermissionService
from typing import Optional

if TYPE_CHECKING:
    from main_controller import MainController

class ProjectController:
    def __init__(self, main_controller, project_service, session_service, permission_service, user_service, category_service):
        self.main_controller = main_controller
        self.project_service = project_service
        self.session_service = session_service
        self.permission_service = permission_service
        self.user_service = user_service
        self.category_service = category_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def create_project(self, name: str, description: str, priority: str, start_date: date, end_date: Optional[date], manager_id: UUID, category_id: UUID):
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesion para crear un proyecto.")
            return
        try:
            if not self.permission_service.can_create_project(current_user):
                raise PermissionError("No tiene permisos para crear proyectos.")
            new_project = self.project_service.create_project(name, description, priority, start_date, end_date, manager_id, category_id, current_user.id)
            messagebox.showinfo("Exito", f"Proyecto '{new_project.name}' creado con exito.")
            self.main_view.show_projects()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Creacion", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrio un error: {e}")