"""
Interfaz de usuario para la aplicación de chat usando Flet.
Implementa un diseño moderno y responsivo estilo ChatGPT.
"""

import flet as ft
from typing import List, Tuple
from chatbot import ChatBot
from db.models import User
import threading
import time

def create_chat_message(message: str, is_user: bool):
    """
    Función para crear mensajes individuales del chat.
    """
    # Configurar colores y alineación según el remitente
    if is_user:
        bg_color = ft.Colors.BLUE_600
        text_color = ft.Colors.WHITE
        alignment = ft.MainAxisAlignment.END
        margin = ft.margin.only(left=50, bottom=10)
    else:
        bg_color = ft.Colors.GREY_100
        text_color = ft.Colors.BLACK87
        alignment = ft.MainAxisAlignment.START
        margin = ft.margin.only(right=50, bottom=10)
    
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(
                    message,
                    color=text_color,
                    size=14,
                    selectable=True
                ),
                padding=ft.padding.all(12),
                margin=margin,
                bgcolor=bg_color,
                border_radius=12,
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=4,
                    color=ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2)
                )
            )
        ],
        alignment=alignment
    )

class ChatUI:
    """
    Clase principal para la interfaz de usuario del chat.
    """
    
    def __init__(self, user: User):
        self.user = user
        self.chatbot = None
        self.on_logout_callback = None  # Callback para logout
        self.chat_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
            spacing=5
        )
        self.message_input = ft.TextField(
            hint_text="Escribe tu mensaje aquí...",
            multiline=True,
            min_lines=1,
            max_lines=5,
            filled=True,
            border_radius=25,
            content_padding=ft.padding.symmetric(15, 10),
            on_submit=self.send_message
        )
        self.send_button = ft.IconButton(
            icon=ft.Icons.SEND,
            tooltip="Enviar mensaje",
            on_click=self.send_message,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_600,
                shape=ft.CircleBorder()
            )
        )
        self.status_text = ft.Text(
            "Inicializando...",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # Estado de la aplicación
        self.is_sending = False
        self.page = None
    
    def initialize_chatbot(self, page: ft.Page):
        """
        Inicializa el chatbot en un hilo separado para no bloquear la UI.
        """
        self.page = page
        
        def init_bot():
            try:
                self.chatbot = ChatBot(self.user.id)
                if self.chatbot.is_api_key_valid():
                    self.status_text.value = f"✅ Conectado como {self.user.username} - Listo para chatear"
                    self.status_text.color = ft.Colors.GREEN_600
                    
                    # Cargar historial existente
                    self.load_conversation_history()
                else:
                    self.status_text.value = "❌ API Key no configurada"
                    self.status_text.color = ft.Colors.RED_600
                    
            except Exception as e:
                self.status_text.value = f"❌ Error: {str(e)}"
                self.status_text.color = ft.Colors.RED_600
            
            page.update()
        
        threading.Thread(target=init_bot, daemon=True).start()
    
    def load_conversation_history(self):
        """
        Carga el historial de conversación existente en la UI.
        """
        if not self.chatbot:
            return
        
        history = self.chatbot.get_conversation_history()
        for role, content in history:
            is_user = role == "user"
            message_widget = create_chat_message(content, is_user)
            self.chat_container.controls.append(message_widget)
    
    def send_message(self, e=None):
        """
        Maneja el envío de mensajes del usuario.
        """
        if self.is_sending or not self.message_input.value.strip():
            return
        
        if not self.chatbot or not self.chatbot.is_api_key_valid():
            self.show_error_message("Por favor configura tu API Key de OpenAI")
            return
        
        user_message = self.message_input.value.strip()
        self.message_input.value = ""
        
        # Mostrar mensaje del usuario inmediatamente
        user_message_widget = create_chat_message(user_message, True)
        self.chat_container.controls.append(user_message_widget)
        
        # Mostrar indicador de escritura
        typing_indicator = self.create_typing_indicator()
        self.chat_container.controls.append(typing_indicator)
        
        self.is_sending = True
        self.send_button.disabled = True
        self.message_input.disabled = True
        
        e.page.update()
        
        # Enviar mensaje en hilo separado
        def send_async():
            try:
                response = self.chatbot.send_message(user_message)
                
                # Remover indicador de escritura
                self.chat_container.controls.remove(typing_indicator)
                
                # Mostrar respuesta de la IA
                ai_message_widget = create_chat_message(response, False)
                self.chat_container.controls.append(ai_message_widget)
                
            except Exception as error:
                # Remover indicador de escritura
                if typing_indicator in self.chat_container.controls:
                    self.chat_container.controls.remove(typing_indicator)
                
                self.show_error_message(f"Error: {str(error)}")
            
            finally:
                self.is_sending = False
                self.send_button.disabled = False
                self.message_input.disabled = False
                e.page.update()
        
        threading.Thread(target=send_async, daemon=True).start()
    
    def create_typing_indicator(self):
        """
        Crea un indicador visual de que la IA está escribiendo.
        """
        return ft.Row(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("IA está escribiendo"),
                            ft.ProgressRing(width=16, height=16, stroke_width=2)
                        ],
                        spacing=10
                    ),
                    padding=ft.padding.all(12),
                    margin=ft.margin.only(right=50, bottom=10),
                    bgcolor=ft.Colors.GREY_100,
                    border_radius=12,
                )
            ],
            alignment=ft.MainAxisAlignment.START
        )
    
    def show_error_message(self, error_text: str):
        """
        Muestra un mensaje de error en el chat.
        """
        error_widget = ft.Container(
            content=ft.Text(
                error_text,
                color=ft.Colors.RED_600,
                size=12
            ),
            padding=ft.padding.all(10),
            margin=ft.margin.only(bottom=10),
            bgcolor=ft.Colors.RED_50,
            border_radius=8,
            border=ft.border.all(1, ft.Colors.RED_200)
        )
        self.chat_container.controls.append(error_widget)
    
    def new_conversation(self, e):
        """
        Inicia una nueva conversación.
        """
        if self.chatbot:
            self.chatbot.start_new_conversation()
            self.chat_container.controls.clear()
            e.page.update()
    
    def logout(self, e):
        """
        Cierra la sesión del usuario actual y regresa a la pantalla de login.
        """
        if self.on_logout_callback:
            self.on_logout_callback()
    
    def build_ui(self, page: ft.Page):
        """
        Construye la interfaz de usuario principal.
        """
        self.page = page
        
        # Barra superior
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        "🤖 ChatGPT Assistant",
                        size=18,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE
                    ),
                    ft.Row(
                        controls=[
                            ft.Text(
                                f"👤 {self.user.username}",
                                size=14,
                                color=ft.Colors.WHITE70
                            ),
                            ft.IconButton(
                                icon=ft.Icons.ADD_COMMENT,
                                tooltip="Nueva conversación",
                                icon_color=ft.Colors.WHITE,
                                on_click=self.new_conversation
                            ),
                            ft.IconButton(
                                icon=ft.Icons.LOGOUT,
                                tooltip="Cerrar sesión",
                                icon_color=ft.Colors.WHITE,
                                on_click=self.logout
                            )
                        ],
                        spacing=5
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN
            ),
            bgcolor=ft.Colors.BLUE_700,
            padding=ft.padding.symmetric(20, 15),
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=4,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 2)
            )
        )
        
        # Área de chat
        chat_area = ft.Container(
            content=self.chat_container,
            padding=ft.padding.all(20),
            expand=True,
            bgcolor=ft.Colors.WHITE
        )
        
        # Área de entrada de mensajes
        input_area = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Divider(height=1, color=ft.Colors.GREY_300),
                    ft.Row(
                        controls=[
                            self.status_text
                        ],
                        alignment=ft.MainAxisAlignment.CENTER
                    ),
                    ft.Row(
                        controls=[
                            ft.Container(
                                content=self.message_input,
                                expand=True
                            ),
                            self.send_button
                        ],
                        spacing=10
                    )
                ],
                spacing=10
            ),
            padding=ft.padding.all(20),
            bgcolor=ft.Colors.GREY_50
        )
        
        # Layout principal
        main_layout = ft.Column(
            controls=[
                header,
                chat_area,
                input_area
            ],
            spacing=0,
            expand=True
        )
        
        page.add(main_layout)
        
        # Inicializar chatbot
        self.initialize_chatbot(page)
        
        # Enfocar el campo de entrada
        self.message_input.focus()

def create_app(user: User):
    """
    Función para crear y configurar la aplicación de chat.
    """
    def main(page: ft.Page):
        chat_ui = ChatUI(user)
        chat_ui.build_ui(page)
    
    return main 