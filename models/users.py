from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, Float, ForeignKey
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum

class MyEstatus(enum.Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"
    Bloqueado = "Bloqueado"
    Suspendido = "Suspendido"

class User(Base):
    __tablename__ = 'tbb_usuarios'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Nombre_Usuario = Column(String(60), nullable=False, unique=True)
    Correo_Electronico = Column(String(100), nullable=False, unique=True)
    Contrasena = Column(String(255), nullable=False)
    Numero_Telefonico_Movil = Column(String(20), nullable=True)
    Estatus = Column(Enum(MyEstatus), nullable=False, default=MyEstatus.Activo)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relación con roles
    roles = relationship("Rol", secondary="tbd_usuarios_roles", back_populates="usuarios")
    
    # Relación con Person - un usuario solo puede tener una persona
    # La relación se define aquí pero la clave foránea está en Person
    persona = relationship("Person", uselist=False, back_populates="usuario")