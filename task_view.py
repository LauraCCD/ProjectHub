import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, List
from uuid import UUID
from datetime import datetime, date

from task import Task

if TYPE_CHECKING:
    from main_controller import MainController
    from task_service import TaskService
    from session_service import SessionService
    from permission_service import PermissionService
    from project_service import ProjectService
    from user_service import UserService
    from task_controller import TaskController
    from comment_service import CommentService

class TaskView(ctk.CTkFrame):
    def __init__(self, parent_frame, controller, task_service, session_service, permission_service, project_service, user_service, task_controller, comment_service=None):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.task_service = task_service
        self.session_service = session_service
        self.permission_service = permission_service
        self.project_service = project_service
        self.user_service = user_service
        self.task_controller = task_controller
        self.comment_service = comment_service

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Gestión de Tareas", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkButton(header, text="+ Nueva Tarea", font=ctk.CTkFont(size=13), fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=10, height=40, command=self.show_new_task_dialog).pack(side="right")

        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 15))

        self.tasks_scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.tasks_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)

    def load_data(self) -> None:
        for widget in self.tasks_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        current_user = self.session_service.current_user
        if not current_user:
            return

        all_tasks = self.task_service.task_repo.get_all()

        if current_user.role == "Colaborador":
            visible_tasks = [t for t in all_tasks if t.assignee_id == current_user.id]
        elif current_user.role == "Gestor":
            all_projects = self.project_service.project_repo.get_all()
            managed_project_ids = {p.id for p in all_projects if p.manager_id == current_user.id}
            visible_tasks = [t for t in all_tasks if t.project_id in managed_project_ids]
        else:
            visible_tasks = all_tasks

        self._update_summary_cards(visible_tasks)

        if not visible_tasks:
            ctk.CTkLabel(self.tasks_scroll_frame, text="No hay tareas para mostrar.",
                         font=ctk.CTkFont(size=14), text_color="#a0a0a0").pack(pady=30)
            return

        for task in visible_tasks:
            self._create_task_card(self.tasks_scroll_frame, task)

    def _update_summary_cards(self, tasks: List[Task]) -> None:
        total = len(tasks)
        pendientes = len([t for t in tasks if t.status == "Pendiente"])
        en_progreso = len([t for t in tasks if t.status == "En Progreso"])
        completadas = len([t for t in tasks if t.status == "Completada"])
        vencidas = len([t for t in tasks if t.status == "Vencida"])

        summaries = [
            ("Total Tareas", str(total), "#4ecca3"),
            ("Pendientes", str(pendientes), "#3498db"),
            ("En Progreso", str(en_progreso), "#f39c12"),
            ("Completadas", str(completadas), "#2ecc71"),
            ("Vencidas", str(vencidas), "#e74c3c"),
        ]

        for title, value, color in summaries:
            card = ctk.CTkFrame(self.summary_frame, fg_color="#16213e", corner_radius=12, height=80)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#a0a0a0").pack(padx=15, pady=(12, 2), anchor="w")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack(padx=15, anchor="w")

    def _create_task_card(self, parent, task) -> None:
        card = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=15, height=110)
        card.pack(fill="x", pady=8)
        card.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=12)

        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="y", expand=True)

        priority_colors = {"Alta": "#e74c3c", "Media": "#f39c12", "Baja": "#2ecc71"}
        priority_color = priority_colors.get(task.priority, "#a0a0a0")

        ctk.CTkLabel(left_frame, text=task.title, font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(left_frame, text=f"Prioridad: {task.priority}  |  Vence: {task.due_date}", font=ctk.CTkFont(size=12), text_color=priority_color).pack(anchor="w", pady=2)

        progress_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        progress_frame.pack(anchor="w", pady=(4, 0))
        progress_bar = ctk.CTkProgressBar(progress_frame, height=8, width=200, corner_radius=4)
        progress_bar.pack(side="left")
        progress_bar.set(task.progress / 100)
        ctk.CTkLabel(progress_frame, text=f"{task.progress}%", font=ctk.CTkFont(size=11), text_color="#a0a0a0").pack(side="left", padx=5)

        right_frame = ctk.CTkFrame(content, fg_color="transparent")
        right_frame.pack(side="right", fill="y")

        status_colors = {"Pendiente": "#3498db", "En Progreso": "#f39c12", "Completada": "#2ecc71", "Vencida": "#e74c3c", "Cancelada": "#6c757d"}
        status_color = status_colors.get(task.status, "#a0a0a0")
        ctk.CTkLabel(right_frame, text=task.status, font=ctk.CTkFont(size=13, weight="bold"), text_color=status_color).pack(anchor="e", pady=(0, 4))

        ctk.CTkButton(right_frame, text="Cambiar Estado", width=130, height=30,
                      fg_color="#2d4263", hover_color="#3d5273", corner_radius=8,
                      command=lambda t=task: self._show_change_status_dialog(t)).pack(anchor="e")

        if self.comment_service:
            ctk.CTkButton(right_frame, text="Comentarios", width=130, height=30,
                          fg_color="#4a235a", hover_color="#6c3483", corner_radius=8,
                          command=lambda t=task: self._show_comments_dialog(t)).pack(anchor="e", pady=(4, 0))

    def _show_change_status_dialog(self, task) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Cambiar Estado de Tarea")
        dialog.geometry("350x250")
        dialog.transient(self)
        dialog.grab_set()

        content = ctk.CTkFrame(dialog, fg_color="#1a1a2e")
        content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(content, text=f"Tarea: {task.title}", font=ctk.CTkFont(size=14, weight="bold"), text_color="#ffffff").pack(pady=(0, 5))
        ctk.CTkLabel(content, text=f"Estado actual: {task.status}", font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(pady=(0, 15))

        estados = ["Pendiente", "En Progreso", "Completada", "Cancelada"]
        status_combobox = ctk.CTkComboBox(content, values=estados, height=35, corner_radius=8)
        status_combobox.set(task.status)
        status_combobox.pack(fill="x", pady=(0, 20))

        def aplicar_cambio():
            nuevo_estado = status_combobox.get()
            try:
                self.task_service.update_task_status(task.id, nuevo_estado, self.session_service.current_user)
                messagebox.showinfo("Éxito", f"Estado actualizado a '{nuevo_estado}'.")
                dialog.destroy()
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        btns = ctk.CTkFrame(content, fg_color="transparent")
        btns.pack(fill="x")
        ctk.CTkButton(btns, text="Cancelar", width=100, fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(btns, text="Aplicar", width=100, fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8, command=aplicar_cambio).pack(side="right")

    def _show_comments_dialog(self, task) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Comentarios: {task.title}")
        dialog.geometry("500x500")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text=f"Comentarios de: {task.title}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w", pady=(0, 10))

        try:
            comments = self.comment_service.comment_repo.get_comments_by_task(task.id)
            if not comments:
                ctk.CTkLabel(scroll, text="No hay comentarios.", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(pady=20)
            else:
                current_user = self.session_service.current_user
                for c in comments:
                    row = ctk.CTkFrame(scroll, fg_color="#16213e", corner_radius=8)
                    row.pack(fill="x", pady=4, padx=5)
                    ctk.CTkLabel(row, text=c.content, font=ctk.CTkFont(size=12), text_color="#ffffff",
                                 wraplength=400, justify="left").pack(anchor="w", padx=15, pady=(8, 2))

                    footer = ctk.CTkFrame(row, fg_color="transparent")
                    footer.pack(fill="x", padx=15, pady=(0, 8))

                    fecha_text = str(c.created_at)
                    if c.edited_at:
                        fecha_text += "  ✏ Editado"
                    ctk.CTkLabel(footer, text=fecha_text, font=ctk.CTkFont(size=10),
                                 text_color="#f39c12" if c.edited_at else "#6c757d").pack(side="left")

                    # RN-CO-06: Botón eliminar para autor o admin
                    if current_user and (current_user.id == c.user_id or current_user.role == "Administrador"):
                        ctk.CTkButton(footer, text="🗑 Eliminar", width=80, height=22,
                                      fg_color="#e74c3c", hover_color="#c0392b", corner_radius=6,
                                      font=ctk.CTkFont(size=10),
                                      command=lambda cid=c.id, t=task: self._eliminar_comentario(cid, t, dialog)).pack(side="right")

        except Exception as e:
            ctk.CTkLabel(scroll, text=f"Error al cargar comentarios: {e}", font=ctk.CTkFont(size=12), text_color="#e74c3c").pack(pady=10)

        ctk.CTkLabel(scroll, text="Nuevo comentario:", font=ctk.CTkFont(size=13), text_color="#a0a0a0").pack(anchor="w", pady=(15, 2))
        comment_box = ctk.CTkTextbox(scroll, height=60, corner_radius=8)
        comment_box.pack(fill="x", pady=(0, 10))

        def agregar_comentario():
            texto = comment_box.get("1.0", "end-1c").strip()
            if not texto:
                messagebox.showwarning("Advertencia", "El comentario no puede estar vacío.")
                return
            try:
                current_user = self.session_service.current_user
                self.comment_service.add_comment(task.id, current_user.id, texto)
                dialog.destroy()
                self._show_comments_dialog(task)
            except Exception as e:
                messagebox.showerror("Error", str(e))

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x")
        ctk.CTkButton(btns, text="Cerrar", width=100, fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(btns, text="Agregar", width=100, fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8, command=agregar_comentario).pack(side="right")

    def _eliminar_comentario(self, comment_id, task, dialog) -> None:
        current_user = self.session_service.current_user
        if not messagebox.askyesno("Confirmar", "¿Eliminar este comentario?"):
            return
        try:
            self.comment_service.delete_comment(comment_id, current_user)
            dialog.destroy()
            self._show_comments_dialog(task)
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error", str(e))

    def show_new_task_dialog(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Tarea")
        dialog.geometry("520x680")
        dialog.transient(self)
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        content = scroll

        ctk.CTkLabel(content, text="Crear Nueva Tarea", font=ctk.CTkFont(size=22, weight="bold"), text_color="#ffffff").pack(pady=(0, 20))

        title_entry = self._create_labeled_entry(content, "Título de la Tarea:")
        desc_textbox = self._create_labeled_textbox(content, "Descripción:")
        due_date_entry = self._create_labeled_entry(content, "Fecha Límite (YYYY-MM-DD):")

        priorities = ["Alta", "Media", "Baja"]
        priority_combobox = self._create_labeled_combobox(content, "Prioridad:", priorities)

        current_user = self.session_service.current_user
        if not current_user:
            messagebox.showerror("Error", "Debe iniciar sesión para crear tareas.")
            dialog.destroy()
            return

        all_projects = self.project_service.project_repo.get_all()
        user_projects = [p for p in all_projects if self.permission_service.can_create_task(current_user, p.id)]
        project_options = [p.name for p in user_projects]
        self._project_map = {p.name: p.id for p in user_projects}
        project_combobox = self._create_labeled_combobox(content, "Proyecto:", project_options)

        all_users = self.user_service.user_repo.get_all()
        active_users = [u for u in all_users if u.status == "Activo"]
        assignee_options = [f"{u.name} {u.last_name}" for u in active_users]
        self._assignee_map = {f"{u.name} {u.last_name}": u.id for u in active_users}
        assignee_combobox = self._create_labeled_combobox(content, "Asignado a:", assignee_options)

        buttons_frame = ctk.CTkFrame(content, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=20)
        ctk.CTkButton(buttons_frame, text="Cancelar", width=120, height=40, fg_color="#6c757d", hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(buttons_frame, text="Crear Tarea", width=150, height=40, fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=8,
                      command=lambda: self._handle_create_task(
                          dialog, title_entry.get(), desc_textbox.get("1.0", "end-1c"),
                          project_combobox.get(), assignee_combobox.get(),
                          priority_combobox.get(), due_date_entry.get()
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

    def _handle_create_task(self, dialog, title, description, project_name, assignee_name, priority, due_date_str):
        try:
            if not title.strip():
                raise ValueError("El título de la tarea no puede estar vacío.")
            if not due_date_str.strip():
                raise ValueError("La fecha límite es obligatoria.")
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d").date()

            project_id = self._project_map.get(project_name)
            if not project_id:
                raise ValueError("Debe seleccionar un proyecto válido.")

            assignee_id = self._assignee_map.get(assignee_name)
            if not assignee_id:
                raise ValueError("Debe seleccionar un responsable válido.")

            self.task_controller.create_task(title, description, project_id, assignee_id, priority, due_date)
            dialog.destroy()
            self.load_data()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error de Validación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al crear la tarea: {e}")