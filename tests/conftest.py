"""
Configuración y fixtures comunes para los tests del Asistente PMP.
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from db.models import DatabaseManager, User, ChatSession, ChatMessage
from auth import AuthManager
from chatbot import ChatBot

@pytest.fixture(scope="session")
def temp_db_path():
    """Crea una base de datos temporal para testing."""
    temp_dir = tempfile.mkdtemp()
    db_path = os.path.join(temp_dir, "test_chat_history.db")
    yield db_path
    # Limpieza después de todos los tests
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def db_manager(temp_db_path):
    """Fixture que proporciona un DatabaseManager con base de datos temporal."""
    # Crear base de datos temporal
    db_manager = DatabaseManager(f"sqlite:///{temp_db_path}")
    
    # Crear tablas
    with db_manager.get_session() as session:
        db_manager.Base.metadata.create_all(bind=session.bind)
    
    yield db_manager
    
    # Limpieza después de cada test
    with db_manager.get_session() as session:
        db_manager.Base.metadata.drop_all(bind=session.bind)

@pytest.fixture
def auth_manager(db_manager):
    """Fixture que proporciona un AuthManager configurado para testing."""
    return AuthManager()

@pytest.fixture
def sample_user_data():
    """Datos de ejemplo para crear usuarios de prueba."""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "TestPass123",
        "full_name": "Usuario de Prueba",
        "phone": "+54 11 1234-5678",
        "company": "Empresa Test",
        "position": "Project Manager",
        "experience_years": 5,
        "target_exam_date": "15/06/2024",
        "study_hours_daily": 2
    }

@pytest.fixture
def sample_user(db_manager, sample_user_data):
    """Crea un usuario de ejemplo en la base de datos."""
    user = db_manager.create_user(
        username=sample_user_data["username"],
        email=sample_user_data["email"],
        password=sample_user_data["password"]
    )
    return user

@pytest.fixture
def sample_chat_session(db_manager, sample_user):
    """Crea una sesión de chat de ejemplo."""
    session = db_manager.create_chat_session(
        user_id=sample_user.id,
        mode="CHARLEMOS",
        name="Sesión de Prueba"
    )
    return session

@pytest.fixture
def sample_messages(db_manager, sample_chat_session):
    """Crea mensajes de ejemplo en una sesión."""
    messages = []
    
    # Mensaje del usuario
    user_msg = db_manager.save_message(
        session_id=sample_chat_session.id,
        content="¿Qué es la gestión de proyectos?",
        is_user=True
    )
    messages.append(user_msg)
    
    # Respuesta del asistente
    assistant_msg = db_manager.save_message(
        session_id=sample_chat_session.id,
        content="La gestión de proyectos es la aplicación de conocimientos, habilidades, herramientas y técnicas...",
        is_user=False
    )
    messages.append(assistant_msg)
    
    return messages

@pytest.fixture
def mock_openai_response():
    """Mock de respuesta de OpenAI para testing."""
    return {
        "choices": [{
            "message": {
                "content": "Esta es una respuesta simulada del asistente PMP."
            }
        }]
    }

@pytest.fixture
def chatbot_instance(db_manager, sample_user):
    """Fixture que proporciona una instancia de ChatBot para testing."""
    return ChatBot(user_id=sample_user.id)

@pytest.fixture
def mock_env_vars():
    """Mock de variables de entorno para testing."""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test_api_key_12345',
        'PYTHON_VERSION': '3.9.0'
    }):
        yield

@pytest.fixture
def mock_flet_page():
    """Mock de una página de Flet para testing de UI."""
    mock_page = Mock()
    mock_page.title = "Test Page"
    mock_page.window_width = 1200
    mock_page.window_height = 800
    mock_page.views = []
    mock_page.controls = []
    
    def mock_add(control):
        mock_page.controls.append(control)
    
    def mock_update():
        pass
    
    mock_page.add = mock_add
    mock_page.update = mock_update
    
    return mock_page

@pytest.fixture
def test_data_dir():
    """Directorio temporal para archivos de test."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

# Configuración de pytest
def pytest_configure(config):
    """Configuración adicional de pytest."""
    # Agregar marcadores personalizados
    config.addinivalue_line(
        "markers", "unit: marca tests unitarios"
    )
    config.addinivalue_line(
        "markers", "integration: marca tests de integración"
    )
    config.addinivalue_line(
        "markers", "slow: marca tests que tardan más tiempo"
    )
    config.addinivalue_line(
        "markers", "auth: marca tests relacionados con autenticación"
    )
    config.addinivalue_line(
        "markers", "chatbot: marca tests relacionados con el chatbot"
    )
    config.addinivalue_line(
        "markers", "database: marca tests relacionados con la base de datos"
    )
    config.addinivalue_line(
        "markers", "ui: marca tests relacionados con la interfaz de usuario"
    ) 