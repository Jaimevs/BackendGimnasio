from sqlalchemy import Column, Integer, String, Text, Time, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime, time

class Clase(Base):
    __tablename__ = 'tbb_clases'
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Entrenador_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=False)
    Nombre = Column(String(100), nullable=False)
    Descripcion = Column(Text, nullable=True)
    Dia_Inicio = Column(String(20), nullable=False)  # Lunes, Martes, etc.
    Dia_Fin = Column(String(20), nullable=False)  # Lunes, Martes, etc.
    Hora_Inicio = Column(Time, nullable=False)
    Hora_Fin = Column(Time, nullable=False)
    Duracion_Minutos = Column(Integer, nullable=False)
    Estatus = Column(Boolean, default=True)
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    entrenador = relationship("User", foreign_keys=[Entrenador_ID], back_populates="clases")
    quejas = relationship("Queja", back_populates="clase", overlaps="reservaciones")