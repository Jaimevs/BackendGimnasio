from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum


class MyTipo(str, enum.Enum):
    Individual = "Individual"
    Familiar = "Familiar"
    Empresarial = "Empresarial"

class MyTipoServicios(str, enum.Enum):
    Basicos = "Basicos"
    Completa = "Completa"
    Coaching = "Coaching"
    Nutriologo = "Nutriologo"

class MyTipoPlan(str, enum.Enum):
    Anual = "Anual"
    Semestral = "Semestral"
    Trimestral = "Trimestral"
    Bimestral = "Bimestral"
    Mensual = "Mensual"
    Semanal = "Semanal"
    Diaria = "Diaria"
    
class MyNivel(str, enum.Enum):
    Nuevo = "Nuevo"
    Plata = "Plata"
    Oro = "Oro"
    Diamante = "Diamante"
   

class Membresia(Base):
    __tablename__ = "tbc_membresias"

    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Usuario_ID = Column(Integer, ForeignKey("tbd_usuarios_roles.Usuario_ID"), nullable=False)
    Codigo = Column(String(50), nullable=False, unique=True)
    Tipo = Column(Enum(MyTipo), nullable=False)
    Tipo_Servicios = Column(Enum(MyTipoServicios), nullable=False)
    Tipo_Plan = Column(Enum(MyTipoPlan), nullable=False)
    Nivel = Column(Enum(MyNivel), nullable=False, default=MyNivel.Nuevo)
    Fecha_Inicio = Column(DateTime, nullable=False)
    Fecha_Fin = Column(DateTime, nullable=True)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relaciones
    usuario_rol = relationship("UserRol", foreign_keys=[Usuario_ID])