# models/reservaciones.py
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Text, Time, SmallInteger
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class Reservacion(Base):
    __tablename__ = 'tbb_reservaciones'
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=False)
    Clase_ID = Column(Integer, ForeignKey('tbb_clases.ID'), nullable=False)
    Fecha_Reservacion = Column(DateTime, nullable=False)  # Fecha específica de la reservación
    Estatus = Column(String(20), default="Confirmada")  # Confirmada, Cancelada, Asistida, No Asistida
    Comentario = Column(Text, nullable=True)
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[Usuario_ID], backref="reservaciones")
    clase = relationship("Clase", foreign_keys=[Clase_ID], backref="reservaciones")