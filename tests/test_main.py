"""
Tests unitarios para el módulo principal (main.py).
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch, MagicMock
from main import MainApp

class TestMainApp:
    """Tests para la clase MainApp."""
    
    @pytest.mark.unit
    def test_init(self):
        """Test de inicialización de MainApp."""
        app = MainApp()
        
        assert app is not None
        assert app.is_executable == getattr(sys, 'frozen', False)
        assert app.authenticated_user is None
        assert app.page is None
        assert app.auth_ui is None
        assert app.chat_ui is None
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_success(self, mock_getenv, mock_exists):
        """Test de verificación exitosa del entorno."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_getenv.return_value = "test_api_key_12345"
        
        app = MainApp()
        result = app.check_environment()
        
        assert result is True
        mock_exists.assert_called_once_with('.env')
        mock_getenv.assert_called_once_with("OPENAI_API_KEY")
    
    @pytest.mark.unit
    @patch('os.path.exists')
    def test_check_environment_no_env_file(self, mock_exists):
        """Test de verificación sin archivo .env."""
        # Configurar mock
        mock_exists.return_value = False
        
        app = MainApp()
        result = app.check_environment()
        
        assert result is False
        mock_exists.assert_called_once_with('.env')
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_no_api_key(self, mock_getenv, mock_exists):
        """Test de verificación sin API key."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_getenv.return_value = None
        
        app = MainApp()
        result = app.check_environment()
        
        assert result is False
        mock_exists.assert_called_once_with('.env')
        mock_getenv.assert_called_once_with("OPENAI_API_KEY")
    
    @pytest.mark.unit
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_default_api_key(self, mock_getenv, mock_exists):
        """Test de verificación con API key por defecto."""
        # Configurar mocks
        mock_exists.return_value = True
        mock_getenv.return_value = "tu_clave_api_aqui"
        
        app = MainApp()
        result = app.check_environment()
        
        assert result is False
        mock_exists.assert_called_once_with('.env')
        mock_getenv.assert_called_once_with("OPENAI_API_KEY")
    
    @pytest.mark.unit
    @patch('main.AuthUI')
    @patch('main.ChatUI')
    def test_setup_ui_components(self, mock_chat_ui, mock_auth_ui):
        """Test de configuración de componentes de UI."""
        app = MainApp()
        mock_page = Mock()
        
        app.setup_ui_components(mock_page)
        
        assert app.page == mock_page
        assert app.auth_ui is not None
        assert app.chat_ui is not None
        
        # Verificar que se crearon las instancias
        mock_auth_ui.assert_called_once_with(
            on_login_success=app.on_login_success,
            on_register_success=app.on_register_success
        )
        mock_chat_ui.assert_called_once_with(
            page=mock_page,
            on_logout=app.on_logout
        )
    
    @pytest.mark.unit
    def test_on_login_success(self):
        """Test de callback de login exitoso."""
        app = MainApp()
        mock_user = Mock()
        mock_user.username = "test_user"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.on_login_success(mock_user)
        
        assert app.authenticated_user == mock_user
        
        # Verificar que se actualizó la UI
        app.chat_ui.set_user.assert_called_once_with(mock_user)
        app.page.go.assert_called_once_with("/chat")
    
    @pytest.mark.unit
    def test_on_register_success(self):
        """Test de callback de registro exitoso."""
        app = MainApp()
        mock_user = Mock()
        mock_user.username = "new_user"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.on_register_success(mock_user)
        
        assert app.authenticated_user == mock_user
        
        # Verificar que se actualizó la UI
        app.chat_ui.set_user.assert_called_once_with(mock_user)
        app.page.go.assert_called_once_with("/chat")
    
    @pytest.mark.unit
    def test_on_logout(self):
        """Test de callback de logout."""
        app = MainApp()
        mock_user = Mock()
        app.authenticated_user = mock_user
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.on_logout()
        
        assert app.authenticated_user is None
        
        # Verificar que se actualizó la UI
        app.chat_ui.clear_user.assert_called_once()
        app.page.go.assert_called_once_with("/auth")
    
    @pytest.mark.unit
    def test_route_change_auth(self):
        """Test de cambio de ruta a autenticación."""
        app = MainApp()
        mock_route = Mock()
        mock_route.route = "/auth"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.route_change(mock_route)
        
        # Verificar que se mostró la UI de autenticación
        app.page.views.clear.assert_called_once()
        app.page.views.append.assert_called_once()
        app.page.update.assert_called_once()
    
    @pytest.mark.unit
    def test_route_change_chat(self):
        """Test de cambio de ruta a chat."""
        app = MainApp()
        mock_route = Mock()
        mock_route.route = "/chat"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.route_change(mock_route)
        
        # Verificar que se mostró la UI de chat
        app.page.views.clear.assert_called_once()
        app.page.views.append.assert_called_once()
        app.page.update.assert_called_once()
    
    @pytest.mark.unit
    def test_route_change_default(self):
        """Test de cambio de ruta por defecto."""
        app = MainApp()
        mock_route = Mock()
        mock_route.route = "/unknown"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.route_change(mock_route)
        
        # Verificar que se redirigió a auth por defecto
        app.page.go.assert_called_once_with("/auth")
    
    @pytest.mark.unit
    @patch('main.MainApp.check_environment')
    @patch('main.MainApp.setup_ui_components')
    @patch('main.MainApp.route_change')
    def test_main_success(self, mock_route_change, mock_setup_ui, mock_check_env):
        """Test de función main exitosa."""
        # Configurar mocks
        mock_check_env.return_value = True
        mock_page = Mock()
        mock_page.route = "/auth"
        
        app = MainApp()
        
        # Simular llamada a main
        with patch('flet.app') as mock_flet_app:
            mock_flet_app.return_value = None
            
            # Llamar a main directamente
            app.main(mock_page)
            
            # Verificar que se ejecutaron los pasos correctos
            mock_check_env.assert_called_once()
            mock_setup_ui.assert_called_once_with(mock_page)
            mock_route_change.assert_called_once()
    
    @pytest.mark.unit
    @patch('main.MainApp.check_environment')
    def test_main_environment_failure(self, mock_check_env):
        """Test de función main con fallo en verificación de entorno."""
        # Configurar mock para fallar
        mock_check_env.return_value = False
        
        app = MainApp()
        
        # Simular llamada a main
        with patch('flet.app') as mock_flet_app:
            mock_flet_app.return_value = None
            
            # Llamar a main directamente
            app.main(Mock())
            
            # Verificar que se verificó el entorno pero no se continuó
            mock_check_env.assert_called_once()
    
    @pytest.mark.unit
    def test_view_pop(self):
        """Test de eliminación de vista."""
        app = MainApp()
        mock_page = Mock()
        app.page = mock_page
        
        app.view_pop(mock_page)
        
        # Verificar que se eliminó la vista
        mock_page.views.pop.assert_called_once()
        mock_page.update.assert_called_once()

class TestMainAppIntegration:
    """Tests de integración para MainApp."""
    
    @pytest.mark.integration
    @patch('main.MainApp.check_environment')
    @patch('main.AuthUI')
    @patch('main.ChatUI')
    def test_full_app_initialization(self, mock_chat_ui, mock_auth_ui, mock_check_env):
        """Test de inicialización completa de la aplicación."""
        # Configurar mocks
        mock_check_env.return_value = True
        mock_auth_instance = Mock()
        mock_chat_instance = Mock()
        mock_auth_ui.return_value = mock_auth_instance
        mock_chat_ui.return_value = mock_chat_instance
        
        app = MainApp()
        mock_page = Mock()
        mock_page.route = "/auth"
        
        # Simular inicialización completa
        app.main(mock_page)
        
        # Verificar que se configuró todo correctamente
        assert app.page == mock_page
        assert app.auth_ui == mock_auth_instance
        assert app.chat_ui == mock_chat_instance
        
        # Verificar que se configuraron los callbacks
        mock_auth_ui.assert_called_once()
        mock_chat_ui.assert_called_once()
    
    @pytest.mark.integration
    @patch('main.MainApp.check_environment')
    def test_authentication_flow(self, mock_check_env):
        """Test del flujo completo de autenticación."""
        # Configurar mocks
        mock_check_env.return_value = True
        
        app = MainApp()
        mock_page = Mock()
        mock_page.route = "/auth"
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = mock_page
        
        # Simular login exitoso
        mock_user = Mock()
        mock_user.username = "test_user"
        
        app.on_login_success(mock_user)
        
        # Verificar estado después del login
        assert app.authenticated_user == mock_user
        app.chat_ui.set_user.assert_called_once_with(mock_user)
        mock_page.go.assert_called_once_with("/chat")
        
        # Simular logout
        app.on_logout()
        
        # Verificar estado después del logout
        assert app.authenticated_user is None
        app.chat_ui.clear_user.assert_called_once()
        mock_page.go.assert_called_with("/auth")

class TestMainAppErrorHandling:
    """Tests de manejo de errores para MainApp."""
    
    @pytest.mark.unit
    def test_route_change_with_none_route(self):
        """Test de cambio de ruta con ruta None."""
        app = MainApp()
        mock_route = Mock()
        mock_route.route = None
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        app.route_change(mock_route)
        
        # Verificar que se redirigió a auth por defecto
        app.page.go.assert_called_once_with("/auth")
    
    @pytest.mark.unit
    def test_on_login_success_with_none_user(self):
        """Test de login exitoso con usuario None."""
        app = MainApp()
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        # Esto no debería causar errores
        app.on_login_success(None)
        
        assert app.authenticated_user is None
    
    @pytest.mark.unit
    def test_on_logout_without_user(self):
        """Test de logout sin usuario autenticado."""
        app = MainApp()
        app.authenticated_user = None
        
        # Configurar UI components
        app.auth_ui = Mock()
        app.chat_ui = Mock()
        app.page = Mock()
        
        # Esto no debería causar errores
        app.on_logout()
        
        assert app.authenticated_user is None
        app.chat_ui.clear_user.assert_called_once()
        app.page.go.assert_called_once_with("/auth")

class TestMainAppExecutableDetection:
    """Tests para la detección de ejecutable."""
    
    @pytest.mark.unit
    @patch('sys.frozen', True)
    def test_init_as_executable(self):
        """Test de inicialización como ejecutable."""
        app = MainApp()
        assert app.is_executable is True
    
    @pytest.mark.unit
    @patch('sys.frozen', False)
    def test_init_as_script(self):
        """Test de inicialización como script."""
        app = MainApp()
        assert app.is_executable is False
    
    @pytest.mark.unit
    @patch('sys.frozen', True)
    @patch('os.path.exists')
    @patch('os.getenv')
    def test_check_environment_executable_mode(self, mock_getenv, mock_exists):
        """Test de verificación de entorno en modo ejecutable."""
        # Configurar mocks
        mock_exists.return_value = False
        mock_getenv.return_value = None
        
        app = MainApp()
        result = app.check_environment()
        
        # En modo ejecutable, no debería imprimir mensajes
        assert result is False 