from sqlalchemy import Column, Boolean, Integer, DateTime, ForeignKey, Enum, String, Float
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
    # Producto_id = Column(Integer, ForeignKey("tbb_producto.ID"), nullable=False)  # Comentado por ahora
    Usuario_ID = Column(Integer, ForeignKey("tbd_usuarios_roles.Usuario_ID"), nullable=False)
    Nombre = Column(String(100), nullable=False)
    Descripcion = Column(String(255), nullable=True)
    Tipo = Column(Enum(MyTipo), nullable=False)
    Descuento = Column(Float, nullable=False)
    Aplicacion_en = Column(Enum(MyAplicacion), nullable=False)
    Fecha_Inicio = Column(DateTime, nullable=False)
    Fecha_Fin = Column(DateTime, nullable=True)
    Fecha_Registro = Column(DateTime, nullable=False, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    Estatus = Column(Boolean, default=True, nullable=False)
    
    # Relaciones
    usuario_rol = relationship("UserRol", foreign_keys=[Usuario_ID])
    # producto = relationship("Producto", foreign_keys=[Producto_id])  # Comentado por ahora