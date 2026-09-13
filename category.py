from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class Category:
    id: Optional[UUID]
    name: str
    deleted_at: Optional[datetime]