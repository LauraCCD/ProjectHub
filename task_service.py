from datetime import date, datetime
from typing import Optional, List
from uuid import UUID

from task import Task
from user import User
from project import Project
from task_repository import TaskRepository
from project_repository import ProjectRepository
from user_repository import UserRepository
from project_user_repository import ProjectUserRepository
from permission_service import PermissionService

class TaskService:
    def __init__(self, task_repo: TaskRepository, project_repo: ProjectRepository, user_repo: UserRepository, project_user_repo: ProjectUserRepository, permission_service: PermissionService):
        self.task_repo = task_repo
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.project_user_repo = project_user_repo
        self.permission_service = permission_service

    def validar_titulo(self, title: str) -> None:
        """RN-TA-01/02: Título obligatorio, mínimo 5 caracteres."""
        if not title or not title.strip():
            raise ValueError("El título de la tarea no puede estar vacío.")
        if len(title.strip()) < 5:
            raise ValueError("El título de la tarea debe tener al menos 5 caracteres.")

    def validar_proyecto_activo(self, project_id: UUID) -> Project:
        """RN-TA-03/04: Toda tarea pertenece a un proyecto Planificado o En Curso."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"El proyecto con ID {project_id} no existe.")
        if project.status not in ["Planificado", "En Curso"]:
            raise ValueError(f"No se pueden añadir tareas a proyectos en estado '{project.status}'.")
        return project

    def validar_responsable(self, assignee_id: UUID, project_id: UUID) -> User:
        """RN-TA-05/06: Responsable obligatorio y debe pertenecer al proyecto."""
        assignee = self.user_repo.get_by_id(assignee_id)
        if not assignee:
            raise ValueError(f"El responsable con ID {assignee_id} no existe.")
        
        project_users = self.project_user_repo.get_users_by_project(project_id)
        if not any(pu.user_id == assignee_id for pu in project_users):
            raise ValueError("El responsable no pertenece al proyecto.")
        return assignee

    def validar_prioridad(self, priority: str) -> None:
        """RN-TA-07: Prioridad: Alta, Media, Baja."""
        if priority not in ["Alta", "Media", "Baja"]:
            raise ValueError("Prioridad inválida. Debe ser 'Alta', 'Media' o 'Baja'.")

    def validar_transicion_estado(self, old_status: str, new_status: str) -> None:
        """RN-TA-08/09: Estados: Pendiente→En Progreso→Completada. Cualquiera puede pasar a Vencida."""
        if old_status == new_status:
            return
        
        valid_transitions = {
            "Pendiente": ["En Progreso", "Vencida"],
            "En Progreso": ["Completada", "Vencida"],
            "Completada": [], # Terminal
            "Vencida": ["En Progreso"] # Solo un gestor puede reactivar
        }
        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Transición de estado de tarea inválida: de '{old_status}' a '{new_status}'.")

    def verificar_vencimiento(self, task: Task) -> None:
        """RN-TA-10: Vencimiento automático si se supera la fecha límite."""
        if task.status not in ["Completada", "Vencida"] and task.due_date < date.today():
            task.status = "Vencida"
            self.task_repo.update(task)

    def actualizar_avance(self, task_id: UUID, new_progress: int, current_user: User) -> Task:
        """RN-TA-11/12: Avance 0-100. Solo responsable o gestor puede modificarlo."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Tarea no encontrada.")
        if not (0 <= new_progress <= 100):
            raise ValueError("El avance debe estar entre 0 y 100.")
        
        project = self.project_repo.get_by_id(task.project_id)
        if not project:
            raise ValueError("Proyecto de la tarea no encontrado.")

        if not (current_user.id == task.assignee_id or (current_user.role == "Gestor" and current_user.id == project.manager_id)):
            raise PermissionError("Solo el responsable de la tarea o el gestor del proyecto pueden modificar el avance.")
        
        task.progress = new_progress
        self.task_repo.update(task)
        return task

    def validar_completitud(self, task: Task) -> None:
        """RN-TA-15: Completada requiere avance = 100%."""
        if task.status == "Completada" and task.progress < 100:
            raise ValueError("Una tarea no puede marcarse como 'Completada' si su avance no es 100%.")
        
    def update_task_status(self, task_id: UUID, new_status: str, current_user: User) -> Task:
        """RN-TA-08/09: Actualiza el estado de una tarea validando transiciones."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError("Tarea no encontrada.")
        
        self.validar_transicion_estado(task.status, new_status)
        
        # Validar completitud si se marca como Completada
        if new_status == "Completada" and task.progress < 100:
            raise ValueError("No puedes marcar la tarea como 'Completada' si el avance no es 100%.")
        
        task.status = new_status
        self.task_repo.update(task)
        return task

    def create_task(self, title: str, description: str, project_id: UUID, assignee_id: UUID, priority: str, due_date: date, creator_id: UUID) -> Task:
        """
        Crea una nueva tarea aplicando todas las reglas de negocio.
        RN-TA-01/02, RN-TA-03/04, RN-TA-05/06, RN-TA-07
        """
        self.validar_titulo(title)
        project = self.validar_proyecto_activo(project_id)
        assignee = self.validar_responsable(assignee_id, project_id)
        self.validar_prioridad(priority)

        new_task = Task(
            id=None,
            title=title.strip(),
            description=description.strip() if description else None,
            project_id=project_id,
            assignee_id=assignee_id,
            status="Pendiente", # Default status for new tasks
            priority=priority,
            due_date=due_date,
            progress=0,
            created_at=datetime.now(),
            deleted_at=None
        )
        new_task.id = self.task_repo.insert(new_task)
        return new_task