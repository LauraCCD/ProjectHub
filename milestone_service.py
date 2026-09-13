from datetime import date, datetime
from typing import List, Optional
from uuid import UUID

from milestone import Milestone
from project import Project
from milestone_repository import MilestoneRepository
from project_repository import ProjectRepository

class MilestoneService:
    def __init__(self, milestone_repo: MilestoneRepository, project_repo: ProjectRepository):
        self.milestone_repo = milestone_repo
        self.project_repo = project_repo

    def validar_proyecto(self, project_id: UUID) -> Project:
        """RN-HI-01/02: Verifica que el proyecto exista y esté activo."""
        project = self.project_repo.get_by_id(project_id)
        if not project:
            raise ValueError(f"El proyecto con ID {project_id} no existe.")
        if project.status in ["Finalizado", "Cancelado"]:
            raise ValueError("No se pueden añadir hitos a proyectos finalizados o cancelados.")
        return project

    def validar_fechas_hito(self, scheduled_date: date, project_start_date: date, effective_completion_date: Optional[date]) -> None:
        """RN-HI-03/04: Fecha programada obligatoria y posterior a la fecha inicio del proyecto.
           RN-HI-XX: Fecha de cumplimiento efectivo no puede ser anterior a la programada."""
        if not scheduled_date:
            raise ValueError("La fecha programada del hito es obligatoria.")
        if scheduled_date <= project_start_date:
            raise ValueError("La fecha programada del hito debe ser posterior a la fecha de inicio del proyecto.")
        if effective_completion_date and effective_completion_date < scheduled_date:
            raise ValueError("La fecha de cumplimiento efectivo no puede ser anterior a la fecha programada.")

    def validar_nombre_hito(self, name: str) -> None:
        if not name or not name.strip():
            raise ValueError("El nombre del hito no puede estar vacío.")
        if len(name.strip()) < 5:
            raise ValueError("El nombre del hito debe tener al menos 5 caracteres.")

    def create_milestone(self, name: str, description: Optional[str], project_id: UUID, scheduled_date: date) -> Milestone:
        """Crea un nuevo hito aplicando las reglas de negocio."""
        project = self.validar_proyecto(project_id)
        self.validar_nombre_hito(name)
        self.validar_fechas_hito(scheduled_date, project.start_date, None)

        new_milestone = Milestone(
            id=None,
            name=name.strip(),
            description=description.strip() if description else None,
            project_id=project_id,
            scheduled_date=scheduled_date,
            effective_completion_date=None,
            status="Pendiente",
            created_at=datetime.now(),
            deleted_at=None
        )
        new_milestone.id = self.milestone_repo.insert(new_milestone)
        return new_milestone

    def update_milestone(self, milestone_id: UUID, name: str, description: Optional[str], scheduled_date: date, effective_completion_date: Optional[date], status: str) -> Milestone:
        """Actualiza un hito existente aplicando las reglas de negocio."""
        milestone = self.milestone_repo.get_by_id(milestone_id)
        if not milestone:
            raise ValueError("Hito no encontrado.")

        project = self.validar_proyecto(milestone.project_id) # Re-validar proyecto
        self.validar_nombre_hito(name)
        self.validar_fechas_hito(scheduled_date, project.start_date, effective_completion_date)
        
        if status not in ["Pendiente", "Cumplido", "Vencido"]:
            raise ValueError("Estado de hito inválido. Debe ser 'Pendiente', 'Cumplido' o 'Vencido'.")
        if status == "Cumplido" and not effective_completion_date:
            raise ValueError("Un hito 'Cumplido' debe tener una fecha de cumplimiento efectivo.")
        if status != "Cumplido" and effective_completion_date:
            raise ValueError("Solo los hitos 'Cumplidos' pueden tener una fecha de cumplimiento efectivo.")
        
        milestone.name = name.strip()
        milestone.description = description.strip() if description else None
        milestone.scheduled_date = scheduled_date
        milestone.effective_completion_date = effective_completion_date
        milestone.status = status
        self.milestone_repo.update(milestone)
        return milestone

    def verificar_vencimiento(self, milestone: Milestone) -> None:
        """RN-HI-05/06: Lógica para marcar hito como 'Vencido' automáticamente."""
        if milestone.status == "Pendiente" and milestone.scheduled_date < date.today():
            # Directamente actualizar el estado a Vencido si no hay una función específica para ello
            milestone.status = "Vencido"
            self.milestone_repo.update(milestone)