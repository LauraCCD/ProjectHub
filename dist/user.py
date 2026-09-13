from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class User:
    id: Optional[UUID]
    name: str
    last_name: str
    email: str
    password_hash: str
    role: str # Administrador, Gestor, Colaborador
    status: str # Activo, Inactivo
    availability: int # 0-100%
    registered_at: datetime
    deleted_at: Optional[datetime]