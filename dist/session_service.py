from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from user import User
from typing import Dict
from settings import SESSION_TIMEOUT_MINUTES

class SessionService:
    def __init__(self):
        self.active_sessions: Dict[UUID, datetime] = {} # {user_id: last_activity_timestamp}
        self.current_user: Optional[User] = None

    def start_session(self, user: User) -> None:
        self.current_user = user
        self.active_sessions[user.id] = datetime.now()

    def end_session(self) -> None:
        if self.current_user and self.current_user.id in self.active_sessions:
            del self.active_sessions[self.current_user.id]
        self.current_user = None

    def verificar_inactividad(self) -> bool:
        """RN-AU-05: Cierra sesión automáticamente si hay inactividad."""
        if self.current_user and self.current_user.id in self.active_sessions:
            last_activity = self.active_sessions[self.current_user.id]
            if datetime.now() > last_activity + timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                self.end_session()
                return True
        return False

    def update_activity(self) -> None:
        if self.current_user and self.current_user.id in self.active_sessions:
            self.active_sessions[self.current_user.id] = datetime.now()