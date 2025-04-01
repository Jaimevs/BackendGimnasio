from typing import List
from pydantic import BaseModel
from datetime import datetime

class OpinionClienteBase(BaseModel):
    descripcion: str
    tipo: str
    respuesta: str
    estatus: bool
    atencion_personal: str
    fecha_registro: datetime
    fecha_actualizacion: datetime

class OpinionClienteCreate(OpinionClienteBase):
    pass

class OpinionClienteUpdate(BaseModel):
    descripcion: str
    tipo: str
    respuesta: str
    estatus: bool
    atencion_personal: str

class OpinionCliente(OpinionClienteBase):
    id: int
    
    class Config:
        orm_mode = True
