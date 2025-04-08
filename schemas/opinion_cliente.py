from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class TipoOpinion(str, Enum):
    Queja = "Queja"
    Sugerencia = "Sugerencia"
    Felicitacion = "Felicitacion"
    Recomendacion = "Recomendacion"
    Otro = "Otro"

class OpinionClienteBase(BaseModel):
    Tipo: TipoOpinion
    Descripcion: str

class OpinionClienteCreate(OpinionClienteBase):
    pass

class OpinionClienteUpdate(BaseModel):
    Tipo: Optional[TipoOpinion] = None
    Descripcion: Optional[str] = None

class OpinionClienteRespuesta(BaseModel):
    Respuesta: str

class OpinionCliente(OpinionClienteBase):
    ID: int
    Usuario_ID: int
    Respuesta_Usuario_ID: Optional[int] = None
    Respuesta: Optional[str] = None
    Estatus: bool
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class OpinionClienteDetalle(OpinionCliente):
    Usuario_Nombre: Optional[str] = None
    Respuesta_Usuario_Nombre: Optional[str] = None