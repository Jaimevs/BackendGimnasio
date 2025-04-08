from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum

class TipoOpinion(str, enum.Enum):
    Queja = "Queja"
    Sugerencia = "Sugerencia"
    Felicitacion = "Felicitacion"
    Recomendacion = "Recomendacion"
    Otro = "Otro"

class OpinionCliente(Base):
    __tablename__ = 'tbd_opinion_cliente'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=False)
    Tipo = Column(Enum(TipoOpinion), nullable=False)
    Descripcion = Column(Text, nullable=False)
    Respuesta_Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=True)
    Respuesta = Column(Text, nullable=True)
    Estatus = Column(Boolean, default=False, nullable=False)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[Usuario_ID], overlaps="reservaciones,clases")
    respuesta_usuario = relationship("User", foreign_keys=[Respuesta_Usuario_ID], overlaps="reservaciones,clases")