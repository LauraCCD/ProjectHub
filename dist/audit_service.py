from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID

from audit_log import AuditLog
from audit_repository import AuditRepository

class AuditService:
    def __init__(self, audit_repo: AuditRepository):
        self.audit_repo = audit_repo

    def registrar_accion(self,
                         user_id: Optional[UUID],
                         action: str,
                         entity_type: str,
                         entity_id: Optional[UUID] = None,
                         old_value: Optional[Dict[str, Any]] = None,
                         new_value: Optional[Dict[str, Any]] = None) -> None:
        """RN-AD-01, RN-AD-03: Registra una acción en el log de auditoría."""
        audit_log = AuditLog(
            id=None,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            timestamp=datetime.now()
        )
        self.audit_repo.insert(audit_log) # Calls the generic insert method in AuditRepository

    def registrar_login(self, user_id: Optional[UUID], success: bool, ip_address: Optional[str]) -> None:
        """RN-AU-08: Registra un intento de login."""
        action = "Login Exitoso" if success else "Login Fallido"
        self.registrar_accion(user_id, action, "Autenticacion", None, {"ip_address": ip_address}, {"success": success})

    def registrar_cambio_avance(self, user_id: UUID, task_id: UUID, old_progress: int, new_progress: int) -> None:
        """RN-TA-13: Registra el cambio de avance de una tarea."""
        self.registrar_accion(user_id, "Cambio de Avance", "Tarea", task_id, {"progress": old_progress}, {"progress": new_progress})

    def registrar_eliminacion(self, user_id: UUID, entity_type: str, entity_id: UUID) -> None:
        """RN-EL-04: Registra la eliminación lógica de una entidad."""
        self.registrar_accion(user_id, "Eliminación Lógica", entity_type, entity_id, None, {"deleted_at": datetime.now()})