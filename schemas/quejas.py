from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class QuejaBase(BaseModel):
    Entrenador_ID: int
    Clase_ID: int
    Calificacion: int
    Comentario: Optional[str] = None
    Estatus: Optional[bool] = True

class QuejaCreate(QuejaBase):
    pass

class QuejaUpdate(BaseModel):
    Calificacion: Optional[int] = None
    Comentario: Optional[str] = None
    Estatus: Optional[bool] = None

class Queja(QuejaBase):
    ID: int
    Usuario_ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class QuejaDetalle(Queja):
    Entrenador_Nombre: Optional[str] = None
    Clase_Nombre: Optional[str] = None
    Usuario_Nombre: Optional[str] = None

