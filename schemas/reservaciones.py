# schemas/reservaciones.py
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

class ReservacionBase(BaseModel):
    Usuario_ID: int
    Clase_ID: int
    Fecha_Reservacion: datetime
    Estatus: Optional[str] = "Confirmada"
    Comentario: Optional[str] = None

class ReservacionCreate(ReservacionBase):
    pass

class ReservacionUpdate(BaseModel):
    Estatus: Optional[str] = None
    Comentario: Optional[str] = None
    Fecha_Reservacion: Optional[datetime] = None

class Reservacion(ReservacionBase):
    ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class ReservacionWithDetails(Reservacion):
    Nombre_Usuario: Optional[str] = None
    Nombre_Clase: Optional[str] = None
    Entrenador_Nombre: Optional[str] = None
    Dia_Clase: Optional[str] = None
    Hora_Inicio: Optional[datetime] = None
    Hora_Fin: Optional[datetime] = None