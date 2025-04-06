from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Esquema base para Ejercicio
class EjercicioBase(BaseModel):
    Nombre: str
    Categoria: str

# Esquema para crear un Ejercicio
class EjercicioCreate(EjercicioBase):
    pass

# Esquema para actualizar un Ejercicio
class EjercicioUpdate(BaseModel):
    Nombre: Optional[str] = None
    Categoria: Optional[str] = None

# Esquema para respuesta de Ejercicio
class Ejercicio(EjercicioBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True