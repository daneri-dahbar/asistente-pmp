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
import datetime

def create_chat_message(message: str, is_user: bool):
    """
    Función para crear mensajes individuales del chat con estilo Slack/Discord.
    """
    # Obtener timestamp actual
    timestamp = datetime.datetime.now().strftime("%H:%M")
    
    # Configurar avatar y nombre según el remitente
    if is_user:
        avatar_icon = ft.Icons.PERSON
        avatar_color = ft.Colors.BLUE_600
        username = "Tú"
        username_color = ft.Colors.BLUE_700
    else:
        avatar_icon = ft.Icons.SMART_TOY
        avatar_color = ft.Colors.GREEN_600
        username = "PMP Assistant"
        username_color = ft.Colors.GREEN_700
    
    # Avatar circular
    avatar = ft.Container(
        content=ft.Icon(
            avatar_icon,
            size=20,
            color=ft.Colors.WHITE
        ),
        width=36,
        height=36,
        bgcolor=avatar_color,
        border_radius=18,
        alignment=ft.alignment.center
    )
    
    # Header con nombre de usuario y timestamp
    header = ft.Row(
        controls=[
            ft.Text(
                username,
                size=14,
                weight=ft.FontWeight.BOLD,
                color=username_color
            ),
            ft.Text(
                timestamp,
                size=12,
                color=ft.Colors.GREY_500
            )
        ],
        spacing=8,
        tight=True
    )
    
    # Contenido del mensaje con ajuste automático de línea
    if is_user:
        message_content = ft.Text(
            message,
            size=14,
            color=ft.Colors.GREY_800,
            selectable=True,
            no_wrap=False,  # Permitir salto de línea automático
            expand=True     # Expandir para usar todo el ancho disponible
        )
    else:
        message_content = ft.Markdown(
            message,
            selectable=True,
            expand=True     # Expandir para usar todo el ancho disponible
        )
    
    # Columna con header y contenido
    content_column = ft.Column(
        controls=[header, message_content],
        spacing=4,
        tight=True,
        expand=True  # Expandir para usar todo el ancho disponible
    )
    
    # Row principal con avatar y contenido
    message_row = ft.Row(
        controls=[
            avatar,
            content_column
        ],
        spacing=12,
        vertical_alignment=ft.CrossAxisAlignment.START,
        expand=True  # Expandir para usar todo el ancho disponible
    )
    
    # Contenedor principal con hover effect
    return ft.Container(
        content=message_row,
        padding=ft.padding.symmetric(horizontal=16, vertical=8),
        margin=ft.margin.only(bottom=2),
        bgcolor=ft.Colors.TRANSPARENT,
        border_radius=4,
        on_hover=lambda e: setattr(e.control, 'bgcolor', 
                                  ft.Colors.GREY_50 if e.data == "true" else ft.Colors.TRANSPARENT) or e.page.update(),
        expand=True,  # Expandir para usar todo el ancho disponible
        width=None    # Sin ancho fijo para permitir responsividad completa
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
        
        # Estado de navegación
        self.current_mode = None  # Modo actual: no iniciamos con ningún modo específico
        
        # Contenedores principales
        self.chat_container = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            auto_scroll=True,
            spacing=5,
            expand=True,
            width=None,  # Se ajusta al contenedor padre
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH
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
                # Solo inicializar chatbot si hay un modo seleccionado
                if self.current_mode:
                    self.chatbot = ChatBot(self.user.id, self.current_mode)
                    if self.chatbot.is_api_key_valid():
                        self.status_text.value = f"✅ Conectado como {self.user.username}"
                        self.status_text.color = ft.Colors.GREEN_600
                        
                        # Establecer sesión actual
                        self.current_session = self.chatbot.current_session
                        
                        # Cargar historial existente
                        self.load_conversation_history()
                    else:
                        self.status_text.value = "❌ API Key no configurada"
                        self.status_text.color = ft.Colors.RED_600
                else:
                    # Sin modo seleccionado, mostrar mensaje de bienvenida general
                    self.status_text.value = f"✅ Conectado como {self.user.username} - Selecciona un modo para comenzar"
                    self.status_text.color = ft.Colors.GREEN_600
                    self.show_welcome_screen()
                    
            except Exception as e:
                self.status_text.value = f"❌ Error: {str(e)}"
                self.status_text.color = ft.Colors.RED_600
            
            page.update()
        
        threading.Thread(target=init_bot, daemon=True).start()
    
    def show_welcome_screen(self):
        """
        Muestra una pantalla de bienvenida general sin seleccionar ningún modo específico.
        """
        welcome_message = """¡Bienvenido al **Asistente PMP**! 👋

Soy tu tutor personal de IA especializado en **Project Management Professional (PMP)**. 

## 🎯 **Modos Disponibles:**

### **💬 CHARLEMOS** 
Chat libre y conversacional sobre cualquier tema PMP
- Preguntas abiertas y clarificaciones
- Explicaciones con analogías y ejemplos
- Discusión flexible de conceptos

### **📚 ESTUDIEMOS UN TEMA**
Sesiones de estudio estructuradas y guiadas
- Estudio por áreas específicas del PMBOK
- Metodología adaptativa según tu nivel
- Checkpoints y verificación de comprensión

### **📊 EVALUEMOS TU CONOCIMIENTO**
Evaluación diagnóstica y práctica dirigida
- Assessment completo de conocimientos
- Práctica por áreas débiles
- Feedback detallado con explicaciones

### **⏱️ SIMULEMOS UN EXAMEN**
Simulacros completos en condiciones reales
- Exámenes de práctica cronometrados
- Ambiente que replica el examen oficial
- Análisis post-examen detallado

### **🔍 ANALICEMOS CASOS**
Análisis profundo de casos prácticos
- Escenarios reales de gestión de proyectos
- Aplicación práctica de frameworks
- Desarrollo de pensamiento crítico

## ✨ **Para comenzar:**
**Selecciona un modo** usando el menú de navegación lateral o simplemente escribe qué tipo de ayuda necesitas.

¿Qué te gustaría hacer hoy?"""
        
        welcome_widget = create_chat_message(welcome_message, False)
        self.chat_container.controls.clear()
        self.chat_container.controls.append(welcome_widget)
        
        # Actualizar placeholder del input
        self.message_input.hint_text = "Selecciona un modo de estudio o simplemente escribe qué necesitas..."
        
        if self.page:
            self.page.update()
    
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
                
                # Si era la conversación actual, limpiar la interfaz
                if self.current_session and self.current_session.id == session.id:
                    self.current_session = None
                    self.chatbot.current_session = None
                    self.chat_container.controls.clear()
                    print("Conversación actual eliminada, interfaz limpiada")
                
                # Recargar la lista de conversaciones
                self.load_conversations_list()
                print("Lista de conversaciones recargada")
                
                # Actualizar la página
                if self.page:
                    self.page.update()
                
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
        
        # Si no hay modo seleccionado, mostrar mensaje informativo
        if not self.current_mode:
            self.show_error_message("Por favor selecciona un modo de estudio usando el menú de navegación lateral antes de enviar mensajes.")
            return
        
        if not self.chatbot or not self.chatbot.is_api_key_valid():
            self.show_error_message("Por favor configura tu API Key de OpenAI")
            return
        
        # Si no hay conversación activa, crear una nueva
        if not self.current_session:
            self.chatbot.start_new_conversation()
            self.current_session = self.chatbot.current_session
            print("Nueva conversación creada automáticamente al enviar mensaje")
        
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
        if not self.current_mode:
            self.show_error_message("Por favor selecciona un modo de estudio antes de crear una nueva conversación.")
            return
            
        if self.chatbot:
            self.chatbot.start_new_conversation()
            self.current_session = self.chatbot.current_session
            self.chat_container.controls.clear()
            
            # Mostrar mensaje de bienvenida según el modo
            if self.current_mode == "charlemos":
                self.update_charlemos_mode()
            elif self.current_mode == "estudiemos":
                self.update_estudiemos_mode()
            elif self.current_mode == "evaluemos":
                self.update_evaluemos_mode()
            elif self.current_mode == "simulemos":
                self.update_simulemos_mode()
            elif self.current_mode == "analicemos":
                self.update_analicemos_mode()
            
            # Recargar lista de conversaciones
            self.load_conversations_list()
            
            if self.page:
                self.page.update()
    
    def toggle_sidebar(self, e):
        """
        Alterna la visibilidad del sidebar de conversaciones.
        """
        self.sidebar_visible = not self.sidebar_visible
        if self.page:
            # Reconstruir el layout
            content = self.build_layout()
            
            # Encontrar el contenedor principal y actualizar su contenido
            main_layout = self.page.controls[0]  # El Column principal
            main_layout.controls[1] = content  # Reemplazar el contenido (índice 1 es el contenido después del header)
            
            self.page.update()
    
    def create_navigation_menu(self):
        """
        Crea el menú de navegación tab-based con indicadores de progreso y diseño moderno.
        """
        # Obtener progreso dinámico
        progress_data = self.calculate_progress_indicators()
        
        # Definir colores optimizados para modo oscuro
        dark_mode_colors = {
            "charlemos": {
                "primary": ft.Colors.LIGHT_BLUE_300,  # #4FC3F7 - Azul cyan suave
                "background": ft.Colors.BLUE_GREY_900,
                "text": ft.Colors.WHITE
            },
            "estudiemos": {
                "primary": ft.Colors.GREEN_300,  # #81C784 - Verde menta
                "background": ft.Colors.GREEN_900,
                "text": ft.Colors.WHITE
            },
            "evaluemos": {
                "primary": ft.Colors.ORANGE_300,  # #FFB74D - Naranja dorado
                "background": ft.Colors.ORANGE_900,
                "text": ft.Colors.WHITE
            },
            "simulemos": {
                "primary": ft.Colors.PINK_300,  # #F06292 - Rosa coral
                "background": ft.Colors.PINK_900,
                "text": ft.Colors.WHITE
            },
            "analicemos": {
                "primary": ft.Colors.PURPLE_300,  # #BA68C8 - Púrpura suave
                "background": ft.Colors.PURPLE_900,
                "text": ft.Colors.WHITE
            }
        }
        
        # Colores para modo claro (mantener los originales)
        light_mode_colors = {
            "charlemos": {
                "primary": ft.Colors.BLUE_600,
                "background": ft.Colors.BLUE_600,
                "text": ft.Colors.WHITE
            },
            "estudiemos": {
                "primary": ft.Colors.GREEN_600,
                "background": ft.Colors.GREEN_600,
                "text": ft.Colors.WHITE
            },
            "evaluemos": {
                "primary": ft.Colors.ORANGE_600,
                "background": ft.Colors.ORANGE_600,
                "text": ft.Colors.WHITE
            },
            "simulemos": {
                "primary": ft.Colors.RED_600,
                "background": ft.Colors.RED_600,
                "text": ft.Colors.WHITE
            },
            "analicemos": {
                "primary": ft.Colors.PURPLE_600,
                "background": ft.Colors.PURPLE_600,
                "text": ft.Colors.WHITE
            }
        }
        
        # Seleccionar paleta según el tema actual
        is_dark_mode = self.page.theme_mode == ft.ThemeMode.DARK
        color_scheme = dark_mode_colors if is_dark_mode else light_mode_colors
        
        menu_items = [
            {
                "key": "charlemos",
                "title": "CHARLEMOS",
                "subtitle": "Chat libre con tutor IA especializado",
                "icon": ft.Icons.CHAT_BUBBLE_OUTLINE,
                "color": color_scheme["charlemos"]["primary"],
                "bg_color": color_scheme["charlemos"]["background"],
                "text_color": color_scheme["charlemos"]["text"],
                "progress": progress_data["charlemos"]["progress"],
                "status": progress_data["charlemos"]["status"],
                "description": "Conversación abierta donde puedes hacer cualquier pregunta sobre PMP."
            },
            {
                "key": "estudiemos",
                "title": "ESTUDIEMOS",
                "subtitle": "Estudio estructurado por áreas",
                "icon": ft.Icons.SCHOOL_OUTLINED,
                "color": color_scheme["estudiemos"]["primary"],
                "bg_color": color_scheme["estudiemos"]["background"],
                "text_color": color_scheme["estudiemos"]["text"],
                "progress": progress_data["estudiemos"]["progress"],
                "status": progress_data["estudiemos"]["status"],
                "description": "Aprendizaje sistemático de temas específicos del PMBOK."
            },
            {
                "key": "evaluemos",
                "title": "EVALUEMOS",
                "subtitle": "Evaluación y práctica dirigida",
                "icon": ft.Icons.QUIZ_OUTLINED,
                "color": color_scheme["evaluemos"]["primary"],
                "bg_color": color_scheme["evaluemos"]["background"],
                "text_color": color_scheme["evaluemos"]["text"],
                "progress": progress_data["evaluemos"]["progress"],
                "status": progress_data["evaluemos"]["status"],
                "description": "Identifica fortalezas y debilidades con evaluaciones adaptativas."
            },
            {
                "key": "simulemos",
                "title": "SIMULEMOS",
                "subtitle": "Exámenes en condiciones reales",
                "icon": ft.Icons.TIMER_OUTLINED,
                "color": color_scheme["simulemos"]["primary"],
                "bg_color": color_scheme["simulemos"]["background"],
                "text_color": color_scheme["simulemos"]["text"],
                "progress": progress_data["simulemos"]["progress"],
                "status": progress_data["simulemos"]["status"],
                "description": "Práctica completa del examen PMP en condiciones reales."
            },
            {
                "key": "analicemos",
                "title": "ANALICEMOS",
                "subtitle": "Dashboard de progreso",
                "icon": ft.Icons.ANALYTICS_OUTLINED,
                "color": color_scheme["analicemos"]["primary"],
                "bg_color": color_scheme["analicemos"]["background"],
                "text_color": color_scheme["analicemos"]["text"],
                "progress": progress_data["analicemos"]["progress"],
                "status": progress_data["analicemos"]["status"],
                "description": "Vista comprehensiva del progreso de estudio y analytics."
            }
        ]
        
        menu_controls = []
        
        for item in menu_items:
            is_selected = self.current_mode == item["key"]
            
            # Crear indicador de progreso mejorado
            progress_bar_width = 180
            progress_fill_width = (item["progress"] / 100) * progress_bar_width
            progress_remaining_width = progress_bar_width - progress_fill_width
            
            progress_indicator = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    width=progress_fill_width,
                                    height=4,
                                    bgcolor=item["color"],
                                    border_radius=2
                                ),
                                ft.Container(
                                    width=progress_remaining_width,
                                    height=4,
                                    bgcolor=ft.Colors.GREY_700 if is_dark_mode else ft.Colors.GREY_200,
                                    border_radius=2
                                )
                            ],
                            spacing=0
                        ),
                        ft.Text(
                            f"{item['progress']}% completado" if item["progress"] > 0 else "Sin progreso",
                            size=9,
                            color=ft.Colors.GREY_400 if is_dark_mode else ft.Colors.GREY_600,
                            text_align=ft.TextAlign.RIGHT
                        ) if item["progress"] > 0 else ft.Container(height=12)
                    ],
                    spacing=2
                ),
                width=progress_bar_width,
                margin=ft.margin.only(top=5)
            )
            
            # Crear badge de status mejorado
            status_colors = {
                "active": ft.Colors.GREEN_500,
                "in_progress": ft.Colors.ORANGE_500,
                "completed": ft.Colors.BLUE_500,
                "available": ft.Colors.GREY_400,
                "locked": ft.Colors.RED_400
            }
            
            status_icons = {
                "active": ft.Icons.PLAY_CIRCLE_FILLED,
                "in_progress": ft.Icons.HOURGLASS_EMPTY,
                "completed": ft.Icons.CHECK_CIRCLE,
                "available": ft.Icons.CIRCLE_OUTLINED,
                "locked": ft.Icons.LOCK
            }
            
            status_badge = ft.Container(
                content=ft.Icon(
                    status_icons.get(item["status"], ft.Icons.CIRCLE_OUTLINED),
                    size=16,
                    color=status_colors.get(item["status"], ft.Colors.GREY_400)
                ),
                margin=ft.margin.only(right=8),
                tooltip=f"Estado: {item['status'].replace('_', ' ').title()}"
            )
            
            # Definir colores según el estado y tema
            card_bg_color = item["bg_color"] if is_selected else (ft.Colors.GREY_800 if is_dark_mode else ft.Colors.WHITE)
            icon_color = ft.Colors.WHITE if is_selected else item["color"]
            title_color = item["text_color"] if is_selected else (ft.Colors.WHITE if is_dark_mode else ft.Colors.BLACK87)
            subtitle_color = ft.Colors.WHITE70 if is_selected else (ft.Colors.GREY_400 if is_dark_mode else ft.Colors.GREY_600)
            border_color = item["color"] if is_selected else (ft.Colors.GREY_600 if is_dark_mode else ft.Colors.GREY_200)
            
            # Tab principal
            tab_content = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                status_badge,
                                ft.Icon(
                                    item["icon"],
                                    color=icon_color,
                                    size=20
                                ),
                                ft.Column(
                                    controls=[
                                        ft.Text(
                                            item["title"],
                                            size=13,
                                            weight=ft.FontWeight.BOLD,
                                            color=title_color
                                        ),
                                        ft.Text(
                                            item["subtitle"],
                                            size=10,
                                            color=subtitle_color,
                                            max_lines=1,
                                            overflow=ft.TextOverflow.ELLIPSIS
                                        )
                                    ],
                                    spacing=2,
                                    expand=True
                                )
                            ],
                            spacing=8,
                            alignment=ft.MainAxisAlignment.START
                        ),
                        progress_indicator if item["progress"] > 0 else ft.Container(height=8)
                    ],
                    spacing=5
                ),
                padding=ft.padding.all(12),
                margin=ft.margin.only(bottom=2),
                bgcolor=card_bg_color,
                border_radius=8,
                border=ft.border.all(2, border_color),
                shadow=ft.BoxShadow(
                    spread_radius=0,
                    blur_radius=6,
                    color=ft.Colors.BLACK26 if is_dark_mode else ft.Colors.BLACK12,
                    offset=ft.Offset(0, 2)
                ) if is_selected else None,
                on_click=lambda e, mode=item["key"]: self.switch_mode(mode),
                ink=True,
                animate=200
            )
            
            menu_controls.append(tab_content)
        

        
        return ft.Column(
            controls=menu_controls,
            spacing=3,
            scroll=ft.ScrollMode.AUTO
        )
    
    def switch_mode(self, mode: str):
        """
        Cambia el modo de la aplicación.
        """
        if self.current_mode != mode:
            self.current_mode = mode
            
            # Inicializar el chatbot con el nuevo modo
            self.chatbot = ChatBot(self.user.id, self.current_mode)
            # Limpiar el chat para el nuevo modo
            self.chat_container.controls.clear()
            # Limpiar la sesión actual para que se cree una nueva cuando sea necesario
            self.current_session = None
            
            # Actualizar la interfaz según el modo
            if mode == "charlemos":
                self.update_charlemos_mode()
            elif mode == "estudiemos":
                self.update_estudiemos_mode()
            elif mode == "evaluemos":
                self.update_evaluemos_mode()
            elif mode == "simulemos":
                self.update_simulemos_mode()
            elif mode == "analicemos":
                self.update_analicemos_mode()
            
            # Actualizar el status text
            self.status_text.value = f"✅ Conectado como {self.user.username} - Modo {mode.upper()} activo"
            self.status_text.color = ft.Colors.GREEN_600
            
            # Reconstruir el layout
            if self.page:
                content = self.build_layout()
                main_layout = self.page.controls[0]
                main_layout.controls[1] = content
                self.page.update()
    
    def update_charlemos_mode(self):
        """
        Actualiza la interfaz para el modo CHARLEMOS.
        """
        # Actualizar el placeholder del input
        self.message_input.hint_text = "Pregúntame cualquier cosa sobre PMP... ¿Qué es la gestión de riesgos? ¿Cómo se relaciona Agile con PMBOK?"
        
        # Actualizar el estado si no hay chatbot inicializado
        if not self.chatbot:
            self.status_text.value = "💬 Modo CHARLEMOS - Chat libre con tutor IA especializado en PMP"
            self.status_text.color = ft.Colors.BLUE_600
        
        # Si hay una conversación activa, mostrar mensaje de bienvenida para el modo
        if self.chatbot and len(self.chat_container.controls) == 0:
            welcome_message = """¡Bienvenido al modo **CHARLEMOS**! 💬

**Conversación libre y natural** sobre cualquier tema PMP con tu tutor personal de IA. Perfecto para clarificar dudas, explorar conceptos y tener discusiones profundas sobre Project Management.

## 🎯 **¿Qué puedes hacer aquí?**

### **💭 Preguntas Abiertas:**
• Conceptos fundamentales del PMBOK Guide

• Diferencias entre metodologías y frameworks

• Aplicación práctica de teorías PMP

• Casos de estudio y ejemplos reales

### **🔍 Clarificaciones y Dudas:**
• "No entiendo la diferencia entre schedule y timeline"

• "¿Qué significa exactamente 'stakeholder engagement'?"

• "Explícame como si tuviera 5 años qué es un PMO"

• "¿Cómo se relaciona Agile con el PMBOK tradicional?"

### **🌟 Exploración de Temas:**
• Gestión de riesgos en proyectos complejos

• Liderazgo y manejo de equipos

• Comunicación efectiva con stakeholders

• Integración de procesos y áreas de conocimiento

## ✨ **Características Especiales:**

🎓 **Explicaciones Adaptativas** - Me adapto a tu nivel de conocimiento

🔄 **Re-explicaciones** - "Explícamelo de otra forma" o "más simple"

🎯 **Analogías Personalizadas** - "Dame una analogía" para conceptos complejos

🔍 **Profundización Inteligente** - "Profundiza en esto" para más detalles

💡 **Ejemplos Prácticos** - Casos reales y situaciones del mundo laboral

🎨 **Múltiples Perspectivas** - Diferentes enfoques para el mismo concepto

## 🚀 **Modos de Conversación:**

### **📚 Modo Explicativo:**
• Definiciones claras y estructuradas

• Paso a paso de procesos complejos

• Frameworks y metodologías detalladas

### **🤔 Modo Socrático:**
• Te hago preguntas para que descubras conceptos

• Análisis crítico de situaciones

• Desarrollo del pensamiento estratégico

### **💼 Modo Práctico:**
• Aplicación en escenarios reales

• Resolución de problemas específicos

• Consejos para el día a día profesional

## 🎪 **Ejemplos de Conversaciones:**

**Conceptual:** "¿Cuál es la diferencia real entre un programa y un proyecto?"

**Práctico:** "Mi stakeholder principal cambió los requisitos a mitad del proyecto, ¿qué hago?"

**Estratégico:** "¿Cómo puedo mejorar la madurez organizacional en gestión de proyectos?"

**Comparativo:** "¿Cuándo usar Waterfall vs Agile vs Híbrido?"

¡Empecemos a charlar! ¿Qué tema de PMP te interesa explorar hoy?"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def update_estudiemos_mode(self):
        """
        Actualiza la interfaz para el modo ESTUDIEMOS UN TEMA.
        """
        # Actualizar el placeholder del input
        self.message_input.hint_text = "Ejemplo: 'Quiero estudiar Risk Management' o 'Necesito aprender Schedule Management'"
        
        # Actualizar el estado si no hay chatbot inicializado
        if not self.chatbot:
            self.status_text.value = "📚 Modo ESTUDIEMOS UN TEMA - Estudio estructurado y guiado por áreas específicas"
            self.status_text.color = ft.Colors.BLUE_600
        
        # Si hay una conversación activa, mostrar mensaje de bienvenida para el modo
        if self.chatbot and len(self.chat_container.controls) == 0:
            welcome_message = """¡Bienvenido al modo **ESTUDIEMOS UN TEMA**! 📚

Aquí tendrás sesiones de estudio **estructuradas y adaptativas** para dominar cualquier área del PMBOK Guide.

## 🎯 **Cómo funciona:**

**1. Selecciona tu tema** - Dime qué área quieres estudiar

**2. Configuramos la sesión** - Nivel, objetivos y tiempo disponible  

**3. Sesión guiada** - Te guío paso a paso con metodología probada

## 📚 **Áreas disponibles:**

### **People Domain:**
• Leadership & Team Management

• Stakeholder Engagement

### **Process Domain:**
• Risk Management

• Schedule Management

• Cost Management

• Quality Management  

• Resource Management

• Communications Management

• Procurement Management

• Scope Management

• Integration Management

### **Business Environment:**
• Strategy & Governance

• Compliance & Benefits Realization

## ✨ **Características especiales:**

🎓 **Ritmo personalizado** - Controlas la velocidad

📝 **Checkpoints** - Verifico tu comprensión

📌 **Note-taking** - Te sugiero puntos clave

🔖 **Bookmarks** - Marcamos secciones importantes

**¿Qué tema te gustaría estudiar hoy?** 
Ejemplo: *"Quiero estudiar Risk Management"* o *"Necesito aprender Schedule Management"*"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def update_evaluemos_mode(self):
        """
        Actualiza la interfaz para el modo EVALUEMOS TU CONOCIMIENTO.
        """
        # Actualizar el placeholder del input
        self.message_input.hint_text = "Ejemplo: 'Diagnóstico completo' o 'Evaluar Risk Management' o 'Práctica por debilidades'"
        
        # Actualizar el estado si no hay chatbot inicializado
        if not self.chatbot:
            self.status_text.value = "📊 Modo EVALUEMOS TU CONOCIMIENTO - Evaluación diagnóstica y práctica dirigida"
            self.status_text.color = ft.Colors.BLUE_600
        
        # Si hay una conversación activa, mostrar mensaje de bienvenida para el modo
        if self.chatbot and len(self.chat_container.controls) == 0:
            welcome_message = """¡Bienvenido al modo **EVALUEMOS TU CONOCIMIENTO**! 📊

Identifica tus **fortalezas y debilidades** con evaluaciones adaptativas y práctica específica para el examen PMP.

## 🎯 **Tipos de Evaluación:**

### **📋 Diagnóstico Inicial:**
• **Assessment completo** - 50 preguntas que cubren todo el PMBOK

• **Identificación de gaps** - Análisis de áreas débiles  

• **Reporte personalizado** - Plan de estudio recomendado

### **🎯 Práctica por Área:**
• **Selección específica** - Focus en un tema

• **Sesiones cortas** - 10-15 preguntas por sesión

• **Feedback inmediato** - Explicación detallada de cada respuesta

• **Adaptive testing** - Dificultad se ajusta según performance

### **💪 Práctica por Debilidades:**
• **Target weak areas** - Solo preguntas de áreas débiles

• **Reinforcement learning** - Repite conceptos hasta dominarlos

• **Progress tracking** - Muestra mejora en tiempo real

## 📚 **Dominios Evaluados:**

**People Domain** | **Process Domain** | **Business Environment**

• Leadership | • Risk Management | • Strategy & Governance

• Team Management | • Schedule Management | • Compliance

• Stakeholder Engagement | • Cost Management | • Benefits Realization

| • Quality Management |

| • Resource Management |

| • Communications |

| • Procurement |

| • Scope Management |

| • Integration |

## ✨ **Características Especiales:**

📝 **Estilo PMP real** - Preguntas largas con escenarios

🔍 **Explicaciones detalladas** - Por qué cada opción es correcta/incorrecta

📖 **Referencias al PMBOK** - Dónde encontrar más información

⏱️ **Time tracking** - Mide tiempo para preparar examen real

📊 **Analytics** - Score por dominio y tendencias temporales

**¿Qué tipo de evaluación prefieres?**

• *"Diagnóstico completo"* - Assessment inicial completo

• *"Evaluar Risk Management"* - Práctica por área específica  

• *"Práctica por debilidades"* - Focus en áreas débiles"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def update_simulemos_mode(self):
        """
        Actualiza la interfaz para el modo SIMULEMOS UN EXAMEN.
        """
        # Actualizar el placeholder del input
        self.message_input.hint_text = "Ejemplo: 'Examen completo' o 'Simulacro 60 minutos' o 'Solo Process Domain'"
        
        # Actualizar el estado si no hay chatbot inicializado
        if not self.chatbot:
            self.status_text.value = "⏱️ Modo SIMULEMOS UN EXAMEN - Simulacros completos en condiciones reales"
            self.status_text.color = ft.Colors.BLUE_600
        
        # Si hay una conversación activa, mostrar mensaje de bienvenida para el modo
        if self.chatbot and len(self.chat_container.controls) == 0:
            welcome_message = """¡Bienvenido al modo **SIMULEMOS UN EXAMEN**! ⏱️

Práctica completa del examen PMP en **condiciones que replican el examen real** con cronómetro, navegación realista y análisis post-examen.

## 🎯 **Tipos de Simulacro:**

### **📋 Examen Completo:**
• **180 preguntas** - Duración real 230 minutos (3h 50min)

• **Distribución oficial** - People (42%), Process (50%), Business Environment (8%)

• **Break opcional** - 10 minutos en la mitad (como examen real)

• **Ambiente controlado** - Sin pausas, cronómetro visible

### **⏰ Simulacro por Tiempo:**
• **30 minutos** - 23 preguntas (práctica rápida)

• **60 minutos** - 47 preguntas (sesión media)

• **90 minutos** - 70 preguntas (práctica extendida)

• **Útil** cuando no tienes tiempo completo

### **🎯 Simulacro por Dominio:**
• **Solo People** - 76 preguntas, tiempo proporcional

• **Solo Process** - 90 preguntas, tiempo proporcional  

• **Solo Business Environment** - 14 preguntas, tiempo proporcional

## ✨ **Características Durante el Examen:**

⏱️ **Timer prominente** - Cuenta regresiva siempre visible

🗺️ **Question navigator** - Overview de progreso, preguntas marcadas

📌 **Mark for review** - Sistema de marcado como examen real

🚫 **No feedback** - Sin respuestas correctas hasta terminar

💾 **Auto-save** - Guarda progreso automáticamente

## 📊 **Post-Examen Analysis:**

📈 **Score breakdown** - Por dominio y área de conocimiento

⏰ **Time analysis** - Tiempo por pregunta, identificar ritmo

🔍 **Question review** - Revisar todas las preguntas con explicaciones

🎯 **Weak areas identification** - Qué estudiar antes del siguiente simulacro

✅ **Readiness assessment** - Predicción de probabilidad de aprobar examen real

**¿Qué tipo de simulacro prefieres?**

• *"Examen completo"* - 180 preguntas, 230 minutos

• *"Simulacro 60 minutos"* - Práctica de tiempo limitado

• *"Solo Process Domain"* - Focus en área específica"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def update_analicemos_mode(self):
        """
        Actualiza la interfaz para el modo ANALICEMOS CÓMO VAMOS.
        """
        # Actualizar el placeholder del input
        self.message_input.hint_text = "Ejemplo: 'Mostrar mi progreso' o 'Análisis de preparación' o 'Dashboard completo'"
        
        # Actualizar el estado si no hay chatbot inicializado
        if not self.chatbot:
            self.status_text.value = "📊 Modo ANALICEMOS CÓMO VAMOS - Dashboard de progreso y análisis de preparación"
            self.status_text.color = ft.Colors.BLUE_600
        
        # Si hay una conversación activa, mostrar mensaje de bienvenida para el modo
        if self.chatbot and len(self.chat_container.controls) == 0:
            welcome_message = """¡Bienvenido al modo **ANALICEMOS CÓMO VAMOS**! 📊

Vista **comprehensiva del progreso de estudio** y preparación para el examen PMP con analytics predictivos y recomendaciones personalizadas.

## 📈 **Overview General:**

📊 **Readiness Score** - Porcentaje de preparación estimado

🔥 **Study Streak** - Días consecutivos de estudio

⏰ **Total Study Time** - Tiempo acumulado en la plataforma

🎯 **Exam Countdown** - Días hasta fecha objetivo de examen

## 🎯 **Progress por Área:**

📚 **Visual Breakdown** - Dominios People/Process/Business Environment

🗺️ **Heatmap de Conocimiento** - Verde=dominado, Amarillo=en progreso, Rojo=débil

✅ **Completion Percentage** - Por cada área de conocimiento

⏱️ **Time Invested** - Por área vs tiempo recomendado

## 📊 **Performance Analytics:**

📈 **Score Trends** - Gráfico de evolución de scores en el tiempo

🎯 **Question Accuracy** - Porcentaje de aciertos por tipo de pregunta

⚡ **Speed Analysis** - Tiempo promedio por pregunta vs objetivo

📊 **Consistency Metrics** - Qué tan consistente es el performance

## 🔍 **Study Patterns:**

⏰ **Best Study Times** - Cuándo es más efectivo estudiando

📚 **Session Effectiveness** - Correlación entre duración y retención

💡 **Content Preferences** - Chat vs estudio estructurado vs evaluaciones

🎯 **Weak Spot Patterns** - Patrones en errores comunes

## 🔮 **Predictive Analytics:**

🎯 **Exam Readiness Prediction** - Basado en todos los datos

📋 **Recommended Study Plan** - Próximos pasos para mejorar score

⏰ **Time to Readiness** - Estimación de cuándo estará listo

⚠️ **Risk Assessment** - Probabilidad de fallar en áreas específicas

## 💡 **Actionable Insights:**

📚 **Study Recommendations** - "Enfócate en Risk Management esta semana"

⏰ **Time Allocation** - "Dedica 60% más tiempo a Process domain"

🎯 **Strategy Adjustments** - "Practica más simulacros completos"

🎯 **Goal Setting** - Objetivos SMART para próxima semana/mes

**¿Qué análisis te gustaría ver?**

• *"Mostrar mi progreso"* - Dashboard completo de progreso

• *"Análisis de preparación"* - Evaluación detallada de readiness

• *"Recomendaciones de estudio"* - Plan personalizado de mejora"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def build_layout(self):
        """
        Construye el layout principal con sidebar integrado (modos + conversaciones) y área de chat.
        """
        # Área de chat principal
        chat_area = ft.Container(
            content=self.chat_container,
            padding=ft.padding.all(20),
            expand=True,
            bgcolor=ft.Colors.WHITE,
            width=None,  # Se ajusta al contenedor padre
            height=None  # Se ajusta al contenido
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
        
        # Construir el layout según la visibilidad del sidebar
        layout_controls = []
        
        # Sidebar integrado (modos + conversaciones)
        if self.sidebar_visible:
            integrated_sidebar = ft.Container(
                content=ft.Column(
                    controls=[
                        # Header del sidebar
                        ft.Container(
                            content=ft.Row(
                                controls=[
                                    ft.Text(
                                        "🎯 PMP Assistant",
                                        size=16,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER
                            ),
                            padding=ft.padding.all(15),
                            bgcolor=ft.Colors.BLUE_800
                        ),
                        
                        # Sección de Modos
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Text(
                                        "MODOS",
                                        size=12,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.BLUE_800
                                    ),
                                    self.create_navigation_menu()
                                ],
                                spacing=10
                            ),
                            padding=ft.padding.all(15),
                            bgcolor=ft.Colors.BLUE_50
                        ),
                        
                        # Divider entre secciones
                        ft.Divider(height=1, color=ft.Colors.BLUE_200),
                        
                        # Sección de Conversaciones
                        ft.Container(
                            content=ft.Column(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Text(
                                                "CONVERSACIONES",
                                                size=12,
                                                weight=ft.FontWeight.BOLD,
                                                color=ft.Colors.BLUE_700
                                            ),
                                            ft.IconButton(
                                                icon=ft.Icons.ADD,
                                                tooltip="Nueva conversación",
                                                icon_color=ft.Colors.BLUE_700,
                                                icon_size=16,
                                                on_click=self.new_conversation
                                            )
                                        ],
                                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                                    ),
                                    ft.Container(
                                        content=self.conversations_list,
                                        expand=True
                                    )
                                ],
                                spacing=5
                            ),
                            padding=ft.padding.all(15),
                            expand=True
                        )
                    ],
                    spacing=0
                ),
                width=320,
                bgcolor=ft.Colors.GREY_50,
                border=ft.border.only(right=ft.BorderSide(1, ft.Colors.GREY_300))
            )
            layout_controls.append(integrated_sidebar)
        
        # Área principal de chat
        layout_controls.append(main_chat_area)
        
        return ft.Row(
            controls=layout_controls,
            spacing=0,
            expand=True
        )
    
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
                                tooltip="Alternar sidebar",
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
        
        # Configurar modo inicial
        self.update_charlemos_mode()
        
        # Enfocar el campo de entrada
        self.message_input.focus()
    
    def show_settings_dialog(self, e):
        """
        Muestra el diálogo de configuración personalizable.
        """
        def close_dialog(e):
            settings_dialog.open = False
            self.page.update()
        
        def save_settings(e):
            # Aquí se guardarían las configuraciones
            snack_bar = ft.SnackBar(
                content=ft.Text("⚙️ Configuración guardada exitosamente"),
                bgcolor=ft.Colors.GREEN_600
            )
            self.page.overlay.append(snack_bar)
            snack_bar.open = True
            self.page.update()
            close_dialog(e)
        
        settings_content = ft.Column(
            controls=[
                ft.Text("🎯 Objetivos de Estudio", size=16, weight=ft.FontWeight.BOLD),
                ft.TextField(
                    label="Fecha objetivo del examen",
                    hint_text="DD/MM/YYYY",
                    prefix_icon=ft.Icons.CALENDAR_TODAY
                ),
                ft.TextField(
                    label="Horas de estudio diarias",
                    hint_text="2-4 horas recomendadas",
                    prefix_icon=ft.Icons.SCHEDULE
                ),
                
                ft.Divider(),
                ft.Text("🔔 Notificaciones", size=16, weight=ft.FontWeight.BOLD),
                ft.Switch(
                    label="Recordatorios de estudio",
                    value=True
                ),
                ft.Switch(
                    label="Alertas de progreso",
                    value=True
                ),
                ft.Switch(
                    label="Notificaciones de logros",
                    value=False
                ),
                
                ft.Divider(),
                ft.Text("🎨 Personalización", size=16, weight=ft.FontWeight.BOLD),
                ft.Dropdown(
                    label="Tema visual",
                    options=[
                        ft.dropdown.Option("light", "Claro"),
                        ft.dropdown.Option("dark", "Oscuro"),
                        ft.dropdown.Option("auto", "Automático")
                    ],
                    value="light"
                ),
                ft.Dropdown(
                    label="Idioma de interfaz",
                    options=[
                        ft.dropdown.Option("es", "Español"),
                        ft.dropdown.Option("en", "English")
                    ],
                    value="es"
                )
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
            height=400
        )
        
        settings_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("⚙️ Configuración"),
            content=settings_content,
            actions=[
                ft.TextButton("Cancelar", on_click=close_dialog),
                ft.ElevatedButton("Guardar", on_click=save_settings)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        
        self.page.dialog = settings_dialog
        settings_dialog.open = True
        self.page.update()
    
    def show_notifications_dialog(self, e):
        """
        Muestra el centro de notificaciones.
        """
        def close_dialog(e):
            notifications_dialog.open = False
            self.page.update()
        
        notifications_content = ft.Column(
            controls=[
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.SCHEDULE, color=ft.Colors.BLUE_600),
                    title=ft.Text("Recordatorio de estudio"),
                    subtitle=ft.Text("Es hora de tu sesión diaria - hace 5 min"),
                    trailing=ft.IconButton(ft.Icons.CLOSE, icon_size=16)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.TRENDING_UP, color=ft.Colors.GREEN_600),
                    title=ft.Text("¡Progreso excelente!"),
                    subtitle=ft.Text("Has completado 3 sesiones esta semana - hace 1 hora"),
                    trailing=ft.IconButton(ft.Icons.CLOSE, icon_size=16)
                ),
                ft.ListTile(
                    leading=ft.Icon(ft.Icons.WARNING, color=ft.Colors.ORANGE_600),
                    title=ft.Text("Área de mejora detectada"),
                    subtitle=ft.Text("Considera reforzar 'Gestión de Riesgos' - hace 2 horas"),
                    trailing=ft.IconButton(ft.Icons.CLOSE, icon_size=16)
                ),
                ft.Divider(),
                ft.TextButton(
                    "Marcar todas como leídas",
                    icon=ft.Icons.DONE_ALL,
                    on_click=close_dialog
                )
            ],
            spacing=5,
            scroll=ft.ScrollMode.AUTO,
            height=300
        )
        
        notifications_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("🔔 Notificaciones"),
            content=notifications_content,
            actions=[
                ft.TextButton("Cerrar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = notifications_dialog
        notifications_dialog.open = True
        self.page.update()
    
    def toggle_theme(self, e):
        """
        Alterna entre tema claro y oscuro.
        """
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            theme_text = "🌙 Tema oscuro activado"
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            theme_text = "☀️ Tema claro activado"
        
        # Actualizar el menú de navegación con los nuevos colores
        # Buscar el contenedor del menú en la página y actualizarlo
        try:
            # Reconstruir toda la UI para aplicar los nuevos colores
            content = self.build_layout()
            self.page.controls.clear()
            self.page.add(content)
        except Exception as ex:
            print(f"Error actualizando tema: {ex}")
        
        snack_bar = ft.SnackBar(
            content=ft.Text(theme_text),
            bgcolor=ft.Colors.BLUE_600
        )
        self.page.overlay.append(snack_bar)
        snack_bar.open = True
        self.page.update()
    
    def show_help_dialog(self, e):
        """
        Muestra el diálogo de ayuda y guía rápida.
        """
        def close_dialog(e):
            help_dialog.open = False
            self.page.update()
        
        help_content = ft.Column(
            controls=[
                ft.Text("🚀 Guía Rápida", size=18, weight=ft.FontWeight.BOLD),
                
                ft.ExpansionTile(
                    title=ft.Text("💬 CHARLEMOS"),
                    subtitle=ft.Text("Chat libre con el tutor IA"),
                    controls=[
                        ft.Text("• Haz cualquier pregunta sobre PMP\n• Conversación natural y adaptativa\n• Ideal para dudas específicas", size=12)
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("📚 ESTUDIEMOS"),
                    subtitle=ft.Text("Aprendizaje estructurado"),
                    controls=[
                        ft.Text("• Sesiones guiadas por tema\n• Metodología de 6 pasos\n• Progreso adaptativo", size=12)
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("📝 EVALUEMOS"),
                    subtitle=ft.Text("Evaluación y práctica"),
                    controls=[
                        ft.Text("• Diagnósticos completos\n• Práctica por áreas débiles\n• Feedback inmediato", size=12)
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("⏱️ SIMULEMOS"),
                    subtitle=ft.Text("Exámenes de práctica"),
                    controls=[
                        ft.Text("• Simulacros completos\n• Condiciones reales\n• Análisis post-examen", size=12)
                    ]
                ),
                
                ft.ExpansionTile(
                    title=ft.Text("📊 ANALICEMOS"),
                    subtitle=ft.Text("Dashboard de progreso"),
                    controls=[
                        ft.Text("• Analytics detallados\n• Predicciones de preparación\n• Recomendaciones personalizadas", size=12)
                    ]
                ),
                
                ft.Divider(),
                ft.Text("💡 Consejos:", weight=ft.FontWeight.BOLD),
                ft.Text("• Usa ESTUDIEMOS para aprender conceptos nuevos\n• Practica con EVALUEMOS regularmente\n• Simula exámenes antes del día real\n• Revisa tu progreso en ANALICEMOS", size=12)
            ],
            spacing=8,
            scroll=ft.ScrollMode.AUTO,
            height=400
        )
        
        help_dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("❓ Ayuda"),
            content=help_content,
            actions=[
                ft.TextButton("Cerrar", on_click=close_dialog)
            ]
        )
        
        self.page.dialog = help_dialog
        help_dialog.open = True
        self.page.update()

    def calculate_progress_indicators(self):
        """
        Calcula los indicadores de progreso para cada sección basado en datos reales del usuario.
        """
        try:
            # Inicializar progreso por defecto
            progress_data = {
                "charlemos": {"progress": 0, "status": "available"},
                "estudiemos": {"progress": 0, "status": "available"},
                "evaluemos": {"progress": 0, "status": "available"},
                "simulemos": {"progress": 0, "status": "available"},
                "analicemos": {"progress": 0, "status": "available"}
            }
            
            # Marcar el modo actual como activo si hay uno seleccionado
            if self.current_mode:
                progress_data[self.current_mode]["status"] = "active"
            
            # Calcular progreso basado en conversaciones si el chatbot está disponible
            total_conversations = 0
            if hasattr(self, 'chatbot') and self.chatbot is not None:
                if hasattr(self.chatbot, 'conversation_manager') and self.chatbot.conversation_manager is not None:
                    try:
                        conversations = self.chatbot.conversation_manager.get_conversations(self.user.id)
                        total_conversations = len(conversations) if conversations else 0
                    except Exception as e:
                        print(f"Error obteniendo conversaciones: {e}")
                        total_conversations = 0
            
            if total_conversations > 0:
                progress_data["charlemos"]["progress"] = min(total_conversations * 10, 100)
                # Solo cambiar el estado si no es el modo actual
                if self.current_mode != "charlemos":
                    progress_data["charlemos"]["status"] = "available"
            
            # Calcular progreso de estudio (simulado - se puede conectar con datos reales)
            # Esto se basaría en temas completados, tiempo de estudio, etc.
            study_sessions = total_conversations // 3  # Ejemplo: cada 3 conversaciones = 1 sesión de estudio
            if study_sessions > 0:
                progress_data["estudiemos"]["progress"] = min(study_sessions * 15, 100)
                progress_data["estudiemos"]["status"] = "in_progress" if study_sessions < 7 else "completed"
            
            # Calcular progreso de evaluaciones
            # Esto se basaría en evaluaciones completadas, scores, etc.
            evaluation_progress = min(total_conversations * 5, 100)  # Ejemplo
            if evaluation_progress > 0:
                progress_data["evaluemos"]["progress"] = evaluation_progress
                progress_data["evaluemos"]["status"] = "available"
            
            # Calcular progreso de simulacros
            # Esto se basaría en exámenes simulados completados
            simulation_progress = max(0, min((total_conversations - 5) * 8, 100))  # Ejemplo
            if simulation_progress > 0:
                progress_data["simulemos"]["progress"] = simulation_progress
                progress_data["simulemos"]["status"] = "available"
            
            # Analytics siempre disponible si hay datos
            if total_conversations > 0:
                progress_data["analicemos"]["progress"] = min(total_conversations * 12, 100)
                progress_data["analicemos"]["status"] = "available"
            
            return progress_data
            
        except Exception as e:
            print(f"Error calculando progreso: {e}")
            # Retornar valores por defecto en caso de error
            default_progress = {
                "charlemos": {"progress": 0, "status": "available"},
                "estudiemos": {"progress": 0, "status": "available"},
                "evaluemos": {"progress": 0, "status": "available"},
                "simulemos": {"progress": 0, "status": "available"},
                "analicemos": {"progress": 0, "status": "available"}
            }
            # Marcar el modo actual como activo si hay uno seleccionado
            if self.current_mode:
                default_progress[self.current_mode]["status"] = "active"
            return default_progress

def create_app(user: User):
    """
    Función para crear y configurar la aplicación de chat.
    """
    def main(page: ft.Page):
        chat_ui = ChatUI(user)
        chat_ui.build_ui(page)
    
    return main 