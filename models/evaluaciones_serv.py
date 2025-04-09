from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Enum, SmallInteger, Text
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import models.persons
import enum

class TipoServicio(enum.Enum):
    SNutricion = "Servicios de nutricion"
    HP = "Horarios y precios"
    C = "Comunidad"
    PE = "Programas de entretenimiento"

class Evaluaciones_serv(Base):
    __tablename__ = 'tbd_evaluaciones_servicios'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Usuario_ID = Column(Integer, ForeignKey("tbd_usuarios_roles.Usuario_ID"), nullable=False)
    Servicio_ID = Column(Integer, ForeignKey("tbb_servicios.ID"), nullable=False)
    Tipo_Servicio = Column(Enum(TipoServicio), nullable=False)
    Calificacion = Column(SmallInteger, nullable=False)
    Comentario = Column(Text, nullable=True)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario_rol = relationship("UserRol", foreign_keys=[Usuario_ID])
    servicio = relationship("Servicios", foreign_keys=[Servicio_ID], back_populates="evaluaciones")