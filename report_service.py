from typing import List, Dict, Any
from uuid import UUID
from datetime import datetime

from user import User
from project_repository import ProjectRepository
from task_repository import TaskRepository
from milestone_repository import MilestoneRepository
from user_repository import UserRepository
from permission_service import PermissionService

class ReportService:
    def __init__(self, project_repo: ProjectRepository, task_repo: TaskRepository,
                 milestone_repo: MilestoneRepository, user_repo: UserRepository,
                 permission_service: PermissionService):
        self.project_repo = project_repo
        self.task_repo = task_repo
        self.milestone_repo = milestone_repo
        self.user_repo = user_repo
        self.permission_service = permission_service

    def get_projects_report(self, current_user: User) -> List[Dict[str, Any]]:
        all_projects = self.project_repo.get_all()
        accessible = [p for p in all_projects
                      if self.permission_service.can_view_project(current_user, p.id)]
        result = []
        for p in accessible:
            manager = self.user_repo.get_by_id(p.manager_id)
            result.append({
                "Nombre": p.name,
                "Estado": p.status,
                "Prioridad": p.priority,
                "Progreso": f"{p.progress}%",
                "Inicio": str(p.start_date),
                "Fin": str(p.end_date) if p.end_date else "N/A",
                "Gestor": f"{manager.name} {manager.last_name}" if manager else "N/A"
            })
        return result

    def get_tasks_report(self, current_user: User) -> List[Dict[str, Any]]:
        all_tasks = self.task_repo.get_all()
        if current_user.role == "Colaborador":
            tasks = [t for t in all_tasks if t.assignee_id == current_user.id]
        elif current_user.role == "Gestor":
            projects = self.project_repo.get_all()
            managed_ids = {p.id for p in projects if p.manager_id == current_user.id}
            tasks = [t for t in all_tasks if t.project_id in managed_ids]
        else:
            tasks = all_tasks

        result = []
        for t in tasks:
            assignee = self.user_repo.get_by_id(t.assignee_id)
            result.append({
                "Título": t.title,
                "Estado": t.status,
                "Prioridad": t.priority,
                "Progreso": f"{t.progress}%",
                "Vence": str(t.due_date),
                "Asignado a": f"{assignee.name} {assignee.last_name}" if assignee else "N/A"
            })
        return result

    def get_milestones_report(self, current_user: User) -> List[Dict[str, Any]]:
        projects = self.project_repo.get_all()
        accessible = [p for p in projects
                      if self.permission_service.can_view_project(current_user, p.id)]
        result = []
        for p in accessible:
            milestones = self.milestone_repo.list_chronological_by_project(p.id)
            for m in milestones:
                result.append({
                    "Hito": m.name,
                    "Proyecto": p.name,
                    "Fecha Programada": str(m.scheduled_date),
                    "Fecha Cumplimiento": str(m.effective_completion_date) if m.effective_completion_date else "N/A",
                    "Estado": m.status
                })
        return result

    def get_resources_report(self, current_user: User) -> List[Dict[str, Any]]:
        if current_user.role not in ["Administrador", "Gestor"]:
            raise PermissionError("No tiene permisos para ver el reporte de recursos.")
        users = self.user_repo.get_all()
        result = []
        for u in users:
            if u.status == "Activo":
                result.append({
                    "Nombre": f"{u.name} {u.last_name}",
                    "Rol": u.role,
                    "Disponibilidad": f"{u.availability}%",
                    "Estado": u.status,
                    "Correo": u.email
                })
        return result