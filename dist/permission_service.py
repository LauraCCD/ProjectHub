from typing import Optional
from uuid import UUID

from user import User
from project_repository import ProjectRepository
from team_repository import TeamRepository
from project_user_repository import ProjectUserRepository
from task_repository import TaskRepository

class PermissionService:

    def __init__(self, project_repo: ProjectRepository, project_user_repo: ProjectUserRepository, task_repo: TaskRepository, team_repo: TeamRepository = None):
        self.project_repo = project_repo
        self.project_user_repo = project_user_repo
        self.task_repo = task_repo
        self.team_repo = team_repo

    def has_permission(self, user: User, action: str, entity_id: Optional[UUID] = None, entity_type: Optional[str] = None) -> bool:
        if user.role == "Administrador":
            return True
        if action == "view_project":
            return self.can_view_project(user, entity_id)
        if action == "edit_project":
            return self.can_edit_project(user, entity_id)
        if action == "change_project_status":
            return self.can_change_project_status(user, entity_id)
        if action == "create_task":
            return self.can_create_task(user, entity_id)
        if action == "edit_task":
            return self.can_edit_task(user, entity_id)
        if action == "update_task_progress":
            return self.can_update_task_progress(user, entity_id)
        if action == "comment_on_task":
            return self.can_comment_on_task(user, entity_id)
        if action == "create_team":
            return self.can_create_team(user)
        if action == "edit_team":
            return self.can_edit_team(user, entity_id)
        return False

    def can_view_project(self, user: User, project_id: UUID) -> bool:
        if user.role == "Administrador":
            return True
        project_users = self.project_user_repo.get_users_by_project(project_id)
        return any(pu.user_id == user.id for pu in project_users)

    def can_edit_project(self, user: User, project_id: UUID) -> bool:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False
        return user.role == "Administrador" or (user.role == "Gestor" and project.manager_id == user.id)

    def can_change_project_status(self, user: User, project_id: UUID) -> bool:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False
        return user.role in ["Administrador", "Gestor"] and project.manager_id == user.id

    def can_view_task(self, user: User, task_id: UUID) -> bool:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return False
        return self.can_view_project(user, task.project_id)

    def can_create_task(self, user: User, project_id: UUID) -> bool:
        project = self.project_repo.get_by_id(project_id)
        if not project:
            return False
        return user.role == "Administrador" or (user.role == "Gestor" and project.manager_id == user.id)

    def can_edit_task(self, user: User, task_id: UUID) -> bool:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return False
        project = self.project_repo.get_by_id(task.project_id)
        if not project:
            return False
        return user.role == "Administrador" or \
               (user.role == "Gestor" and project.manager_id == user.id) or \
               (user.id == task.assignee_id)

    def can_update_task_progress(self, user: User, task_id: UUID) -> bool:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return False
        project = self.project_repo.get_by_id(task.project_id)
        if not project:
            return False
        return user.role == "Administrador" or \
               (user.role == "Gestor" and project.manager_id == user.id) or \
               (user.id == task.assignee_id)

    def can_comment_on_task(self, user: User, task_id: UUID) -> bool:
        task = self.task_repo.get_by_id(task_id)
        if not task:
            return False
        project_users = self.project_user_repo.get_users_by_project(task.project_id)
        return any(pu.user_id == user.id for pu in project_users) or user.role == "Administrador"

    def can_create_project(self, user: User) -> bool:
        return user.role in ["Administrador", "Gestor"]

    def can_create_team(self, user: User) -> bool:
        return user.role in ["Administrador", "Gestor"]

    def can_edit_team(self, user: User, team_id: UUID) -> bool:
        if user.role == "Administrador":
            return True
        return False