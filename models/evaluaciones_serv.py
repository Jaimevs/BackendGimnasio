from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import models.persons
import enum

class Servicios(enum.Enum):
    SNutricion = "Servicios de nutricion"
    HP = "Horarios y precios"
    C = "Comunidad"
    PE = "Programas de entretenimiento"

class Evaluaciones_serv(Base):
    __tablename__ = 'tbd_evaluaciones_servicios'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Usuario_ID = Column(Integer, nullable=False)
    Servicios = Column(Enum(Servicios), nullable=False)
    Calificacion = Column(String(60), nullable=False)
    Criterio = Column(String(100), nullable=False)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # intems = relationship("Item", back_populates="owner") Clave foranea