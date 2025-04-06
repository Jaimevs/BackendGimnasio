from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from schemas.ejercicios import Ejercicio

# Esquema base para Entrenamiento
class EntrenamientoBase(BaseModel):
    Nombre: str
    Fecha: date
    ID_Usuario: int

# Esquema para crear un Entrenamiento
class EntrenamientoCreate(EntrenamientoBase):
    ejercicios_ids: List[int]

# Esquema para actualizar un Entrenamiento
class EntrenamientoUpdate(BaseModel):
    Nombre: Optional[str] = None
    Fecha: Optional[date] = None
    ejercicios_ids: Optional[List[int]] = None

# Esquema para respuesta de Entrenamiento
class Entrenamiento(EntrenamientoBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None
    ejercicios: List[Ejercicio] = []

    class Config:
        orm_mode = True