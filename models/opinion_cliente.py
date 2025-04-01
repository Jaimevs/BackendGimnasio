from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime
import enum

Base = declarative_base()

class TipoOpinion(str, enum.Enum):
    Queja = "Queja"
    Sugerencia = "Sugerencia"
    Felicitacion = "Felicitacion"
    Recomendacion = "Recomendacion"
    Otro = "Otro"

class OpinionCliente(Base):
    __tablename__ = 'tbd_opinion_cliente'
    
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    descripcion = Column(LONGTEXT, nullable=False)
    tipo = Column(String(100), nullable=False)
    respuesta = Column(LONGTEXT, nullable=True)
    estatus = Column(Boolean, default=True, nullable=False)
    atencion_personal = Column(String(100), nullable=True)
    fecha_registro = Column(DateTime, nullable=False, default=datetime.now)
    fecha_actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)