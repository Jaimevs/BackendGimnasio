from sqlalchemy import Column, Boolean, Integer, String, DateTime, Text, SmallInteger
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class Rol(Base):
    __tablename__ = 'tbc_roles'
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    Nombre = Column(String(60), unique=True, index=True, nullable=False)
    Descripcion = Column(Text, nullable=True)
    Estatus = Column(SmallInteger, default=1, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relación con usuarios
    usuarios = relationship("User", secondary="tbd_usuarios_roles", back_populates="roles")