from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from uuid import UUID
from task import Task
from milestone import Milestone
from task_repository import TaskRepository
from milestone_repository import MilestoneRepository

class NotificationService:
    def __init__(self, task_repo: TaskRepository, milestone_repo: MilestoneRepository):
        self.task_repo = task_repo
        self.milestone_repo = milestone_repo
        self._notifications: List[Dict[str, Any]] = []

    def notificar_tarea_proxima(self) -> List[Task]:
        """RN-NT-01: Identifica tareas que vencen en las próximas 48h."""
        upcoming_tasks: List[Task] = []
        all_tasks = self.task_repo.get_all()
        for task in all_tasks:
            if task.status not in ["Completada", "Cancelada"] and \
               date.today() <= task.due_date <= (date.today() + timedelta(days=2)):
                upcoming_tasks.append(task)
        return upcoming_tasks

    def notificar_hito_proximo(self) -> List[Milestone]:
        """RN-NT-02: Identifica hitos que vencen en las próximas 72h."""
        upcoming_milestones: List[Milestone] = []
        all_milestones = self.milestone_repo.get_all()
        for milestone in all_milestones:
            if milestone.status == "Pendiente" and \
               date.today() <= milestone.scheduled_date <= (date.today() + timedelta(days=3)):
                upcoming_milestones.append(milestone)
        return upcoming_milestones

    def notificar_cambio_estado(self, entity_type: str, entity_name: str, old_status: str, new_status: str, user_name: str) -> None:
        """RN-NT-03: Notifica cambios críticos de estado."""
        self._notifications.append({
            "tipo": "cambio_estado",
            "mensaje": f"{entity_type} '{entity_name}' cambió de '{old_status}' a '{new_status}' por {user_name}.",
            "timestamp": datetime.now()
        })

    def notificar_asignacion_tarea(self, task_title: str, assignee_name: str) -> None:
        """RN-NT-04: Notifica al usuario cuando se le asigna una tarea."""
        self._notifications.append({
            "tipo": "asignacion",
            "mensaje": f"Se te asignó la tarea '{task_title}' a {assignee_name}.",
            "timestamp": datetime.now()
        })

    def notificar_cancelacion_proyecto(self, project_name: str, user_name: str) -> None:
        """RN-NT-05: Notifica la cancelación de un proyecto."""
        self._notifications.append({
            "tipo": "cancelacion",
            "mensaje": f"El proyecto '{project_name}' fue cancelado por {user_name}.",
            "timestamp": datetime.now()
        })

    def get_all_notifications(self) -> List[Dict[str, Any]]:
        """Retorna todas las notificaciones pendientes."""
        return self._notifications.copy()

    def get_pending_alerts(self) -> List[str]:
        """Retorna alertas combinadas de tareas próximas, hitos próximos y notificaciones."""
        alerts = []

        # Tareas próximas a vencer
        for task in self.notificar_tarea_proxima():
            alerts.append(f"⚠ Tarea '{task.title}' vence el {task.due_date}")

        # Hitos próximos a vencer
        for milestone in self.notificar_hito_proximo():
            alerts.append(f"🏁 Hito '{milestone.name}' vence el {milestone.scheduled_date}")

        # Notificaciones de cambios
        for notif in self._notifications:
            alerts.append(f"🔔 {notif['mensaje']}")

        return alerts

    def limpiar_notificaciones(self) -> None:
        """Limpia las notificaciones después de mostrarlas."""
        self._notifications.clear()