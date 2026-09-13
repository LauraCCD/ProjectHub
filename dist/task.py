from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

@dataclass
class Task:
    id: Optional[UUID]
    title: str
    description: Optional[str]
    project_id: UUID
    assignee_id: UUID
    status: str # Pendiente, En Progreso, Completada, Vencida
    priority: str # Alta, Media, Baja
    due_date: date
    progress: int
    created_at: datetime
    deleted_at: Optional[datetime]