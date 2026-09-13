import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID
from datetime import date

from milestone import Milestone
from milestone_service import MilestoneService
from session_service import SessionService
from permission_service import PermissionService

if TYPE_CHECKING:
    from main_controller import MainController

class MilestoneController:
    def __init__(self, main_controller: 'MainController', milestone_service: MilestoneService, session_service: SessionService, permission_service: PermissionService):
        self.main_controller = main_controller
        self.milestone_service = milestone_service
        self.session_service = session_service
        self.permission_service = permission_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def create_milestone(self, name: str, description: Optional[str], project_id: UUID, scheduled_date: date) -> None:
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para crear hitos.")
            return
        try:
            if not self.permission_service.can_edit_project(current_user, project_id):
                raise PermissionError("No tiene permisos para crear hitos en este proyecto.")
            new_milestone = self.milestone_service.create_milestone(name, description, project_id, scheduled_date)
            messagebox.showinfo("Éxito", f"Hito '{new_milestone.name}' creado con éxito.")
            self.main_view.project_view.load_data()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Creación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

    def update_milestone(self, milestone_id: UUID, name: str, description: Optional[str], scheduled_date: date, effective_completion_date: Optional[date], status: str) -> None:
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para actualizar hitos.")
            return
        try:
            milestone = self.milestone_service.milestone_repo.get_by_id(milestone_id)
            if not milestone:
                raise ValueError("Hito no encontrado.")
            if not self.permission_service.can_edit_project(current_user, milestone.project_id):
                raise PermissionError("No tiene permisos para actualizar este hito.")
            updated_milestone = self.milestone_service.update_milestone(milestone_id, name, description, scheduled_date, effective_completion_date, status)
            messagebox.showinfo("Éxito", f"Hito '{updated_milestone.name}' actualizado con éxito.")
            self.main_view.project_view.load_data()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Actualización", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

    def get_milestones_by_project(self, project_id: UUID) -> List[Milestone]:
        return self.milestone_service.milestone_repo.list_chronological_by_project(project_id)