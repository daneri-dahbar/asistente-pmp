"""
Tests unitarios para el módulo del chatbot (chatbot.py).
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from chatbot import ChatBot

class TestChatBot:
    """Tests para la clase ChatBot."""
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_init(self, chatbot_instance, sample_user):
        """Test de inicialización del ChatBot."""
        assert chatbot_instance is not None
        assert chatbot_instance.user_id == sample_user.id
        assert chatbot_instance.db_manager is not None
        assert chatbot_instance.current_session is None
        assert chatbot_instance.mode == "CHARLEMOS"
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_switch_mode(self, chatbot_instance):
        """Test de cambio de modo."""
        # Cambiar a modo ESTUDIEMOS
        chatbot_instance.switch_mode("ESTUDIEMOS")
        assert chatbot_instance.mode == "ESTUDIEMOS"
        
        # Cambiar a modo EVALUEMOS
        chatbot_instance.switch_mode("EVALUEMOS")
        assert chatbot_instance.mode == "EVALUEMOS"
        
        # Cambiar a modo SIMULEMOS
        chatbot_instance.switch_mode("SIMULEMOS")
        assert chatbot_instance.mode == "SIMULEMOS"
        
        # Cambiar a modo ANALICEMOS
        chatbot_instance.switch_mode("ANALICEMOS")
        assert chatbot_instance.mode == "ANALICEMOS"
        
        # Volver a CHARLEMOS
        chatbot_instance.switch_mode("CHARLEMOS")
        assert chatbot_instance.mode == "CHARLEMOS"
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_switch_mode_invalid(self, chatbot_instance):
        """Test de cambio a modo inválido."""
        original_mode = chatbot_instance.mode
        
        # Intentar cambiar a modo inválido
        chatbot_instance.switch_mode("MODO_INVALIDO")
        
        # Debe mantener el modo original
        assert chatbot_instance.mode == original_mode
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_create_new_session(self, chatbot_instance, sample_user):
        """Test de creación de nueva sesión."""
        session = chatbot_instance.create_new_session("Nueva Sesión de Prueba")
        
        assert session is not None
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.mode == chatbot_instance.mode
        assert session.title == "Nueva Sesión de Prueba"
        assert chatbot_instance.current_session == session
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_load_session(self, chatbot_instance, sample_chat_session):
        """Test de carga de sesión existente."""
        chatbot_instance.load_session(sample_chat_session.id)
        
        assert chatbot_instance.current_session is not None
        assert chatbot_instance.current_session.id == sample_chat_session.id
        assert chatbot_instance.mode == sample_chat_session.mode
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_load_session_nonexistent(self, chatbot_instance):
        """Test de carga de sesión inexistente."""
        with pytest.raises(ValueError, match="no encontrada"):
            chatbot_instance.load_session(99999)
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_system_prompt_charlemos(self, chatbot_instance):
        """Test de obtención del prompt del sistema para modo CHARLEMOS."""
        chatbot_instance.switch_mode("CHARLEMOS")
        prompt = chatbot_instance.get_system_prompt()
        
        assert "CHARLEMOS" in prompt
        assert "conversación libre" in prompt.lower()
        assert "PMP" in prompt
        assert "PMBOK" in prompt
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_system_prompt_estudiemos(self, chatbot_instance):
        """Test de obtención del prompt del sistema para modo ESTUDIEMOS."""
        chatbot_instance.switch_mode("ESTUDIEMOS")
        prompt = chatbot_instance.get_system_prompt()
        
        assert "ESTUDIEMOS" in prompt
        assert "estructurado" in prompt.lower()
        assert "sesión de aprendizaje" in prompt.lower()
        assert "PMP" in prompt
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_system_prompt_evaluemos(self, chatbot_instance):
        """Test de obtención del prompt del sistema para modo EVALUEMOS."""
        chatbot_instance.switch_mode("EVALUEMOS")
        prompt = chatbot_instance.get_system_prompt()
        
        assert "EVALUEMOS" in prompt
        assert "evaluación" in prompt.lower()
        assert "práctica" in prompt.lower()
        assert "preguntas" in prompt.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_system_prompt_simulemos(self, chatbot_instance):
        """Test de obtención del prompt del sistema para modo SIMULEMOS."""
        chatbot_instance.switch_mode("SIMULEMOS")
        prompt = chatbot_instance.get_system_prompt()
        
        assert "SIMULEMOS" in prompt
        assert "simulacro" in prompt.lower()
        assert "examen" in prompt.lower()
        assert "180 preguntas" in prompt
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_system_prompt_analicemos(self, chatbot_instance):
        """Test de obtención del prompt del sistema para modo ANALICEMOS."""
        chatbot_instance.switch_mode("ANALICEMOS")
        prompt = chatbot_instance.get_system_prompt()
        
        assert "ANALICEMOS" in prompt
        assert "análisis" in prompt.lower()
        assert "progreso" in prompt.lower()
        assert "estadísticas" in prompt.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_build_context_from_history(self, chatbot_instance, sample_chat_session, sample_messages):
        """Test de construcción de contexto desde historial."""
        chatbot_instance.load_session(sample_chat_session.id)
        
        context = chatbot_instance.build_context_from_history()
        
        assert context is not None
        assert len(context) > 0
        assert "historial" in context.lower()
        assert "mensajes" in context.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_build_context_from_history_empty(self, chatbot_instance, sample_chat_session):
        """Test de construcción de contexto con historial vacío."""
        chatbot_instance.load_session(sample_chat_session.id)
        
        context = chatbot_instance.build_context_from_history()
        
        assert context is not None
        assert "sin historial previo" in context.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_build_context_from_history_no_session(self, chatbot_instance):
        """Test de construcción de contexto sin sesión activa."""
        context = chatbot_instance.build_context_from_history()
        
        assert context is not None
        assert "sin sesión activa" in context.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    @patch('chatbot.openai.ChatCompletion.create')
    def test_send_message_success(self, mock_openai_create, chatbot_instance, sample_chat_session, mock_openai_response):
        """Test de envío exitoso de mensaje."""
        # Configurar mock
        mock_openai_create.return_value = mock_openai_response
        
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Enviar mensaje
        response = chatbot_instance.send_message("¿Qué es la gestión de proyectos?")
        
        assert response is not None
        assert "respuesta simulada" in response.lower()
        
        # Verificar que se llamó a OpenAI
        mock_openai_create.assert_called_once()
        
        # Verificar que el mensaje se guardó
        messages = chatbot_instance.db_manager.get_session_messages(sample_chat_session.id)
        assert len(messages) >= 2  # Mensaje del usuario + respuesta del asistente
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    @patch('chatbot.openai.ChatCompletion.create')
    def test_send_message_no_session(self, mock_openai_create, chatbot_instance, mock_openai_response):
        """Test de envío de mensaje sin sesión activa."""
        # Configurar mock
        mock_openai_create.return_value = mock_openai_response
        
        # Enviar mensaje sin sesión activa
        response = chatbot_instance.send_message("¿Qué es la gestión de proyectos?")
        
        assert response is not None
        assert "respuesta simulada" in response.lower()
        
        # Verificar que se creó una nueva sesión
        assert chatbot_instance.current_session is not None
        assert chatbot_instance.current_session.title is not None
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    @patch('chatbot.openai.ChatCompletion.create')
    def test_send_message_openai_error(self, mock_openai_create, chatbot_instance, sample_chat_session):
        """Test de envío de mensaje con error de OpenAI."""
        # Configurar mock para simular error
        mock_openai_create.side_effect = Exception("Error de API")
        
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Enviar mensaje
        response = chatbot_instance.send_message("¿Qué es la gestión de proyectos?")
        
        assert response is not None
        assert "error" in response.lower()
        assert "disculpa" in response.lower()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    @patch('chatbot.openai.ChatCompletion.create')
    def test_send_message_empty_content(self, mock_openai_create, chatbot_instance, sample_chat_session):
        """Test de envío de mensaje con contenido vacío."""
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Enviar mensaje vacío
        response = chatbot_instance.send_message("")
        
        assert response is not None
        assert "mensaje vacío" in response.lower() or "contenido" in response.lower()
        
        # Verificar que NO se llamó a OpenAI
        mock_openai_create.assert_not_called()
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_user_sessions(self, chatbot_instance, sample_user):
        """Test de obtención de sesiones del usuario."""
        # Crear múltiples sesiones
        session1 = chatbot_instance.create_new_session("Sesión 1")
        session2 = chatbot_instance.create_new_session("Sesión 2")
        
        # Obtener sesiones
        sessions = chatbot_instance.get_user_sessions()
        
        assert len(sessions) >= 2
        session_ids = [s.id for s in sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_user_sessions_empty(self, chatbot_instance):
        """Test de obtención de sesiones cuando no hay ninguna."""
        sessions = chatbot_instance.get_user_sessions()
        assert len(sessions) == 0
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_delete_session(self, chatbot_instance, sample_chat_session):
        """Test de eliminación de sesión."""
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Verificar que la sesión está activa
        assert chatbot_instance.current_session is not None
        
        # Eliminar sesión
        chatbot_instance.delete_session(sample_chat_session.id)
        
        # Verificar que la sesión ya no está activa
        assert chatbot_instance.current_session is None
        
        # Verificar que la sesión ya no existe en la base de datos
        with pytest.raises(ValueError):
            chatbot_instance.db_manager.get_chat_session_by_id(sample_chat_session.id)
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_delete_session_nonexistent(self, chatbot_instance):
        """Test de eliminación de sesión inexistente."""
        with pytest.raises(ValueError, match="no encontrada"):
            chatbot_instance.delete_session(99999)
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_rename_session(self, chatbot_instance, sample_chat_session):
        """Test de renombrado de sesión."""
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Renombrar sesión
        new_title = "Nuevo Título de Sesión"
        updated_session = chatbot_instance.rename_session(sample_chat_session.id, new_title)
        
        assert updated_session is not None
        assert updated_session.title == new_title
        
        # Verificar que la sesión actual también se actualizó
        assert chatbot_instance.current_session.title == new_title
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_rename_session_nonexistent(self, chatbot_instance):
        """Test de renombrado de sesión inexistente."""
        with pytest.raises(ValueError, match="no encontrada"):
            chatbot_instance.rename_session(99999, "Nuevo Título")
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_session_messages(self, chatbot_instance, sample_chat_session, sample_messages):
        """Test de obtención de mensajes de una sesión."""
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Obtener mensajes
        messages = chatbot_instance.get_session_messages()
        
        assert len(messages) == len(sample_messages)
        for i, message in enumerate(messages):
            assert message.id == sample_messages[i].id
            assert message.content == sample_messages[i].content
            assert message.is_user == sample_messages[i].is_user
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_session_messages_no_session(self, chatbot_instance):
        """Test de obtención de mensajes sin sesión activa."""
        messages = chatbot_instance.get_session_messages()
        assert len(messages) == 0

class TestChatBotAnalytics:
    """Tests para las funcionalidades de análisis del ChatBot."""
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_user_analytics(self, chatbot_instance, sample_user):
        """Test de obtención de analytics del usuario."""
        # Crear múltiples sesiones con diferentes modos
        chatbot_instance.switch_mode("CHARLEMOS")
        session1 = chatbot_instance.create_new_session("Sesión CHARLEMOS")
        
        chatbot_instance.switch_mode("ESTUDIEMOS")
        session2 = chatbot_instance.create_new_session("Sesión ESTUDIEMOS")
        
        chatbot_instance.switch_mode("EVALUEMOS")
        session3 = chatbot_instance.create_new_session("Sesión EVALUEMOS")
        
        # Agregar algunos mensajes
        chatbot_instance.send_message("Mensaje de prueba 1")
        chatbot_instance.load_session(session2.id)
        chatbot_instance.send_message("Mensaje de prueba 2")
        
        # Obtener analytics
        analytics = chatbot_instance.get_user_analytics()
        
        assert analytics is not None
        assert "total_sessions" in analytics
        assert "total_messages" in analytics
        assert "sessions_by_mode" in analytics
        assert "recent_activity" in analytics
        
        # Verificar datos básicos
        assert analytics["total_sessions"] >= 3
        assert analytics["total_messages"] >= 2
        assert len(analytics["sessions_by_mode"]) >= 3
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_user_analytics_empty(self, chatbot_instance):
        """Test de obtención de analytics para usuario sin actividad."""
        analytics = chatbot_instance.get_user_analytics()
        
        assert analytics is not None
        assert analytics["total_sessions"] == 0
        assert analytics["total_messages"] == 0
        assert len(analytics["sessions_by_mode"]) == 0
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_session_analytics(self, chatbot_instance, sample_chat_session, sample_messages):
        """Test de obtención de analytics de una sesión específica."""
        # Cargar sesión
        chatbot_instance.load_session(sample_chat_session.id)
        
        # Obtener analytics de la sesión
        analytics = chatbot_instance.get_session_analytics(sample_chat_session.id)
        
        assert analytics is not None
        assert "session_id" in analytics
        assert "total_messages" in analytics
        assert "user_messages" in analytics
        assert "assistant_messages" in analytics
        assert "session_duration" in analytics
        
        # Verificar datos
        assert analytics["session_id"] == sample_chat_session.id
        assert analytics["total_messages"] == len(sample_messages)
        assert analytics["user_messages"] == len([m for m in sample_messages if m.is_user])
        assert analytics["assistant_messages"] == len([m for m in sample_messages if not m.is_user])
    
    @pytest.mark.unit
    @pytest.mark.chatbot
    def test_get_session_analytics_nonexistent(self, chatbot_instance):
        """Test de obtención de analytics de sesión inexistente."""
        with pytest.raises(ValueError, match="no encontrada"):
            chatbot_instance.get_session_analytics(99999)

class TestChatBotIntegration:
    """Tests de integración del ChatBot."""
    
    @pytest.mark.integration
    @pytest.mark.chatbot
    def test_full_conversation_flow(self, chatbot_instance, sample_user):
        """Test de flujo completo de conversación."""
        # Crear nueva sesión
        session = chatbot_instance.create_new_session("Conversación Completa")
        
        # Enviar múltiples mensajes
        messages = [
            "¿Qué es la gestión de proyectos?",
            "¿Cuáles son las áreas de conocimiento del PMBOK?",
            "Explícame sobre la gestión de riesgos"
        ]
        
        responses = []
        for message in messages:
            response = chatbot_instance.send_message(message)
            responses.append(response)
            assert response is not None
            assert len(response) > 0
        
        # Verificar que todos los mensajes se guardaron
        saved_messages = chatbot_instance.get_session_messages()
        assert len(saved_messages) == len(messages) * 2  # Mensaje del usuario + respuesta del asistente
        
        # Verificar analytics
        analytics = chatbot_instance.get_session_analytics(session.id)
        assert analytics["total_messages"] == len(messages) * 2
        assert analytics["user_messages"] == len(messages)
        assert analytics["assistant_messages"] == len(messages)
    
    @pytest.mark.integration
    @pytest.mark.chatbot
    def test_mode_switching_with_sessions(self, chatbot_instance, sample_user):
        """Test de cambio de modos con sesiones."""
        # Crear sesiones en diferentes modos
        modes = ["CHARLEMOS", "ESTUDIEMOS", "EVALUEMOS", "SIMULEMOS", "ANALICEMOS"]
        sessions = []
        
        for mode in modes:
            chatbot_instance.switch_mode(mode)
            session = chatbot_instance.create_new_session(f"Sesión {mode}")
            sessions.append(session)
            
            # Enviar un mensaje en cada modo
            response = chatbot_instance.send_message(f"Mensaje en modo {mode}")
            assert response is not None
        
        # Verificar que todas las sesiones se crearon
        user_sessions = chatbot_instance.get_user_sessions()
        assert len(user_sessions) >= len(modes)
        
        # Verificar analytics por modo
        analytics = chatbot_instance.get_user_analytics()
        assert len(analytics["sessions_by_mode"]) >= len(modes) 