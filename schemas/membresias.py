from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class TipoEnum(str, Enum):
    Individual = "Individual"
    Familiar = "Familiar"
    Empresarial = "Empresarial"

class TipoServiciosEnum(str, Enum):
    Basicos = "Basicos"
    Completa = "Completa"
    Coaching = "Coaching"
    Nutriologo = "Nutriologo"

class TipoPlanEnum(str, Enum):
    Anual = "Anual"
    Semestral = "Semestral"
    Trimestral = "Trimestral"
    Bimestral = "Bimestral"
    Mensual = "Mensual"
    Semanal = "Semanal"
    Diaria = "Diaria"
    
class NivelEnum(str, Enum):
    Nuevo = "Nuevo"
    Plata = "Plata"
    Oro = "Oro"
    Diamante = "Diamante"

class MembresiaBase(BaseModel):
    Codigo: str
    Tipo: TipoEnum
    Tipo_Servicios: TipoServiciosEnum
    Tipo_Plan: TipoPlanEnum
    Nivel: Optional[NivelEnum] = NivelEnum.Nuevo
    Fecha_Inicio: datetime
    Fecha_Fin: Optional[datetime] = None
    Estatus: Optional[bool] = True

class MembresiaCreate(MembresiaBase):
    Usuario_ID: int

class MembresiaUpdate(BaseModel):
    Codigo: Optional[str] = None
    Tipo: Optional[TipoEnum] = None
    Tipo_Servicios: Optional[TipoServiciosEnum] = None
    Tipo_Plan: Optional[TipoPlanEnum] = None
    Nivel: Optional[NivelEnum] = None
    Fecha_Inicio: Optional[datetime] = None
    Fecha_Fin: Optional[datetime] = None
    Estatus: Optional[bool] = None

class Membresia(MembresiaBase):
    ID: int
    Usuario_ID: int
    Fecha_Registro: datetime
    Fecha_Actualizacion: Optional[datetime] = None

    class Config:
        from_attributes = True

class MembresiaDetalle(Membresia):
    Usuario_Nombre: Optional[str] = None
    Usuario_Correo: Optional[str] = None