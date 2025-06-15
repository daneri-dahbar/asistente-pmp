"""
Modelos de base de datos para el chat.
Utiliza SQLAlchemy ORM para definir las estructuras de datos.
"""

from datetime import datetime, timedelta, timezone
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import hashlib
import secrets

Base = declarative_base()

# Zona horaria GMT-3 (Argentina/Chile/Uruguay)
GMT_MINUS_3 = timezone(timedelta(hours=-3))

def get_local_datetime():
    """Retorna la fecha y hora actual en GMT-3"""
    return datetime.now(GMT_MINUS_3)

class User(Base):
    """
    Modelo para los usuarios del sistema.
    Maneja registro, autenticación y datos del usuario.
    """
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    salt = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=get_local_datetime)
    is_active = Column(Boolean, default=True)
    
    # Campos adicionales del perfil
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    company = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    experience_years = Column(Integer, nullable=True)
    target_exam_date = Column(String(20), nullable=True)  # Formato DD/MM/YYYY
    study_hours_daily = Column(Integer, nullable=True)
    
    # Relación con las sesiones de chat
    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    
    def set_password(self, password: str):
        """Establece la contraseña hasheada con salt"""
        self.salt = secrets.token_hex(16)
        self.password_hash = self._hash_password(password, self.salt)
    
    def check_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return self.password_hash == self._hash_password(password, self.salt)
    
    @staticmethod
    def _hash_password(password: str, salt: str) -> str:
        """Hashea la contraseña con el salt usando SHA-256"""
        return hashlib.sha256((password + salt).encode()).hexdigest()

class ChatSession(Base):
    """
    Modelo para las sesiones de chat.
    Permite separar diferentes conversaciones por usuario.
    """
    __tablename__ = 'chat_sessions'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(255), default="Nueva Conversación")
    mode = Column(String(50), default="charlemos")  # Modo de la conversación
    created_at = Column(DateTime, default=get_local_datetime)
    last_used_at = Column(DateTime, default=get_local_datetime)  # Última vez que se usó
    
    # Relaciones
    user = relationship("User", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """
    Modelo para los mensajes individuales del chat.
    Almacena tanto mensajes del usuario como respuestas de la IA.
    """
    __tablename__ = 'chat_messages'
    
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey('chat_sessions.id'), nullable=False)
    role = Column(String(50), nullable=False)  # 'user' o 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=get_local_datetime)
    
    # Relación con la sesión
    session = relationship("ChatSession", back_populates="messages")

class DatabaseManager:
    """
    Gestiona la conexión y operaciones con la base de datos.
    """
    
    def __init__(self, database_url: str = "sqlite:///chat_history.db"):
        self.engine = create_engine(database_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self):
        """Retorna una nueva sesión de base de datos"""
        return self.SessionLocal()
    
    # Métodos de autenticación
    def create_user(self, username: str, email: str, password: str) -> User:
        """Crea un nuevo usuario"""
        with self.get_session() as db:
            # Verificar si el usuario ya existe
            existing_user = db.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                if existing_user.username == username:
                    raise ValueError("El nombre de usuario ya existe")
                else:
                    raise ValueError("El email ya está registrado")
            
            user = User(username=username, email=email)
            user.set_password(password)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
    
    def authenticate_user(self, username: str, password: str) -> User:
        """Autentica un usuario"""
        with self.get_session() as db:
            user = db.query(User).filter(User.username == username).first()
            if user and user.check_password(password) and user.is_active:
                return user
            return None
    
    def get_user_by_id(self, user_id: int) -> User:
        """Obtiene un usuario por ID"""
        with self.get_session() as db:
            return db.query(User).filter(User.id == user_id).first()
    
    def create_chat_session(self, user_id: int, name: str = "Nueva Conversación", mode: str = "charlemos") -> ChatSession:
        """Crea una nueva sesión de chat para un usuario"""
        with self.get_session() as db:
            session = ChatSession(user_id=user_id, name=name, mode=mode)
            db.add(session)
            db.commit()
            db.refresh(session)
            return session
    
    def get_latest_chat_session(self, user_id: int) -> ChatSession:
        """Obtiene la sesión de chat más reciente de un usuario"""
        with self.get_session() as db:
            session = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(ChatSession.created_at.desc()).first()
            if not session:
                session = self.create_chat_session(user_id)
            return session
    
    def get_user_sessions(self, user_id: int, mode: str = None) -> list:
        """Obtiene todas las sesiones de un usuario, opcionalmente filtradas por modo"""
        with self.get_session() as db:
            query = db.query(ChatSession).filter(ChatSession.user_id == user_id)
            
            if mode:
                query = query.filter(ChatSession.mode == mode)
            
            sessions = query.order_by(ChatSession.last_used_at.desc()).all()
            return sessions
    
    def add_message(self, session_id: int, role: str, content: str):
        """Añade un nuevo mensaje a la sesión especificada"""
        with self.get_session() as db:
            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content
            )
            db.add(message)
            
            # Actualizar la fecha de último uso de la sesión
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if session:
                session.last_used_at = get_local_datetime()
            
            db.commit()
    
    def get_session_messages(self, session_id: int) -> list:
        """Obtiene todos los mensajes de una sesión específica"""
        with self.get_session() as db:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp.asc()).all()
            return [(msg.role, msg.content) for msg in messages]
    
    # Métodos específicos para análisis de datos
    def get_user_analytics_data(self, user_id: int) -> dict:
        """
        Obtiene datos comprehensivos para análisis del usuario.
        Incluye estadísticas de todas las sesiones de EVALUEMOS y SIMULEMOS.
        """
        with self.get_session() as db:
            # Obtener información básica del usuario
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Obtener todas las sesiones del usuario
            all_sessions = db.query(ChatSession).filter(
                ChatSession.user_id == user_id
            ).order_by(ChatSession.created_at.asc()).all()
            
            # Separar sesiones por modo
            evaluemos_sessions = [s for s in all_sessions if s.mode == "evaluemos"]
            simulemos_sessions = [s for s in all_sessions if s.mode == "simulemos"]
            estudiemos_sessions = [s for s in all_sessions if s.mode == "estudiemos"]
            charlemos_sessions = [s for s in all_sessions if s.mode == "charlemos"]
            
            # Calcular estadísticas básicas
            total_sessions = len(all_sessions)
            total_messages = db.query(ChatMessage).join(ChatSession).filter(
                ChatSession.user_id == user_id
            ).count()
            
            # Calcular tiempo total de estudio (aproximado por número de mensajes y sesiones)
            study_time_hours = self._estimate_study_time(all_sessions, db)
            
            # Obtener datos de evaluaciones
            evaluation_data = self._extract_evaluation_data(evaluemos_sessions, db)
            
            # Obtener datos de simulacros
            simulation_data = self._extract_simulation_data(simulemos_sessions, db)
            
            # Calcular streak de estudio
            study_streak = self._calculate_study_streak(all_sessions)
            
            # Preparar datos del perfil
            profile_data = {
                'full_name': user.full_name,
                'experience_years': user.experience_years,
                'target_exam_date': user.target_exam_date,
                'study_hours_daily': user.study_hours_daily,
                'company': user.company,
                'position': user.position
            }
            
            return {
                'user_profile': profile_data,
                'overview': {
                    'total_sessions': total_sessions,
                    'total_messages': total_messages,
                    'study_time_hours': study_time_hours,
                    'study_streak_days': study_streak,
                    'sessions_by_mode': {
                        'charlemos': len(charlemos_sessions),
                        'estudiemos': len(estudiemos_sessions),
                        'evaluemos': len(evaluemos_sessions),
                        'simulemos': len(simulemos_sessions)
                    }
                },
                'evaluations': evaluation_data,
                'simulations': simulation_data,
                'study_patterns': self._analyze_study_patterns(all_sessions, db),
                'progress_trends': self._calculate_progress_trends(evaluemos_sessions, simulemos_sessions, db)
            }
    
    def _estimate_study_time(self, sessions: list, db) -> float:
        """Estima el tiempo total de estudio basado en sesiones y mensajes"""
        total_hours = 0.0
        
        for session in sessions:
            # Obtener mensajes de la sesión
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).all()
            
            if len(messages) >= 2:
                # Calcular duración de la sesión basada en timestamps
                first_message = min(messages, key=lambda m: m.timestamp)
                last_message = max(messages, key=lambda m: m.timestamp)
                duration = last_message.timestamp - first_message.timestamp
                session_hours = duration.total_seconds() / 3600
                
                # Agregar tiempo base por número de mensajes (estimación)
                message_time = len(messages) * 0.05  # 3 minutos promedio por mensaje
                
                total_hours += max(session_hours, message_time)
            else:
                # Sesión muy corta, estimar tiempo mínimo
                total_hours += 0.1
        
        return round(total_hours, 1)
    
    def _extract_evaluation_data(self, evaluemos_sessions: list, db) -> dict:
        """Extrae datos específicos de las sesiones de EVALUEMOS"""
        if not evaluemos_sessions:
            return {'has_data': False, 'message': 'No hay sesiones de EVALUEMOS completadas'}
        
        evaluation_stats = {
            'has_data': True,
            'total_sessions': len(evaluemos_sessions),
            'sessions_detail': []
        }
        
        for session in evaluemos_sessions:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.timestamp.asc()).all()
            
            # Analizar contenido de mensajes para extraer datos de evaluación
            session_data = {
                'session_id': session.id,
                'session_name': session.name,
                'date': session.created_at.strftime('%Y-%m-%d'),
                'duration_minutes': self._calculate_session_duration(messages),
                'total_interactions': len([m for m in messages if m.role == 'user']),
                'questions_attempted': self._count_questions_in_session(messages),
                'topics_covered': self._extract_topics_from_messages(messages)
            }
            
            evaluation_stats['sessions_detail'].append(session_data)
        
        return evaluation_stats
    
    def _extract_simulation_data(self, simulemos_sessions: list, db) -> dict:
        """Extrae datos específicos de las sesiones de SIMULEMOS"""
        if not simulemos_sessions:
            return {'has_data': False, 'message': 'No hay sesiones de SIMULEMOS completadas'}
        
        simulation_stats = {
            'has_data': True,
            'total_sessions': len(simulemos_sessions),
            'sessions_detail': []
        }
        
        for session in simulemos_sessions:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).order_by(ChatMessage.timestamp.asc()).all()
            
            session_data = {
                'session_id': session.id,
                'session_name': session.name,
                'date': session.created_at.strftime('%Y-%m-%d'),
                'duration_minutes': self._calculate_session_duration(messages),
                'total_interactions': len([m for m in messages if m.role == 'user']),
                'exam_type': self._identify_exam_type_from_messages(messages),
                'completion_status': self._assess_completion_status(messages)
            }
            
            simulation_stats['sessions_detail'].append(session_data)
        
        return simulation_stats
    
    def _calculate_session_duration(self, messages: list) -> int:
        """Calcula la duración de una sesión en minutos"""
        if len(messages) < 2:
            return 0
        
        first_message = min(messages, key=lambda m: m.timestamp)
        last_message = max(messages, key=lambda m: m.timestamp)
        duration = last_message.timestamp - first_message.timestamp
        return int(duration.total_seconds() / 60)
    
    def _count_questions_in_session(self, messages: list) -> int:
        """Cuenta aproximadamente cuántas preguntas se respondieron en la sesión"""
        question_indicators = ['pregunta', 'respuesta', 'opción', 'alternativa', 'selecciona', 'elige']
        question_count = 0
        
        for message in messages:
            if message.role == 'assistant':
                content_lower = message.content.lower()
                if any(indicator in content_lower for indicator in question_indicators):
                    question_count += 1
        
        return question_count
    
    def _extract_topics_from_messages(self, messages: list) -> list:
        """Extrae temas/áreas de conocimiento mencionados en los mensajes"""
        # Áreas de conocimiento del PMBOK
        pmbok_areas = [
            'integration', 'integración', 'scope', 'alcance', 'schedule', 'cronograma',
            'cost', 'costo', 'quality', 'calidad', 'resource', 'recursos',
            'communications', 'comunicaciones', 'risk', 'riesgo', 'procurement', 'adquisiciones',
            'stakeholder', 'interesados', 'people', 'personas', 'process', 'proceso',
            'business environment', 'entorno de negocio'
        ]
        
        topics_found = set()
        
        for message in messages:
            content_lower = message.content.lower()
            for area in pmbok_areas:
                if area in content_lower:
                    topics_found.add(area.title())
        
        return list(topics_found)
    
    def _identify_exam_type_from_messages(self, messages: list) -> str:
        """Identifica el tipo de examen/simulacro basado en el contenido"""
        exam_types = {
            'completo': ['180 preguntas', 'examen completo', 'simulacro completo'],
            'por_tiempo': ['30 minutos', '60 minutos', '90 minutos', 'tiempo limitado'],
            'por_dominio': ['people domain', 'process domain', 'business environment']
        }
        
        for message in messages:
            content_lower = message.content.lower()
            for exam_type, indicators in exam_types.items():
                if any(indicator in content_lower for indicator in indicators):
                    return exam_type
        
        return 'general'
    
    def _assess_completion_status(self, messages: list) -> str:
        """Evalúa si el simulacro fue completado"""
        completion_indicators = ['completado', 'finalizado', 'terminado', 'score', 'resultado']
        
        for message in messages:
            if message.role == 'assistant':
                content_lower = message.content.lower()
                if any(indicator in content_lower for indicator in completion_indicators):
                    return 'completado'
        
        return 'en_progreso'
    
    def _calculate_study_streak(self, sessions: list) -> int:
        """Calcula la racha de días consecutivos de estudio"""
        if not sessions:
            return 0
        
        # Obtener fechas únicas de sesiones (solo fecha, sin hora)
        study_dates = set()
        for session in sessions:
            study_dates.add(session.created_at.date())
        
        # Ordenar fechas
        sorted_dates = sorted(study_dates, reverse=True)
        
        if not sorted_dates:
            return 0
        
        # Calcular racha desde la fecha más reciente
        streak = 1
        current_date = sorted_dates[0]
        
        for i in range(1, len(sorted_dates)):
            expected_date = current_date - timedelta(days=i)
            if sorted_dates[i] == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    def _analyze_study_patterns(self, sessions: list, db) -> dict:
        """Analiza patrones de estudio del usuario"""
        if not sessions:
            return {'has_data': False}
        
        # Analizar horarios de estudio
        hour_distribution = {}
        day_distribution = {}
        mode_preferences = {}
        
        for session in sessions:
            # Hora del día
            hour = session.created_at.hour
            hour_distribution[hour] = hour_distribution.get(hour, 0) + 1
            
            # Día de la semana
            day = session.created_at.strftime('%A')
            day_distribution[day] = day_distribution.get(day, 0) + 1
            
            # Preferencia de modo
            mode_preferences[session.mode] = mode_preferences.get(session.mode, 0) + 1
        
        # Encontrar el mejor horario
        best_hour = max(hour_distribution.items(), key=lambda x: x[1])[0] if hour_distribution else None
        best_day = max(day_distribution.items(), key=lambda x: x[1])[0] if day_distribution else None
        preferred_mode = max(mode_preferences.items(), key=lambda x: x[1])[0] if mode_preferences else None
        
        return {
            'has_data': True,
            'best_study_hour': best_hour,
            'best_study_day': best_day,
            'preferred_mode': preferred_mode,
            'hour_distribution': hour_distribution,
            'day_distribution': day_distribution,
            'mode_distribution': mode_preferences
        }
    
    def _calculate_progress_trends(self, evaluemos_sessions: list, simulemos_sessions: list, db) -> dict:
        """Calcula tendencias de progreso a lo largo del tiempo"""
        all_assessment_sessions = evaluemos_sessions + simulemos_sessions
        
        if len(all_assessment_sessions) < 2:
            return {'has_data': False, 'message': 'Necesitas al menos 2 sesiones de evaluación/simulacro para mostrar tendencias'}
        
        # Ordenar sesiones por fecha
        sorted_sessions = sorted(all_assessment_sessions, key=lambda s: s.created_at)
        
        trends = {
            'has_data': True,
            'total_assessment_sessions': len(all_assessment_sessions),
            'first_session_date': sorted_sessions[0].created_at.strftime('%Y-%m-%d'),
            'latest_session_date': sorted_sessions[-1].created_at.strftime('%Y-%m-%d'),
            'session_frequency': self._calculate_session_frequency(sorted_sessions),
            'engagement_trend': self._calculate_engagement_trend(sorted_sessions, db)
        }
        
        return trends
    
    def _calculate_session_frequency(self, sessions: list) -> dict:
        """Calcula la frecuencia de sesiones"""
        if len(sessions) < 2:
            return {'frequency': 'insuficientes_datos'}
        
        first_date = sessions[0].created_at
        last_date = sessions[-1].created_at
        days_span = (last_date - first_date).days
        
        if days_span == 0:
            return {'frequency': 'mismo_dia', 'sessions_per_week': len(sessions) * 7}
        
        sessions_per_week = (len(sessions) / days_span) * 7
        
        return {
            'days_span': days_span,
            'sessions_per_week': round(sessions_per_week, 1),
            'frequency_category': self._categorize_frequency(sessions_per_week)
        }
    
    def _categorize_frequency(self, sessions_per_week: float) -> str:
        """Categoriza la frecuencia de estudio"""
        if sessions_per_week >= 5:
            return 'muy_alta'
        elif sessions_per_week >= 3:
            return 'alta'
        elif sessions_per_week >= 1:
            return 'moderada'
        else:
            return 'baja'
    
    def _calculate_engagement_trend(self, sessions: list, db) -> dict:
        """Calcula la tendencia de engagement (participación)"""
        engagement_data = []
        
        for session in sessions:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session.id
            ).all()
            
            user_messages = [m for m in messages if m.role == 'user']
            engagement_score = len(user_messages)  # Número de interacciones del usuario
            
            engagement_data.append({
                'date': session.created_at.strftime('%Y-%m-%d'),
                'engagement_score': engagement_score
            })
        
        # Calcular tendencia (simple: comparar primera mitad vs segunda mitad)
        if len(engagement_data) >= 4:
            mid_point = len(engagement_data) // 2
            first_half_avg = sum(d['engagement_score'] for d in engagement_data[:mid_point]) / mid_point
            second_half_avg = sum(d['engagement_score'] for d in engagement_data[mid_point:]) / (len(engagement_data) - mid_point)
            
            if second_half_avg > first_half_avg * 1.1:
                trend = 'mejorando'
            elif second_half_avg < first_half_avg * 0.9:
                trend = 'declinando'
            else:
                trend = 'estable'
        else:
            trend = 'insuficientes_datos'
        
        return {
            'trend': trend,
            'engagement_history': engagement_data
        } 