# models/quejas.py
from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Text, SmallInteger
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class Queja(Base):
    __tablename__ = 'tbb_quejas'
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=False)
    Entrenador_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=False)
    Clase_ID = Column(Integer, ForeignKey('tbb_clases.ID'), nullable=False)
    Calificacion = Column(SmallInteger, nullable=False) 
    Comentario = Column(Text, nullable=True)
    Estatus = Column(Boolean, default=True)
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[Usuario_ID], overlaps="reservaciones")
    entrenador = relationship("User", foreign_keys=[Entrenador_ID], overlaps="clases")
    clase = relationship("Clase", foreign_keys=[Clase_ID])