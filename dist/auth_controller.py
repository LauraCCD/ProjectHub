import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING
import secrets
from datetime import datetime, timedelta

from auth_service import AuthService, AuthenticationError
from session_service import SessionService

if TYPE_CHECKING:
    from main_controller import MainController

class AuthController:
    def __init__(self, main_controller: 'MainController', auth_service: AuthService, session_service: SessionService):
        self.main_controller = main_controller
        self.auth_service = auth_service
        self.session_service = session_service

    @property
    def main_view(self):
        return self.main_controller.main_view

    def login(self, email: str, password: str) -> None:
        try:
            user = self.auth_service.autenticar(email, password)
            self.session_service.start_session(user)
            messagebox.showinfo("Éxito", f"Bienvenido, {user.name}!")
            self.main_view.show_dashboard()
        except AuthenticationError as e:
            messagebox.showerror("Error de Autenticación", str(e))
        except Exception as e:
            self.main_view.login_view.clear_fields()
            messagebox.showerror("Error Inesperado", f"Ocurrió un error durante el login: {e}")

    def logout(self) -> None:
        self.session_service.end_session()
        messagebox.showinfo("Sesión Cerrada", "Has cerrado sesión correctamente.")
        self.main_view.show_login()
        self.main_view.login_view.clear_fields()

    def create_initial_admin(self, name: str, last_name: str, email: str, password: str) -> None:
        try:
            new_admin = self.main_controller.user_service.create_user(
                name=name, last_name=last_name, email=email, password=password, role="Administrador", availability=100
            )
            messagebox.showinfo("Éxito", f"Administrador '{new_admin.name}' creado con éxito. Por favor, inicie sesión.")
            self.main_view.show_login()
            self.main_view.login_view.clear_fields()
            self.main_view.initial_setup_view.clear_fields()
        except ValueError as e:
            messagebox.showerror("Error de Creación", str(e))
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al crear el administrador: {e}")

    def solicitar_recuperacion(self, email: str) -> None:
        """RN-AU-06: Genera token de recuperación válido por 30 minutos."""
        try:
            user = self.main_controller.user_repo.get_by_email(email.strip())
            if not user:
                messagebox.showinfo("Recuperación", "Si el correo existe en el sistema, recibirás instrucciones.")
                return

            token = secrets.token_urlsafe(32)
            expires_at = datetime.now() + timedelta(minutes=30)

            query = """
                INSERT INTO password_reset_tokens (user_id, token, expires_at)
                VALUES (%s, %s, %s);
            """
            with self.main_controller.db_connection.get_cursor() as cursor:
                cursor.execute(query, (str(user.id), token, expires_at))
                self.main_controller.db_connection.connection.commit()

            messagebox.showinfo("Token de Recuperación",
                f"Tu token de recuperación es:\n\n{token}\n\nVálido por 30 minutos.")
            self._mostrar_formulario_nueva_contrasena(user.id, token)

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar recuperación: {e}")

    def _mostrar_formulario_nueva_contrasena(self, user_id, token: str) -> None:
        dialog = ctk.CTkToplevel()
        dialog.title("Nueva Contraseña")
        dialog.geometry("400x300")
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Nueva Contraseña", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)

        ctk.CTkLabel(dialog, text="Token de recuperación:", text_color="#a0a0a0").pack(anchor="w", padx=20)
        token_entry = ctk.CTkEntry(dialog, width=360)
        token_entry.pack(padx=20, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Nueva contraseña:", text_color="#a0a0a0").pack(anchor="w", padx=20)
        password_entry = ctk.CTkEntry(dialog, width=360, show="*")
        password_entry.pack(padx=20, pady=(2, 10))

        ctk.CTkLabel(dialog, text="Confirmar contraseña:", text_color="#a0a0a0").pack(anchor="w", padx=20)
        confirm_entry = ctk.CTkEntry(dialog, width=360, show="*")
        confirm_entry.pack(padx=20, pady=(2, 10))

        def cambiar():
            token_ingresado = token_entry.get().strip()
            nueva = password_entry.get()
            confirmar = confirm_entry.get()

            if token_ingresado != token:
                messagebox.showerror("Error", "Token inválido.")
                return
            if nueva != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return
            try:
                query = """
                    SELECT * FROM password_reset_tokens
                    WHERE token = %s AND used_at IS NULL AND expires_at > %s;
                """
                with self.main_controller.db_connection.get_cursor(dictionary=True) as cursor:
                    cursor.execute(query, (token_ingresado, datetime.now()))
                    token_record = cursor.fetchone()

                if not token_record:
                    messagebox.showerror("Error", "Token expirado o ya utilizado.")
                    return

                self.auth_service.validar_nueva_contrasena(user_id, nueva)
                new_hash = self.auth_service.hashear_contrasena(nueva)

                user = self.main_controller.user_repo.get_by_id(user_id)
                user.password_hash = new_hash
                self.main_controller.user_repo.update(user)

                query_update = """
                    UPDATE password_reset_tokens SET used_at = %s WHERE token = %s;
                """
                with self.main_controller.db_connection.get_cursor() as cursor:
                    cursor.execute(query_update, (datetime.now(), token_ingresado))
                    self.main_controller.db_connection.connection.commit()

                messagebox.showinfo("Éxito", "Contraseña actualizada correctamente.")
                self.auth_service.limpiar_bloqueos_diarios(user_id)
                dialog.destroy()

            except ValueError as e:
                messagebox.showerror("Error", str(e))
            except Exception as e:
                messagebox.showerror("Error Inesperado", str(e))

        ctk.CTkButton(dialog, text="Cambiar Contraseña", fg_color="#4ecca3",
                      text_color="#1a1a2e", hover_color="#3db892", command=cambiar).pack(pady=15)