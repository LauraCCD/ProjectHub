from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from base_repository import BaseRepository
from user import User

class UserRepository(BaseRepository[User]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "users")

    def _row_to_model(self, row: Dict[str, Any]) -> User:
        return User(
            id=row["id"] if isinstance(row["id"], UUID) else UUID(str(row["id"])) if row["id"] else None,
            name=str(row["name"]),
            last_name=str(row["last_name"]),
            email=str(row["email"]),
            password_hash=str(row["password_hash"]),
            role=str(row["role"]),
            status=str(row["status"]),
            availability=int(row["availability"]),
            registered_at=row["registered_at"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: User) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "name": model.name,
            "last_name": model.last_name,
            "email": model.email,
            "password_hash": model.password_hash,
            "role": model.role,
            "status": model.status,
            "availability": model.availability,
            "registered_at": model.registered_at,
            "deleted_at": model.deleted_at
        }

    def insert(self, user: User) -> UUID:
        query = """
            INSERT INTO users (name, last_name, email, password_hash, role, status, availability)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (
            user.name, user.last_name, user.email, user.password_hash, user.role, user.status, user.availability
        ))

    def update(self, user: User) -> bool:
        query = """
            UPDATE users SET name = %s, last_name = %s, email = %s, password_hash = %s,
            role = %s, status = %s, availability = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                user.name, user.last_name, user.email, user.password_hash, user.role, user.status,
                user.availability, str(user.id)
            ))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_by_email(self, email: str) -> Optional[User]:
        query = f"SELECT * FROM {self.table_name} WHERE email = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (email,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def count_active_admins(self) -> int:
        query = "SELECT COUNT(*) FROM users WHERE role = 'Administrador' AND status = 'Activo' AND deleted_at IS NULL;"
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchone()[0]