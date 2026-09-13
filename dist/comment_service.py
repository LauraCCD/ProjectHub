from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

from comment import Comment
from user import User
from comment_repository import CommentRepository
from task_repository import TaskRepository
from project_user_repository import ProjectUserRepository
from permission_service import PermissionService

class CommentService:
    def __init__(self, comment_repo: CommentRepository, task_repo: TaskRepository, project_user_repo: ProjectUserRepository, permission_service: PermissionService):
        self.comment_repo = comment_repo
        self.task_repo = task_repo
        self.project_user_repo = project_user_repo
        self.permission_service = permission_service

    def validar_participante(self, task_id: UUID, user_id: UUID) -> None:
        """RN-CO-01/02/03: Verifica que la tarea exista y el usuario sea participante del proyecto."""
        task = self.task_repo.get_by_id(task_id)
        if not task:
            raise ValueError(f"La tarea con ID {task_id} no existe.")
        project_users = self.project_user_repo.get_users_by_project(task.project_id)
        if not any(pu.user_id == user_id for pu in project_users):
            raise PermissionError("El usuario no es participante de este proyecto y no puede comentar.")

    def add_comment(self, task_id: UUID, user_id: UUID, content: str) -> Comment:
        self.validar_participante(task_id, user_id)
        if not content.strip():
            raise ValueError("El contenido del comentario no puede estar vacío.")
        new_comment = Comment(id=None, task_id=task_id, user_id=user_id, content=content.strip(),
                              created_at=datetime.now(), edited_at=None, deleted_at=None)
        new_comment.id = self.comment_repo.insert(new_comment)
        return new_comment

    def update_comment(self, comment_id: UUID, new_content: str, current_user: User) -> Comment:
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Comentario no encontrado.")
        if comment.user_id != current_user.id:
            raise PermissionError("Solo el autor puede editar su comentario.")
        self.verificar_ventana_edicion(comment)
        comment.content = new_content.strip()
        self.comment_repo.update(comment)
        return comment

    def delete_comment(self, comment_id: UUID, current_user: User) -> None:
        """RN-CO-06: Solo el autor puede eliminar dentro de 15 min. Admin puede eliminar siempre."""
        comment = self.comment_repo.get_by_id(comment_id)
        if not comment:
            raise ValueError("Comentario no encontrado.")

        if current_user.role == "Administrador":
            self.comment_repo.soft_delete(comment_id)
            return

        if comment.user_id != current_user.id:
            raise PermissionError("Solo el autor o un administrador puede eliminar este comentario.")

        if datetime.now() > comment.created_at + timedelta(minutes=15):
            raise PermissionError("El tiempo para eliminar este comentario ha expirado. Contacte a un administrador.")

        self.comment_repo.soft_delete(comment_id)

    def verificar_ventana_edicion(self, comment: Comment) -> None:
        """RN-CO-05: Permite edición solo 15 minutos después de publicar."""
        if datetime.now() > comment.created_at + timedelta(minutes=15):
            raise PermissionError("El tiempo para editar este comentario ha expirado (15 minutos).")