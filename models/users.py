from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Table, SmallInteger
from sqlalchemy.dialects.mysql import LONGTEXT
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
    ID = Column(Integer, primary_key=True, index=True)
    # Eliminar esta línea: Persona_Id = Column(Integer, ForeignKey("tbb_personas.ID"))
    Nombre_Usuario = Column(String(60))
    Correo_Electronico = Column(String(100))
    Contrasena = Column(String(40))
    Numero_Telefonico_Movil = Column(String(20))
    Estatus = Column(Enum(MyEstatus))
    Fecha_Registro = Column(DateTime)
    Fecha_Actualizacion = Column(DateTime)
    
    # Relación con roles
    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")
    
    # Relación uno a uno con Person
    persona = relationship("Person", back_populates="usuario", uselist=False)