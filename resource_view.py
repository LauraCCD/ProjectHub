import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING, List
from uuid import UUID

from user import User

if TYPE_CHECKING:
    from main_controller import MainController
    from user_service import UserService
    from resource_controller import ResourceController
    from team_controller import TeamController

class ResourceView(ctk.CTkFrame):
    def __init__(self, parent_frame: ctk.CTkFrame, controller: 'MainController', user_service: 'UserService', resource_controller: 'ResourceController', team_controller: 'TeamController' = None):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller
        self.user_service = user_service
        self.resource_controller = resource_controller
        self.team_controller = team_controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=30, pady=20)
        ctk.CTkLabel(header, text="Gestión de Recursos", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").pack(side="left")
        ctk.CTkButton(header, text="+ Agregar Recurso", font=ctk.CTkFont(size=13), fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", corner_radius=10, height=40, command=self.show_new_resource_dialog).pack(side="right")

        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 15))

        self.resources_scroll_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.resources_scroll_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=10)

    def load_data(self) -> None:
        for widget in self.resources_scroll_frame.winfo_children():
            widget.destroy()
        for widget in self.summary_frame.winfo_children():
            widget.destroy()

        all_resources = self.user_service.user_repo.get_all()
        active_resources = [r for r in all_resources if r.status == 'Activo']

        self._update_summary_cards(active_resources)

        for resource in active_resources:
            self._create_resource_card(self.resources_scroll_frame, resource)

    def _update_summary_cards(self, resources: List[User]) -> None:
        total_resources = len(resources)
        high_avail = len([r for r in resources if r.availability >= 70])
        medium_avail = len([r for r in resources if 40 <= r.availability < 70])
        low_avail = len([r for r in resources if r.availability < 40])

        summaries = [
            ("Total Recursos", str(total_resources), "#4ecca3"),
            ("Alta Disponibilidad", str(high_avail), "#3498db"),
            ("Media Disponibilidad", str(medium_avail), "#f39c12"),
            ("Baja Disponibilidad", str(low_avail), "#e74c3c"),
        ]

        for title, value, color in summaries:
            card = ctk.CTkFrame(self.summary_frame, fg_color="#16213e", corner_radius=12, height=80)
            card.pack(side="left", fill="both", expand=True, padx=5)
            card.pack_propagate(False)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=11), text_color="#a0a0a0").pack(padx=15, pady=(12, 2), anchor="w")
            ctk.CTkLabel(card, text=value, font=ctk.CTkFont(size=28, weight="bold"), text_color=color).pack(padx=15, anchor="w")

    def _create_resource_card(self, parent: ctk.CTkFrame, resource: User) -> None:
        card = ctk.CTkFrame(parent, fg_color="#16213e", corner_radius=15, height=100)
        card.pack(fill="x", pady=8)
        card.pack_propagate(False)

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=15)

        left_frame = ctk.CTkFrame(content, fg_color="transparent")
        left_frame.pack(side="left", fill="y")

        avatar = ctk.CTkFrame(left_frame, width=50, height=50, fg_color="#4ecca3", corner_radius=25)
        avatar.pack(side="left")
        avatar.pack_propagate(False)
        ctk.CTkLabel(avatar, text=resource.name[0], font=ctk.CTkFont(size=20, weight="bold"), text_color="#1a1a2e").place(relx=0.5, rely=0.5, anchor="center")

        info_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        info_frame.pack(side="left", padx=15)
        ctk.CTkLabel(info_frame, text=f"{resource.name} {resource.last_name}", font=ctk.CTkFont(size=16, weight="bold"), text_color="#ffffff").pack(anchor="w")
        ctk.CTkLabel(info_frame, text=resource.role, font=ctk.CTkFont(size=12), text_color="#a0a0a0").pack(anchor="w")

        avail_frame = ctk.CTkFrame(content, fg_color="transparent")
        avail_frame.pack(side="right", fill="y")
        avail_color = "#4ecca3" if resource.availability >= 70 else "#f39c12" if resource.availability >= 40 else "#e74c3c"
        ctk.CTkLabel(avail_frame, text="Disponibilidad", font=ctk.CTkFont(size=11), text_color="#6c757d").pack()
        ctk.CTkLabel(avail_frame, text=f"{resource.availability}%", font=ctk.CTkFont(size=24, weight="bold"), text_color=avail_color).pack()
        progress_bar = ctk.CTkProgressBar(avail_frame, height=8, width=100, corner_radius=4, progress_color=avail_color)
        progress_bar.pack(pady=5)
        progress_bar.set(resource.availability / 100)

        # Botón desactivar (solo admin)
        current_user = self.controller.session_service.current_user
        if current_user and current_user.role == "Administrador":
            btn_frame = ctk.CTkFrame(content, fg_color="transparent")
            btn_frame.pack(side="right", fill="y", padx=(0, 20))
            ctk.CTkButton(btn_frame, text="Desactivar", width=90, height=28,
                          fg_color="#e74c3c", hover_color="#c0392b", corner_radius=8,
                          command=lambda r=resource: self._desactivar_usuario(r)).pack(pady=5)

    def _desactivar_usuario(self, resource: User) -> None:
        current_user = self.controller.session_service.current_user
        if not current_user:
            return
        if not messagebox.askyesno("Confirmar", f"¿Desactivar al usuario '{resource.name} {resource.last_name}'?"):
            return
        try:
            self.controller.user_service.proteger_ultimo_admin(resource.id)
            self.controller.user_service.verificar_tareas_antes_desactivar(resource.id)
            resource.status = "Inactivo"
            self.controller.user_service.user_repo.update(resource)
            messagebox.showinfo("Éxito", f"Usuario '{resource.name}' desactivado.")
            self.load_data()
        except (ValueError, PermissionError) as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", str(e))

    def show_new_resource_dialog(self) -> None:
        current_user = self.controller.session_service.current_user
        if not current_user or current_user.role != "Administrador":
            messagebox.showerror("Acceso denegado", "Solo el Administrador puede crear usuarios.")
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Nuevo Usuario")
        dialog.geometry("450x550")
        dialog.grab_set()

        scroll = ctk.CTkScrollableFrame(dialog, fg_color="#1a1a2e")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="Crear Nuevo Usuario",
                     font=ctk.CTkFont(size=20, weight="bold"), text_color="#ffffff").pack(pady=(0, 15))

        ctk.CTkLabel(scroll, text="Nombre:", text_color="#a0a0a0").pack(anchor="w")
        name_entry = ctk.CTkEntry(scroll, width=400, placeholder_text="Nombre")
        name_entry.pack(pady=(2, 10))

        ctk.CTkLabel(scroll, text="Apellido:", text_color="#a0a0a0").pack(anchor="w")
        last_name_entry = ctk.CTkEntry(scroll, width=400, placeholder_text="Apellido")
        last_name_entry.pack(pady=(2, 10))

        ctk.CTkLabel(scroll, text="Correo Electrónico:", text_color="#a0a0a0").pack(anchor="w")
        email_entry = ctk.CTkEntry(scroll, width=400, placeholder_text="usuario@ejemplo.com")
        email_entry.pack(pady=(2, 10))

        ctk.CTkLabel(scroll, text="Contraseña:", text_color="#a0a0a0").pack(anchor="w")
        password_entry = ctk.CTkEntry(scroll, width=400, show="*", placeholder_text="Mínimo 8 chars, mayúscula, número, especial")
        password_entry.pack(pady=(2, 10))

        ctk.CTkLabel(scroll, text="Rol:", text_color="#a0a0a0").pack(anchor="w")
        role_combo = ctk.CTkComboBox(scroll, values=["Administrador", "Gestor", "Colaborador"], width=400)
        role_combo.set("Colaborador")
        role_combo.pack(pady=(2, 10))

        ctk.CTkLabel(scroll, text="Disponibilidad (0-100):", text_color="#a0a0a0").pack(anchor="w")
        avail_entry = ctk.CTkEntry(scroll, width=400, placeholder_text="100")
        avail_entry.insert(0, "100")
        avail_entry.pack(pady=(2, 15))

        def crear():
            try:
                avail_str = avail_entry.get().strip()
                if not avail_str.isdigit() or not (0 <= int(avail_str) <= 100):
                    raise ValueError("La disponibilidad debe ser un número entre 0 y 100.")
                new_user = self.controller.user_service.create_user(
                    name=name_entry.get().strip(),
                    last_name=last_name_entry.get().strip(),
                    email=email_entry.get().strip(),
                    password=password_entry.get(),
                    role=role_combo.get(),
                    availability=int(avail_str)
                )
                messagebox.showinfo("Éxito", f"Usuario '{new_user.name} {new_user.last_name}' creado con rol '{new_user.role}'.")
                dialog.destroy()
                self.load_data()
            except (ValueError, PermissionError) as e:
                messagebox.showerror("Error de Validación", str(e))
            except Exception as e:
                messagebox.showerror("Error Inesperado", str(e))

        btns = ctk.CTkFrame(scroll, fg_color="transparent")
        btns.pack(fill="x", pady=10)
        ctk.CTkButton(btns, text="Cancelar", width=120, fg_color="#6c757d",
                      hover_color="#5a6268", corner_radius=8, command=dialog.destroy).pack(side="left")
        ctk.CTkButton(btns, text="Crear Usuario", width=150, fg_color="#4ecca3",
                      text_color="#1a1a2e", hover_color="#3db892", corner_radius=8,
                      command=crear).pack(side="right")