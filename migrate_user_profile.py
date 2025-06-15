"""
Script de migración para agregar campos de perfil de usuario.
Ejecutar una sola vez para actualizar la base de datos existente.
"""

import sqlite3
import os

def migrate_user_profile():
    """
    Agrega los nuevos campos de perfil al modelo User.
    """
    db_path = "chat_history.db"
    
    if not os.path.exists(db_path):
        print("❌ Base de datos no encontrada. Ejecuta la aplicación primero para crearla.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Lista de campos a agregar
        new_fields = [
            ("full_name", "VARCHAR(100)"),
            ("phone", "VARCHAR(20)"),
            ("company", "VARCHAR(100)"),
            ("position", "VARCHAR(100)"),
            ("experience_years", "INTEGER"),
            ("target_exam_date", "VARCHAR(20)"),
            ("study_hours_daily", "INTEGER")
        ]
        
        print("🔄 Iniciando migración de perfil de usuario...")
        
        for field_name, field_type in new_fields:
            try:
                # Verificar si el campo ya existe
                cursor.execute("PRAGMA table_info(users)")
                columns = [column[1] for column in cursor.fetchall()]
                
                if field_name not in columns:
                    # Agregar el campo
                    cursor.execute(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}")
                    print(f"✅ Campo '{field_name}' agregado exitosamente")
                else:
                    print(f"ℹ️  Campo '{field_name}' ya existe, omitiendo...")
                    
            except sqlite3.Error as e:
                print(f"❌ Error al agregar campo '{field_name}': {e}")
        
        conn.commit()
        print("✅ Migración completada exitosamente")
        
    except sqlite3.Error as e:
        print(f"❌ Error de base de datos: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_user_profile() 