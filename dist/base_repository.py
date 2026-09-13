from typing import TypeVar, Generic, List, Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime

from db_connection import DBConnection

# Define a type variable for the model
T = TypeVar('T')

class BaseRepository(Generic[T]):
    def __init__(self, db_connection: DBConnection, table_name: str):
        self.db = db_connection
        self.table_name = table_name

    def _row_to_model(self, row: Dict[str, Any]) -> T:
        """Converts a database row (dictionary) to a model instance."""
        raise NotImplementedError

    def _model_to_dict(self, model: T) -> Dict[str, Any]:
        """Converts a model instance to a dictionary for database insertion/update."""
        raise NotImplementedError

    def _execute_insert(self, query: str, params: tuple) -> UUID:
        """Executes an INSERT query and returns the UUID of the newly created record."""
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            new_id = cursor.fetchone()[0]
            self.db.connection.commit()
            return UUID(str(new_id))

    def get_by_id(self, id: UUID) -> Optional[T]:
        """Retrieves a single record by its ID."""
        query = f"SELECT * FROM {self.table_name} WHERE id = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(id),))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None

    def get_all(self) -> List[T]:
        """Retrieves all active records."""
        query = f"SELECT * FROM {self.table_name} WHERE deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_model(row) for row in rows]

    def soft_delete(self, id: UUID) -> bool:
        """Marks a record as deleted (soft delete)."""
        query = f"UPDATE {self.table_name} SET deleted_at = %s WHERE id = %s;"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (datetime.now(), str(id)))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def hard_delete(self, id: UUID) -> bool:
        """Permanently deletes a record by its ID."""
        query = f"DELETE FROM {self.table_name} WHERE id = %s;"
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (str(id),))
            self.db.connection.commit()
            return cursor.rowcount > 0

    # Additional methods like `find_by_criteria`, `count`, etc., can be added here