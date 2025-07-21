"""
Tests unitarios para los modelos de base de datos (db/models.py).
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError
from db.models import DatabaseManager, User, ChatSession, ChatMessage
from sqlalchemy import text

class TestDatabaseManager:
    """Tests para la clase DatabaseManager."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_init(self, db_manager):
        """Test de inicialización del DatabaseManager."""
        assert db_manager is not None
        assert db_manager.engine is not None
        assert db_manager.SessionLocal is not None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_database_connection(self, db_manager):
        """Test de conexión a la base de datos."""
        with db_manager.get_session() as session:
            assert session is not None
            # Verificar que podemos hacer una consulta simple
            result = session.execute(text("SELECT 1"))
            assert result.scalar() == 1
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_session(self, db_manager):
        """Test de obtención de sesión de base de datos."""
        with db_manager.get_session() as session:
            assert session is not None
            
            # Verificar que es una sesión válida
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')

class TestUserModel:
    """Tests para el modelo User."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_user_success(self, db_manager, sample_user_data):
        """Test de creación exitosa de usuario."""
        user = db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        assert user is not None
        assert user.id is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.password_hash is not None
        assert user.salt is not None
        assert user.created_at is not None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_user_duplicate_username(self, db_manager, sample_user_data):
        """Test de creación de usuario con username duplicado."""
        # Crear primer usuario
        db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Intentar crear segundo usuario con mismo username
        with pytest.raises(ValueError, match="ya existe"):
            db_manager.create_user(
                username=sample_user_data["username"],
                email="different@example.com",
                password="DifferentPass123"
            )
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_user_duplicate_email(self, db_manager, sample_user_data):
        """Test de creación de usuario con email duplicado."""
        # Crear primer usuario
        db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Intentar crear segundo usuario con mismo email
        with pytest.raises(ValueError, match="ya está registrado"):
            db_manager.create_user(
                username="different_user",
                email=sample_user_data["email"],
                password="DifferentPass123"
            )
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_authenticate_user_success(self, db_manager, sample_user_data):
        """Test de autenticación exitosa de usuario."""
        # Crear usuario
        created_user = db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Autenticar usuario
        authenticated_user = db_manager.authenticate_user(
            username=sample_user_data["username"],
            password=sample_user_data["password"]
        )
        
        assert authenticated_user is not None
        assert authenticated_user.id == created_user.id
        assert authenticated_user.username == created_user.username
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_authenticate_user_wrong_password(self, db_manager, sample_user_data):
        """Test de autenticación con contraseña incorrecta."""
        # Crear usuario
        db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Intentar autenticar con contraseña incorrecta
        authenticated_user = db_manager.authenticate_user(
            username=sample_user_data["username"],
            password="WrongPassword123"
        )
        
        assert authenticated_user is None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_authenticate_user_nonexistent(self, db_manager):
        """Test de autenticación de usuario inexistente."""
        authenticated_user = db_manager.authenticate_user(
            username="nonexistent_user",
            password="SomePassword123"
        )
        
        assert authenticated_user is None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_user_by_id(self, db_manager, sample_user_data):
        """Test de obtención de usuario por ID."""
        # Crear usuario
        created_user = db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Obtener usuario por ID
        retrieved_user = db_manager.get_user_by_id(created_user.id)
        
        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.username == created_user.username
        assert retrieved_user.email == created_user.email
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_user_by_id_nonexistent(self, db_manager):
        """Test de obtención de usuario inexistente por ID."""
        retrieved_user = db_manager.get_user_by_id(99999)
        assert retrieved_user is None

class TestChatSessionModel:
    """Tests para el modelo ChatSession."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_chat_session_success(self, db_manager, sample_user):
        """Test de creación exitosa de sesión de chat."""
        session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            name="Sesión de Prueba"
        )
        
        assert session is not None
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.mode == "CHARLEMOS"
        assert session.name == "Sesión de Prueba"
        assert session.created_at is not None

class TestChatMessageModel:
    """Tests para el modelo ChatMessage."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_save_message_success(self, db_manager, sample_chat_session):
        """Test de guardado exitoso de mensaje."""
        message = db_manager.add_message(
            sample_chat_session.id,
            role="user",
            content="Este es un mensaje de prueba"
        )
        
        assert message is not None
        assert message.id is not None
        assert message.session_id == sample_chat_session.id
        assert message.content == "Este es un mensaje de prueba"
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_session_messages(self, db_manager, sample_chat_session):
        """Test de obtención de mensajes de una sesión."""
        # Crear múltiples mensajes
        db_manager.add_message(
            sample_chat_session.id,
            role="user",
            content="Mensaje 1"
        )
        db_manager.add_message(
            sample_chat_session.id,
            role="assistant",
            content="Mensaje 2"
        )
        messages = db_manager.get_session_messages(sample_chat_session.id)
        
        assert len(messages) == 2
        assert messages[0][0] == "user"
        assert messages[0][1] == "Mensaje 1"
        assert messages[1][0] == "assistant"
        assert messages[1][1] == "Mensaje 2"
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_session_messages_empty(self, db_manager, sample_chat_session):
        """Test de obtención de mensajes de sesión vacía."""
        messages = db_manager.get_session_messages(sample_chat_session.id)
        assert len(messages) == 0 