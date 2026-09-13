from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID

@dataclass
class ProjectUser:
    project_id: UUID
    user_id: UUID
    assigned_at: datetime