from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from datetime import datetime

Base = declarative_base()

class OpinionCliente(Base):
    __tablename__ = 'tbd_opinion_cliente'
    
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(LONGTEXT, nullable=False)
    tipo = Column(String(100))
    respuesta = Column(LONGTEXT)
    estatus = Column(Boolean, default=True)
    atencion_personal = Column(String(100))
    fecha_registro = Column(DateTime)
    fecha_actualizacion = Column(DateTime)
