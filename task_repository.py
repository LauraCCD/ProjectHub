from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from base_repository import BaseRepository
from task import Task

class TaskRepository(BaseRepository[Task]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "tasks")

    def _row_to_model(self, row: Dict[str, Any]) -> Task:
        return Task(
            id=UUID(row["id"]) if row["id"] else None,
            title=row["title"],
            description=row["description"],
            project_id=UUID(row["project_id"]),
            assignee_id=UUID(row["assignee_id"]),
            status=row["status"],
            priority=row["priority"],
            due_date=row["due_date"],
            progress=row["progress"],
            created_at=row["created_at"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Task) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "title": model.title,
            "description": model.description,
            "project_id": str(model.project_id),
            "assignee_id": str(model.assignee_id),
            "status": model.status,
            "priority": model.priority,
            "due_date": model.due_date,
            "progress": model.progress,
            "created_at": model.created_at,
            "deleted_at": model.deleted_at
        }

    def insert(self, task: Task) -> UUID:
        query = """
            INSERT INTO tasks (title, description, project_id, assignee_id, status, priority, due_date, progress)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (
            task.title, task.description, str(task.project_id), str(task.assignee_id),
            task.status, task.priority, task.due_date, task.progress
        ))

    def update(self, task: Task) -> bool:
        query = """
            UPDATE tasks SET title = %s, description = %s, project_id = %s, assignee_id = %s,
            status = %s, priority = %s, due_date = %s, progress = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                task.title, task.description, str(task.project_id), str(task.assignee_id),
                task.status, task.priority, task.due_date, task.progress, str(task.id)
            ))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_tasks_by_project(self, project_id: UUID) -> List[Task]:
        query = "SELECT * FROM tasks WHERE project_id = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(project_id),))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_tasks_by_assignee(self, assignee_id: UUID) -> List[Task]:
        query = "SELECT * FROM tasks WHERE assignee_id = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(assignee_id),))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def list_ordered(self, project_id: Optional[UUID] = None) -> List[Task]:
        """RN-TA-14: Ordenamiento: primero por prioridad, luego por fecha límite."""
        sql_filter = "WHERE deleted_at IS NULL"
        params: List[Any] = []
        if project_id:
            sql_filter += " AND project_id = %s"
            params.append(str(project_id))

        query = f"""
            SELECT * FROM tasks
            {sql_filter}
            ORDER BY
                CASE priority
                    WHEN 'Alta' THEN 1
                    WHEN 'Media' THEN 2
                    WHEN 'Baja' THEN 3
                    ELSE 4
                END,
                due_date ASC;
        """
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def count_active_tasks_for_project(self, project_id: UUID) -> int:
        query = "SELECT COUNT(*) FROM tasks WHERE project_id = %s AND status NOT IN ('Completada', 'Cancelada') AND deleted_at IS NULL;"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (str(project_id),))
            return cursor.fetchone()[0]

    def count_active_tasks_for_user(self, user_id: UUID) -> int:
        query = "SELECT COUNT(*) FROM tasks WHERE assignee_id = %s AND status NOT IN ('Completada', 'Cancelada') AND deleted_at IS NULL;"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (str(user_id),))
            return cursor.fetchone()[0]