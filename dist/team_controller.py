import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from team import Team
from team_service import TeamService
from session_service import SessionService
from permission_service import PermissionService

if TYPE_CHECKING:
    from main_controller import MainController

class TeamController:
    def __init__(self, main_controller: 'MainController', team_service: TeamService, session_service: SessionService, permission_service: PermissionService):
        self.main_controller = main_controller
        self.team_service = team_service
        self.session_service = session_service
        self.permission_service = permission_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def create_team(self, name: str, description: Optional[str]) -> None:
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para crear equipos.")
            return
        try:
            new_team = self.team_service.create_team(name, description, current_user)
            messagebox.showinfo("Éxito", f"Equipo '{new_team.name}' creado con éxito.")
            self.main_view.resource_view.load_data() # Refrescar la vista de recursos para mostrar el nuevo equipo
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Creación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

    def update_team(self, team_id: UUID, name: str, description: Optional[str], status: str) -> None:
        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para actualizar equipos.")
            return
        try:
            updated_team = self.team_service.update_team(team_id, name, description, status, current_user)
            messagebox.showinfo("Éxito", f"Equipo '{updated_team.name}' actualizado con éxito.")
            self.main_view.resource_view.load_data()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Actualización", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}")

    def get_all_teams(self) -> List[Team]:
        return self.team_service.get_all_teams()

    def soft_delete_team(self, team_id: UUID) -> None:
        current_user = self.session_service.current_user
        if not current_user or not self.permission_service.can_delete_team(current_user, team_id): # Asumiendo can_delete_team
            messagebox.showerror("Permiso Denegado", "No tiene permisos para eliminar equipos.")
            return
        if messagebox.askyesno("Confirmar Eliminación", "¿Está seguro de que desea eliminar este equipo?"):
            try:
                self.team_service.team_repo.soft_delete(team_id)
                messagebox.showinfo("Éxito", "Equipo eliminado lógicamente.")
                self.main_view.resource_view.load_data()
            except Exception as e:
                messagebox.showerror("Error", f"Error al eliminar equipo: {e}")