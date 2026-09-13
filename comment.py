from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Comment:
    id: Optional[UUID]
    task_id: UUID
    user_id: UUID
    content: str
    created_at: datetime
    edited_at: Optional[datetime]
    deleted_at: Optional[datetime]