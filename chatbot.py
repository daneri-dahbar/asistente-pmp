"""
Lógica del chatbot utilizando LangChain y OpenAI.
Maneja la conversación y el historial de mensajes.
"""

import os
from typing import List, Tuple
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from db.models import DatabaseManager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class ChatBot:
    """
    Clase principal del chatbot que integra OpenAI con LangChain
    y maneja la persistencia de datos.
    """
    
    def __init__(self, user_id: int):
        """
        Inicializa el chatbot con configuración de OpenAI y base de datos.
        
        Args:
            user_id (int): ID del usuario autenticado
        """
        self.user_id = user_id
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no encontrada en variables de entorno")
        
        # Inicializar el modelo de OpenAI
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",  # Modelo más reciente y eficiente
            temperature=0.7,
            api_key=self.api_key
        )
        
        # Inicializar base de datos
        self.db_manager = DatabaseManager()
        
        # Obtener o crear sesión actual para el usuario
        self.current_session = self.db_manager.get_latest_chat_session(user_id)
        
        # Cargar historial existente
        self.conversation_history = []
        self._load_conversation_history()
        
        # Mensaje del sistema para definir el comportamiento
        self.system_message = SystemMessage(
            content="Eres un asistente de IA útil y amigable. "
                   "Responde de manera clara, concisa y educada. "
                   "Puedes ayudar con una amplia variedad de temas."
        )
    
    def _load_conversation_history(self):
        """
        Carga el historial de conversación desde la base de datos.
        """
        messages = self.db_manager.get_session_messages(self.current_session.id)
        self.conversation_history = []
        
        for role, content in messages:
            if role == "user":
                self.conversation_history.append(HumanMessage(content=content))
            elif role == "assistant":
                self.conversation_history.append(AIMessage(content=content))
    
    def send_message(self, user_message: str) -> str:
        """
        Envía un mensaje del usuario y obtiene la respuesta de la IA.
        
        Args:
            user_message (str): Mensaje del usuario
            
        Returns:
            str: Respuesta de la IA
        """
        try:
            # Crear mensaje del usuario
            human_message = HumanMessage(content=user_message)
            
            # Construir el historial completo para enviar a la IA
            messages_to_send = [self.system_message] + self.conversation_history + [human_message]
            
            # Obtener respuesta de OpenAI
            response = self.llm.invoke(messages_to_send)
            ai_response = response.content
            
            # Guardar ambos mensajes en el historial local
            self.conversation_history.append(human_message)
            self.conversation_history.append(AIMessage(content=ai_response))
            
            # Guardar en base de datos
            self.db_manager.add_message(self.current_session.id, "user", user_message)
            self.db_manager.add_message(self.current_session.id, "assistant", ai_response)
            
            return ai_response
            
        except Exception as e:
            error_message = f"Error al procesar el mensaje: {str(e)}"
            print(f"Error en chatbot: {error_message}")
            return "Lo siento, ocurrió un error al procesar tu mensaje. Por favor, intenta de nuevo."
    
    def get_conversation_history(self) -> List[Tuple[str, str]]:
        """
        Retorna el historial de conversación en formato de tuplas (role, content).
        
        Returns:
            List[Tuple[str, str]]: Lista de mensajes como (role, content)
        """
        history = []
        for message in self.conversation_history:
            if isinstance(message, HumanMessage):
                history.append(("user", message.content))
            elif isinstance(message, AIMessage):
                history.append(("assistant", message.content))
        return history
    
    def start_new_conversation(self, name: str = "Nueva Conversación"):
        """
        Inicia una nueva conversación.
        
        Args:
            name (str): Nombre para la nueva conversación
        """
        self.current_session = self.db_manager.create_chat_session(self.user_id, name)
        self.conversation_history = []
    
    def is_api_key_valid(self) -> bool:
        """
        Verifica si la clave API está configurada.
        
        Returns:
            bool: True si la clave API está disponible
        """
        return bool(self.api_key) 