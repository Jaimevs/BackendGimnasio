from sqlalchemy import Column,Integer,String,Boolean,DateTime,ForeignKey,Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
import enum

class MyTipo(enum.Enum):
    Consulta ="Consulta"
    Reclamo ="Reclamo"
    Sugerencia = "Sugerencia"

class Servicio_Cliente(Base):
    __tablename__ = "tbc_servicios_clientes"
    
    ID = Column(Integer, primary_key=True, index=True)
    Persona_ID = Column(String(80))
    Tipo_Servicio = Column(Enum(MyTipo))
    Descripcion = Column(String(255)) 
    Comentarios = Column(String(200))    
    Estatus = Column(Boolean, default=False)
    Fecha_Registro = Column(DateTime)
    Fecha_Actualizacion = Column(DateTime)    
