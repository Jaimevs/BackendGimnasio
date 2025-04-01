from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum

class MyTipo(enum.Enum):
    Consulta = "Consulta"
    Reclamo = "Reclamo"
    Sugerencia = "Sugerencia"

class Servicio_Cliente(Base):
    __tablename__ = "tbc_servicios_clientes"
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Persona_ID = Column(Integer, nullable=False)
    Tipo_Servicio = Column(Enum(MyTipo), nullable=False)
    Descripcion = Column(String(255), nullable=False) 
    Comentarios = Column(String(200), nullable=True)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)