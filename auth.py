"""
Sistema de autenticación para la aplicación de chat.
Maneja registro, login y gestión de sesiones de usuario.
"""

import re
from typing import Optional
from db.models import DatabaseManager, User

class AuthManager:
    """
    Gestiona la autenticación y validación de usuarios.
    """
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.current_user: Optional[User] = None
    
    def register_user(self, username: str, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
        """
        Registra un nuevo usuario.
        
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        # Validar datos
        validation_result = self._validate_registration_data(username, email, password, confirm_password)
        if not validation_result[0]:
            return validation_result
        
        try:
            user = self.db_manager.create_user(username, email, password)
            return True, f"Usuario '{username}' registrado exitosamente"
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Error al registrar usuario: {str(e)}"
    
    def login_user(self, username: str, password: str) -> tuple[bool, str]:
        """
        Autentica un usuario.
        
        Returns:
            tuple[bool, str]: (éxito, mensaje)
        """
        if not username or not password:
            return False, "Usuario y contraseña son requeridos"
        
        try:
            user = self.db_manager.authenticate_user(username, password)
            if user:
                self.current_user = user
                return True, f"Bienvenido, {user.username}!"
            else:
                return False, "Usuario o contraseña incorrectos"
        except Exception as e:
            return False, f"Error al autenticar: {str(e)}"
    
    def logout_user(self):
        """Cierra la sesión del usuario actual"""
        self.current_user = None
    
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado"""
        return self.current_user is not None
    
    def get_current_user(self) -> Optional[User]:
        """Obtiene el usuario actual"""
        return self.current_user
    
    def _validate_registration_data(self, username: str, email: str, password: str, confirm_password: str) -> tuple[bool, str]:
        """
        Valida los datos de registro.
        
        Returns:
            tuple[bool, str]: (válido, mensaje de error)
        """
        # Validar campos vacíos
        if not all([username, email, password, confirm_password]):
            return False, "Todos los campos son requeridos"
        
        # Validar usuario
        if len(username) < 3:
            return False, "El nombre de usuario debe tener al menos 3 caracteres"
        
        if len(username) > 50:
            return False, "El nombre de usuario no puede tener más de 50 caracteres"
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "El nombre de usuario solo puede contener letras, números y guiones bajos"
        
        # Validar email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Formato de email inválido"
        
        # Validar contraseña
        if len(password) < 6:
            return False, "La contraseña debe tener al menos 6 caracteres"
        
        if password != confirm_password:
            return False, "Las contraseñas no coinciden"
        
        # Validar complejidad de contraseña
        if not re.search(r'[A-Za-z]', password):
            return False, "La contraseña debe contener al menos una letra"
        
        if not re.search(r'[0-9]', password):
            return False, "La contraseña debe contener al menos un número"
        
        return True, "Datos válidos"
    
    def get_password_strength(self, password: str) -> tuple[str, str]:
        """
        Evalúa la fortaleza de una contraseña.
        
        Returns:
            tuple[str, str]: (nivel, descripción)
        """
        if len(password) < 6:
            return "Débil", "Muy corta"
        
        score = 0
        checks = {
            "minúsculas": re.search(r'[a-z]', password),
            "mayúsculas": re.search(r'[A-Z]', password),
            "números": re.search(r'[0-9]', password),
            "símbolos": re.search(r'[!@#$%^&*(),.?":{}|<>]', password),
            "longitud": len(password) >= 8
        }
        
        score = sum(1 for check in checks.values() if check)
        
        if score <= 2:
            return "Débil", "Añade más variedad de caracteres"
        elif score <= 3:
            return "Media", "Buena, pero puede mejorar"
        elif score <= 4:
            return "Fuerte", "Excelente seguridad"
        else:
            return "Muy fuerte", "Máxima seguridad" 