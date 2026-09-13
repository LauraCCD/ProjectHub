from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from base_repository import BaseRepository
from category import Category

class CategoryRepository(BaseRepository[Category]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "categories")

    def _row_to_model(self, row: Dict[str, Any]) -> Category:
        return Category(
            id=UUID(row["id"]) if row["id"] else None,
            name=row["name"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Category) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "name": model.name,
            "deleted_at": model.deleted_at
        }

    def insert(self, category: Category) -> UUID:
        query = """
            INSERT INTO categories (name)
            VALUES (%s) RETURNING id;
        """
        return self._execute_insert(query, (category.name,))

    def update(self, category: Category) -> bool:
        query = """
            UPDATE categories SET name = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (category.name, str(category.id)))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_by_name(self, name: str) -> Optional[Category]:
        query = f"SELECT * FROM {self.table_name} WHERE name = %s AND deleted_at IS NULL;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (name,))
            row = cursor.fetchone()
            return self._row_to_model(row) if row else None