import re
from datetime import date, datetime, timedelta
from typing import Optional, List
from uuid import UUID
from project import Project
from user import User
from project_repository import ProjectRepository
from user_repository import UserRepository
from task_repository import TaskRepository
from category_repository import CategoryRepository
from permission_service import PermissionService

class ProjectService:
    def __init__(self, project_repo: ProjectRepository, user_repo: UserRepository, task_repo: TaskRepository, category_repo: CategoryRepository, permission_service: PermissionService):
        self.project_repo = project_repo
        self.user_repo = user_repo
        self.task_repo = task_repo
        self.category_repo = category_repo
        self.permission_service = permission_service

    def validar_nombre(self, name: str) -> None:
        """RN-PR-01: Nombre obligatorio, mínimo 5 caracteres, sin espacios vacíos."""
        if not name or not name.strip():
            raise ValueError("El nombre del proyecto no puede estar vacío.")
        if len(name.strip()) < 5:
            raise ValueError("El nombre del proyecto debe tener al menos 5 caracteres.")

    def verificar_unicidad(self, name: str, project_id: Optional[UUID] = None) -> None:
        """RN-PR-02: Nombre único por organización."""
        existing_project = self.project_repo.get_by_name(name.strip())
        if existing_project and (project_id is None or existing_project.id != project_id):
            raise ValueError(f"Ya existe un proyecto con el nombre '{name}'.")

    def validar_fecha_inicio(self, start_date: date) -> None:
        """RN-PR-03: Fecha de inicio obligatoria y válida."""
        if not start_date:
            raise ValueError("La fecha de inicio es obligatoria.")

    def validar_coherencia_fechas(self, start_date: date, end_date: Optional[date]) -> None:
        """RN-PR-04: Fecha fin > Fecha inicio."""
        if end_date and end_date <= start_date:
            raise ValueError("La fecha de fin debe ser posterior a la fecha de inicio.")

    def calcular_estado_temporal(self, project: Project) -> str:
        """RN-PR-05: Marca visualmente si la fecha fin es ausente y han pasado 365 días."""
        if project.end_date is None and (date.today() - project.start_date).days > 365:
            return "Alerta: Sin fecha fin y lleva más de un año."
        return ""

    def validar_prioridad(self, priority: str) -> None:
        """RN-PR-06: Prioridad: solo Alta, Media, Baja."""
        if priority not in ["Alta", "Media", "Baja"]:
            raise ValueError("Prioridad inválida. Debe ser 'Alta', 'Media' o 'Baja'.")

    def validar_estado(self, status: str) -> None:
        """RN-PR-07: Estados: Planificado, En Curso, Finalizado, Cancelado."""
        if status not in ["Planificado", "En Curso", "Finalizado", "Cancelado"]:
            raise ValueError("Estado inválido. Debe ser 'Planificado', 'En Curso', 'Finalizado' o 'Cancelado'.")

    def validar_transicion_estado(self, old_status: str, new_status: str) -> None:
        """RN-PR-08: Transiciones de estado permitidas."""
        if old_status == new_status:
            return
        valid_transitions = {
            "Planificado": ["En Curso"],
            "En Curso": ["Finalizado", "Cancelado"],
            "Finalizado": [],
            "Cancelado": []
        }
        if new_status not in valid_transitions.get(old_status, []):
            raise ValueError(f"Transición de estado inválida: de '{old_status}' a '{new_status}'.")

    def verificar_permiso_estado(self, current_user: User, project: Project) -> None:
        """RN-PR-09: Solo Administrador o Gestor puede cambiar estado."""
        if not self.permission_service.can_change_project_status(current_user, project.id):
            raise PermissionError("No tiene permisos para cambiar el estado de este proyecto.")

    def validar_categoria(self, category_id: UUID) -> None:
        """RN-PR-10/11: Proyecto requiere categoría existente."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"La categoría con ID {category_id} no existe.")

    def validar_gestor(self, manager_id: UUID) -> User:
        """RN-PR-12: Gestor responsable obligatorio, activo y con rol gestor/admin."""
        manager = self.user_repo.get_by_id(manager_id)
        if not manager:
            raise ValueError(f"El gestor con ID {manager_id} no existe.")
        if manager.status == 'Inactivo':
            raise ValueError("El gestor asignado está inactivo.")
        if manager.role not in ['Gestor', 'Administrador']:
            raise ValueError("El usuario asignado como gestor no tiene el rol 'Gestor' o 'Administrador'.")
        return manager

    def validar_usuario_activo_para_asignacion(self, user_id: UUID) -> User:
        """RN-US-12: Usuario inactivo no puede recibir asignaciones."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError(f"El usuario con ID {user_id} no existe.")
        if user.status == 'Inactivo':
            raise ValueError(f"El usuario '{user.name} {user.last_name}' está inactivo y no puede recibir asignaciones.")
        return user

    def verificar_operaciones_permitidas(self, project: Project, operation: str) -> None:
        """RN-PR-15/16/17: Proyectos Finalizados y Cancelados bloquean operaciones."""
        if project.status in ["Finalizado", "Cancelado"]:
            if operation == "read_only" and project.status == "Finalizado":
                return
            raise PermissionError(f"No se pueden realizar operaciones en proyectos '{project.status}'.")

    def verificar_tareas_activas(self, project_id: UUID) -> None:
        """RN-EL-02: Proyecto con tareas activas no puede eliminarse."""
        active_tasks_count = self.task_repo.count_active_tasks_for_project(project_id)
        if active_tasks_count > 0:
            raise ValueError(f"El proyecto tiene {active_tasks_count} tareas activas. Cierre o reasigne las tareas antes de eliminar el proyecto.")

    def create_project(self, name: str, description: str, priority: str, start_date: date, end_date: Optional[date], manager_id: UUID, category_id: UUID, creator_id: UUID) -> Project:
        """
        Crea un nuevo proyecto aplicando todas las reglas de negocio.
        RN-PR-01, RN-PR-02, RN-PR-03, RN-PR-04, RN-PR-06, RN-PR-10/11, RN-PR-12, RN-US-12
        """
        self.validar_nombre(name)
        self.verificar_unicidad(name)
        self.validar_fecha_inicio(start_date)
        self.validar_coherencia_fechas(start_date, end_date)
        self.validar_prioridad(priority)
        self.validar_categoria(category_id)
        manager = self.validar_gestor(manager_id)
        self.validar_usuario_activo_para_asignacion(manager_id)  # RN-US-12

        new_project = Project(
            id=None,
            name=name.strip(),
            description=description.strip() if description else None,
            status="Planificado",
            progress=0,
            priority=priority,
            start_date=start_date,
            end_date=end_date,
            manager_id=manager_id,
            category_id=category_id,
            budget=None,
            created_at=datetime.now(),
            deleted_at=None
        )
        new_project.id = self.project_repo.insert(new_project)
        self.permission_service.project_user_repo.assign_user_to_project(new_project.id, manager_id)
        return new_project