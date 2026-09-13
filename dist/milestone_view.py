import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING
from uuid import UUID
from datetime import date

if TYPE_CHECKING:
    from main_controller import MainController

class MilestoneView(ctk.CTkFrame):
    def __init__(self, parent, controller: 'MainController'):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.controller = controller
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Encabezado
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        header_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header_frame, text="Gestión de Hitos",
                     font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(header_frame, text="+ Nuevo Hito", width=150,
                      command=self._open_create_dialog).grid(row=0, column=1, sticky="e")

        # Filtro por proyecto
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(filter_frame, text="Filtrar por proyecto:").pack(side="left", padx=(0, 10))
        self.project_filter = ctk.CTkComboBox(filter_frame, width=250, command=self._on_project_filter)
        self.project_filter.pack(side="left")

        # Tabla de hitos
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)

        self._projects = []
        self._project_map = {}  # nombre -> id

    def load_data(self):
        try:
            projects = self.controller.project_service.project_repo.get_all_active()
            self._projects = projects
            self._project_map = {p.name: p.id for p in projects}
            names = ["Todos"] + [p.name for p in projects]
            self.project_filter.configure(values=names)
            self.project_filter.set("Todos")
            self._load_milestones(None)
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {e}")

    def _on_project_filter(self, selected):
        project_id = self._project_map.get(selected) if selected != "Todos" else None
        self._load_milestones(project_id)

    def _load_milestones(self, project_id):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        headers = ["Nombre", "Proyecto", "Fecha Programada", "Fecha Cumplimiento", "Estado", "Acciones"]
        for col, h in enumerate(headers):
            ctk.CTkLabel(self.scroll_frame, text=h,
                         font=ctk.CTkFont(weight="bold")).grid(row=0, column=col, padx=10, pady=5, sticky="w")

        try:
            if project_id:
                milestones = self.controller.milestone_controller.get_milestones_by_project(project_id)
                project_names = {p.id: p.name for p in self._projects}
            else:
                milestones = []
                project_names = {p.id: p.name for p in self._projects}
                for p in self._projects:
                    milestones += self.controller.milestone_controller.get_milestones_by_project(p.id)

            if not milestones:
                ctk.CTkLabel(self.scroll_frame, text="No hay hitos registrados.",
                             text_color="gray").grid(row=1, column=0, columnspan=6, pady=20)
                return

            status_colors = {
                "Pendiente": "#F0A500",
                "Cumplido": "#2ECC71",
                "Vencido": "#E74C3C"
            }

            for row_idx, milestone in enumerate(milestones, start=1):
                proj_name = project_names.get(milestone.project_id, "—")
                fecha_cumplimiento = str(milestone.effective_completion_date) if milestone.effective_completion_date else "—"
                color = status_colors.get(milestone.status, "gray")

                ctk.CTkLabel(self.scroll_frame, text=milestone.name).grid(row=row_idx, column=0, padx=10, pady=4, sticky="w")
                ctk.CTkLabel(self.scroll_frame, text=proj_name).grid(row=row_idx, column=1, padx=10, pady=4, sticky="w")
                ctk.CTkLabel(self.scroll_frame, text=str(milestone.scheduled_date)).grid(row=row_idx, column=2, padx=10, pady=4, sticky="w")
                ctk.CTkLabel(self.scroll_frame, text=fecha_cumplimiento).grid(row=row_idx, column=3, padx=10, pady=4, sticky="w")
                ctk.CTkLabel(self.scroll_frame, text=milestone.status,
                             text_color=color).grid(row=row_idx, column=4, padx=10, pady=4, sticky="w")

                btn_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
                btn_frame.grid(row=row_idx, column=5, padx=10, pady=4)
                ctk.CTkButton(btn_frame, text="Editar", width=70,
                              command=lambda m=milestone: self._open_edit_dialog(m)).pack(side="left", padx=2)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar hitos: {e}")

    def _open_create_dialog(self):
        if not self._projects:
            messagebox.showwarning("Aviso", "No hay proyectos disponibles para asignar un hito.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Hito")
        dialog.geometry("450x400")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Nombre:").pack(padx=20, pady=(15, 0), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=400)
        name_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Descripción:").pack(padx=20, pady=(10, 0), anchor="w")
        desc_entry = ctk.CTkTextbox(dialog, width=400, height=80)
        desc_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Proyecto:").pack(padx=20, pady=(10, 0), anchor="w")
        project_combo = ctk.CTkComboBox(dialog, values=[p.name for p in self._projects], width=400)
        project_combo.set(self._projects[0].name)
        project_combo.pack(padx=20)

        ctk.CTkLabel(dialog, text="Fecha Programada (YYYY-MM-DD):").pack(padx=20, pady=(10, 0), anchor="w")
        sched_entry = ctk.CTkEntry(dialog, width=400)
        sched_entry.pack(padx=20)

        def guardar():
            try:
                sched = date.fromisoformat(sched_entry.get().strip())
                project_id = self._project_map.get(project_combo.get())
                if not project_id:
                    raise ValueError("Selecciona un proyecto válido.")
                self.controller.milestone_controller.create_milestone(
                    name_entry.get().strip(),
                    desc_entry.get("1.0", "end").strip(),
                    project_id,
                    sched
                )
                dialog.destroy()
                self.load_data()
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Crear Hito", command=guardar).pack(pady=15)

    def _open_edit_dialog(self, milestone):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Hito: {milestone.name}")
        dialog.geometry("450x450")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Nombre:").pack(padx=20, pady=(15, 0), anchor="w")
        name_entry = ctk.CTkEntry(dialog, width=400)
        name_entry.insert(0, milestone.name)
        name_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Descripción:").pack(padx=20, pady=(10, 0), anchor="w")
        desc_entry = ctk.CTkTextbox(dialog, width=400, height=80)
        desc_entry.insert("1.0", milestone.description or "")
        desc_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Fecha Programada (YYYY-MM-DD):").pack(padx=20, pady=(10, 0), anchor="w")
        sched_entry = ctk.CTkEntry(dialog, width=400)
        sched_entry.insert(0, str(milestone.scheduled_date))
        sched_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Fecha Cumplimiento Efectivo (YYYY-MM-DD, opcional):").pack(padx=20, pady=(10, 0), anchor="w")
        comp_entry = ctk.CTkEntry(dialog, width=400)
        comp_entry.insert(0, str(milestone.effective_completion_date) if milestone.effective_completion_date else "")
        comp_entry.pack(padx=20)

        ctk.CTkLabel(dialog, text="Estado:").pack(padx=20, pady=(10, 0), anchor="w")
        status_var = ctk.CTkComboBox(dialog, values=["Pendiente", "Cumplido", "Vencido"], width=400)
        status_var.set(milestone.status)
        status_var.pack(padx=20)

        def guardar():
            try:
                sched = date.fromisoformat(sched_entry.get().strip()) 
                comp_str = comp_entry.get().strip()
                comp = date.fromisoformat(comp_str) if comp_str else None
                self.controller.milestone_controller.update_milestone(
                    milestone.id,
                    name_entry.get().strip(),
                    desc_entry.get("1.0", "end").strip(),
                    sched, comp,
                    status_var.get()
                )
                dialog.destroy()
                self._load_milestones(None if self.project_filter.get() == "Todos"
                                      else self._project_map.get(self.project_filter.get()))
            except ValueError as e:
                messagebox.showerror("Error", str(e))

        ctk.CTkButton(dialog, text="Guardar", command=guardar).pack(pady=15)