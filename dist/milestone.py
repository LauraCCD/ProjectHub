from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

@dataclass
class Milestone:
    id: Optional[UUID]
    name: str
    description: Optional[str]
    project_id: UUID
    scheduled_date: date # Fecha programada
    effective_completion_date: Optional[date] # Fecha de cumplimiento efectivo
    status: str # Pendiente, Cumplido, Vencido
    created_at: datetime
    deleted_at: Optional[datetime]