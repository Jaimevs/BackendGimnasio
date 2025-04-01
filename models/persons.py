from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from config.db import Base
import enum
from datetime import datetime

class MyGenero(str, enum.Enum):
    Masculino = "Masculino"
    Femenino = "Femenino"
    Otro = "Otro"

class Person(Base):
    __tablename__ = 'tbb_personas'
    ID = Column(Integer, primary_key=True, index=True)
    Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=True, unique=True)
    Titulo_Cortesia = Column(String(20), nullable=True)
    Nombre = Column(String(80), nullable=True)
    Primer_Apellido = Column(String(80), nullable=True)
    Segundo_Apellido = Column(String(80), nullable=True)
    Fecha_Nacimiento = Column(DateTime, nullable=True)
    Fotografia = Column(String(255), nullable=True) 
    Genero = Column(Enum(MyGenero), nullable=True)
    Tipo_Sangre = Column(Enum("O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-", name="tipo_sangre_enum"), nullable=True)
    Numero_Telefonico = Column(String(20), nullable=True)  
    Estatura = Column(Float, nullable=True)  
    Peso = Column(Float, nullable=True) 
    Estatus = Column(Boolean, default=True, nullable=True)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=True)
    Fecha_Actualizacion = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    usuario = relationship("User", back_populates="persona", uselist=False)