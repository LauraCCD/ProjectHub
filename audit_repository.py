import json
from typing import Any, Dict, List, Optional
from uuid import UUID
from datetime import datetime

from audit_log import AuditLog # Import the correct AuditLog model
from base_repository import BaseRepository

class AuditRepository(BaseRepository[AuditLog]):
    def __init__(self, db_connection):
        super().__init__(db_connection, "audit_logs")

    def _row_to_model(self, row: Dict[str, Any]) -> AuditLog:
        return AuditLog(
            id=UUID(row["id"]), # ID should always be present for a retrieved log
            user_id=UUID(row["user_id"]) if row["user_id"] else None,
            action=row["action"],
            entity_type=row["entity_type"],
            entity_id=UUID(row["entity_id"]) if row["entity_id"] else None,
            old_value=json.loads(row["old_value"]) if row["old_value"] else None, # Assuming JSON string in DB
            new_value=json.loads(row["new_value"]) if row["new_value"] else None, # Assuming JSON string in DB
            timestamp=row["timestamp"]
        )

    def _model_to_dict(self, model: AuditLog) -> Dict[str, Any]:
        return {
            "id": str(model.id) if model.id else None,
            "user_id": str(model.user_id) if model.user_id else None,
            "action": model.action,
            "entity_type": model.entity_type,
            "entity_id": str(model.entity_id) if model.entity_id else None,
            "old_value": json.dumps(model.old_value) if model.old_value else None, # Convert dict to JSON string
            "new_value": json.dumps(model.new_value) if model.new_value else None, # Convert dict to JSON string
            "timestamp": model.timestamp,
        }

    def insert(self, audit_log: AuditLog) -> int:
        query = """
         INSERT INTO audit_logs (user_id, action, entity_type, entity_id, old_value, new_value, timestamp)
         VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                str(audit_log.user_id) if audit_log.user_id else None,
                audit_log.action,
                audit_log.entity_type,
                str(audit_log.entity_id) if audit_log.entity_id else None,
                json.dumps(audit_log.old_value) if audit_log.old_value else None,
                json.dumps(audit_log.new_value) if audit_log.new_value else None,
                audit_log.timestamp
            ))
            new_id = cursor.fetchone()[0]
            self.db.connection.commit()
            return new_id  # Retorna int, no UUID