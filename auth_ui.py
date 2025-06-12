"""
Interfaz de autenticación para la aplicación de chat.
Implementa pantallas de login y registro con validación.
"""

import flet as ft
from auth import AuthManager
import threading
import time

class AuthUI:
    """
    Clase para manejar la interfaz de autenticación.
    """
    
    def __init__(self, on_auth_success):
        self.auth_manager = AuthManager()
        self.on_auth_success = on_auth_success  # Callback cuando la autenticación es exitosa
        self.page = None
        
        # Estado de la UI
        self.is_login_mode = True
        self.is_processing = False
        
        # Controles del formulario
        self.username_field = ft.TextField(
            label="Usuario",
            prefix_icon=ft.Icons.PERSON,
            border_radius=10,
            filled=True,
            width=300
        )
        
        self.email_field = ft.TextField(
            label="Email",
            prefix_icon=ft.Icons.EMAIL,
            border_radius=10,
            filled=True,
            width=300,
            visible=False  # Solo visible en registro
        )
        
        self.password_field = ft.TextField(
            label="Contraseña",
            prefix_icon=ft.Icons.LOCK,
            password=True,
            can_reveal_password=True,
            border_radius=10,
            filled=True,
            width=300,
            on_change=self.on_password_change
        )
        
        self.confirm_password_field = ft.TextField(
            label="Confirmar Contraseña",
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            border_radius=10,
            filled=True,
            width=300,
            visible=False  # Solo visible en registro
        )
        
        # Indicador de fortaleza de contraseña
        self.password_strength = ft.Text(
            "",
            size=12,
            visible=False
        )
        
        # Botones
        self.submit_button = ft.ElevatedButton(
            text="Iniciar Sesión",
            width=300,
            height=45,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=10),
                bgcolor=ft.Colors.BLUE_600,
                color=ft.Colors.WHITE
            ),
            on_click=self.on_submit
        )
        
        self.toggle_button = ft.TextButton(
            text="¿No tienes cuenta? Regístrate",
            on_click=self.toggle_mode
        )
        
        # Mensaje de estado
        self.status_text = ft.Text(
            "",
            color=ft.Colors.RED_600,
            size=12,
            text_align=ft.TextAlign.CENTER,
            width=300
        )
        
        # Indicador de carga
        self.loading_indicator = ft.ProgressRing(
            width=20,
            height=20,
            visible=False
        )
    
    def on_password_change(self, e):
        """Maneja el cambio en el campo de contraseña para mostrar fortaleza"""
        if not self.is_login_mode and self.password_field.value:
            strength, description = self.auth_manager.get_password_strength(self.password_field.value)
            color = {
                "Débil": ft.Colors.RED_600,
                "Media": ft.Colors.ORANGE_600,
                "Fuerte": ft.Colors.GREEN_600,
                "Muy fuerte": ft.Colors.GREEN_800
            }.get(strength, ft.Colors.GREY_600)
            
            self.password_strength.value = f"Fortaleza: {strength} - {description}"
            self.password_strength.color = color
            self.password_strength.visible = True
        else:
            self.password_strength.visible = False
        
        self.page.update()
    
    def toggle_mode(self, e):
        """Cambia entre modo login y registro"""
        self.is_login_mode = not self.is_login_mode
        
        if self.is_login_mode:
            # Modo Login
            self.submit_button.text = "Iniciar Sesión"
            self.toggle_button.text = "¿No tienes cuenta? Regístrate"
            self.email_field.visible = False
            self.confirm_password_field.visible = False
            self.password_strength.visible = False
        else:
            # Modo Registro
            self.submit_button.text = "Registrarse"
            self.toggle_button.text = "¿Ya tienes cuenta? Inicia sesión"
            self.email_field.visible = True
            self.confirm_password_field.visible = True
        
        # Limpiar campos y mensajes
        self.clear_fields()
        self.page.update()
    
    def clear_fields(self):
        """Limpia todos los campos del formulario"""
        self.username_field.value = ""
        self.email_field.value = ""
        self.password_field.value = ""
        self.confirm_password_field.value = ""
        self.status_text.value = ""
        self.password_strength.visible = False
    
    def on_submit(self, e):
        """Maneja el envío del formulario"""
        if self.is_processing:
            return
        
        self.is_processing = True
        self.submit_button.disabled = True
        self.loading_indicator.visible = True
        self.status_text.value = ""
        self.page.update()
        
        # Ejecutar autenticación en hilo separado
        def process_auth():
            try:
                if self.is_login_mode:
                    success, message = self.auth_manager.login_user(
                        self.username_field.value,
                        self.password_field.value
                    )
                else:
                    success, message = self.auth_manager.register_user(
                        self.username_field.value,
                        self.email_field.value,
                        self.password_field.value,
                        self.confirm_password_field.value
                    )
                
                # Actualizar UI en el hilo principal
                def update_ui():
                    self.status_text.value = message
                    self.status_text.color = ft.Colors.GREEN_600 if success else ft.Colors.RED_600
                    
                    if success:
                        if self.is_login_mode:
                            # Login exitoso - llamar callback
                            time.sleep(0.5)  # Breve pausa para mostrar el mensaje
                            self.on_auth_success(self.auth_manager.get_current_user())
                        else:
                            # Registro exitoso - cambiar a modo login
                            time.sleep(1)
                            self.is_login_mode = True
                            self.toggle_mode(None)
                    
                    self.is_processing = False
                    self.submit_button.disabled = False
                    self.loading_indicator.visible = False
                    self.page.update()
                
                # Ejecutar actualización de UI en el hilo principal
                self.page.run_thread(update_ui)
                
            except Exception as error:
                def show_error():
                    self.status_text.value = f"Error: {str(error)}"
                    self.status_text.color = ft.Colors.RED_600
                    self.is_processing = False
                    self.submit_button.disabled = False
                    self.loading_indicator.visible = False
                    self.page.update()
                
                self.page.run_thread(show_error)
        
        threading.Thread(target=process_auth, daemon=True).start()
    
    def build_ui(self, page: ft.Page):
        """Construye la interfaz de autenticación"""
        self.page = page
        
        # Configurar navegación por teclado
        self.username_field.on_submit = lambda e: self.email_field.focus() if not self.is_login_mode else self.password_field.focus()
        self.email_field.on_submit = lambda e: self.password_field.focus()
        self.password_field.on_submit = lambda e: self.confirm_password_field.focus() if not self.is_login_mode else self.on_submit(e)
        self.confirm_password_field.on_submit = self.on_submit
        
        # Header
        header = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.Icons.CHAT_BUBBLE_OUTLINE,
                        size=60,
                        color=ft.Colors.BLUE_600
                    ),
                    ft.Text(
                        "ChatGPT Assistant",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER
                    ),
                    ft.Text(
                        "Inicia sesión para comenzar",
                        size=14,
                        color=ft.Colors.GREY_600,
                        text_align=ft.TextAlign.CENTER
                    )
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10
            ),
            padding=ft.padding.all(40),
            alignment=ft.alignment.center
        )
        
        # Formulario
        form = ft.Container(
            content=ft.Column(
                controls=[
                    self.username_field,
                    self.email_field,
                    self.password_field,
                    self.password_strength,
                    self.confirm_password_field,
                    ft.Container(height=10),  # Espaciado
                    self.status_text,
                    ft.Row(
                        controls=[
                            self.submit_button,
                            self.loading_indicator
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                        spacing=10
                    ),
                    ft.Container(height=10),  # Espaciado
                    self.toggle_button
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            ),
            padding=ft.padding.symmetric(20, 0),
            alignment=ft.alignment.center
        )
        
        # Layout principal
        main_layout = ft.Column(
            controls=[
                header,
                form
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True
        )
        
        # Contenedor principal con gradiente de fondo
        main_container = ft.Container(
            content=main_layout,
            gradient=ft.LinearGradient(
                begin=ft.alignment.top_center,
                end=ft.alignment.bottom_center,
                colors=[ft.Colors.BLUE_50, ft.Colors.WHITE]
            ),
            expand=True
        )
        
        page.add(main_container)
        
        # Enfocar el campo de usuario
        self.username_field.focus()

def create_auth_app(on_auth_success):
    """
    Función para crear la aplicación de autenticación.
    """
    def main(page: ft.Page):
        auth_ui = AuthUI(on_auth_success)
        auth_ui.build_ui(page)
    
    return main 