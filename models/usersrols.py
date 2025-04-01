from sqlalchemy import Column, Boolean, Integer, ForeignKey, DateTime, PrimaryKeyConstraint
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class UserRol(Base):
    __tablename__ = 'tbd_usuarios_roles'
    __table_args__ = {'extend_existing': True}
    
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID"), primary_key=True)
    Rol_ID = Column(Integer, ForeignKey("tbc_roles.ID"), primary_key=True)
    Estatus = Column(Boolean, default=True)
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[Usuario_ID])
    rol = relationship("Rol", foreign_keys=[Rol_ID])