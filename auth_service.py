import bcrypt
from datetime import datetime, timedelta, date
from typing import Optional, Dict, List
from uuid import UUID
import re

from audit_service import AuditService
from user import User
from user_repository import UserRepository
from settings import PASSWORD_SALT, LOGIN_ATTEMPTS_LIMIT, LOGIN_BLOCK_DURATION_MINUTES, DAILY_BLOCK_LIMIT, PASSWORD_RESET_TOKEN_EXPIRATION_MINUTES

class AuthenticationError(Exception):
    pass

class AuthService:
    def __init__(self, user_repo: UserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service
        self.failed_login_attempts: Dict[UUID, List[datetime]] = {}
        self.blocked_users: Dict[UUID, datetime] = {}
        self.daily_blocks: Dict[UUID, List[datetime]] = {}  # RN-AU-04: registro de bloqueos diarios

    def hashear_contrasena(self, password: str) -> str:
        """RN-US-07: Hashea una contraseña usando bcrypt."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_password.decode('utf-8')

    def verificar_contrasena(self, password: str, hashed_password: str) -> bool:
        """Verifica una contraseña contra su hash."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

    def validar_contrasena(self, password: str) -> None:
        """RN-US-06: Valida la complejidad de la contraseña."""
        if len(password) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", password):
            raise ValueError("La contraseña debe contener al menos una letra mayúscula.")
        if not re.search(r"[0-9]", password):
            raise ValueError("La contraseña debe contener al menos un número.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("La contraseña debe contener al menos un carácter especial.")

    def autenticar(self, email: str, password: str, ip_address: Optional[str] = None) -> User:
        """RN-AU-01/02: Autentica un usuario y gestiona intentos fallidos."""
        user = self.user_repo.get_by_email(email)
        user_id = user.id if user else None

        # RN-AU-04: Verificar si requiere recuperación de contraseña
        if user_id and self._requiere_recuperacion(user_id):
            self.audit_service.registrar_login(user_id, False, ip_address)
            raise AuthenticationError(
                "Su cuenta ha sido bloqueada 3 veces hoy.\n"
                "Debe recuperar su contraseña para continuar.\n"
                "Use la opción '¿Olvidaste tu contraseña?' en el login."
            )

        # RN-AU-03: Verificar bloqueo temporal
        if user_id in self.blocked_users and self.blocked_users[user_id] > datetime.now():
            self.audit_service.registrar_login(user_id, False, ip_address)
            raise AuthenticationError(
                f"Cuenta bloqueada temporalmente hasta {self.blocked_users[user_id].strftime('%H:%M')}."
            )

        if not user or not self.verificar_contrasena(password, user.password_hash):
            self._registrar_intento_fallido(user_id)
            self.audit_service.registrar_login(user_id, False, ip_address)
            raise AuthenticationError("Credenciales inválidas.")

        if user.status == 'Inactivo':
            self.audit_service.registrar_login(user_id, False, ip_address)
            raise AuthenticationError("La cuenta está inactiva.")

        # Login exitoso — limpiar intentos
        if user_id in self.failed_login_attempts:
            del self.failed_login_attempts[user_id]
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]

        self.audit_service.registrar_login(user_id, True, ip_address)
        return user

    def _registrar_intento_fallido(self, user_id: Optional[UUID]) -> None:
        """RN-AU-03/04: Registra intento fallido, bloquea y cuenta bloqueos diarios."""
        if not user_id:
            return

        if user_id not in self.failed_login_attempts:
            self.failed_login_attempts[user_id] = []
        self.failed_login_attempts[user_id].append(datetime.now())

        # Mantener solo intentos recientes
        self.failed_login_attempts[user_id] = [
            t for t in self.failed_login_attempts[user_id]
            if t > datetime.now() - timedelta(minutes=LOGIN_BLOCK_DURATION_MINUTES)
        ]

        if len(self.failed_login_attempts[user_id]) >= LOGIN_ATTEMPTS_LIMIT:
            # Aplicar bloqueo temporal
            self.blocked_users[user_id] = datetime.now() + timedelta(minutes=LOGIN_BLOCK_DURATION_MINUTES)
            self.failed_login_attempts[user_id] = []

            # RN-AU-04: Registrar bloqueo diario
            if user_id not in self.daily_blocks:
                self.daily_blocks[user_id] = []

            # Limpiar bloqueos de días anteriores
            self.daily_blocks[user_id] = [
                t for t in self.daily_blocks[user_id]
                if t.date() == date.today()
            ]
            self.daily_blocks[user_id].append(datetime.now())

    def _requiere_recuperacion(self, user_id: UUID) -> bool:
        """RN-AU-04: Verifica si el usuario alcanzó 3 bloqueos diarios."""
        if user_id not in self.daily_blocks:
            return False
        bloqueos_hoy = [
            t for t in self.daily_blocks[user_id]
            if t.date() == date.today()
        ]
        return len(bloqueos_hoy) >= DAILY_BLOCK_LIMIT

    def limpiar_bloqueos_diarios(self, user_id: UUID) -> None:
        """Limpia los bloqueos diarios después de recuperar contraseña."""
        if user_id in self.daily_blocks:
            del self.daily_blocks[user_id]
        if user_id in self.blocked_users:
            del self.blocked_users[user_id]
        if user_id in self.failed_login_attempts:
            del self.failed_login_attempts[user_id]

    def validar_nueva_contrasena(self, user_id: UUID, new_password: str) -> None:
        """RN-AU-07: Valida que la nueva contraseña no sea igual a la anterior."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("Usuario no encontrado.")
        if self.verificar_contrasena(new_password, user.password_hash):
            raise ValueError("La nueva contraseña no puede ser igual a la anterior.")
        self.validar_contrasena(new_password)