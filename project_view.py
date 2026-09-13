import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime, date
from typing import TYPE_CHECKING, List, Optional
from uuid import UUID

from project import Project
from user import User
from category import Category

if TYPE_CHECKING:
    from main_controller import MainController
    from project_service import ProjectService
    from category_service import CategoryService
    from user_service import UserService
    from project_controller import ProjectController
    from milestone_controller import MilestoneController

class ProjectView(ctk.CTkFrame):
    def __init__(self, parent_frame, controller, project_service, category_service, user_service, project_controller, milestone_controller=None):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.project_service = project_service
        self.category_service = category_service
        self.user_service = user_service
        self.project_controller = project_controller
        self.milestone_controller = milestone_controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Gestión de Proyectos", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkButton(header, text="+ Nuevo Proyecto", font=ctk.CTkFont(size=13), fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=10, height=40, command=self.show_new_project_dialog).pack(side="right")

        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))
        ctk.CTkLabel(filter_frame, text="Filtrar por:", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="left")
        self.status_filter = ctk.CTkComboBox(
            filter_frame,
            values=["Todos", "Planificado", "En Curso", "Finalizado", "Cancelado"],
            width=150, height=35, corner_radius=8,
            command=lambda _: self.load_data()
        )
        self.status_filter.pack(side="left", padx=10)
        self.status_filter.set("Todos")

        self.projects_scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.projects_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)

    def load_data(self) -> None:
        for widget in self.projects_scroll_frame.winfo_children():
            widget.destroy()

        current_user = self.controller.session_service.current_user
        if not current_user:
            return

        filter_status = self.status_filter.get()
        all_projects = self.project_service.project_repo.get_all()

        filtered_projects = []
        for project in all_projects:
            if self.controller.permission_service.can_view_project(current_user, project.id):
                if filter_status == "Todos" or project.status == filter_status:
                    filtered_projects.append(project)

        if not filtered_projects:
            ctk.CTkLabel(self.projects_scroll_frame, text="No hay proyectos para mostrar.", font=ctk.CTkFont(size=14), text_color="#a0a0a0").pack(pady=30)
            return

        for project in filtered_projects:
            self._create_project_card(self.projects_scroll_frame, project)

    def _create_project_card(self, parent, project) -> None:
        card = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=15, height=160)
        card.pack(fill="x", pady=8)
        card.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")
        ctk.CTkLabel(top_row, text=project.name, font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(side="left")

        badges_frame = ctk.CTkFrame(top_row, fg_color="transparent")
        badges_frame.pack(side="right")

        priority_colors = {"Alta": "#e74c3c", "Media": "#f39c12", "Baja": "#3498db"}
        ctk.CTkLabel(badges_frame, text=project.priority, font=ctk.CTkFont(size=11), fg_color=priority_colors.get(project.priority, "#6c757d"), text_color="#ffffff", corner_radius=5, width=60, height=24).pack(side="left", padx=5)

        status_colors = {"En Curso": "#f39c12", "Finalizado": "#4ecca3", "Planificado": "#3498db", "Cancelado": "#6c757d"}
        ctk.CTkLabel(badges_frame, text=project.status, font=ctk.CTkFont(size=11), fg_color=status_colors.get(project.status, "#a0a0a0"), text_color="#ffffff", corner_radius=5, width=90, height=24).pack(side="left")

        dates_row = ctk.CTkFrame(content, fg_color="transparent")
        dates_row.pack(fill="x", pady=8)
        ctk.CTkLabel(dates_row, text=f"Inicio: {project.start_date}", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="left")
        ctk.CTkLabel(dates_row, text=f"Fin: {project.end_date if project.end_date else 'N/A'}", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="left", padx=20)

        manager = self.user_service.user_repo.get_by_id(project.manager_id)
        manager_name = f"{manager.name} {manager.last_name}" if manager else "Desconocido"
        ctk.CTkLabel(dates_row, text=f"Gestor: {manager_name}", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="right")

        try:
            category = self.project_service.category_repo.get_by_id(project.category_id) if hasattr(self.project_service, 'category_repo') else None
            category_name = category.name if category else ""
        except Exception:
            category_name = ""

        if category_name:
            ctk.CTkLabel(dates_row, text=f"Categoría: {category_name}", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="right", padx=10)

        progress_row = ctk.CTkFrame(content, fg_color="transparent")
        progress_row.pack(fill="x", pady=(4, 0))
        ctk.CTkLabel(progress_row, text="Progreso:", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(side="left")
        progress_bar = ctk.CTkProgressBar(progress_row, height=12, corner_radius=6, width=350)
        progress_bar.pack(side="left", padx=10)
        progress_bar.set(project.progress / 100)
        ctk.CTkLabel(progress_row, text=f"{project.progress}%", font=ctk.CTkFont(size=13, weight="bold"), text_color="#4ecca3").pack(side="left")

        actions_frame = ctk.CTkFrame(progress_row, fg_color="transparent")
        actions_frame.pack(side="right")
        ctk.CTkButton(actions_frame, text="Ver", width=60, height=30, fg_color="#2d4263", hover_color="#3d5273", corner_radius=8,
                      command=lambda p=project: self._show_project_detail(p)).pack(side="left", padx=3)
        ctk.CTkButton(actions_frame, text="Editar", width=60, height=30, fg_color="#3498db", hover_color="#2980b9", corner_radius=8,
                      command=lambda p=project: self._show_edit_project_dialog(p)).pack(side="left", padx=3)
        if self.milestone_controller:
            ctk.CTkButton(actions_frame, text="Hitos", width=60, height=30, fg_color="#8e44ad", hover_color="#7d3c98", corner_radius=8,
                          command=lambda p=project: self._show_milestones_dialog(p)).pack(side="left", padx=3)

    def _show_project_detail(self, project) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Detalle: {project.name}")
        dialog.geometry("500x450")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=project.name, font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 15))

        manager = self.user_service.user_repo.get_by_id(project.manager_id)
        manager_name = f"{manager.name} {manager.last_name}" if manager else "Desconocido"

        try:
            category = self.project_service.category_repo.get_by_id(project.category_id) if hasattr(self.project_service, 'category_repo') else None
            category_name = category.name if category else "Sin categoría"
        except Exception:
            category_name = "Sin categoría"

        fields = [
            ("Descripción", project.description or "Sin descripción"),
            ("Estado", project.status),
            ("Prioridad", project.priority),
            ("Fecha de Inicio", str(project.start_date)),
            ("Fecha de Fin", str(project.end_date) if project.end_date else "No definida"),
            ("Gestor Responsable", manager_name),
            ("Categoría", category_name),
            ("Progreso", f"{project.progress}%"),
        ]

        for label, value in fields:
            row = ctk.CTkFrame(scroll, fg_color="#16213e", corner_radius=8, height=45)
            row.pack(fill="x", pady=4)
            row.pack_propagate(False)
            ctk.CTkLabel(row, text=label + ":", font=ctk.CTkFont(size=12), text_color="#a0a0a0", width=160, anchor="w").pack(side="left", padx=15)
            ctk.CTkLabel(row, text=value, font=ctk.CTkFont(size=12, weight="bold"), text_color="#ffffff", anchor="w").pack(side="left", padx=5)

        ctk.CTkButton(scroll, text="Cerrar", fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, height=38, command=dialog.destroy).pack(pady=15)

    def _show_edit_project_dialog(self, project) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar: {project.name}")
        dialog.geometry("420x500")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Editar Proyecto", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(pady=(0, 15))

        ctk.CTkLabel(scroll, text="Cambiar Estado:", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w")
        estados = ["Planificado", "En Curso", "Finalizado", "Cancelado"]
        status_combo = ctk.CTkComboBox(scroll, values=estados, height=35, corner_radius=8)
        status_combo.set(project.status)
        status_combo.pack(fill="x", pady=(2, 15))

        ctk.CTkLabel(scroll, text="Descripción:", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w")
        desc_box = ctk.CTkTextbox(scroll, height=80, corner_radius=8)
        desc_box.pack(fill="x", pady=(2, 15))
        if project.description:
            desc_box.insert("1.0", project.description)

        def guardar_cambios():
            nuevo_estado = status_combo.get()
            nueva_desc = desc_box.get("1.0", "end-1c").strip()

            # RN-UX-04: Confirmación para cancelar o cerrar proyecto
            if nuevo_estado in ["Cancelado", "Finalizado"] and project.status != nuevo_estado:
                accion = "cancelar" if nuevo_estado == "Cancelado" else "finalizar"
                if not messagebox.askyesno("Confirmar acción crítica",
                                           f"¿Está seguro que desea {accion} el proyecto '{project.name}'?\nEsta acción no se puede deshacer."):
                    return

            try:
                current_user = self.controller.session_service.current_user
                self.project_service.validar_transicion_estado(project.status, nuevo_estado)
                self.project_service.verificar_permiso_estado(current_user, project)
                project.status = nuevo_estado
                project.description = nueva_desc
                self.project_service.project_repo.update(project)
                messagebox.showinfo("Éxito", "Proyecto actualizado correctamente.")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=10)
        ctk.CTkButton(btns, text="Cancelar", width=120, fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(btns, text="Guardar", width=120, fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8, command=guardar_cambios).pack(side="right")

    def _show_milestones_dialog(self, project) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Hitos: {project.name}")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"Hitos de: {project.name}", font=ctk.CTkFont(size=18, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 15))

        try:
            milestones = self.milestone_controller.milestone_service.milestone_repo.get_by_project(project.id)
            if not milestones:
                ctk.CTkLabel(scroll, text="No hay hitos registrados para este proyecto.", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(pady=20)
            else:
                for m in milestones:
                    row = ctk.CTkFrame(scroll, fg_color="#16213e", corner_radius=8, height=55)
                    row.pack(fill="x", pady=4)
                    row.pack_propagate(False)
                    ctk.CTkLabel(row, text=m.name, font=ctk.CTkFont(size=13, weight="bold"), text_color="#ffffff").pack(side="left", padx=15)
                    status_colors = {"Pendiente": "#3498db", "Cumplido": "#2ecc71", "Vencido": "#e74c3c"}
                    ctk.CTkLabel(row, text=m.status, font=ctk.CTkFont(size=11), text_color=status_colors.get(m.status, "#a0a0a0")).pack(side="right", padx=15)
        except Exception as e:
            ctk.CTkLabel(scroll, text=f"Error al cargar hitos: {e}", font=ctk.CTkFont(size=12), text_color="#e74c3c").pack(pady=10)

        ctk.CTkButton(scroll, text="Cerrar", fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, height=38, command=dialog.destroy).pack(pady=15)

    def show_new_project_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Proyecto")
        dialog.geometry("420x680")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        content = scroll

        ctk.CTkLabel(content, text="Crear Nuevo Proyecto", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(pady=(0, 20))

        name_entry = self._create_labeled_entry(content, "Nombre del Proyecto:")
        desc_textbox = self._create_labeled_textbox(content, "Descripción:")
        start_date_entry = self._create_labeled_entry(content, "Fecha de Inicio (YYYY-MM-DD):")
        end_date_entry = self._create_labeled_entry(content, "Fecha de Fin (YYYY-MM-DD, opcional):")

        priorities = ["Alta", "Media", "Baja"]
        priority_combobox = self._create_labeled_combobox(content, "Prioridad:", priorities)

        managers = self.user_service.user_repo.get_all()
        valid_managers = [u for u in managers if u.role in ["Administrador", "Gestor"]]
        manager_options = [f"{u.name} {u.last_name}" for u in valid_managers]
        self._manager_map = {f"{u.name} {u.last_name}": u.id for u in valid_managers}
        manager_combobox = self._create_labeled_combobox(content, "Gestor Responsable:", manager_options)

        categories = self.category_service.get_all_categories()
        category_options = [c.name for c in categories]
        self._category_map = {c.name: c.id for c in categories}
        category_combobox = self._create_labeled_combobox(content, "Categoría:", category_options)

        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        ctk.CTkButton(buttons_frame, text="Cancelar", width=120, height=40, fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(buttons_frame, text="Crear Proyecto", width=150, height=40, fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8,
                      command=lambda: self._handle_create_project(
                          dialog, name_entry.get(), desc_textbox.get("1.0", "end-1c"),
                          priority_combobox.get(), start_date_entry.get(), end_date_entry.get(),
                          manager_combobox.get(), category_combobox.get()
                      )).pack(side="right")

    def _create_labeled_entry(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w")
        entry = ctk.CTkEntry(frame, height=35, corner_radius=8)
        entry.pack(fill="x", pady=(2, 0))
        return entry

    def _create_labeled_textbox(self, parent, label_text):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w")
        textbox = ctk.CTkTextbox(frame, height=70, corner_radius=8)
        textbox.pack(fill="x", pady=(2, 0))
        return textbox

    def _create_labeled_combobox(self, parent, label_text, values):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.pack(fill="x", pady=5)
        ctk.CTkLabel(frame, text=label_text, font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w")
        combobox = ctk.CTkComboBox(frame, values=values, height=35, corner_radius=8)
        combobox.pack(fill="x", pady=(2, 0))
        if values:
            combobox.set(values[0])
        return combobox

    def _handle_create_project(self, dialog, name, description, priority,
                               start_date_str, end_date_str, manager_name, category_name):
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date() if end_date_str.strip() else None

            manager_id = self._manager_map.get(manager_name)
            if not manager_id:
                raise ValueError("Debe seleccionar un gestor responsable válido.")

            category_id = self._category_map.get(category_name)
            if not category_id:
                raise ValueError("Debe seleccionar una categoría válida.")

            self.project_controller.create_project(name, description, priority, start_date, end_date, manager_id, category_id)
            dialog.destroy()
            self.load_data()
        except ValueError as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Ocurrió un error al crear el proyecto: {e}")