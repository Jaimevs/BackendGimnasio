from sqlalchemy import Column, Boolean, Integer, ForeignKey, DateTime, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime

class UserRol(Base):
    __tablename__ = 'tbd_usuarios_roles'
    __table_args__ = (
        # Restricción única para la combinación Usuario_ID y Rol_ID
        UniqueConstraint('Usuario_ID', 'Rol_ID', name='uq_usuario_rol'),
        {'extend_existing': True}  # Esto es crucial para evitar duplicaciones en la definición
    )
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Usuario_ID = Column(Integer, ForeignKey("tbb_usuarios.ID"), nullable=False)
    Rol_ID = Column(Integer, ForeignKey("tbc_roles.ID"), nullable=False)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario = relationship("User", foreign_keys=[Usuario_ID])
    rol = relationship("Rol", foreign_keys=[Rol_ID])