from dataclasses import dataclass
from datetime import date, datetime
from typing import Optional
from uuid import UUID

@dataclass
class Project:
    id: Optional[UUID]
    name: str
    description: Optional[str]
    status: str # Planificado, En Curso, Finalizado, Cancelado
    progress: int
    priority: str # Alta, Media, Baja
    start_date: date
    end_date: Optional[date]
    manager_id: UUID
    category_id: Optional[UUID]
    budget: Optional[float] # Nuevo campo
    created_at: datetime
    deleted_at: Optional[datetime]