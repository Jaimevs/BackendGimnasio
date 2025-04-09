from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum

class Servicios(Base):
    __tablename__ = 'tbb_servicios'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Nombre = Column(String(100), nullable=False)
    Descripcion = Column(LONGTEXT, nullable=True)
    Costo = Column(Float, nullable=False)
    # Area_ID = Column(Integer, ForeignKey("tbb_areas.ID"), nullable=False)  # Relación con tbb_areas (comentada por ahora)
    Usuario_ID = Column(Integer, ForeignKey("tbd_usuarios_roles.Usuario_ID"), nullable=False)  # Relación con el usuario que creó el servicio
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario_rol = relationship("UserRol", foreign_keys=[Usuario_ID])
    # area = relationship("Area", foreign_keys=[Area_ID])  # Comentada por ahora
    evaluaciones = relationship("Evaluaciones_serv", back_populates="servicio")