#!/usr/bin/env python3
"""
Script de configuración automatizada para Asistente para Certificación PMP con Autenticación.
Configura el entorno, instala dependencias y prepara la aplicación.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_header():
    """Imprime el header de la aplicación"""
    print("=" * 60)
    print("🎓 Asistente para Certificación PMP - Setup con Autenticación")
    print("=" * 60)
    print("📦 Configurando entorno y dependencias...")
    print()

def check_python_version():
    """Verifica la versión de Python"""
    print("🐍 Verificando versión de Python...")
    
    if sys.version_info < (3, 9):
        print("❌ Error: Se requiere Python 3.9 o superior")
        print(f"   Versión actual: {sys.version}")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} - OK")
    return True

def create_virtual_environment():
    """Crea un entorno virtual si no existe"""
    print("\n🔧 Configurando entorno virtual...")
    
    venv_path = Path(".venv")
    
    if venv_path.exists():
        print("✅ Entorno virtual ya existe")
        return True
    
    try:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
        print("✅ Entorno virtual creado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al crear entorno virtual: {e}")
        return False

def get_pip_command():
    """Obtiene el comando pip correcto según el sistema operativo"""
    if platform.system() == "Windows":
        return [".venv\\Scripts\\pip.exe"]
    else:
        return [".venv/bin/pip"]

def install_dependencies():
    """Instala las dependencias del proyecto"""
    print("\n📦 Instalando dependencias...")
    
    pip_cmd = get_pip_command()
    
    try:
        # Actualizar pip
        subprocess.run(pip_cmd + ["install", "--upgrade", "pip"], check=True)
        print("✅ pip actualizado")
        
        # Instalar dependencias
        subprocess.run(pip_cmd + ["install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencias instaladas exitosamente")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error al instalar dependencias: {e}")
        return False

def create_env_file():
    """Crea el archivo .env si no existe"""
    print("\n🔑 Configurando archivo de entorno...")
    
    env_file = Path(".env")
    
    if env_file.exists():
        print("✅ Archivo .env ya existe")
        return True
    
    try:
        with open(env_file, "w", encoding="utf-8") as f:
            f.write("# Configuración de Asistente para Certificación PMP\n")
            f.write("# Reemplaza 'tu_clave_api_aqui' con tu clave real de OpenAI\n")
            f.write("OPENAI_API_KEY=tu_clave_api_aqui\n")
            f.write("\n")
            f.write("# Configuración de base de datos (opcional)\n")
            f.write("DATABASE_URL=sqlite:///chat_history.db\n")
        
        print("✅ Archivo .env creado")
        print("⚠️  IMPORTANTE: Edita el archivo .env y agrega tu clave API de OpenAI")
        return True
        
    except Exception as e:
        print(f"❌ Error al crear archivo .env: {e}")
        return False

def initialize_database():
    """Inicializa la base de datos"""
    print("\n🗄️  Inicializando base de datos...")
    
    try:
        # Importar y crear las tablas
        from db.models import DatabaseManager
        
        db_manager = DatabaseManager()
        print("✅ Base de datos inicializada correctamente")
        print("✅ Tablas de usuarios y conversaciones creadas")
        return True
        
    except Exception as e:
        print(f"❌ Error al inicializar base de datos: {e}")
        return False

def create_demo_user():
    """Crea un usuario de demostración"""
    print("\n👤 ¿Deseas crear un usuario de demostración?")
    response = input("   Escribe 'si' para crear usuario demo (admin/admin123): ").lower().strip()
    
    if response in ['si', 'sí', 's', 'yes', 'y']:
        try:
            from auth import AuthManager
            
            auth_manager = AuthManager()
            success, message = auth_manager.register_user(
                username="admin",
                email="admin@demo.com",
                password="admin123",
                confirm_password="admin123"
            )
            
            if success:
                print("✅ Usuario demo creado exitosamente")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
                print("   Email: admin@demo.com")
            else:
                print(f"⚠️  No se pudo crear usuario demo: {message}")
                
        except Exception as e:
            print(f"❌ Error al crear usuario demo: {e}")

def print_next_steps():
    """Imprime los siguientes pasos"""
    print("\n" + "=" * 60)
    print("🎉 ¡Configuración completada!")
    print("=" * 60)
    print()
    print("📝 Próximos pasos:")
    print("   1. Edita el archivo .env y agrega tu clave API de OpenAI")
    print("   2. Ejecuta la aplicación: python main.py")
    print()
    print("🔐 Sistema de Autenticación:")
    print("   • Primera vez: Regístrate creando una cuenta")
    print("   • Usuarios existentes: Inicia sesión normalmente")
    print("   • Cada usuario tiene su historial privado")
    print()
    print("🚀 Para crear un ejecutable:")
    print("   pyinstaller main.spec")
    print()
    print("📖 Consulta el README.md para más información")
    print("=" * 60)

def main():
    """Función principal del setup"""
    print_header()
    
    # Verificar Python
    if not check_python_version():
        sys.exit(1)
    
    # Crear entorno virtual
    if not create_virtual_environment():
        sys.exit(1)
    
    # Instalar dependencias
    if not install_dependencies():
        sys.exit(1)
    
    # Crear archivo .env
    if not create_env_file():
        sys.exit(1)
    
    # Inicializar base de datos
    if not initialize_database():
        sys.exit(1)
    
    # Crear usuario demo (opcional)
    create_demo_user()
    
    # Mostrar próximos pasos
    print_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelado por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1) 
    main() 