"""
Tests unitarios para los modelos de base de datos (db/models.py).
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from sqlalchemy.exc import IntegrityError
from db.models import DatabaseManager, User, ChatSession, ChatMessage

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
            result = session.execute("SELECT 1")
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
        assert user.updated_at is not None
        
        # Verificar que la contraseña está hasheada
        assert user.password_hash != sample_user_data["password"]
    
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
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_update_user_profile(self, db_manager, sample_user_data):
        """Test de actualización del perfil de usuario."""
        # Crear usuario
        user = db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Actualizar perfil
        updated_data = {
            "full_name": "Nombre Actualizado",
            "phone": "+54 11 9876-5432",
            "company": "Nueva Empresa",
            "position": "Senior PM",
            "experience_years": 10,
            "target_exam_date": "01/12/2024",
            "study_hours_daily": 3
        }
        
        updated_user = db_manager.update_user_profile(user.id, updated_data)
        
        assert updated_user is not None
        assert updated_user.full_name == updated_data["full_name"]
        assert updated_user.phone == updated_data["phone"]
        assert updated_user.company == updated_data["company"]
        assert updated_user.position == updated_data["position"]
        assert updated_user.experience_years == updated_data["experience_years"]
        assert updated_user.target_exam_date == updated_data["target_exam_date"]
        assert updated_user.study_hours_daily == updated_data["study_hours_daily"]

class TestChatSessionModel:
    """Tests para el modelo ChatSession."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_chat_session_success(self, db_manager, sample_user):
        """Test de creación exitosa de sesión de chat."""
        session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión de Prueba"
        )
        
        assert session is not None
        assert session.id is not None
        assert session.user_id == sample_user.id
        assert session.mode == "CHARLEMOS"
        assert session.title == "Sesión de Prueba"
        assert session.created_at is not None
        assert session.updated_at is not None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_create_chat_session_invalid_user(self, db_manager):
        """Test de creación de sesión con usuario inexistente."""
        with pytest.raises(ValueError, match="no encontrado"):
            db_manager.create_chat_session(
                user_id=99999,
                mode="CHARLEMOS",
                title="Sesión de Prueba"
            )
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_user_chat_sessions(self, db_manager, sample_user):
        """Test de obtención de sesiones de chat de un usuario."""
        # Crear múltiples sesiones
        session1 = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión 1"
        )
        session2 = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="ESTUDIEMOS",
            title="Sesión 2"
        )
        
        # Obtener sesiones del usuario
        sessions = db_manager.get_user_chat_sessions(sample_user.id)
        
        assert len(sessions) == 2
        session_ids = [s.id for s in sessions]
        assert session1.id in session_ids
        assert session2.id in session_ids
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_chat_session_by_id(self, db_manager, sample_user):
        """Test de obtención de sesión por ID."""
        # Crear sesión
        created_session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión de Prueba"
        )
        
        # Obtener sesión por ID
        retrieved_session = db_manager.get_chat_session_by_id(created_session.id)
        
        assert retrieved_session is not None
        assert retrieved_session.id == created_session.id
        assert retrieved_session.user_id == created_session.user_id
        assert retrieved_session.mode == created_session.mode
        assert retrieved_session.title == created_session.title
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_chat_session_by_id_nonexistent(self, db_manager):
        """Test de obtención de sesión inexistente por ID."""
        retrieved_session = db_manager.get_chat_session_by_id(99999)
        assert retrieved_session is None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_update_chat_session_title(self, db_manager, sample_user):
        """Test de actualización del título de sesión."""
        # Crear sesión
        session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Título Original"
        )
        
        # Actualizar título
        updated_session = db_manager.update_chat_session_title(
            session.id,
            "Nuevo Título"
        )
        
        assert updated_session is not None
        assert updated_session.title == "Nuevo Título"
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_delete_chat_session(self, db_manager, sample_user):
        """Test de eliminación de sesión de chat."""
        # Crear sesión
        session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión a Eliminar"
        )
        
        # Verificar que existe
        assert db_manager.get_chat_session_by_id(session.id) is not None
        
        # Eliminar sesión
        db_manager.delete_chat_session(session.id)
        
        # Verificar que ya no existe
        assert db_manager.get_chat_session_by_id(session.id) is None

class TestChatMessageModel:
    """Tests para el modelo ChatMessage."""
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_save_message_success(self, db_manager, sample_chat_session):
        """Test de guardado exitoso de mensaje."""
        message = db_manager.save_message(
            session_id=sample_chat_session.id,
            content="Este es un mensaje de prueba",
            is_user=True
        )
        
        assert message is not None
        assert message.id is not None
        assert message.session_id == sample_chat_session.id
        assert message.content == "Este es un mensaje de prueba"
        assert message.is_user is True
        assert message.created_at is not None
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_save_message_invalid_session(self, db_manager):
        """Test de guardado de mensaje con sesión inexistente."""
        with pytest.raises(ValueError, match="no encontrada"):
            db_manager.save_message(
                session_id=99999,
                content="Mensaje de prueba",
                is_user=True
            )
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_session_messages(self, db_manager, sample_chat_session):
        """Test de obtención de mensajes de una sesión."""
        # Crear múltiples mensajes
        message1 = db_manager.save_message(
            session_id=sample_chat_session.id,
            content="Mensaje 1",
            is_user=True
        )
        message2 = db_manager.save_message(
            session_id=sample_chat_session.id,
            content="Mensaje 2",
            is_user=False
        )
        
        # Obtener mensajes de la sesión
        messages = db_manager.get_session_messages(sample_chat_session.id)
        
        assert len(messages) == 2
        message_ids = [m.id for m in messages]
        assert message1.id in message_ids
        assert message2.id in message_ids
        
        # Verificar orden cronológico
        assert messages[0].created_at <= messages[1].created_at
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_session_messages_empty(self, db_manager, sample_chat_session):
        """Test de obtención de mensajes de sesión vacía."""
        messages = db_manager.get_session_messages(sample_chat_session.id)
        assert len(messages) == 0
    
    @pytest.mark.unit
    @pytest.mark.database
    def test_get_latest_chat_session(self, db_manager, sample_user):
        """Test de obtención de la sesión más reciente."""
        # Crear sesiones con diferentes fechas
        session1 = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión Antigua"
        )
        
        # Simular que la primera sesión es más antigua
        with db_manager.get_session() as session:
            session1_db = session.query(ChatSession).filter_by(id=session1.id).first()
            session1_db.created_at = datetime.now() - timedelta(hours=2)
            session.commit()
        
        session2 = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="ESTUDIEMOS",
            title="Sesión Reciente"
        )
        
        # Obtener sesión más reciente
        latest_session = db_manager.get_latest_chat_session(sample_user.id)
        
        assert latest_session is not None
        assert latest_session.id == session2.id
        assert latest_session.title == "Sesión Reciente"

class TestDatabaseIntegrity:
    """Tests de integridad de la base de datos."""
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_cascade_delete_session_messages(self, db_manager, sample_user):
        """Test de eliminación en cascada de mensajes al eliminar sesión."""
        # Crear sesión con mensajes
        session = db_manager.create_chat_session(
            user_id=sample_user.id,
            mode="CHARLEMOS",
            title="Sesión con Mensajes"
        )
        
        message1 = db_manager.save_message(
            session_id=session.id,
            content="Mensaje 1",
            is_user=True
        )
        message2 = db_manager.save_message(
            session_id=session.id,
            content="Mensaje 2",
            is_user=False
        )
        
        # Verificar que los mensajes existen
        messages = db_manager.get_session_messages(session.id)
        assert len(messages) == 2
        
        # Eliminar sesión
        db_manager.delete_chat_session(session.id)
        
        # Verificar que los mensajes también se eliminaron
        with db_manager.get_session() as db_session:
            remaining_messages = db_session.query(ChatMessage).filter_by(session_id=session.id).all()
            assert len(remaining_messages) == 0
    
    @pytest.mark.integration
    @pytest.mark.database
    def test_user_profile_completeness(self, db_manager, sample_user_data):
        """Test de completitud del perfil de usuario."""
        # Crear usuario con datos mínimos
        user = db_manager.create_user(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"]
        )
        
        # Verificar que los campos opcionales están en None
        assert user.full_name is None
        assert user.phone is None
        assert user.company is None
        assert user.position is None
        assert user.experience_years is None
        assert user.target_exam_date is None
        assert user.study_hours_daily is None
        
        # Actualizar perfil completo
        profile_data = {
            "full_name": sample_user_data["full_name"],
            "phone": sample_user_data["phone"],
            "company": sample_user_data["company"],
            "position": sample_user_data["position"],
            "experience_years": sample_user_data["experience_years"],
            "target_exam_date": sample_user_data["target_exam_date"],
            "study_hours_daily": sample_user_data["study_hours_daily"]
        }
        
        updated_user = db_manager.update_user_profile(user.id, profile_data)
        
        # Verificar que todos los campos se actualizaron 