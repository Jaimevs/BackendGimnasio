from sqlalchemy import Column, Boolean, Integer, String, DateTime, ForeignKey, Enum, Float
from sqlalchemy.orm import relationship
from config.db import Base
import enum
from datetime import datetime

class MyGenero(str, enum.Enum):
    Masculino = "Masculino"
    Femenino = "Femenino"
    Otro = "Otro"

class TipoSangre(str, enum.Enum):
    OP = "O+"
    ON = "O-"
    AP = "A+"
    AN = "A-"
    BP = "B+"
    BN = "B-"
    ABP = "AB+"
    ABN = "AB-"

class Person(Base):
    __tablename__ = 'tbb_personas'
    
    # ID con autoincremento y not null
    ID = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    
    # La clave foránea que apunta a User
    # Esta es la columna que establece la relación uno a uno
    Usuario_ID = Column(Integer, ForeignKey('tbb_usuarios.ID'), nullable=True, unique=True)
    
    # Resto de campos
    Titulo_Cortesia = Column(String(20), nullable=True)
    Nombre = Column(String(80), nullable=False)
    Primer_Apellido = Column(String(80), nullable=False)
    Segundo_Apellido = Column(String(80), nullable=True)
    Fecha_Nacimiento = Column(DateTime, nullable=True)
    Fotografia = Column(String(255), nullable=True) 
    Genero = Column(Enum(MyGenero), nullable=True)
    Tipo_Sangre = Column(Enum(TipoSangre), nullable=True)
    Numero_Telefonico = Column(String(20), nullable=True)  
    Estatura = Column(Float, nullable=True)
    Peso = Column(Float, nullable=True)
    Estatus = Column(Boolean, default=True, nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now, nullable=False)
    Fecha_Actualizacion = Column(DateTime, onupdate=datetime.now, nullable=True)
    
    # Relación con User - una persona pertenece a un solo usuario
    usuario = relationship("User", back_populates="persona")