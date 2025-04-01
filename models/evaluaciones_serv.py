from sqlalchemy import Column,Boolean, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
import models.persons
import enum

class Servicios(enum.Enum):
    SNutricion = "Servicios de nutricion"
    HP = "Horarios y precios"
    C = "Comunidad"
    PE = "Programas de entretenimiento"

class Evaluaciones_serv(Base):
    __tablename__ = 'tbd_evaluaciones_servicios'
    ID = Column(Integer, primary_key=True, index=True)
    Usuario_ID = Column(Integer)
    Servicios = Column( Enum(Servicios))
    Calificacion = Column(String(60))
    Criterio = Column(String(100))
    Estatus = Column(Boolean)
    
    Fecha_Registro = Column(DateTime)
    # intems = relationship("Item", back_populates="owner") Clave foranea