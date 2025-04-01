from sqlalchemy import Column, Boolean, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy.orm import relationship
from config.db import Base
from datetime import datetime
import enum

class MyTipo(enum.Enum):
    Miembro = "Miembro"
    Empleado = "Empleado"
    Usuario = "Usuario"
    
class MyAplicacion(enum.Enum):
    Tienda_Virtual = "Tienda virtual"
    Tienda_Presencial = "Tienda presencial"

class Promocion(Base):
    __tablename__ = 'tbb_promociones'
    
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    Producto_id = Column(Integer, nullable=False)
    Tipo = Column(Enum(MyTipo), nullable=False)
    Aplicacion_en = Column(Enum(MyAplicacion), nullable=False)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    Estatus = Column(Boolean, default=True, nullable=False)