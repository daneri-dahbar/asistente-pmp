#!/usr/bin/env python3
"""
Script para generar datos de demostración del Asistente PMP
Crea un usuario demo con múltiples sesiones y mensajes para mostrar
el potencial completo de la aplicación, especialmente en analytics.
"""

import os
import sys
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.models import Base, User, ChatSession, ChatMessage
import hashlib
import secrets

# Configuración de la base de datos
DATABASE_URL = "sqlite:///chat_history.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Datos de demostración
DEMO_USER = {
    "username": "demo_user",
    "email": "demo@asistente-pmp.com",
    "full_name": "Usuario de Demostración",
    "phone": "+54 11 1234-5678",
    "company": "Tech Solutions SA",
    "position": "Senior Project Manager",
    "experience_years": 8,
    "target_exam_date": "15/06/2024",
    "study_hours_daily": 2
}

# Modos de estudio disponibles
STUDY_MODES = ["CHARLEMOS", "ESTUDIEMOS", "EVALUEMOS", "SIMULEMOS", "ANALICEMOS"]

# Temas de PMP para generar conversaciones realistas
PMP_TOPICS = [
    "Gestión de Integración del Proyecto",
    "Gestión del Alcance del Proyecto",
    "Gestión del Cronograma del Proyecto",
    "Gestión de los Costos del Proyecto",
    "Gestión de la Calidad del Proyecto",
    "Gestión de los Recursos del Proyecto",
    "Gestión de las Comunicaciones del Proyecto",
    "Gestión de los Riesgos del Proyecto",
    "Gestión de las Adquisiciones del Proyecto",
    "Gestión de los Interesados del Proyecto",
    "Metodologías Ágiles",
    "Gestión de Cambios",
    "Análisis de Valor Ganado",
    "Diagramas de Red",
    "Gestión de Conflictos",
    "Liderazgo de Equipos",
    "Comunicación Efectiva",
    "Negociación",
    "Gestión de Stakeholders",
    "Control de Calidad"
]

# Mensajes de usuario realistas por modo
USER_MESSAGES = {
    "CHARLEMOS": [
        "Hola, ¿cómo estás?",
        "¿Puedes explicarme qué es la gestión de integración?",
        "Tengo dudas sobre el proceso de iniciación",
        "¿Cuál es la diferencia entre planificar y ejecutar?",
        "¿Cómo se maneja el cierre de un proyecto?",
        "¿Qué herramientas se usan en la planificación?",
        "¿Cómo se gestionan los cambios durante la ejecución?",
        "¿Qué documentos son clave en cada fase?",
        "¿Cómo se mide el progreso del proyecto?",
        "¿Qué hacer cuando hay retrasos?",
        "¿Cómo manejar conflictos en el equipo?",
        "¿Cuál es el rol del sponsor?",
        "¿Cómo se gestionan las lecciones aprendidas?",
        "¿Qué es el baseline del proyecto?",
        "¿Cómo se actualiza el plan de proyecto?"
    ],
    "ESTUDIEMOS": [
        "Quiero estudiar gestión de alcance",
        "Explícame los procesos de planificación",
        "¿Cuáles son las herramientas de control de calidad?",
        "Necesito repasar gestión de riesgos",
        "¿Cómo se calcula el valor ganado?",
        "Explícame las metodologías ágiles",
        "¿Qué son los diagramas de red?",
        "¿Cómo se gestionan las adquisiciones?",
        "Explícame la gestión de stakeholders",
        "¿Cuáles son los procesos de ejecución?",
        "¿Cómo se maneja la comunicación?",
        "¿Qué es la gestión de integración?",
        "Explícame el control de cambios",
        "¿Cómo se planifica el cronograma?",
        "¿Qué herramientas de estimación existen?"
    ],
    "EVALUEMOS": [
        "Dame un quiz sobre gestión de alcance",
        "Quiero evaluar mi conocimiento en costos",
        "Hazme preguntas sobre calidad",
        "Evalúa mi comprensión de riesgos",
        "Dame ejercicios de valor ganado",
        "Quiero practicar con preguntas de cronograma",
        "Evalúa mi conocimiento en adquisiciones",
        "Hazme preguntas sobre stakeholders",
        "Quiero evaluar mi comprensión de integración",
        "Dame un quiz sobre comunicación",
        "Evalúa mi conocimiento en recursos",
        "Hazme preguntas sobre cierre de proyectos",
        "Quiero practicar con preguntas de ejecución",
        "Evalúa mi comprensión de planificación",
        "Dame ejercicios de control y monitoreo"
    ],
    "SIMULEMOS": [
        "Simula una pregunta del examen PMP",
        "Dame una pregunta sobre gestión de alcance",
        "Simula una pregunta de valor ganado",
        "Quiero una pregunta sobre cronograma",
        "Simula una pregunta de gestión de riesgos",
        "Dame una pregunta sobre calidad",
        "Simula una pregunta de adquisiciones",
        "Quiero una pregunta sobre stakeholders",
        "Simula una pregunta de comunicación",
        "Dame una pregunta sobre recursos",
        "Simula una pregunta de integración",
        "Quiero una pregunta sobre costos",
        "Simula una pregunta de cierre",
        "Dame una pregunta sobre ejecución",
        "Simula una pregunta de planificación"
    ],
    "ANALICEMOS": [
        "Analiza mi progreso de estudio",
        "¿Cómo voy con mi preparación?",
        "Dame recomendaciones para mejorar",
        "¿En qué temas debo enfocarme más?",
        "Analiza mis patrones de estudio",
        "¿Cuál es mi fortaleza principal?",
        "¿Qué áreas necesito reforzar?",
        "Dame un reporte de mi actividad",
        "¿Cómo optimizar mi tiempo de estudio?",
        "Analiza mi consistencia",
        "¿Qué temas he dominado mejor?",
        "Dame insights sobre mi aprendizaje",
        "¿Cómo mejorar mi rendimiento?",
        "Analiza mi evolución en el tiempo",
        "¿Qué estrategias me recomiendas?"
    ]
}

# Respuestas de IA realistas por modo
AI_RESPONSES = {
    "CHARLEMOS": [
        "¡Hola! Estoy aquí para ayudarte con tu preparación PMP. ¿En qué puedo asistirte hoy?",
        "La gestión de integración es fundamental en PMP. Coordina todos los elementos del proyecto para lograr los objetivos.",
        "El proceso de iniciación establece las bases del proyecto. Incluye desarrollar el acta de constitución y identificar stakeholders.",
        "Planificar se enfoca en crear el plan del proyecto, mientras que ejecutar se centra en realizar el trabajo definido.",
        "El cierre formaliza la finalización del proyecto, incluyendo la entrega de productos y documentación de lecciones aprendidas.",
        "Las herramientas incluyen juicio de expertos, reuniones, análisis de datos y software de gestión de proyectos.",
        "Los cambios se gestionan a través del proceso de control integrado de cambios, evaluando impacto y obteniendo aprobación.",
        "Documentos clave: acta de constitución, plan de proyecto, registros de trabajo, informes de desempeño.",
        "El progreso se mide mediante métricas de valor ganado, cronograma y presupuesto.",
        "Para retrasos: analizar causas, evaluar impacto, actualizar plan y comunicar a stakeholders."
    ],
    "ESTUDIEMOS": [
        "Excelente elección. La gestión de alcance incluye 6 procesos: planificar, recopilar, definir, crear WBS, validar y controlar.",
        "Los procesos de planificación incluyen: desarrollar plan de proyecto, recopilar requisitos, definir alcance, crear WBS, definir actividades, secuenciar actividades, estimar recursos, estimar duraciones, desarrollar cronograma, estimar costos, determinar presupuesto, planificar calidad, planificar recursos, planificar comunicaciones, planificar riesgos, planificar adquisiciones, planificar stakeholder engagement.",
        "Herramientas de control de calidad: diagramas de flujo, histogramas, diagramas de causa-efecto, diagramas de dispersión, gráficos de control, inspección, auditorías de calidad.",
        "La gestión de riesgos incluye: planificar, identificar, realizar análisis cualitativo y cuantitativo, planificar respuestas, implementar respuestas y monitorear.",
        "Valor ganado = % completado × presupuesto total. CV = EV - AC, SV = EV - PV, CPI = EV/AC, SPI = EV/PV.",
        "Metodologías ágiles: Scrum, Kanban, XP, Crystal, FDD. Se enfocan en iteraciones cortas, adaptación y entrega continua.",
        "Diagramas de red muestran dependencias entre actividades. Tipos: AOA (flechas), AON (nodos), PDM (precedencia).",
        "Gestión de adquisiciones: planificar, conducir, controlar y cerrar adquisiciones. Incluye contratos y relaciones con vendedores.",
        "Gestión de stakeholders: identificar, planificar engagement, gestionar engagement y monitorear engagement.",
        "Procesos de ejecución: dirigir y gestionar trabajo del proyecto, gestionar conocimiento, gestionar calidad, adquirir recursos, desarrollar equipo, gestionar equipo, gestionar comunicaciones, implementar respuestas a riesgos, conducir adquisiciones, gestionar stakeholder engagement."
    ],
    "EVALUEMOS": [
        "Perfecto, aquí tienes un quiz sobre gestión de alcance:\n\n1. ¿Cuál es la diferencia entre alcance del producto y alcance del proyecto?\n2. ¿Qué documento contiene los criterios de aceptación?\n3. ¿Cuál es el propósito del WBS?\n4. ¿Qué herramienta se usa para validar el alcance?\n\n¿Quieres que revisemos las respuestas?",
        "Excelente, evaluemos tu conocimiento en costos:\n\n1. ¿Cuál es la diferencia entre costo directo e indirecto?\n2. ¿Qué es el presupuesto de referencia?\n3. ¿Cómo se calcula la estimación hasta la conclusión (EAC)?\n4. ¿Qué significa CV negativo?\n\n¿Listo para las respuestas?",
        "Perfecto, aquí tienes preguntas sobre calidad:\n\n1. ¿Cuál es la diferencia entre calidad y grado?\n2. ¿Qué es el costo de conformidad?\n3. ¿Cuál es el propósito de las auditorías de calidad?\n4. ¿Qué herramienta identifica causas raíz?\n\n¿Procedemos con las respuestas?"
    ],
    "SIMULEMOS": [
        "Aquí tienes una pregunta típica del examen PMP:\n\nUn proyecto tiene un EV de $50,000, AC de $60,000 y PV de $45,000. ¿Cuál es el índice de rendimiento del cronograma (SPI)?\n\na) 0.83\nb) 1.11\nc) 0.90\nd) 1.20\n\n¿Cuál es tu respuesta?",
        "Pregunta sobre gestión de alcance:\n\nDurante la ejecución, el cliente solicita una característica adicional. ¿Cuál es el primer paso que debe tomar el director del proyecto?\n\na) Implementar el cambio inmediatamente\nb) Evaluar el impacto en el alcance\nc) Actualizar el WBS\nd) Documentar la solicitud en el registro de cambios\n\n¿Qué opción eliges?",
        "Pregunta sobre valor ganado:\n\nSi el CV es -$5,000 y el SV es -$3,000, ¿qué significa esto?\n\na) El proyecto está adelantado y bajo presupuesto\nb) El proyecto está retrasado y sobre presupuesto\nc) El proyecto está adelantado y sobre presupuesto\nd) El proyecto está retrasado y bajo presupuesto\n\n¿Cuál es la respuesta correcta?"
    ],
    "ANALICEMOS": [
        "Basándome en tu actividad, veo un progreso excelente:\n\n📊 **Resumen de Actividad:**\n• 45 sesiones completadas\n• 1,247 mensajes intercambiados\n• 18 días consecutivos de estudio\n• 2.3 horas promedio por día\n\n🎯 **Fortalezas Identificadas:**\n• Excelente consistencia en el estudio\n• Dominio en gestión de alcance y cronograma\n• Buena comprensión de metodologías ágiles\n\n📈 **Áreas de Mejora:**\n• Reforzar gestión de riesgos\n• Practicar más cálculos de valor ganado\n• Profundizar en adquisiciones\n\n¿Te gustaría que profundice en algún área específica?",
        "Tu preparación va muy bien. Aquí mi análisis:\n\n✅ **Puntos Fuertes:**\n• Consistencia diaria en el estudio\n• Buen balance entre modos de aprendizaje\n• Comprensión sólida de conceptos fundamentales\n\n⚠️ **Oportunidades:**\n• Más práctica con simulaciones\n• Reforzar temas técnicos complejos\n• Aumentar velocidad en preguntas\n\n📅 **Recomendación:** Mantén el ritmo actual y enfócate en simulaciones los próximos días.",
        "Aquí tienes mis recomendaciones personalizadas:\n\n🎯 **Prioridad Alta:**\n• Practicar 30 minutos diarios de simulaciones\n• Revisar fórmulas de valor ganado\n• Estudiar casos de estudio complejos\n\n📚 **Recursos Sugeridos:**\n• Enfócate en preguntas de 4-5 opciones\n• Practica gestión de tiempo en exámenes\n• Revisa temas de mayor peso en el examen\n\n⏰ **Plan de Acción:**\n• Semana 1: Simulaciones diarias\n• Semana 2: Repaso de temas débiles\n• Semana 3: Examen de práctica completo"
    ]
}

def create_demo_user():
    """Crear usuario de demostración"""
    db = SessionLocal()
    
    # Verificar si el usuario ya existe
    existing_user = db.query(User).filter(User.username == DEMO_USER["username"]).first()
    if existing_user:
        print(f"✅ Usuario {DEMO_USER['username']} ya existe")
        return existing_user
    
    # Crear salt y hash de contraseña
    salt = secrets.token_hex(32)
    password = "demo123"  # Contraseña simple para demo
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    # Crear usuario
    demo_user = User(
        username=DEMO_USER["username"],
        email=DEMO_USER["email"],
        password_hash=password_hash,
        salt=salt,
        full_name=DEMO_USER["full_name"],
        phone=DEMO_USER["phone"],
        company=DEMO_USER["company"],
        position=DEMO_USER["position"],
        experience_years=DEMO_USER["experience_years"],
        target_exam_date=DEMO_USER["target_exam_date"],
        study_hours_daily=DEMO_USER["study_hours_daily"],
        created_at=datetime.now() - timedelta(days=30)  # Usuario creado hace 30 días
    )
    
    db.add(demo_user)
    db.commit()
    db.refresh(demo_user)
    
    print(f"✅ Usuario {DEMO_USER['username']} creado exitosamente")
    print(f"   Contraseña: {password}")
    return demo_user

def generate_session_name(mode, topic, date):
    """Generar nombre realista para la sesión"""
    time_str = date.strftime("%d/%m %H:%M")
    return f"{mode} - {topic} - {time_str}"

def create_demo_sessions(user_id):
    """Crear múltiples sesiones de demostración"""
    db = SessionLocal()
    
    # Fechas de las últimas 30 días
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    sessions_created = 0
    
    # Crear sesiones con diferentes patrones
    for day in range(30):
        current_date = start_date + timedelta(days=day)
        
        # Patrón de estudio: más actividad en días laborables
        if current_date.weekday() < 5:  # Lunes a Viernes
            num_sessions = random.randint(1, 4)
        else:  # Fin de semana
            num_sessions = random.randint(0, 2)
        
        for session_num in range(num_sessions):
            # Seleccionar modo y tema
            mode = random.choice(STUDY_MODES)
            topic = random.choice(PMP_TOPICS)
            
            # Hora del día (más actividad en mañana y tarde)
            if random.random() < 0.6:
                hour = random.choice([8, 9, 10, 14, 15, 16, 17])
            else:
                hour = random.choice([11, 12, 13, 18, 19, 20])
            
            minute = random.randint(0, 59)
            session_time = current_date.replace(hour=hour, minute=minute)
            
            # Crear sesión
            session_name = generate_session_name(mode, topic, session_time)
            session = ChatSession(
                user_id=user_id,
                name=session_name,
                mode=mode,
                created_at=session_time,
                last_used_at=session_time + timedelta(minutes=random.randint(15, 90))
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            # Crear mensajes para esta sesión
            num_messages = random.randint(3, 12)
            create_session_messages(db, session.id, mode, session_time, num_messages)
            
            sessions_created += 1
    
    print(f"✅ {sessions_created} sesiones de demostración creadas")
    return sessions_created

def create_session_messages(db, session_id, mode, start_time, num_messages):
    """Crear mensajes realistas para una sesión"""
    user_messages = USER_MESSAGES.get(mode, USER_MESSAGES["CHARLEMOS"])
    ai_responses = AI_RESPONSES.get(mode, AI_RESPONSES["CHARLEMOS"])
    
    current_time = start_time
    
    for i in range(num_messages):
        # Mensaje del usuario
        user_message = random.choice(user_messages)
        user_msg = ChatMessage(
            session_id=session_id,
            role="user",
            content=user_message,
            timestamp=current_time
        )
        db.add(user_msg)
        current_time += timedelta(seconds=random.randint(30, 120))
        
        # Respuesta de la IA
        ai_response = random.choice(ai_responses)
        ai_msg = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=ai_response,
            timestamp=current_time
        )
        db.add(ai_msg)
        current_time += timedelta(seconds=random.randint(60, 180))

def generate_demo_data():
    """Función principal para generar datos de demostración"""
    print("🚀 Generando datos de demostración para Asistente PMP...")
    print("=" * 60)
    
    # Crear base de datos si no existe
    Base.metadata.create_all(bind=engine)
    
    # Crear usuario demo
    demo_user = create_demo_user()
    
    # Crear sesiones y mensajes
    sessions_count = create_demo_sessions(demo_user.id)
    
    # Estadísticas finales
    db = SessionLocal()
    total_messages = db.query(ChatMessage).join(ChatSession).filter(ChatSession.user_id == demo_user.id).count()
    
    print("=" * 60)
    print("📊 RESUMEN DE DATOS DE DEMOSTRACIÓN:")
    print(f"   👤 Usuario: {DEMO_USER['username']}")
    print(f"   📝 Contraseña: demo123")
    print(f"   💬 Sesiones creadas: {sessions_count}")
    print(f"   💭 Mensajes totales: {total_messages}")
    print(f"   📅 Período: Últimos 30 días")
    print(f"   🎯 Modos utilizados: {', '.join(STUDY_MODES)}")
    print("=" * 60)
    print("✅ Datos de demostración generados exitosamente!")
    print("   Ahora puedes iniciar sesión con 'demo_user' y 'demo123'")
    print("   para ver el potencial completo de la aplicación.")

if __name__ == "__main__":
    try:
        generate_demo_data()
    except Exception as e:
        print(f"❌ Error generando datos de demostración: {e}")
        sys.exit(1) 