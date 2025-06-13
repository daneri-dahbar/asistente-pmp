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
        self.current_session = None
        self.sessions_list = []
        
        # Contenedores principales
        self.chat_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
            spacing=5
        )
        
        # Lista de conversaciones (sidebar)
        self.conversations_list = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            spacing=5,
            width=250
        )
        
        # Campo de entrada de mensajes
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
        
        # Botón de envío
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
        
        # Texto de estado
        self.status_text = ft.Text(
            "Inicializando...",
            size=12,
            color=ft.Colors.GREY_600
        )
        
        # Estado de la aplicación
        self.is_sending = False
        self.page = None
        self.sidebar_visible = True
    
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
                    
                    # Establecer sesión actual
                    self.current_session = self.chatbot.current_session
                    
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
        
        # Cargar lista de conversaciones
        self.load_conversations_list()
        
        # Cargar historial de la conversación actual
        history = self.chatbot.get_conversation_history()
        self.chat_container.controls.clear()
        for role, content in history:
            is_user = role == "user"
            message_widget = create_chat_message(content, is_user)
            self.chat_container.controls.append(message_widget)
    
    def load_conversations_list(self):
        """
        Carga la lista de conversaciones del usuario en el sidebar.
        """
        if not self.chatbot:
            return
        
        try:
            # Obtener sesiones del usuario
            self.sessions_list = self.chatbot.db_manager.get_user_sessions(self.user.id)
            self.conversations_list.controls.clear()
            
            # Agregar cada conversación a la lista
            for session in self.sessions_list:
                conversation_item = self.create_conversation_item(session)
                self.conversations_list.controls.append(conversation_item)
            
            if self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error al cargar conversaciones: {e}")
    
    def create_conversation_item(self, session):
        """
        Crea un elemento de conversación para el sidebar.
        """
        try:
            is_current = self.current_session and session.id == self.current_session.id
            
            # Obtener preview del último mensaje
            try:
                messages = self.chatbot.db_manager.get_session_messages(session.id)
                if messages:
                    last_message = messages[-1][1]  # content del último mensaje
                    preview = last_message[:50] + "..." if len(last_message) > 50 else last_message
                else:
                    preview = "Nueva conversación"
            except:
                preview = "Nueva conversación"
        
            # Contenedor de la conversación
            conversation_container = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Text(
                                    session.name,
                                    size=14,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE if is_current else ft.Colors.BLACK87,
                                    expand=True
                                ),
                                ft.Row(
                                    controls=[
                                        ft.IconButton(
                                            icon=ft.Icons.EDIT,
                                            icon_size=16,
                                            icon_color=ft.Colors.WHITE if is_current else ft.Colors.GREY_600,
                                            tooltip="Renombrar",
                                            on_click=lambda e, s=session: self.show_rename_dialog(s)
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_size=16,
                                            icon_color=ft.Colors.WHITE if is_current else ft.Colors.GREY_600,
                                            tooltip="Eliminar",
                                            on_click=lambda e, s=session: self.show_delete_dialog(s)
                                        )
                                    ],
                                    spacing=0
                                )
                            ]
                        ),
                        ft.Text(
                            preview,
                            size=11,
                            color=ft.Colors.WHITE70 if is_current else ft.Colors.GREY_600,
                            overflow=ft.TextOverflow.ELLIPSIS
                        )
                    ],
                    spacing=2
                ),
                padding=ft.padding.all(10),
                margin=ft.margin.symmetric(0, 2),
                bgcolor=ft.Colors.BLUE_600 if is_current else ft.Colors.TRANSPARENT,
                border_radius=8,
                on_click=lambda e, s=session: self.switch_conversation(s),
                ink=True
            )
            
            return conversation_container
            
        except Exception as e:
            print(f"Error al crear elemento de conversación: {e}")
            # Retornar un elemento básico en caso de error
            return ft.Container(
                content=ft.Text(
                    session.name if hasattr(session, 'name') else "Conversación",
                    size=14
                ),
                padding=ft.padding.all(10),
                margin=ft.margin.symmetric(0, 2),
                on_click=lambda e, s=session: self.switch_conversation(s)
            )
    
    def switch_conversation(self, session):
        """
        Cambia a una conversación diferente.
        """
        if self.is_sending:
            return
        
        try:
            self.current_session = session
            self.chatbot.current_session = session
            self.chatbot._load_conversation_history()
            
            # Recargar la interfaz
            self.load_conversation_history()
            
            if self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error al cambiar conversación: {e}")
    
    def create_menu_items(self, session):
        """
        Crea los elementos del menú contextual para una conversación.
        """
        def on_rename_click(e):
            print(f"Renombrar clicked para sesión: {session.id}")
            self.show_rename_dialog(session)
        
        def on_delete_click(e):
            print(f"Eliminar clicked para sesión: {session.id}")
            self.show_delete_dialog(session)
        
        return [
            ft.PopupMenuItem(
                text="Renombrar",
                icon=ft.Icons.EDIT,
                on_click=on_rename_click
            ),
            ft.PopupMenuItem(
                text="Eliminar",
                icon=ft.Icons.DELETE,
                on_click=on_delete_click
            )
        ]
    
    def create_rename_handler(self, session):
        """
        Crea un handler para renombrar una conversación específica.
        """
        def handler(e):
            self.show_rename_dialog(session)
        return handler
    
    def create_delete_handler(self, session):
        """
        Crea un handler para eliminar una conversación específica.
        """
        def handler(e):
            self.show_delete_dialog(session)
        return handler
    
    def show_rename_dialog(self, session):
        """
        Muestra un diálogo personalizado para renombrar una conversación.
        """
        print(f"Mostrando diálogo de renombrar para: {session.name}")
        
        # Crear el campo de texto
        name_field = ft.TextField(
            value=session.name,
            label="Nuevo nombre",
            width=300,
            autofocus=True
        )
        
        def on_save(e):
            print(f"Guardando nuevo nombre: {name_field.value}")
            new_name = name_field.value.strip()
            if new_name and new_name != session.name:
                try:
                    # Actualizar en base de datos
                    with self.chatbot.db_manager.get_session() as db:
                        from db.models import ChatSession
                        
                        db_session = db.query(ChatSession).filter(
                            ChatSession.id == session.id
                        ).first()
                        if db_session:
                            db_session.name = new_name
                            db.commit()
                            print(f"Nombre actualizado en BD: {new_name}")
                    
                    # Actualizar en memoria
                    session.name = new_name
                    
                    # Recargar lista
                    self.load_conversations_list()
                    print("Lista de conversaciones recargada")
                    
                except Exception as error:
                    print(f"Error al actualizar nombre: {error}")
            
            # Cerrar diálogo personalizado
            self.close_custom_dialog()
            print("Diálogo cerrado")
        
        def on_cancel(e):
            print("Cancelando renombrar")
            self.close_custom_dialog()
        
        # Crear diálogo personalizado usando Container
        dialog_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Renombrar Conversación", size=20, weight=ft.FontWeight.BOLD),
                    ft.Divider(),
                    name_field,
                    ft.Row(
                        controls=[
                            ft.TextButton("Cancelar", on_click=on_cancel),
                            ft.ElevatedButton("Guardar", on_click=on_save)
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=15,
                tight=True
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 4)
            ),
            width=400
        )
        
        # Overlay para el fondo
        overlay = ft.Container(
            content=ft.Stack(
                controls=[
                    # Fondo semi-transparente
                    ft.Container(
                        bgcolor=ft.Colors.BLACK54,
                        expand=True,
                        on_click=on_cancel  # Cerrar al hacer clic fuera
                    ),
                    # Diálogo centrado
                    ft.Container(
                        content=dialog_content,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ]
            ),
            expand=True
        )
        
        # Mostrar el diálogo personalizado
        self.show_custom_dialog(overlay)
        print("Diálogo personalizado mostrado")
    
    def show_custom_dialog(self, dialog_overlay):
        """
        Muestra un diálogo personalizado.
        """
        # Guardar el contenido actual de la página
        self.original_page_content = self.page.controls.copy()
        
        # Limpiar la página y mostrar el diálogo
        self.page.controls.clear()
        self.page.controls.append(dialog_overlay)
        self.page.update()
    
    def close_custom_dialog(self):
        """
        Cierra el diálogo personalizado y restaura el contenido original.
        """
        if hasattr(self, 'original_page_content'):
            self.page.controls.clear()
            self.page.controls.extend(self.original_page_content)
            self.page.update()
    
    def close_dialog(self):
        """
        Método auxiliar para cerrar diálogos (mantenido para compatibilidad).
        """
        self.close_custom_dialog()
    
    def show_delete_dialog(self, session):
        """
        Muestra un diálogo personalizado para eliminar una conversación.
        """
        print(f"Mostrando diálogo de eliminar para: {session.name}")
        
        def on_delete(e):
            print(f"Eliminando conversación: {session.name}")
            try:
                # Eliminar de base de datos
                with self.chatbot.db_manager.get_session() as db:
                    from db.models import ChatMessage, ChatSession
                    
                    # Eliminar mensajes
                    db.query(ChatMessage).filter(
                        ChatMessage.session_id == session.id
                    ).delete()
                    
                    # Eliminar sesión
                    db.query(ChatSession).filter(
                        ChatSession.id == session.id
                    ).delete()
                    
                    db.commit()
                    print("Conversación eliminada de la BD")
                
                # Si era la conversación actual, crear una nueva
                if self.current_session and self.current_session.id == session.id:
                    self.new_conversation(None)
                    print("Era la conversación actual, creando nueva")
                else:
                    # Solo recargar la lista
                    self.load_conversations_list()
                    print("Recargando lista de conversaciones")
                
            except Exception as error:
                print(f"Error al eliminar conversación: {error}")
            
            # Cerrar diálogo personalizado
            self.close_custom_dialog()
            print("Diálogo de eliminar cerrado")
        
        def on_cancel(e):
            print("Cancelando eliminación")
            self.close_custom_dialog()
        
        # Crear diálogo personalizado usando Container
        dialog_content = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text("Eliminar Conversación", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.RED_600),
                    ft.Divider(),
                    ft.Text(
                        f"¿Estás seguro de que quieres eliminar '{session.name}'?",
                        size=16
                    ),
                    ft.Text(
                        "Esta acción no se puede deshacer.",
                        size=14,
                        color=ft.Colors.GREY_600,
                        italic=True
                    ),
                    ft.Row(
                        controls=[
                            ft.TextButton("Cancelar", on_click=on_cancel),
                            ft.ElevatedButton(
                                "Eliminar", 
                                on_click=on_delete,
                                style=ft.ButtonStyle(bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE)
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=15,
                tight=True
            ),
            padding=20,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=15,
                color=ft.Colors.BLACK26,
                offset=ft.Offset(0, 4)
            ),
            width=400
        )
        
        # Overlay para el fondo
        overlay = ft.Container(
            content=ft.Stack(
                controls=[
                    # Fondo semi-transparente
                    ft.Container(
                        bgcolor=ft.Colors.BLACK54,
                        expand=True,
                        on_click=on_cancel  # Cerrar al hacer clic fuera
                    ),
                    # Diálogo centrado
                    ft.Container(
                        content=dialog_content,
                        alignment=ft.alignment.center,
                        expand=True
                    )
                ]
            ),
            expand=True
        )
        
        # Mostrar el diálogo personalizado
        self.show_custom_dialog(overlay)
        print("Diálogo de eliminar personalizado mostrado")
    
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
                
                # Actualizar lista de conversaciones (para mostrar el nuevo mensaje)
                self.load_conversations_list()
                
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
            self.current_session = self.chatbot.current_session
            self.chat_container.controls.clear()
            
            # Recargar lista de conversaciones
            self.load_conversations_list()
            
            if self.page:
                self.page.update()
    
    def toggle_sidebar(self, e):
        """
        Alterna la visibilidad del sidebar de conversaciones.
        """
        self.sidebar_visible = not self.sidebar_visible
        
        # Reconstruir la interfaz completa
        self.page.controls.clear()
        
        # Barra superior
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.MENU,
                                tooltip="Alternar conversaciones",
                                icon_color=ft.Colors.WHITE,
                                on_click=self.toggle_sidebar
                            ),
                            ft.Text(
                                "🤖 ChatGPT Assistant",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            )
                        ],
                        spacing=10
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
        
        # Construir layout principal
        content = self.build_layout()
        
        # Layout principal
        main_layout = ft.Column(
            controls=[
                header,
                content
            ],
            spacing=0,
            expand=True
        )
        
        self.page.add(main_layout)
        self.page.update()
    
    def build_layout(self):
        """
        Construye el layout principal con o sin sidebar.
        """
        # Área de chat principal
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
        
        # Área principal de chat
        main_chat_area = ft.Column(
            controls=[
                chat_area,
                input_area
            ],
            spacing=0,
            expand=True
        )
        
        if self.sidebar_visible:
            # Layout con sidebar
            content = ft.Row(
                controls=[
                    # Sidebar de conversaciones
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                # Header del sidebar
                                ft.Container(
                                    content=ft.Row(
                                        controls=[
                                            ft.Text(
                                                "Conversaciones",
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.WHITE
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.ADD,
                                                tooltip="Nueva conversación",
                                                icon_color=ft.Colors.WHITE,
                                                icon_size=20,
                                                on_click=self.new_conversation
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    padding=ft.padding.all(15),
                                    bgcolor=ft.Colors.BLUE_700
                                ),
                                # Lista de conversaciones
                                ft.Container(
                                    content=self.conversations_list,
                                    padding=ft.padding.all(10),
                                    expand=True
                                )
                            ],
                            spacing=0
                        ),
                        width=280,
                        bgcolor=ft.Colors.GREY_50,
                        border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_300))
                    ),
                    # Área principal de chat
                    main_chat_area
                ],
                spacing=0,
                expand=True
            )
        else:
            # Layout sin sidebar
            content = main_chat_area
        
        return content
    
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
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.MENU,
                                tooltip="Alternar conversaciones",
                                icon_color=ft.Colors.WHITE,
                                on_click=self.toggle_sidebar
                            ),
                            ft.Text(
                                "🤖 ChatGPT Assistant",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            )
                        ],
                        spacing=10
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
        
        # Construir layout principal
        content = self.build_layout()
        
        # Layout principal
        main_layout = ft.Column(
            controls=[
                header,
                content
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