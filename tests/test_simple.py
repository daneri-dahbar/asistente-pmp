"""
Tests simplificados para verificar la funcionalidad básica del proyecto.
Estos tests están diseñados para funcionar con la estructura actual del código.
"""

import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from auth import AuthManager
from db.models import DatabaseManager, User, ChatSession, ChatMessage
from main import MainApp


class TestAuthManager:
    """Tests básicos para AuthManager"""
    
    def test_auth_manager_initialization(self):
        """Test que AuthManager se inicializa correctamente"""
        auth_manager = AuthManager()
        assert auth_manager is not None
        assert auth_manager.current_user is None
        assert auth_manager.db_manager is not None
    
    def test_validate_registration_data_valid(self):
        """Test validación de datos de registro válidos"""
        auth_manager = AuthManager()
        result, message = auth_manager._validate_registration_data(
            "testuser", "test@example.com", "password123", "password123"
        )
        assert result is True
        assert "válidos" in message
    
    def test_validate_registration_data_invalid_username(self):
        """Test validación de username inválido"""
        auth_manager = AuthManager()
        result, message = auth_manager._validate_registration_data(
            "ab", "test@example.com", "password123", "password123"
        )
        assert result is False
        assert "3 caracteres" in message
    
    def test_validate_registration_data_invalid_email(self):
        """Test validación de email inválido"""
        auth_manager = AuthManager()
        result, message = auth_manager._validate_registration_data(
            "testuser", "invalid-email", "password123", "password123"
        )
        assert result is False
        assert "email inválido" in message
    
    def test_validate_registration_data_password_mismatch(self):
        """Test validación de contraseñas que no coinciden"""
        auth_manager = AuthManager()
        result, message = auth_manager._validate_registration_data(
            "testuser", "test@example.com", "password123", "different123"
        )
        assert result is False
        assert "no coinciden" in message
    
    def test_get_password_strength(self):
        """Test evaluación de fortaleza de contraseña"""
        auth_manager = AuthManager()
        strength, description = auth_manager.get_password_strength("weak")
        assert strength == "Débil"
        
        strength, description = auth_manager.get_password_strength("StrongPass123!")
        assert strength in ["Fuerte", "Muy fuerte"]


class TestDatabaseManager:
    """Tests básicos para DatabaseManager"""
    
    def test_database_manager_initialization(self):
        """Test que DatabaseManager se inicializa correctamente"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(f"sqlite:///{db_path}")
            assert db_manager is not None
            assert db_manager.engine is not None
            assert db_manager.SessionLocal is not None
        finally:
            try:
                os.unlink(db_path)
            except PermissionError:
                # En Windows, el archivo puede estar en uso
                pass
    
    def test_get_session(self):
        """Test que get_session retorna una sesión válida"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            db_manager = DatabaseManager(f"sqlite:///{db_path}")
            session = db_manager.get_session()
            assert session is not None
            session.close()
        finally:
            try:
                os.unlink(db_path)
            except PermissionError:
                # En Windows, el archivo puede estar en uso
                pass


class TestUserModel:
    """Tests básicos para el modelo User"""
    
    def test_user_password_hashing(self):
        """Test que el hashing de contraseñas funciona correctamente"""
        user = User(username="testuser", email="test@example.com")
        password = "testpassword123"
        
        user.set_password(password)
        assert user.password_hash is not None
        assert user.salt is not None
        assert user.check_password(password) is True
        assert user.check_password("wrongpassword") is False
    
    def test_user_creation(self):
        """Test creación básica de usuario"""
        user = User(
            username="testuser",
            email="test@example.com",
            full_name="Test User",
            company="Test Company"
        )
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.full_name == "Test User"
        assert user.company == "Test Company"


class TestChatSessionModel:
    """Tests básicos para el modelo ChatSession"""
    
    def test_chat_session_creation(self):
        """Test creación básica de sesión de chat"""
        session = ChatSession(
            user_id=1,
            name="Test Session",
            mode="charlemos"
        )
        assert session.user_id == 1
        assert session.name == "Test Session"
        assert session.mode == "charlemos"


class TestChatMessageModel:
    """Tests básicos para el modelo ChatMessage"""
    
    def test_chat_message_creation(self):
        """Test creación básica de mensaje de chat"""
        message = ChatMessage(
            session_id=1,
            role="user",
            content="Hello, this is a test message"
        )
        assert message.session_id == 1
        assert message.role == "user"
        assert message.content == "Hello, this is a test message"


class TestMainApp:
    """Tests básicos para MainApp"""
    
    def test_main_app_initialization(self):
        """Test que MainApp se inicializa correctamente"""
        app = MainApp()
        assert app is not None
        assert app.authenticated_user is None
        assert app.page is None
        assert app.auth_ui is None
        assert app.chat_ui is None
    
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_missing_env_file(self, mock_getenv, mock_exists):
        """Test verificación de entorno sin archivo .env"""
        mock_exists.return_value = False
        mock_getenv.return_value = None
        
        app = MainApp()
        result = app.check_environment()
        assert result is False
    
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_missing_api_key(self, mock_getenv, mock_exists):
        """Test verificación de entorno sin API key"""
        mock_exists.return_value = True
        mock_getenv.return_value = None
        
        app = MainApp()
        result = app.check_environment()
        assert result is False
    
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_valid(self, mock_getenv, mock_exists):
        """Test verificación de entorno válido"""
        mock_exists.return_value = True
        mock_getenv.return_value = "valid-api-key"
        
        app = MainApp()
        result = app.check_environment()
        assert result is True
    
    def test_on_auth_success(self):
        """Test callback de autenticación exitosa"""
        app = MainApp()
        mock_user = MagicMock()
        mock_user.username = "testuser"
        
        # Mock de los métodos que se llaman
        with patch.object(app, 'show_chat') as mock_show_chat:
            app.on_auth_success(mock_user)
            
            assert app.authenticated_user == mock_user
            mock_show_chat.assert_called_once()
    
    def test_on_logout(self):
        """Test callback de logout"""
        app = MainApp()
        app.authenticated_user = MagicMock()
        
        # Mock de los métodos que se llaman
        with patch.object(app, 'show_auth') as mock_show_auth:
            app.on_logout()
            
            assert app.authenticated_user is None
            mock_show_auth.assert_called_once()


class TestIntegration:
    """Tests de integración básicos"""
    
    def test_auth_manager_with_database(self):
        """Test integración entre AuthManager y DatabaseManager"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp:
            db_path = tmp.name
        
        try:
            # Crear AuthManager con base de datos temporal
            auth_manager = AuthManager()
            auth_manager.db_manager = DatabaseManager(f"sqlite:///{db_path}")
            
            # Test registro de usuario
            success, message = auth_manager.register_user(
                "testuser", "test@example.com", "password123", "password123"
            )
            assert success is True
            assert "registrado exitosamente" in message
            
            # Test login
            success, message = auth_manager.login_user("testuser", "password123")
            assert success is True
            assert "Bienvenido" in message
            assert auth_manager.is_authenticated() is True
            
            # Test logout
            auth_manager.logout_user()
            assert auth_manager.is_authenticated() is False
            
        finally:
            try:
                os.unlink(db_path)
            except PermissionError:
                # En Windows, el archivo puede estar en uso
                pass


if __name__ == "__main__":
    # Ejecutar tests básicos
    pytest.main([__file__, "-v"]) 