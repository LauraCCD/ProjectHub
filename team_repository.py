from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from base_repository import BaseRepository
from team import Team

class TeamRepository(BaseRepository[Team]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "teams")

    def _row_to_model(self, row: Dict[str, Any]) -> Team:
        return Team(
            id=UUID(row["id"]) if row["id"] else None,
            name=row["name"],
            description=row["description"],
            created_at=row["created_at"],
            status=row["status"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Team) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "name": model.name,
            "description": model.description,
            "created_at": model.created_at,
            "status": model.status,
            "deleted_at": model.deleted_at
        }

    def insert(self, team: Team) -> UUID:
        query = """
            INSERT INTO teams (name, description, status)
            VALUES (%s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (team.name, team.description, team.status))

    def update(self, team: Team) -> bool:
        query = """
            UPDATE teams SET name = %s, description = %s, status = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                team.name, team.description, team.status, str(team.id)
            ))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_by_name(self, name: str) -> Optional[Team]:
        query = f"SELECT * FROM {self.table_name} WHERE name = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_teams_by_user(self, user_id: UUID) -> List[Team]:
        # This would require a many-to-many table (e.g., team_members)
        # For now, returning an empty list as this table is not defined.
        # If implemented, the query would join teams and team_members.
        # query = "SELECT t.* FROM teams t JOIN team_members tm ON t.id = tm.team_id WHERE tm.user_id = %s AND t.deleted_at IS NULL;"
        # with self.db.get_cursor(dictionary=True) as cursor:
        #     cursor.execute(query, (str(user_id),))
        #     return [self._row_to_model(row) for row in cursor.fetchall()]
        return []