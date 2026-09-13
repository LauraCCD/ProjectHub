from typing import Dict, Any, List
from uuid import UUID
from datetime import datetime
from user import User
from project_repository import ProjectRepository
from user_repository import UserRepository
from task_repository import TaskRepository
from permission_service import PermissionService

class DashboardService:
    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository, task_repo: TaskRepository, permission_service: PermissionService):
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.task_repo = task_repo
        self.permission_service = permission_service

    def get_dashboard_summary(self, current_user: User) -> Dict[str, Any]:
        """RN-RE-03: Obtiene datos agregados para el dashboard ejecutivo."""
        all_projects = self.project_repo.get_all()
        all_users = self.user_repo.get_all()
        all_tasks = self.task_repo.get_all()

        # Apply RBAC filtering
        accessible_projects = [
            p for p in all_projects
            if self.permission_service.can_view_project(current_user, p.id)
        ]
        accessible_tasks = [
            t for t in all_tasks
            if self.permission_service.can_view_task(current_user, t.id) # Assuming can_view_task is implemented
        ]

        active_projects = [p for p in accessible_projects if p.status != "Completado"]
        pending_tasks = [t for t in accessible_tasks if t.status not in ["Completada", "Cancelada"]]
        
        # Resource availability (assuming all users are potential resources)
        available_resources = [u for u in all_users if u.status == 'Activo' and u.availability > 0]

        # Simple progress calculation (can be more complex)
        total_progress = sum(p.progress for p in accessible_projects)
        overall_progress = (total_progress / (len(accessible_projects) * 100)) * 100 if accessible_projects else 0

        return {
            "total_projects": len(accessible_projects),
            "active_projects": len(active_projects),
            "total_resources": len(available_resources),
            "pending_tasks": len(pending_tasks),
            "overall_progress": round(overall_progress, 2)
        }

    def get_recent_projects(self, current_user: User, limit: int = 3) -> List[Dict[str, Any]]:
        all_projects = self.project_repo.get_all()
        accessible_projects = [
            p for p in all_projects
            if self.permission_service.can_view_project(current_user, p.id)
        ]
        # Sort by creation date (most recent first)
        recent_projects = sorted(accessible_projects, key=lambda p: p.created_at, reverse=True)[:limit]
        
        # Convert to dicts for easier display in view
        return [
            {
                "id": p.id,
                "name": p.name,
                "status": p.status,
                "progress": p.progress,
                "priority": p.priority,
                "manager_name": self.user_repo.get_by_id(p.manager_id).name if self.user_repo.get_by_id(p.manager_id) else "N/A"
            } for p in recent_projects
        ]

    def get_resource_availability_summary(self, current_user: User, limit: int = 4) -> List[Dict[str, Any]]:
        all_users = self.user_repo.get_all()
        # Filter users based on who can be considered a "resource" for the current user's view
        # For simplicity, let's assume all active users are resources for dashboard display
        active_resources = [u for u in all_users if u.status == 'Activo']
        
        # Sort by availability (least available first, to highlight potential bottlenecks)
        sorted_resources = sorted(active_resources, key=lambda u: u.availability)[:limit]

        return [
            {
                "id": u.id,
                "name": f"{u.name} {u.last_name}",
                "role": u.role,
                "availability": u.availability
            } for u in sorted_resources
        ]