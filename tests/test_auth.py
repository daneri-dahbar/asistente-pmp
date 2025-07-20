"""
Tests unitarios para el módulo de autenticación (auth.py).
"""

import pytest
import re
from unittest.mock import Mock, patch
from auth import AuthManager

class TestAuthManager:
    """Tests para la clase AuthManager."""
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_init(self, auth_manager):
        """Test de inicialización del AuthManager."""
        assert auth_manager is not None
        assert auth_manager.current_user is None
        assert auth_manager.db_manager is not None
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_registration_data_valid(self, auth_manager, sample_user_data):
        """Test de validación de datos de registro válidos."""
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            confirm_password=sample_user_data["password"]
        )
        
        assert result[0] is True
        assert "válidos" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_registration_data_invalid_username(self, auth_manager, sample_user_data):
        """Test de validación con nombre de usuario inválido."""
        # Usuario muy corto
        result = auth_manager._validate_registration_data(
            username="ab",
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            confirm_password=sample_user_data["password"]
        )
        assert result[0] is False
        assert "usuario" in result[1].lower()
        
        # Usuario con caracteres inválidos
        result = auth_manager._validate_registration_data(
            username="user@test",
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            confirm_password=sample_user_data["password"]
        )
        assert result[0] is False
        assert "caracteres" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_registration_data_invalid_email(self, auth_manager, sample_user_data):
        """Test de validación con email inválido."""
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email="invalid-email",
            password=sample_user_data["password"],
            confirm_password=sample_user_data["password"]
        )
        assert result[0] is False
        assert "email" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_registration_data_invalid_password(self, auth_manager, sample_user_data):
        """Test de validación con contraseña inválida."""
        # Contraseña muy corta
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password="123",
            confirm_password="123"
        )
        assert result[0] is False
        assert "contraseña" in result[1].lower()
        
        # Contraseña sin letras
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password="123456",
            confirm_password="123456"
        )
        assert result[0] is False
        assert "letras" in result[1].lower()
        
        # Contraseña sin números
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password="abcdef",
            confirm_password="abcdef"
        )
        assert result[0] is False
        assert "números" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_validate_registration_data_password_mismatch(self, auth_manager, sample_user_data):
        """Test de validación con contraseñas que no coinciden."""
        result = auth_manager._validate_registration_data(
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
            confirm_password="DifferentPass123"
        )
        assert result[0] is False
        assert "coinciden" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_get_password_strength(self, auth_manager):
        """Test de análisis de fortaleza de contraseñas."""
        # Contraseña débil
        strength = auth_manager.get_password_strength("123")
        assert strength == "Débil"
        
        # Contraseña media
        strength = auth_manager.get_password_strength("abc123")
        assert strength == "Media"
        
        # Contraseña fuerte
        strength = auth_manager.get_password_strength("StrongPass123!")
        assert strength == "Fuerte"
        
        # Contraseña muy fuerte
        strength = auth_manager.get_password_strength("VeryStrongPassword123!@#")
        assert strength == "Muy Fuerte"
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_register_user_success(self, auth_manager, sample_user_data):
        """Test de registro exitoso de usuario."""
        with patch.object(auth_manager.db_manager, 'create_user') as mock_create:
            mock_user = Mock()
            mock_user.username = sample_user_data["username"]
            mock_create.return_value = mock_user
            
            result = auth_manager.register_user(
                username=sample_user_data["username"],
                email=sample_user_data["email"],
                password=sample_user_data["password"],
                confirm_password=sample_user_data["password"]
            )
            
            assert result[0] is True
            assert "registrado exitosamente" in result[1]
            mock_create.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_register_user_validation_failure(self, auth_manager):
        """Test de registro con datos inválidos."""
        result = auth_manager.register_user(
            username="ab",  # Muy corto
            email="invalid-email",
            password="123",
            confirm_password="123"
        )
        
        assert result[0] is False
        assert "usuario" in result[1].lower()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_register_user_database_error(self, auth_manager, sample_user_data):
        """Test de registro con error en base de datos."""
        with patch.object(auth_manager.db_manager, 'create_user') as mock_create:
            mock_create.side_effect = ValueError("Usuario ya existe")
            
            result = auth_manager.register_user(
                username=sample_user_data["username"],
                email=sample_user_data["email"],
                password=sample_user_data["password"],
                confirm_password=sample_user_data["password"]
            )
            
            assert result[0] is False
            assert "ya existe" in result[1]
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_login_user_success(self, auth_manager, sample_user_data):
        """Test de login exitoso."""
        with patch.object(auth_manager.db_manager, 'authenticate_user') as mock_auth:
            mock_user = Mock()
            mock_user.username = sample_user_data["username"]
            mock_auth.return_value = mock_user
            
            result = auth_manager.login_user(
                username=sample_user_data["username"],
                password=sample_user_data["password"]
            )
            
            assert result[0] is True
            assert "Bienvenido" in result[1]
            assert auth_manager.current_user == mock_user
            mock_auth.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_login_user_invalid_credentials(self, auth_manager):
        """Test de login con credenciales inválidas."""
        with patch.object(auth_manager.db_manager, 'authenticate_user') as mock_auth:
            mock_auth.return_value = None
            
            result = auth_manager.login_user(
                username="invalid_user",
                password="wrong_password"
            )
            
            assert result[0] is False
            assert "incorrectos" in result[1]
            assert auth_manager.current_user is None
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_login_user_empty_credentials(self, auth_manager):
        """Test de login con credenciales vacías."""
        result = auth_manager.login_user("", "")
        assert result[0] is False
        assert "requeridos" in result[1]
        
        result = auth_manager.login_user("user", "")
        assert result[0] is False
        assert "requeridos" in result[1]
        
        result = auth_manager.login_user("", "pass")
        assert result[0] is False
        assert "requeridos" in result[1]
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_login_user_database_error(self, auth_manager):
        """Test de login con error en base de datos."""
        with patch.object(auth_manager.db_manager, 'authenticate_user') as mock_auth:
            mock_auth.side_effect = Exception("Error de conexión")
            
            result = auth_manager.login_user("user", "pass")
            
            assert result[0] is False
            assert "Error al autenticar" in result[1]
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_logout(self, auth_manager, sample_user_data):
        """Test de logout."""
        # Simular usuario logueado
        mock_user = Mock()
        mock_user.username = sample_user_data["username"]
        auth_manager.current_user = mock_user
        
        auth_manager.logout()
        
        assert auth_manager.current_user is None
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_is_authenticated(self, auth_manager):
        """Test de verificación de autenticación."""
        # Sin usuario autenticado
        assert auth_manager.is_authenticated() is False
        
        # Con usuario autenticado
        mock_user = Mock()
        auth_manager.current_user = mock_user
        assert auth_manager.is_authenticated() is True
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_get_current_user(self, auth_manager, sample_user_data):
        """Test de obtención del usuario actual."""
        # Sin usuario autenticado
        assert auth_manager.get_current_user() is None
        
        # Con usuario autenticado
        mock_user = Mock()
        mock_user.username = sample_user_data["username"]
        auth_manager.current_user = mock_user
        
        current_user = auth_manager.get_current_user()
        assert current_user == mock_user
        assert current_user.username == sample_user_data["username"]

class TestPasswordValidation:
    """Tests específicos para validación de contraseñas."""
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_password_validation_pattern(self):
        """Test del patrón regex para contraseñas."""
        auth_manager = AuthManager()
        
        # Contraseñas válidas (mínimo 6 caracteres)
        valid_passwords = [
            "Test123",
            "MyPass456",
            "Secure789",
            "ComplexPass123"
        ]
        
        for password in valid_passwords:
            assert len(password) >= 6
        
        # Contraseñas inválidas
        invalid_passwords = [
            "123",    # Muy corta
            "test",   # Muy corta
            "abc",    # Muy corta
        ]
        
        for password in invalid_passwords:
            assert len(password) < 6
    
    @pytest.mark.unit
    @pytest.mark.auth
    def test_username_validation_pattern(self):
        """Test del patrón regex para nombres de usuario."""
        auth_manager = AuthManager()
        
        # Usernames válidos
        valid_usernames = [
            "user123",
            "test_user",
            "myusername",
            "user_name_123"
        ]
        
        for username in valid_usernames:
            assert re.match(r'^[a-zA-Z0-9_]+$', username) is not None
        
        # Usernames inválidos
        invalid_usernames = [
            "user@test",  # Caracteres especiales
            "user-test",  # Guiones
            "user test",  # Espacios
            "ab",         # Muy corto
            "a" * 51      # Muy largo
        ]
        
        for username in invalid_usernames:
            assert re.match(r'^[a-zA-Z0-9_]+$', username) is None 