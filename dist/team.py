from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Team:
    id: Optional[UUID]
    name: str
    description: Optional[str]
    created_at: datetime
    status: str # Activo, Inactivo
    deleted_at: Optional[datetime]