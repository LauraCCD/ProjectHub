import re
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from user import User
from user_repository import UserRepository
from task_repository import TaskRepository
from auth_service import AuthService

class UserService:
    def __init__(self, user_repo: UserRepository, task_repo: TaskRepository, auth_service: AuthService):
        self.user_repo = user_repo
        self.task_repo = task_repo
        self.auth_service = auth_service

    def validar_nombre(self, name: str, last_name: str) -> None:
        if not name or len(name.strip()) < 2:
            raise ValueError("El nombre es obligatorio y debe tener al menos 2 caracteres.")
        if not last_name or len(last_name.strip()) < 2:
            raise ValueError("El apellido es obligatorio y debe tener al menos 2 caracteres.")

    def validar_correo(self, email: str, user_id: Optional[UUID] = None) -> None:
        if not email or not email.strip():
            raise ValueError("El correo electrónico es obligatorio.")
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            raise ValueError("Formato de correo electrónico inválido.")
        existing_user = self.user_repo.get_by_email(email.strip())
        if existing_user and (user_id is None or existing_user.id != user_id):
            raise ValueError(f"Ya existe un usuario con el correo '{email}'.")

    def validar_rol(self, role: str) -> None:
        if role not in ["Administrador", "Gestor", "Colaborador"]:
            raise ValueError("Rol inválido. Debe ser 'Administrador', 'Gestor' o 'Colaborador'.")

    def verificar_estado_activo(self, user: User) -> None:
        if user.status == 'Inactivo':
            raise PermissionError("El usuario está inactivo y no puede realizar esta operación.")

    def proteger_ultimo_admin(self, user_id: UUID) -> None:
        user_to_deactivate = self.user_repo.get_by_id(user_id)
        if user_to_deactivate and user_to_deactivate.role == 'Administrador' and user_to_deactivate.status == 'Activo':
            active_admins_count = self.user_repo.count_active_admins()
            if active_admins_count <= 1:
                raise PermissionError("No se puede desactivar al último administrador activo del sistema.")

    def verificar_tareas_antes_desactivar(self, user_id: UUID) -> None:
        active_tasks_count = self.task_repo.count_active_tasks_for_user(user_id)
        if active_tasks_count > 0:
            raise ValueError(f"El usuario tiene {active_tasks_count} tareas activas asignadas. Reasigne las tareas antes de desactivar al usuario.")

    def create_user(self, name: str, last_name: str, email: str, password: str, role: str, availability: int = 100) -> User:
        self.validar_nombre(name, last_name)
        self.validar_correo(email)
        self.auth_service.validar_contrasena(password)
        self.validar_rol(role)

        password_hash = self.auth_service.hashear_contrasena(password)
        new_user = User(
            id=None,
            name=name.strip(),
            last_name=last_name.strip(),
            email=email.strip(),
            password_hash=password_hash,
            role=role,
            status="Activo",
            availability=availability,
            registered_at=datetime.now(),
            deleted_at=None
        )
        new_user.id = self.user_repo.insert(new_user)
        return new_user