from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Date
from config.db import Base
from sqlalchemy.orm import relationship
from datetime import datetime

class Ejercicio(Base):
    __tablename__ = "tbb_ejercicios"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    Categoria = Column(String(60), nullable=False)
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relación con entrenamientos
    entrenamientos = relationship(
        "Entrenamiento", 
        secondary="tbb_entrenamiento_ejercicios",
        back_populates="ejercicios"
    )

class Entrenamiento(Base):
    __tablename__ = "tbb_entrenamientos"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Nombre = Column(String(100), nullable=False)
    Fecha = Column(Date, nullable=False)
    ID_Usuario = Column(Integer, ForeignKey("tbb_usuarios.ID"))
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)
    
    # Relación con usuario - asegurar que User tenga la relación correspondiente
    usuario = relationship("User", backref="entrenamientos")
    
    # Relación con ejercicios
    ejercicios = relationship(
        "Ejercicio", 
        secondary="tbb_entrenamiento_ejercicios", 
        back_populates="entrenamientos"
    )

class EntrenamientoEjercicios(Base):
    __tablename__ = "tbb_entrenamiento_ejercicios"
    
    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    ID_Entrenamiento = Column(Integer, ForeignKey("tbb_entrenamientos.ID"))
    ID_Ejercicio = Column(Integer, ForeignKey("tbb_ejercicios.ID"))
    Fecha_Registro = Column(DateTime, default=datetime.now)
    Fecha_Actualizacion = Column(DateTime, nullable=True, onupdate=datetime.now)