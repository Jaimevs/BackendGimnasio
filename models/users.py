from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Table, SmallInteger
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import models.persons
import enum

# Tabla de relación entre usuarios y roles
usuario_rol = Table('tbd_usuarios_roles', Base.metadata,
    Column('Usuario_ID', Integer, ForeignKey('tbb_usuarios.ID'), primary_key=True),
    Column('Rol_ID', Integer, ForeignKey('tbc_roles.ID'), primary_key=True),
    Column('Estatus', SmallInteger, default=1),
    Column('Fecha_Registro', DateTime, default=datetime.now),
    Column('Fecha_Actualizacion', DateTime, nullable=True, onupdate=datetime.now),
    extend_existing=True  # Importante para evitar problemas de duplicación
)

class MyEstatus(enum.Enum):
    Activo = "Activo"
    Inactivo = "Inactivo"
    Bloqueado = "Bloqueado"
    Suspendido = "Suspendido"

class User(Base):
    __tablename__ = 'tbb_usuarios'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Nombre_Usuario = Column(String(60), nullable=False)
    Correo_Electronico = Column(String(100), nullable=False, unique=True)
    Contrasena = Column(String(40), nullable=False)
    Numero_Telefonico_Movil = Column(String(20), nullable=True)
    Estatus = Column(Enum(MyEstatus), nullable=False, default=MyEstatus.Activo)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relación con roles
    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    
    # Relación uno a uno con Person
    persona_id = Column(Integer, ForeignKey("tbb_personas.ID"), nullable=True)
    persona = relationship("Person", back_populates="usuario", uselist=False)