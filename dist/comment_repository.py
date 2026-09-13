from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime
from base_repository import BaseRepository
from comment import Comment

class CommentRepository(BaseRepository[Comment]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "comments")

    def _row_to_model(self, row: Dict[str, Any]) -> Comment:
        return Comment(
            id=UUID(row["id"]) if row["id"] else None,
            task_id=UUID(row["task_id"]),
            user_id=UUID(row["user_id"]),
            content=row["content"],
            created_at=row["created_at"],
            edited_at=row["edited_at"],
            deleted_at=row["deleted_at"]
        )

    def _model_to_dict(self, model: Comment) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "task_id": str(model.task_id),
            "user_id": str(model.user_id),
            "content": model.content,
            "created_at": model.created_at,
            "edited_at": model.edited_at,
            "deleted_at": model.deleted_at
        }

    def insert(self, comment: Comment) -> UUID:
        query = """
            INSERT INTO comments (task_id, user_id, content)
            VALUES (%s, %s, %s) RETURNING id;
        """
        return self._execute_insert(query, (str(comment.task_id), str(comment.user_id), comment.content))

    def update(self, comment: Comment) -> bool:
        query = """
            UPDATE comments SET content = %s, edited_at = %s
            WHERE id = %s AND deleted_at IS NULL;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (comment.content, datetime.now(), str(comment.id)))
            self.db.connection.commit()
            return cursor.rowcount > 0

    def get_comments_by_task(self, task_id: UUID) -> List[Comment]:
        query = "SELECT * FROM comments WHERE task_id = %s AND deleted_at IS NULL ORDER BY created_at ASC;"
        with self.db.get_cursor(dictionary=True) as cursor:
            cursor.execute(query, (str(task_id),))
            return [self._row_to_model(row) for row in cursor.fetchall()]