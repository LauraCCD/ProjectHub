from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from base_repository import BaseRepository
from project_user import ProjectUser

class ProjectUserRepository(BaseRepository[ProjectUser]):
    def __init__(self, db_connection):
        # The 'project_users' table is a join table and typically does not have a single 'id' column
        # or 'deleted_at' for soft deletion in the same way as other entity tables.
        # Therefore, methods like get_by_id, soft_delete, hard_delete from BaseRepository are not directly applicable
        # and should not be used for this repository without specific overrides.
        super().__init__(db_connection, "project_users")

    def _row_to_model(self, row: Dict[str, Any]) -> ProjectUser:
        return ProjectUser(
            project_id=UUID(row["project_id"]),
            user_id=UUID(row["user_id"]),
            assigned_at=row["assigned_at"]
        )

    def _model_to_dict(self, model: ProjectUser) -> Dict[str, Any]:
        return {
            "project_id": str(model.project_id),
            "user_id": str(model.user_id),
            "assigned_at": model.assigned_at
        }

    def assign_user_to_project(self, project_id: UUID, user_id: UUID) -> bool:
        query = """
            INSERT INTO project_users (project_id, user_id)
            VALUES (%s, %s) ON CONFLICT (project_id, user_id) DO NOTHING;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (str(project_id), str(user_id)))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_users_by_project(self, project_id: UUID) -> List[ProjectUser]:
        query = "SELECT * FROM project_users WHERE project_id = %s;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(project_id),))
            return [self._row_to_model(row) for row in cursor.fetchall()]