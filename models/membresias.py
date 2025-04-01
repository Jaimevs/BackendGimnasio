from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
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

    ID= Column(Integer, primary_key=True, index=True)
    Codigo = Column(String(50))
    Tipo = Column(Enum(MyTipo))
    Tipo_Servicios = Column( Enum(MyTipoServicios))
    Tipo_Plan = Column( Enum(MyTipoPlan))
    Nivel = Column(Enum(MyNivel))
    Fecha_Inicio = Column(DateTime)
    Fecha_Fin = Column(DateTime)
    Estatus = Column(Boolean, default=False)
    Fecha_Registro = Column(DateTime)
    Fecha_Actualizacion = Column(DateTime)
    #items = relationship("Item", back_populates="owner") Clave Foranea


