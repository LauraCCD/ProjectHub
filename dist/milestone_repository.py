from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime, date
from base_repository import BaseRepository
from milestone import Milestone

class MilestoneRepository(BaseRepository[Milestone]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "milestones")

    def _row_to_model(self, row: Dict[str, Any]) -> Milestone:
        return Milestone(
            id=UUID(row["id"]) if row["id"] else None,
            name=row["name"],
            description=row["description"],
            project_id=UUID(row["project_id"]),
            scheduled_date=row["scheduled_date"],
            effective_completion_date=row["effective_completion_date"],
            status=row["status"],
            created_at=row["created_at"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Milestone) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "name": model.name,
            "description": model.description,
            "project_id": str(model.project_id),
            "due_date": model.scheduled_date,
            "scheduled_date": model.scheduled_date,
            "effective_completion_date": model.effective_completion_date,
            "status": model.status,
            "created_at": model.created_at,
            "deleted_at": model.deleted_at
        }

    def insert(self, milestone: Milestone) -> UUID:
        query = """
            INSERT INTO milestones (name, description, project_id, due_date, scheduled_date, status)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (
            milestone.name, milestone.description, str(milestone.project_id),
            milestone.scheduled_date, milestone.scheduled_date, milestone.status
        ))

    def update(self, milestone: Milestone) -> bool:
        query = """
            UPDATE milestones SET name = %s, description = %s, due_date = %s, scheduled_date = %s, 
            effective_completion_date = %s, status = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                milestone.name, milestone.description, milestone.scheduled_date,
                milestone.scheduled_date, milestone.effective_completion_date,
                milestone.status, str(milestone.id)
            ))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def list_chronological_by_project(self, project_id: UUID) -> List[Milestone]:
        query = "SELECT * FROM milestones WHERE project_id = %s AND deleted_at IS NULL ORDER BY scheduled_date ASC;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(project_id),))
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def get_by_project(self, project_id: UUID) -> List[Milestone]:
        return self.list_chronological_by_project(project_id)