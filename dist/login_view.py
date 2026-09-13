import customtkinter as ctk
from tkinter import messagebox
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from main_controller import MainController

class LoginView(ctk.CTkFrame):
    def __init__(self, parent_frame: ctk.CTkFrame, controller: 'MainController'):
        super().__init__(parent_frame, fg_color="transparent")
        self.controller = controller

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self._create_widgets()

    def _create_widgets(self) -> None:
        login_frame = ctk.CTkFrame(self, fg_color="#16213e", corner_radius=15)
        login_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        login_frame.grid_columnconfigure(0, weight=1)
        login_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(login_frame, text="Iniciar Sesión", font=ctk.CTkFont(size=28, weight="bold"), text_color="#ffffff").grid(row=0, column=0, columnspan=2, pady=20)

        ctk.CTkLabel(login_frame, text="Correo Electrónico:", text_color="#a0a0a0").grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.email_entry = ctk.CTkEntry(login_frame, width=300, placeholder_text="tu@ejemplo.com")
        self.email_entry.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(login_frame, text="Contraseña:", text_color="#a0a0a0").grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.password_entry = ctk.CTkEntry(login_frame, width=300, show="*", placeholder_text="********")
        self.password_entry.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

        login_button = ctk.CTkButton(login_frame, text="Entrar", command=self._handle_login, font=ctk.CTkFont(size=16, weight="bold"), fg_color="#4ecca3", text_color="#1a1a2e", hover_color="#3db892", height=40)
        login_button.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")

    def _handle_login(self) -> None:
        email = self.email_entry.get()
        password = self.password_entry.get()
        self.controller.auth_controller.login(email, password)

    def clear_fields(self) -> None:
        self.email_entry.delete(0, ctk.END)
        self.password_entry.delete(0, ctk.END)