from typing import List, Union
from pydantic import BaseModel
from datetime import datetime, date
import enum

class MembresiaBase(BaseModel):
    Codigo: str
    Tipo: str
    Tipo_Servicios: str
    Tipo_Plan: str
    Nivel: str
    Fecha_Inicio: datetime
    Estatus: bool
    Fecha_Registro : datetime
    Fecha_Actualizacion: datetime


class MembresiaCreate(MembresiaBase):
    pass

class MembresiaUpdate(MembresiaBase):
    pass

class Membresia(MembresiaBase):
    ID: int
    #owner_id: int clave foranea
    class Config:
        orm_mode = True