import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, List
from uuid import UUID

from user import User
from user_service import UserService
from session_service import SessionService
from permission_service import PermissionService
if TYPE_CHECKING: # Corrected import for type hinting
    from main_controller import MainController

class ResourceController:
    def __init__(self, main_controller: 'MainController', user_service: UserService, session_service: SessionService, permission_service: PermissionService):
        self.main_controller = main_controller # Reference to the main controller
        self.user_service = user_service
        self.session_service = session_service
        self.permission_service = permission_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def get_all_resources(self) -> List[User]:
        current_user = self.session_service.current_user
        if not current_user:
            return [] # Or raise error
        
        # In a real scenario, you might filter resources based on user's permissions
        # For now, assuming all active users are "resources" for display purposes
        all_users = self.user_service.user_repo.get_all()
        return [u for u in all_users if u.status == 'Activo']