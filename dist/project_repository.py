from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from base_repository import BaseRepository
from project import Project

class ProjectRepository(BaseRepository[Project]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "projects")

    def _row_to_model(self, row: Dict[str, Any]) -> Project:
        return Project(
            id=UUID(row["id"]) if row["id"] else None,
            name=row["name"],
            description=row["description"],
            status=row["status"],
            progress=row["progress"],
            priority=row["priority"],
            start_date=row["start_date"],
            end_date=row["end_date"],
            manager_id=UUID(row["manager_id"]),
            category_id=UUID(row["category_id"]) if row["category_id"] else None,
            budget=row.get("budget"),
            created_at=row["created_at"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Project) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "name": model.name,
            "description": model.description,
            "status": model.status,
            "progress": model.progress,
            "priority": model.priority,
            "start_date": model.start_date,
            "end_date": model.end_date,
            "manager_id": str(model.manager_id),
            "category_id": str(model.category_id) if model.category_id else None,
            "budget": model.budget,
            "created_at": model.created_at,
            "deleted_at": model.deleted_at
        }

    def insert(self, project: Project) -> UUID:
        query = """
            INSERT INTO projects (name, description, status, progress, priority, start_date, end_date, manager_id, category_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (
            project.name, project.description, project.status, project.progress, project.priority,
            project.start_date, project.end_date, str(project.manager_id), str(project.category_id) if project.category_id else None
        ))

    def update(self, project: Project) -> bool:
        query = """
            UPDATE projects SET name = %s, description = %s, status = %s, progress = %s,
            priority = %s, start_date = %s, end_date = %s, manager_id = %s, category_id = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                project.name, project.description, project.status, project.progress, project.priority,
                project.start_date, project.end_date, str(project.manager_id), str(project.category_id) if project.category_id else None, str(project.id)
            ))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_by_name(self, name: str) -> Optional[Project]:
        query = f"SELECT * FROM {self.table_name} WHERE name = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_all_active(self) -> List[Project]:
        query = f"SELECT * FROM {self.table_name} WHERE deleted_at IS NULL ORDER BY created_at DESC;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]