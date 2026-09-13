from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class AuditLog:
    id: Optional[UUID]
    user_id: Optional[UUID]
    action: str
    entity_type: str
    entity_id: Optional[UUID]
    old_value: Optional[dict]
    new_value: Optional[dict]
    timestamp: datetime