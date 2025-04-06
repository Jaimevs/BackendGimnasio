from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime, time

class ClaseBase(BaseModel):
    Nombre: str
    Descripcion: Optional[str] = None
    Dia_Inicio: str
    Dia_Fin: str
    Hora_Inicio: time
    Hora_Fin: time
    Duracion_Minutos: int
    Estatus: Optional[bool] = True

class ClaseCreate(ClaseBase):
    pass

class ClaseUpdate(BaseModel):
    Nombre: Optional[str] = None
    Descripcion: Optional[str] = None
    Dia_Inicio: Optional[str] = None
    Dia_Fin: Optional[str] = None
    Hora_Inicio: Optional[time] = None
    Hora_Fin: Optional[time] = None
    Duracion_Minutos: Optional[int] = None
    Estatus: Optional[bool] = None

class Clase(ClaseBase):
    ID: int
    Entrenador_ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class ClaseWithEntrenador(Clase):
    Entrenador_Nombre: Optional[str] = None
    Entrenador_Apellido: Optional[str] = None