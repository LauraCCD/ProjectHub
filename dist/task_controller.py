import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING
from uuid import UUID
from datetime import date
from task_service import TaskService
from session_service import SessionService
from project_service import ProjectService
from user_service import UserService
from permission_service import PermissionService

if TYPE_CHECKING:
    from main_controller import MainController

class TaskController:
    def __init__(self, main_controller, task_service, session_service, permission_service, project_service, user_service):
        self.main_controller = main_controller
        self.task_service = task_service
        self.session_service = session_service
        self.permission_service = permission_service
        self.project_service = project_service
        self.user_service = user_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def create_task(self, title, description, project_id, assignee_id, priority, due_date):
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para crear una tarea.")
            return
        try:
            if not self.permission_service.can_create_task(current_user, project_id):
                raise PermissionError("No tiene permisos para crear tareas en este proyecto.")
            new_task = self.task_service.create_task(title, description, project_id, assignee_id, priority, due_date, current_user.id)

            # RN-NT-04: Notificar asignación de tarea
            assignee = self.user_service.user_repo.get_by_id(assignee_id)
            if assignee:
                self.main_controller.notification_service.notificar_asignacion_tarea(
                    new_task.title, f"{assignee.name} {assignee.last_name}"
                )

            messagebox.showinfo("Éxito", f"Tarea '{new_task.title}' creada con éxito.")
            self.main_view.show_tasks()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Creación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")