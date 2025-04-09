from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

class ServicioBase(BaseModel):
    Nombre: str
    Descripcion: Optional[str] = None
    Costo: float = Field(..., ge=0.0)  # Asegurar que el costo no sea negativo
    # Area_ID: Optional[int] = None  # Comentado por ahora
    Estatus: Optional[bool] = True

class ServicioCreate(ServicioBase):
    pass

class ServicioUpdate(BaseModel):
    Nombre: Optional[str] = None
    Descripcion: Optional[str] = None
    Costo: Optional[float] = Field(None, ge=0.0)  # Asegurar que el costo no sea negativo
    # Area_ID: Optional[int] = None  # Comentado por ahora
    Estatus: Optional[bool] = None

class Servicio(ServicioBase):
    ID: int
    Usuario_ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class ServicioDetalle(Servicio):
    Usuario_Nombre: Optional[str] = None
    # Area_Nombre: Optional[str] = None  # Comentado por ahora
    Total_Evaluaciones: Optional[int] = 0
    Promedio_Calificacion: Optional[float] = 0.0