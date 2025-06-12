"""
Script de migración para actualizar la base de datos existente.
Agrega las tablas de usuarios y actualiza la estructura de chat_sessions.
"""

import sqlite3
import os
from pathlib import Path

def backup_database():
    """Crea una copia de seguridad de la base de datos actual"""
    db_path = "chat_history.db"
    if os.path.exists(db_path):
        backup_path = "chat_history_backup.db"
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Copia de seguridad creada: {backup_path}")
        return True
    return False

def migrate_database():
    """Migra la base de datos a la nueva estructura con usuarios"""
    db_path = "chat_history.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Iniciando migración de base de datos...")
        
        # Verificar si la tabla users ya existe
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name='users'
        """)
        
        if not cursor.fetchone():
            print("📝 Creando tabla de usuarios...")
            # Crear tabla users
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(128) NOT NULL,
                    salt VARCHAR(32) NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            """)
            print("✅ Tabla users creada")
        else:
            print("ℹ️  Tabla users ya existe")
        
        # Verificar si la columna user_id existe en chat_sessions
        cursor.execute("PRAGMA table_info(chat_sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'user_id' not in columns:
            print("📝 Agregando columna user_id a chat_sessions...")
            
            # Crear usuario por defecto si no existe
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            
            if user_count == 0:
                print("👤 Creando usuario por defecto...")
                # Crear usuario por defecto con hash de contraseña
                import hashlib
                import secrets
                
                salt = secrets.token_hex(16)
                password_hash = hashlib.sha256(("admin123" + salt).encode()).hexdigest()
                
                cursor.execute("""
                    INSERT INTO users (username, email, password_hash, salt)
                    VALUES (?, ?, ?, ?)
                """, ("admin", "admin@demo.com", password_hash, salt))
                
                default_user_id = cursor.lastrowid
                print(f"✅ Usuario por defecto creado (ID: {default_user_id})")
                print("   Usuario: admin")
                print("   Contraseña: admin123")
            else:
                # Usar el primer usuario existente
                cursor.execute("SELECT id FROM users LIMIT 1")
                default_user_id = cursor.fetchone()[0]
                print(f"ℹ️  Usando usuario existente (ID: {default_user_id})")
            
            # Agregar columna user_id a chat_sessions
            cursor.execute("ALTER TABLE chat_sessions ADD COLUMN user_id INTEGER")
            
            # Actualizar todas las sesiones existentes con el usuario por defecto
            cursor.execute("UPDATE chat_sessions SET user_id = ? WHERE user_id IS NULL", (default_user_id,))
            
            print("✅ Columna user_id agregada y sesiones actualizadas")
        else:
            print("ℹ️  Columna user_id ya existe en chat_sessions")
        
        # Confirmar cambios
        conn.commit()
        print("✅ Migración completada exitosamente")
        
        # Mostrar estadísticas
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chat_sessions")
        session_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM chat_messages")
        message_count = cursor.fetchone()[0]
        
        print(f"\n📊 Estadísticas de la base de datos:")
        print(f"   👤 Usuarios: {user_count}")
        print(f"   💬 Sesiones de chat: {session_count}")
        print(f"   📝 Mensajes: {message_count}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        conn.rollback()
        conn.close()
        return False

def verify_migration():
    """Verifica que la migración se haya completado correctamente"""
    try:
        from db.models import DatabaseManager
        
        print("\n🔍 Verificando migración...")
        db_manager = DatabaseManager()
        
        # Intentar obtener usuarios
        with db_manager.get_session() as session:
            from db.models import User, ChatSession
            
            users = session.query(User).all()
            sessions = session.query(ChatSession).all()
            
            print(f"✅ Verificación exitosa:")
            print(f"   👤 {len(users)} usuarios encontrados")
            print(f"   💬 {len(sessions)} sesiones encontradas")
            
            if users:
                print(f"   🔑 Usuario disponible: {users[0].username}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en verificación: {e}")
        return False

def main():
    """Función principal de migración"""
    print("=" * 60)
    print("🔄 MIGRACIÓN DE BASE DE DATOS")
    print("=" * 60)
    print("Este script actualizará tu base de datos para soportar autenticación.")
    print()
    
    # Crear copia de seguridad
    if backup_database():
        print()
    
    # Ejecutar migración
    if migrate_database():
        print()
        # Verificar migración
        if verify_migration():
            print("\n🎉 ¡Migración completada exitosamente!")
            print("\n📝 Próximos pasos:")
            print("   1. Ejecuta: python main.py")
            print("   2. Inicia sesión con: admin / admin123")
            print("   3. O crea una nueva cuenta")
        else:
            print("\n⚠️  Migración completada pero hay problemas en la verificación")
    else:
        print("\n❌ La migración falló")
        print("💡 Puedes restaurar desde: chat_history_backup.db")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 