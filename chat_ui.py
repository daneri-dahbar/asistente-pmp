"""
Interfaz de usuario para la aplicación de chat usando Flet.
Implementa un diseño moderno y responsivo para el Asistente PMP.
"""

import flet as ft
from typing import List, Tuple
from chatbot import ChatBot
from db.models import User, get_local_datetime
import threading
import time
import datetime

def create_chat_message(message: str, is_user: bool):
    """
    Función para crear mensajes individuales del chat con estilo Slack/Discord.
    """
    # Obtener timestamp actual en GMT-3
    timestamp = get_local_datetime().strftime("%H:%M")
    
    # Configurar avatar y nombre según el remitente
    if is_user:
        avatar_icon = ft.Icons.PERSON
        avatar_color = ft.Colors.BLUE_600
        username = "Tú"
        username_color = ft.Colors.BLUE_700
    else:
        avatar_icon = ft.Icons.SMART_TOY
        avatar_color = ft.Colors.GREEN_600
        username = "Asistente PMP"
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
            auto_scroll=False,  # Desactivado por defecto para permitir scroll manual
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
            multiline=False,  # Cambiar a single line para que Enter envíe el mensaje
            filled=True,
            border_radius=25,
            content_padding=ft.padding.symmetric(15, 10),
            on_submit=self.handle_submit,
            autofocus=False  # No hacer autofocus por defecto
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
        self.should_auto_scroll = False  # Controla cuándo hacer auto-scroll
        self.showing_profile = False  # Controla si se está mostrando el formulario de perfil
        self.cronometro_visible = False
        self.cronometro_segundos = 0
        self.cronometro_text = ft.Text("", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
        self._cronometro_thread = None
        self._cronometro_running = False
    
    def handle_submit(self, e):
        """
        Maneja el envío de mensajes desde el campo de texto.
        Enter = Enviar mensaje
        El campo es single line para que Enter siempre envíe el mensaje.
        """
        self.send_message(e)
    
    def scroll_to_bottom(self):
        """
        Hace scroll hacia abajo en el chat cuando es necesario.
        """
        if self.should_auto_scroll and self.page:
            # Activar temporalmente auto_scroll
            self.chat_container.auto_scroll = True
            self.page.update()
            # Desactivar auto_scroll después de un breve momento
            def disable_auto_scroll():
                import time
                time.sleep(0.1)  # Esperar un poco para que se complete el scroll
                self.chat_container.auto_scroll = False
                self.should_auto_scroll = False
                if self.page:
                    self.page.update()
            
            threading.Thread(target=disable_auto_scroll, daemon=True).start()
    
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
        
        # Hacer scroll hacia abajo al cargar una conversación
        if history:  # Solo si hay mensajes
            self.should_auto_scroll = True
            self.scroll_to_bottom()
    
    def load_conversations_list(self):
        """
        Carga la lista de conversaciones del usuario en el sidebar, filtradas por modo actual.
        """
        if not self.chatbot:
            return
        
        try:
            # Obtener sesiones del usuario filtradas por modo actual
            mode_filter = self.current_mode if self.current_mode else None
            self.sessions_list = self.chatbot.db_manager.get_user_sessions(self.user.id, mode_filter)
            self.conversations_list.controls.clear()
            
            # Agregar cada conversación a la lista
            for session in self.sessions_list:
                conversation_item = self.create_conversation_item(session)
                self.conversations_list.controls.append(conversation_item)
            
            if self.page:
                self.page.update()
                
        except Exception as e:
            print(f"Error al cargar conversaciones: {e}")
    
    def get_mode_colors(self, mode: str):
        """
        Retorna los colores asociados a cada modo.
        """
        mode_colors = {
            "charlemos": {
                "primary": ft.Colors.BLUE_600,
                "light": ft.Colors.BLUE_100,
                "text": ft.Colors.BLUE_800
            },
            "estudiemos": {
                "primary": ft.Colors.GREEN_600,
                "light": ft.Colors.GREEN_100,
                "text": ft.Colors.GREEN_800
            },
            "evaluemos": {
                "primary": ft.Colors.ORANGE_600,
                "light": ft.Colors.ORANGE_100,
                "text": ft.Colors.ORANGE_800
            },
            "simulemos": {
                "primary": ft.Colors.PURPLE_600,
                "light": ft.Colors.PURPLE_100,
                "text": ft.Colors.PURPLE_800
            },
            "analicemos": {
                "primary": ft.Colors.TEAL_600,
                "light": ft.Colors.TEAL_100,
                "text": ft.Colors.TEAL_800
            }
        }
        return mode_colors.get(mode, {
            "primary": ft.Colors.GREY_600,
            "light": ft.Colors.GREY_100,
            "text": ft.Colors.GREY_800
        })
    
    def format_date(self, date_obj):
        """
        Formatea una fecha para mostrar en la interfaz estilo YouTube.
        """
        if not date_obj:
            return "Sin fecha"
        
        try:
            from datetime import datetime, timedelta
            
            # Si es string, convertir a datetime
            if isinstance(date_obj, str):
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            
            # Asegurar que ambas fechas estén en la misma zona horaria (sin timezone)
            now = get_local_datetime().replace(tzinfo=None)
            if date_obj.tzinfo:
                date_obj = date_obj.replace(tzinfo=None)
            
            # Calcular diferencia
            diff = now - date_obj
            total_seconds = int(diff.total_seconds())
            
            # Si es negativo (fecha futura), mostrar "Ahora"
            if total_seconds < 0:
                return "Ahora"
            
            # Menos de 1 minuto
            if total_seconds < 60:
                return "Ahora"
            
            # Menos de 1 hora
            elif total_seconds < 3600:
                minutes = total_seconds // 60
                return f"Hace {minutes} min"
            
            # Menos de 24 horas (mismo día)
            elif diff.days == 0:
                hours = total_seconds // 3600
                return f"Hace {hours}h"
            
            # Ayer
            elif diff.days == 1:
                return "Ayer"
            
            # Hoy (si por alguna razón diff.days es 0 pero ya pasamos las horas)
            elif diff.days == 0:
                return "Hoy"
            
            # Menos de 1 semana
            elif diff.days < 7:
                return f"Hace {diff.days} día{'s' if diff.days > 1 else ''}"
            
            # Menos de 1 mes (aproximadamente 30 días)
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"Hace {weeks} semana{'s' if weeks > 1 else ''}"
            
            # Menos de 1 año (aproximadamente 365 días)
            elif diff.days < 365:
                months = diff.days // 30
                return f"Hace {months} mes{'es' if months > 1 else ''}"
            
            # 1 año o más
            else:
                years = diff.days // 365
                return f"Hace {years} año{'s' if years > 1 else ''}"
                
        except Exception as e:
            print(f"Error al formatear fecha: {e}")
            return "Sin fecha"
    
    def create_conversation_item(self, session):
        """
        Crea un elemento de conversación para el sidebar.
        """
        try:
            is_current = self.current_session and session.id == self.current_session.id
            
            # Obtener colores del modo
            session_mode = getattr(session, 'mode', 'charlemos')
            colors = self.get_mode_colors(session_mode)
            
            # Obtener preview del último mensaje
            try:
                messages = self.chatbot.db_manager.get_session_messages(session.id)
                if messages:
                    last_message = messages[-1][1]  # content del último mensaje
                    preview = last_message[:45] + "..." if len(last_message) > 45 else last_message
                else:
                    preview = "Nueva conversación"
            except:
                preview = "Nueva conversación"
            
            # Formatear fecha de último uso
            last_used_text = self.format_date(getattr(session, 'last_used_at', None))
        
            # Contenedor de la conversación
            conversation_container = ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        session.name,
                                        size=14,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE if is_current else colors["text"],
                                        overflow=ft.TextOverflow.ELLIPSIS
                                    ),
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
                        ),
                        ft.Row(
                            controls=[
                                ft.Container(
                                    content=ft.Text(
                                        session_mode.upper(),
                                        size=9,
                                        weight=ft.FontWeight.BOLD,
                                        color=colors["primary"] if not is_current else ft.Colors.WHITE
                                    ),
                                    bgcolor=colors["light"] if not is_current else ft.Colors.WHITE24,
                                    padding=ft.padding.symmetric(horizontal=6, vertical=2),
                                    border_radius=10
                                ),
                                ft.Text(
                                    last_used_text,
                                    size=9,
                                    color=ft.Colors.WHITE60 if is_current else ft.Colors.GREY_500,
                                    expand=True,
                                    text_align=ft.TextAlign.RIGHT
                                )
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        )
                    ],
                    spacing=4
                ),
                padding=ft.padding.all(10),
                margin=ft.margin.symmetric(0, 2),
                bgcolor=colors["primary"] if is_current else colors["light"],
                border=ft.border.all(1, colors["primary"]) if not is_current else None,
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
            
            # Hacer scroll hacia abajo al cambiar de conversación
            self.should_auto_scroll = True
            self.scroll_to_bottom()
            
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
        
        # Hacer scroll hacia abajo al enviar mensaje
        self.should_auto_scroll = True
        self.scroll_to_bottom()
        
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
                
                # Hacer scroll hacia abajo al recibir respuesta
                self.should_auto_scroll = True
                self.scroll_to_bottom()
                
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
            
            # Hacer scroll hacia abajo al crear nueva conversación
            self.should_auto_scroll = True
            self.scroll_to_bottom()
            
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
            # Detener cronómetro si cambiamos de modo
            if self.current_mode in ["simulemos", "evaluemos"]:
                self.stop_cronometro()
            self.current_mode = mode
            # Ya NO iniciar cronómetro aquí
            
            # Recrear el message_input con autofocus para el nuevo modo
            self.message_input = ft.TextField(
                hint_text="Escribe tu mensaje aquí...",
                multiline=False,  # Cambiar a single line para que Enter envíe el mensaje
                filled=True,
                border_radius=25,
                content_padding=ft.padding.symmetric(15, 10),
                on_submit=self.handle_submit,
                autofocus=True  # Hacer autofocus cuando se activa un modo
            )
            
            # Inicializar el chatbot con el nuevo modo
            self.chatbot = ChatBot(self.user.id, self.current_mode)
            # Limpiar el chat para el nuevo modo
            self.chat_container.controls.clear()
            # Limpiar la sesión actual para que se cree una nueva cuando sea necesario
            self.current_session = None
            
            # Recargar las conversaciones filtradas por el nuevo modo
            self.load_conversations_list()
            
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
            welcome_message = """¡Bienvenido al modo **CHARLEMOS**! 💬\n\n**Conversación libre y natural** sobre cualquier tema de gestión de proyectos y PMP. Ideal para aclarar dudas, explorar conceptos y conversar sobre experiencias reales.\n\n## 🎯 **¿Qué puedes hacer aquí?**\n\n### **💭 Preguntas Abiertas:**\n• Conceptos fundamentales del PMBOK\n• Diferencias entre metodologías y enfoques\n• Aplicación práctica de la gestión de proyectos\n• Casos de estudio y ejemplos reales\n\n### **🔍 Clarificaciones y Dudas:**\n• "No entiendo la diferencia entre cronograma y calendario"\n• "¿Qué significa exactamente 'interesados'?"\n• "Explícame como si tuviera 5 años qué es una PMO"\n• "¿Cómo se relaciona Ágil con el PMBOK tradicional?"\n\n### **🌟 Exploración de Temas:**\n• Gestión de riesgos en proyectos\n• Liderazgo y manejo de equipos\n• Comunicación efectiva con interesados\n• Integración de procesos y áreas de conocimiento\n\n## ✨ **Características Especiales:**\n\n🎓 **Explicaciones adaptadas** a tu nivel\n🔄 **Re-explicaciones** con diferentes ejemplos\n🎯 **Analogías** para conceptos complejos\n🔍 **Profundización** cuando lo necesites\n💡 **Ejemplos prácticos** y situaciones reales\n\n¡Empecemos a charlar! ¿Qué tema de gestión de proyectos te interesa explorar hoy?"""
            
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
            welcome_message = """¡Bienvenido al modo **ESTUDIEMOS UN TEMA**! 📚\n\nAquí tendrás sesiones de estudio **estructuradas y adaptativas** para dominar cualquier área del PMBOK.\n\n## 🎯 **¿Cómo funciona?**\n\n1. Selecciona tu tema: dime qué área quieres estudiar\n2. Configuramos la sesión: nivel, objetivos y tiempo disponible\n3. Sesión guiada: te acompaño paso a paso\n\n## 📚 **Áreas disponibles:**\n\n### **Personas:**\n• Liderazgo y gestión de equipos\n• Relación con interesados\n\n### **Procesos:**\n• Gestión de riesgos\n• Gestión del cronograma\n• Gestión de costos\n• Gestión de la calidad\n• Gestión de recursos\n• Gestión de las comunicaciones\n• Gestión de adquisiciones\n• Gestión del alcance\n• Integración\n\n### **Entorno de Negocio:**\n• Estrategia y gobernanza\n• Cumplimiento y beneficios\n\n## ✨ **Características especiales:**\n\n🎓 Ritmo personalizado\n📝 Verificación de comprensión\n📌 Sugerencias de puntos clave\n🔖 Marcadores de secciones importantes\n\n**¿Qué tema te gustaría estudiar hoy?**\nEjemplo: "Quiero estudiar gestión de riesgos" o "Necesito aprender cronograma"""
            
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
            welcome_message = """¡Bienvenido al modo **EVALUEMOS TU CONOCIMIENTO**! 📊\n\nIdentifica tus **fortalezas y debilidades** con evaluaciones adaptativas y práctica específica para el examen PMP.\n\n## 🎯 **Tipos de Evaluación:**\n\n### **📋 Diagnóstico Inicial:**\n• Diagnóstico completo - 50 preguntas que cubren todo el PMBOK\n• Identificación de áreas débiles\n• Reporte personalizado con plan de estudio\n\n### **🎯 Práctica por Área:**\n• Selección de un tema específico\n• Sesiones cortas de 10-15 preguntas\n• Retroalimentación inmediata y detallada\n• Dificultad adaptativa según tu desempeño\n\n### **💪 Práctica por Debilidades:**\n• Solo preguntas de áreas débiles\n• Repetición de conceptos hasta dominarlos\n• Seguimiento de tu progreso en tiempo real\n\n## 📚 **Dominios Evaluados:**\n• Personas\n• Procesos\n• Entorno de Negocio\n\n## ✨ **Características Especiales:**\n\n📝 Preguntas tipo examen real\n🔍 Explicaciones detalladas\n📖 Referencias al PMBOK\n⏱️ Medición de tiempo\n📊 Análisis de resultados\n\n**¿Qué tipo de evaluación prefieres?**\n• "Diagnóstico completo"\n• "Evaluar gestión de riesgos"\n• "Práctica por debilidades"""
            
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
            welcome_message = """¡Bienvenido al modo **SIMULEMOS UN EXAMEN**! ⏱️\n\nPráctica completa del examen PMP en **condiciones que replican el examen real** con cronómetro, navegación realista y análisis posterior.\n\n## 🎯 **Tipos de Simulacro:**\n\n### **📋 Examen Completo:**\n• 180 preguntas - Duración real 230 minutos (3h 50min)\n• Distribución oficial: Personas (42%), Procesos (50%), Entorno de Negocio (8%)\n• Pausa opcional de 10 minutos en la mitad\n• Ambiente controlado, sin pausas, cronómetro visible\n\n### **⏰ Simulacro por Tiempo:**\n• 30 minutos - 23 preguntas (práctica rápida)\n• 60 minutos - 47 preguntas (sesión media)\n• 90 minutos - 70 preguntas (práctica extendida)\n• Útil cuando no tienes tiempo completo\n\n### **🎯 Simulacro por Dominio:**\n• Solo Personas - 76 preguntas, tiempo proporcional\n• Solo Procesos - 90 preguntas, tiempo proporcional\n• Solo Entorno de Negocio - 14 preguntas, tiempo proporcional\n\n## ✨ **Características Durante el Examen:**\n\n⏱️ Cronómetro siempre visible\n🗺️ Navegador de preguntas\n📌 Marcado para revisión\n🚫 Sin feedback hasta terminar\n💾 Guardado automático\n\n## 📊 **Análisis Posterior:**\n\n📈 Resultados por dominio y área\n⏰ Análisis de tiempo por pregunta\n🔍 Revisión de todas las preguntas\n🎯 Identificación de áreas a reforzar\n✅ Predicción de preparación para el examen real\n\n**¿Qué tipo de simulacro prefieres?**\n• "Examen completo"\n• "Simulacro 60 minutos"\n• "Solo Procesos"""
            
            welcome_widget = create_chat_message(welcome_message, False)
            self.chat_container.controls.append(welcome_widget)
    
    def update_analicemos_mode(self):
        """
        Actualiza la interfaz para el modo ANALICEMOS CÓMO VAMOS.
        """
        # Utilidad para traducción de días y formato de fecha
        dias_es = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }
        def fecha_es(date_str):
            # Convierte yyyy-MM-dd a dd/MM/aaaa solo si es una fecha
            try:
                if isinstance(date_str, str) and '-' in date_str:
                    from datetime import datetime
                    return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d/%m/%Y")
                return date_str
            except:
                return date_str

        # Limpiar el contenedor principal
        self.chat_container.controls.clear()

        # Obtener datos reales del usuario
        analytics = None
        if self.chatbot and hasattr(self.chatbot, 'db_manager'):
            try:
                analytics = self.chatbot.db_manager.get_user_analytics_data(self.user.id)
            except Exception as e:
                analytics = None
                print(f"Error obteniendo datos analíticos: {e}")

        # Valores por defecto si no hay datos
        overview = analytics['overview'] if analytics and 'overview' in analytics else {}
        total_sessions = overview.get('total_sessions', 0)
        total_study_hours = overview.get('study_time_hours', 0)
        streak_days = overview.get('study_streak_days', 0)
        sessions_by_mode = overview.get('sessions_by_mode', {
            'charlemos': 0,
            'estudiemos': 0,
            'evaluemos': 0,
            'simulemos': 0
        })

        # Tarjetas resumen
        summary_cards = ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Sesiones totales", size=12, color=ft.Colors.GREY_700),
                    ft.Text(str(total_sessions), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                ], spacing=2),
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.BLUE_50,
                border_radius=8,
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Horas de estudio", size=12, color=ft.Colors.GREY_700),
                    ft.Text(str(total_study_hours), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700)
                ], spacing=2),
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.GREEN_50,
                border_radius=8,
                expand=True
            ),
            ft.Container(
                content=ft.Column([
                    ft.Text("Racha de días", size=12, color=ft.Colors.GREY_700),
                    ft.Text(str(streak_days), size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700)
                ], spacing=2),
                padding=ft.padding.all(16),
                bgcolor=ft.Colors.ORANGE_50,
                border_radius=8,
                expand=True
            )
        ], spacing=16)

        # Tabla de distribución por modo
        mode_labels = [
            ("charlemos", "Charlemos", ft.Colors.BLUE_600),
            ("estudiemos", "Estudiemos", ft.Colors.GREEN_600),
            ("evaluemos", "Evaluemos", ft.Colors.ORANGE_600),
            ("simulemos", "Simulemos", ft.Colors.PURPLE_600)
        ]
        max_sessions = max(sessions_by_mode.values()) if sessions_by_mode else 1
        table_rows = []
        for key, label, color in mode_labels:
            count = sessions_by_mode.get(key, 0)
            percent = int((count / max_sessions) * 100) if max_sessions > 0 else 0
            table_rows.append(
                ft.Row([
                    ft.Text(label, size=14, width=120),
                    ft.ProgressBar(value=count / max_sessions if max_sessions > 0 else 0, color=color, width=180, height=12),
                    ft.Text(f"{count}", size=14, color=color, width=32)
                ], spacing=10)
            )
        mode_table = ft.Column(table_rows, spacing=6)

        # Título del dashboard
        dashboard_title = ft.Text("📊 Dashboard de Progreso y Actividad", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_800)

        # Mensaje si no hay datos
        no_data_msg = ft.Text("No hay datos suficientes para mostrar el dashboard. Realiza sesiones en los diferentes modos para ver tu progreso.", color=ft.Colors.GREY_600, size=16, italic=True) if total_sessions == 0 else None

        # Gráfico circular: Proporción de actividad por modo
        pie_chart = ft.PieChart(
            sections=[
                ft.PieChartSection(value=sessions_by_mode.get("charlemos", 0), color=ft.Colors.BLUE_600, title="Charlemos"),
                ft.PieChartSection(value=sessions_by_mode.get("estudiemos", 0), color=ft.Colors.GREEN_600, title="Estudiemos"),
                ft.PieChartSection(value=sessions_by_mode.get("evaluemos", 0), color=ft.Colors.ORANGE_600, title="Evaluemos"),
                ft.PieChartSection(value=sessions_by_mode.get("simulemos", 0), color=ft.Colors.PURPLE_600, title="Simulemos")
            ],
            sections_space=2,
            center_space_radius=40,
            height=220,
            width=220
        )

        # --- 1. Tendencia de sesiones en el tiempo ---
        progress_trends = analytics.get('progress_trends', {}) if analytics else {}
        trends_section = []
        if progress_trends.get('has_data'):
            trends_section.append(ft.Text("Tendencia de sesiones en el tiempo", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800))
            trends_section.append(
                ft.Text(f"Primera sesión: {self.format_date(progress_trends.get('first_session_date', '-'))}")
            )
            trends_section.append(
                ft.Text(f"Última sesión: {self.format_date(progress_trends.get('latest_session_date', '-'))}")
            )
            freq = progress_trends.get('session_frequency', {})
            if freq:
                trends_section.append(ft.Text(f"Sesiones por semana: {freq.get('sessions_per_week', '-')} ({freq.get('frequency_category', '-').replace('muy_alta','muy alta').replace('alta','alta').replace('moderada','moderada').replace('baja','baja')})"))
        else:
            trends_section.append(ft.Text("No hay suficientes datos para mostrar tendencias.", color=ft.Colors.GREY_600))

        # --- 2. Progreso hacia el objetivo de estudio ---
        user_profile = analytics.get('user_profile', {}) if analytics else {}
        objetivo_diario = user_profile.get('study_hours_daily', 2) or 2
        objetivo_semanal = objetivo_diario * 7
        progreso = min(total_study_hours / objetivo_semanal, 1.0) if objetivo_semanal > 0 else 0
        progreso_section = ft.Column([
            ft.Text("Progreso hacia tu objetivo semanal de estudio", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.ProgressBar(value=progreso, width=320, color=ft.Colors.BLUE_600),
            ft.Text(f"{total_study_hours}h / {objetivo_semanal}h esta semana", size=14)
        ], spacing=6)

        # --- 3. Rendimiento en evaluaciones ---
        evaluations = analytics.get('evaluations', {}) if analytics else {}
        eval_section = [ft.Text("Rendimiento en evaluaciones (EVALUEMOS)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)]
        if evaluations.get('has_data') and evaluations.get('sessions_detail'):
            eval_table = []
            eval_table.append(ft.Row([
                ft.Text("Fecha", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Duración (min)", width=90, weight=ft.FontWeight.BOLD),
                ft.Text("Preguntas", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Correctas", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Incorrectas", width=90, weight=ft.FontWeight.BOLD),
                ft.Text("% Acierto", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Temas", weight=ft.FontWeight.BOLD)
            ], spacing=8))
            for s in evaluations['sessions_detail']:
                if s.get('questions_attempted', 0) > 0:
                    eval_table.append(ft.Row([
                        ft.Text(fecha_es(s.get('date', '-')), width=80),
                        ft.Text(str(s.get('duration_minutes', '-')), width=90),
                        ft.Text(str(s.get('questions_attempted', '-')), width=80),
                        ft.Text(str(s.get('correct_answers', '-')), width=80),
                        ft.Text(str(s.get('incorrect_answers', '-')), width=90),
                        ft.Text(f"{s.get('accuracy_percent', 0)}%", width=80),
                        ft.Text(", ".join(s.get('topics_covered', [])), width=180)
                    ], spacing=8))
            eval_section.append(ft.Column(eval_table, spacing=2))
        else:
            eval_section.append(ft.Text("No hay evaluaciones registradas.", color=ft.Colors.GREY_600))

        # --- 4. Historial de simulacros ---
        simulations = analytics.get('simulations', {}) if analytics else {}
        sim_section = [ft.Text("Historial de simulacros (SIMULEMOS)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)]
        if simulations.get('has_data') and simulations.get('sessions_detail'):
            sim_table = []
            sim_table.append(ft.Row([
                ft.Text("Fecha", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Duración (min)", width=90, weight=ft.FontWeight.BOLD),
                ft.Text("Tipo", width=80, weight=ft.FontWeight.BOLD),
                ft.Text("Estado", width=80, weight=ft.FontWeight.BOLD)
            ], spacing=8))
            for s in simulations['sessions_detail']:
                sim_table.append(ft.Row([
                    ft.Text(self.format_date(s.get('date', '-')), width=80),
                    ft.Text(str(s.get('duration_minutes', '-')), width=90),
                    ft.Text(s.get('exam_type', '-').replace('completo','Completo').replace('por_tiempo','Por tiempo').replace('por_dominio','Por dominio').replace('general','General'), width=80),
                    ft.Text(s.get('completion_status', '-').replace('completado','Completado').replace('en_progreso','En progreso'), width=80)
                ], spacing=8))
            sim_section.append(ft.Column(sim_table, spacing=2))
        else:
            sim_section.append(ft.Text("No hay simulacros registrados.", color=ft.Colors.GREY_600))

        # --- 5. Temas más estudiados y menos practicados ---
        temas_counter = {}
        if evaluations.get('sessions_detail'):
            for s in evaluations['sessions_detail']:
                for t in s.get('topics_covered', []):
                    temas_counter[t] = temas_counter.get(t, 0) + 1
        temas_ranking = sorted(temas_counter.items(), key=lambda x: x[1], reverse=True)
        temas_section = [ft.Text("Ranking de temas más estudiados", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)]
        if temas_ranking:
            for tema, count in temas_ranking[:5]:
                temas_section.append(ft.Text(f"{tema}: {count} sesiones"))
        else:
            temas_section.append(ft.Text("No hay temas registrados.", color=ft.Colors.GREY_600))

        # --- 6. Consistencia y rachas ---
        racha_section = ft.Column([
            ft.Text("Consistencia y racha de estudio", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Text(f"Racha actual: {streak_days} días")
        ], spacing=4)

        # --- 7. Mejores horarios y días de estudio ---
        study_patterns = analytics.get('study_patterns', {}) if analytics else {}
        horarios_section = [ft.Text("Mejores horarios y días de estudio", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)]
        if study_patterns.get('has_data'):
            best_hour = study_patterns.get('best_study_hour', '-')
            best_day = dias_es.get(study_patterns.get('best_study_day', '-'), study_patterns.get('best_study_day', '-'))
            horarios_section.append(ft.Text(f"Mejor hora: {best_hour}h"))
            horarios_section.append(ft.Text(f"Mejor día: {best_day}"))
            # Tabla de distribución por hora
            hour_dist = study_patterns.get('hour_distribution', {})
            if hour_dist:
                hour_table = []
                for h in sorted(hour_dist.keys()):
                    hour_table.append(ft.Row([
                        ft.Text(f"{h:02d}:00", width=60),
                        ft.ProgressBar(value=hour_dist[h]/max(hour_dist.values()), width=120, color=ft.Colors.BLUE_400),
                        ft.Text(str(hour_dist[h]), width=32)
                    ], spacing=6))
                horarios_section.append(ft.Text("Distribución por hora:"))
                horarios_section.append(ft.Column(hour_table, spacing=2))
            # Tabla de distribución por día
            day_dist = study_patterns.get('day_distribution', {})
            if day_dist:
                day_table = []
                for d_en in ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]:
                    if d_en in day_dist:
                        d_es = dias_es.get(d_en, d_en)
                        day_table.append(ft.Row([
                            ft.Text(d_es, width=80),
                            ft.ProgressBar(value=day_dist[d_en]/max(day_dist.values()), width=120, color=ft.Colors.GREEN_400),
                            ft.Text(str(day_dist[d_en]), width=32)
                        ], spacing=6))
                horarios_section.append(ft.Text("Distribución por día:"))
                horarios_section.append(ft.Column(day_table, spacing=2))
        else:
            horarios_section.append(ft.Text("No hay suficientes datos para analizar horarios.", color=ft.Colors.GREY_600))

        # --- 8. Recomendaciones personalizadas ---
        recomendaciones = []
        if total_sessions == 0:
            recomendaciones.append("¡Comienza tu primera sesión para ver recomendaciones!")
        else:
            if progreso < 0.5:
                recomendaciones.append("Te recomendamos aumentar tus horas de estudio esta semana para alcanzar tu objetivo.")
            if temas_ranking:
                menos_practicado = temas_ranking[-1][0]
                recomendaciones.append(f"Dedica más tiempo a repasar el tema: {menos_practicado}.")
            if streak_days < 3:
                recomendaciones.append("Intenta mantener una racha de al menos 3 días seguidos de estudio.")
            if study_patterns.get('preferred_mode') and study_patterns['preferred_mode'] != 'evaluemos':
                recomendaciones.append("Te sugerimos realizar más evaluaciones para medir tu progreso.")
        recomendaciones_section = ft.Column([
            ft.Text("Recomendaciones personalizadas", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800)
        ] + [ft.Text(f"• {r}") for r in recomendaciones], spacing=2)

        # --- 9. Comparativa con la comunidad (placeholder) ---
        comparativa_section = ft.Column([
            ft.Text("Comparativa con la comunidad", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            ft.Text("Funcionalidad próximamente disponible. ¡Pronto podrás comparar tu progreso con otros usuarios!", color=ft.Colors.GREY_600)
        ], spacing=2)

        # --- 10. Exportar o compartir progreso (placeholder) ---
        exportar_section = ft.Row([
            ft.ElevatedButton("Exportar dashboard (próximamente)", icon=ft.Icons.DOWNLOAD)
        ], alignment=ft.MainAxisAlignment.END)

        # --- Agregar todo al contenedor principal ---
        self.chat_container.controls = [
            dashboard_title,
            ft.Divider(height=16),
            summary_cards,
            ft.Divider(height=24),
            ft.Text("Distribución de sesiones por modo", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            mode_table,
            ft.Divider(height=24),
            ft.Text("Proporción de actividad por modo", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.GREY_800),
            pie_chart,
            ft.Divider(height=24),
            *trends_section,
            ft.Divider(height=24),
            progreso_section,
            ft.Divider(height=24),
            *eval_section,
            ft.Divider(height=24),
            *sim_section,
            ft.Divider(height=24),
            *temas_section,
            ft.Divider(height=24),
            racha_section,
            ft.Divider(height=24),
            *horarios_section,
            ft.Divider(height=24),
            recomendaciones_section,
            ft.Divider(height=24),
            comparativa_section,
            ft.Divider(height=24),
            exportar_section
        ]
        if no_data_msg:
            self.chat_container.controls.append(ft.Divider(height=16))
            self.chat_container.controls.append(no_data_msg)

        # Ocultar el input de mensajes en modo dashboard
        self.message_input.visible = False
        self.send_button.visible = False

        if self.page:
            self.page.update()
    
    def build_layout(self):
        """
        Construye el layout principal con sidebar integrado (modos + conversaciones) y área de chat.
        """
        # Área de chat principal
        chat_area_controls = []
        # Mostrar cronómetro solo en modos simulemos/evaluemos
        if self.cronometro_visible:
            chat_area_controls.append(
                ft.Container(
                    content=self.cronometro_text,
                    padding=ft.padding.only(bottom=10)
                )
            )
        chat_area_controls.append(self.chat_container)
        chat_area = ft.Container(
            content=ft.Column(chat_area_controls, spacing=0),
            padding=ft.padding.all(20),
            expand=True,
            bgcolor=ft.Colors.WHITE,
            width=None,
            height=None
        )
        
        # Área de entrada de mensajes (siempre visible, excepto cuando se muestra el perfil)
        chat_controls = [chat_area]
        
        if not self.showing_profile:
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
            chat_controls.append(input_area)
        
        # Área principal de chat
        main_chat_area = ft.Column(
            controls=chat_controls,
            spacing=0,
            expand=True
        )
        
        # Construir el layout según la visibilidad del sidebar
        layout_controls = []
        
        # Sidebar integrado (modos + conversaciones)
        if self.sidebar_visible:
            sidebar_controls = [
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
                ft.Divider(height=1, color=ft.Colors.BLUE_200)
            ]
            # Solo mostrar la sección de conversaciones si el modo no es 'analicemos'
            if self.current_mode != "analicemos":
                sidebar_controls.append(
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
                )
            integrated_sidebar = ft.Container(
                content=ft.Column(
                    controls=sidebar_controls,
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
                                "🎓 Asistente para Certificación PMP",
                                size=18,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.WHITE
                            )
                        ],
                        spacing=10
                    ),
                    ft.Row(
                        controls=[
                            ft.TextButton(
                                content=ft.Text(
                                    f"👤 {self.user.username}",
                                    size=14,
                                    color=ft.Colors.WHITE70
                                ),
                                tooltip="Gestionar perfil",
                                on_click=self.show_user_profile_dialog,
                                style=ft.ButtonStyle(
                                    overlay_color=ft.Colors.WHITE12,
                                    padding=ft.padding.symmetric(8, 4)
                                )
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
        
        # Configurar modo inicial (sin modo activo al inicio)
        # self.update_charlemos_mode()  # Comentado para no activar modo por defecto
    
    def show_user_profile_dialog(self, e):
        """
        Muestra el formulario de perfil en la sección del chat.
        """
        print(f"DEBUG: Mostrando perfil de usuario en chat")
        
        # Limpiar el chat y mostrar el formulario de perfil
        self.show_profile_form()
    
    def show_profile_form(self):
        """
        Muestra el formulario de perfil directamente en el área del chat.
        """
        # Activar estado de mostrar perfil
        self.showing_profile = True
        
        # Limpiar el contenedor del chat
        self.chat_container.controls.clear()
        
        def save_profile(e):
            try:
                # Actualizar datos del usuario en la base de datos
                from db.database import DatabaseManager
                db_manager = DatabaseManager()
                
                with db_manager.get_session() as db:
                    from db.models import User
                    
                    user = db.query(User).filter(User.id == self.user.id).first()
                    if user:
                        user.username = username_field.value.strip()
                        user.email = email_field.value.strip()
                        user.full_name = full_name_field.value.strip() if full_name_field.value else None
                        user.phone = phone_field.value.strip() if phone_field.value else None
                        user.company = company_field.value.strip() if company_field.value else None
                        user.position = position_field.value.strip() if position_field.value else None
                        
                        try:
                            user.experience_years = int(experience_field.value) if experience_field.value else None
                        except ValueError:
                            user.experience_years = None
                            
                        user.target_exam_date = target_date_field.value.strip() if target_date_field.value else None
                        
                        try:
                            user.study_hours_daily = int(study_hours_field.value) if study_hours_field.value else None
                        except ValueError:
                            user.study_hours_daily = None
                        
                        db.commit()
                        
                        # Actualizar objeto usuario local
                        self.user.username = user.username
                        self.user.email = user.email
                        
                        # Actualizar header con nuevo nombre
                        self.rebuild_ui()
                        
                        # Mostrar mensaje de éxito
                        success_message = ft.Container(
                            content=ft.Text(
                                "✅ Perfil actualizado exitosamente",
                                color=ft.Colors.GREEN_600,
                                size=16,
                                weight=ft.FontWeight.BOLD
                            ),
                            padding=ft.padding.all(15),
                            margin=ft.margin.only(bottom=20),
                            bgcolor=ft.Colors.GREEN_50,
                            border_radius=8,
                            border=ft.border.all(1, ft.Colors.GREEN_200)
                        )
                        
                        self.chat_container.controls.insert(0, success_message)
                        self.page.update()
                        
                        # Volver al chat después de 2 segundos
                        import threading
                        import time
                        def return_to_chat():
                            time.sleep(2)
                            self.return_to_chat()
                        
                        threading.Thread(target=return_to_chat, daemon=True).start()
                        
            except Exception as error:
                print(f"Error al actualizar perfil: {error}")
                error_message = ft.Container(
                    content=ft.Text(
                        f"❌ Error al actualizar perfil: {str(error)}",
                        color=ft.Colors.RED_600,
                        size=14
                    ),
                    padding=ft.padding.all(15),
                    margin=ft.margin.only(bottom=20),
                    bgcolor=ft.Colors.RED_50,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.RED_200)
                )
                self.chat_container.controls.insert(0, error_message)
                self.page.update()
        
        def cancel_profile(e):
            self.return_to_chat()
        
        # Campos del formulario
        username_field = ft.TextField(
            label="Nombre de usuario",
            value=self.user.username,
            prefix_icon=ft.Icons.PERSON,
            width=400
        )
        
        email_field = ft.TextField(
            label="Email",
            value=self.user.email,
            prefix_icon=ft.Icons.EMAIL,
            width=400
        )
        
        full_name_field = ft.TextField(
            label="Nombre completo",
            value=getattr(self.user, 'full_name', '') or '',
            prefix_icon=ft.Icons.BADGE,
            width=400
        )
        
        phone_field = ft.TextField(
            label="Teléfono",
            value=getattr(self.user, 'phone', '') or '',
            prefix_icon=ft.Icons.PHONE,
            width=400
        )
        
        company_field = ft.TextField(
            label="Empresa",
            value=getattr(self.user, 'company', '') or '',
            prefix_icon=ft.Icons.BUSINESS,
            width=400
        )
        
        position_field = ft.TextField(
            label="Cargo/Posición",
            value=getattr(self.user, 'position', '') or '',
            prefix_icon=ft.Icons.WORK,
            width=400
        )
        
        experience_field = ft.TextField(
            label="Años de experiencia en PM",
            value=str(getattr(self.user, 'experience_years', '') or ''),
            prefix_icon=ft.Icons.TIMELINE,
            width=400,
            keyboard_type=ft.KeyboardType.NUMBER
        )
        
        target_date_field = ft.TextField(
            label="Fecha objetivo del examen PMP",
            value=getattr(self.user, 'target_exam_date', '') or '',
            prefix_icon=ft.Icons.CALENDAR_TODAY,
            width=400,
            hint_text="DD/MM/YYYY"
        )
        
        study_hours_field = ft.TextField(
            label="Horas de estudio diarias",
            value=str(getattr(self.user, 'study_hours_daily', '') or ''),
            prefix_icon=ft.Icons.SCHEDULE,
            width=400,
            keyboard_type=ft.KeyboardType.NUMBER,
            hint_text="2-4 horas recomendadas"
        )
        
        # Crear el formulario
        profile_form = ft.Container(
            content=ft.Column(
                controls=[
                    # Header
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Icon(ft.Icons.PERSON, color=ft.Colors.BLUE_600, size=30),
                                ft.Text("Gestión de Perfil", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700)
                            ],
                            spacing=10
                        ),
                        margin=ft.margin.only(bottom=20)
                    ),
                    
                    # Información Básica
                    ft.Text("📋 Información Básica", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_700),
                    username_field,
                    email_field,
                    full_name_field,
                    phone_field,
                    
                    ft.Divider(height=20),
                    
                    # Información Profesional
                    ft.Text("💼 Información Profesional", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_700),
                    company_field,
                    position_field,
                    experience_field,
                    
                    ft.Divider(height=20),
                    
                    # Objetivos PMP
                    ft.Text("🎯 Objetivos de Estudio PMP", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_700),
                    target_date_field,
                    study_hours_field,
                    
                    ft.Divider(height=20),
                    
                    # Botones
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "Cancelar",
                                icon=ft.Icons.CANCEL,
                                on_click=cancel_profile,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.GREY_300,
                                    color=ft.Colors.BLACK
                                )
                            ),
                            ft.ElevatedButton(
                                "Guardar Cambios",
                                icon=ft.Icons.SAVE,
                                on_click=save_profile,
                                style=ft.ButtonStyle(
                                    bgcolor=ft.Colors.BLUE_600,
                                    color=ft.Colors.WHITE
                                )
                            )
                        ],
                        alignment=ft.MainAxisAlignment.END,
                        spacing=10
                    )
                ],
                spacing=15,
                scroll=ft.ScrollMode.AUTO,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=ft.padding.all(20),
            margin=ft.margin.all(10),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.BLACK12,
                offset=ft.Offset(0, 2)
            )
        )
        
        # Agregar el formulario al chat
        self.chat_container.controls.append(profile_form)
        
        # Reconstruir el layout completo para ocultar la barra de entrada
        self.rebuild_ui()
        
        # Actualizar la página
        if self.page:
            self.page.update()
    
    def return_to_chat(self):
        """
        Regresa al chat normal desde el formulario de perfil.
        """
        # Desactivar estado de mostrar perfil
        self.showing_profile = False
        
        # Limpiar el contenedor del chat
        self.chat_container.controls.clear()
        
        # Mostrar mensaje de bienvenida o cargar historial según el modo
        if self.current_mode:
            self.load_conversation_history()
        else:
            self.show_welcome_screen()
        
        # Reconstruir el layout completo para mostrar la barra de entrada
        self.rebuild_ui()
        
        if self.page:
            self.page.update()
            
            # El focus se manejará automáticamente cuando sea necesario
    

    
    def rebuild_ui(self):
        """
        Reconstruye la interfaz de usuario para reflejar cambios en el perfil.
        """
        if self.page and len(self.page.controls) > 0:
            # Reconstruir el header
            main_layout = self.page.controls[0]
            if hasattr(main_layout, 'controls') and len(main_layout.controls) > 0:
                # Crear nuevo header
                new_header = ft.Container(
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
                                        "🎓 Asistente para Certificación PMP",
                                        size=18,
                                        weight=ft.FontWeight.BOLD,
                                        color=ft.Colors.WHITE
                                    )
                                ],
                                spacing=10
                            ),
                            ft.Row(
                                controls=[
                                    ft.TextButton(
                                        content=ft.Text(
                                            f"👤 {self.user.username}",
                                            size=14,
                                            color=ft.Colors.WHITE70
                                        ),
                                        tooltip="Gestionar perfil",
                                        on_click=self.show_user_profile_dialog,
                                        style=ft.ButtonStyle(
                                            overlay_color=ft.Colors.WHITE12,
                                            padding=ft.padding.symmetric(8, 4)
                                        )
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
                
                # Reemplazar el header
                main_layout.controls[0] = new_header
                self.page.update()
    
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

    def start_cronometro(self):
        self.cronometro_segundos = 0
        self.cronometro_visible = True
        self._cronometro_running = True
        def run():
            import time
            while self._cronometro_running:
                mins = self.cronometro_segundos // 60
                secs = self.cronometro_segundos % 60
                self.cronometro_text.value = f"⏱️ Tiempo de sesión: {mins:02d}:{secs:02d}"
                if self.page:
                    self.page.update()
                time.sleep(1)
                self.cronometro_segundos += 1
        import threading
        self._cronometro_thread = threading.Thread(target=run, daemon=True)
        self._cronometro_thread.start()

    def stop_cronometro(self):
        self.cronometro_visible = False
        self._cronometro_running = False
        self.cronometro_text.value = ""
        if self.page:
            self.page.update()

def create_app(user: User):
    """
    Función para crear y configurar la aplicación de chat.
    """
    def main(page: ft.Page):
        chat_ui = ChatUI(user)
        chat_ui.build_ui(page)
    
    return main 