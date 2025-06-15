"""
Modelos de base de datos para el chat.
Utiliza SQLAlchemy ORM para definir las estructuras de datos.
"""

from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os
import hashlib
import secrets

Base = declarative_base()

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
    created_at = Column(DateTime, default=datetime.utcnow)
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
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used_at = Column(DateTime, default=datetime.utcnow)  # Última vez que se usó
    
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
    timestamp = Column(DateTime, default=datetime.utcnow)
    
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
                session.last_used_at = datetime.utcnow()
            
            db.commit()
    
    def get_session_messages(self, session_id: int) -> list:
        """Obtiene todos los mensajes de una sesión específica"""
        with self.get_session() as db:
            messages = db.query(ChatMessage).filter(
                ChatMessage.session_id == session_id
            ).order_by(ChatMessage.timestamp.asc()).all()
            return [(msg.role, msg.content) for msg in messages] 