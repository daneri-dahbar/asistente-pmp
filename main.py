"""
Punto de entrada principal para la aplicación de Chat con ChatGPT.
Aplicación de escritorio con autenticación creada con Flet, LangChain y OpenAI.

Para ejecutar: python main.py
"""

import flet as ft
import os
import sys
from chat_ui import ChatUI
from auth_ui import AuthUI

class MainApp:
    """
    Aplicación principal que maneja autenticación y chat en una sola ventana.
    """
    
    def __init__(self):
        self.is_executable = getattr(sys, 'frozen', False)
        self.authenticated_user = None
        self.page = None
        self.auth_ui = None
        self.chat_ui = None
    
    def check_environment(self):
        """
        Verifica que el entorno esté configurado correctamente.
        """
        # Verificar si existe el archivo .env
        if not os.path.exists('.env'):
            if not self.is_executable:
                print("⚠️  Archivo .env no encontrado.")
                print("📝 Crea un archivo .env con tu OPENAI_API_KEY")
                print("   Ejemplo: OPENAI_API_KEY=tu_clave_aqui")
            return False
        
        # Cargar variables de entorno
        from dotenv import load_dotenv
        load_dotenv()
        
        # Verificar API Key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            if not self.is_executable:
                print("❌ OPENAI_API_KEY no encontrada en el archivo .env")
                print("📝 Agrega tu clave API al archivo .env:")
                print("   OPENAI_API_KEY=tu_clave_aqui")
            return False
        
        if api_key == "tu_clave_api_aqui":
            if not self.is_executable:
                print("⚠️  Debes reemplazar 'tu_clave_api_aqui' con tu clave real de OpenAI")
            return False
        
        if not self.is_executable:
            print("✅ Configuración del entorno verificada correctamente")
        return True
    
    def on_auth_success(self, user):
        """
        Callback ejecutado cuando la autenticación es exitosa.
        """
        self.authenticated_user = user
        if not self.is_executable:
            print(f"✅ Usuario {user.username} autenticado exitosamente")
        
        # Cambiar a la interfaz de chat
        self.show_chat()
    
    def on_logout(self):
        """
        Callback ejecutado cuando el usuario cierra sesión.
        """
        self.authenticated_user = None
        if not self.is_executable:
            print("👋 Usuario desconectado")
        
        # Volver a la interfaz de autenticación
        self.show_auth()
    
    def show_auth(self):
        """
        Muestra la interfaz de autenticación.
        """
        # Limpiar la página
        self.page.controls.clear()
        
        # Crear nueva instancia de AuthUI
        self.auth_ui = AuthUI(self.on_auth_success)
        self.auth_ui.build_ui(self.page)
        
        self.page.update()
    
    def show_chat(self):
        """
        Muestra la interfaz de chat.
        """
        # Limpiar la página
        self.page.controls.clear()
        
        # Crear nueva instancia de ChatUI con callback de logout
        self.chat_ui = ChatUI(self.authenticated_user)
        self.chat_ui.on_logout_callback = self.on_logout
        self.chat_ui.build_ui(self.page)
        
        self.page.update()
    
    def main(self, page: ft.Page):
        """
        Función principal de la aplicación Flet.
        """
        self.page = page
        
        # Configuración inicial de la página
        page.title = "ChatGPT Assistant"
        page.window_width = 800
        page.window_height = 600
        page.window_min_width = 400
        page.window_min_height = 500
        page.theme_mode = ft.ThemeMode.LIGHT
        page.padding = 0
        
        # Mostrar interfaz de autenticación inicialmente
        self.show_auth()

def main():
    """
    Función principal que inicia la aplicación.
    """
    try:
        app = MainApp()
        
        # Verificar entorno
        if not app.check_environment():
            if not app.is_executable:
                print("\n❌ No se puede iniciar la aplicación debido a problemas de configuración.")
                print("📖 Consulta el README.md para instrucciones de configuración.")
            sys.exit(1)
        
        if not app.is_executable:
            print("🚀 Iniciando ChatGPT con Flet...")
            print("📦 Versión: 2.0.0 con Autenticación")
            print("🔗 Powered by OpenAI, LangChain & Flet")
            print("-" * 50)
        
        # Lanzar la aplicación
        ft.app(
            target=app.main,
            name="ChatGPT Assistant",
            assets_dir="assets"
        )
        
    except KeyboardInterrupt:
        print("\n👋 Aplicación cerrada por el usuario")
    except Exception as e:
        is_executable = getattr(sys, 'frozen', False)
        if not is_executable:
            print(f"❌ Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 