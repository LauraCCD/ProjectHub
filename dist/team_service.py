from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from uuid import UUID

from team import Team
from team_repository import TeamRepository
from user import User
from user_repository import UserRepository

if TYPE_CHECKING:
    from permission_service import PermissionService

class TeamService:
    def __init__(self, team_repo: TeamRepository, user_repo: UserRepository, permission_service: 'PermissionService'):
        self.team_repo = team_repo
        self.user_repo = user_repo
        self.permission_service = permission_service

    def validar_nombre_equipo(self, name: str, team_id: Optional[UUID] = None) -> None:
        if not name or not name.strip():
            raise ValueError("El nombre del equipo no puede estar vacío.")
        if len(name.strip()) < 3:
            raise ValueError("El nombre del equipo debe tener al menos 3 caracteres.")
        existing_team = self.team_repo.get_by_name(name.strip())
        if existing_team and (team_id is None or existing_team.id != team_id):
            raise ValueError(f"Ya existe un equipo con el nombre '{name}'.")

    def validar_estado_equipo(self, status: str) -> None:
        if status not in ["Activo", "Inactivo"]:
            raise ValueError("Estado de equipo inválido. Debe ser 'Activo' o 'Inactivo'.")

    def create_team(self, name: str, description: Optional[str], creator_user: User) -> Team:
        if not self.permission_service.can_create_team(creator_user):
            raise PermissionError("No tiene permisos para crear equipos.")
        self.validar_nombre_equipo(name)
        new_team = Team(
            id=None,
            name=name.strip(),
            description=description.strip() if description else None,
            created_at=datetime.now(),
            status="Activo",
            deleted_at=None
        )
        new_team.id = self.team_repo.insert(new_team)
        return new_team

    def update_team(self, team_id: UUID, name: str, description: Optional[str], status: str, current_user: User) -> Team:
        team = self.team_repo.get_by_id(team_id)
        if not team:
            raise ValueError("Equipo no encontrado.")
        if not self.permission_service.can_edit_team(current_user, team_id):
            raise PermissionError("No tiene permisos para editar este equipo.")
        self.validar_nombre_equipo(name, team_id)
        self.validar_estado_equipo(status)
        team.name = name.strip()
        team.description = description.strip() if description else None
        team.status = status
        self.team_repo.update(team)
        return team

    def get_all_teams(self) -> List[Team]:
        return self.team_repo.get_all()