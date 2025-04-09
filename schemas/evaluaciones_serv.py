from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TipoServicio(str, Enum):
    SNutricion = "Servicios de nutricion"
    HP = "Horarios y precios"
    C = "Comunidad"
    PE = "Programas de entretenimiento"

class EvaluacionServBase(BaseModel):
    Servicio_ID: int
    Tipo_Servicio: TipoServicio
    Calificacion: int
    Comentario: Optional[str] = None
    Estatus: Optional[bool] = True

class EvaluacionServCreate(EvaluacionServBase):
    pass

class EvaluacionServUpdate(BaseModel):
    Servicio_ID: Optional[int] = None
    Tipo_Servicio: Optional[TipoServicio] = None
    Calificacion: Optional[int] = None
    Comentario: Optional[str] = None
    Estatus: Optional[bool] = None

class EvaluacionServ(EvaluacionServBase):
    ID: int
    Usuario_ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class EvaluacionServDetalle(EvaluacionServ):
    Servicio_Nombre: Optional[str] = None
    Usuario_Nombre: Optional[str] = None